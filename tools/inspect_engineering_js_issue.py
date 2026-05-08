from pathlib import Path
import re
import shutil
import subprocess
import sys

root = Path(r"D:\Shinnan ERP")
py_path = root / "app" / "routes" / "engineering_app.py"
out_dir = root / "tools" / "_debug_engineering_js"
out_dir.mkdir(parents=True, exist_ok=True)

text = py_path.read_text(encoding="utf-8")

html_blocks = []
for m in re.finditer(r'html\s*=\s*"""(.*?)"""', text, flags=re.S):
    html_blocks.append(m.group(1))

if not html_blocks:
    print("ERROR: 找不到 html = triple quote 區塊")
    sys.exit(1)

print(f"found_html_blocks = {len(html_blocks)}")

node = shutil.which("node")
if not node:
    print("ERROR: 找不到 node.exe，請先安裝 Node.js，或把下面輸出的 script 檔案貼回來。")

for idx, html in enumerate(html_blocks, start=1):
    html_file = out_dir / f"engineering_html_block_{idx}.html"
    html_file.write_text(html, encoding="utf-8")

    scripts = re.findall(r"<script[^>]*>(.*?)</script>", html, flags=re.S | re.I)

    print()
    print("=" * 80)
    print(f"HTML_BLOCK_{idx}")
    print(f"html_file = {html_file}")
    print(f"script_count = {len(scripts)}")

    for sidx, js in enumerate(scripts, start=1):
        js_file = out_dir / f"engineering_html_block_{idx}_script_{sidx}.js"
        js_file.write_text(js, encoding="utf-8")

        print()
        print(f"--- script {sidx} ---")
        print(f"js_file = {js_file}")

        if node:
            result = subprocess.run(
                [node, "--check", str(js_file)],
                cwd=str(root),
                text=True,
                capture_output=True,
            )

            if result.returncode == 0:
                print("node_check = OK")
            else:
                print("node_check = FAILED")
                print(result.stderr)

                m = re.search(r":(\d+)\s*\n", result.stderr)
                if not m:
                    m = re.search(r"\((?:.*?):(\d+):(\d+)\)", result.stderr)

                if m:
                    line_no = int(m.group(1))
                    lines = js.splitlines()

                    print()
                    print(f"=== script {sidx} error nearby lines {max(1, line_no-6)}-{min(len(lines), line_no+6)} ===")
                    for n in range(max(1, line_no - 6), min(len(lines), line_no + 6) + 1):
                        pointer = ">>" if n == line_no else "  "
                        print(f"{pointer} {n:5}: {lines[n-1]}")

        # 額外掃描：可能造成 JS Invalid token 的實際斷行字串
        suspicious = []
        lines = js.splitlines()
        for n, line in enumerate(lines, start=1):
            if "alert(" in line or ".join(" in line or "innerHTML" in line or "onclick=" in line:
                suspicious.append((n, line))

        if suspicious:
            print()
            print("=== suspicious lines ===")
            for n, line in suspicious[:80]:
                print(f"{n:5}: {line}")

print()
print("debug_output_dir =", out_dir)
