# 訊南 RouterBoard 個人機 SSH 連線資訊
# 更新日期：2026-05-21

## 設備資訊
- 型號：RB450Gx4
- 主機名稱：wesbe-rb
- RouterOS：6.49.19 (stable)
- LAN IP：192.168.99.1/23（介面 BR）
- WAN：PPPoE W1（中華電信）
- DDNS：wesbe.duckdns.org

## SSH 連線方式（透過 Desktop Commander + Python paramiko）

```python
import paramiko

HOST = '192.168.99.1'
PORT = 3200        # SSH port
USER = 'wesbe'
PASS = '@Zax129381'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, port=PORT, username=USER, password=PASS, timeout=10)
stdin, stdout, stderr = ssh.exec_command('指令')
print(stdout.read().decode())
ssh.close()
```

執行方式：
C:\Users\wesbe\miniconda3\python.exe "D:\shinnan erp\rb_ssh.py"

## 管理介面
- WebFig：http://192.168.99.1:9000
- Winbox port：10100
- 登入帳號：admin / 密碼：pear

## 帳號清單
| 帳號 | 群組 | 說明 |
|------|------|------|
| admin | admin | 系統預設 |
| admin_sn | full | NMS 回報用，也是 SSH 連線帳號 |
| administrator | full | 本地管理員 |
| aoyama | full | 本地管理員 |
| command | write | 遠端指令專用 |
| hunter_... | full | Hunter Wang |
| rick_cha... | full | Hunter Wang |

## IP Services
| 服務 | Port | 狀態 | 允許來源 |
|------|------|------|----------|
| ssh | 3200 | 開啟 | 192.168.99.0/24 |
| winbox | 10100 | 開啟 | - |
| www | 9000 | 開啟 | - |
| api | 3800 | 關閉 | - |
| ftp | 3100 | 關閉 | - |
| telnet | 3300 | 關閉 | - |
| api-ssl | 3900 | 關閉 | - |

## 防火牆 Input 規則
| # | Comment | Action | Chain | Src Address | Protocol | Dst Port |
|---|---------|--------|-------|------------|----------|----------|
| 0 | SSH-LAN | accept | input | 192.168.99.x | tcp | 25422 |
| 1 | SSH-LAN | accept | input | 192.168.99.x | tcp | 25422 |
| 7 | - | accept | input | - | - | - |
| 8 | - | drop | input | - | - | - |
| 9 | - | jump | input | - | WAN | - |

注意：防火牆規則 0,1 寫的是 25422 但 SSH 服務實際在 3200，
SSH 能連通是因為規則 7 accept 放行了所有 input（LAN 方向）

## WAN 設定
- ETH1（ether1）：DHCP Client，已取得 192.168.1.101
- 上游路由器 Gateway：192.168.1.1

## 注意事項
- 這是測試機，不是正式環境
- SSH 只允許從 192.168.99.0/24 連入
- 您的電腦 IP：192.168.99.5（在允許範圍內）
- Python 執行環境：C:\Users\wesbe\miniconda3\python.exe
- 腳本存放位置：D:\shinnan erp\rb_ssh.py
