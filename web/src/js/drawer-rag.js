/* Drawer RAG module for the Hub & Spoke frontend.
   Vanilla JS included via <script> (no build step). All code ASCII-only. */
(function () {
  var DRAWER_ID = "drawer-rag";
  var BACKDROP_ID = "drawer-rag-backdrop";
  var TRIGGER_SELECTOR = '[aria-controls="drawer-rag"]';
  var MESSAGES_ID = "drawer-rag-messages";
  var LOADING_ID = "drawer-rag-loading";
  var ERROR_ID = "drawer-rag-error";
  var FORM_ID = "drawer-rag-form";
  var INPUT_ID = "drawer-rag-input";
  var SEND_ID = "drawer-rag-send";
  var CLOSE_ID = "drawer-rag-close";

  function el(id) {
    return document.getElementById(id);
  }

  function appendMessage(text, sender) {
    var container = el(MESSAGES_ID);
    if (!container) { return; }
    var wrap = document.createElement("div");
    wrap.className = "drawer-message drawer-message-" + sender;
    var label = document.createElement("div");
    label.className = "drawer-message-label";
    label.textContent = sender === "user" ? "You" : "Assistant";
    var body = document.createElement("div");
    body.className = "drawer-message-body";
    body.textContent = text;
    wrap.appendChild(label);
    wrap.appendChild(body);
    container.appendChild(wrap);
    container.scrollTop = container.scrollHeight;
  }

  function showError(message) {
    var errorEl = el(ERROR_ID);
    if (!errorEl) { return; }
    errorEl.textContent = message;
    errorEl.hidden = false;
  }

  function hideError() {
    var errorEl = el(ERROR_ID);
    if (!errorEl) { return; }
    errorEl.hidden = true;
  }

  function setLoading(loading) {
    var loadingEl = el(LOADING_ID);
    var form = el(FORM_ID);
    if (loadingEl) { loadingEl.hidden = !loading; }
    if (form) {
      var input = el(INPUT_ID);
      var send = el(SEND_ID);
      if (input) { input.disabled = loading; }
      if (send) { send.disabled = loading; }
    }
  }

  function openDrawer() {
    var drawer = el(DRAWER_ID);
    var backdrop = el(BACKDROP_ID);
    if (drawer) { drawer.classList.add("open"); }
    if (backdrop) { backdrop.classList.add("open"); }
  }

  function closeDrawer() {
    var drawer = el(DRAWER_ID);
    var backdrop = el(BACKDROP_ID);
    if (drawer) { drawer.classList.remove("open"); }
    if (backdrop) { backdrop.classList.remove("open"); }
  }

  function onSend(event) {
    event.preventDefault();
    hideError();
    setLoading(true);
    var input = el(INPUT_ID);
    var message = input ? input.value : "";
    if (!message) {
      setLoading(false);
      return;
    }
    appendMessage(message, "user");
    if (input) { input.value = ""; }

    shared.apiRequest("/chat", {
      method: "POST",
      body: { message: message, intent_category: "rag" }
    }).then(function (response) {
      var text = "";
      if (response && response.message) { text = response.message; }
      else if (response && response.answer) { text = response.answer; }
      else if (typeof response === "string") { text = response; }
      else { text = JSON.stringify(response); }
      appendMessage(text, "assistant");
      setLoading(false);
    }).catch(function (err) {
      showError(err && err.message ? err.message : "Request failed.");
      setLoading(false);
    });
  }

  function init() {
    var trigger = document.querySelector(TRIGGER_SELECTOR);
    var closeBtn = el(CLOSE_ID);
    var backdrop = el(BACKDROP_ID);
    var form = el(FORM_ID);

    if (trigger) {
      trigger.addEventListener("click", function () {
        var drawer = el(DRAWER_ID);
        var isOpen = drawer && drawer.classList.contains("open");
        if (isOpen) { closeDrawer(); } else { openDrawer(); }
      });
    }
    if (closeBtn) { closeBtn.addEventListener("click", closeDrawer); }
    if (backdrop) { backdrop.addEventListener("click", closeDrawer); }
    if (form) { form.addEventListener("submit", onSend); }
  }

  window.drawerRag = { init: init };

  if (typeof shared !== "undefined" && shared.domReady) {
    shared.domReady(init);
  } else if (typeof document !== "undefined") {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", init);
    } else {
      init();
    }
  }
})();
