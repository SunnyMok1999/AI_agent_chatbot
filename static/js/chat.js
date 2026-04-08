/* AI Agent Chatbot – frontend logic */

(function () {
  "use strict";

  const messagesEl = document.getElementById("messages");
  const formEl = document.getElementById("chat-form");
  const inputEl = document.getElementById("user-input");
  const typingEl = document.getElementById("typing-indicator");
  const sendBtn = formEl.querySelector(".send-btn");

  // Conversation history sent to the API
  let history = [];

  // ---- Helpers ----

  function escapeHtml(text) {
    return text
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  function appendMessage(role, text) {
    // Remove welcome placeholder if present
    const welcome = messagesEl.querySelector(".welcome");
    if (welcome) welcome.remove();

    const wrapper = document.createElement("div");
    wrapper.className = `message ${role}`;

    const avatar = document.createElement("div");
    avatar.className = "avatar";
    avatar.textContent = role === "user" ? "🧑" : role === "error" ? "⚠️" : "🤖";

    const bubble = document.createElement("div");
    bubble.className = "bubble";
    bubble.innerHTML = escapeHtml(text).replace(/\n/g, "<br>");

    wrapper.appendChild(avatar);
    wrapper.appendChild(bubble);
    messagesEl.appendChild(wrapper);
    messagesEl.scrollTop = messagesEl.scrollHeight;
    return wrapper;
  }

  function setLoading(loading) {
    sendBtn.disabled = loading;
    inputEl.disabled = loading;
    typingEl.classList.toggle("hidden", !loading);
    if (loading) messagesEl.scrollTop = messagesEl.scrollHeight;
  }

  // Auto-resize textarea
  function resizeInput() {
    inputEl.style.height = "auto";
    inputEl.style.height = Math.min(inputEl.scrollHeight, 160) + "px";
  }

  // ---- Welcome screen ----

  function showWelcome() {
    const div = document.createElement("div");
    div.className = "welcome";
    div.innerHTML =
      "<strong>Welcome! I'm your AI Agent 👋</strong>" +
      "I can calculate, tell the time, search the web, and convert units.<br>" +
      "Try: <em>'What is 12 * 8?'</em> or <em>'Convert 100 km to miles'</em>";
    messagesEl.appendChild(div);
  }

  // ---- Send message ----

  async function sendMessage(text) {
    if (!text.trim()) return;

    appendMessage("user", text);
    history.push({ role: "user", content: text });

    setLoading(true);

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ messages: history }),
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: res.statusText }));
        throw new Error(err.detail || "Request failed");
      }

      const data = await res.json();

      // Append assistant and tool messages to local history
      for (const msg of data.messages) {
        if (msg.role === "assistant" || msg.role === "tool") {
          history.push({ role: msg.role, content: msg.content || "" });
        }
      }

      appendMessage("assistant", data.reply);
    } catch (err) {
      appendMessage("error", "Error: " + err.message);
    } finally {
      setLoading(false);
    }
  }

  // ---- Event listeners ----

  formEl.addEventListener("submit", function (e) {
    e.preventDefault();
    const text = inputEl.value.trim();
    if (!text) return;
    inputEl.value = "";
    resizeInput();
    sendMessage(text);
  });

  inputEl.addEventListener("keydown", function (e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      formEl.dispatchEvent(new Event("submit"));
    }
  });

  inputEl.addEventListener("input", resizeInput);

  // ---- Init ----

  showWelcome();
  inputEl.focus();
})();
