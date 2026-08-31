from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.llm import chat
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.database import init_db, save_message, get_history

app = FastAPI()
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
    return {
        "status": "ok"
    }
    
@app.get("/history")
def history():
    return {
        "messages": get_history(1)
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
        save_message(1, "user", messages[-1]["content"])#-1表示最新的一条消息，就是本次用户输入
        answer = chat(messages)
        save_message(1, "assistant", answer)

        return {
            "answer": answer
        }

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="模型服务调用失败"
        )
