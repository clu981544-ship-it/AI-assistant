from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.llm import chat
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.database import init_db, save_message, get_history,clear_conversation
from app.logging_config import logger

app = FastAPI()
USER_ID = 1
CONVERSATION_ID = 1
init_db()
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: list[Message]


@app.get("/")
def root():
    return FileResponse("frontend/index.html")


@app.get("/health")
def health():
    logger.info("健康检查请求成功")
    return {
        "status": "ok"
    }
    
@app.get("/history")
def history():
    logger.info("正在读取聊天历史")
    return {
        "messages":get_history(USER_ID, CONVERSATION_ID)
    }
@app.delete("/conversation")
def clear_current_conversation():
    clear_conversation(USER_ID,CONVERSATION_ID)
    logger.info("会话已空")
    return{
        "message":"会话已经清空"
    }
@app.post("/chat")
def chat_api(request: ChatRequest):
    messages = []

    for message in request.messages:
        messages.append({
            "role": message.role,
            "content": message.content,
        })

    try:
        logger.info("收到聊天请求，消息数量：%s", len(messages))
        save_message(USER_ID,CONVERSATION_ID, "user", messages[-1]["content"])#-1表示最新的一条消息，就是本次用户输入
        recent_messages=messages[-10:]
        answer = chat(recent_messages)
        save_message(USER_ID,CONVERSATION_ID, "assistant", answer)#大写代表是常量
        logger.info("聊天请求处理成功")
        return {
            "answer": answer
        }

    except Exception:
        logger.exception("聊天请求处理失败")
        raise HTTPException(
            status_code=500,
            detail="模型服务调用失败"
        )
