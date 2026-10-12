/*
 * Booking page for /schedule/.
 *
 * Talks to the scheduling Worker (src in ~/schedule-worker), which is the only
 * authority on what is free. This file renders what the Worker offers and
 * posts back a choice; it never decides availability itself, and a slot it
 * shows can still be refused on submit if someone else got there first. That
 * case is handled by reloading the list rather than pretending.
 *
 * Deliberately a separate file rather than an inline script: the site's HTML
 * passes through the compress layout, and block comments plus an external file
 * keep that transformation from being able to touch this logic.
 */
(function () {
  "use strict";

  var app = document.getElementById("sc-app");
  if (!app) return;
  var API = (app.getAttribute("data-endpoint") || "").replace(/\/+$/, "");
  if (!API) return;

  var el = {
    boot: document.getElementById("sc-boot"),
    main: document.getElementById("sc-main"),
    types: document.getElementById("sc-types"),
    stepWhen: document.getElementById("sc-step-when"),
    stepWho: document.getElementById("sc-step-who"),
    stepDone: document.getElementById("sc-step-done"),
    days: document.getElementById("sc-days"),
    tz: document.getElementById("sc-tz"),
    tzNote: document.getElementById("sc-tz-note"),
    sel: document.getElementById("sc-sel"),
    form: document.getElementById("sc-form"),
    formErr: document.getElementById("sc-form-err"),
    submit: document.getElementById("sc-submit"),
    name: document.getElementById("sc-name"),
    email: document.getElementById("sc-email"),
    emailHint: document.getElementById("sc-email-hint"),
    orgField: document.getElementById("sc-org-field"),
    org: document.getElementById("sc-org"),
    topic: document.getElementById("sc-topic"),
    website: document.getElementById("sc-website")
  };

  var state = {
    types: [],
    hostTz: "America/Chicago",
    type: null,
    slots: [],
    nonce: "",
    chosen: null,
    viewTz: guessTz(),
    busy: false
  };

  function guessTz() {
    try {
      return Intl.DateTimeFormat().resolvedOptions().timeZone || "America/Chicago";
    } catch (e) {
      return "America/Chicago";
    }
  }

  function show(node, on) {
    if (node) node.classList[on ? "remove" : "add"]("sc-hide");
  }

  function text(s) {
    return String(s == null ? "" : s);
  }

  function fmt(epoch, tz, opts) {
    var o = { timeZone: tz };
    for (var k in opts) if (Object.prototype.hasOwnProperty.call(opts, k)) o[k] = opts[k];
    return new Intl.DateTimeFormat("en-US", o).format(new Date(epoch * 1000));
  }

  function timeOf(epoch, tz) {
    return fmt(epoch, tz, { hour: "numeric", minute: "2-digit", hour12: true });
  }

  function zoneOf(epoch, tz) {
    try {
      var parts = new Intl.DateTimeFormat("en-US", {
        timeZone: tz, timeZoneName: "short"
      }).formatToParts(new Date(epoch * 1000));
      for (var i = 0; i < parts.length; i++) {
        if (parts[i].type === "timeZoneName") return parts[i].value;
      }
    } catch (e) { /* fall through to the raw name */ }
    return tz;
  }

  function dayKeyOf(epoch, tz) {
    return fmt(epoch, tz, { year: "numeric", month: "2-digit", day: "2-digit" });
  }

  function dayLabelOf(epoch, tz) {
    return fmt(epoch, tz, { weekday: "long", month: "long", day: "numeric", year: "numeric" });
  }

  function notice(container, cls, html) {
    container.innerHTML = '<div class="sc-note ' + cls + '">' + html + "</div>";
  }

  function api(path, opts) {
    return fetch(API + path, opts).then(function (res) {
      return res.json().then(function (body) {
        return { status: res.status, body: body };
      }).catch(function () {
        return { status: res.status, body: { ok: false, error: "bad_response" } };
      });
    });
  }

  /* ----------------------------------------------------------- step one -- */

  function renderTypes() {
    el.types.innerHTML = "";
    state.types.forEach(function (t) {
      var b = document.createElement("button");
      b.type = "button";
      b.className = "sc-type";
      b.setAttribute("aria-pressed", "false");
      b.innerHTML =
        '<span class="sc-type-l">' + text(t.label) + "</span>" +
        '<span class="sc-type-b">' + text(t.blurb) + "</span>";
      b.addEventListener("click", function () { chooseType(t); });
      el.types.appendChild(b);
    });
  }

  function chooseType(t) {
    state.type = t;
    state.chosen = null;
    var btns = el.types.querySelectorAll(".sc-type");
    for (var i = 0; i < btns.length; i++) {
      btns[i].setAttribute("aria-pressed", state.types[i] === t ? "true" : "false");
    }
    show(el.stepWhen, true);
    show(el.stepWho, false);
    show(el.stepDone, false);

    el.orgField.classList[t.askOrg ? "remove" : "add"]("sc-hide");
    el.org.required = !!t.askOrg;
    el.emailHint.textContent = (t.requireEmailDomain && t.requireEmailDomain.length)
      ? "Use your " + t.requireEmailDomain.join(" or ") + " address."
      : "";

    loadSlots();
  }

  /* ----------------------------------------------------------- step two -- */

  function loadSlots() {
    el.days.innerHTML = '<p class="sc-spin">Checking the calendar…</p>';
    api("/api/slots?type=" + encodeURIComponent(state.type.key)).then(function (r) {
      if (r.status !== 200 || !r.body.ok) {
        notice(el.days, "sc-err",
          "Could not load available times. Please email " + mailtoLink() + ".");
        return;
      }
      if (r.body.degraded) {
        /*
         * The Worker could not read the calendar and will not guess. Say so
         * plainly instead of showing times that might collide.
         */
        notice(el.days, "sc-warn",
          "<strong>Live availability is unavailable right now.</strong> " +
          "Rather than offer a time that might clash, the calendar is hidden " +
          "until the check is working again. Please email " + mailtoLink() +
          " and I will confirm a time directly.");
        return;
      }
      state.hostTz = r.body.hostTz || state.hostTz;
      state.nonce = r.body.nonce || "";
      state.slots = [];
      (r.body.days || []).forEach(function (d) {
        (d.slots || []).forEach(function (s) { state.slots.push(s); });
      });
      renderTzPicker();
      renderDays();
    }).catch(function () {
      notice(el.days, "sc-err",
        "Could not reach the booking service. Please email " + mailtoLink() + ".");
    });
  }

  function mailtoLink() {
    var a = document.querySelector('.sc-intro a[href^="mailto:"]');
    return a ? a.outerHTML : "me";
  }

  function renderTzPicker() {
    if (el.tz.options.length) return;
    var opts = [state.viewTz];
    if (state.hostTz !== state.viewTz) opts.push(state.hostTz);
    opts.forEach(function (z) {
      var o = document.createElement("option");
      o.value = z;
      o.textContent = z.replace(/_/g, " ") + (z === state.hostTz ? " (my time)" : " (your time)");
      el.tz.appendChild(o);
    });
    el.tz.value = state.viewTz;
    el.tz.addEventListener("change", function () {
      state.viewTz = el.tz.value;
      renderDays();
      if (state.chosen) renderSelection();
    });
    el.tzNote.textContent = state.hostTz === state.viewTz
      ? ""
      : " — I am in " + state.hostTz.replace(/_/g, " ") + ".";
  }

  function renderDays() {
    el.days.innerHTML = "";
    if (!state.slots.length) {
      notice(el.days, "sc-warn",
        "No open times in the next " + state.type.maxDaysAhead +
        " days. Please email " + mailtoLink() + " and we will find something.");
      return;
    }

    /*
     * Regroup by the viewer's day, not the host's: a late-afternoon Central
     * slot is already tomorrow in much of the world, and showing it under the
     * Central date would be wrong for the person reading it.
     */
    var groups = [];
    var index = {};
    state.slots.slice().sort(function (a, b) { return a.start - b.start; }).forEach(function (s) {
      var key = dayKeyOf(s.start, state.viewTz);
      if (!index[key]) {
        index[key] = { label: dayLabelOf(s.start, state.viewTz), slots: [] };
        groups.push(index[key]);
      }
      index[key].slots.push(s);
    });

    groups.forEach(function (g) {
      var wrap = document.createElement("div");
      wrap.className = "sc-day";
      var h = document.createElement("p");
      h.className = "sc-day-l";
      h.textContent = g.label;
      wrap.appendChild(h);

      var row = document.createElement("div");
      row.className = "sc-slots";
      g.slots.forEach(function (s) {
        var b = document.createElement("button");
        b.type = "button";
        b.className = "sc-slot";
        b.setAttribute("aria-pressed", state.chosen && state.chosen.start === s.start ? "true" : "false");
        var label = timeOf(s.start, state.viewTz) + " " + zoneOf(s.start, state.viewTz);
        b.innerHTML = text(label) +
          (state.viewTz !== state.hostTz
            ? '<span class="sc-slot-sub">' + text(s.hostLabel) + " my time</span>"
            : "");
        b.addEventListener("click", function () { chooseSlot(s); });
        row.appendChild(b);
      });
      wrap.appendChild(row);
      el.days.appendChild(wrap);
    });
  }

  function chooseSlot(s) {
    state.chosen = s;
    var btns = el.days.querySelectorAll(".sc-slot");
    for (var i = 0; i < btns.length; i++) btns[i].setAttribute("aria-pressed", "false");
    renderDays();
    renderSelection();
    show(el.stepWho, true);
    el.formErr.innerHTML = "";
    el.stepWho.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }

  function renderSelection() {
    var s = state.chosen;
    el.sel.innerHTML =
      "<strong>" + text(state.type.label) + "</strong>, " +
      text(state.type.durationMin) + " minutes<br>" +
      text(dayLabelOf(s.start, state.viewTz)) + " at " +
      text(timeOf(s.start, state.viewTz)) + " " + text(zoneOf(s.start, state.viewTz)) +
      (state.viewTz !== state.hostTz
        ? '<br><span style="color:#777">' + text(s.hostLabel) + " my time</span>"
        : "") +
      (state.type.location
        ? '<br><span style="color:#777">' + text(state.type.location) + "</span>"
        : "");
  }

  /* --------------------------------------------------------- step three -- */

  var ERRORS = {
    email_domain: "That meeting type needs a university address.",
    email_invalid: "That email address does not look right.",
    name_required: "Please give your name.",
    org_required: "Please say which organization you are with.",
    rate_limited: "You have booked several times today already. Email me instead and I will sort it out.",
    too_soon: "That time is too close to now. Please pick a later one.",
    too_far: "That time is beyond how far ahead this opens.",
    not_a_slot: "That time is no longer being offered. Please pick another.",
    calendar_conflict: "Something came up on my calendar for that time. Please pick another.",
    already_booked: "Someone just took that time. Please pick another.",
    day_full: "That day is full. Please pick another.",
    too_fast: "That submitted unusually fast. Please try once more.",
    nonce_expired: "This page has been open a while. Reloading the times now.",
    nonce_bad: "Please reload the page and try again.",
    nonce_malformed: "Please reload the page and try again.",
    calendar_unavailable: "I cannot check my calendar at the moment, so I am not taking bookings. Please email me.",
    turnstile_failed: "The anti-spam check did not pass. Please try again.",
    rejected: "That submission was rejected."
  };

  el.form.addEventListener("submit", function (ev) {
    ev.preventDefault();
    if (state.busy || !state.chosen) return;

    var name = el.name.value.trim();
    var email = el.email.value.trim();
    var org = el.org.value.trim();

    if (name.length < 2) return failForm("Please give your name.");
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) return failForm("That email address does not look right.");
    if (state.type.askOrg && org.length < 2) return failForm("Please say which organization you are with.");
    var domains = state.type.requireEmailDomain || [];
    if (domains.length) {
      var host = email.split("@").pop().toLowerCase();
      var fits = domains.some(function (d) {
        d = d.toLowerCase();
        return host === d || host.indexOf("." + d, host.length - d.length - 1) !== -1;
      });
      if (!fits) return failForm("Please use your " + domains.join(" or ") + " address.");
    }

    state.busy = true;
    el.submit.disabled = true;
    el.submit.textContent = "Confirming…";
    el.formErr.innerHTML = "";

    api("/api/book", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        type: state.type.key,
        start: state.chosen.start,
        nonce: state.nonce,
        name: name,
        email: email,
        org: org,
        topic: el.topic.value.trim(),
        tz: state.viewTz,
        website: el.website.value
      })
    }).then(function (r) {
      state.busy = false;
      el.submit.disabled = false;
      el.submit.textContent = "Confirm this time";

      if (r.status === 200 && r.body.ok) {
        done(r.body);
        return;
      }
      var code = r.body && r.body.error;
      failForm(ERRORS[code] || "That did not go through. Please try again, or email me.");

      /* A conflict means the list is out of date; fetch the truth again. */
      if (code === "already_booked" || code === "not_a_slot" ||
          code === "calendar_conflict" || code === "day_full" ||
          code === "nonce_expired") {
        state.chosen = null;
        show(el.stepWho, false);
        loadSlots();
      }
    }).catch(function () {
      state.busy = false;
      el.submit.disabled = false;
      el.submit.textContent = "Confirm this time";
      failForm("Could not reach the booking service. Please email me.");
    });
  });

  function failForm(msg) {
    notice(el.formErr, "sc-err", text(msg));
    el.formErr.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }

  /* ------------------------------------------------------------- done ---- */

  function icsBlobUrl(b) {
    function stamp(sec) {
      return new Date(sec * 1000).toISOString().replace(/[-:]/g, "").replace(/\.\d{3}/, "");
    }
    var lines = [
      "BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//scottlangford.com//schedule//EN",
      "BEGIN:VEVENT",
      "UID:booking-" + b.id + "@scottlangford.com",
      "DTSTAMP:" + stamp(Math.floor(Date.now() / 1000)),
      "DTSTART:" + stamp(b.start),
      "DTEND:" + stamp(b.end),
      "SUMMARY:" + String(b.typeLabel).replace(/[,;]/g, " "),
      b.location ? "LOCATION:" + String(b.location).replace(/[,;]/g, " ") : "",
      "END:VEVENT", "END:VCALENDAR"
    ].filter(Boolean);
    try {
      return URL.createObjectURL(new Blob([lines.join("\r\n")], { type: "text/calendar" }));
    } catch (e) {
      return null;
    }
  }

  function done(payload) {
    var b = payload.booking;
    show(el.stepWhen, false);
    show(el.stepWho, false);
    show(el.stepDone, true);

    var mine = state.viewTz !== state.hostTz
      ? '<dt>My time</dt><dd>' + text(b.hostDate) + ", " + text(b.hostTime) + "</dd>"
      : "";
    var yours = '<dt>When</dt><dd>' +
      text(dayLabelOf(b.start, state.viewTz)) + ", " +
      text(timeOf(b.start, state.viewTz)) + "–" + text(timeOf(b.end, state.viewTz)) + " " +
      text(zoneOf(b.start, state.viewTz)) + "</dd>";

    var mailLine = payload.mailed
      ? "<p class='sc-muted'>A confirmation with a calendar invite is on its way to " +
        text(b.email) + ".</p>"
      : "<div class='sc-note sc-warn'><strong>Your time is held.</strong> " +
        "The confirmation email did not go out, though — so save this page or add " +
        "the invite below, and I will follow up directly.</div>";

    var ics = icsBlobUrl(b);
    var manage = "/schedule/manage/?t=" + encodeURIComponent(b.manageToken);

    el.stepDone.innerHTML =
      '<div class="sc-conf">' +
        "<h3>You are booked in</h3>" +
        "<p class='sc-muted'>" + text(b.typeLabel) + ", " + text(b.durationMin) + " minutes.</p>" +
        "<dl>" + yours + mine +
          (b.location ? "<dt>Where</dt><dd>" + text(b.location) + "</dd>" : "") +
          "<dt>Reference</dt><dd>" + text(b.id) + "</dd>" +
        "</dl>" +
        mailLine +
        "<p class='sc-muted'>" +
          (ics ? '<a href="' + ics + '" download="meeting.ics">Add to your calendar</a> &nbsp;·&nbsp; ' : "") +
          '<a href="' + manage + '">Change or cancel this booking</a>' +
        "</p>" +
      "</div>";
    el.stepDone.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  /* ------------------------------------------------------------- boot ---- */

  api("/api/types").then(function (r) {
    if (r.status !== 200 || !r.body.ok || !(r.body.types || []).length) {
      el.boot.innerHTML =
        '<div class="sc-note sc-err">The booking service is not reachable right now. ' +
        "Please email " + mailtoLink() + " and I will find a time.</div>";
      return;
    }
    state.types = r.body.types;
    state.hostTz = r.body.hostTz || state.hostTz;
    renderTypes();
    show(el.boot, false);
    el.boot.classList.add("sc-hide");
    show(el.main, true);
    if (state.types.length === 1) chooseType(state.types[0]);
  }).catch(function () {
    el.boot.innerHTML =
      '<div class="sc-note sc-err">The booking service is not reachable right now. ' +
      "Please email " + mailtoLink() + " and I will find a time.</div>";
  });
})();
