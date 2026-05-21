import sys
sys.stdout.reconfigure(encoding='utf-8')

fpath = r"D:\shinnan ERP\app\routes\hr_admin.py"
content = open(fpath, encoding='utf-8').read()

# 找 hr_home_page 函式，替換 body
OLD_BODY = '''    body = f"""
      <section class="summary">
        <div class="summary-card"><div class="summary-label">員工總數</div><div class="summary-value">{total}</div></div>
        <div class="summary-card"><div class="summary-label">在職員工</div><div class="summary-value">{active}</div></div>
        <div class="summary-card"><div class="summary-label">帳號啟用</div><div class="summary-value">{enabled}</div></div>
        <div class="summary-card"><div class="summary-label">部門數</div><div class="summary-value">{departments}</div></div>
      </section>

      <section class="dashboard-grid">
        <div class="dash-panel">
          <div class="dash-panel-title">📋 待辦事項</div>
          <ul class="dash-list">
            <li><a href="/admin/hr/leave-requests">請假審核 — 點此查看待審假單</a></li>
            <li><a href="/admin/hr/leave-management">排休管理 — 確認本月值班安排</a></li>
            <li><a href="/admin/hr/passwords">帳號管理 — 檢查停用或異常帳號</a></li>
          </ul>
        </div>
        <div class="dash-panel">
          <div class="dash-panel-title">👥 人員狀況</div>
          <table class="dash-table">
            <tr><td>在職人數</td><td class="val">{active} 人</td></tr>
            <tr><td>帳號啟用</td><td class="val">{enabled} 人</td></tr>
            <tr><td>帳號停用</td><td class="val">{total - enabled} 人</td></tr>
            <tr><td>部門數</td><td class="val">{departments} 個</td></tr>
          </table>
        </div>
        <div class="dash-panel">
          <div class="dash-panel-title">⚡ 快速入口</div>
          <div class="dash-shortcuts">
            <a href="/admin/hr/employees" class="shortcut-btn">員工名冊</a>
            <a href="/admin/hr/permissions" class="shortcut-btn">權限管理</a>
            <a href="/admin/hr/payroll" class="shortcut-btn">薪資試算</a>
            <a href="/admin/hr/change-logs" class="shortcut-btn">異動紀錄</a>
          </div>
        </div>
      </section>
    """'''

print("找到:", OLD_BODY in content)
