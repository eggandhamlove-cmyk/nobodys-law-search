from pathlib import Path
import re

p = Path('index.html')
s = p.read_text(encoding='utf-8')

# Social preview for the public overview page (X / Open Graph).
# Use the explicit index.html URL so X treats it separately from the cached root URL.
SOCIAL_URL = 'https://nobodyslaw.github.io/nobodys-law-search/index.html'
SOCIAL_IMAGE = 'https://nobodyslaw.github.io/nobodys-law-search/IMG_1376_x.png'
SOCIAL_META = f'''<meta name="description" content="Nobody's Law 企画概要・世界観まとめ">
<meta property="og:type" content="website">
<meta property="og:title" content="Nobody's Law">
<meta property="og:description" content="Nobody's Law 企画概要・世界観まとめ">
<meta property="og:url" content="{SOCIAL_URL}">
<meta property="og:image" content="{SOCIAL_IMAGE}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="Nobody's Law">
<meta name="twitter:description" content="Nobody's Law 企画概要・世界観まとめ">
<meta name="twitter:image" content="{SOCIAL_IMAGE}">
'''
s = re.sub(r'<meta name="description" content="Nobody\'s Law 企画概要・世界観まとめ">.*?<meta name="twitter:image"[^>]*>\s*', '', s, count=1, flags=re.S)
s = re.sub(r'<link rel="canonical" href="https://nobodyslaw\.github\.io/nobodys-law-search/[^\"]*">\s*', '', s, count=1)
s = s.replace('</head>', SOCIAL_META + '</head>', 1)

s = re.sub(
    r'<aside([^>]*)>\s*概要まとめになります.(?:\s*<p[^>]*>.*?</p>)?\s*</aside>',
    r'<aside\1>概要まとめになります。<br><br>順次更新予定です。<br>更新作業に伴い、<strong>予告なく一時的に公開を停止する</strong>場合がございます。<br>あらかじめご了承ください。</aside>',
    s, count=1, flags=re.S,
)

QA_URL = 'qa.html'
QA_IMAGE = '582_20260823202440.png'
qa_img = Path(QA_IMAGE)
if qa_img.exists():
    qa_html = ('<div class="qa-section">'
        '<blockquote class="qa-link"><strong>Q＆Aはこちら</strong></blockquote>'
        f'<div class="qa-wrap"><a class="qa-banner" href="{QA_URL}">'
        f'<img src="{QA_IMAGE}" alt="Nobody\'s Law Q&A"></a>'
        '<div class="qa-caption">画像をクリック/タップでQ＆Aとお題箱に飛びます</div>'
        '</div></div>')
else:
    qa_html = f'<blockquote class="qa-link"><strong><a href="{QA_URL}">Q＆Aはこちら</a></strong></blockquote>'
s = re.sub(r'<blockquote[^>]*>\s*<strong>(?:<a[^>]*>)?Q＆Aはこちら(?:</a>)?</strong>\s*</blockquote>', qa_html, s, count=1, flags=re.S)

toc_pattern = re.compile(r'<nav[^>]*class="toc"[^>]*><b>目次</b><div class="toc-items">.*?</div></nav>', re.S)
tocs = list(toc_pattern.finditer(s))
if len(tocs) > 1:
    for m in reversed(tocs[1:]): s = s[:m.start()] + s[m.end():]

def toggles_from_markers(inner, labels):
    alt = '|'.join(re.escape(x) for x in labels)
    marker = re.compile(r'<p(?P<attrs>[^>]*)>\s*(?:<strong>)?(?P<label>' + alt + r')(?:</strong>)?\s*</p>', re.S)
    found = list(marker.finditer(inner))
    if not found: return inner, 0
    out = [inner[:found[0].start()]]
    for idx, m in enumerate(found):
        end = found[idx + 1].start() if idx + 1 < len(found) else len(inner)
        content = re.sub(r'^\s*<hr[^>]*>', '', inner[m.end():end], count=1)
        id_match = re.search(r'\bid="([^"]+)"', m.group('attrs'))
        id_attr = f' id="{id_match.group(1)}"' if id_match else ''
        out.append(f'<details{id_attr} class="toggle item-toggle"><summary><strong>{m.group("label")}</strong></summary><div class="toggle-body">{content}</div></details>')
    return ''.join(out), len(found)

char_pat = re.compile(r'(<h3[^>]*>キャラクター作成詳細</h3>)(.*?)(?=<h3[^>]*>エリア詳細</h3>)', re.S)
char_count = 0
def char_repl(m):
    global char_count
    inner = re.sub(r'^\s*<hr[^>]*>', '', m.group(2), count=1)
    rebuilt, n = toggles_from_markers(inner, ['共通作成ルール', 'マフィア', '警察', '教会', '看守', '囚人'])
    char_count = n
    return m.group(1) + '<hr>' + rebuilt
s = char_pat.sub(char_repl, s, count=1)

