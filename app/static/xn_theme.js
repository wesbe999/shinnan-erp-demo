/* xn_theme.js - 訊南 ERP 全域主題 v7 - 底圖切換 */
(function(){
  var THEMES = {
    navy: {
      f:"#0a1828", m:"#122d5c", t:"#1a3a6b", g:"60,130,220",
      ac:"#60a5fa", acGlow:"rgba(60,130,246,.6)", acGlow2:"rgba(60,130,246,.2)",
      bdGlow:"rgba(60,130,220,.55)",
      cardFrom:"rgba(10,40,90,.50)", cardTo:"rgba(5,18,40,.65)",
      cardShine:"rgba(60,130,220,.10)", desc:"#d0e8ff",
      heroBg:"/erp-static/home_hero_navy.png",
      heroText:"#e8f4ff", heroSub:"#60a5fa", heroSubGlow:"rgba(96,165,250,.5)",
      heroSubLine:"#60a5fa", heroDesc:"#b8d8f8",
      portalBorder:"rgba(60,130,220,.8)", portalShadow:"rgba(60,130,220,.18)",
    },
    purple: {
      f:"#14082a", m:"#2e1260", t:"#3b1a6b", g:"160,80,255",
      ac:"#c084fc", acGlow:"rgba(168,85,247,.6)", acGlow2:"rgba(168,85,247,.2)",
      bdGlow:"rgba(160,80,255,.55)",
      cardFrom:"rgba(50,15,100,.50)", cardTo:"rgba(20,8,42,.65)",
      cardShine:"rgba(160,80,255,.10)", desc:"#ead0ff",
      heroBg:null,
    },
    crimson: {
      f:"#220808", m:"#5a1212", t:"#6b1a1a", g:"220,60,60",
      ac:"#f87171", acGlow:"rgba(239,68,68,.6)", acGlow2:"rgba(239,68,68,.2)",
      bdGlow:"rgba(220,60,60,.55)",
      cardFrom:"rgba(90,15,15,.50)", cardTo:"rgba(34,8,8,.65)",
      cardShine:"rgba(220,60,60,.10)", desc:"#ffd0d0",
      heroBg:null,
    },
    slate: {
      f:"#0a1020", m:"#162030", t:"#1e293b", g:"100,130,160",
      ac:"#94a3b8", acGlow:"rgba(100,116,139,.6)", acGlow2:"rgba(100,116,139,.2)",
      bdGlow:"rgba(100,130,160,.55)",
      cardFrom:"rgba(20,35,55,.50)", cardTo:"rgba(10,16,32,.65)",
      cardShine:"rgba(100,130,160,.10)", desc:"#d0daea",
      heroBg:null,
    },
    amber: {
      f:"#140c02", m:"#3a2008", t:"#4a2c0a", g:"220,160,30",
      ac:"#fbbf24", acGlow:"rgba(245,158,11,.6)", acGlow2:"rgba(245,158,11,.2)",
      bdGlow:"rgba(220,160,30,.55)",
      cardFrom:"rgba(80,45,5,.50)", cardTo:"rgba(20,12,2,.65)",
      cardShine:"rgba(220,160,30,.10)", desc:"#ffedb0",
      heroBg:null,
    },
  };

  var id = localStorage.getItem("xn_theme") || "default";
  if (id === "default") return;
  var t = THEMES[id];
  if (!t) return;

  var hg = [
    "radial-gradient(circle at 68% 58%,rgba("+t.g+",.32) 0,rgba("+t.g+",.09) 10%,transparent 25%)",
    "radial-gradient(circle at 78% 20%,rgba("+t.g+",.18) 0,rgba("+t.g+",0) 36%)",
    "linear-gradient(105deg,"+t.f+" 0%,"+t.m+" 38%,"+t.t+" 64%,"+t.f+" 100%)"
  ].join(",");
  var sg = "linear-gradient(135deg,"+t.f+","+t.t+")";
  var ag = [
    "radial-gradient(circle at 50% 45%,rgba("+t.g+",.22) 0%,rgba("+t.g+",.09) 28%,transparent 60%)",
    "linear-gradient(90deg,"+t.f+" 0%,"+t.m+" 38%,"+t.t+" 52%,"+t.m+" 68%,"+t.f+" 100%)"
  ].join(",");

  function injectStyle() {
    var existing = document.getElementById("xn-theme-v7");
    if (existing) existing.remove();
    var style = document.createElement("style");
    style.id = "xn-theme-v7";

    var css = [
      ":root:root{",
      "  --xn-ac:"+t.ac+";",
      "  --xn-ac-glow:"+t.acGlow+";",
      "  --xn-ac-glow2:"+t.acGlow2+";",
      "  --xn-bd-glow:"+t.bdGlow+";",
      "  --xn-card-from:"+t.cardFrom+";",
      "  --xn-card-to:"+t.cardTo+";",
      "  --xn-card-shine:"+t.cardShine+";",
      "  --xn-desc:"+t.desc+";",
      (t.heroBg ? "  --xn-portal-border:"+( t.portalBorder||"rgba("+t.g+",.6)" )+";" : ""),
      (t.heroBg ? "  --xn-portal-bg:url('"+t.heroBg+"') center/cover no-repeat;" : ""),
      (t.heroBg ? "  --xn-portal-shadow: 0 22px 64px rgba(0,0,0,.4),0 0 28px "+(t.portalShadow||"rgba("+t.g+",.2)")+";": ""),
      (t.heroBg ? "  --xn-grid-opacity: 0;" : ""),
      (t.heroBg ? "  --xn-overlay-opacity: 0;" : ""),
      (t.heroBg ? "  --xn-body-bg: "+t.f+";" : ""),
      "}",
      ":root:root .web-title{background:"+hg+"!important;border-color:rgba("+t.g+",.45)!important}",
      ":root:root .sv2-hero{background:"+sg+"!important}",
      ":root:root .sv2-det-header{background:"+sg+"!important}",
    ];

    // 有底圖的主題：整個 portal 用底圖滿版
    if (t.heroBg) {
      css.push(
        // portal 整體換底圖，hero 和 panel 背景全透明
        ":root:root .portal{" +
        "background:url('"+t.heroBg+"') center/cover no-repeat!important;" +
        "border:1px solid "+(t.portalBorder||"rgba("+t.g+",.6)")+"!important;" +
        "box-shadow:0 22px 64px rgba(0,0,0,.4),0 0 28px "+(t.portalShadow||"rgba("+t.g+",.2)")+"!important;" +
        "}",
        // hero 透明，讓底圖透出來
        ":root:root .hero{background:transparent!important;border:none!important}",
        // panel 格子加半透明深色遮罩讓字看清楚
        ":root:root .module{background:rgba(5,15,35,.55)!important;border-color:rgba("+t.g+",.35)!important;backdrop-filter:blur(2px)!important}",
        ":root:root .module:hover{background:rgba(10,25,55,.70)!important;border-color:"+(t.ac)+"!important}",
        // 文字顏色
        ":root:root .headline{color:"+(t.heroText||"#fff")+"!important;text-shadow:0 2px 28px rgba(0,0,0,.7)!important}",
        ":root:root .headline-sub{color:"+(t.heroSub||t.ac)+"!important;text-shadow:0 0 20px "+(t.heroSubGlow||"rgba("+t.g+",.6)")+"!important}",
        ":root:root .headline-sub:before,:root:root .headline-sub:after{background:linear-gradient(90deg,transparent,"+(t.heroSubLine||t.ac)+",transparent)!important;box-shadow:none!important}",
        ":root:root .panel-title{color:"+(t.ac)+"!important}",
        // 隱藏舊 world-img 和星星（底圖已內建）
        ":root:root .world-img{display:none!important}",
        ":root:root .star-overlay{display:none!important}",
        // 全域格線和遮罩移除，body/shell 換純深藍滿版
        "body:before{display:none!important}",
        "body:after{display:none!important}",
        "html,body{background:"+t.f+"!important;font-family:'LXGW WenKai TC','FangSong','STFangsong','Microsoft JhengHei',serif!important}",
        ".shell{padding:0!important;overflow:hidden!important}",
        // portal：上下左右留出金框空間，右側格子縮窄
        ":root:root .portal{border-radius:0!important;border:none!important;grid-template-columns:42% 58%!important;gap:0!important;padding:56px 52px 52px 40px!important;overflow:visible!important}",
        // 左側 hero：所有文字靠右對齊，整體往右上
        ":root:root .hero{padding:0 16px 0 0!important;justify-content:flex-start!important;padding-top:10%!important;align-items:flex-end!important;overflow:visible!important;text-align:right!important}",
        ":root:root .brand{margin-bottom:14px!important;display:flex!important;flex-direction:column!important;align-items:flex-end!important}",
        // logo-wrap 隱藏（含星芒），logo 改用 brand-zh::before 偽元素顯示在文字左側
        ":root:root .logo-wrap{display:none!important}",
        ":root:root .brand > div:last-child{display:flex!important;flex-direction:column!important;align-items:flex-end!important}",
        ":root:root .brand-zh{font-size:24px!important;letter-spacing:3px!important;display:flex!important;align-items:center!important;gap:8px!important}",
        ":root:root .brand-zh::before{content:''!important;display:inline-block!important;width:36px!important;height:36px!important;background:url('/erp-static/shinnan_home_logo.png') center/contain no-repeat!important;flex-shrink:0!important}",
        ":root:root .brand-en{font-size:10px!important;letter-spacing:6px!important;margin-top:2px!important}",
        ":root:root .logo-img{display:none!important}",
        ":root:root .headline{font-size:40px!important;letter-spacing:2px!important;line-height:1.05!important;white-space:nowrap!important;text-align:right!important}",
        ":root:root .headline-sub{font-size:22px!important;margin-top:10px!important;letter-spacing:6px!important;text-align:right!important}",
        ":root:root .headline-sub:before{display:none!important}",
        ":root:root .desc{display:none!important}",
        ":root:root .status{display:none!important}",
        // 右側 panel：panel-title 放大，格子縮窄
        ":root:root .panel{padding:0 0 0 10px!important;overflow:hidden!important}",
        ":root:root .panel-title{font-size:18px!important;margin-bottom:8px!important;letter-spacing:4px!important}",
        ":root:root .grid{gap:6px!important;grid-template-rows:repeat(4,minmax(0,1fr))!important;overflow:hidden!important}",
        ":root:root .module{padding:6px 22px 6px 12px!important;border-radius:8px!important;min-height:0!important;height:100%!important;overflow:hidden!important}",
        ":root:root .mi{width:18px!important;height:16px!important;margin-bottom:2px!important}",
        ":root:root .mi svg{width:16px!important;height:16px!important}",
        ":root:root .module-name{font-size:13px!important;margin-bottom:2px!important;letter-spacing:1px!important;white-space:nowrap!important}",
        ":root:root .module-desc{font-size:10px!important;line-height:1.3!important;overflow:hidden!important}",
        ":root:root .arrow{font-size:16px!important;right:8px!important;top:50%!important;transform:translateY(-50%)!important}"
      );
    } else {
      css.push(
        ":root:root .hero,:root:root .hero.app-standard-hero{background:"+ag+"!important;border-color:rgba("+t.g+",.32)!important}"
      );
    }

    style.textContent = css.join("\n");
    document.head.appendChild(style);

    // portal 背景（底圖主題不覆寫，交給 CSS 處理）
    var portal = document.querySelector(".portal");
    if (portal && !t.heroBg) {
      portal.style.cssText += ";background:" + [
        "radial-gradient(circle at 18% 20%,rgba(255,255,255,.04),transparent 22%)",
        "radial-gradient(circle at 24% 82%,rgba("+t.g+",.07),transparent 34%)",
        "linear-gradient(90deg,"+t.f+"cc,"+t.t+"99 46%,"+t.f+"cc)",
        "linear-gradient(180deg,rgba(255,255,255,.03),transparent 34%,rgba(0,0,0,.18))"
      ].join(",") + "!important";
      if (t.portalBorder) portal.style.border = "1px solid "+t.portalBorder;
      if (t.portalShadow) portal.style.boxShadow = "0 22px 64px rgba(0,0,0,.34),0 0 24px "+t.portalShadow;
      document.body.style.background = "linear-gradient(135deg,"+t.f+" 0%,"+t.t+" 46%,"+t.f+"88 100%)";
    } else if (portal && t.heroBg) {
      // 清掉綠色格線框，html/body 強制深藍
      portal.style.removeProperty("border");
      portal.style.removeProperty("box-shadow");
      document.documentElement.style.setProperty('background', t.f, 'important');
      document.body.style.setProperty('background', t.f, 'important');
      document.documentElement.style.setProperty('--xn-grid-opacity', '0');
      document.documentElement.style.setProperty('--xn-overlay-opacity', '0');
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", injectStyle);
  } else {
    injectStyle();
  }
})();
