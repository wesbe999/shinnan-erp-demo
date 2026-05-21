/**
 * app_header_actions.js v=cl17p6
 * 統一 header：返回首頁 + 登出
 * - 有自己 toolbar（web-title-actions）的頁面：只補登出按鈕
 * - 沒有 toolbar 的頁面：建立 xn-header-actions
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
      align-items: center !important;
      gap: 7px !important;
      white-space: nowrap !important;
      background: none !important;
      border: none !important;
      padding: 0 !important;
      box-shadow: none !important;
    }
    body .xn-header-actions button,
    body .web-title-actions button.xn-logout {
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
      flex: 0 0 auto !important;
    }
    body .xn-header-actions button:hover,
    body .web-title-actions button.xn-logout:hover {
      background: #174a2a !important;
      border-color: #ead27b !important;
    }
    body .xn-header-actions button.xn-logout,
    body .web-title-actions button.xn-logout {
      background: #cf3b2f !important;
      border-color: rgba(244,180,140,0.82) !important;
      color: #fff !important;
    }
    body .xn-header-actions button.xn-logout:hover,
    body .web-title-actions button.xn-logout:hover {
      background: #b02a20 !important;
      border-color: #ffd0b0 !important;
    }
    @media (max-width: 1200px) {
      body .xn-header-actions { right: 20px !important; bottom: 16px !important; gap: 5px !important; }
      body .xn-header-actions button,
      body .web-title-actions button.xn-logout {
        height: 26px !important; min-width: 58px !important;
        padding: 0 7px !important; font-size: 11px !important;
      }
    }
  `;
  document.head.appendChild(style);

  function makeLogoutBtn() {
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.textContent = '登出';
    btn.className = 'xn-logout';
    btn.onclick = function () {
      sessionStorage.removeItem('xunnan_admin_token');
      localStorage.removeItem('xunnan_admin_token');
      localStorage.removeItem('xunnan_auth_token');
      localStorage.removeItem('xunnan_admin_role');
      localStorage.removeItem('xunnan_login_role');
      var path = window.location.pathname;
      var isApp = path.startsWith('/app');
      var next = isApp ? '/employee/login' : '/';
      window.location.href = '/employee/logout?next=' + encodeURIComponent(next);
    };
    return btn;
  }

  function makeSaveAllBtn() {
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.id = 'xn-save-all-btn';
    btn.textContent = '💾 儲存';
    btn.style.cssText = 'background:#1a6b3a !important; border-color:rgba(100,220,130,0.8) !important;';
    btn.onclick = async function () {
      btn.textContent = '儲存中…';
      btn.disabled = true;
      try {
        const res = await fetch('/api/admin/buildings?ts=' + Date.now());
        const buildings = await res.json();
        const STORAGE_KEY = 'xunnan_buildings_overrides';
        const overrides = JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}');
        let count = 0;
        for (const b of buildings) {
          const ov = overrides[b.building_no];
          if (!ov || !b.id) continue;
          await fetch('/api/admin/buildings/' + b.id, {
            method: 'PATCH',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(ov)
          });
          count++;
        }
        localStorage.removeItem('xunnan_buildings_overrides');
        btn.textContent = count > 0 ? ('✓ 已儲存' + count + '筆') : '✓ 已是最新';
        btn.style.background = '#0d4a27 !important';
        setTimeout(function () {
          btn.textContent = '💾 儲存';
          btn.disabled = false;
          btn.style.background = '#1a6b3a !important';
        }, 2500);
      } catch (e) {
        btn.textContent = '❌ 失敗';
        btn.disabled = false;
        setTimeout(function () { btn.textContent = '💾 儲存'; }, 2500);
      }
    };
    return btn;
  }

  function inject() {
    const header = document.querySelector(
      '.web-title.web-title-tech, .web-title, .app-standard-hero, .hero, header, .site-header, .app-header'
    );
    if (!header) return;

    // 情況1：頁面已有任何 toolbar/actions（自己的按鈕群）
    // 只補登出按鈕，不另建框框
    const existingActions = header.querySelector(
      '.web-title-actions, .cl15i10-header-actions, [class*="header-actions"]'
    );
    if (existingActions) {
      if (header.querySelector('.xn-header-actions')) {
        // 大樓頁面補儲存按鈕（若尚未加入）
        const box = header.querySelector('.xn-header-actions');
        if (window.location.pathname.startsWith('/admin/buildings') && !box.querySelector('#xn-save-all-btn')) {
          box.insertBefore(makeSaveAllBtn(), box.firstChild);
        }
        return;
      }
      const hasLogout = [...existingActions.querySelectorAll('button')]
        .some(b => b.textContent.trim() === '登出');
      if (!hasLogout) existingActions.appendChild(makeLogoutBtn());
      return;
    }

    // 情況2：cl15i10 已處理（雙重保險）
    if (header.querySelector('.cl15i10-header-actions')) return;

    // 情況3：沒有 toolbar，建立 xn-header-actions
    if (header.querySelector('.xn-header-actions')) return;
    const pos = window.getComputedStyle(header).position;
    if (pos === 'static') header.style.position = 'relative';

    const box = document.createElement('div');
    box.className = 'xn-header-actions';

    // 大樓名錄頁面：加儲存按鈕
    if (window.location.pathname.startsWith('/admin/buildings')) {
      box.appendChild(makeSaveAllBtn());
    }

    const backBtn = document.createElement('button');
    backBtn.type = 'button';
    backBtn.textContent = '返回首頁';
    backBtn.onclick = function () {
      var isApp = window.location.pathname.startsWith('/app');
      window.location.href = isApp ? '/app' : '/';
    };
    box.appendChild(backBtn);
    box.appendChild(makeLogoutBtn());

    header.appendChild(box);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', inject);
  } else {
    inject();
  }

  // MutationObserver：動態注入的 toolbar（如帳務系統）也能偵測到
  const observer = new MutationObserver(function() {
    const header = document.querySelector(
      '.web-title.web-title-tech, .web-title, .app-standard-hero, .hero'
    );
    if (!header) return;
    const existingActions = header.querySelector(
      '.web-title-actions, .cl15i10-header-actions, [class*="header-actions"]'
    );
    if (!existingActions) return;
    if (existingActions.classList.contains('xn-logout-added')) return;
    const hasLogout = [...existingActions.querySelectorAll('button')]
      .some(b => b.textContent.trim() === '登出');
    if (!hasLogout) {
      existingActions.appendChild(makeLogoutBtn());
      existingActions.classList.add('xn-logout-added');
    }
  });
  observer.observe(document.body, { childList: true, subtree: true });
})();
