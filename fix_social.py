from pathlib import Path
import re

p = Path('index.html')
s = p.read_text(encoding='utf-8')

# Use the exact same minimal social-card structure as qa.html, which X already renders correctly.
url = 'https://nobodyslaw.github.io/nobodys-law-search/'
image = 'https://nobodyslaw.github.io/nobodys-law-search/IMG_1376_x.png'
meta = f'''<meta name="description" content="Nobody's Law">
<meta property="og:type" content="website">
<meta property="og:title" content="Nobody's Law">
<meta property="og:description" content="Nobody's Law">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{image}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="Nobody's Law">
<meta name="twitter:description" content="Nobody's Law">
<meta name="twitter:image" content="{image}">
'''

# Strip the richer overview metadata inserted by postprocess.py.
s = re.sub(r'<link rel="canonical" href="https://nobodyslaw\.github\.io/nobodys-law-search/">\s*', '', s)
s = re.sub(
    r'<meta name="description" content="Nobody\'s Law 企画概要・世界観まとめ">.*?<meta name="twitter:image:alt"[^>]*>\s*',
    '', s, count=1, flags=re.S,
)
# Fallback if the upstream metadata shape changes slightly.
s = re.sub(
    r'<meta name="description" content="Nobody\'s Law 企画概要・世界観まとめ">.*?<meta name="twitter:image"[^>]*>\s*',
    '', s, count=1, flags=re.S,
)
s = s.replace('</head>', meta + '</head>', 1)
p.write_text(s, encoding='utf-8')
print('Overview social metadata matched to Q&A structure')
