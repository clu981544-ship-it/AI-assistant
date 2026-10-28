# 足球规则文档处理与 Day 2 验收

## 来源与处理范围

主来源为本地 `knowledge_base/documents/Laws of the Game 2026_27_double pages.pdf`，规则版本为 `2026/27`。下载链接尚未单独核验；通过文件哈希标识本次实际处理的资料，不混入仓库中的 `2016/17` 版或示例文本。

源文件 SHA256：

```text
db0ed5d111e261dfff50ff59596ce352eabe9f71b60b6ba9c153bf6d8063abf3
```

源 PDF 共 131 页，本流程只处理文件第 **23–76 页（含首尾）**，即 Law 1–17 所在双页，不包含后续附录、VAR 等内容。`pdf_page` 从 1 开始，`side` 区分左右半页；`printed_page` 是书上印刷页码，两者不能互换。

`knowledge_base/processed/football-rules-extracted.txt` 是旧实验产物，已发现混入代码，不作为后续切分输入。其他版本和示例资料继续保留。

## 重新生成

在 Windows PowerShell 中运行；其他机器需要替换项目根目录，并自行准备同版本源文件。无需启动网页、配置模型 Key 或调用外部服务。

```powershell
Set-Location 'D:\AI.project\AI-assiant'
.\venv\Scripts\python.exe -m pip install -r requirements-docs.txt
.\venv\Scripts\python.exe -X utf8 scripts/process_rules.py
```

本次环境为 Python 3.11.6、pdfplumber 0.11.9、pypdf 6.16.2。预期输出：

```text
保存记录：108
未解析页码：17
无正文区域：9
```

结果写入 `knowledge_base/processed/rules-2026-27-pages.jsonl`，每行一个 JSON 对象。每次重新生成并覆盖同名输出，不会在文件尾重复追加。执行期间不要让其他进程同时读取或生成此文件；目前写入还没有采用原子替换。

查看元数据：

```powershell
Get-Content -LiteralPath 'knowledge_base/processed/rules-2026-27-pages.jsonl' -Encoding UTF8 |
    ForEach-Object { $_ | ConvertFrom-Json } |
    Select-Object pdf_page, side, printed_page, law_number, law_title, law_source, review_reasons
```

## 脚本调用关系

| 脚本 | 用途 |
| --- | --- |
| `scripts/inspect_rules.py` | 共享项目和来源路径；直接执行时用 pypdf 查看 PDF 第 56 页的原始文本 |
| `scripts/inspect_spread.py` | 提供页码、章节解析函数；直接执行时生成第 56 页的两条教学样本 |
| `scripts/process_rules.py` | 导入路径与解析函数，批量生成本次后续切分使用的页面记录 |

教学样本仍使用底部 40 点裁剪，仅用于已经核对的第 56 页。批量流程采用字符位置和字号筛选页脚，避免把靠近页面底部的正文一起裁掉。

## 处理规则与元数据

1. 按 PDF 文件页序处理，每页按 `left`、`right` 的顺序提取。遇到纵向页面会报错，避免默默套用当前双页布局。
2. 本资料的页脚字符字号为 5.5–6.5 点，字符顶部距底部约 22–31 点；符合两个条件的字符进入 `footer_text`，其余字符进入正文。这是针对当前资料的参数，更换 PDF 后需要重新核对。
3. 正文和页脚均采用 `use_text_flow=True`，使用 PDF 文字流顺序。该方式解决了已抽查正文的部分交错问题，但不保证图表的阅读顺序与视觉语义。
4. 页码解析先排除 `Law 11` 这类章节编号，再寻找独立整数。同一个号码重复出现（例如 `51 51`）按一个号码处理；出现不同候选号码（例如 `51 52`）时仍返回 `null`。不根据文件页序猜填缺失页码。
5. 页脚明确给出章节时标记 `law_source=footer`；只有页码、没有章节时继承之前的明确章节，标记 `previous_footer`；不能确定时保留 `null`，标记 `unresolved`。
6. 缺页码或正文为空时分别记录 `missing_printed_page`、`empty_text`。这两个标记只表示已执行的检查，不是完整的文本质量判定。

