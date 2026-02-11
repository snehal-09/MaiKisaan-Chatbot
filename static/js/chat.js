const chatBox = document.getElementById("chat-box");
const input = document.getElementById("message");
const chatbot = document.getElementById("chatbot");
const languageBox = document.getElementById("language-box");
const inputArea = document.getElementById("input-area");

let userLanguage = null;
let typingDiv = null;

/* Toggle chatbot */
function toggleChat() {
    chatbot.classList.toggle("hidden");
}

/* Select language */
function selectLanguage(lang) {
    userLanguage = lang;

    languageBox.classList.add("hidden");
    chatBox.classList.remove("hidden");
    inputArea.classList.remove("hidden");

    let welcomeMsg = "";

    if (lang === "mr") {
        welcomeMsg =
            "नमस्कार 🙏 मी MaiKisaan सहाय्यक आहे.\n" +
            "मी तुमची कशी मदत करू शकतो?\n" +
            "पीक, खत, कीड, हवामान किंवा शासकीय योजना याबाबत विचारा.";
        input.placeholder = "आपला सवाल लिहा…";
    }
    else if (lang === "hi") {
        welcomeMsg =
            "नमस्कार 🙏 मैं MaiKisaan सहायक हूँ।\n" +
            "मैं आपकी कैसे मदद कर सकता हूँ?\n" +
            "फसल, खाद, कीट, मौसम या सरकारी योजनाओं के बारे में पूछें।";
        input.placeholder = "अपना सवाल लिखें…";
    }
    else {
        welcomeMsg =
            "Hello 👋 I am MaiKisaan Assistant.\n" +
            "How can I help you?\n" +
            "Ask about crops, fertilizer, pests, weather or schemes.";
        input.placeholder = "Type your question…";
    }

    addMessage(welcomeMsg, "bot");
}

/* Enter key */
input.addEventListener("keypress", function (e) {
    if (e.key === "Enter") sendMessage();
});

/* Add message */
function addMessage(text, sender) {
    const div = document.createElement("div");
    div.className = `message ${sender}`;
    div.innerText = text;
    chatBox.appendChild(div);
    chatBox.scrollTop = chatBox.scrollHeight;
    return div;
}

/* Show typing indicator */
function showTyping() {
    let typingText = "Typing…";
    if (userLanguage === "mr") typingText = "उत्तर तयार करत आहे…";
    if (userLanguage === "hi") typingText = "उत्तर तैयार किया जा रहा है…";

    typingDiv = addMessage(typingText, "bot");
    typingDiv.classList.add("typing");
}

/* Remove typing indicator */
function removeTyping() {
    if (typingDiv) {
        typingDiv.remove();
        typingDiv = null;
    }
}

/* Send message */
function sendMessage() {
    const msg = input.value.trim();
    if (!msg || !userLanguage) return;

    addMessage(msg, "user");
    input.value = "";

    showTyping();

    fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            message: msg,
            language: userLanguage
        })
    })
    .then(res => res.json())
    .then(data => {
        removeTyping();
        addMessage(data.reply, "bot");
    })
    .catch(() => {
        removeTyping();
        addMessage("Server error. Please try again.", "bot");
    });
}
