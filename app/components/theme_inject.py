"""app/components/theme_inject.py
共用主題注入工具，安全地在 server 端替換 HTML 的主題相關標記
"""
from fastapi import Request

VALID_THEMES = {"default", "navy", "purple", "crimson", "slate", "amber"}


def apply_theme(html: str, request: Request) -> str:
    """從 cookie 讀取主題，注入 data-theme 和主題 CSS link"""
    theme = request.cookies.get("xn_theme", "default")
    if not theme or theme not in VALID_THEMES or theme == "default":
        return html
    # 加 data-theme 到 <html> tag
    html = html.replace(
        '<html lang="zh-Hant">',
        f'<html lang="zh-Hant" data-theme="{theme}">',
        1
    )
    # 在 web_title_unified.css link 後插入主題 CSS
    for ver in ["xn_v2", "xn_v1", "cl_header_v1"]:
        marker = f'href="/static/web_title_unified.css?v={ver}">'
        if marker in html:
            theme_css = f'<link rel="stylesheet" href="/static/themes/{theme}/theme.css?v=xn_v3">'
            html = html.replace(marker, marker + f'\n  {theme_css}', 1)
            break
    return html
