let sessionId = null;

function toggleChat() {
  const box = document.getElementById("chatbot-box");
  box.style.display = box.style.display === "flex" ? "none" : "flex";
}

function addMessage(text, sender) {
  const messages = document.getElementById("chat-messages");
  const div = document.createElement("div");
  div.className = "message " + sender;
  div.innerText = text;
  messages.appendChild(div);
  messages.scrollTop = messages.scrollHeight;
}

function sendMessage() {
  const input = document.getElementById("userInput");
  const text = input.value.trim();
  if (!text) return;

  addMessage(text, "user");
  input.value = "";

  let url = `http://127.0.0.1:8000/chatbot?question=${encodeURIComponent(text)}`;
  if (sessionId) url += `&session_id=${sessionId}`;

  fetch(url)
    .then(res => res.json())
    .then(data => {
      sessionId = data.session_id;
      data.responses.forEach(r => addMessage(r.answer, "bot"));
    });
}
