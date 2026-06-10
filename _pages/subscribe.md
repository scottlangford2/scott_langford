---
layout: archive
title: "Subscribe to Southbound 35"
permalink: /subscribe/
author_profile: true
---

{% include base_path %}

[Southbound 35](/year-archive/) publishes on Mondays at 5 AM Central, with occasional extra posts throughout the week. Three ways to follow along.

## 1. Email

Get each new post in your inbox. The list is small and free, and each post goes out as an individual email from me, not a BCC blast. One-click unsubscribe is in every message. I don't share the list, sell the list, or use it for anything other than sending Southbound 35 posts.

<form id="sb-subscribe" style="margin: 1.2em 0;">
  <div style="display:flex; flex-wrap:wrap; gap:8px; align-items:center;">
    <input id="sb-email" name="email" type="email" required placeholder="you@example.com"
      autocomplete="email"
      style="flex:1 1 240px; padding:10px 12px; border:1px solid #ccc; border-radius:4px; font-size:1em;">
    <button type="submit"
      style="background:#006BA2; color:#fff; padding:10px 18px; border:0; border-radius:4px; font-weight:600; font-size:1em; cursor:pointer;">📬 Subscribe</button>
  </div>
  <!-- honeypot: real people never fill this; bots do -->
  <input type="text" name="website" tabindex="-1" autocomplete="off"
    style="position:absolute; left:-9999px; width:1px; height:1px; opacity:0;" aria-hidden="true">
  <!-- Turnstile (optional). After creating a widget, uncomment the next line,
       paste your site key, and uncomment the script tag below.
  <div class="cf-turnstile" data-sitekey="TURNSTILE_SITEKEY" style="margin-top:10px;"></div>
  -->
  <p id="sb-msg" style="margin:10px 0 0; font-size:.95em;" role="status" aria-live="polite"></p>
</form>

<!-- <script src="https://challenges.cloudflare.com/turnstile/v0/api.js" async defer></script> -->
<script>
(function () {
  // After deploying the Worker, replace SUBDOMAIN with your workers.dev subdomain.
  var WORKER_URL = "https://southbound35-subscribe.southbound35.workers.dev";
  var form = document.getElementById("sb-subscribe");
  var msg = document.getElementById("sb-msg");
  if (!form) return;
  form.addEventListener("submit", function (e) {
    e.preventDefault();
    var btn = form.querySelector("button");
    var payload = {
      email: document.getElementById("sb-email").value.trim(),
      website: form.elements["website"].value
    };
    var ts = form.querySelector('[name="cf-turnstile-response"]');
    if (ts) payload["cf-turnstile-response"] = ts.value;
    btn.disabled = true;
    msg.style.color = "#555";
    msg.textContent = "Subscribing…";
    fetch(WORKER_URL + "/subscribe", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    })
      .then(function (r) { return r.json().then(function (d) { return { ok: r.ok, d: d }; }); })
      .then(function (res) {
        if (res.ok && res.d.ok) {
          msg.style.color = "#1a7f37";
          msg.textContent = "You're on the list. Watch for the next post.";
          form.reset();
        } else {
          msg.style.color = "#b00";
          msg.textContent = (res.d && res.d.error) || "Something went wrong. Please try again.";
          btn.disabled = false;
        }
      })
      .catch(function () {
        msg.style.color = "#b00";
        msg.textContent = "Network error. Please try again.";
        btn.disabled = false;
      });
  });
})();
</script>

## 2. RSS

Standard RSS feed:

<p style="font-size: 1.05em;"><a href="{{ '/feed.xml' | relative_url }}"><strong>{{ site.url }}{{ site.baseurl }}/feed.xml</strong></a></p>

Drop that URL into any feed reader — [Feedly](https://feedly.com), [NetNewsWire](https://netnewswire.com), [Inoreader](https://www.inoreader.com), [The Old Reader](https://theoldreader.com), or whatever you prefer.

## 3. Bluesky

I post links to new entries on [Bluesky](https://bsky.app/profile/{{ site.author.bluesky }}).
