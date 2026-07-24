(function () {
  "use strict";

  const copy = {
    "zh": {
      navCapabilities: "核心能力", navWorkflow: "工作方式", navAsk: "咨询助手",
      eyebrow: "AI 知识库助手", heroLead: "藏在文档里的答案，", heroAccent: "几秒就能找到。",
      heroCta: "立即提问", heroLearn: "了解核心能力", trustGrounded: "严格依据知识库", trustSources: "回答附带可查来源",
      demoOnline: "在线 · 知识库已同步", demoQuestion: "如何邀请新的团队成员？",
      demoAnswer: "进入 <strong>设置 → 团队</strong>，点击 <strong>邀请成员</strong>。填写对方邮箱并选择角色，邀请链接将在 7 天内有效。",
      demoSource: "内容来源", demoDocument: "快速开始 · 团队管理", demoMatch: "知识库原文", demoPlaceholder: "询问任何产品问题…",
      noteResponse: "流式响应", noteIndexed: "知识内容已索引", proofIntro: "为需要可靠答案，而不是更多搜索的团队而生",
      capKicker: "清晰可靠", capTitle: "每个问题，都有答案。", capSummary: "把分散的文档变成真正值得团队信赖的智能助手。",
      featureSearchTitle: "直接给答案，而非一页结果", featureSearchText: "使用自然语言提问，从最相关的内容中快速生成清晰、简洁的回答。", searchVisual: "计费规则是什么？",
      featureSourceTitle: "每个结论都有据可查", featureSourceText: "引用信息可定位到具体文档与章节，答案来源清晰透明。",
      featureFormatsTitle: "真实文档，统一检索", featureFormatsText: "在同一个专注的问答体验中检索 Markdown、PDF、Word、Excel 与 HTML。",
      flowKicker: "工作方式", flowTitle: "从文档到答案，只有关键信息。", flowSummary: "所有回答都以你的内容为中心。助手负责检索、排序，只呈现真正相关的信息。", flowCta: "体验智能助手",
      stepOneTitle: "连接你的知识", stepOneText: "添加产品文档、制度、指南和客服资料，兼容常用文件格式。",
      stepTwoTitle: "使用自然语言提问", stepTwoText: "无需关键词和高级筛选，就像向同事提问一样表达你的问题。",
      stepThreeTitle: "获得有依据的回答", stepThreeText: "实时获得清晰答案，并查看它所依据的原始内容来源。",
      ctaKicker: "让知识随时准备回答", ctaTitle: "告别搜索，直接提问。", ctaSummary: "现在就找到已经存在于文档里的答案。", ctaButton: "提出第一个问题",
      footerText: "可靠答案，源于你的知识。"
    }
  };

  function useCopy(lang) {
    const selected = lang.toLowerCase().startsWith("zh") ? copy.zh : null;
    if (!selected) return;
    document.querySelectorAll("[data-copy]").forEach((node) => {
      const value = selected[node.dataset.copy];
      if (value) node.innerHTML = value;
    });
  }

  function openChat() {
    const host = document.getElementById("rag-support-widget");
    const launcher = host && host.shadowRoot && host.shadowRoot.querySelector(".launcher");
    if (launcher) launcher.click();
  }

  document.querySelectorAll(".js-open-chat").forEach((button) => button.addEventListener("click", openChat));
  document.getElementById("year").textContent = new Date().getFullYear();

  Promise.all([
    fetch("/api/config").then((response) => response.ok ? response.json() : Promise.reject()),
    fetch("/api/health").then((response) => response.ok ? response.json() : null).catch(() => null)
  ]).then(([config, health]) => {
    const name = config.name || "Knowledge Base";
    const lang = config.lang || "en";
    document.title = name;
    document.documentElement.lang = lang;
    document.getElementById("brand-name").textContent = name;
    document.getElementById("footer-name").textContent = name;
    document.getElementById("demo-name").textContent = lang.toLowerCase().startsWith("zh") ? `${name} 助手` : `${name} Assistant`;
    document.getElementById("page-tagline").textContent = config.tagline;
    useCopy(lang);
    if (health && Number.isFinite(health.chunks_indexed)) {
      document.getElementById("indexed-count").textContent = health.chunks_indexed.toLocaleString(lang);
    }
  }).catch(() => {});
})();
