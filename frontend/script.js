let sessionId = null;

function addMessage(text, sender, suggestions = []) {
    const chatBox = document.getElementById("chat-box");

    const msg = document.createElement("div");
    msg.className = `message ${sender}`;
    msg.innerText = text;
    chatBox.appendChild(msg);

    if (suggestions.length > 0) {
        const sugDiv = document.createElement("div");
        sugDiv.className = "suggestions";

        suggestions.forEach(s => {
            const btn = document.createElement("button");
            btn.innerText = s;
            btn.onclick = () => sendSuggestion(s);
            sugDiv.appendChild(btn);
        });

        chatBox.appendChild(sugDiv);
    }

    chatBox.scrollTop = chatBox.scrollHeight;
}

function sendMessage() {
    const input = document.getElementById("user-input");
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
            data.responses.forEach(r => {
                addMessage(r.answer, "bot", r.suggestions);
            });
        });
}

function sendSuggestion(text) {
    document.getElementById("user-input").value = text;
    sendMessage();
}
