/*
 * /schedule/manage/ — cancel or move an existing booking.
 *
 * The link in the confirmation email carries a 32-hex token that stands in for
 * a login. Everything here is driven by that token: the page can read and
 * change exactly one booking and nothing else.
 */
(function () {
  "use strict";

  var root = document.getElementById("sc-manage");
  if (!root) return;
  var API = (root.getAttribute("data-endpoint") || "").replace(/\/+$/, "");

  var boot = document.getElementById("sc-m-boot");
  var body = document.getElementById("sc-m-body");
  var slotsBox = document.getElementById("sc-m-slots");

  var token = new URLSearchParams(window.location.search).get("t") || "";
  var viewTz = "America/Chicago";
  try {
    viewTz = Intl.DateTimeFormat().resolvedOptions().timeZone || viewTz;
  } catch (e) { /* keep the default */ }

  var current = null;
  var busy = false;

  function fmt(epoch, opts) {
    var o = { timeZone: viewTz };
    for (var k in opts) if (Object.prototype.hasOwnProperty.call(opts, k)) o[k] = opts[k];
    return new Intl.DateTimeFormat("en-US", o).format(new Date(epoch * 1000));
  }
  function timeOf(e) { return fmt(e, { hour: "numeric", minute: "2-digit", hour12: true }); }
  function dayOf(e) { return fmt(e, { weekday: "long", month: "long", day: "numeric", year: "numeric" }); }
  function zoneOf(e) {
    try {
      var p = new Intl.DateTimeFormat("en-US", { timeZone: viewTz, timeZoneName: "short" })
        .formatToParts(new Date(e * 1000));
      for (var i = 0; i < p.length; i++) if (p[i].type === "timeZoneName") return p[i].value;
    } catch (err) { /* fall through */ }
    return viewTz;
  }
  function esc(s) {
    return String(s == null ? "" : s)
      .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  }
  function api(path, opts) {
    return fetch(API + path, opts).then(function (res) {
      return res.json().then(function (b) { return { status: res.status, body: b }; })
        .catch(function () { return { status: res.status, body: {} }; });
    });
  }
  function fail(html) {
    boot.classList.add("sc-hide");
    body.classList.remove("sc-hide");
    body.innerHTML = '<div class="sc-note sc-err">' + html + "</div>";
  }

  if (!API) { fail("Booking management is unavailable."); return; }
  if (!/^[0-9a-f]{32}$/.test(token)) {
    fail("That link is not valid. Please use the link in your confirmation email.");
    return;
  }

  function render() {
    var b = current;
    var cancelled = b.status !== "confirmed";
    boot.classList.add("sc-hide");
    body.classList.remove("sc-hide");

    body.innerHTML =
      '<div class="sc-card' + (cancelled ? " sc-cancelled" : "") + '">' +
        "<h3>" + esc(b.typeLabel) + (cancelled ? " — cancelled" : "") + "</h3>" +
        "<dl>" +
          "<dt>When</dt><dd>" + esc(dayOf(b.start)) + ", " +
            esc(timeOf(b.start)) + "–" + esc(timeOf(b.end)) + " " + esc(zoneOf(b.start)) + "</dd>" +
          "<dt>Booked by</dt><dd>" + esc(b.name) + "</dd>" +
          (b.location ? "<dt>Where</dt><dd>" + esc(b.location) + "</dd>" : "") +
          "<dt>Reference</dt><dd>" + esc(b.id) + "</dd>" +
        "</dl>" +
      "</div>" +
      (cancelled
        ? '<div class="sc-note sc-warn">This booking has been cancelled. ' +
          'You can <a href="/schedule/">pick a new time</a> whenever you like.</div>'
        : '<div class="sc-actions">' +
            '<button type="button" class="sc-btn" id="sc-m-move">Pick a different time</button>' +
            '<button type="button" class="sc-btn sc-btn-danger" id="sc-m-cancel">Cancel this booking</button>' +
          "</div><div id='sc-m-msg'></div>");

    if (cancelled) { slotsBox.innerHTML = ""; return; }
    document.getElementById("sc-m-cancel").addEventListener("click", doCancel);
    document.getElementById("sc-m-move").addEventListener("click", loadSlots);
  }

  function msg(cls, html) {
    var n = document.getElementById("sc-m-msg");
    if (n) n.innerHTML = '<div class="sc-note ' + cls + '">' + html + "</div>";
  }

  function doCancel() {
    if (busy) return;
    if (!window.confirm("Cancel this booking? The time will be released.")) return;
    busy = true;
    var btn = document.getElementById("sc-m-cancel");
    btn.disabled = true;
    btn.textContent = "Cancelling…";
    api("/api/cancel", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ token: token })
    }).then(function (r) {
      busy = false;
      if (r.status === 200 && r.body.ok) {
        current.status = "cancelled";
        slotsBox.innerHTML = "";
        render();
        return;
      }
      btn.disabled = false;
      btn.textContent = "Cancel this booking";
      msg("sc-err", r.body.error === "already_cancelled"
        ? "That booking was already cancelled."
        : "Could not cancel it. Please email me instead.");
    }).catch(function () {
      busy = false;
      btn.disabled = false;
      btn.textContent = "Cancel this booking";
      msg("sc-err", "Could not reach the booking service.");
    });
  }

  function loadSlots() {
    slotsBox.innerHTML = '<p class="sc-spin">Checking the calendar…</p>';
    api("/api/slots?type=" + encodeURIComponent(current.type)).then(function (r) {
      if (r.status !== 200 || !r.body.ok) {
        slotsBox.innerHTML = '<div class="sc-note sc-err">Could not load available times.</div>';
        return;
      }
      if (r.body.degraded) {
        slotsBox.innerHTML =
          '<div class="sc-note sc-warn"><strong>Live availability is unavailable right now.</strong> ' +
          "Rather than offer a time that might clash, no times are shown until the " +
          "calendar check is working again.</div>";
        return;
      }
      var all = [];
      (r.body.days || []).forEach(function (d) {
        (d.slots || []).forEach(function (s) { all.push(s); });
      });
      if (!all.length) {
        slotsBox.innerHTML = '<div class="sc-note sc-warn">No other open times at the moment.</div>';
        return;
      }

      var html = '<p class="sc-h">Move it to</p>';
      var groups = [], idx = {};
      all.sort(function (a, b) { return a.start - b.start; }).forEach(function (s) {
        var k = fmt(s.start, { year: "numeric", month: "2-digit", day: "2-digit" });
        if (!idx[k]) { idx[k] = { label: dayOf(s.start), slots: [] }; groups.push(idx[k]); }
        idx[k].slots.push(s);
      });
      groups.forEach(function (g) {
        html += '<div class="sc-day"><p class="sc-day-l">' + esc(g.label) + '</p><div class="sc-slots">';
        g.slots.forEach(function (s) {
          html += '<button type="button" class="sc-slot" data-start="' + s.start + '">' +
            esc(timeOf(s.start)) + " " + esc(zoneOf(s.start)) + "</button>";
        });
        html += "</div></div>";
      });
      slotsBox.innerHTML = html;

      var btns = slotsBox.querySelectorAll(".sc-slot");
      for (var i = 0; i < btns.length; i++) {
        btns[i].addEventListener("click", function () {
          doMove(parseInt(this.getAttribute("data-start"), 10), this);
        });
      }
    }).catch(function () {
      slotsBox.innerHTML = '<div class="sc-note sc-err">Could not reach the booking service.</div>';
    });
  }

  function doMove(start, btn) {
    if (busy) return;
    busy = true;
    btn.disabled = true;
    btn.textContent = "Moving…";
    api("/api/reschedule", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ token: token, start: start })
    }).then(function (r) {
      busy = false;
      if (r.status === 200 && r.body.ok) {
        /*
         * A move issues a fresh booking with a fresh token, so the URL has to
         * follow it — otherwise reloading this page would 404 on a released
         * booking and the person would think their meeting had vanished.
         */
        token = r.body.booking.manageToken;
        current = r.body.booking;
        try {
          window.history.replaceState({}, "", "/schedule/manage/?t=" + token);
        } catch (e) { /* a stale URL is survivable; the render below is not */ }
        slotsBox.innerHTML = "";
        render();
        msg("sc-ok", "Moved. A new confirmation is on its way" +
          (r.body.mailed ? "." : ", though the email did not go out — I will follow up."));
        return;
      }
      busy = false;
      btn.disabled = false;
      slotsBox.innerHTML = '<div class="sc-note sc-err">' +
        (r.body.error === "already_booked"
          ? "Someone just took that time. Here are the current options."
          : "Could not move it. Please try another time.") + "</div>";
      loadSlots();
    }).catch(function () {
      busy = false;
      btn.disabled = false;
      slotsBox.innerHTML = '<div class="sc-note sc-err">Could not reach the booking service.</div>';
    });
  }

  api("/api/booking?t=" + encodeURIComponent(token)).then(function (r) {
    if (r.status === 404) {
      fail("That booking could not be found. It may have been moved or cancelled already. " +
        'You can <a href="/schedule/">book a new time</a>.');
      return;
    }
    if (r.status !== 200 || !r.body.ok) {
      fail("Could not load that booking. Please email me.");
      return;
    }
    current = r.body.booking;
    render();
  }).catch(function () {
    fail("Could not reach the booking service.");
  });
})();
