/**
 * app_header_actions.js v=cl17p3
 * 統一 header 右上角：返回上一頁 + 登出
 */
(function () {
  if (document.getElementById('xn-header-actions-injected')) return;

  const style = document.createElement('style');
  style.id = 'xn-header-actions-injected';
  style.textContent = `
    body .xn-header-actions {
      position: absolute !important;
      right: 38px !important;
      bottom: 24px !important;
      z-index: 9999 !important;
      display: flex !important;
      flex-direction: row !important;
      flex-wrap: nowrap !important;
      align-items: center !important;
      gap: 7px !important;
      white-space: nowrap !important;
    }
    body .xn-header-actions button {
      flex: 0 0 auto !important;
      height: 28px !important;
      min-width: 68px !important;
      padding: 0 10px !important;
      border-radius: 9px !important;
      border: 1px solid rgba(224,201,119,0.82) !important;
      background: #10361f !important;
      color: #fff7d6 !important;
      font-size: 12px !important;
      font-weight: 1000 !important;
      line-height: 1 !important;
      display: inline-flex !important;
      align-items: center !important;
      justify-content: center !important;
      cursor: pointer !important;
      box-shadow: none !important;
    }
    body .xn-header-actions button:hover {
      background: #174a2a !important;
      border-color: #ead27b !important;
      transform: translateY(-1px);
    }
    body .xn-header-actions button.xn-logout {
      background: #7f251f !important;
      border-color: rgba(244,180,140,0.82) !important;
      color: #fff4ec !important;
    }
    body .xn-header-actions button.xn-logout:hover {
      background: #9b2d25 !important;
      border-color: #ffd0b0 !important;
    }
    @media (max-width: 1200px) {
      body .xn-header-actions {
        right: 20px !important;
        bottom: 16px !important;
        gap: 5px !important;
      }
      body .xn-header-actions button {
        height: 26px !important;
        min-width: 58px !important;
        padding: 0 7px !important;
        font-size: 11px !important;
      }
    }
  `;
  document.head.appendChild(style);

  function inject() {
    // 支援多種 header 類型
    const header = document.querySelector([
      '.web-title.web-title-tech',
      '.web-title',
      '.app-standard-hero',
      '.hero',
      'header',
      '.site-header',
      '.app-header',
    ].join(', '));

    if (!header) return;
    if (header.querySelector('.xn-header-actions')) return;

    // 確保 header 有相對定位
    const pos = window.getComputedStyle(header).position;
    if (pos === 'static') header.style.position = 'relative';

    const box = document.createElement('div');
    box.className = 'xn-header-actions';

    // 返回上一頁
    const backBtn = document.createElement('button');
    backBtn.type = 'button';
    backBtn.textContent = '返回上一頁';
    backBtn.onclick = function () { history.back(); };
    box.appendChild(backBtn);

    // 登出
    const logoutBtn = document.createElement('button');
    logoutBtn.type = 'button';
    logoutBtn.textContent = '登出';
    logoutBtn.className = 'xn-logout';
    logoutBtn.onclick = function () {
      sessionStorage.removeItem('xunnan_admin_token');
      localStorage.removeItem('xunnan_admin_token');
      localStorage.removeItem('xunnan_auth_token');
      window.location.href = '/employee/logout?next=/';
    };
    box.appendChild(logoutBtn);

    header.appendChild(box);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', inject);
  } else {
    inject();
  }
})();
