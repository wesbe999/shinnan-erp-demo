/* xn_theme.js - 訊南 ERP 全域主題套用 v1 */
(function(){
  const THEMES = {
    default: {hf:"#0f3320", ht:"#1a5c38", ac:"#d4af37", bg1:"#0a2015", bg2:"#1b5a2e"},
    navy:    {hf:"#0d1f3c", ht:"#1a3a6b", ac:"#60a5fa", bg1:"#0d1f3c", bg2:"#1a3a6b"},
    purple:  {hf:"#1a0a2e", ht:"#3b1a6b", ac:"#c084fc", bg1:"#1a0a2e", bg2:"#3b1a6b"},
    crimson: {hf:"#2a0a0a", ht:"#6b1a1a", ac:"#f87171", bg1:"#2a0a0a", bg2:"#6b1a1a"},
    slate:   {hf:"#0f172a", ht:"#1e293b", ac:"#94a3b8", bg1:"#0f172a", bg2:"#1e293b"},
    amber:   {hf:"#1c1004", ht:"#4a2c0a", ac:"#fbbf24", bg1:"#1c1004", bg2:"#4a2c0a"},
  };

  const id = localStorage.getItem("xn_theme") || "default";
  const t = THEMES[id] || THEMES.default;
  if (id === "default") return; // 預設不需要修改

  const root = document.documentElement;

  // 1. CSS 變數注入（對使用 CSS 變數的元件有效）
  root.style.setProperty("--xn-hero-from", t.hf);
  root.style.setProperty("--xn-hero-to",   t.ht);
  root.style.setProperty("--xn-accent",    t.ac);

  // 2. 套用 hero/header 漸層背景（找常見 class）
  function applyHero() {
    const grad = `linear-gradient(135deg, ${t.hf}, ${t.ht})`;

    // web-title（後台 header）
    document.querySelectorAll(".web-title").forEach(el => {
      el.style.background = [
        `radial-gradient(circle at 68% 58%, rgba(255,222,92,.28) 0, rgba(255,222,92,.06) 10%, rgba(255,222,92,0) 25%)`,
        `radial-gradient(circle at 78% 20%, rgba(73,196,95,.18) 0, rgba(73,196,95,0) 36%)`,
        `linear-gradient(105deg, ${t.hf} 0%, ${blend(t.hf, t.ht, .4)} 38%, ${blend(t.hf, t.ht, .7)} 64%, ${t.hf} 100%)`
      ].join(",");
    });

    // sv2-hero（業務手機 APP header）
    document.querySelectorAll(".sv2-hero, .sv2-det-header").forEach(el => {
      el.style.background = grad;
    });

    // portal（ERP 首頁）
    const portal = document.querySelector(".portal");
    if (portal) {
      portal.style.background = [
        `radial-gradient(circle at 18% 20%,rgba(255,255,255,.045),transparent 22%)`,
        `linear-gradient(90deg,${t.hf}cc,${t.ht}99 46%,${t.hf}cc)`,
        `linear-gradient(180deg,rgba(255,255,255,.035),transparent 34%,rgba(0,0,0,.18))`
      ].join(",");
      document.body.style.background = `linear-gradient(135deg,${t.bg1} 0%,${t.ht} 46%,${t.bg1}88 100%)`;
    }

    // sa2-nav-btn active（後台頁籤 active 色）
    const styleTag = document.getElementById("xn-theme-style") || document.createElement("style");
    styleTag.id = "xn-theme-style";
    styleTag.textContent = `
      .sa2-nav-btn.active { background: ${t.hf} !important; border-color: ${t.ac} !important; color: ${t.ac} !important; }
      .sa2-nav-btn:hover  { background: ${t.hf}88 !important; }
      .sv2-tab.active     { color: ${t.ac} !important; border-bottom-color: ${t.ac} !important; }
      .sv2-bot-btn.primary{ background: ${t.hf} !important; border-color: ${t.ac} !important; }
      .sv2-chip.active    { background: ${t.hf} !important; border-color: ${t.ac} !important; }
    `;
    if (!document.getElementById("xn-theme-style")) document.head.appendChild(styleTag);
  }

  // 顏色混合工具（hex）
  function blend(c1, c2, r) {
    const h = s => [1,3,5].map(i=>parseInt(s.slice(i,i+2),16));
    const [r1,g1,b1] = h(c1), [r2,g2,b2] = h(c2);
    const mix = (a,b) => Math.round(a+(b-a)*r).toString(16).padStart(2,"0");
    return "#" + mix(r1,r2) + mix(g1,g2) + mix(b1,b2);
  }

  // DOM 可能尚未 ready，確保執行
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", applyHero);
  } else {
    applyHero();
  }
})();
