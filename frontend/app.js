const messages = [];//保存历史记录


function handleKeyDown(event) {
    if (event.key === "Enter") {
        sendMessage();
    }
}

async function loadHistory() {
    const response = await fetch("/history");
    const data = await response.json()//把后端返回的数据解析成 JavaScript 对象

    const chatBox = document.getElementById("chatBox");

    for (const message of data.messages) {//遍历每一条历史消息
        messages.push(message);//把历史消息加入前端的 messages 数组，保证后续继续聊天时模型知道上下文。

        const messageElement = document.createElement("div");

        if (message.role === "user") {
            messageElement.className = "message user-message";
            messageElement.innerText = "用户：" + message.content;
        } else {
            messageElement.className = "message ai-message";
            messageElement.innerText = "AI：" + message.content;
        }

        chatBox.appendChild(messageElement);
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
loadHistory();
