/* Contact form module for the Showcase Hub & Spoke frontend.
   Vanilla JS included via <script> (no build step). All code ASCII-only.
   Sends POST /contact with client-side honeypot protection and shows
   the API result (status, lead_priority) in #contact-result. */

(function () {
  var form = null;
  var result = null;
  var honeypot = null;

  function showResult(message, kind) {
    if (!result) { return; }
    result.textContent = message;
    result.className = "alert";
    if (kind) {
      result.classList.add(kind);
    }
    result.style.display = message ? "block" : "none";
  }

  function clearResult() {
    if (!result) { return; }
    result.textContent = "";
    result.className = "";
    result.style.display = "none";
  }

  function handleSubmit(event) {
    event.preventDefault();
    if (!form || !result) { return; }
    clearResult();

    // Honeypot check: any value means a bot filled it. Block without submitting.
    if (honeypot && honeypot.value && honeypot.value.trim().length > 0) {
      showResult("spam_detected: submission blocked", "blocked");
      return;
    }

    if (!shared || !shared.apiRequest) {
      showResult("Error: shared.apiRequest is not available", "error");
      return;
    }

    var nameInput = form.elements.namedItem("name");
    var emailInput = form.elements.namedItem("email");
    var messageInput = form.elements.namedItem("message");
    var name = nameInput ? nameInput.value : "";
    var email = emailInput ? emailInput.value : "";
    var message = messageInput ? messageInput.value : "";

    shared.apiRequest("/contact", {
      method: "POST",
      body: { name: name, email: email, message: message }
    }).then(function (payload) {
      showResult("status: " + (payload && payload.status) +
        ", lead_priority: " + (payload && payload.lead_priority), "ok");
    }).catch(function (err) {
      showResult("Error sending message: " +
        (err && err.message ? err.message : String(err)), "error");
    });
  }

  window.contactForm = {
    init: function () {
      form = document.getElementById("contact-form");
      result = document.getElementById("contact-result");
      honeypot = form ? form.elements.namedItem("website") : null;
      if (form) {
        form.addEventListener("submit", handleSubmit);
      }
    }
  };
})();
