from pathlib import Path
import re

path = Path('index.html')
s = path.read_text(encoding='utf-8')

QA_URL = 'https://app.notion.com/p/Nobody-s-Law-Q-A-3c4a36e22f8980ad8aadd30fbefa7920'

# Turn the Q&A label into an actual link even when the Notion API drops the href.
s = re.sub(
    r'<blockquote>\s*<strong>Q＆Aはこちら</strong>\s*</blockquote>',
    f'<blockquote><strong><a href="{QA_URL}" target="_blank" rel="noopener">Q＆Aはこちら</a></strong></blockquote>',
    s,
    count=1,
)

# Notion currently exposes this toggle-heading's visible children as sibling blocks.
# Force the section from "キャラクター作成詳細" up to "エリア詳細" into one <details>.
pat = re.compile(
    r'<h3>キャラクター作成詳細</h3>(?P<body>.*?)(?=<h3>エリア詳細</h3>)',
    re.S,
)
m = pat.search(s)
if m:
    body = m.group('body')
    wrapped = (
        '<details class="toggle heading-toggle character-details">'
        '<summary><span class="h3">キャラクター作成詳細</span></summary>'
        f'<div class="toggle-body">{body}</div>'
        '</details>'
    )
    s = s[:m.start()] + wrapped + s[m.end():]

path.write_text(s, encoding='utf-8')
print('Patched Q&A link and character-details toggle')
