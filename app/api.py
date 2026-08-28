from fastapi import FastAPI #创建一个web api 应用
from pydantic import BaseModel #定义前端发来的json
from app.llm import chat
app=FastAPI()#创建一个后端服务应用
class ChatRequest(BaseModel):#规定请求的格式
    message: str#字符串
@app.get("/")  #get 接口 访问了就会执行root
def root():
    return {
        "message": "AI Chat Assistant API"
    }
@app.get("/health")
def health():
    return{
        "status":"ok"
    }
@app.post("/chat")  #当客户端向 /chat 这个地址发送 POST 请求时，FastAPI 就执行下面这个函数。
def chat_api(request: ChatRequest):
    messages=[
        {
            "role":"user",
            "content":request.message,
        }
    ]
    answer=chat(messages)
    return {
        "answer":answer
    }