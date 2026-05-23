from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from app.routes.employee_auth import _employee_current_user_from_request

router = APIRouter(tags=["sales-admin-v2"])

# SHINNAN_SALES_ADMIN_V2_START
@router.get("/admin/sales/v2", response_class=HTMLResponse)
def sales_admin_v2_page(request: Request):
    user = _employee_current_user_from_request(request)
    if not user:
        return RedirectResponse("/employee/login?next=/admin/sales/v2", status_code=303)
    name = str(user.get("display_name") or "管理員")
    role = str(user.get("role") or "")
    return f"""<!doctype html>
<html lang="zh-Hant">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>業務管理後台｜訊南 ERP</title>
  <link rel="stylesheet" href="/static/web_title_unified.css?v=xn_v1">
  <link rel="stylesheet" href="/static/xn_buttons.css?v=xn_v1">
  <link rel="stylesheet" href="/static/sales_admin_v2.css?v=sv2_20260523c">
</head>
<body>
<div class="wrap">

  <section class="web-title web-title-tech" id="xn-page-header">
    <img class="web-title-watermark" src="/static/shinnan_logo_outline_white.png" alt="">
    <div class="web-title-map"></div>
    <div class="web-title-radar"></div>
    <div class="web-title-main">
      <div class="web-title-logo-box">
        <img class="web-title-logo" src="/static/shinnan_logo_gold_transparent.png?v=cl_header_v1" alt="">
      </div>
      <div class="web-title-text">
        <h1 class="web-title-system">業務管理後台</h1>
        <div class="web-title-sub">訊南科技 · {name} · 業務系統 v2</div>
      </div>
      <div class="web-title-actions">
        <a href="/app/sales/v2" class="xn-btn xn-btn-sm">📱 手機版</a>
        <a href="/admin/sales" class="xn-btn xn-btn-sm">舊版後台</a>
        <a href="/app" class="xn-btn xn-btn-sm">首頁</a>
      </div>
    </div>
  </section>

  <!-- ── 頁籤導覽 ── -->
  <div class="sa2-nav">
    <button class="sa2-nav-btn active" onclick="switchPage('dashboard',this)">📊 儀表板</button>
    <button class="sa2-nav-btn" onclick="switchPage('activities',this)">🎯 活動管理</button>
    <button class="sa2-nav-btn" onclick="switchPage('buildings',this)">🏢 大樓總覽</button>
    <button class="sa2-nav-btn" onclick="switchPage('devices',this)">💻 設備庫存</button>
    <button class="sa2-nav-btn" onclick="switchPage('targets',this)">🎖 業務目標</button>
    <button class="sa2-nav-btn" onclick="switchPage('reminders',this)">🔔 提醒管理</button>
  </div>

  <!-- ══ 儀表板頁 ══ -->
  <div id="page-dashboard" class="sa2-page active">
    <div class="sa2-dash-filters">
      <select id="dash-area" onchange="loadDashboard()">
        <option value="">全部區域</option>
      </select>
      <select id="dash-owner" onchange="loadDashboard()">
        <option value="">全部業務</option>
      </select>
      <select id="dash-year" onchange="loadDashboard()"></select>
      <select id="dash-month" onchange="loadDashboard()"></select>
      <button class="xn-btn xn-btn-sm" onclick="loadDashboard()">🔄 更新</button>
    </div>

    <!-- 統計卡 -->
    <div class="sa2-kpi-grid" id="dash-kpi">
      <div class="sa2-kpi-card"><div class="sa2-kpi-n" id="kpi-total">-</div><div class="sa2-kpi-l">業務大樓</div></div>
      <div class="sa2-kpi-card good"><div class="sa2-kpi-n" id="kpi-signed">-</div><div class="sa2-kpi-l">已簽約</div></div>
      <div class="sa2-kpi-card warn"><div class="sa2-kpi-n" id="kpi-negotiating">-</div><div class="sa2-kpi-l">議約中</div></div>
      <div class="sa2-kpi-card danger"><div class="sa2-kpi-n" id="kpi-renewing">-</div><div class="sa2-kpi-l">待續約</div></div>
      <div class="sa2-kpi-card"><div class="sa2-kpi-n" id="kpi-activities">-</div><div class="sa2-kpi-l">本月活動</div></div>
      <div class="sa2-kpi-card good"><div class="sa2-kpi-n" id="kpi-new-users">-</div><div class="sa2-kpi-l">本月新用戶</div></div>
      <div class="sa2-kpi-card danger"><div class="sa2-kpi-n" id="kpi-overdue">-</div><div class="sa2-kpi-l">逾期拜訪</div></div>
      <div class="sa2-kpi-card warn"><div class="sa2-kpi-n" id="kpi-expiring">-</div><div class="sa2-kpi-l">60天到期合約</div></div>
      <div class="sa2-kpi-card good"><div class="sa2-kpi-n" id="kpi-active-users">-</div><div class="sa2-kpi-l">有效用戶</div></div>
      <div class="sa2-kpi-card good"><div class="sa2-kpi-n" id="kpi-revenue">-</div><div class="sa2-kpi-l">月費收入</div></div>
      <div class="sa2-kpi-card"><div class="sa2-kpi-n" id="kpi-penetration">-</div><div class="sa2-kpi-l">整體滲透率</div></div>
    </div>

    <div class="sa2-two-col">
      <!-- 業務員排行 -->
      <div class="sa2-card">
        <div class="sa2-card-title">📈 業務員本月活動排行</div>
        <div id="dash-owner-rank"></div>
      </div>
      <!-- 合約追蹤 -->
      <div class="sa2-card">
        <div class="sa2-card-title">⚠️ 合約到期預警（60天內）</div>
        <div id="dash-expiring"></div>
      </div>
    </div>

    <div class="sa2-two-col">
      <!-- 逾期拜訪 -->
      <div class="sa2-card">
        <div class="sa2-card-title">🔴 逾期未拜訪</div>
        <div id="dash-overdue"></div>
      </div>
      <!-- 活動分佈 -->
      <div class="sa2-card">
        <div class="sa2-card-title">🎯 本月活動類型分佈</div>
        <div id="dash-activity-stats"></div>
      </div>
    </div>
  </div>

  <!-- ══ 活動管理頁 ══ -->
  <div id="page-activities" class="sa2-page">
    <div class="sa2-topbar">
      <div class="sa2-filters">
        <input id="act-kw" class="sa2-input" placeholder="搜尋大樓、類型、負責人" oninput="filterActivities()">
        <select id="act-category" class="sa2-select" onchange="filterActivities()">
          <option value="">全部類別</option>
          <option>業務推廣</option><option>客戶服務</option>
          <option>財務回饋</option><option>關係維護</option><option>其他</option>
        </select>
        <input id="act-date-from" type="date" class="sa2-input" onchange="filterActivities()">
        <span style="color:var(--muted)">~</span>
        <input id="act-date-to" type="date" class="sa2-input" onchange="filterActivities()">
      </div>
      <button class="xn-btn" onclick="openActModal()">+ 新增活動</button>
    </div>
    <div class="sa2-table-wrap">
      <table class="sa2-table" id="act-table">
        <thead>
          <tr>
            <th>日期</th><th>大樓</th><th>區域</th><th>類別</th><th>類型</th>
            <th>負責人</th><th>出席</th><th>新用戶</th><th>費用</th><th>結果</th><th>備註</th><th>操作</th>
          </tr>
        </thead>
        <tbody id="act-tbody"></tbody>
      </table>
    </div>
    <div class="sa2-pagination" id="act-pagination"></div>
  </div>

  <!-- ══ 大樓總覽頁 ══ -->
  <div id="page-buildings" class="sa2-page">
    <div class="sa2-topbar">
      <div class="sa2-filters">
        <input id="bld-kw" class="sa2-input" placeholder="搜尋大樓名稱、總幹事" oninput="filterBuildings()">
        <select id="bld-area" class="sa2-select" onchange="filterBuildings()"><option value="">全部區域</option></select>
        <select id="bld-contract" class="sa2-select" onchange="filterBuildings()">
          <option value="">全部合約</option>
          <option>簽約</option><option>議約中</option><option>待續約</option><option>已流失</option>
        </select>
      </div>
      <button class="xn-btn" onclick="exportBuildingCSV()">📥 匯出 CSV</button>
    </div>
    <div class="sa2-table-wrap">
      <table class="sa2-table" id="bld-table">
        <thead>
          <tr>
            <th>大樓</th><th>區域</th><th>合約狀態</th><th>合約到期</th>
            <th>用戶/總戶</th><th>滲透率</th><th>負責業務</th>
            <th>下次拜訪</th><th>上次活動</th><th>月費收入</th><th>操作</th>
          </tr>
        </thead>
        <tbody id="bld-tbody"></tbody>
      </table>
    </div>
  </div>

  <!-- ══ 設備庫存頁 ══ -->
  <div id="page-devices" class="sa2-page">
    <div class="sa2-topbar">
      <div class="sa2-filters">
        <select id="dev-status" class="sa2-select" onchange="loadDevices()">
          <option value="">全部狀態</option>
          <option value="available">庫存中</option>
          <option value="lent">借出中</option>
          <option value="given">已贈送</option>
          <option value="returned">已歸還</option>
        </select>
        <select id="dev-type" class="sa2-select" onchange="loadDevices()"><option value="">全部類型</option></select>
      </div>
      <button class="xn-btn" onclick="openDevModal()">+ 登錄設備</button>
    </div>
    <div class="sa2-kpi-grid" id="dev-stats" style="margin-bottom:16px;grid-template-columns:repeat(4,1fr)"></div>
    <div class="sa2-table-wrap">
      <table class="sa2-table">
        <thead>
          <tr><th>設備編號</th><th>類型</th><th>型號</th><th>序號</th><th>狀態</th><th>大樓</th><th>負責人</th><th>借出日</th><th>預計歸還</th><th>操作</th></tr>
        </thead>
        <tbody id="dev-tbody"></tbody>
      </table>
    </div>
  </div>

  <!-- ══ 業務目標頁 ══ -->
  <div id="page-targets" class="sa2-page">
    <div class="sa2-topbar">
      <div class="sa2-filters">
        <select id="tgt-year" class="sa2-select" onchange="loadTargets()"></select>
        <select id="tgt-month" class="sa2-select" onchange="loadTargets()"></select>
        <select id="tgt-area" class="sa2-select" onchange="loadTargets()"><option value="">全部區域</option></select>
      </div>
      <button class="xn-btn" onclick="openTgtModal()">+ 設定目標</button>
    </div>
    <div class="sa2-table-wrap">
      <table class="sa2-table">
        <thead>
          <tr>
            <th>業務員</th><th>區域</th>
            <th>目標新用戶</th><th>實際</th><th>達成率</th>
            <th>目標合約</th><th>實際</th><th>達成率</th>
            <th>目標拜訪</th><th>實際</th><th>達成率</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody id="tgt-tbody"></tbody>
      </table>
    </div>
  </div>

  <!-- ══ 提醒管理頁 ══ -->
  <div id="page-reminders" class="sa2-page">
    <div class="sa2-topbar">
      <div class="sa2-filters">
        <select id="rem-status" class="sa2-select" onchange="loadAdminReminders()">
          <option value="">全部狀態</option>
          <option value="pending">待處理</option>
          <option value="done">已完成</option>
        </select>
        <input id="rem-kw" class="sa2-input" placeholder="搜尋大樓、類型" oninput="filterReminders()">
      </div>
      <button class="xn-btn" onclick="fetch('/api/v2/sales/reminders/auto-generate',{{method:'POST',credentials:'same-origin'}}).then(r=>r.json()).then(d=>{{alert(d.message||'完成');loadAdminReminders();}})">🤖 自動生成提醒</button>
    </div>
    <div class="sa2-table-wrap">
      <table class="sa2-table">
        <thead>
          <tr><th>提醒日期</th><th>大樓</th><th>區域</th><th>類型</th><th>狀態</th><th>自動</th><th>備註</th><th>操作</th></tr>
        </thead>
        <tbody id="rem-tbody"></tbody>
      </table>
    </div>
  </div>

</div>

<!-- ── 新增活動 Modal ── -->
<div id="act-modal" class="sa2-modal-overlay" onclick="if(event.target===this)closeActModal()">
  <div class="sa2-modal">
    <div class="sa2-modal-header">
      <div class="sa2-modal-title" id="act-modal-title">新增活動</div>
      <button class="sa2-modal-close" onclick="closeActModal()">✕</button>
    </div>
    <div class="sa2-modal-body">
      <div class="sa2-form-grid">
        <div><label class="sa2-label">大樓編號 *</label><input id="af-building" class="sa2-field" placeholder="B001..."></div>
        <div><label class="sa2-label">活動日期 *</label><input id="af-date" type="date" class="sa2-field"></div>
        <div>
          <label class="sa2-label">活動類別 *</label>
          <select id="af-category" class="sa2-field" onchange="updateTypeOptions()">
            <option value="業務推廣">業務推廣</option><option value="客戶服務">客戶服務</option>
            <option value="財務回饋">財務回饋</option><option value="關係維護">關係維護</option>
            <option value="其他">其他</option>
          </select>
        </div>
        <div>
          <label class="sa2-label">活動類型 *</label>
          <select id="af-type" class="sa2-field"></select>
        </div>
        <div><label class="sa2-label">負責人</label><input id="af-owner" class="sa2-field"></div>
        <div><label class="sa2-label">地點</label><input id="af-location" class="sa2-field"></div>
        <div><label class="sa2-label">出席人數</label><input id="af-participants" type="number" class="sa2-field" value="0" min="0"></div>
        <div><label class="sa2-label">新增用戶數</label><input id="af-new-users" type="number" class="sa2-field" value="0" min="0"></div>
        <div><label class="sa2-label">費用 (NT$)</label><input id="af-cost" type="number" class="sa2-field" value="0" min="0"></div>
        <div><label class="sa2-label">結果</label><input id="af-result" class="sa2-field" placeholder="活動成效..."></div>
      </div>
      <label class="sa2-label">備註</label>
      <textarea id="af-note" class="sa2-field" rows="3" style="width:100%;resize:vertical;" placeholder="活動重點、議程..."></textarea>
    </div>
    <div class="sa2-modal-footer">
      <button class="xn-btn xn-btn-outline" onclick="closeActModal()">取消</button>
      <button class="xn-btn" onclick="saveActivity()">💾 儲存</button>
    </div>
  </div>
</div>

<!-- ── 新增設備 Modal ── -->
<div id="dev-modal" class="sa2-modal-overlay" onclick="if(event.target===this)closeDevModal()">
  <div class="sa2-modal">
    <div class="sa2-modal-header">
      <div class="sa2-modal-title">登錄設備</div>
      <button class="sa2-modal-close" onclick="closeDevModal()">✕</button>
    </div>
    <div class="sa2-modal-body">
      <div class="sa2-form-grid">
        <div><label class="sa2-label">設備編號</label><input id="df-no" class="sa2-field" placeholder="自動編號可留空"></div>
        <div>
          <label class="sa2-label">設備類型 *</label>
          <select id="df-type" class="sa2-field">
            <option>電腦</option><option>平板</option><option>手機</option>
            <option>路由器</option><option>電視棒</option><option>其他</option>
          </select>
        </div>
        <div><label class="sa2-label">型號</label><input id="df-model" class="sa2-field"></div>
        <div><label class="sa2-label">序號</label><input id="df-serial" class="sa2-field"></div>
        <div>
          <label class="sa2-label">狀態</label>
          <select id="df-status" class="sa2-field">
            <option value="available">庫存中</option>
            <option value="lent">借出中</option>
            <option value="given">已贈送</option>
          </select>
        </div>
        <div><label class="sa2-label">大樓編號</label><input id="df-building" class="sa2-field" placeholder="借出/贈送時填寫"></div>
        <div><label class="sa2-label">負責業務</label><input id="df-owner" class="sa2-field"></div>
        <div><label class="sa2-label">借出日期</label><input id="df-lend-date" type="date" class="sa2-field"></div>
      </div>
      <label class="sa2-label">備註</label>
      <textarea id="df-note" class="sa2-field" rows="2" style="width:100%;"></textarea>
    </div>
    <div class="sa2-modal-footer">
      <button class="xn-btn xn-btn-outline" onclick="closeDevModal()">取消</button>
      <button class="xn-btn" onclick="saveDevice()">💾 儲存</button>
    </div>
  </div>
</div>

<!-- ── 設定目標 Modal ── -->
<div id="tgt-modal" class="sa2-modal-overlay" onclick="if(event.target===this)closeTgtModal()">
  <div class="sa2-modal">
    <div class="sa2-modal-header">
      <div class="sa2-modal-title">設定業務目標</div>
      <button class="sa2-modal-close" onclick="closeTgtModal()">✕</button>
    </div>
    <div class="sa2-modal-body">
      <div class="sa2-form-grid">
        <div><label class="sa2-label">業務員 *</label><input id="tf-owner" class="sa2-field"></div>
        <div><label class="sa2-label">區域</label><input id="tf-area" class="sa2-field"></div>
        <div><label class="sa2-label">年份 *</label><input id="tf-year" type="number" class="sa2-field"></div>
        <div><label class="sa2-label">月份 *</label><input id="tf-month" type="number" class="sa2-field" min="1" max="12"></div>
        <div><label class="sa2-label">目標新用戶</label><input id="tf-new-users" type="number" class="sa2-field" value="0"></div>
        <div><label class="sa2-label">目標合約</label><input id="tf-contracts" type="number" class="sa2-field" value="0"></div>
        <div><label class="sa2-label">目標拜訪次數</label><input id="tf-visits" type="number" class="sa2-field" value="0"></div>
        <div><label class="sa2-label">目標活動次數</label><input id="tf-activities" type="number" class="sa2-field" value="0"></div>
      </div>
    </div>
    <div class="sa2-modal-footer">
      <button class="xn-btn xn-btn-outline" onclick="closeTgtModal()">取消</button>
      <button class="xn-btn" onclick="saveTarget()">💾 儲存</button>
    </div>
  </div>
</div>

<script src="/static/sales_admin_v2.js?v=sv2_20260523c"></script>
</body></html>"""
# SHINNAN_SALES_ADMIN_V2_END
