/* xn_theme.js - 訊南 ERP 全域主題 v5 - inject style tag with highest specificity */
(function(){
  var THEMES = {
    navy:    {f:"#0a1828",m:"#122d5c",t:"#1a3a6b",g:"60,130,220"},
    purple:  {f:"#14082a",m:"#2e1260",t:"#3b1a6b",g:"160,80,255"},
    crimson: {f:"#220808",m:"#5a1212",t:"#6b1a1a",g:"220,60,60"},
    slate:   {f:"#0a1020",m:"#162030",t:"#1e293b",g:"100,130,160"},
    amber:   {f:"#140c02",m:"#3a2008",t:"#4a2c0a",g:"220,160,30"},
  };

  var id = localStorage.getItem("xn_theme") || "default";
  if (id === "default") return;
  var t = THEMES[id];
  if (!t) return;

  // hero gradient
  var hg = [
    "radial-gradient(circle at 68% 58%,rgba("+t.g+",.32) 0,rgba("+t.g+",.09) 10%,transparent 25%)",
    "radial-gradient(circle at 78% 20%,rgba("+t.g+",.18) 0,rgba("+t.g+",0) 36%)",
    "linear-gradient(105deg,"+t.f+" 0%,"+t.m+" 38%,"+t.t+" 64%,"+t.f+" 100%)"
  ].join(",");
  var sg = "linear-gradient(135deg,"+t.f+","+t.t+")";
  // app-standard-hero gradient (horizontal like original)
  var ag = [
    "radial-gradient(circle at 50% 45%,rgba("+t.g+",.22) 0%,rgba("+t.g+",.09) 28%,transparent 60%)",
    "linear-gradient(90deg,"+t.f+" 0%,"+t.m+" 38%,"+t.t+" 52%,"+t.m+" 68%,"+t.f+" 100%)"
  ].join(",");

  function injectStyle() {
    var existing = document.getElementById("xn-theme-v5");
    if (existing) existing.remove();
    var style = document.createElement("style");
    style.id = "xn-theme-v5";
    // 用 :root:root 提高特異性以打敗 !important
    style.textContent = [
      ":root:root .web-title{background:"+hg+"!important;border-color:rgba("+t.g+",.45)!important}",
      ":root:root .hero,:root:root .hero.app-standard-hero{background:"+ag+"!important;border-color:rgba("+t.g+",.32)!important}",
      ":root:root .sv2-hero{background:"+sg+"!important}",
      ":root:root .sv2-det-header{background:"+sg+"!important}",
    ].join("\n");
    document.head.appendChild(style);

    // ERP 電腦首頁 portal (inline style needed)
    var portal = document.querySelector(".portal");
    if (portal) {
      portal.style.cssText += ";background:" + [
        "radial-gradient(circle at 18% 20%,rgba(255,255,255,.04),transparent 22%)",
        "radial-gradient(circle at 24% 82%,rgba("+t.g+",.07),transparent 34%)",
        "linear-gradient(90deg,"+t.f+"cc,"+t.t+"99 46%,"+t.f+"cc)",
        "linear-gradient(180deg,rgba(255,255,255,.03),transparent 34%,rgba(0,0,0,.18))"
      ].join(",") + "!important";
      document.body.style.background = "linear-gradient(135deg,"+t.f+" 0%,"+t.t+" 46%,"+t.f+"88 100%)";
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", injectStyle);
  } else {
    injectStyle();
  }
})();
