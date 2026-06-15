document.addEventListener("DOMContentLoaded", () => {
    const userInput = document.getElementById("user-input");
    const sendBtn = document.getElementById("send-btn");
    const chatBox = document.getElementById("chat-box");
    const characterAnim = document.getElementById("character-anim");
    const confirmPassField = document.getElementById("confirm-pass");

    // 1. Reactive Password Typing (Triggers bouncing physics on character)
    if (confirmPassField && characterAnim) {
        confirmPassField.addEventListener("input", () => {
            if (confirmPassField.value.length > 0) {
                characterAnim.classList.add("character-typing-action");
            } else {
                characterAnim.classList.remove("character-typing-action");
            }
        });
    }

    // 2. Chat messaging flow 
    if (sendBtn && userInput) {
        const executeMessageSend = () => {
            const secureText = userInput.value.trim();
            if (secureText === "") return;

            // Generate clean User Bubble structure
            const userBubble = document.createElement("div");
            userBubble.className = "chat-bubble user-bubble";
            userBubble.innerText = secureText;
            chatBox.appendChild(userBubble);

            userInput.value = "";
            chatBox.scrollTop = chatBox.scrollHeight;

            // Simulate CutiBot responding dynamically
            setTimeout(() => {
                const botBubble = document.createElement("div");
                botBubble.className = "chat-bubble bot-bubble";
                botBubble.innerText = "I am very happy today because I can talk with you! 🥰";
                chatBox.appendChild(botBubble);
                chatBox.scrollTop = chatBox.scrollHeight;
            }, 750);
        };

        sendBtn.addEventListener("click", executeMessageSend);
        userInput.addEventListener("keypress", (e) => {
            if (e.key === "Enter") executeMessageSend();
        });
    }
});
