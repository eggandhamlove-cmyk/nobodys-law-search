from pathlib import Path
import re

p=Path('index.html')
s=p.read_text(encoding='utf-8')

QA_URL='https://app.notion.com/p/Nobody-s-Law-Q-A-3c4a36e22f8980ad8aadd30fbefa7920'

# Keep the Q&A label clickable even when Notion's API omits the href.
s=re.sub(
    r'<blockquote>\s*<strong>(?:<a[^>]*>)?Q＆Aはこちら(?:</a>)?</strong>\s*</blockquote>',
    f'<blockquote><strong><a href="{QA_URL}" target="_blank" rel="noopener">Q＆Aはこちら</a></strong></blockquote>',
    s,
    count=1,
)

# Avoid duplicated TOCs when both a Notion TOC block and the old visual "目次" marker are present.
s=re.sub(r'(<nav class="toc"><b>目次</b><div class="toc-items"></div></nav>)\s*\1', r'\1', s, count=1)


def toggles_from_markers(inner, labels):
    """Turn flat Notion sibling blocks into one collapsible item per known label."""
    alt='|'.join(re.escape(x) for x in labels)
    marker=re.compile(r'<p>\s*(?:<strong>)?(' + alt + r')(?:</strong>)?\s*</p>', re.S)
    found=list(marker.finditer(inner))
    if not found:
        return inner, 0

    prefix=inner[:found[0].start()]
    out=[prefix]
    for idx,m in enumerate(found):
        label=m.group(1)
        end=found[idx+1].start() if idx+1 < len(found) else len(inner)
        content=inner[m.end():end]
        content=re.sub(r'^\s*<hr>','',content,count=1)
        out.append(
            '<details class="toggle item-toggle">'
            f'<summary><strong>{label}</strong></summary>'
            f'<div class="toggle-body">{content}</div>'
            '</details>'
        )
    return ''.join(out), len(found)

# Character creation: keep the section heading visible, and collapse each role separately.
char_pat=re.compile(r'<h3>キャラクター作成詳細</h3>(.*?)(?=<h3>エリア詳細</h3>)', re.S)
char_count=0

def char_repl(m):
    global char_count
    inner=re.sub(r'^\s*<hr>','',m.group(1),count=1)
    rebuilt,n=toggles_from_markers(inner,[
        '共通作成ルール','マフィア','警察','教会','看守','囚人'
    ])
    char_count=n
    return '<h3>キャラクター作成詳細</h3><hr>'+rebuilt

s=char_pat.sub(char_repl,s,count=1)

# Area details: keep the section heading visible, and collapse each area separately.
area_pat=re.compile(r'<h3>エリア詳細</h3>(.*?)(?=<h3>NPCファミリー</h3>)', re.S)
area_count=0

def area_repl(m):
    global area_count
    inner=re.sub(r'^\s*<hr>','',m.group(1),count=1)
    rebuilt,n=toggles_from_markers(inner,[
        'Newvail -ニューヴェール-',
        'Polcano -ポルカーノ-',
        'Vesper -ヴェスパー-',
        '桜月 -おうげつ-',
        '鬼籠 -グイロン-',
        'Zastoy -ザストイ-'
    ])
    area_count=n
    return '<h3>エリア詳細</h3><hr>'+rebuilt

s=area_pat.sub(area_repl,s,count=1)

p.write_text(s,encoding='utf-8')
print(f'Patched Q&A; character toggles={char_count}; area toggles={area_count}')
