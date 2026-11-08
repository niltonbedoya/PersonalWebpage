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
  var CV_CONTAINER_ID = "drawer-cv-form-container";
  var CV_FORM_ID = "drawer-cv-form";
  var CV_TOGGLE_ID = "drawer-cv-toggle-btn";
  var CV_CANCEL_ID = "drawer-cv-cancel-btn";
  var CV_CLOSE_ID = "drawer-cv-close-btn";
  var CV_STATUS_ID = "drawer-cv-status";

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
    var userLabel = "You";
    var assistantLabel = "Assistant";
    if (window.portfolioI18n && window.portfolioI18n.dictionary) {
      var curLang = window.portfolioI18n.getLanguage ? window.portfolioI18n.getLanguage() : "es";
      var dict = window.portfolioI18n.dictionary[curLang];
      if (dict) {
        userLabel = dict["drawer.user_label"] || userLabel;
        assistantLabel = dict["drawer.assistant_label"] || assistantLabel;
      }
    }
    label.textContent = sender === "user" ? userLabel : assistantLabel;
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

  function toggleCVForm(show) {
    var container = el(CV_CONTAINER_ID);
    if (!container) { return; }
    if (typeof show === "boolean") {
      container.hidden = !show;
    } else {
      container.hidden = !container.hidden;
    }
    var statusEl = el(CV_STATUS_ID);
    if (statusEl) { statusEl.hidden = true; }
  }

  function onCVSubmit(event) {
    event.preventDefault();
    var companyEl = el("cv-company");
    var nameEl = el("cv-name");
    var phoneEl = el("cv-phone");
    var emailEl = el("cv-email");
    var reasonEl = el("cv-reason");
    var honeypotEl = el("cv-honeypot");
    var statusEl = el(CV_STATUS_ID);
    var submitBtn = el("drawer-cv-submit-btn");

    var company = companyEl ? companyEl.value.trim() : "";
    var name = nameEl ? nameEl.value.trim() : "";
    var phone = phoneEl ? phoneEl.value.trim() : "";
    var email = emailEl ? emailEl.value.trim() : "";
    var reason = reasonEl ? reasonEl.value.trim() : "";
    var honeypot = honeypotEl ? honeypotEl.value.trim() : "";

    if (!company || !name || !phone || !email || !reason) {
      if (statusEl) {
        statusEl.textContent = "Por favor completa todos los campos requeridos.";
        statusEl.style.color = "#ef4444";
        statusEl.hidden = false;
      }
      return;
    }

    if (submitBtn) { submitBtn.disabled = true; }
    if (statusEl) {
      statusEl.textContent = "Enviando solicitud...";
      statusEl.style.color = "var(--brand-cyan)";
      statusEl.hidden = false;
    }

    shared.apiRequest("/contact/cv-request", {
      method: "POST",
      body: {
        company: company,
        name: name,
        phone: phone,
        email: email,
        reason: reason,
        honeypot: honeypot
      }
    }).then(function (res) {
      if (submitBtn) { submitBtn.disabled = false; }
      toggleCVForm(false);
      if (companyEl) companyEl.value = "";
      if (nameEl) nameEl.value = "";
      if (phoneEl) phoneEl.value = "";
      if (emailEl) emailEl.value = "";
      if (reasonEl) reasonEl.value = "";

      var curLang = (window.portfolioI18n && window.portfolioI18n.getLanguage) ? window.portfolioI18n.getLanguage() : "es";
      var msg = curLang === "en"
        ? "Thank you! Your official CV request has been submitted directly to Nilton Bedoya. He will review your details and contact you shortly."
        : "¡Muchas gracias! Tu solicitud de CV oficial ha sido enviada directamente a Nilton Bedoya. Nilton revisará los datos de tu empresa y te contactará a la brevedad.";
      appendMessage(msg, "assistant");
    }).catch(function (err) {
      if (submitBtn) { submitBtn.disabled = false; }
      if (statusEl) {
        statusEl.textContent = err && err.message ? err.message : "Error al enviar la solicitud.";
        statusEl.style.color = "#ef4444";
        statusEl.hidden = false;
      }
    });
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

    var currentLang = (window.portfolioI18n && window.portfolioI18n.getLanguage) ? window.portfolioI18n.getLanguage() : (document.documentElement.lang || "es");

    shared.apiRequest("/chat", {
      method: "POST",
      body: { message: message, intent_category: "TECHNICAL_PROFILE", language: currentLang }
    }).then(function (response) {
      var text = "";
      if (response && typeof response.response === "string") { text = response.response; }
      else if (response && typeof response.message === "string") { text = response.message; }
      else if (response && typeof response.answer === "string") { text = response.answer; }
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
    var triggers = document.querySelectorAll(TRIGGER_SELECTOR);
    var closeBtn = el(CLOSE_ID);
    var backdrop = el(BACKDROP_ID);
    var form = el(FORM_ID);

    triggers.forEach(function (trigger) {
      trigger.addEventListener("click", function (e) {
        e.preventDefault();
        var drawer = el(DRAWER_ID);
        var isOpen = drawer && drawer.classList.contains("open");
        if (isOpen) { closeDrawer(); } else { openDrawer(); }
      });
    });
    if (closeBtn) { closeBtn.addEventListener("click", closeDrawer); }
    if (backdrop) { backdrop.addEventListener("click", closeDrawer); }
    if (form) { form.addEventListener("submit", onSend); }

    var cvToggleBtn = el(CV_TOGGLE_ID);
    var cvCancelBtn = el(CV_CANCEL_ID);
    var cvCloseBtn = el(CV_CLOSE_ID);
    var cvForm = el(CV_FORM_ID);

    if (cvToggleBtn) { cvToggleBtn.addEventListener("click", function () { toggleCVForm(); }); }
    if (cvCancelBtn) { cvCancelBtn.addEventListener("click", function () { toggleCVForm(false); }); }
    if (cvCloseBtn) { cvCloseBtn.addEventListener("click", function () { toggleCVForm(false); }); }
    if (cvForm) { cvForm.addEventListener("submit", onCVSubmit); }
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
