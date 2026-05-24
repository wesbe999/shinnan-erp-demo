"""
app/components/header.py
========================
訊南 ERP 公版 Header 模組

使用方式：
    from app.components.header import render_header, render_page_head

    # 在路由中：
    head = render_page_head(title="大樓名錄", extra_css="...")
    header = render_header(
        title="大樓名錄",
        subtitle="中央控管系統",
        buttons=[
            {"label": "返回首頁", "href": "/"},
            {"label": "新增資料", "id": "create_btn", "onclick": "openModal()"},
            {"label": "登出",     "href": "/employee/logout", "style": "danger"},
        ]
    )
    return HTMLResponse(head + "<body>" + header + body_html + "</body></html>")

按鈕 dict 欄位：
    label   : 顯示文字（必填）
    href    : 連結（與 onclick 擇一）
    onclick : JS 事件（與 href 擇一）
    id      : HTML id（可選）
    style   : "default" | "danger" | "primary"（預設 "default"）
    cls     : 額外 class（可選）
"""

from __future__ import annotations
import html as _html
from fastapi import Request

VALID_THEMES = {"default", "navy", "purple", "crimson", "slate", "amber"}

def get_theme(request: Request) -> str:
    t = request.cookies.get("xn_theme", "default")
    return t if t in VALID_THEMES else "default"

# ── 設定區（換圖只需改這裡）──────────────────────────────────
LOGO_MAIN      = "/static/shinnan_logo_gold_transparent.png?v=cl_header_v1"
LOGO_WATERMARK = "/static/shinnan_logo_outline_white.png"
CSS_VERSION    = "cl_header_v1"
# ────────────────────────────────────────────────────────────


def _esc(s: str) -> str:
    return _html.escape(str(s or ""), quote=True)


def render_page_head(
    title: str = "訊南 ERP",
    extra_css: str = "",
    extra_head: str = "",
    theme: str = "default",
) -> str:
    """產生 <html><head>...</head> 區段"""
    theme_link = ""
    if theme and theme != "default":
        theme_link = f'<link rel="stylesheet" href="/static/themes/{theme}/theme.css?v={CSS_VERSION}">'
    data_theme = f' data-theme="{theme}"' if theme and theme != "default" else ""
    return f"""<!doctype html>
<html lang="zh-Hant"{data_theme}>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{_esc(title)}｜訊南 ERP</title>
<link rel="stylesheet" href="/static/web_title_unified.css?v={CSS_VERSION}">
{theme_link}
{extra_css}
{extra_head}
"""


def render_header(
    title: str,
    subtitle: str = "中央控管系統",
    buttons: list[dict] | None = None,
) -> str:
    """
    產生公版 header HTML。

    buttons 範例：
        [
            {"label": "返回首頁", "href": "/"},
            {"label": "新增資料", "onclick": "openModal()", "id": "btn_create"},
            {"label": "登出",     "href": "/employee/logout", "style": "danger"},
        ]
    """
    buttons = buttons or []
    buttons_html = _render_buttons(buttons)

    return f"""<section class="web-title web-title-tech" id="xn-page-header">
  <img class="web-title-watermark" src="{LOGO_WATERMARK}" alt="">
  <div class="web-title-map"></div>
  <div class="web-title-radar"></div>
  <div class="web-title-main">
    <div class="web-title-logo-box">
      <img class="web-title-logo" src="{LOGO_MAIN}" alt="ShinNan Logo">
    </div>
    <div class="web-title-text">
      <h1 class="web-title-system">{_esc(title)}</h1>
      <div class="web-title-sub">
        <span class="web-title-sub-dot"></span>
        {_esc(subtitle)}
        <span class="web-title-sub-dot"></span>
      </div>
    </div>
  </div>
  {buttons_html}
</section>
<style>
/* ── xn-header-actions 公版按鈕區 ── */
#xn-page-header .xn-header-actions {{
  position: absolute;
  right: 38px;
  bottom: 20px;
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 7px;
  z-index: 20;
}}
#xn-page-header .xn-header-btn {{
  height: 28px;
  min-width: 68px;
  padding: 0 12px;
  border-radius: 9px;
  border: 1px solid rgba(224,201,119,.82);
  background: #10361f;
  color: #fff7d6;
  font-size: 12px;
  font-weight: 1000;
  line-height: 1;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  text-decoration: none;
  font-family: inherit;
  transition: .15s;
}}
#xn-page-header .xn-header-btn:hover {{
  background: #174a2a;
  border-color: #ead27b;
}}
#xn-page-header .xn-header-btn.danger {{
  background: #cf3b2f;
  border-color: rgba(244,180,140,.82);
  color: #fff;
}}
#xn-page-header .xn-header-btn.danger:hover {{
  background: #b02a20;
}}
#xn-page-header .xn-header-btn.primary {{
  background: #1a5276;
  border-color: rgba(224,201,119,.82);
  color: #fff;
}}
#xn-page-header .xn-header-btn.primary:hover {{
  background: #154360;
}}
</style>
"""


def _render_buttons(buttons: list[dict]) -> str:
    if not buttons:
        return ""

    items = []
    for btn in buttons:
        label   = _esc(btn.get("label", ""))
        style   = btn.get("style", "default")
        cls     = btn.get("cls", "")
        btn_id  = f'id="{_esc(btn["id"])}"' if btn.get("id") else ""
        style_cls = "" if style == "default" else f" {style}"

        if btn.get("href"):
            href = _esc(btn["href"])
            items.append(
                f'<a {btn_id} href="{href}" '
                f'class="xn-header-btn{style_cls} {cls}">{label}</a>'
            )
        else:
            onclick = btn.get("onclick", "")
            items.append(
                f'<button {btn_id} type="button" onclick="{_esc(onclick)}" '
                f'class="xn-header-btn{style_cls} {cls}">{label}</button>'
            )

    return '<div class="xn-header-actions">' + "\n  ".join(items) + "</div>"
