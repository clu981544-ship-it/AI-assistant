# AI Chat Assistant

基于 FastAPI、OpenAI Python SDK 和 DeepSeek API 开发的网页聊天助手，作为后续足球助手的聊天底座。

当前版本使用固定的 `USER_ID = 1` 和 `CONVERSATION_ID = 1`，所有访问者共用一个演示会话。尚未实现登录、动态会话、足球规则 RAG、赛事查询或模型工具调用。

## 功能

- 基于 DeepSeek 的 AI 对话
- 多轮对话上下文
- FastAPI 聊天接口
- 原生 HTML、CSS、JavaScript 聊天页面
- SQLite 聊天记录持久化
- 页面刷新后自动加载当前会话历史
- 固定用户、固定会话演示
- 清空当前演示会话的全部历史
- 仅向模型发送最近 10 条消息，控制上下文长度
- 前端空白输入拦截，以及后端消息列表、正文和角色校验
- Enter 发送消息
- 发送中状态、按钮禁用和请求失败提示
- 基础请求与异常日志、`GET /health` 健康检查
- Dockerfile、Docker Compose、数据库数据卷和容器健康检查
- 离线提取 2026/27 足球规则的 Law 1–17，保留来源、章节和文件页/印刷页信息（尚未接入聊天检索）

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
│   ├── logging_config.py # 日志配置
│   └── main.py         # 早期命令行版本入口
├── frontend/
│   ├── index.html      # 页面结构
│   ├── app.js          # 前端聊天逻辑
│   └── style.css       # 页面样式
├── Dockerfile          # 应用镜像构建
├── compose.yaml        # 容器、数据卷和健康检查配置
├── .env.example        # 环境变量占位示例
├── .env                # 自行创建的本地配置，不提交到 Git
├── .gitignore
├── requirements.txt
└── README.md
```

## 本地运行

需要 Python 3.11 和可用的 DeepSeek API Key。以下命令在 Windows PowerShell 中执行；调用真实模型需要网络连接，并可能产生 API 费用。

### 1. 进入项目并创建虚拟环境

以下示例使用当前项目目录；其他机器请替换为实际克隆目录。已有 `venv` 时跳过创建步骤。

```powershell
Set-Location 'D:\AI.project\AI-assiant'
python -m venv venv
```

后续直接使用虚拟环境中的 Python，无需先激活环境。

### 2. 安装依赖

```powershell
.\venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 3. 配置环境变量

在项目根目录复制示例配置；下面的命令不会覆盖已有 `.env`：

```powershell
if (-not (Test-Path -LiteralPath '.env')) {
    Copy-Item -LiteralPath '.env.example' -Destination '.env'
}
```

编辑 `.env`，将占位符替换为自己的 Key。不要提交真实 Key：

```env
APP_NAME=AI Chat Assistant
DEEPSEEK_API_KEY=your_deepseek_api_key_here
```

当前模型和地址在 `app/config.py` 中固定为 `deepseek-chat` 和 `https://api.deepseek.com`；`.env` 不支持覆盖这两个设置。

### 4. 启动服务

在项目根目录运行：

```powershell
.\venv\Scripts\python.exe -m uvicorn app.api:app --reload --port 8000
```