| 字段 | 含义 |
| --- | --- |
| `source_file`、`rule_version` | 相对于项目的来源路径、规则版本 |
| `pdf_page`、`side`、`printed_page` | 文件页、半页位置、可解析的印刷页码 |
| `law_number`、`law_title`、`law_source` | 章节编号、标题及其获取依据 |
| `extraction_mode` | 当前均为 `text_only`，没有解析图形关系 |
| `review_reasons` | 当前自动检查发现的问题列表 |
| `footer_text`、`text` | 提取的原始页脚文字、去页脚后的正文 |

## 2026-10-28 验收记录

- 生成 108 条有序记录，`(pdf_page, side)` 无重复；来源文件存在，版本均为 `2026/27`。
- 连续重新生成两次，输出字节一致。当前输出 SHA256 为 `b3bbe91b7bdf30292102e9b2a19dd2ec6734f187c2739c6dfb98ceae0c28e76c`。
- 核对 Law 1–17 的全部 17 处章节切换，非封面记录所属章节与当前封面及后续页脚一致。章节来源统计为：明确页脚 43 条、继承 48 条、未确定 17 条。
- 对 108 个区域比较去页脚后的源字符与输出字符数量，规范化空白和连字后均一致。这项检查验证字符保留，不证明阅读顺序或图示含义正确。
- 结合原 PDF 渲染图抽查正文与顺序：第 31 页左侧、第 50 页左侧的底部正文完整；第 55–56 页的越位内容按左右半页连续提取；第 58 页右侧正确进入 Law 12。
- 第 26 页右侧、第 46 页右侧、第 53 页左侧文字层分别有重复页码 `51 51`、`91 91`、`104 104`；已修正为 51、91、104，并保留原 `footer_text` 供核对。
- 4 项自动回归测试通过，覆盖重复页码、冲突号码、版本与章节编号干扰、缺失元数据。

17 条缺页码记录都是章节封面，位于下列 PDF 页的左侧；已逐一查看渲染图，保留未知值，不将封面的巨大章节数字当页码：

```text
23, 28, 30, 34, 37, 43, 47, 49, 51, 52, 55, 58, 66, 68, 71, 73, 75
```

9 条无正文记录位于下列 PDF 页的右侧；已逐一查看渲染图，均为照片页，并非丢失了规则正文。这里的“无正文”指没有提取出正文文字，不表示视觉上是空白页：

```text
29, 42, 48, 50, 57, 65, 72, 74, 76
```

运行回归测试及重复执行核对：

```powershell
Set-Location 'D:\AI.project\AI-assiant'
.\venv\Scripts\python.exe -X utf8 -m unittest discover -s tests -v
$beforeHash = (Get-FileHash -LiteralPath 'knowledge_base/processed/rules-2026-27-pages.jsonl' -Algorithm SHA256).Hash
.\venv\Scripts\python.exe -X utf8 scripts/process_rules.py
(Get-FileHash -LiteralPath 'knowledge_base/processed/rules-2026-27-pages.jsonl' -Algorithm SHA256).Hash -eq $beforeHash
```

最后一行应返回 `True`。这些统计与哈希只适用于上面记录的源文件、依赖和处理代码。

## 已知边界与 Day 3 交接

- 本次 Day 2 验收通过：建立了可重复执行、可追溯并经代表段落核对的文本提取流程，不代表整本 PDF 完成逐字校对。
- 图示只能提取部分文字。第 26 页右侧的球门图、第 46 页右侧的裁判手势图、第 53 页左侧的进球图、第 59 页右侧的手球示意图等，都需要原图才能理解空间关系；文字层还可能含未显示的标签。这些区域不能仅凭提取文本推导图示结论。
- 图表、表格和照片没有自动完成全面分类；`review_reasons=[]` 也不能证明适合直接检索。页脚继承依赖当前章节顺序，更换资料或处理范围后必须复查。
- 进入 Day 3 后，先过滤封面、照片和需单独处理的图示，核对表格，再按章节与条目切分；跨页规则需保留上下文和来源页列表。不能直接把 108 条页面记录全部当成完整知识片段。
- 样本 JSONL 与批量 JSONL 是本地生成物，可按命令重建；本次提交不包含原 PDF、整本提取文本或旧实验产物。

Day 2 到此结束。下一单元是文档切分与元数据，不在本单元追加向量入库、RAG 接口或并发改造。
