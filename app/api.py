from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.llm import chat


app = FastAPI()


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
    return {
        "message": "AI Chat Assistant API"
    }


@app.get("/health")
def health():
    return {
        "status": "ok"
    }


@app.post("/chat")
def chat_api(request: ChatRequest):
    messages = []

    for message in request.messages:
        messages.append({
            "role": message.role,
            "content": message.content,
        })

    answer = chat(messages)

    return {
        "answer": answer
    }