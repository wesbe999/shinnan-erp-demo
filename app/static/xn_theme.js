/* xn_theme.js - 訊南 ERP 主題系統 v8
   每個主題只需定義 CSS 變數，不再用 !important 覆蓋
   新增主題：在 THEMES 加一個 key，填入所有變數值即可 */
(function(){

var THEMES = {

  navy: {
    /* 字體與基底 */
    font: '"LXGW WenKai TC","FangSong","Microsoft JhengHei",serif',
    bodyBg: '#0a1828',
    text: '#e8f4ff',
    /* 格線（關閉） */
    gridDisplay: 'none',
    overlayDisplay: 'none',
    /* shell */
    shellPadding: '0',
    shellOverflow: 'hidden',
    /* portal */
    portalCols: '42% 58%',
    portalGap: '0',
    portalPadding: '56px 52px 52px 40px',
    portalBorder: 'rgba(60,130,220,.0)',
    portalRadius: '0',
    portalOverflow: 'visible',
    portalBg: 'url("/erp-static/home_hero_navy.png") center/cover no-repeat',
    portalShadow: '0 22px 64px rgba(0,0,0,.4)',
    /* hero */
    heroPadding: '0 16px 0 0',
    heroJustify: 'flex-start',
    heroAlign: 'flex-end',
    heroTextAlign: 'right',
    heroOverflow: 'visible',
    heroPaddingTop: '10%',
    /* brand */
    brandZhColor: '#e8f4ff',
    brandZhSize: '24px',
    brandEnColor: '#60a5fa',
    logoWrapDisplay: 'none',
    logoImgDisplay: 'none',
    logoImgWidth: '0',
    starburstDisplay: 'none',
    /* headline */
    headlineColor: '#e8f4ff',
    headlineSize: '40px',
    headlineSubColor: '#60a5fa',
    headlineSubSize: '22px',
    headlineSubLine: 'rgba(60,130,246,.4)',
    /* desc & status */
    descDisplay: 'none',
    /* world-img（關閉，底圖已含） */
    worldDisplay: 'none',
    starDisplay: 'none',
    /* panel */
    panelTitleSize: '18px',
    /* accent */
    ac: '#60a5fa',
    acGlow: 'rgba(60,130,246,.55)',
    acGlow2: 'rgba(60,130,246,.18)',
    bdGlow: 'rgba(60,130,220,.45)',
    cardFrom: 'rgba(5,15,35,.55)',
    cardTo: 'rgba(10,25,55,.65)',
    cardShine: 'rgba(60,130,220,.08)',
    desc: '#d0e8ff',
    footerColor: 'rgba(96,165,250,.82)',
    footerShadow: 'rgba(60,130,246,.35)',
    /* logo 用 CSS 顯示在文字左側 */
    logoBeforeContent: 'url("/erp-static/shinnan_home_logo.png")',
    logoBeforeSize: '72px',
  },

};

/* ── 主題套用邏輯 ── */
var id = localStorage.getItem('xn_theme') || 'default';
if (id === 'default') return;
var t = THEMES[id];
if (!t) return;

function applyTheme() {
  /* 移除舊 style */
  var old = document.getElementById('xn-theme-v8');
  if (old) old.remove();

  var vars = [
    '--xn-font:' + t.font,
    '--xn-body-bg:' + t.bodyBg,
    '--xn-text:' + (t.text||'#f4fff4'),
    '--xn-grid-display:' + (t.gridDisplay||'block'),
    '--xn-overlay-display:' + (t.overlayDisplay||'block'),
    '--xn-shell-padding:' + (t.shellPadding||'16px 24px'),
    '--xn-shell-overflow:' + (t.shellOverflow||'hidden'),
    '--xn-portal-cols:' + (t.portalCols||'48% 52%'),
    '--xn-portal-gap:' + (t.portalGap||'28px'),
    '--xn-portal-padding:' + (t.portalPadding||'24px 34px'),
    '--xn-portal-border:' + (t.portalBorder||'rgba(143,255,73,.78)'),
    '--xn-portal-radius:' + (t.portalRadius||'24px'),
    '--xn-portal-overflow:' + (t.portalOverflow||'hidden'),
    '--xn-portal-bg:' + (t.portalBg||'none'),
    '--xn-portal-shadow:' + (t.portalShadow||'0 22px 64px rgba(0,0,0,.34)'),
    '--xn-hero-padding:' + (t.heroPadding||'0 34px 16px 24px'),
    '--xn-hero-justify:' + (t.heroJustify||'flex-start'),
    '--xn-hero-align:' + (t.heroAlign||'flex-start'),
    '--xn-hero-text-align:' + (t.heroTextAlign||'left'),
    '--xn-hero-overflow:' + (t.heroOverflow||'visible'),
    '--xn-brand-zh-color:' + (t.brandZhColor||'#fff'),
    '--xn-brand-zh-size:' + (t.brandZhSize||'32px'),
    '--xn-brand-en-color:' + (t.brandEnColor||'#d4af37'),
    '--xn-logo-wrap-display:' + (t.logoWrapDisplay||'inline-block'),
    '--xn-logo-img-display:' + (t.logoImgDisplay||'block'),
    '--xn-logo-img-width:' + (t.logoImgWidth||'132px'),
    '--xn-starburst-display:' + (t.starburstDisplay||'block'),
    '--xn-headline-color:' + (t.headlineColor||'#fff'),
    '--xn-headline-size:' + (t.headlineSize||'46px'),
    '--xn-headline-sub-color:' + (t.headlineSubColor||'#d4af37'),
    '--xn-headline-sub-size:' + (t.headlineSubSize||'34px'),
    '--xn-headline-sub-line:' + (t.headlineSubLine||'rgba(164,255,67,.34)'),
    '--xn-desc-display:' + (t.descDisplay||'block'),
    '--xn-desc-color:' + (t.descColor||'#e9f8e9'),
    '--xn-world-display:' + (t.worldDisplay||'block'),
    '--xn-world-left:' + (t.worldLeft||'-94px'),
    '--xn-world-bottom:' + (t.worldBottom||'-27px'),
    '--xn-world-width:' + (t.worldWidth||'255%'),
    '--xn-world-height:' + (t.worldHeight||'648px'),
    '--xn-world-opacity:' + (t.worldOpacity||'.82'),
    '--xn-star-display:' + (t.starDisplay||'block'),
    '--xn-panel-title-size:' + (t.panelTitleSize||'23px'),
    '--xn-ac:' + (t.ac||'#d4af37'),
    '--xn-ac-glow:' + (t.acGlow||'rgba(145,255,62,.75)'),
    '--xn-ac-glow2:' + (t.acGlow2||'rgba(164,255,67,.16)'),
    '--xn-bd-glow:' + (t.bdGlow||'rgba(152,255,77,.55)'),
    '--xn-card-from:' + (t.cardFrom||'rgba(24,96,42,.40)'),
    '--xn-card-to:' + (t.cardTo||'rgba(8,34,20,.58)'),
    '--xn-card-shine:' + (t.cardShine||'rgba(164,255,67,.09)'),
    '--xn-desc:' + (t.desc||'#e3f7e0'),
    '--xn-footer-color:' + (t.footerColor||'rgba(255,210,92,.82)'),
    '--xn-footer-shadow:' + (t.footerShadow||'rgba(255,210,92,.38)'),
  ];

  var extraCss = '';

  /* hero padding-top 特殊處理 */
  if (t.heroPaddingTop) {
    extraCss += '.hero{padding-top:' + t.heroPaddingTop + ';}';
  }

  /* navy logo 用 brand-zh::before 顯示 */
  if (t.logoBeforeContent) {
    extraCss += [
      '.brand > div{transform:none;}',
      '.brand-zh{display:flex;align-items:center;gap:8px;}',
      '.brand-zh::before{content:"";display:inline-block;',
      '  width:' + t.logoBeforeSize + ';height:' + t.logoBeforeSize + ';',
      '  background:' + t.logoBeforeContent + ' center/contain no-repeat;',
      '  flex-shrink:0;}',
      '.brand-en{text-align:right;}',
    ].join('');
  }

  /* html/body 背景 */
  extraCss += 'html,body{background:' + t.bodyBg + ';}';

  var style = document.createElement('style');
  style.id = 'xn-theme-v8';
  style.textContent = ':root{' + vars.join(';') + '}' + extraCss;
  document.head.appendChild(style);

  /* body 背景 inline（確保覆蓋） */
  document.documentElement.style.setProperty('background', t.bodyBg, 'important');
  document.body.style.setProperty('background', t.bodyBg, 'important');
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', applyTheme);
} else {
  applyTheme();
}

})();
