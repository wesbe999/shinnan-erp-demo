"""
app/components/layout.py
========================
訊南 ERP 公版 Layout 模組

使用方式：
    from app.components.layout import render_head, render_body_open, CSS_VERSION

    html = render_head(title="派工系統", extra_css="<style>...</style>")
    html += render_body_open()
    html += header_html
    html += body_html
    html += "</body></html>"
"""

from __future__ import annotations
import html as _html

# ── 版本號（改這裡讓瀏覽器清快取）──────────────────────────────
CSS_VERSION = "xn_v1"
# ─────────────────────────────────────────────────────────────

# 全域 CSS 變數（各頁面共用）
GLOBAL_CSS_VARS = """
<style id="xn-global-vars">
:root {
  --bg:     #eef3f9;
  --card:   #ffffff;
  --line:   #d7e1ef;
  --text:   #102348;
  --muted:  #64748b;
  --gold:   #d4af37;
  --green:  #1a6b3a;
  --blue:   #1a4a8a;
  --orange: #b45309;
  --purple: #6b3fa0;
  --red:    #b91c1c;
  --gray:   #374151;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  background: var(--bg);
  color: var(--text);
  font-family: "Microsoft JhengHei", "Segoe UI", Arial, sans-serif;
}
.page {
  width: min(1680px, calc(100% - 36px));
  margin: 24px auto 42px;
}
/* card */
.card {
  background: var(--card);
  border: 1px solid var(--line);
  border-radius: 22px;
  padding: 20px;
  box-shadow: 0 6px 18px rgba(15,23,42,.06);
  margin-bottom: 16px;
}
/* pill 狀態標籤 */
.pill {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 999px;
  padding: 0 10px;
  min-width: 64px;
  height: 26px;
  font-size: 12px;
  font-weight: 1000;
  line-height: 1;
  white-space: nowrap;
  border: 1px solid transparent;
}
.pill-wait     { background:#fef3c7; color:#92400e; border-color:#fcd34d; }
.pill-claim    { background:#dbeafe; color:#1d4ed8; border-color:#93c5fd; }
.pill-done     { background:#d1fae5; color:#047857; border-color:#6ee7b7; }
.pill-default  { background:#f1f5f9; color:#334155; border-color:#cbd5e1; }
.pill-green    { background:#dcfce7; color:#166534; border-color:#bbf7d0; }
.pill-red      { background:#fee2e2; color:#b91c1c; border-color:#fca5a5; }
.pill-blue     { background:#dbeafe; color:#1d4ed8; border-color:#93c5fd; }
.pill-orange   { background:#ffedd5; color:#c2410c; border-color:#fed7aa; }
.pill-purple   { background:#ede9fe; color:#5b21b6; border-color:#c4b5fd; }
/* modal 遮罩 */
.modal-mask {
  position: fixed;
  inset: 0;
  z-index: 9000;
  display: none;
  align-items: center;
  justify-content: center;
  background: rgba(15,23,42,.58);
  padding: 24px;
}
.modal-mask.active { display: flex; }
.modal {
  width: min(920px,96vw);
  max-height: 90vh;
  overflow: auto;
  background: #fff;
  border: 1px solid var(--line);
  border-radius: 24px;
  padding: 24px;
  box-shadow: 0 26px 80px rgba(0,0,0,.32);
}
.modal-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 18px;
}
.modal-title   { font-size: 26px; font-weight: 1000; color: var(--text); }
.modal-actions { display: flex; flex-wrap: wrap; justify-content: flex-end; gap: 8px; padding-top: 12px; }
/* form grid */
.form-grid {
  display: grid;
  grid-template-columns: repeat(3,1fr);
  gap: 12px 14px;
}
.field label {
  display: block;
  color: var(--muted);
  font-size: 13px;
  font-weight: 1000;
  margin-bottom: 6px;
}
.field input,
.field select,
.field textarea {
  width: 100%;
  height: 38px;
  border: 1px solid #cbd5e1;
  border-radius: 10px;
  padding: 0 12px;
  font-size: 14px;
  font-family: inherit;
  color: var(--text);
  background: #fff;
  outline: none;
}
.field textarea { height: 78px; resize: vertical; }
.field.full { grid-column: 1 / -1; }
/* table */
.table-wrap {
  border: 1px solid var(--line);
  border-radius: 16px;
  overflow: auto;
  background: #fff;
}
table {
  width: 100%;
  border-collapse: collapse;
  table-layout: fixed;
}
th {
  background: #f8fafc;
  color: #475569;
  font-weight: 1000;
  font-size: 13px;
  text-align: left;
  padding: 8px 10px;
  border-bottom: 1px solid var(--line);
  white-space: nowrap;
}
td {
  padding: 8px 10px;
  font-size: 13px;
  font-weight: 900;
  border-bottom: 1px solid #edf2f7;
  vertical-align: middle;
  color: var(--text);
}
tr:hover td { background: #f8fbff; }
/* hint */
.hint {
  color: var(--muted);
  font-size: 13px;
  font-weight: 900;
  margin-bottom: 12px;
}
/* notice panel */
.notice-panel {
  border: 1px solid #fdba74;
  background: #fff7ed;
  border-radius: 12px;
  padding: 7px 10px;
  margin: 8px 0 12px;
}
.notice-head { display:flex; align-items:center; gap:20px; margin-bottom:5px; }
.notice-title { font-size:14px; font-weight:1000; color:#c2410c; }
.notice-subtitle { font-size:13px; font-weight:800; color:#9a3412; }
.notice-input-row {
  display: grid;
  grid-template-columns: minmax(0,1fr) 52px 52px;
  gap: 7px;
  align-items: center;
  height: 28px;
  border: 1px solid #fdba74;
  border-radius: 8px;
  background: #fff;
  padding: 2px 4px 2px 8px;
}
#notice_input {
  width:100%; height:22px; border:0; outline:0;
  background:transparent; color:var(--text);
  font-size:12px; font-weight:900;
}
.notice-list {
  margin-top:5px; border:1px dashed #fb923c;
  border-radius:8px; background:#fff; overflow:hidden;
}
.notice-row {
  display:grid; grid-template-columns:minmax(0,1fr) 44px;
  align-items:center; gap:6px;
  height:24px; padding:0 6px;
  border-bottom:1px dashed #fdba74;
}
.notice-row:last-child { border-bottom:0; }
.notice-text {
  overflow:hidden; white-space:nowrap; text-overflow:ellipsis;
  color:var(--text); font-size:12px; font-weight:900;
}
</style>
"""


def render_head(
    title: str = "訊南 ERP",
    extra_css: str = "",
    extra_head: str = "",
) -> str:
    """產生 <!doctype html><html><head>...</head> 區段"""
    safe_title = _html.escape(str(title or "訊南 ERP"))
    return f"""<!doctype html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{safe_title}｜中央控管系統</title>
<link rel="stylesheet" href="/static/web_title_unified.css?v={CSS_VERSION}">
<link rel="stylesheet" href="/static/xn_buttons.css?v={CSS_VERSION}">
{GLOBAL_CSS_VARS}
{extra_css}
{extra_head}
</head>
"""


def render_body_open(body_class: str = "") -> str:
    """產生 <body> 開標籤"""
    cls = f' class="{_html.escape(body_class)}"' if body_class else ""
    return f"<body{cls}>\n"
