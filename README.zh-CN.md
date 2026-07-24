# 知识库问答服务

[English](README.md)

[![CI](https://github.com/xyh-wiki/rag-support-bot/actions/workflows/ci.yml/badge.svg)](https://github.com/xyh-wiki/rag-support-bot/actions/workflows/ci.yml)

在线演示: https://bot.xyh.wiki

![Knowledge Base Assistant preview](assets/social-preview.png)

一个用于产品文档、内部手册、制度文件和支持资料的自托管文档问答服务。
它会索引本地文件,根据用户问题检索相关章节,再流式返回带引用来源的回答。

支持格式:Markdown、纯文本、PDF、Word(`.docx`)、Excel(`.xlsx`)和 HTML。

## 功能

- 按文档结构切分内容。
- 使用内存 BM25 检索,不依赖向量数据库。
- 监听文档目录变化,自动重建索引。
- 通过 Server-Sent Events 流式输出。
- 回答前先返回来源列表。
- 没有配置补全接口 key 时,仍可返回命中的原文片段。
- 提供本站专用的浮动问答组件。

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
| `PUBLIC_ORIGIN` | 唯一允许调用问答接口的展示站点来源 | 根据当前请求判断 |
| `DOCS_DIR` | 知识库目录 | `docs/` |
| `SYSTEM_PROMPT_FILE` | 自定义系统提示词文件 | 内置提示词 |
| `SHOW_KB_PANEL` | 是否在页面显示已加载文档 | `false` |
| `SHOW_SOURCES` | 是否发送并展示文档来源，同时要求模型附带引用 | `true` |

## 访问限制

这是一个仅供本站展示的问答页面，不提供跨域嵌入或第三方 API 接入。`POST /api/chat`
会校验 `Origin` 和浏览器 Fetch Metadata，只接受 `PUBLIC_ORIGIN` 页面发起的同源请求；无来源及
跨站请求均返回 HTTP 403。每个 IP 仍受 `RATE_LIMIT_PER_MIN` 限制。

## 内部 HTTP 接口

`POST /api/chat`

```json
{
  "message": "如何重置密码?",
  "history": []
}
```

响应是 SSE 流:

- `sources`:来源列表，仅在 `SHOW_SOURCES=true` 时发送
- `token`:回答文本片段
- `done`:结束

其他接口:

- `GET /api/config`
- `GET /api/health`
- `GET /api/kb`,仅在 `SHOW_KB_PANEL=true` 时可用

## 使用场景

- 客服知识库
- 内部文档检索
- 制度、合规、流程问答
- PDF、Word、Excel 文档检索
- 独立的产品知识库演示页面

更多说明见 `docs-public/use-cases.md`。

## 工作流程

1. `rag/ingest.py` 读取文件并按结构切分:Markdown/HTML/Word 按标题,PDF 按页,
   Excel 按工作表和行。
2. `rag/retriever.py` 对文档块分词并建立 BM25 索引。中文、日文、韩文使用双字切分。
3. `rag/index.py` 计算文档目录指纹,文件变化后在后台重建索引。
4. `app.py` 根据问题检索最相关的文档块,把这些片段放入提示词,然后流式返回回答。
5. `static/widget.js` 和 `static/widget.css` 渲染本站问答组件并消费 SSE 流。

语料规模较大时,可以把检索器替换成向量检索,摄取层和 HTTP 层不需要跟着改。

## 生产更新流程

源代码、运行目录和知识库文档应分开管理。每次发布建议按以下顺序执行：

1. 拉取已审核的源码版本，并在服务虚拟环境中安装依赖。
2. 同步应用文件和静态资源，确保 `widget.js` 与 `widget.css` 同时更新。
3. 重启服务，然后通过公网反向代理验证 `/api/health`、`/api/config`、页面资源和一次
   本站真实问答。
4. 更新静态资源版本参数，然后强制刷新展示页面，避免旧缓存掩盖发布问题。

将 `DOCS_DIR` 指向的目录作为知识库唯一事实来源，只更新其中的原始文档，不要手工修改
生成的索引数据。服务会根据文档指纹自动重建内存索引；每次更新文档后，应使用包含新事实
的真实问题进行验证。产品版本信息应直接写进文档，并在每次产品发布时同步更新或删除过期
页面。

## 开发

```bash
python3 -m pytest tests/ -q
node --check static/widget.js
python3 -m pytest tests/test_widget_assets.py -q
```

项目包含 Docker 部署文件:

- `Dockerfile`
- `docker-compose.yml`
- `.dockerignore`

生产镜像使用 `requirements.lock`，以非 root 的 `993:993` 用户运行，并包含健康检查。
`xyh-dep` 独立展示部署详见 `deploy/xyh-dep/README.md`；该部署必须使用单独容器和回环端口，
不得复用现有支持 Bot 的私有文档或凭据。

## 许可证

MIT
