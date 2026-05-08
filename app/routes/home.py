from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["訊南 ERP 入口首頁"])


@router.get("/", response_class=HTMLResponse, summary="訊南 ERP 系統入口首頁")
def erp_home_page():
    return """
<!doctype html>
<html lang="zh-Hant">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Shinnan ERP｜訊南ERP系統</title>
  <style>
    :root {
      --bg1: #07111f;
      --bg2: #0f2f55;
      --cyan: #38e8ff;
      --blue: #3b82f6;
      --teal: #14b8a6;
      --purple: #8b5cf6;
      --orange: #f97316;
      --green: #22c55e;
      --white: #ffffff;
      --muted: #a8c7e8;
      --glass: rgba(255,255,255,0.10);
      --glass2: rgba(255,255,255,0.16);
    }

    * {
      box-sizing: border-box;
    }

    body {
      margin: 0;
      min-height: 100vh;
      font-family: "Microsoft JhengHei", "Segoe UI", Arial, sans-serif;
      color: var(--white);
      background:
        radial-gradient(circle at 18% 12%, rgba(56,232,255,0.30), transparent 32%),
        radial-gradient(circle at 85% 18%, rgba(139,92,246,0.32), transparent 32%),
        radial-gradient(circle at 50% 92%, rgba(20,184,166,0.22), transparent 35%),
        linear-gradient(135deg, var(--bg1), var(--bg2));
      overflow-x: hidden;
    }

    body::before {
      content: "";
      position: fixed;
      inset: 0;
      pointer-events: none;
      background-image:
        linear-gradient(rgba(255,255,255,0.045) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,0.045) 1px, transparent 1px);
      background-size: 42px 42px;
      mask-image: linear-gradient(to bottom, rgba(0,0,0,0.85), rgba(0,0,0,0.10));
    }

    .page {
      width: min(1180px, calc(100% - 40px));
      margin: 0 auto;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      justify-content: center;
      padding: 54px 0;
      position: relative;
      z-index: 1;
    }

    .hero {
      display: grid;
      grid-template-columns: 1.05fr 0.95fr;
      gap: 36px;
      align-items: center;
    }

    .brand-card {
      padding: 38px;
      border: 1px solid rgba(255,255,255,0.22);
      border-radius: 34px;
      background: linear-gradient(145deg, rgba(255,255,255,0.16), rgba(255,255,255,0.06));
      box-shadow:
        0 26px 80px rgba(0,0,0,0.38),
        inset 0 1px 0 rgba(255,255,255,0.35);
      backdrop-filter: blur(18px);
    }

    .brand-row {
      display: flex;
      align-items: center;
      gap: 22px;
      margin-bottom: 28px;
    }

    .logo {
      width: 96px;
      height: 96px;
      border-radius: 28px;
      position: relative;
      background:
        linear-gradient(135deg, rgba(56,232,255,0.95), rgba(59,130,246,0.95) 48%, rgba(139,92,246,0.96));
      box-shadow:
        0 18px 40px rgba(56,232,255,0.26),
        inset 0 2px 0 rgba(255,255,255,0.42);
      overflow: hidden;
      flex: 0 0 auto;
    }

    .logo::before {
      content: "";
      position: absolute;
      width: 66px;
      height: 66px;
      left: 15px;
      top: 15px;
      border: 8px solid rgba(255,255,255,0.94);
      border-right-color: transparent;
      border-bottom-color: transparent;
      border-radius: 24px;
      transform: rotate(-45deg);
    }

    .logo::after {
      content: "";
      position: absolute;
      width: 20px;
      height: 58px;
      left: 52px;
      top: 19px;
      border-radius: 999px;
      background: rgba(255,255,255,0.95);
      box-shadow: -22px 18px 0 rgba(255,255,255,0.82);
      transform: skewX(-18deg);
    }

    .brand-title {
      line-height: 1.05;
    }

    .zh {
      font-size: 46px;
      font-weight: 1000;
      letter-spacing: 2px;
    }

    .en {
      margin-top: 8px;
      font-size: 22px;
      font-weight: 800;
      letter-spacing: 6px;
      color: var(--cyan);
      text-transform: uppercase;
    }

    .headline {
      font-size: 56px;
      line-height: 1.12;
      font-weight: 1000;
      margin: 22px 0 18px;
      letter-spacing: 1px;
    }

    .headline span {
      color: var(--cyan);
      text-shadow: 0 0 24px rgba(56,232,255,0.45);
    }

    .subtitle {
      color: var(--muted);
      font-size: 20px;
      line-height: 1.8;
      font-weight: 700;
      max-width: 660px;
    }

    .signal-line {
      margin-top: 30px;
      display: flex;
      align-items: center;
      gap: 14px;
      color: #dffbff;
      font-size: 16px;
      font-weight: 900;
      letter-spacing: 1px;
    }

    .pulse {
      width: 12px;
      height: 12px;
      border-radius: 50%;
      background: var(--green);
      box-shadow: 0 0 0 0 rgba(34,197,94,0.9);
      animation: pulse 1.6s infinite;
    }

    @keyframes pulse {
      0% { box-shadow: 0 0 0 0 rgba(34,197,94,0.8); }
      70% { box-shadow: 0 0 0 16px rgba(34,197,94,0); }
      100% { box-shadow: 0 0 0 0 rgba(34,197,94,0); }
    }

    .module-panel {
      padding: 28px;
      border-radius: 34px;
      background: rgba(5,15,31,0.48);
      border: 1px solid rgba(255,255,255,0.18);
      box-shadow:
        0 26px 80px rgba(0,0,0,0.32),
        inset 0 1px 0 rgba(255,255,255,0.16);
      backdrop-filter: blur(16px);
    }

    .panel-title {
      font-size: 25px;
      font-weight: 1000;
      margin: 0 0 18px;
      color: #f8fbff;
    }

    .module-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 16px;
    }

    .module {
      position: relative;
      min-height: 116px;
      padding: 20px;
      border-radius: 24px;
      text-decoration: none;
      color: white;
      overflow: hidden;
      border: 1px solid rgba(255,255,255,0.20);
      background: linear-gradient(135deg, rgba(255,255,255,0.18), rgba(255,255,255,0.07));
      box-shadow:
        0 18px 28px rgba(0,0,0,0.25),
        inset 0 1px 0 rgba(255,255,255,0.25);
      transition: transform .16s ease, box-shadow .16s ease, border-color .16s ease;
    }

    .module:hover {
      transform: translateY(-5px);
      box-shadow:
        0 24px 38px rgba(0,0,0,0.34),
        0 0 30px rgba(56,232,255,0.14),
        inset 0 1px 0 rgba(255,255,255,0.32);
      border-color: rgba(56,232,255,0.55);
    }

    .module::before {
      content: "";
      position: absolute;
      width: 120px;
      height: 120px;
      right: -42px;
      top: -42px;
      border-radius: 50%;
      background: var(--accent);
      opacity: .28;
      filter: blur(1px);
    }

    .module-name {
      position: relative;
      font-size: 24px;
      font-weight: 1000;
      margin-bottom: 10px;
      letter-spacing: 1px;
    }

    .module-desc {
      position: relative;
      color: #cde5ff;
      font-size: 14px;
      line-height: 1.55;
      font-weight: 700;
    }

    .m-dispatch { --accent: #38e8ff; }
    .m-billing { --accent: #f97316; }
    .m-customer { --accent: #22c55e; }
    .m-building { --accent: #8b5cf6; }
    .m-sales { --accent: #facc15; }
    .m-engineer { --accent: #60a5fa; }

    .footer {
      margin-top: 28px;
      color: rgba(220,240,255,0.72);
      font-size: 13px;
      font-weight: 700;
      letter-spacing: 1px;
      text-align: center;
    }

    @media (max-width: 880px) {
      .hero {
        grid-template-columns: 1fr;
      }

      .headline {
        font-size: 42px;
      }

      .zh {
        font-size: 38px;
      }
    }

    @media (max-width: 560px) {
      .page {
        width: min(100% - 24px, 1180px);
        padding: 28px 0;
      }

      .brand-card,
      .module-panel {
        padding: 22px;
        border-radius: 26px;
      }

      .brand-row {
        gap: 14px;
      }

      .logo {
        width: 76px;
        height: 76px;
        border-radius: 22px;
      }

      .logo::before {
        width: 50px;
        height: 50px;
        left: 13px;
        top: 13px;
        border-width: 6px;
      }

      .logo::after {
        width: 16px;
        height: 45px;
        left: 41px;
        top: 16px;
      }

      .zh {
        font-size: 31px;
      }

      .en {
        font-size: 16px;
        letter-spacing: 4px;
      }

      .headline {
        font-size: 34px;
      }

      .subtitle {
        font-size: 17px;
      }

      .module-grid {
        grid-template-columns: 1fr;
      }
    }
  </style>
</head>
<body>
  <main class="page">
    <section class="hero">
      <div class="brand-card">
        <div class="brand-row">
          <div class="logo" aria-label="Shinnan Logo"></div>
          <div class="brand-title">
            <div class="zh">訊南ERP系統</div>
            <div class="en">Shinnan ERP</div>
          </div>
        </div>

        <div class="headline">
          電信營運管理<br>
          <span>一站式中樞</span>
        </div>

        <div class="subtitle">
          整合派工、帳務、客戶、大樓、業務與工程資料，讓現場作業與公司管理能在同一套系統中快速銜接。
        </div>

        <div class="signal-line">
          <span class="pulse"></span>
          <span>SHINNAN TELECOM OPERATION PLATFORM</span>
        </div>
      </div>

      <div class="module-panel">
        <div class="panel-title">請選擇系統入口</div>

        <div class="module-grid">
          <a class="module m-dispatch" href="/admin">
            <div class="module-name">派工系統</div>
            <div class="module-desc">案件建立、工程師指派、手機派工與完工管理。</div>
          </a>

          <a class="module m-billing" href="/admin/billing">
            <div class="module-name">帳務系統</div>
            <div class="module-desc">費用、押金、月租、材料與財務同步管理。</div>
          </a>

          <a class="module m-customer" href="/admin?module=customers">
            <div class="module-name">客戶資料</div>
            <div class="module-desc">住戶、聯絡人、服務地址與裝退機紀錄。</div>
          </a>

          <a class="module m-building" href="/admin/buildings">
            <div class="module-name">大樓資料</div>
            <div class="module-desc">社區大樓、設備 IP、管理公司與住戶數據。</div>
          </a>

          <a class="module m-sales" href="/admin?module=sales">
            <div class="module-name">業務系統</div>
            <div class="module-desc">新戶開發、合約追蹤與社區合作狀態。</div>
          </a>

          <a class="module m-engineer" href="/admin/engineers">
            <div class="module-name">工程系統</div>
            <div class="module-desc">工程師名錄、派工負載與維修支援資料。</div>
          </a>
        </div>
      </div>
    </section>

    <div class="footer">© Shinnan ERP System｜訊南科技內部管理平台</div>
  </main>
</body>
</html>
"""
