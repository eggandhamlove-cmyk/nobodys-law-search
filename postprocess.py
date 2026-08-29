from pathlib import Path
import re

p=Path('index.html')
s=p.read_text(encoding='utf-8')

QA_URL='https://app.notion.com/p/Nobody-s-Law-Q-A-3c4a36e22f8980ad8aadd30fbefa7920'

# Notion sometimes drops the href for page mentions/linked quote text in the API output.
# Force the known Q&A label to remain clickable.
s=re.sub(
    r'<blockquote>\s*<strong>Q＆Aはこちら</strong>\s*</blockquote>',
    f'<blockquote><strong><a href="{QA_URL}" target="_blank" rel="noopener">Q＆Aはこちら</a></strong></blockquote>',
    s,
    count=1,
)

# Notion sometimes returns toggle headings as a normal heading plus following sibling blocks.
# Force the known Character Creation Details section into one collapsible block.
pat=re.compile(r'(<h3>キャラクター作成詳細</h3>)(.*?)(?=<h3>エリア詳細</h3>)', re.S)

def repl(m):
    inner=m.group(2)
    # Keep everything up to the next section inside the toggle.
    inner=re.sub(r'^\s*<hr>','',inner,count=1)
    return '<details class="toggle heading-toggle forced-toggle"><summary><span class="h3">キャラクター作成詳細</span></summary><div class="toggle-body">'+inner+'</div></details>'

s,n=pat.subn(repl,s,count=1)
p.write_text(s,encoding='utf-8')
print('Patched Q&A link and forced character details toggle:', n)
