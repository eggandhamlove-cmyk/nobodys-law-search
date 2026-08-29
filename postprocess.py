from pathlib import Path
import re

p=Path('index.html')
s=p.read_text(encoding='utf-8')

# Notion sometimes returns toggle headings as a normal heading plus following sibling blocks.
# Force the known Character Creation Details section into one collapsible block.
pat=re.compile(r'(<h3>キャラクター作成詳細</h3>)(.*?)(?=<h3>エリア詳細</h3>)', re.S)

def repl(m):
    inner=m.group(2)
    # remove the divider immediately below the heading so it stays inside the toggle cleanly
    inner=re.sub(r'^\s*<hr>','',inner,count=1)
    return '<details class="toggle heading-toggle forced-toggle"><summary><span class="h3">キャラクター作成詳細</span></summary><div class="toggle-body">'+inner+'</div></details>'

s,n=pat.subn(repl,s,count=1)
p.write_text(s,encoding='utf-8')
print('Forced character details toggle:', n)
