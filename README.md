# AI Chat Assistant

基于 FastAPI、OpenAI SDK 和 DeepSeek API 开发的 AI 聊天助手。项目提供网页聊天界面、SQLite 聊天记录持久化、基础会话隔离和错误提示等功能。

## 功能

- 基于 DeepSeek 的 AI 对话
- 多轮对话上下文
- FastAPI 聊天接口
- 原生 HTML、CSS、JavaScript 聊天页面
- SQLite 聊天记录持久化
- 页面刷新后自动加载当前会话历史
- 基础会话隔离
- 清空当前会话
- 仅向模型发送最近 10 条消息，控制上下文长度
- 空输入校验
- Enter 发送消息
- 发送中状态、按钮禁用和请求失败提示

## 技术栈

- Python
- FastAPI
- Uvicorn
- OpenAI Python SDK
- DeepSeek API
- SQLite
- HTML / CSS / JavaScript

## 项目结构

```text
AI-assiant/
├── app/
│   ├── api.py          # FastAPI 路由和接口逻辑
│   ├── config.py       # 读取环境变量和模型配置
│   ├── database.py     # SQLite 数据库操作
│   ├── llm.py          # DeepSeek 模型调用
│   └── main.py         # 早期命令行版本入口
├── frontend/
│   ├── index.html      # 页面结构
│   ├── app.js          # 前端聊天逻辑
│   └── style.css       # 页面样式
├── .env                # 本地 API Key 配置，不提交到 Git
├── .gitignore
├── requirements.txt
└── README.md
```

## 本地运行

### 1. 创建并激活虚拟环境

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 2. 安装依赖

```powershell
python -m pip install -r requirements.txt
```

### 3. 配置环境变量

在项目根目录创建 `.env` 文件：

```env
APP_NAME=AI Chat Assistant
DEEPSEEK_API_KEY=你的 DeepSeek API Key
```

### 4. 启动服务

在项目根目录运行：

```powershell
python -m uvicorn app.api:app --reload --port 8000
```

打开浏览器访问：

```text
http://127.0.0.1:8000/
```

接口文档：

```text
http://127.0.0.1:8000/docs
```

## Docker Compose 运行

### 1. 配置环境变量

在项目根目录创建 `.env` 文件：

```env
APP_NAME=AI Chat Assistant
DEEPSEEK_API_KEY=你的 DeepSeek API Key

## API 接口

### `GET /health`

检查服务是否正常运行。

响应示例：

```json
{
  "status": "ok"
}
```

### `GET /history`

读取当前会话的聊天记录。

响应示例：

```json
{
  "messages": [
    {
      "role": "user",
      "content": "你好"
    },
    {
      "role": "assistant",
      "content": "你好，有什么可以帮你的吗？"
    }
  ]
}
```

### `POST /chat`

向模型发送聊天消息。

请求示例：

```json
{
  "messages": [
    {
      "role": "user",
      "content": "什么是 FastAPI？"
    }
  ]
}
```

响应示例：

```json
{
  "answer": "FastAPI 是一个用于构建 Web API 的 Python 框架。"
}
```

### `DELETE /conversation`

删除当前会话的聊天记录。

响应示例：

```json
{
  "message": "会话已经清空"
}
```

## 当前实现说明

- 当前项目使用固定的 `USER_ID = 1` 和 `CONVERSATION_ID = 1`。
- 数据库会保存完整的当前会话记录。
- 模型调用时只使用最近 10 条消息，避免上下文无限增长。
- `.env` 中的 API Key 不应提交到 GitHub。
- 当前项目还没有登录系统、动态新建会话、Docker 部署和流式输出。

## 后续计划

- 支持动态创建和切换聊天会话
- 增加日志和更细化的异常处理
- 完善 `.env.example`
- 使用 Docker 容器化运行
- 部署到服务器
- 开发 AI Knowledge Base Assistant（RAG）
