# 訊南 ERP — 開發交接文件
# 建立時間：2026-05-22

## 專案基本資訊

| 項目 | 內容 |
|------|------|
| 專案名稱 | 訊南 ERP（訊南科技派工/帳務/業務管理系統） |
| 本地路徑 | `D:\Shinnan ERP\` |
| 技術棧 | FastAPI + SQLite + 純 HTML/CSS/JS（無前端框架） |
| 本地伺服器 | http://127.0.0.1:8050，啟動：`D:\start_server.bat` |
| 雲端部署 | https://shinnan-erp-demo.onrender.com（Render free plan） |
| GitHub | https://github.com/wesbe999/shinnan-erp-demo.git |
| Python 虛擬環境 | `D:\Shinnan ERP\.venv\` |

---

## 資料庫

| 項目 | 說明 |
|------|------|
| 正式 DB | `D:\Shinnan ERP\xunnan_dispatch.db`（根目錄） |
| render.yaml 設定 | `XUNNAN_DB_PATH: xunnan_dispatch.db` |
| 推送 DB 腳本 | `D:\run_push_db_only.bat`（只 push DB，不動 code） |

---

## 主要路由檔案

| 頁面 | 路徑 | URL |
|------|------|-----|
| 派工系統 | `app/routes/admin_dispatch.py` | `/admin` |
| 帳務系統 | `app/routes/billing.py` | `/admin/billing` |
| 大樓名錄 | `app/routes/buildings_admin.py` | `/admin/buildings` |
| 資料統計 | `app/routes/stats_admin.py` | `/admin/stats` |
| 業務管理 | `app/routes/sales_admin.py` | `/admin/sales` |

---

## 模組化架構（已完成）

### app/components/
- `header.py` — 公版 header（render_header, render_page_head）
- `layout.py` — 公版 layout（render_head, render_body_open, GLOBAL_CSS_VARS, CSS_VERSION）
- `__init__.py` — 統一匯出

### app/static/ 公版 CSS
| 檔案 | 用途 |
|------|------|
| `web_title_unified.css` | header 樣式（四角圓弧 border-radius:18px + 全包金框 + margin:8px） |
| `xn_buttons.css` | 全域按鈕公版（v2，全部金邊實色 #d4af37） |
| `admin_dispatch.css` | 派工頁面專屬 CSS（從 inline 抽出） |
| `billing.css` | 帳務頁面專屬 CSS |
| `billing_notice.css` | 帳務通知面板 + 計算機 CSS |
| `buildings_admin.css` | 大樓名錄專屬 CSS |
| `stats_admin.css` | 統計頁面專屬 CSS |
| `sales_admin.css` | 業務管理專屬 CSS |

---

## Header 按鈕公版規則

所有頁面 header 右上角按鈕順序：**綠(功能) → 橘(次要) → 紫(首頁) → 紅(登出)**

| 顏色 | class/背景 | 用途 |
|------|-----------|------|
| 深綠 `#1a6b3a` | 主要功能按鈕 | 新增、建立、儲存 |
| 深橘 `#b45309` | 次要操作 | 重新整理、開立發票 |
| 深紫 `#6b3fa0` | 導覽首頁 | 🏠 首頁 |
| 深紅 class=`danger` | 登出 | 登出 |

按鈕 inline style 格式：
```
style="background:#1a6b3a !important;border:1.5px solid #d4af37 !important"
```
**注意：「重新整理」按鈕不用 emoji**（Chrome 會渲染成系統圖示），純文字即可。

---

## 按鈕顏色公版（xn_buttons.css）

| class | 背景色 | 用途 |
|-------|-------|------|
| `btn-green` / 無 class | `#0f5132` | 送出、確認、功能 |
| `btn-blue` | `#1a3a6b` | 藍色資訊 |
| `btn-orange` | `#b45309` | 次要操作 |
| `btn-gray` | `#374151` | 清除、取消、關閉 |
| `btn-purple` | `#4c1d95` | 首頁按鈕 |
| `btn-red` / `btn-danger` / `danger` | `#b91c1c` | 刪除、登出 |
| `delete-button` | `#b91c1c` | 資料列刪除 |
| `modal-close` / `building-detail-close` / `customer-detail-close` | `#374151` | 關閉 modal |
| `print-list-button` | `#1a4a8a` | 列印 |
| `detail-switch-button` | `#1a4a8a` | 切換分頁按鈕 |
| `detail-switch-button.active` | `#1a6b3a` | 當前分頁 |
| `billing-notice-send` | `#1a6b3a` | 送出通知 |
| `billing-notice-clear` | `#374151` | 清除通知 |
| `billing-notice-delete` | `#b91c1c` | 刪除通知 |
| `building-detail-save` | `#1a6b3a` | 儲存大樓詳細 |

所有按鈕金邊統一：**`border: 1.5px solid #d4af37 !important`**

---

## Billing 頁面 Tab 按鈕

「建立資料」/ 「開立發票」/ 「客戶清單」三個 tab 按鈕：
- 統一深綠底色 `#10361f`，金邊 1.5px
- active 狀態：`border: 2px solid #d4af37` + `box-shadow: 0 0 0 2px rgba(212,175,55,0.4)`

---

## CSS 版本號

所有 CSS link 使用 `?v=xn_v1`，改樣式後記得更新版本號以清瀏覽器快取。

---

## Git 狀態（2026-05-22）

**本地 14 個 commit 尚未 push 雲端。**

最近 commit 清單：
```
8ddd3df style: header 4-corner rounded + full gold border
4b5102b fix: header 按鈕移除多餘 box-shadow
d4194ed fix: billing.py modal HTML 從 <head> 搬回 <body>
6cdae35 refactor: 5 個頁面 inline CSS 全部抽出成獨立 .css 檔
f15e573 refactor: 建立 layout.py 模組
13bffed chore: 移除根目錄暫存腳本
a833601 chore: 清除 103 個垃圾檔案，釋放 7.8 MB
53ac2dd style: billing tab 按鈕統一顏色
...（共 14 個）
```

Push 指令：
```
cd "D:\Shinnan ERP" && git push
```

---

## 待辦事項（PENDING）

- [ ] Push 全部 14 個 commit 到雲端（GitHub + Render 自動重部署）
- [ ] **Step 5（模組化）**：各頁面 JS 抽出成獨立 `.js` 檔（目前 JS 仍嵌在 .py 裡）
- [ ] hr_admin、engineering_app 等其他頁面按鈕公版化
- [ ] router_mgmt_mobile.py 手機路由管理確認雲端 DB 連線（已 push DB）

---

## 快速啟動

```cmd
D:\start_server.bat
```

登入帳號：S001 / 0000

---

## 重要腳本（D:\ 根目錄）

| 腳本 | 用途 |
|------|------|
| `D:\start_server.bat` | 啟動本地伺服器 |
| `D:\run_push_db_only.bat` | 只 push DB 到雲端 |
| `D:\run_syntax2.bat` | 語法驗證 5 個主要路由 |
| `D:\check_syntax2.py` | 語法驗證腳本 |

---

## 伺服器 PID

目前運行中 PID：**40048**（`uvicorn app.main:app`）
