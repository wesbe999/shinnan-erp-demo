/* 訊南業務系統 v2 JS */
const SV2 = (function(){
const todayStr = () => new Date().toISOString().slice(0,10);
const today = new Date(); today.setHours(0,0,0,0);
function esc(s){return String(s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');}
function isOverdue(d){if(!d)return false;const dt=new Date(d);dt.setHours(0,0,0,0);return dt<today;}
function isToday(d){if(!d)return false;const dt=new Date(d);dt.setHours(0,0,0,0);return dt.getTime()===today.getTime();}
function diffDays(d){if(!d)return null;const dt=new Date(d);dt.setHours(0,0,0,0);return Math.ceil((dt-today)/86400000);}

function contractPill(c){
  if(!c||c==='-')return '<span class="pill pill-gray">-</span>';
  if(c==='簽約')return '<span class="pill pill-green">'+esc(c)+'</span>';
  if(c==='議約中')return '<span class="pill pill-orange">'+esc(c)+'</span>';
  if(c==='待續約')return '<span class="pill pill-red">'+esc(c)+'</span>';
  if(c==='已流失')return '<span class="pill pill-gray">'+esc(c)+'</span>';
  return '<span class="pill pill-blue">'+esc(c)+'</span>';
}

function activityDot(cat){
  const m={
    '業務推廣':'#365ee8','客戶服務':'#16a34a','財務回饋':'#f97316',
    '關係維護':'#7c3aed','其他':'#64748b'
  };
  const icons={'業務推廣':'📢','客戶服務':'🔧','財務回饋':'💰','關係維護':'🤝','其他':'📋'};
  const bg=m[cat]||'#64748b';
  const ic=icons[cat]||'📋';
  return `<div class="sv2-act-dot" style="background:${bg}20">${ic}</div>`;
}

/* ── State ── */
let records=[], memos={}, activities={}, events=[], reminders=[];
let currentFilter='全部', currentBuilding=null, selectedResult='';
let calYear=today.getFullYear(), calMonth=today.getMonth();

/* ── API helpers ── */
async function api(url, opts={}){
  const r = await fetch(url, {credentials:'same-origin', cache:'no-store', ...opts});
  return r.json();
}

/* ── Load data ── */
async function loadRecords(){
  const el = document.getElementById('sv2-card-list');
  if(el) el.innerHTML = '<div class="sv2-empty">載入中...</div>';
  try{
    const d = await api('/api/app/sales/business-records?ts='+Date.now());
    records = Array.isArray(d) ? d : (d.items||d.records||[]);
    renderStats(); renderCards();
  }catch(e){
    if(el) el.innerHTML='<div class="sv2-empty">載入失敗：'+esc(String(e))+'</div>';
  }
}

async function loadBuildingDetail(no){
  try{
    const d = await api('/api/v2/sales/buildings/'+encodeURIComponent(no));
    if(d.ok && d.data) return d.data;
  }catch(e){}
  return null;
}

async function loadReminders(){
  try{
    const d = await api('/api/v2/sales/reminders?days=60');
    reminders = d.ok ? (d.data||[]) : [];
    renderRemindersTab();
  }catch(e){}
}

async function loadEvents(){
  try{
    const y=calYear, m=calMonth+1;
    const d = await api('/api/v2/sales/events?year='+y+'&month='+m);
    events = d.ok ? (d.data||[]) : [];
    renderCalendar();
  }catch(e){}
}

/* ── Stats ── */
function renderStats(){
  const od = records.filter(r=>isOverdue(r.next_visit)).length;
  const td = records.filter(r=>isToday(r.next_visit)).length;
  const el_od = document.getElementById('sv2-s-overdue');
  const el_td = document.getElementById('sv2-s-today');
  const el_tt = document.getElementById('sv2-s-total');
  if(el_od) el_od.textContent = od;
  if(el_td) el_td.textContent = td;
  if(el_tt) el_tt.textContent = records.length;
}

/* ── Filter ── */
function getFiltered(){
  const kw = (document.getElementById('sv2-kw')||{}).value||'';
  return records.filter(r=>{
    if(kw){
      const h=[r.building_name,r.area,r.manager_name,r.manager_phone,r.owner,
               r.business_type,r.status,r.contract_status].join(' ').toLowerCase();
      if(!h.includes(kw.toLowerCase())) return false;
    }
    if(currentFilter==='逾期') return isOverdue(r.next_visit);
    if(currentFilter==='今日') return isToday(r.next_visit);
    if(currentFilter==='重要') return r.important_schedule;
    if(currentFilter==='待拜訪') return r.next_visit && !isOverdue(r.next_visit) && !isToday(r.next_visit);
    if(currentFilter==='合約') return r.contract_status==='議約中'||r.contract_status==='待續約';
    if(currentFilter==='事件') return r.event_type && r.event_status !== '已完成';
    return true;
  }).sort((a,b)=>{
    if(a.important_schedule&&!b.important_schedule) return -1;
    if(!a.important_schedule&&b.important_schedule) return 1;
    if(isOverdue(a.next_visit)&&!isOverdue(b.next_visit)) return -1;
    if(!isOverdue(a.next_visit)&&isOverdue(b.next_visit)) return 1;
    return (a.next_visit||'9999').localeCompare(b.next_visit||'9999');
  });
}

/* ── Render cards ── */
function renderCards(){
  const rows = getFiltered();
  const lbl = document.getElementById('sv2-list-label');
  const list = document.getElementById('sv2-card-list');
  if(lbl) lbl.textContent = currentFilter+'業務工作｜'+rows.length+' 筆';
  if(!list) return;
  if(!rows.length){list.innerHTML='<div class="sv2-empty">目前沒有符合條件的業務工作</div>';return;}
  list.innerHTML = rows.map(r=>{
    const od = isOverdue(r.next_visit);
    const cls = (r.important_schedule?'important ':'')+(od?'overdue':'');
    const vClass = od?'red':isToday(r.next_visit)?'orange':'';
    const memo = r.business_note||'';
    return `<div class="sv2-card ${cls}" onclick="SV2.openDetail(${JSON.stringify(r.building_no)}, ${r.id||0})">
      <div class="sv2-card-top">
        <div>
          <div class="sv2-bname">${esc(r.building_name||'-')}</div>
          <div class="sv2-meta">${esc(r.area||'-')} · 負責：${esc(r.owner||'-')}</div>
        </div>
        ${contractPill(r.contract_status)}
      </div>
      <div class="sv2-info-grid">
        <div class="sv2-info">
          <div class="sv2-info-l">總幹事</div>
          <div class="sv2-info-v">${esc(r.manager_name||'-')}</div>
        </div>
        <div class="sv2-info">
          <div class="sv2-info-l">下次拜訪</div>
          <div class="sv2-info-v ${vClass}">${esc(r.next_visit||'-')}${od?' ⚠':''}</div>
        </div>
        <div class="sv2-info">
          <div class="sv2-info-l">狀態</div>
          <div class="sv2-info-v">${esc(r.status||'-')}</div>
        </div>
        <div class="sv2-info">
          <div class="sv2-info-l">業務行為</div>
          <div class="sv2-info-v">${esc(r.event_type||'-')} · ${esc(r.event_status||'-')}</div>
        </div>
      </div>
      ${memo?'<div class="sv2-memo-preview">📝 '+esc(memo)+'</div>':''}
    </div>`;
  }).join('');
}

/* ── Today Tab ── */
function renderTodayTab(){
  const todays = records.filter(r=>isToday(r.next_visit));
  const overdues = records.filter(r=>isOverdue(r.next_visit));
  const el_t = document.getElementById('sv2-today-list');
  const el_o = document.getElementById('sv2-overdue-list');
  if(el_t) el_t.innerHTML = todays.length ? todays.map(r=>`
    <div class="sv2-sched-card" onclick="SV2.openDetail(${JSON.stringify(r.building_no)}, ${r.id||0})">
      <div class="sv2-sched-time"><div class="th">${r.visit_time?r.visit_time.split('-')[0]:'今日'}</div><div class="td">拜訪</div></div>
      <div class="sv2-sched-body">
        <div class="tn">${esc(r.building_name)}</div>
        <div class="tm">${esc(r.area)} · ${esc(r.owner)} · ${esc(r.business_type||'')}</div>
      </div>
    </div>`).join('') : '<div class="sv2-empty">今日無排定拜訪 ✅</div>';
  if(el_o) el_o.innerHTML = overdues.length ? overdues.map(r=>`
    <div class="sv2-sched-card overdue" onclick="SV2.openDetail(${JSON.stringify(r.building_no)}, ${r.id||0})">
      <div class="sv2-sched-time red"><div class="th">${esc(r.next_visit||'?')}</div><div class="td">逾期</div></div>
      <div class="sv2-sched-body">
        <div class="tn">${esc(r.building_name)}</div>
        <div class="tm">${esc(r.area)} · ${contractPill(r.contract_status)}</div>
      </div>
    </div>`).join('') : '<div class="sv2-empty">無逾期拜訪 ✅</div>';
}

/* ── Important Tab ── */
function renderImportantTab(){
  const imps = records.filter(r=>r.important_schedule);
  const contracts = records.filter(r=>r.contract_status==='議約中'||r.contract_status==='待續約');
  const el_i = document.getElementById('sv2-imp-list');
  const el_c = document.getElementById('sv2-contract-list');
  if(el_i) el_i.innerHTML = imps.length ? imps.map(r=>`
    <div class="sv2-imp-card" onclick="SV2.openDetail(${JSON.stringify(r.building_no)}, ${r.id||0})">
      <div class="sv2-imp-title">⭐ ${esc(r.building_name)}</div>
      <div class="sv2-imp-meta">${esc(r.area)} · 下次拜訪：${esc(r.next_visit||'-')}</div>
      <div class="sv2-imp-date ${isOverdue(r.next_visit)?'red':'orange'}">${isOverdue(r.next_visit)?'⚠ 已逾期':'📍 待拜訪'}</div>
    </div>`).join('') : '<div class="sv2-empty">無重要事項</div>';
  if(el_c) el_c.innerHTML = contracts.length ? contracts.map(r=>`
    <div class="sv2-sched-card" onclick="SV2.openDetail(${JSON.stringify(r.building_no)}, ${r.id||0})">
      <div class="sv2-sched-time ${r.contract_status==='待續約'?'red':'orange'}">
        <div class="th">${esc(r.contract_status)}</div>
      </div>
      <div class="sv2-sched-body">
        <div class="tn">${esc(r.building_name)}</div>
        <div class="tm">${esc(r.area)} · ${esc(r.owner)}</div>
      </div>
    </div>`).join('') : '<div class="sv2-empty">無合約追蹤項目</div>';
}

/* ── Reminders Tab ── */
function renderRemindersTab(){
  const el = document.getElementById('sv2-reminder-list');
  if(!el) return;
  if(!reminders.length){el.innerHTML='<div class="sv2-empty">目前無待處理提醒</div>';return;}
  const urgent = reminders.filter(r=>diffDays(r.remind_date)<=7);
  const warn   = reminders.filter(r=>{const d=diffDays(r.remind_date);return d>7&&d<=30;});
  let html = '';
  if(urgent.length){
    html += `<div class="sv2-section-title" style="color:var(--red)">🚨 緊急（7天內）</div>`;
    html += urgent.map(r=>`
      <div class="sv2-imp-card danger" onclick="SV2.openDetail(${JSON.stringify(r.building_no)}, 0)">
        <div class="sv2-imp-title">${esc(r.reminder_type)} · ${esc(r.building_name||r.building_no)}</div>
        <div class="sv2-imp-meta">${esc(r.area||'')} · ${esc(r.note||'')}</div>
        <div class="sv2-imp-date red">⚠ ${esc(r.remind_date)}（剩 ${diffDays(r.remind_date)} 天）</div>
      </div>`).join('');
  }
  if(warn.length){
    html += `<div class="sv2-section-title" style="color:var(--orange);margin-top:12px">⚠️ 注意（30天內）</div>`;
    html += warn.map(r=>`
      <div class="sv2-imp-card" onclick="SV2.openDetail(${JSON.stringify(r.building_no)}, 0)">
        <div class="sv2-imp-title">${esc(r.reminder_type)} · ${esc(r.building_name||r.building_no)}</div>
        <div class="sv2-imp-meta">${esc(r.note||'')}</div>
        <div class="sv2-imp-date orange">📋 ${esc(r.remind_date)}（剩 ${diffDays(r.remind_date)} 天）</div>
      </div>`).join('');
  }
  el.innerHTML = html||'<div class="sv2-empty">近期無提醒</div>';
}

/* ── Calendar ── */
function renderCalendar(){
  const titleEl = document.getElementById('sv2-cal-title');
  const gridEl  = document.getElementById('sv2-cal-grid');
  if(!gridEl) return;
  if(titleEl) titleEl.textContent = calYear+'年'+(calMonth+1)+'月';
  const first = new Date(calYear, calMonth, 1);
  const last  = new Date(calYear, calMonth+1, 0);
  const evtDates = {};
  events.forEach(e=>{
    const k = e.event_date;
    if(!evtDates[k]) evtDates[k]=[];
    evtDates[k].push(e);
  });
  let html = '';
  for(let i=0;i<first.getDay();i++) html+='<div></div>';
  const tStr = todayStr();
  for(let d=1;d<=last.getDate();d++){
    const ds = calYear+'-'+String(calMonth+1).padStart(2,'0')+'-'+String(d).padStart(2,'0');
    const isT = ds===tStr;
    const evts = evtDates[ds]||[];
    html+=`<div class="sv2-cal-day${isT?' today':''}" onclick="SV2.showCalDay('${ds}')">
      ${d}
      ${evts.length?'<div class="sv2-cal-dot" style="background:'+( evts.some(e=>e.event_type.includes('合約'))?'var(--red)':'var(--green)')+'"></div>':''}
    </div>`;
  }
  gridEl.innerHTML = html;
}

function showCalDay(ds){
  const evtDates = {};
  events.forEach(e=>{if(!evtDates[e.event_date])evtDates[e.event_date]=[];evtDates[e.event_date].push(e);});
  const evts = evtDates[ds]||[];
  const el = document.getElementById('sv2-cal-events');
  if(!el) return;
  el.innerHTML = evts.length
    ? '<div style="font-size:12px;font-weight:1000;color:var(--muted);margin-bottom:6px;">'+esc(ds)+'</div>'
      + evts.map(e=>`<div style="background:var(--card);border:1px solid var(--line);border-radius:10px;padding:8px 10px;margin-bottom:6px;font-size:13px;font-weight:1000;">${esc(e.event_type)} · ${esc(e.building_name||e.building_no)} · ${esc(e.event_time||'')}</div>`).join('')
    : '<div style="font-size:12px;color:var(--muted);padding:8px 0">無活動</div>';
}

function changeMonth(d){
  calMonth+=d;
  if(calMonth>11){calMonth=0;calYear++;}
  if(calMonth<0){calMonth=11;calYear--;}
  loadEvents();
}

/* ── Detail Page ── */
async function openDetail(building_no, sales_id){
  const detEl = document.getElementById('sv2-detail');
  if(!detEl) return;
  detEl.classList.add('open');
  document.getElementById('sv2-det-title').textContent = '載入中...';
  document.getElementById('sv2-det-body-info').innerHTML = '<div class="sv2-empty">載入中...</div>';
  switchDetTab('info', document.querySelector('.sv2-det-tab'));
  selectedResult = '';
  document.querySelectorAll('.sv2-qr').forEach(q=>q.classList.remove('sel'));

  const data = await loadBuildingDetail(building_no);
  if(!data){
    document.getElementById('sv2-det-title').textContent = '載入失敗';
    return;
  }
  currentBuilding = data;
  document.getElementById('sv2-det-title').textContent = data.name||building_no;
  document.getElementById('sv2-det-badge').innerHTML = contractPill(data.contract_status||data.s_contract_status||'');

  const od = isOverdue(data.next_visit);
  const phone = data.manager_phone||'';
  const mgrPhone = data.management_phone||'';

  // ── 資料頁 ──
  let infoHtml = '';
  if(phone||mgrPhone){
    infoHtml += '<div class="sv2-det-section"><div class="sv2-det-sec-title">聯絡資訊</div>';
    if(phone) infoHtml += `<div class="sv2-call-block">
      <div><div class="sv2-call-name">總幹事 · ${esc(data.manager_name||'')}</div><div class="sv2-call-phone">${esc(phone)}</div></div>
      <button class="sv2-call-btn" onclick="location.href='tel:${esc(phone)}'">📞 撥打</button></div>`;
    if(mgrPhone) infoHtml += `<div class="sv2-call-block blue">
      <div><div class="sv2-call-name">管理室</div><div class="sv2-call-phone">${esc(mgrPhone)}</div></div>
      <button class="sv2-call-btn blue" onclick="location.href='tel:${esc(mgrPhone)}'">📞 撥打</button></div>`;
    infoHtml += '</div>';
  }

  infoHtml += `<div class="sv2-det-section"><div class="sv2-det-sec-title">大樓資料</div>
    <div class="sv2-det-row"><span class="sv2-det-label">地址</span><span class="sv2-det-val">${esc(data.address||'-')}</span></div>
    <div class="sv2-det-row"><span class="sv2-det-label">區域</span><span class="sv2-det-val">${esc(data.area||'-')}</span></div>
    <div class="sv2-det-row"><span class="sv2-det-label">管理公司</span><span class="sv2-det-val">${esc(data.management_company||'-')}</span></div>
    <div class="sv2-det-row"><span class="sv2-det-label">拜訪時間</span><span class="sv2-det-val">${esc(data.visit_time||'-')}</span></div>
    <div class="sv2-det-row"><span class="sv2-det-label">委員會</span><span class="sv2-det-val">${esc(data.committee_time||'-')}</span></div>
    <div class="sv2-det-row"><span class="sv2-det-label">住戶大會</span><span class="sv2-det-val">${esc(data.resident_meeting_time||'-')}</span></div>
    <div class="sv2-det-row"><span class="sv2-det-label">用戶數</span><span class="sv2-det-val">${data.active_users||0} / ${data.total_households||0} 戶</span></div>
    <div class="sv2-det-row"><span class="sv2-det-label">滲透率</span><span class="sv2-det-val ${(data.penetration_rate||0)>15?'green':'orange'}">${data.penetration_rate||0}%</span></div>
  </div>`;

  infoHtml += `<div class="sv2-det-section"><div class="sv2-det-sec-title">業務進度</div>
    <div class="sv2-det-row"><span class="sv2-det-label">業務類型</span><span class="sv2-det-val">${esc(data.business_type||'-')}</span></div>
    <div class="sv2-det-row"><span class="sv2-det-label">目前狀態</span><span class="sv2-det-val">${esc(data.status||'-')}</span></div>
    <div class="sv2-det-row"><span class="sv2-det-label">合約狀態</span><span class="sv2-det-val">${contractPill(data.contract_status||'')}</span></div>
    <div class="sv2-det-row"><span class="sv2-det-label">合約到期</span><span class="sv2-det-val ${isOverdue(data.contract_end_date)?'red':''}">${esc(data.contract_end_date||'-')}</span></div>
    <div class="sv2-det-row"><span class="sv2-det-label">下次拜訪</span><span class="sv2-det-val ${od?'red':''}">${esc(data.next_visit||'-')}${od?' (逾期)':''}</span></div>
    <div class="sv2-det-row"><span class="sv2-det-label">事件</span><span class="sv2-det-val">${esc(data.event_type||'-')} · ${esc(data.event_status||'-')}</span></div>
    <div class="sv2-det-row"><span class="sv2-det-label">備註</span><span class="sv2-det-val">${esc(data.business_note||'-')}</span></div>
  </div>`;

  // 競業資訊
  if(data.competitor){
    infoHtml += `<div class="sv2-det-section"><div class="sv2-det-sec-title">競業資訊</div>
      <div class="sv2-det-row"><span class="sv2-det-label">競業業者</span><span class="sv2-det-val">${esc(data.competitor)}</span></div>
      <div class="sv2-det-row"><span class="sv2-det-label">對方報價</span><span class="sv2-det-val">${esc(data.competitor_price||'-')}</span></div>
    </div>`;
  }

  // 帳務狀況
  const bs = data.billing_stats||{};
  if(bs.total){
    infoHtml += `<div class="sv2-det-section"><div class="sv2-det-sec-title">帳務狀況</div>
      <div class="sv2-det-row"><span class="sv2-det-label">有效用戶</span><span class="sv2-det-val">${bs.total||0} 戶</span></div>
      <div class="sv2-det-row"><span class="sv2-det-label">欠費用戶</span><span class="sv2-det-val ${(bs.overdue||0)>0?'red':''}">${bs.overdue||0} 戶</span></div>
      <div class="sv2-det-row"><span class="sv2-det-label">月費收入</span><span class="sv2-det-val green">NT$ ${(bs.monthly_revenue||0).toLocaleString()}</span></div>
    </div>`;
  }

  document.getElementById('sv2-det-body-info').innerHTML = infoHtml;
  document.getElementById('sv2-memo-ta').value = '';

  // ── 拜訪歷史 ──
  const memoList = data.memos||[];
  document.getElementById('sv2-det-body-visit').querySelector('#sv2-memo-hist').innerHTML =
    memoList.length ? memoList.map(m=>`
      <div class="sv2-hist-item">
        <div class="sv2-hist-date">${esc(m.visit_date)} · ${esc(m.owner||'')}</div>
        <div class="sv2-hist-text">${esc(m.content||'')}</div>
        <span class="sv2-hist-result">${esc(m.visit_result||'已拜訪')}</span>
      </div>`).join('')
    : '<div style="font-size:12px;color:var(--muted);padding:4px 0">尚無拜訪紀錄</div>';

  // ── 活動歷史 ──
  const actList = data.activities||[];
  document.getElementById('sv2-act-timeline').innerHTML =
    actList.length ? actList.map(a=>`
      <div class="sv2-act-item">
        ${activityDot(a.activity_category||'其他')}
        <div class="sv2-act-body">
          <div class="sv2-act-type">${esc(a.activity_type)} · ${esc(a.activity_category||'')}</div>
          <div class="sv2-act-meta">${esc(a.activity_date)} · ${esc(a.owner||'')}${a.participants?' · '+a.participants+'人':''}</div>
          ${a.note?'<div class="sv2-act-note">'+esc(a.note)+'</div>':''}
        </div>
      </div>`).join('')
    : '<div class="sv2-empty">尚無活動記錄</div>';

  // ── 統計 ──
  document.getElementById('sv2-det-stats').innerHTML = `
    <div class="sv2-stats-grid">
      <div class="sv2-stats-card"><div class="sn">${data.active_users||0}</div><div class="sl">已簽用戶</div></div>
      <div class="sv2-stats-card"><div class="sn">${data.total_households||0}</div><div class="sl">總戶數</div></div>
      <div class="sv2-stats-card"><div class="sn" style="color:${(data.penetration_rate||0)>15?'var(--green)':'var(--orange)'}">${data.penetration_rate||0}%</div><div class="sl">滲透率</div></div>
      <div class="sv2-stats-card"><div class="sn">${actList.length}</div><div class="sl">活動次數</div></div>
    </div>
    <div class="sv2-det-section">
      <div class="sv2-det-sec-title">拜訪概況</div>
      <div class="sv2-det-row"><span class="sv2-det-label">上次拜訪</span><span class="sv2-det-val">${esc(data.last_visit_date||'-')}</span></div>
      <div class="sv2-det-row"><span class="sv2-det-label">拜訪次數</span><span class="sv2-det-val">${data.visit_count||memoList.length}</span></div>
      <div class="sv2-det-row"><span class="sv2-det-label">上次活動</span><span class="sv2-det-val">${esc(data.last_activity_date||'-')}</span></div>
    </div>
    <div class="sv2-det-section">
      <div class="sv2-det-sec-title">業務標籤</div>
      <div class="sv2-tag-row">
        ${data.business_type?'<span class="sv2-tag">'+esc(data.business_type)+'</span>':''}
        ${data.contract_status?'<span class="sv2-tag">'+esc(data.contract_status)+'</span>':''}
        ${data.important_schedule?'<span class="sv2-tag">⭐ 重要</span>':''}
        ${data.event_type?'<span class="sv2-tag">'+esc(data.event_type)+'</span>':''}
      </div>
    </div>`;
}

function closeDetail(){
  const el = document.getElementById('sv2-detail');
  if(el) el.classList.remove('open');
  currentBuilding = null;
}

function switchDetTab(id, el){
  document.querySelectorAll('.sv2-det-tab').forEach(t=>t.classList.remove('active'));
  document.querySelectorAll('.sv2-det-page').forEach(p=>p.classList.remove('active'));
  if(el) el.classList.add('active');
  const page = document.getElementById('sv2-det-page-'+id);
  if(page) page.classList.add('active');
}

function selQR(el, v){
  selectedResult = v;
  document.querySelectorAll('.sv2-qr').forEach(q=>q.classList.remove('sel'));
  el.classList.add('sel');
}

async function saveMemo(){
  if(!currentBuilding) return;
  const text = (document.getElementById('sv2-memo-ta')||{}).value||'';
  if(!text && !selectedResult){alert('請輸入備忘或選擇拜訪結果');return;}
  const btn = document.getElementById('sv2-save-memo-btn');
  if(btn) btn.disabled = true;
  try{
    const r = await api('/api/v2/sales/memos', {
      method:'POST', headers:{'Content-Type':'application/json'},
      body: JSON.stringify({
        building_no: currentBuilding.building_no,
        sales_record_id: currentBuilding.sales_id||0,
        visit_date: todayStr(),
        visit_result: selectedResult||'已拜訪',
        content: text,
      })
    });
    if(r.ok){
      alert('拜訪記錄已儲存！');
      closeDetail();
      await loadRecords();
    } else {
      alert('儲存失敗：'+(r.error||'未知錯誤'));
    }
  }catch(e){alert('儲存失敗：'+e);}
  if(btn) btn.disabled = false;
}

/* ── Add Activity / Event modal ── */
let addMode = 'activity';

function openAddModal(mode){
  addMode = mode || 'activity';
  const el = document.getElementById('sv2-add-modal');
  if(el) el.classList.add('open');
  const title = document.getElementById('sv2-add-modal-title');
  if(title) title.textContent = mode==='event' ? '新增行程事件' : '新增活動記錄';
  document.querySelectorAll('.sv2-type-btn').forEach(b=>b.classList.remove('sel'));
  const first = document.querySelector('.sv2-type-btn');
  if(first) first.classList.add('sel');
}

function closeAddModal(){
  const el = document.getElementById('sv2-add-modal');
  if(el) el.classList.remove('open');
}

function selType(el){
  document.querySelectorAll('.sv2-type-btn').forEach(b=>b.classList.remove('sel'));
  el.classList.add('sel');
}

async function saveActivity(){
  const building_no = (document.getElementById('sv2-add-building')||{}).value||'';
  const activity_date = (document.getElementById('sv2-add-date')||{}).value||'';
  const type_btn = document.querySelector('.sv2-type-btn.sel');
  const activity_type = type_btn ? type_btn.dataset.type||type_btn.textContent.trim() : '';
  const activity_category = type_btn ? type_btn.dataset.category||'其他' : '其他';
  const note = (document.getElementById('sv2-add-note')||{}).value||'';
  const result = (document.getElementById('sv2-add-result')||{}).value||'';
  const participants = parseInt((document.getElementById('sv2-add-participants')||{}).value||0);
  const new_users = parseInt((document.getElementById('sv2-add-new-users')||{}).value||0);

  if(!building_no||!activity_date||!activity_type){alert('請填寫必要欄位');return;}

  const endpoint = addMode==='event' ? '/api/v2/sales/events' : '/api/v2/sales/activities';
  const body = addMode==='event'
    ? {building_no, event_type:activity_type, event_date:activity_date, note, location:(document.getElementById('sv2-add-location')||{}).value||''}
    : {building_no, activity_category, activity_type, activity_date, note, result, participants, new_users};

  try{
    const r = await api(endpoint, {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(body)});
    if(r.ok){alert('已新增！');closeAddModal();await loadRecords();}
    else{alert('失敗：'+(r.error||''));}
  }catch(e){alert('失敗：'+e);}
}

/* ── Tab switching ── */
function switchTab(id, el){
  document.querySelectorAll('.sv2-tab').forEach(t=>t.classList.remove('active'));
  document.querySelectorAll('.sv2-page').forEach(p=>p.classList.remove('active'));
  if(el) el.classList.add('active');
  const page = document.getElementById('sv2-page-'+id);
  if(page) page.classList.add('active');
  if(id==='today'){renderTodayTab();}
  if(id==='important'){renderImportantTab();}
  if(id==='remind'){loadReminders();}
  if(id==='calendar'){loadEvents();}
}

function setChip(f, el){
  currentFilter = f;
  document.querySelectorAll('.sv2-chip').forEach(c=>c.classList.remove('active'));
  if(el) el.classList.add('active');
  switchTab('list', document.querySelector('.sv2-tab'));
  renderCards();
}

/* ── Init ── */
function init(){
  const todayEl = document.getElementById('sv2-today-str');
  if(todayEl) todayEl.innerHTML = '<strong>'+new Date().toLocaleDateString('zh-TW',{month:'long',day:'numeric',weekday:'short'})+'</strong>';
  loadRecords();
}

return {
  init, loadRecords, setChip, switchTab,
  openDetail, closeDetail, switchDetTab, selQR, saveMemo,
  openAddModal, closeAddModal, selType, saveActivity,
  changeMonth, showCalDay, renderCards,
};
})();

document.addEventListener('DOMContentLoaded', SV2.init);
