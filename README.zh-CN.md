# 知识库问答服务

[English](README.md)

[![CI](https://github.com/xyh-wiki/rag-support-bot/actions/workflows/ci.yml/badge.svg)](https://github.com/xyh-wiki/rag-support-bot/actions/workflows/ci.yml)

在线演示: https://bot.xyh.wiki

![Knowledge Base Assistant preview](assets/social-preview.png)

一个用于产品文档、内部手册、制度文件和支持资料的自托管文档问答服务。
它会索引本地文件,根据用户问题检索相关章节,再流式返回带引用来源的回答。

支持格式:Markdown、纯文本、PDF、Word(`.docx`)、Excel(`.xlsx`)和 HTML。

```html
<script
  src="https://your-domain.example/static/widget.js"
  data-api-base="https://your-domain.example">
</script>
```

## 功能

- 按文档结构切分内容。
- 使用内存 BM25 检索,不依赖向量数据库。
- 监听文档目录变化,自动重建索引。
- 通过 Server-Sent Events 流式输出。
- 回答前先返回来源列表。
- 没有配置补全接口 key 时,仍可返回命中的原文片段。
- 提供可嵌入其他网站的浮动聊天挂件。

## 快速开始

Python:

```bash
pip install -r requirements.txt
cp .env.example .env
export OPENAI_API_KEY=sk-...
uvicorn app:app --reload
```

Docker Compose:

```bash
cp .env.example .env
docker compose up --build
```

打开 `http://localhost:8000`。

如果没有设置 `OPENAI_API_KEY`,服务会进入纯检索模式:返回最相关的文档片段和引用,
但不会生成归纳式回答。

## 配置

| 变量 | 说明 | 默认值 |
|---|---|---|
| `OPENAI_API_KEY` | 生成回答所需的 key | 未设置 |
| `OPENAI_BASE_URL` | OpenAI 兼容接口地址 | 官方 API |
| `MODEL` | 生成回答使用的模型 | `gpt-5.4` |
| `TOP_K` | 每次检索的文档块数量 | `4` |
| `RATE_LIMIT_PER_MIN` | 每 IP 每分钟请求上限 | `30` |
| `BOT_NAME` | 页面和默认提示词中的产品名 | `Knowledge Base` |
| `BOT_TAGLINE` | 页面副标题 | 示例文案 |
| `BOT_PLACEHOLDER` | 输入框占位文字 | 示例文案 |
| `BOT_LANG` | 页面语言(`en`、`zh-CN` 等) | `en` |
| `DOCS_DIR` | 知识库目录 | `docs/` |
| `SYSTEM_PROMPT_FILE` | 自定义系统提示词文件 | 内置提示词 |
| `SHOW_KB_PANEL` | 是否在页面显示已加载文档 | `false` |
| `ALLOWED_ORIGINS` | 允许跨域调用的来源,逗号分隔 | 仅同源 |

## 嵌入网页

```html
<script
  src="https://your-domain.example/static/widget.js"
  data-api-base="https://your-domain.example">
</script>
```

加上 `data-open="true"` 可以让聊天窗在页面加载后自动展开。

跨域嵌入时需要设置:

```bash
export ALLOWED_ORIGINS=https://your-site.com
```

### 内容安全策略（CSP）

挂件使用 Shadow DOM 隔离界面，并通过内联 `<style>` 元素加载组件样式。因此，启用严格
CSP 的宿主网站需要同时允许挂件脚本、接口连接和内联组件样式。如果通过
`/support-bot/` 等路径做同源反向代理，可使用以下最小兼容策略：

```http
Content-Security-Policy: default-src 'self'; script-src 'self'; connect-src 'self'; style-src 'self' 'unsafe-inline'
```

跨域部署时，还需要在 `script-src` 和 `connect-src` 中允许机器人域名，并在机器人服务中
配置 `ALLOWED_ORIGINS`：

```http
Content-Security-Policy: default-src 'self'; script-src 'self' https://bot.example.com; connect-src 'self' https://bot.example.com; style-src 'self' 'unsafe-inline'
```

应继续把 `script-src` 限制在可信来源。挂件脚本不需要开启脚本级别的
`'unsafe-inline'`。

如果右下角没有出现机器人按钮，请检查浏览器控制台是否存在 `style-src` CSP 拒绝，确认
`widget.js` 和 `/api/config` 均返回 HTTP 200，并在部署后强制刷新宿主页面。

最小嵌入示例见 `examples/embed.html`。

## HTTP API

`POST /api/chat`

```json
{
  "message": "如何重置密码?",
  "history": []
}
```

响应是 SSE 流:

- `sources`:来源列表
- `token`:回答文本片段
- `done`:结束

其他接口:

- `GET /api/config`
- `GET /api/health`
- `GET /api/kb`,仅在 `SHOW_KB_PANEL=true` 时可用

命令行 SSE 示例见 `examples/curl-sse.sh`。

## 使用场景

- 客服知识库
- 内部文档检索
- 制度、合规、流程问答
- PDF、Word、Excel 文档检索
- 嵌入现有网站的右下角聊天挂件

更多说明见 `docs-public/use-cases.md`。

## 工作流程

1. `rag/ingest.py` 读取文件并按结构切分:Markdown/HTML/Word 按标题,PDF 按页,
   Excel 按工作表和行。
2. `rag/retriever.py` 对文档块分词并建立 BM25 索引。中文、日文、韩文使用双字切分。
3. `rag/index.py` 计算文档目录指纹,文件变化后在后台重建索引。
4. `app.py` 根据问题检索最相关的文档块,把这些片段放入提示词,然后流式返回回答。
5. `static/widget.js` 渲染右下角聊天挂件并消费 SSE 流。

语料规模较大时,可以把检索器替换成向量检索,摄取层和 HTTP 层不需要跟着改。

## 开发

```bash
python3 -m pytest tests/ -q
node --check static/widget.js
```

项目包含 Docker 部署文件:

- `Dockerfile`
- `docker-compose.yml`
- `.dockerignore`

## 许可证

MIT
