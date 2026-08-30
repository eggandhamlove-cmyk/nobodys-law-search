import os
import re
import subprocess
from pathlib import Path

QA_PAGE_ID = os.environ.get(
    "QA_NOTION_PAGE_ID",
    "3c4a36e22f8980ad8aadd30fbefa7920",
)
ODAIBAKO_URL = "https://odaibako.net/u/Nobodys_Law"
ODAIBAKO_IMAGE = "582_20260823202844.png"

# build.py always writes index.html, so keep the public overview page safe,
# build the Q&A into that temporary path, then restore index.html.
index = Path("index.html")
backup = index.read_bytes() if index.exists() else None

env = os.environ.copy()
env["NOTION_PAGE_ID"] = QA_PAGE_ID

try:
    try:
        subprocess.run(["python", "build.py"], check=True, env=env)
    except subprocess.CalledProcessError:
        # Keep the scheduled workflow alive if the Q&A Notion page is moved,
        # deleted, or no longer shared with the integration. The existing
        # qa.html (if any) is left untouched until a valid page ID is supplied.
        print(
            "WARNING: Q&A page could not be fetched from Notion; "
            "keeping the existing qa.html unchanged."
        )
    else:
        html = index.read_text(encoding="utf-8")
        html = html.replace(
            '<aside>ctrl/cmd+F でキーワード検索ができます。ご活用ください。</aside>',
            '',
        )
        odaibako = (
            '<div style="width:100%;max-width:760px;margin:18px 0 24px">'
            f'<a href="{ODAIBAKO_URL}" target="_blank" rel="noopener" '
            'style="display:block;width:100%;margin:0;text-decoration:none;line-height:0;border-radius:8px;overflow:hidden">'
            f'<img src="{ODAIBAKO_IMAGE}" alt="お題箱はこちら" '
            'style="display:block;width:100%;height:auto;max-width:none;max-height:none;object-fit:contain;margin:0;padding:0;border:0">'
            '</a>'
            '</div>'
        )
        html, count = re.subn(
            r'<blockquote>\s*<strong>お題箱はこちら</strong>\s*</blockquote>',
            odaibako,
            html,
            count=1,
        )
        Path("qa.html").write_text(html, encoding="utf-8")
        print(f"Patched Odaibako image={bool(count)}")
        print("Built searchable Q&A page -> qa.html")
finally:
    if backup is None:
        if index.exists():
            index.unlink()
    else:
        index.write_bytes(backup)
