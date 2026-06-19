let currentSessionId = null;

document.addEventListener("DOMContentLoaded", () => {
    // Session click binding configuration
    document.querySelectorAll(".session-item").forEach(item => {
        item.addEventListener("click", () => switchSession(item.dataset.id));
    });

    document.getElementById("new-chat-btn").addEventListener("click", createNewSession);
    document.getElementById("send-btn").addEventListener("click", sendMessage);
    document.getElementById("user-input").addEventListener("keypress", (e) => {
        if (e.key === "Enter") sendMessage();
    });
    
    // Voice Registration Init
    initVoiceInput();
    document.getElementById("export-btn").addEventListener("click", exportChatHistory);
});

function toggleDarkMode() {
    const body = document.body;
    const icon = document.getElementById("dark-mode-icon");
    if (body.getAttribute("data-theme") === "dark") {
        body.removeAttribute("data-theme");
        icon.className = "fa fa-moon";
    } else {
        body.setAttribute("data-theme", "dark");
        icon.className = "fa fa-sun";
    }
}

function toggleModal(id) {
    const modal = document.getElementById(id);
    modal.style.display = (modal.style.display === "flex") ? "none" : "flex";
}

async function createNewSession() {
    const res = await fetch("/sessions/new", { method: "POST" });
    const data = await res.json();
    if (data.session_id) {
        window.location.reload(); // Quick refresh to update systemic lists
    }
}

async function switchSession(sessionId) {
    currentSessionId = sessionId;
    document.querySelectorAll(".session-item").forEach(i => i.classList.remove("active"));
    document.querySelector(`[data-id="${sessionId}"]`).classList.add("active");
    
    document.getElementById("user-input").disabled = false;
    document.getElementById("send-btn").disabled = false;

    const res = await fetch(`/sessions/${sessionId}/messages`);
    const messages = await res.json();
    
    const container = document.getElementById("messages-container");
    container.innerHTML = "";
    
    messages.forEach(msg => {
        appendMessageElement(msg.sender, msg.message_text, msg.sentiment);
    });
    scrollToBottom();
}

async function sendMessage() {
    const input = document.getElementById("user-input");
    const text = input.value.trim();
    if (!text || !currentSessionId) return;

    input.value = "";
    appendMessageElement("user", text);
    scrollToBottom();

    // Show Real-time Typing Animation
    const typingIndicator = document.getElementById("typing-indicator");
    typingIndicator.style.display = "block";

    const res = await fetch(`/chat/${currentSessionId}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text })
    });
    const data = await res.json();
    
    typingIndicator.style.display = "none";
    
    // Append Bot message and update last user message with analyzed sentiment feedback
    appendMessageElement("bot", data.reply);
    if(data.sentiment) {
        const userBubbles = document.querySelectorAll(".msg-bubble.user");
        if(userBubbles.length > 0) {
             const lastBubble = userBubbles[userBubbles.length - 1];
             const sentimentSpan = document.createElement("span");
             sentimentSpan.className = "sentiment-badge";
             sentimentSpan.innerText = `Sentiment: ${data.sentiment}`;
             lastBubble.appendChild(sentimentSpan);
        }
    }
    scrollToBottom();
}

function appendMessageElement(sender, text, sentiment = null) {
    const container = document.getElementById("messages-container");
    const bubble = document.createElement("div");
    bubble.className = `msg-bubble ${sender}`;
    bubble.innerText = text;
    
    if (sender === 'user' && sentiment) {
        const sentimentSpan = document.createElement("span");
        sentimentSpan.className = "sentiment-badge";
        sentimentSpan.innerText = `Sentiment: ${sentiment}`;
        bubble.appendChild(sentimentSpan);
    }
    
    container.appendChild(bubble);
}

function scrollToBottom() {
    const container = document.getElementById("messages-container");
    container.scrollTop = container.scrollHeight;
}

// Advanced Feature: Web Speech Voice Synthesis Recognition Input
function initVoiceInput() {
    const voiceBtn = document.getElementById("voice-btn");
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    
    if (!SpeechRecognition) {
        voiceBtn.style.display = "none";
        return;
    }
    
    const recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.lang = 'en-US';
    
    voiceBtn.addEventListener("click", () => {
        voiceBtn.style.color = "#d32f2f";
        recognition.start();
    });
    
    recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        document.getElementById("user-input").value = transcript;
        voiceBtn.style.color = "#888";
    };
    
    recognition.onerror = () => { voiceBtn.style.color = "#888"; };
    recognition.onend = () => { voiceBtn.style.color = "#888"; };
}

// Advanced Feature: Client Side Conversational Data Export
function exportChatHistory() {
    const bubbles = document.querySelectorAll(".msg-bubble");
    let logText = "";
    bubbles.forEach(b => {
        const speaker = b.classList.contains("user") ? "User" : "AI Bot";
        logText += `[${speaker}]: ${b.innerText}\n`;
    });
    
    if(!logText) return alert("No active history stream elements found to export.");
    
    const blob = new Blob([logText], { type: "text/plain" });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = `chat_session_${currentSessionId || 'export'}.txt`;
    link.click();
}
