from pathlib import Path
import re

p = Path('index.html')
s = p.read_text(encoding='utf-8')

# postprocess.py can close .toggle-body before the Mafia "制服" quote-group.
# Move that quote-group back inside the same Mafia toggle-body so it aligns
# with "ファミリーの作成に関して" instead of shifting to the left.
pattern = re.compile(
    r'(?P<family><blockquote[^>]*><strong>ファミリーの作成に関して</strong></blockquote>'
    r'\s*<p[^>]*>.*?</p>)'
    r'</div>'
    r'(?P<uniform><div class="quote-group">\s*<blockquote[^>]*><strong>制服</strong></blockquote>'
    r'\s*<p[^>]*>.*?</p>\s*</div>)'
    r'</div></details>',
    re.S,
)

s, n = pattern.subn(r'\g<family>\g<uniform></div></details>', s, count=1)

p.write_text(s, encoding='utf-8')
print(f'Fixed Mafia subsection nesting: {n}')
