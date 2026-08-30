from pathlib import Path
import re

p = Path('index.html')
s = p.read_text(encoding='utf-8')

# Keep every Mafia subsection inside the same .toggle-body.
# Notion content can grow between "ファミリーの作成に関して" and "制服";
# postprocess.py may otherwise close .toggle-body just after the first paragraph,
# which makes later subsection headings shift left and can create odd spacing.
mafia = re.compile(
    r'(?P<start><details[^>]*class="toggle item-toggle"[^>]*>\s*'
    r'<summary><strong>マフィア</strong></summary>\s*'
    r'<div class="toggle-body">)'
    r'(?P<body>.*?)'
    r'(?P<end></details>)(?=\s*<details[^>]*class="toggle item-toggle"[^>]*>\s*<summary><strong>警察</strong>)',
    re.S,
)

fixed = 0

def fix_mafia_block(m):
    global fixed
    body = m.group('body')

    # Remove only the premature toggle-body close that appears after the
    # introductory Family-creation paragraph and before its lists/sections.
    body2, n = re.subn(
        r'(<blockquote[^>]*><strong>ファミリーの作成に関して</strong></blockquote>\s*'
        r'<p[^>]*>.*?</p>)\s*</div>\s*(?=<(?:ul|ol|div class="quote-group"|blockquote))',
        r'\1',
        body,
        count=1,
        flags=re.S,
    )

    # If the previous fixer already left one final outer </div>, keep it;
    # otherwise close the single toggle-body before </details>.
    if not re.search(r'</div>\s*$', body2):
        body2 += '</div>'

    fixed = n
    return m.group('start') + body2 + m.group('end')

s = mafia.sub(fix_mafia_block, s, count=1)

# Normalize character-toggle spacing and make nested Mafia quote headings use
# the same left edge as the rest of the Mafia content.
style = '''<style id="nbl-mafia-layout-fix">
.item-toggle{margin:8px 0!important}
.item-toggle>.toggle-body>.quote-group,
.item-toggle>.toggle-body>blockquote{margin-left:0!important}
.item-toggle>.toggle-body>.quote-group blockquote{margin-left:0!important}
</style>'''
s = re.sub(r'<style id="nbl-mafia-layout-fix">.*?</style>', '', s, flags=re.S)
s = s.replace('</head>', style + '</head>', 1)

p.write_text(s, encoding='utf-8')
print(f'Fixed Mafia subsection nesting: {fixed}')
