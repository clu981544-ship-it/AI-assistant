const messages = [];//保存历史记录


function handleKeyDown(event) {
    if (event.key === "Enter") {
        sendMessage();
    }
}


async function sendMessage() {
    const input = document.getElementById("messageInput");
    const chatBox = document.getElementById("chatBox");
    const sendButton = document.getElementById("sendButton");
    const userText = input.value.trim();

    if (sendButton.disabled) {
        return;
    }

    if (userText === "") {
        return;
    }

    const userMessage = document.createElement("div");
    userMessage.className = "message user-message";
    userMessage.innerText = "用户：" + userText;
    chatBox.appendChild(userMessage);

    messages.push({
        role: "user",
        content: userText,
    });

    const aiMessage = document.createElement("div");
    aiMessage.className = "message ai-message";
    aiMessage.innerText = "AI 正在思考...";
    chatBox.appendChild(aiMessage);

    sendButton.disabled = true;
    sendButton.innerText = "发送中...";

    try {
        const response = await fetch("/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                messages: messages,
            }),
        });

        if (!response.ok) {
            throw new Error("Chat request failed");
        }

        const data = await response.json();

        aiMessage.innerText = "AI：" + data.answer;

        messages.push({
            role: "assistant",
            content: data.answer,
        });
    } catch (error) {
        aiMessage.innerText = "请求失败，请检查后端服务是否正常运行。";
    } finally {
        sendButton.disabled = false;
        sendButton.innerText = "发送";
    }

    input.value = "";
}