保持启动终端运行，打开 [聊天页面](http://127.0.0.1:8000/) 或 [接口文档](http://127.0.0.1:8000/docs)。服务启动后，在另一个 PowerShell 终端执行：

```powershell
Invoke-RestMethod -Uri 'http://127.0.0.1:8000/health'
```

预期返回 `status` 为 `ok`。按 `Ctrl+C` 停止本地服务。

## Docker Compose 运行

需要安装并启动 Docker Desktop，使用 Linux 容器模式，且 `docker compose` 可用。以下命令仍在项目根目录的 PowerShell 终端运行。

### 1. 配置环境变量并释放端口

按上面的本地运行步骤准备 `.env` 和真实 Key。若本地 Uvicorn 正占用 8000 端口，先在其终端按 `Ctrl+C`；容器也会使用宿主机的 8000 端口。

### 2. 准备外部数据卷并启动

`compose.yaml` 将 `ai-chat-data` 声明为外部数据卷，因此需要在首次启动前创建。对已有同名数据卷执行创建命令会复用它。

```powershell
docker volume create ai-chat-data
docker compose up -d --build
docker compose ps
docker compose logs --tail 50 app
```

容器启动并通过健康检查后，访问同一个 [聊天页面](http://127.0.0.1:8000/)。

### 3. 数据位置与停止方式

- 本地运行默认使用项目根目录的 `chat.db`；可在启动前通过环境变量 `DATABASE_PATH` 指定其他路径，其父目录需要已存在。
- 容器使用 `/data/chat.db`，由 `ai-chat-data` 数据卷保存，容器重建后可继续读取。
- 本地数据库与容器数据卷中的数据库相互独立，切换运行方式不会自动迁移历史。
- 容器健康检查访问 `/health`，间隔 30 秒、超时 5 秒、重试 3 次，启动宽限期为 10 秒。

停止并移除本项目容器：

```powershell
docker compose down
```

该命令保留外部数据卷。不要删除 `ai-chat-data`，除非确认不再需要其中的聊天历史。

## API 接口

### `GET /health`

检查服务是否正常运行。

此接口仅检查应用能否响应，不验证 DeepSeek API Key、模型服务或数据库读写是否正常。

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

请求须满足：

- `messages` 是至少包含一条消息的列表。
- 每条消息的 `role` 只能是 `user` 或 `assistant`。
- `content` 必须是非空白字符串；校验通过后保留原始正文。
- 最后一条消息必须为 `user`，表示本次用户输入。

缺少必填字段、字段类型错误或不满足以上规则时，接口返回 `422`，`detail` 中包含错误位置和原因，不进入消息保存和模型调用。

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

当前所有访问者共用演示会话，因此此操作会清空该会话的全部历史。

响应示例：

```json
{
  "message": "会话已经清空"
}
```

## 当前实现说明

- 前端加载时通过 `/history` 读取数据库历史，恢复页面和前端消息数组；发送请求时提交该数组。
- `/chat` 使用请求中的最近 10 条消息调用模型，不会自行查询数据库补齐上下文。10 条指消息条数，不是 10 轮对话。
- 输入校验通过后，先保存本次用户消息，再调用模型，成功后保存模型回答。模型调用失败时，用户消息可能已经保存。
- 聊天处理中的数据库或模型异常目前统一返回 `500` 和“模型服务调用失败”；该提示尚不能区分真实失败原因，需要结合后端日志排查。
- 前端聊天失败时显示通用提示，尚未展示后端返回的具体校验原因；历史加载和清空失败的提示也待完善。
- `.env`、API Key、数据库和真实敏感资料不应提交到 GitHub。
- 尚未实现登录权限、动态会话、流式输出、足球规则 RAG、赛事查询、问题路由和工具调用。
- 尚未建立完整的固定测试集和效果报告。

## Day 1 手动验证

启动服务后，按以下顺序检查：

1. `/health` 返回 `200` 和 `{"status":"ok"}`。
2. 网页发送正常问题并得到回答；发送包含测试标记的消息，刷新后历史仍在，追问能使用该标记。
3. 需要保留的历史先备份，再点击“清空会话”；刷新后页面仍为空，`/history` 返回 `{"messages":[]}`。
4. 通过接口提交空列表、空正文、纯空白正文、非法角色或以 `assistant` 结尾的列表，均应返回 `422`，且错误原因与输入对应。
5. 非法请求不增加历史记录；校验完成后，网页正常两轮聊天仍可用。

例如，在另一个 PowerShell 终端发送空列表；此请求应在调用模型前被拒绝：

```powershell
try {
    Invoke-RestMethod -Uri 'http://127.0.0.1:8000/chat' -Method Post -ContentType 'application/json' -Body '{"messages":[]}'
} catch {
    Write-Output ("HTTP 状态码：{0}" -f [int]$_.Exception.Response.StatusCode)
    Write-Output $_.ErrorDetails.Message
}
```

预期状态码为 `422`，错误指向 `body.messages`，原因为列表长度不足，而不是缺少其他字段或服务内部错误。

## 足球规则文档处理（Day 2）

已建立当前 2026/27 双页 PDF 的读取、半页拆分、页脚清理和 JSONL 输出流程。完整范围、运行命令、字段解释、抽查结果和图示限制见 [规则处理与验收记录](docs/rules-processing.md)。

在项目根目录的 Windows PowerShell 中执行：

```powershell
.\venv\Scripts\python.exe -m pip install -r requirements-docs.txt
.\venv\Scripts\python.exe -X utf8 scripts/process_rules.py
.\venv\Scripts\python.exe -X utf8 -m unittest discover -s tests -v
```

需要自行准备说明中指定的源 PDF。当前生成 108 条页面记录；17 张章节封面保留未知页码，9 张照片页没有正文。图示文字不包含完整图形语义，输出需要筛选后再进行切分，不能直接作为完整规则知识片段。此流程在本地离线执行；应用 Dockerfile 尚未安装文档处理依赖，聊天接口也尚未使用这些记录。

## 工程实践与后续计划

后续按 [工程实践与验收安排](docs/engineering-plan.md) 增加会话隔离、数据一致性、依赖超时、并发压测、瓶颈定位与部署验证。当前尚无性能测量结果。

1. 对已提取文本按章节和规则条目切分，保留来源、适用版本和跨页关联。
2. 完成向量入库、独立检索验证、RAG 回答与真实来源引用。
3. 增加一种赛事查询工具，再接入问题路由与有限轮数的模型工具调用。
4. 建立固定评测问题、失败案例、部署说明和演示步骤。

以上为计划功能，当前不能作为已完成能力描述。
