/* sales_admin_v2.js */
const SA2 = (function(){

function esc(s){return String(s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');}
async function api(url,opts={}){const r=await fetch(url,{credentials:'same-origin',cache:'no-store',...opts});return r.json();}

const today = new Date().toISOString().slice(0,10);
const thisYear = new Date().getFullYear();
const thisMonth = new Date().getMonth()+1;

let allActivities=[], allBuildings=[], allDevices=[], allReminders=[];
let actPage=1; const actPageSize=50;

const ACT_TYPES = {
  '業務推廣':['說明會','DM投放','促銷活動','展覽參與'],
  '客戶服務':['設備贈送','設備出借','設備整修','公設維護','技術支援'],
  '財務回饋':['資金回饋','折扣優惠','免費升速','續約優惠'],
  '關係維護':['管委會拜訪','總幹事拜訪','住戶大會','業主大會','客戶拜訪'],
  '其他':['競業回報','客訴處理','其他'],
};

/* ── 頁籤切換 ── */
function switchPage(id, el){
  document.querySelectorAll('.sa2-nav-btn').forEach(b=>b.classList.remove('active'));
  document.querySelectorAll('.sa2-page').forEach(p=>p.classList.remove('active'));
  if(el) el.classList.add('active');
  document.getElementById('page-'+id).classList.add('active');
  if(id==='dashboard') loadDashboard();
  if(id==='activities') loadActivities();
  if(id==='buildings')  loadBuildings();
  if(id==='devices')    loadDevices();
  if(id==='targets')    loadTargets();
  if(id==='reminders')  loadAdminReminders();
}

/* ══ 儀表板 ══ */
async function loadDashboard(){
  const area  = document.getElementById('dash-area')?.value||'';
  const owner = document.getElementById('dash-owner')?.value||'';
  const year  = document.getElementById('dash-year')?.value||thisYear;
  const month = document.getElementById('dash-month')?.value||thisMonth;
  const params = new URLSearchParams({area,owner,year,month});
  const d = await api('/api/v2/sales/dashboard?'+params);
  if(!d.ok) return;
  const data = d.data;

  // 計算合約統計
  const contracts = data.contract_stats||[];
  // 合約狀態對應：簽約/有效 都算已簽
  const signed = contracts.filter(c=>c.contract_status==='簽約'||c.contract_status==='有效').reduce((s,c)=>s+(c.cnt||0),0);
  const nego   = contracts.find(c=>c.contract_status==='議約中')?.cnt||0;
  const renew  = contracts.find(c=>c.contract_status==='待續約')?.cnt||0;
  const lost   = contracts.find(c=>c.contract_status==='已流失')?.cnt||0;
  const total  = contracts.reduce((s,c)=>s+(c.cnt||0),0);

  const actStats = data.activity_stats||[];
  const totalAct = actStats.reduce((s,a)=>s+(a.cnt||0),0);
  const totalNew = actStats.reduce((s,a)=>s+(a.new_users||0),0);

  // 成長數據
  const gr = data.growth||{};
  const activeUsers = gr.current_users||0;
  const totalHH = gr.total_households||0;
  const monthlyRev = gr.monthly_revenue||0;
  const penRate = totalHH>0 ? Math.round(activeUsers/totalHH*100) : 0;

  document.getElementById('kpi-total').textContent = total;
  document.getElementById('kpi-signed').textContent = signed;
  document.getElementById('kpi-negotiating').textContent = nego;
  document.getElementById('kpi-renewing').textContent = renew;
  document.getElementById('kpi-activities').textContent = totalAct;
  document.getElementById('kpi-new-users').textContent = totalNew;
  document.getElementById('kpi-overdue').textContent = (data.overdue_visits||[]).length;
  document.getElementById('kpi-expiring').textContent = (data.expiring||[]).length;

  // 額外成長指標
  const elUsers = document.getElementById('kpi-active-users');
  const elRev   = document.getElementById('kpi-revenue');
  const elPen   = document.getElementById('kpi-penetration');
  if(elUsers) elUsers.textContent = activeUsers.toLocaleString();
  if(elRev)   elRev.textContent   = 'NT$' + Math.round(monthlyRev/10000) + '萬';
  if(elPen)   elPen.textContent   = penRate + '%';

  // 業務員排行
  const owners = data.owner_stats||[];
  document.getElementById('dash-owner-rank').innerHTML = owners.length
    ? owners.map((o,i)=>`<div class="sa2-rank-row">
        <div class="sa2-rank-num ${i===0?'gold':i===1?'silver':i===2?'bronze':''}">${i+1}</div>
        <div class="sa2-rank-name">${esc(o.owner)}</div>
        <div style="font-size:11px;color:var(--muted);margin-right:12px;">${o.building_count}棟·${o.activity_count}活動</div>
        <div class="sa2-rank-val">+${o.new_users}戶</div>
      </div>`).join('')
    : '<div style="color:var(--muted);font-size:13px;padding:12px 0;">本月尚無活動記錄</div>';

  // 合約到期
  const expiring = data.expiring||[];
  document.getElementById('dash-expiring').innerHTML = expiring.length
    ? `<table style="width:100%;font-size:12px;border-collapse:collapse;">
        <thead><tr style="color:var(--muted)"><th style="padding:6px 8px;text-align:left;">大樓</th><th>區域</th><th>業務</th><th>到期日</th></tr></thead>
        <tbody>${expiring.map(e=>`<tr style="border-top:1px solid #f1f5f9;">
          <td style="padding:6px 8px;font-weight:900">${esc(e.name||'-')}</td>
          <td style="padding:6px 8px">${esc(e.area||'-')}</td>
          <td style="padding:6px 8px">${esc(e.owner||'-')}</td>
          <td style="padding:6px 8px;color:var(--red);font-weight:1000">${esc(e.contract_end_date)}</td>
        </tr>`).join('')}</tbody></table>`
    : '<div style="color:var(--muted);font-size:13px;padding:12px 0;">60天內無合約到期</div>';

  // 逾期拜訪
  const overdue = data.overdue_visits||[];
  document.getElementById('dash-overdue').innerHTML = overdue.length
    ? `<table style="width:100%;font-size:12px;border-collapse:collapse;">
        <thead><tr style="color:var(--muted)"><th style="padding:6px 8px;text-align:left;">大樓</th><th>區域</th><th>業務</th><th>預定拜訪</th></tr></thead>
        <tbody>${overdue.map(e=>`<tr style="border-top:1px solid #f1f5f9;">
          <td style="padding:6px 8px;font-weight:900">${esc(e.name||'-')}</td>
          <td style="padding:6px 8px">${esc(e.area||'-')}</td>
          <td style="padding:6px 8px">${esc(e.owner||'-')}</td>
          <td style="padding:6px 8px;color:var(--red);font-weight:1000">${esc(e.next_visit)}</td>
        </tr>`).join('')}</tbody></table>`
    : '<div style="color:var(--green);font-size:13px;padding:12px 0;">✅ 無逾期拜訪</div>';

  // 活動類型分佈
  document.getElementById('dash-activity-stats').innerHTML = actStats.length
    ? actStats.map(a=>`<div style="display:flex;align-items:center;gap:10px;padding:6px 0;border-bottom:1px solid #f1f5f9;font-size:13px;">
        <div style="flex:1;font-weight:900">${esc(a.activity_category||'-')}</div>
        <div style="color:var(--muted);font-size:11px;margin-right:8px;">${a.cnt}次</div>
        <div class="sa2-progress" style="width:80px"><div class="sa2-progress-fill green" style="width:${Math.min(100,a.cnt/Math.max(1,totalAct)*100)}%"></div></div>
      </div>`).join('')
    : '<div style="color:var(--muted);font-size:13px;padding:12px 0;">本月尚無活動</div>';
}

/* ══ 活動管理 ══ */
async function loadActivities(){
  const d = await api('/api/v2/sales/activities?limit=500');
  allActivities = d.ok ? (d.data||[]) : [];
  filterActivities();
}

function filterActivities(){
  const kw = document.getElementById('act-kw')?.value.toLowerCase()||'';
  const cat = document.getElementById('act-category')?.value||'';
  const df  = document.getElementById('act-date-from')?.value||'';
  const dt  = document.getElementById('act-date-to')?.value||'';
  let rows = allActivities.filter(a=>{
    if(kw && ![a.building_name,a.area,a.activity_type,a.owner].join(' ').toLowerCase().includes(kw)) return false;
    if(cat && a.activity_category !== cat) return false;
    if(df && a.activity_date < df) return false;
    if(dt && a.activity_date > dt) return false;
    return true;
  });
  actPage = 1;
  renderActivities(rows);
}

function renderActivities(rows){
  const total = rows.length;
  const pages = Math.ceil(total/actPageSize);
  const slice = rows.slice((actPage-1)*actPageSize, actPage*actPageSize);
  const tbody = document.getElementById('act-tbody');
  if(!tbody) return;

  tbody.innerHTML = slice.map(a=>`<tr>
    <td style="white-space:nowrap">${esc(a.activity_date)}</td>
    <td style="font-weight:900">${esc(a.building_name||a.building_no)}</td>
    <td>${esc(a.area||'-')}</td>
    <td>${catBadge(a.activity_category)}</td>
    <td>${esc(a.activity_type)}</td>
    <td>${esc(a.owner||'-')}</td>
    <td style="text-align:center">${a.participants||0}</td>
    <td style="text-align:center;color:var(--green);font-weight:1000">${a.new_users||0}</td>
    <td style="text-align:right">${a.cost?'NT$'+(a.cost||0).toLocaleString():'-'}</td>
    <td>${esc(a.result||'-')}</td>
    <td style="max-width:160px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap" title="${esc(a.note||'')}">${esc(a.note||'-')}</td>
    <td>
      <button class="sa2-btn-sm sa2-btn-danger" onclick="deleteActivity(${a.id})">刪除</button>
    </td>
  </tr>`).join('');

  // 分頁
  const pg = document.getElementById('act-pagination');
  if(pg){
    let html = `<span style="font-size:12px;color:var(--muted)">共 ${total} 筆</span>`;
    for(let i=1;i<=Math.min(pages,10);i++){
      html += `<button class="sa2-page-btn ${i===actPage?'active':''}" onclick="SA2.goPage(${i})">${i}</button>`;
    }
    pg.innerHTML = html;
  }
}

function goPage(p){ actPage=p; filterActivities(); }

function catBadge(cat){
  const m={'業務推廣':'blue','客戶服務':'green','財務回饋':'orange','關係維護':'purple','其他':'gray'};
  const cls = 'sa2-badge sa2-badge-'+(m[cat]||'gray');
  return `<span class="${cls}">${esc(cat||'-')}</span>`;
}

async function deleteActivity(id){
  if(!confirm('確認刪除此活動？')) return;
  const r = await api('/api/v2/sales/activities/'+id, {method:'DELETE'});
  if(r.ok){loadActivities();}else{alert(r.error||'刪除失敗');}
}

/* ── 活動 Modal ── */
let editActId = null;
function openActModal(id=null){
  editActId = id;
  document.getElementById('act-modal-title').textContent = id ? '編輯活動' : '新增活動';
  document.getElementById('af-building').value = '';
  document.getElementById('af-date').value = today;
  document.getElementById('af-owner').value = '';
  document.getElementById('af-result').value = '';
  document.getElementById('af-note').value = '';
  document.getElementById('af-participants').value = 0;
  document.getElementById('af-new-users').value = 0;
  document.getElementById('af-cost').value = 0;
  updateTypeOptions();
  document.getElementById('act-modal').classList.add('open');
}
function closeActModal(){ document.getElementById('act-modal').classList.remove('open'); }

function updateTypeOptions(){
  const cat = document.getElementById('af-category')?.value||'業務推廣';
  const types = ACT_TYPES[cat]||[];
  document.getElementById('af-type').innerHTML = types.map(t=>`<option>${t}</option>`).join('');
}

async function saveActivity(){
  const body = {
    building_no:       document.getElementById('af-building').value.trim(),
    activity_category: document.getElementById('af-category').value,
    activity_type:     document.getElementById('af-type').value,
    activity_date:     document.getElementById('af-date').value,
    owner:             document.getElementById('af-owner').value.trim(),
    result:            document.getElementById('af-result').value.trim(),
    note:              document.getElementById('af-note').value.trim(),
    participants:      parseInt(document.getElementById('af-participants').value)||0,
    new_users:         parseInt(document.getElementById('af-new-users').value)||0,
    cost:              parseInt(document.getElementById('af-cost').value)||0,
  };
  if(!body.building_no||!body.activity_date){alert('請填寫大樓編號和日期');return;}
  const url = editActId ? '/api/v2/sales/activities/'+editActId : '/api/v2/sales/activities';
  const method = editActId ? 'PUT' : 'POST';
  const r = await api(url, {method, headers:{'Content-Type':'application/json'}, body:JSON.stringify(body)});
  if(r.ok){closeActModal();loadActivities();}else{alert(r.error||'儲存失敗');}
}

/* ══ 大樓總覽 ══ */
async function loadBuildings(){
  const d = await api('/api/app/sales/business-records?ts='+Date.now());
  allBuildings = Array.isArray(d) ? d : (d.items||d.records||[]);
  // 填充區域下拉
  const areas = [...new Set(allBuildings.map(b=>b.area||'').filter(Boolean))].sort();
  const areaEl = document.getElementById('bld-area');
  if(areaEl) areaEl.innerHTML = '<option value="">全部區域</option>' + areas.map(a=>`<option>${a}</option>`).join('');
  filterBuildings();
}

function filterBuildings(){
  const kw  = document.getElementById('bld-kw')?.value.toLowerCase()||'';
  const area= document.getElementById('bld-area')?.value||'';
  const con = document.getElementById('bld-contract')?.value||'';
  const rows = allBuildings.filter(b=>{
    if(kw && ![b.building_name,b.manager_name,b.area].join(' ').toLowerCase().includes(kw)) return false;
    if(area && b.area !== area) return false;
    if(con && b.contract_status !== con) return false;
    return true;
  });
  renderBuildings(rows);
}

function renderBuildings(rows){
  const tbody = document.getElementById('bld-tbody');
  if(!tbody) return;
  tbody.innerHTML = rows.map(b=>{
    const od = b.next_visit && b.next_visit < today;
    const pen = b.total_households > 0 ? Math.round(b.active_users/b.total_households*100) : 0;
    return `<tr>
      <td style="font-weight:1000"><a href="/app/sales/v2" style="color:var(--blue);text-decoration:none">${esc(b.building_name||'-')}</a></td>
      <td>${esc(b.area||'-')}</td>
      <td>${contractBadge(b.contract_status)}</td>
      <td style="${b.contract_end_date&&b.contract_end_date<today?'color:var(--red);font-weight:1000':''}">${esc(b.contract_end_date||'-')}</td>
      <td style="text-align:center">${b.active_users||0}/${b.total_households||0}</td>
      <td>
        <div style="display:flex;align-items:center;gap:6px;">
          <div class="sa2-progress"><div class="sa2-progress-fill ${pen>=15?'green':pen>=5?'orange':'red'}" style="width:${Math.min(100,pen*3)}%"></div></div>
          <span style="font-size:12px;font-weight:1000">${pen}%</span>
        </div>
      </td>
      <td>${esc(b.owner||'-')}</td>
      <td style="${od?'color:var(--red);font-weight:1000':''}">${esc(b.next_visit||'-')}${od?' ⚠':''}</td>
      <td>${esc(b.last_activity_date||'-')}</td>
      <td style="text-align:right;color:var(--green);font-weight:1000">${b.monthly_revenue?'NT$'+(b.monthly_revenue||0).toLocaleString():'-'}</td>
      <td>
        <a href="/app/sales/v2" class="sa2-btn-sm" style="text-decoration:none">詳細</a>
      </td>
    </tr>`;
  }).join('');
}

function contractBadge(c){
  if(!c) return '<span class="sa2-badge sa2-badge-gray">-</span>';
  if(c==='簽約') return '<span class="sa2-badge sa2-badge-green">'+esc(c)+'</span>';
  if(c==='議約中') return '<span class="sa2-badge sa2-badge-orange">'+esc(c)+'</span>';
  if(c==='待續約') return '<span class="sa2-badge sa2-badge-red">'+esc(c)+'</span>';
  return '<span class="sa2-badge sa2-badge-gray">'+esc(c)+'</span>';
}

function exportBuildingCSV(){
  const rows = allBuildings;
  const header = ['大樓','區域','合約狀態','合約到期','用戶數','總戶數','滲透率','負責業務','下次拜訪','月費收入'];
  const lines = [header.join(',')];
  rows.forEach(b=>{
    const pen = b.total_households>0 ? Math.round(b.active_users/b.total_households*100) : 0;
    lines.push([b.building_name,b.area,b.contract_status,b.contract_end_date,b.active_users,b.total_households,pen+'%',b.owner,b.next_visit,b.monthly_revenue].map(v=>'"'+(v||'')+'"').join(','));
  });
  const blob = new Blob(['\uFEFF'+lines.join('\n')], {type:'text/csv;charset=utf-8;'});
  const a = document.createElement('a'); a.href = URL.createObjectURL(blob);
  a.download = '業務大樓總覽_'+today+'.csv'; a.click();
}

/* ══ 設備庫存 ══ */
async function loadDevices(){
  const status = document.getElementById('dev-status')?.value||'';
  const params = status ? '?status='+status : '';
  const d = await api('/api/v2/sales/devices'+params);
  allDevices = d.ok ? (d.data||[]) : [];
  // 統計
  const avail   = allDevices.filter(v=>v.status==='available').length;
  const lent    = allDevices.filter(v=>v.status==='lent').length;
  const given   = allDevices.filter(v=>v.status==='given').length;
  const total   = allDevices.length;
  document.getElementById('dev-stats').innerHTML = `
    <div class="sa2-kpi-card"><div class="sa2-kpi-n">${total}</div><div class="sa2-kpi-l">總計</div></div>
    <div class="sa2-kpi-card good"><div class="sa2-kpi-n">${avail}</div><div class="sa2-kpi-l">庫存中</div></div>
    <div class="sa2-kpi-card warn"><div class="sa2-kpi-n">${lent}</div><div class="sa2-kpi-l">借出中</div></div>
    <div class="sa2-kpi-card"><div class="sa2-kpi-n">${given}</div><div class="sa2-kpi-l">已贈送</div></div>`;
  const tbody = document.getElementById('dev-tbody');
  if(tbody) tbody.innerHTML = allDevices.map(d=>`<tr>
    <td style="font-weight:900">${esc(d.device_no||'-')}</td>
    <td>${esc(d.device_type)}</td>
    <td>${esc(d.model||'-')}</td>
    <td style="font-size:11px;color:var(--muted)">${esc(d.serial||'-')}</td>
    <td>${statusBadge(d.status)}</td>
    <td>${esc(d.building_name||d.building_no||'-')}</td>
    <td>${esc(d.owner||'-')}</td>
    <td>${esc(d.lend_date||'-')}</td>
    <td>${esc(d.return_date||'-')}</td>
    <td>
      ${d.status==='lent'?`<button class="sa2-btn-sm" onclick="returnDevice(${d.id})">歸還</button>`:''}
      <button class="sa2-btn-sm sa2-btn-danger" onclick="deleteDevice(${d.id})">刪除</button>
    </td>
  </tr>`).join('');
}

function statusBadge(s){
  const m={available:'green',lent:'orange',given:'blue',returned:'gray'};
  const lbl={available:'庫存中',lent:'借出中',given:'已贈送',returned:'已歸還'};
  return `<span class="sa2-badge sa2-badge-${m[s]||'gray'}">${lbl[s]||s}</span>`;
}

async function returnDevice(id){
  if(!confirm('確認歸還此設備？')) return;
  const r = await api('/api/v2/sales/devices/'+id+'/return', {method:'PUT', headers:{'Content-Type':'application/json'}, body:JSON.stringify({return_date:today})});
  if(r.ok){loadDevices();}else{alert(r.error||'操作失敗');}
}

async function deleteDevice(id){
  if(!confirm('確認刪除此設備紀錄？')) return;
  // 設備目前無 DELETE API，暫用歸還代替
  alert('請聯絡系統管理員刪除設備紀錄');
}

function openDevModal(){ document.getElementById('dev-modal').classList.add('open'); }
function closeDevModal(){ document.getElementById('dev-modal').classList.remove('open'); }

async function saveDevice(){
  const body = {
    device_no:   document.getElementById('df-no').value.trim(),
    device_type: document.getElementById('df-type').value,
    model:       document.getElementById('df-model').value.trim(),
    serial:      document.getElementById('df-serial').value.trim(),
    status:      document.getElementById('df-status').value,
    building_no: document.getElementById('df-building').value.trim(),
    owner:       document.getElementById('df-owner').value.trim(),
    lend_date:   document.getElementById('df-lend-date').value,
    note:        document.getElementById('df-note').value.trim(),
  };
  if(!body.device_type){alert('請選擇設備類型');return;}
  const r = await api('/api/v2/sales/devices', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(body)});
  if(r.ok){closeDevModal();loadDevices();}else{alert(r.error||'儲存失敗');}
}

/* ══ 業務目標 ══ */
async function loadTargets(){
  const year  = document.getElementById('tgt-year')?.value||thisYear;
  const month = document.getElementById('tgt-month')?.value||thisMonth;
  const params = new URLSearchParams({year,month});
  const d = await api('/api/v2/sales/targets?'+params);
  const rows = d.ok ? (d.data||[]) : [];
  const tbody = document.getElementById('tgt-tbody');
  if(!tbody) return;
  tbody.innerHTML = rows.length ? rows.map(t=>{
    const nPct = t.target_new_users>0 ? Math.round(t.actual_new_users/t.target_new_users*100) : 0;
    const cPct = t.target_contracts>0 ? Math.round(t.actual_contracts/t.target_contracts*100) : 0;
    const vPct = t.target_visits>0 ? Math.round(t.actual_visits/t.target_visits*100) : 0;
    return `<tr>
      <td style="font-weight:1000">${esc(t.owner)}</td>
      <td>${esc(t.area||'-')}</td>
      <td style="text-align:center">${t.target_new_users}</td>
      <td style="text-align:center;font-weight:1000">${t.actual_new_users}</td>
      <td>${progressCell(nPct)}</td>
      <td style="text-align:center">${t.target_contracts}</td>
      <td style="text-align:center;font-weight:1000">${t.actual_contracts}</td>
      <td>${progressCell(cPct)}</td>
      <td style="text-align:center">${t.target_visits}</td>
      <td style="text-align:center;font-weight:1000">${t.actual_visits}</td>
      <td>${progressCell(vPct)}</td>
      <td><button class="sa2-btn-sm" onclick="SA2.openTgtModal()">編輯</button></td>
    </tr>`;
  }).join('') : '<tr><td colspan="12" style="text-align:center;padding:24px;color:var(--muted)">尚無目標設定</td></tr>';
}

function progressCell(pct){
  const cls = pct>=100?'green':pct>=60?'orange':'red';
  return `<div style="display:flex;align-items:center;gap:6px;">
    <div class="sa2-progress"><div class="sa2-progress-fill ${cls}" style="width:${Math.min(100,pct)}%"></div></div>
    <span style="font-size:11px;font-weight:1000;color:var(--${cls==='green'?'green':cls==='orange'?'orange':'red'})">${pct}%</span>
  </div>`;
}

function openTgtModal(){
  const y = document.getElementById('tgt-year')?.value||thisYear;
  const m = document.getElementById('tgt-month')?.value||thisMonth;
  document.getElementById('tf-year').value = y;
  document.getElementById('tf-month').value = m;
  document.getElementById('tgt-modal').classList.add('open');
}
function closeTgtModal(){ document.getElementById('tgt-modal').classList.remove('open'); }

async function saveTarget(){
  const body = {
    owner:             document.getElementById('tf-owner').value.trim(),
    area:              document.getElementById('tf-area').value.trim(),
    year:              parseInt(document.getElementById('tf-year').value),
    month:             parseInt(document.getElementById('tf-month').value),
    target_new_users:  parseInt(document.getElementById('tf-new-users').value)||0,
    target_contracts:  parseInt(document.getElementById('tf-contracts').value)||0,
    target_visits:     parseInt(document.getElementById('tf-visits').value)||0,
    target_activities: parseInt(document.getElementById('tf-activities').value)||0,
  };
  if(!body.owner||!body.year||!body.month){alert('請填寫必要欄位');return;}
  const r = await api('/api/v2/sales/targets', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(body)});
  if(r.ok){closeTgtModal();loadTargets();}else{alert(r.error||'儲存失敗');}
}

/* ══ 提醒管理 ══ */
async function loadAdminReminders(){
  const status = document.getElementById('rem-status')?.value||'';
  const url = '/api/v2/sales/reminders?days=90' + (status?'&status='+status:'');
  const d = await api(url);
  allReminders = d.ok ? (d.data||[]) : [];
  filterReminders();
}

function filterReminders(){
  const kw = document.getElementById('rem-kw')?.value.toLowerCase()||'';
  const rows = allReminders.filter(r=>{
    if(kw && ![r.building_name,r.reminder_type,r.area].join(' ').toLowerCase().includes(kw)) return false;
    return true;
  });
  const tbody = document.getElementById('rem-tbody');
  if(!tbody) return;
  const tday = today;
  tbody.innerHTML = rows.map(r=>{
    const dt = new Date(r.remind_date); dt.setHours(0,0,0,0);
    const now = new Date(); now.setHours(0,0,0,0);
    const diff = Math.ceil((dt-now)/86400000);
    const urgent = diff<=7;
    return `<tr style="${urgent&&r.status!=='done'?'background:#fff8f8':''}">
      <td style="${urgent&&r.status!=='done'?'color:var(--red);font-weight:1000':''}">${esc(r.remind_date)}${urgent&&r.status!=='done'?' ('+diff+'天)':''}</td>
      <td style="font-weight:900">${esc(r.building_name||r.building_no)}</td>
      <td>${esc(r.area||'-')}</td>
      <td>${esc(r.reminder_type)}</td>
      <td><span class="sa2-badge ${r.status==='done'?'sa2-badge-green':'sa2-badge-orange'}">${r.status==='done'?'已完成':'待處理'}</span></td>
      <td style="text-align:center">${r.auto_generated?'🤖 自動':'手動'}</td>
      <td style="max-width:200px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">${esc(r.note||'-')}</td>
      <td>
        ${r.status!=='done'?`<button class="sa2-btn-sm" onclick="doneReminder(${r.id})">✓ 完成</button>`:''}
      </td>
    </tr>`;
  }).join('');
}

async function doneReminder(id){
  const r = await api('/api/v2/sales/reminders/'+id+'/done', {method:'POST'});
  if(r.ok){loadAdminReminders();}else{alert(r.error||'操作失敗');}
}

/* ── Init ── */
function init(){
  // 填充年月選擇器
  ['dash-year','tgt-year'].forEach(id=>{
    const el = document.getElementById(id);
    if(el) for(let y=thisYear;y>=thisYear-3;y--) el.innerHTML += `<option ${y===thisYear?'selected':''}>${y}</option>`;
  });
  ['dash-month','tgt-month'].forEach(id=>{
    const el = document.getElementById(id);
    if(el) for(let m=1;m<=12;m++) el.innerHTML += `<option ${m===thisMonth?'selected':''}>${m}</option>`;
  });
  updateTypeOptions();
  loadDashboard();
}

return {
  init,
  switchPage, loadDashboard, loadActivities, filterActivities, goPage,
  loadBuildings, filterBuildings, exportBuildingCSV,
  loadDevices, openDevModal, closeDevModal, saveDevice, returnDevice,
  openTgtModal, closeTgtModal, saveTarget, loadTargets,
  loadAdminReminders, filterReminders, doneReminder,
  openActModal, closeActModal, saveActivity, deleteActivity, updateTypeOptions,
};
})();

document.addEventListener('DOMContentLoaded', SA2.init);
