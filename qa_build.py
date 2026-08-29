import os
import subprocess
from pathlib import Path

QA_PAGE_ID = "3c4a36e22f8980ad8aadd30fbefa7920"

# build.py always writes index.html, so keep the public overview page safe,
# build the Q&A into that temporary path, then restore index.html.
index = Path("index.html")
backup = index.read_bytes() if index.exists() else None

env = os.environ.copy()
env["NOTION_PAGE_ID"] = QA_PAGE_ID

try:
    subprocess.run(["python", "build.py"], check=True, env=env)
    Path("qa.html").write_bytes(index.read_bytes())
finally:
    if backup is None:
        if index.exists():
            index.unlink()
    else:
        index.write_bytes(backup)

print("Built searchable Q&A page -> qa.html")
