from pathlib import Path
import re

p=Path('index.html')
s=p.read_text(encoding='utf-8')

QA_URL='https://app.notion.com/p/Nobody-s-Law-Q-A-3c4a36e22f8980ad8aadd30fbefa7920'
QA_IMAGE='582_20260823202440.png'
qa_img=Path(QA_IMAGE)
if qa_img.exists():
    qa_html=(f'<a class="qa-banner" href="{QA_URL}" target="_blank" rel="noopener">'
             f'<img src="{QA_IMAGE}" alt="Nobody\'s Law Q&A"></a>')
else:
    qa_html=f'<blockquote class="qa-link"><strong><a href="{QA_URL}" target="_blank" rel="noopener">Q＆Aはこちら</a></strong></blockquote>'

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

s=re.sub(r'<blockquote>(.*?)</blockquote>\s*<p>(.*?)</p>',r'<div class="quote-group"><blockquote>\1</blockquote><p>\2</p></div>',s,flags=re.S)

def vertical_cs_tags(m):
    content=m.group(1).replace('\r\n','\n').replace('\r','\n'); content=re.sub(r'\n+','<br>',content); return '<p class="cs-tags">'+content+'</p>'
s=re.sub(r'<p>(︎✦︎<strong>CS必須</strong>.*?)</p>',vertical_cs_tags,s,count=1,flags=re.S)

s=re.sub(r'<style id="nbl-postprocess-style">.*?</style>','',s,flags=re.S)
extra_css='''<style id="nbl-postprocess-style">
.quote-group{margin:16px 0;padding-left:16px;border-left:4px solid #ff3f8e}.quote-group blockquote{margin:0;padding:0;border:0}.quote-group p{margin:4px 0 0;padding:0}.cs-tags{line-height:1.9}
.qa-banner{display:block;width:100%;max-width:760px;margin:18px 0;text-decoration:none;line-height:0;border-radius:8px;overflow:hidden}
.qa-banner img{display:block!important;width:100%!important;height:auto!important;max-width:none!important;max-height:none!important;object-fit:contain!important;margin:0!important;padding:0!important}
</style>'''
s=s.replace('</head>',extra_css+'</head>',1)
p.write_text(s,encoding='utf-8')
print(f'Patched Q&A image={qa_img.exists()}; character toggles={char_count}; area toggles={area_count}')
