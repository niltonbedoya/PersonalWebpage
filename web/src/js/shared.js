/* Shared frontend helpers for the Showcase Hub & Spoke frontend.
   Vanilla JS included via <script> (no build step). All code ASCII-only. */

/* Same-origin API base URL. FastAPI serves /static and the API lives at
   /chat, /news, /contact, /health on the same origin, so relative paths work. */
var API_BASE_URL = "";

/* Fetch a JSON API endpoint with error handling.
   path: relative API path, e.g. "/news?category=AI_SOFTWARE"
   opts: optional { method, body, headers }
   Returns parsed JSON or rejects with a descriptive Error. */
async function apiRequest(path, opts) {
  var url = API_BASE_URL + path;
  var init = { headers: { "Accept": "application/json" } };
  if (opts) {
    if (opts.method) { init.method = opts.method; }
    if (opts.headers) {
      Object.keys(opts.headers).forEach(function (k) { init.headers[k] = opts.headers[k]; });
    }
    if (opts.body && opts.method && opts.method !== "GET") {
      init.headers["Content-Type"] = "application/json";
      init.body = JSON.stringify(opts.body);
    }
  }
  try {
    var response = await fetch(url, init);
    if (!response.ok) {
      var bodyText = await response.text().catch(function () { return ""; });
      throw new Error("API " + (init.method || "GET") + " " + path + " failed (" + response.status + "): " + bodyText);
    }
    var contentType = response.headers.get("content-type") || "";
    if (contentType.indexOf("application/json") === -1) {
      var text = await response.text();
      throw new Error("API " + path + " returned non-JSON: " + text.slice(0, 200));
    }
    return await response.json();
  } catch (err) {
    if (err instanceof Error && err.message && err.message.indexOf("API ") === 0) {
      throw err;
    }
    throw new Error("API " + (init.method || "GET") + " " + path + " network error: " + (err && err.message ? err.message : String(err)));
  }
}

/* DOM ready helper. Runs fn when the document is ready. */
function domReady(fn) {
  if (typeof fn !== "function") { return; }
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", fn);
  } else {
    fn();
  }
}

/* Tiny pub/sub for cross-component events (e.g. drawer open/close). */
var hub = (function () {
  var topics = {};
  return {
    on: function (topic, handler) {
      if (!topics[topic]) { topics[topic] = []; }
      topics[topic].push(handler);
    },
    emit: function (topic) {
      var args = Array.prototype.slice.call(arguments, 1);
      (topics[topic] || []).forEach(function (handler) { handler.apply(null, args); });
    }
  };
})();

/* Page Transition with 3D Logo Spin (GPU-accelerated, zero lag) */
function initPageTransitions() {
  if (window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    return;
  }
  var overlay = document.getElementById("page-transition-overlay");
  if (!overlay) {
    overlay = document.createElement("div");
    overlay.id = "page-transition-overlay";
    overlay.className = "page-transition-overlay";
    overlay.innerHTML = '<div class="transition-spinner-wrap"><img src="/static/assets/logos/logo_transparent.png" alt="Transitioning" class="transition-logo" width="60" height="60"></div>';
    document.body.appendChild(overlay);
  }

  // Hide overlay on page show (handles initial load and bfcache)
  function hideOverlay() {
    overlay.classList.remove("active");
  }
  window.addEventListener("pageshow", hideOverlay);
  hideOverlay();

  // Intercept internal HTML navigation clicks
  document.addEventListener("click", function (e) {
    var link = e.target.closest("a");
    if (!link) return;
    var href = link.getAttribute("href");
    if (!href || href.indexOf("#") === 0 || href.indexOf("mailto:") === 0 || href.indexOf("tel:") === 0) return;
    if (link.target === "_blank" || e.ctrlKey || e.metaKey || e.shiftKey) return;
    if (href.indexOf("http://") === 0 || href.indexOf("https://") === 0) {
      if (href.indexOf(window.location.origin) !== 0) return;
    }
    // Only intercept local html page routes
    if (href.indexOf(".html") !== -1 || href === "/" || href.indexOf("/static/pages/") !== -1) {
      // If clicking link to current page, do not animate
      var currentPath = window.location.pathname.split("/").pop() || "index.html";
      var targetPath = href.split("/").pop().split("?")[0].split("#")[0] || "index.html";
      if (currentPath === targetPath) return;

      e.preventDefault();
      overlay.classList.add("active");
      setTimeout(function () {
        window.location.href = href;
      }, 240);
    }
  });
}

domReady(initPageTransitions);

window.shared = {
  API_BASE_URL: API_BASE_URL,
  apiRequest: apiRequest,
  domReady: domReady,
  hub: hub,
  initPageTransitions: initPageTransitions
};
