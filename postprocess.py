from pathlib import Path
import re

p=Path('index.html')
s=p.read_text(encoding='utf-8')

# Restore the full introductory notice if Notion only exposes the first line.
s=s.replace(
    '<aside>概要まとめになります。</aside>',
    '<aside>概要まとめになります。<br><br>順次更新予定です。<br>更新作業に伴い、<strong>予告なく一時的に公開を停止する</strong>場合がございます。<br>あらかじめご了承ください。</aside>',
    1,
)

QA_URL='qa.html'
QA_IMAGE='582_20260823202440.png'
qa_img=Path(QA_IMAGE)
if qa_img.exists():
    qa_html=(f'<div class="qa-section"><blockquote class="qa-link"><strong>Q＆Aはこちら</strong></blockquote>'
             f'<div class="qa-wrap"><a class="qa-banner" href="{QA_URL}">'
             f'<img src="{QA_IMAGE}" alt="Nobody\'s Law Q&A"></a>'
             f'<div class="qa-caption">画像をクリック/タップでQ＆Aとお題箱に飛びます</div></div></div>')
else:
    qa_html=f'<blockquote class="qa-link"><strong><a href="{QA_URL}">Q＆Aはこちら</a></strong></blockquote>'

s=re.sub(r'<blockquote(?: class="qa-link")?>\s*<strong>(?:<a[^>]*>)?Q＆Aはこちら(?:</a>)?</strong>\s*</blockquote>',qa_html,s,count=1)
s=re.sub(r'(<nav class="toc"><b>目次</b><div class="toc-items"></div></nav>)\s*\1',r'\1',s,count=1)

def toggles_from_markers(inner,labels):
    alt='|'.join(re.escape(x) for x in labels); marker=re.compile(r'<p>\s*(?:<strong>)?('+alt+r')(?:</strong>)?\s*</p>',re.S); found=list(marker.finditer(inner))
    if not found:return inner,0
    out=[inner[:found[0].start()]]
    for idx,m in enumerate(found):
        end=found[idx+1].start() if idx+1<len(found) else len(inner); content=re.sub(r'^\s*<hr>','',inner[m.end():end],count=1)
        out.append('<details class="toggle item-toggle"><summary><strong>'+m.group(1)+'</strong></summary><div class="toggle-body">'+content+'</div></details>')
    return ''.join(out),len(found)

char_pat=re.compile(r'<h3>キャラクター作成詳細</h3>(.*?)(?=<h3>エリア詳細</h3>)',re.S); char_count=0
def char_repl(m):
    global char_count
    rebuilt,n=toggles_from_markers(re.sub(r'^\s*<hr>','',m.group(1),count=1),['共通作成ルール','マフィア','警察','教会','看守','囚人']); char_count=n
    return '<h3>キャラクター作成詳細</h3><hr>'+rebuilt
s=char_pat.sub(char_repl,s,count=1)

area_pat=re.compile(r'<h3>エリア詳細</h3>(.*?)(?=<h3>NPCファミリー</h3>)',re.S); area_count=0
def area_repl(m):
    global area_count
    rebuilt,n=toggles_from_markers(re.sub(r'^\s*<hr>','',m.group(1),count=1),['Newvail -ニューヴェール-','Polcano -ポルカーノ-','Vesper -ヴェスパー-','桜月 -おうげつ-','鬼籠 -グイロン-','Zastoy -ザストイ-']); area_count=n
    return '<h3>エリア詳細</h3><hr>'+rebuilt
s=area_pat.sub(area_repl,s,count=1)

# Keep the pink quote line on the quoted heading only; following text is normal body text.
s=re.sub(r'<blockquote>(.*?)</blockquote>\s*<p>(.*?)</p>',r'<div class="quote-group"><blockquote>\1</blockquote><p>\2</p></div>',s,flags=re.S)

def vertical_cs_tags(m):
    content=m.group(1).replace('\r\n','\n').replace('\r','\n'); content=re.sub(r'\n+','<br>',content); return '<p class="cs-tags">'+content+'</p>'
s=re.sub(r'<p>(︎✦︎<strong>CS必須</strong>.*?)</p>',vertical_cs_tags,s,count=1,flags=re.S)