area_pat = re.compile(r'(<h3[^>]*>エリア詳細</h3>)(.*?)(?=<h3[^>]*>NPCファミリー</h3>)', re.S)
area_count = 0
def area_repl(m):
    global area_count
    inner = re.sub(r'^\s*<hr[^>]*>', '', m.group(2), count=1)
    rebuilt, n = toggles_from_markers(inner, ['Newvail -ニューヴェール-', 'Polcano -ポルカーノ-', 'Vesper -ヴェスパー-', '桜月 -おうげつ-', '鬼籠 -グイロン-', 'Zastoy -ザストイ-'])
    area_count = n
    return m.group(1) + '<hr>' + rebuilt
s = area_pat.sub(area_repl, s, count=1)

s = re.sub(r'<blockquote(?P<attrs>[^>]*)>(?P<quote>.*?)</blockquote>\s*<p(?P<pattrs>[^>]*)>(?P<body>.*?)</p>', r'<div class="quote-group"><blockquote\g<attrs>>\g<quote></blockquote><p\g<pattrs>>\g<body></p></div>', s, flags=re.S)

def vertical_cs_tags(m):
    content = m.group(1).replace('\r\n', '\n').replace('\r', '\n')
    content = re.sub(r'\n+', '<br>', content)
    return '<p class="cs-tags">' + content + '</p>'
s = re.sub(r'<p[^>]*>(︎✦︎<strong>CS必須</strong>.*?)</p>', vertical_cs_tags, s, count=1, flags=re.S)

s = re.sub(r'<style id="nbl-postprocess-style">.*?</style>', '', s, flags=re.S)
extra_css = '''<style id="nbl-postprocess-style">
main p,.toggle-body p{margin:0 0 14px;line-height:1.75;white-space:pre-line}main li,.toggle-body li{white-space:pre-line}main p+p,.toggle-body p+p{margin-top:8px}main h2{margin-top:2.1em;margin-bottom:.75em}main h3{margin-top:1.8em;margin-bottom:.65em}main hr{margin:22px 0}.toggle-body{padding-top:12px;padding-bottom:8px}.toggle-body ul,.toggle-body ol{margin-top:8px;margin-bottom:14px}.toggle-body li{margin:6px 0;line-height:1.7}
.quote-group{margin:18px 0 22px;padding-left:0;border-left:0}.quote-group blockquote{margin:0;padding:0 0 0 16px;border-left:4px solid #ff3f8e;white-space:pre-line}.quote-group p{margin:8px 0 0;padding:0;line-height:1.75;white-space:pre-line}.cs-tags{line-height:1.9;margin-top:8px!important;margin-bottom:18px!important;white-space:normal!important}
.qa-section{width:100%;max-width:760px;margin:18px 0 24px}.qa-section .qa-link{margin-left:0;margin-right:0}.qa-wrap{width:100%;max-width:760px;margin:18px 0 24px}.qa-banner{display:block;width:100%;margin:0;text-decoration:none;line-height:0;border-radius:8px;overflow:hidden}.qa-banner img{display:block!important;width:100%!important;height:auto!important;max-width:none!important;max-height:none!important;object-fit:contain!important;margin:0!important;padding:0!important}.qa-caption{margin-top:7px;text-align:center;font-size:13px;color:#777;line-height:1.5}
.toc .lv4{padding-left:36px;font-size:.94em;color:#666}
/* Mafia subsection headings: keep Family creation and Uniform aligned as siblings. */
.item-toggle> .toggle-body h4,.item-toggle> .toggle-body .h4{margin-left:0!important;padding-left:0!important}.item-toggle> .toggle-body blockquote{margin-left:0}.item-toggle> .toggle-body>p,.item-toggle> .toggle-body>div{max-width:100%}
</style>'''
s = s.replace('</head>', extra_css + '</head>', 1)

toc_script = '''<script id="nbl-overview-toc-fix">
window.addEventListener('DOMContentLoaded',()=>{
  const toc=document.querySelector('.toc .toc-items'); if(!toc)return; toc.innerHTML='';
  const main=document.querySelector('main');
  const items=[...main.querySelectorAll('h2,h3,.heading-toggle .h2,.heading-toggle .h3,.item-toggle>summary')]; let seq=0;
  items.forEach(el=>{const isItem=el.matches('.item-toggle>summary'); const target=isItem?el.parentElement:(el.closest('details')||el); if(!target.id)target.id='overview-toc-'+seq; seq++; const a=document.createElement('a'); a.href='#'+target.id; a.textContent=el.textContent.trim(); a.className=isItem?'lv4':(el.matches('h3,.h3')?'lv3':'lv2'); a.addEventListener('click',()=>{for(let d=target.closest('details');d;d=d.parentElement.closest('details'))d.open=true;if(target.matches('details'))target.open=true;}); toc.appendChild(a);});
});
</script>'''
s = s.replace('</body>', toc_script + '</body>', 1)

p.write_text(s, encoding='utf-8')
print(f'Patched Q&A image={qa_img.exists()}; character toggles={char_count}; area toggles={area_count}')
