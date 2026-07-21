(function () {
  "use strict";

  const currentScript = document.currentScript;
  const scriptUrl = new URL(currentScript.src, window.location.href);
  const apiBase = (currentScript.dataset.apiBase || scriptUrl.origin).replace(/\/$/, "");
  const startOpen = currentScript.dataset.open === "true";

  function boot() {
  if (document.getElementById("rag-support-widget")) return;
  const rootHost = document.createElement("div");
  rootHost.id = "rag-support-widget";
  document.body.appendChild(rootHost);

  const root = rootHost.attachShadow({ mode: "open" });
  root.innerHTML = `
    <link rel="stylesheet" href="${apiBase}/static/widget.css">
    <section class="panel" aria-label="Knowledge base" aria-hidden="true">
      <header class="header">
        <span class="dot" aria-hidden="true"></span>
        <div class="title">
          <h1>Knowledge Base</h1>
          <p>Answers grounded in the product knowledge base</p>
        </div>
        <button class="kb-toggle" type="button" aria-label="Show knowledge base" aria-expanded="false">Docs</button>
        <button class="close" type="button" aria-label="Close chat">×</button>
      </header>
      <div class="content">
        <main class="conversation" role="log" aria-live="polite" aria-label="Conversation"></main>
        <aside class="kb" aria-label="Knowledge base">
          <h2>Knowledge base</h2>
          <div class="kb-total"></div>
          <div class="kb-docs"></div>
        </aside>
      </div>
      <form aria-label="Ask a question">
        <input autocomplete="off" maxlength="2000" required aria-label="Your question" placeholder="Ask a question…">
        <button class="send" type="submit" aria-label="Send">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <path d="m22 2-7 20-4-9-9-4Z"></path><path d="M22 2 11 13"></path>
          </svg>
        </button>
      </form>
    </section>
    <button class="launcher" type="button" aria-label="Open chat">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
        <path d="M21 15a4 4 0 0 1-4 4H8l-5 3V7a4 4 0 0 1 4-4h10a4 4 0 0 1 4 4z"></path>
      </svg>
    </button>
  `;

  const panel = root.querySelector(".panel");
  const launcher = root.querySelector(".launcher");
  const close = root.querySelector(".close");
  const chat = root.querySelector(".conversation");
  const form = root.querySelector("form");
  const input = root.querySelector("input");
  const send = root.querySelector(".send");
  const title = root.querySelector(".title h1");
  const tagline = root.querySelector(".title p");
  const kbPanel = root.querySelector(".kb");
  const kbTitle = root.querySelector(".kb h2");
  const kbTotal = root.querySelector(".kb-total");
  const kbDocs = root.querySelector(".kb-docs");
  const kbToggle = root.querySelector(".kb-toggle");
  const history = [];
  let lang = "en";
  let librariesLoading = null;
  let kbEnabled = false;
  let showSources = true;
  let kbLoaded = false;
  let kbRefreshTimer = null;

  function openPanel() {
    panel.classList.add("open");
    panel.setAttribute("aria-hidden", "false");
    launcher.style.display = "none";
    setTimeout(() => input.focus(), 0);
  }

  function closePanel() {
    panel.classList.remove("open");
    panel.setAttribute("aria-hidden", "true");
    launcher.style.display = "grid";
  }

  launcher.addEventListener("click", openPanel);
  close.addEventListener("click", closePanel);
  if (startOpen) openPanel();

  function loadScript(src) {
    return new Promise((resolve, reject) => {
      const s = document.createElement("script");
      s.src = src;
      s.async = true;
      s.onload = resolve;
      s.onerror = reject;
      document.head.appendChild(s);
    });
  }

  function ensureMarkdownLibraries() {
    if (window.marked && window.DOMPurify) return Promise.resolve();
    if (!librariesLoading) {
      librariesLoading = Promise.all([
        window.marked ? Promise.resolve() : loadScript(`${apiBase}/static/vendor/marked.min.js`),
        window.DOMPurify ? Promise.resolve() : loadScript(`${apiBase}/static/vendor/purify.min.js`),
      ]).catch(() => null);
    }
    return librariesLoading;
  }

  function renderMarkdown(bubble, text) {
    if (window.marked && window.DOMPurify) {
      bubble.innerHTML = DOMPurify.sanitize(marked.parse(text));
    } else {
      bubble.textContent = text;
    }
  }

  function addMsg(role, text) {
    const div = document.createElement("div");
    div.className = `msg ${role}`;
    const bubble = document.createElement("div");
    bubble.className = "bubble";
    bubble.textContent = text;
    div.appendChild(bubble);
    chat.appendChild(div);
    chat.scrollTop = chat.scrollHeight;
    return bubble;
  }

  function refreshKbPanel() {
    const zh = lang.startsWith("zh");
    kbTitle.textContent = zh ? "知识库文档" : "Knowledge base";
    return fetch(`${apiBase}/api/kb`).then(r => {
      if (!r.ok) throw new Error("KB panel disabled");
      return r.json();
    }).then(kb => {
      kbTotal.textContent = zh
        ? `${kb.documents.length} 个文档 · ${kb.total_chunks} 个知识块`
        : `${kb.documents.length} documents · ${kb.total_chunks} chunks`;
      kbDocs.textContent = "";
      for (const d of kb.documents) {
        const item = document.createElement("div");
        item.className = "kb-doc";
        const name = document.createElement("b");
        name.textContent = d.name;
        const meta = document.createElement("small");
        meta.textContent = zh
          ? `${d.sections} 个章节 · ${d.chunks} 个知识块`
          : `${d.sections} sections · ${d.chunks} chunks`;
        item.append(name, meta);
        kbDocs.appendChild(item);
      }
    }).catch(() => {});
  }

  function enableKbPanel() {
    kbEnabled = true;
    const zh = lang.startsWith("zh");
    kbToggle.textContent = zh ? "文档" : "Docs";
    kbToggle.setAttribute("aria-label", zh ? "显示知识库文档" : "Show knowledge base");
    kbToggle.classList.add("enabled");
  }

  function setKbVisible(visible) {
    if (!kbEnabled) return;
    kbPanel.classList.toggle("show", visible);
    kbToggle.classList.toggle("active", visible);
    kbToggle.setAttribute("aria-expanded", visible ? "true" : "false");
    kbToggle.setAttribute(
      "aria-label",
      visible
        ? (lang.startsWith("zh") ? "隐藏知识库文档" : "Hide knowledge base")
        : (lang.startsWith("zh") ? "显示知识库文档" : "Show knowledge base")
    );
    if (visible && !kbLoaded) {
      kbLoaded = true;
      refreshKbPanel();
      kbRefreshTimer = setInterval(refreshKbPanel, 15000);
    }
    if (!visible && kbRefreshTimer) {
      clearInterval(kbRefreshTimer);
      kbRefreshTimer = null;
      kbLoaded = false;
    }
  }

  kbToggle.addEventListener("click", () => {
    setKbVisible(!kbPanel.classList.contains("show"));
  });

  fetch(`${apiBase}/api/config`).then(r => r.json()).then(cfg => {
    lang = cfg.lang || "en";
    title.textContent = cfg.name;
    tagline.textContent = cfg.tagline;
    input.placeholder = cfg.placeholder;
    showSources = cfg.show_sources !== false;
    if (!currentScript.dataset.noTitle) document.title = cfg.name;
    if (cfg.show_kb) enableKbPanel();
  }).catch(() => {});

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const message = input.value.trim();
    if (!message) return;

    input.value = "";
    send.disabled = true;
    addMsg("user", message);
    const bubble = addMsg("assistant", "…");
    let answer = "";

    await ensureMarkdownLibraries();

    try {
      const res = await fetch(`${apiBase}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message, history }),
      });
      if (!res.ok || !res.body) throw new Error(`HTTP ${res.status}`);

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buf = "";
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buf += decoder.decode(value, { stream: true });
        const events = buf.split("\n\n");
        buf = events.pop();
        for (const raw of events) {
          const evLine = raw.split("\n").find(l => l.startsWith("event: "));
          const dataLine = raw.split("\n").find(l => l.startsWith("data: "));
          if (!evLine || !dataLine) continue;
          const ev = evLine.slice(7);
          const data = JSON.parse(dataLine.slice(6));
          if (ev === "token") {
            answer += data.text;
            renderMarkdown(bubble, answer);
          } else if (ev === "sources" && showSources && data.sources.length) {
            const s = document.createElement("div");
            s.className = "sources";
            const strong = document.createElement("b");
            strong.textContent = lang.startsWith("zh") ? "来源:" : "Sources:";
            s.append(strong, " ", data.sources.join(" · "));
            bubble.parentElement.appendChild(s);
          } else if (ev === "error") {
            const s = document.createElement("div");
            s.className = "error";
            s.textContent = data.message;
            bubble.parentElement.appendChild(s);
            if (!answer) bubble.textContent = lang.startsWith("zh") ? "(未生成回答)" : "(no answer generated)";
          }
          chat.scrollTop = chat.scrollHeight;
        }
      }
    } catch (err) {
      const s = document.createElement("div");
      s.className = "error";
      s.textContent = lang.startsWith("zh")
        ? `请求失败: ${err.message}`
        : `Request failed: ${err.message}`;
      bubble.parentElement.appendChild(s);
      if (!answer) bubble.textContent = lang.startsWith("zh") ? "(未生成回答)" : "(no answer generated)";
    } finally {
      history.push({ role: "user", content: message });
      if (answer) history.push({ role: "assistant", content: answer });
      send.disabled = false;
      input.focus();
    }
  });
  }

  if (document.body) {
    boot();
  } else {
    window.addEventListener("DOMContentLoaded", boot, { once: true });
  }
})();