# build.py creates the TOC before postprocess.py turns these labels into toggles.
# Rebuild it here so the item toggles also appear as indented subheadings.
toc_match=re.search(r'<nav class="toc"><b>目次</b><div class="toc-items">.*?</div></nav>',s,re.S)
if toc_match:
    entries=[]
    pos=0
    pat=re.compile(r'<h([23])>(.*?)</h\1>|<details class="toggle item-toggle"><summary><strong>(.*?)</strong></summary>',re.S)
    for m in pat.finditer(s):
        if m.start() < toc_match.end():
            continue
        if m.group(1):
            level='lv2' if m.group(1)=='2' else 'lv3'
            label=re.sub(r'<[^>]+>','',m.group(2)).strip()
        else:
            level='lv4'
            label=re.sub(r'<[^>]+>','',m.group(3)).strip()
        if not label:
            continue
        anchor=f'toc-section-{pos}'
        pos+=1
        start=m.start()
        if m.group(1):
            original=m.group(0)
            replacement=original.replace('>',f' id="{anchor}">',1)
        else:
            original=m.group(0)
            replacement=original.replace('<details ',f'<details id="{anchor}" ',1)
        s=s[:start]+replacement+s[m.end():]
        # Regex positions become stale after insertion, so only collect here;
        # IDs are normalized below in a second pass.
        entries.append((level,label))
        break

    # Assign stable IDs in document order after all post-processing.
    def add_ids():
        nonlocal_dummy=None
    targets=[]
    for m in re.finditer(r'<h([23])(?: id="[^"]*")?>(.*?)</h\1>|<details(?: id="[^"]*")? class="toggle item-toggle"><summary><strong>(.*?)</strong></summary>',s,re.S):
        if m.start() > toc_match.end(): targets.append(m)
    # Strip any temporary ID added above, then add all IDs safely from the end.
    s=re.sub(r' id="toc-section-\d+"','',s)
    targets=list(re.finditer(r'<h([23])>(.*?)</h\1>|<details class="toggle item-toggle"><summary><strong>(.*?)</strong></summary>',s,re.S))
    items=[]
    for i,m in reversed(list(enumerate(targets))):
        if m.start() < toc_match.end(): continue
        anchor=f'toc-section-{i}'
        if m.group(1):
            repl=m.group(0).replace('>',f' id="{anchor}">',1)
            level='lv2' if m.group(1)=='2' else 'lv3'; label=re.sub(r'<[^>]+>','',m.group(2)).strip()
        else:
            repl=m.group(0).replace('<details ',f'<details id="{anchor}" ',1)
            level='lv4'; label=re.sub(r'<[^>]+>','',m.group(3)).strip()
        s=s[:m.start()]+repl+s[m.end():]
        items.append((i,level,label,anchor))
    items.sort()
    links=''.join(f'<a class="{level}" href="#{anchor}">{label}</a>' for _,level,label,anchor in items)
    s=re.sub(r'<nav class="toc"><b>目次</b><div class="toc-items">.*?</div></nav>',f'<nav class="toc"><b>目次</b><div class="toc-items">{links}</div></nav>',s,count=1,flags=re.S)

s=re.sub(r'<style id="nbl-postprocess-style">.*?</style>','',s,flags=re.S)
extra_css='''<style id="nbl-postprocess-style">
/* Notion-like text rhythm */
main p,.toggle-body p{margin:0 0 14px;line-height:1.75;white-space:pre-line}main li,.toggle-body li{white-space:pre-line}main p+p,.toggle-body p+p{margin-top:8px}main h2{margin-top:2.1em;margin-bottom:.75em}main h3{margin-top:1.8em;margin-bottom:.65em}main hr{margin:22px 0}.toggle-body{padding-top:12px;padding-bottom:8px}.toggle-body ul,.toggle-body ol{margin-top:8px;margin-bottom:14px}.toggle-body li{margin:6px 0;line-height:1.7}
.quote-group{margin:18px 0 22px;padding-left:0;border-left:0}.quote-group blockquote{margin:0;padding:0 0 0 16px;border-left:4px solid #ff3f8e;white-space:pre-line}.quote-group p{margin:8px 0 0;padding:0;line-height:1.75;white-space:pre-line}.cs-tags{line-height:1.9;margin-top:8px!important;margin-bottom:18px!important;white-space:normal!important}
.qa-section{width:100%;max-width:760px;margin:18px 0 24px}.qa-section .qa-link{margin-left:0;margin-right:0}.qa-wrap{width:100%;max-width:760px;margin:18px 0 24px}.qa-banner{display:block;width:100%;margin:0;text-decoration:none;line-height:0;border-radius:8px;overflow:hidden}.qa-banner img{display:block!important;width:100%!important;height:auto!important;max-width:none!important;max-height:none!important;object-fit:contain!important;margin:0!important;padding:0!important}.qa-caption{margin-top:7px;text-align:center;font-size:13px;color:#777;line-height:1.5}
.toc .lv4{padding-left:36px;font-size:.94em;color:#666}
</style>'''
s=s.replace('</head>',extra_css+'</head>',1)
p.write_text(s,encoding='utf-8')
print(f'Patched Q&A image={qa_img.exists()}; character toggles={char_count}; area toggles={area_count}')
