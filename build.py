import os, html, re
from pathlib import Path
import requests

TOKEN=os.environ['NOTION_TOKEN']; PAGE=os.environ.get('NOTION_PAGE_ID','3c5a36e22f8980faa373c5a3b63518d3').replace('-','')
API='https://api.notion.com/v1'; S=requests.Session(); S.headers.update({'Authorization':f'Bearer {TOKEN}','Notion-Version':'2022-06-28'})
def get(path,params=None):
 r=S.get(API+path,params=params,timeout=30); r.raise_for_status(); return r.json()
def kids(i):
 out=[]; c=None
 while True:
  p={'page_size':100};
  if c:p['start_cursor']=c
  d=get(f'/blocks/{i}/children',p); out+=d['results']
  if not d.get('has_more'):return out
  c=d['next_cursor']
def rt(xs):
 z=''
 for x in xs or []:
  t=html.escape(x.get('plain_text','')); a=x.get('annotations',{})
  if a.get('bold'):t=f'<strong>{t}</strong>'
  if a.get('italic'):t=f'<em>{t}</em>'
  if a.get('strikethrough'):t=f'<s>{t}</s>'
  if a.get('underline'):t=f'<u>{t}</u>'
  if a.get('code'):t=f'<code>{t}</code>'
  href=x.get('href')
  if href:t=f'<a href="{html.escape(href,quote=True)}" target="_blank" rel="noopener">{t}</a>'
  z+=t
 return z
def render(bs):
 out=[]; ul=ol=False
 def close():
  nonlocal ul,ol
  if ul:out.append('</ul>');ul=False
  if ol:out.append('</ol>');ol=False
 for b in bs:
  typ=b['type']; d=b.get(typ,{})
  if typ=='bulleted_list_item':
   if ol:out.append('</ol>');ol=False
   if not ul:out.append('<ul>');ul=True
   sub=render(kids(b['id'])) if b.get('has_children') else ''; out.append(f'<li>{rt(d.get("rich_text"))}{sub}</li>');continue
  if typ=='numbered_list_item':
   if ul:out.append('</ul>');ul=False
   if not ol:out.append('<ol>');ol=True
   sub=render(kids(b['id'])) if b.get('has_children') else ''; out.append(f'<li>{rt(d.get("rich_text"))}{sub}</li>');continue
  close()
  sub=render(kids(b['id'])) if b.get('has_children') else ''
  if typ=='paragraph':
   x=rt(d.get('rich_text')); out.append(f'<p>{x}</p>{sub}' if x else sub)
  elif typ in ('heading_1','heading_2','heading_3'):
   n=int(typ[-1]); x=rt(d.get('rich_text'))
   # Notion headings can themselves be toggles.
   if d.get('is_toggleable') or sub: out.append(f'<details class="toggle heading-toggle"><summary><span class="h{n}">{x}</span></summary>{sub}</details>')
   else: out.append(f'<h{n}>{x}</h{n}>')
  elif typ=='toggle':out.append(f'<details class="toggle"><summary>{rt(d.get("rich_text"))}</summary>{sub}</details>')
  elif typ=='quote':out.append(f'<blockquote>{rt(d.get("rich_text"))}</blockquote>{sub}')
  elif typ=='callout':out.append(f'<aside>{rt(d.get("rich_text"))}{sub}</aside>')
  elif typ=='divider':out.append('<hr>')
  elif typ=='code':out.append(f'<pre><code>{html.escape("".join(x.get("plain_text","") for x in d.get("rich_text",[])))}</code></pre>')
  elif typ=='to_do':out.append(f'<label class="todo"><input type="checkbox" disabled{" checked" if d.get("checked") else ""}> {rt(d.get("rich_text"))}</label>{sub}')
  elif typ=='child_page':out.append(f'<section><h2>{html.escape(d.get("title",""))}</h2>{sub}</section>')
  elif typ=='bookmark' or typ=='link_preview' or typ=='embed':
   u=d.get('url',''); out.append(f'<p class="linkcard"><a href="{html.escape(u,quote=True)}" target="_blank" rel="noopener">{html.escape(u)}</a></p>')
  elif typ=='link_to_page':
   target=d.get('page_id') or d.get('database_id') or ''; out.append(f'<p><a href="https://www.notion.so/{target.replace("-","")}" target="_blank" rel="noopener">Notionページを開く</a></p>')
  elif typ=='table_of_contents':out.append('<nav id="notion-toc" class="toc"><b>目次</b><div class="toc-items"></div></nav>')
  elif typ=='table':
   out.append('<div class="table"><table>')
   for row in kids(b['id']):out.append('<tr>'+''.join(f'<td>{rt(c)}</td>' for c in row.get('table_row',{}).get('cells',[]))+'</tr>')
   out.append('</table></div>')
  elif typ=='synced_block':out.append(sub)
  elif typ=='column_list' or typ=='column':out.append(f'<div class="{typ}">{sub}</div>')
  else:
   x=rt(d.get('rich_text')); out.append((f'<p>{x}</p>' if x else '')+sub)
 close();return ''.join(out)
page=get(f'/pages/{PAGE}'); title="Nobody's Law"
for v in page.get('properties',{}).values():
 if v.get('type')=='title':title=''.join(x.get('plain_text','') for x in v.get('title',[])) or title;break
body=render(kids(PAGE))
CSS='''*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:#f4f4f4;color:#171717;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","Noto Sans JP",sans-serif;line-height:1.8}main{width:min(920px,100%);min-height:100vh;margin:auto;background:#fff;padding:100px 64px}h1{font-size:42px}h2{margin-top:48px;border-bottom:2px solid #171717}.toggle{margin:8px 0}.toggle summary{cursor:pointer;font-weight:600}.heading-toggle>summary{list-style-position:outside}.h1,.h2,.h3{display:inline;font-weight:700}.h1{font-size:2em}.h2{font-size:1.5em}.h3{font-size:1.17em}.toggle> :not(summary){margin-left:22px}.toc{padding:14px 18px;border:1px solid #ddd;border-radius:10px;background:#fafafa;margin:22px 0}.toc a{display:block;color:#555;text-decoration:none;padding:3px 0}.toc a:hover{color:#ff3f8e}.toc .lv3{padding-left:18px}.linkcard{padding:10px 12px;border:1px solid #ddd;border-radius:8px;overflow-wrap:anywhere}blockquote{border-left:4px solid #ff3f8e;padding-left:16px}aside{padding:12px;background:#fafafa;border-radius:8px}.table{overflow:auto}table{border-collapse:collapse;width:100%}td{border:1px solid #ddd;padding:7px}#search{position:fixed;z-index:20;right:16px;top:16px;width:min(410px,calc(100vw - 24px));background:#fffd;border:1px solid #ddd;border-radius:14px;box-shadow:0 10px 35px #0002;padding:12px;backdrop-filter:blur(12px)}#q{width:calc(100% - 125px);height:38px;border:1px solid #ccc;border-radius:8px;padding:0 10px}button{height:36px;min-width:35px;margin-left:4px;border:0;border-radius:8px;cursor:pointer}.status{font-size:11px;color:#777;margin-top:6px}.results{max-height:290px;overflow:auto}.result{display:block;width:100%;height:auto;text-align:left;margin:0;padding:8px;background:#fff;border-radius:0;border-top:1px solid #eee}.result.active{background:#ff3f8e12}.hit{background:#ffe66b}.hit.current{background:#ff3f8e;color:#fff}@media(max-width:600px){main{padding:110px 20px 60px}h1{font-size:30px}#search{right:8px;top:8px}}'''
JS='''(()=>{const main=document.querySelector('main');let hs=[...main.querySelectorAll('h2,h3,.heading-toggle .h2,.heading-toggle .h3')];hs.forEach((h,i)=>{let target=h.closest('details')||h;target.id='section-'+i});document.querySelectorAll('.toc-items').forEach(t=>{hs.forEach((h,i)=>{let a=document.createElement('a');a.href='#section-'+i;a.textContent=h.textContent;a.className=(h.matches('h3,.h3')?'lv3':'lv2');a.onclick=()=>{let d=h.closest('details');if(d)d.open=true};t.appendChild(a)})});const q=document.getElementById('q'),st=document.getElementById('status'),rs=document.getElementById('results');let hits=[],cur=-1;function clear(){document.querySelectorAll('.hit').forEach(x=>{let p=x.parentNode;while(x.firstChild)p.insertBefore(x.firstChild,x);x.remove();p.normalize()});hits=[];cur=-1}function nodes(){let w=document.createTreeWalker(main,NodeFilter.SHOW_TEXT,{acceptNode:n=>n.nodeValue.trim()&&!n.parentElement.closest('.toc')?NodeFilter.FILTER_ACCEPT:NodeFilter.FILTER_REJECT}),a=[],n;while(n=w.nextNode())a.push(n);return a}function go(i){if(!hits.length)return;hits.forEach(x=>x.classList.remove('current'));cur=(i+hits.length)%hits.length;let h=hits[cur];h.classList.add('current');for(let d=h.parentElement.closest('details');d;d=d.parentElement.closest('details'))d.open=true;h.scrollIntoView({behavior:'smooth',block:'center'});[...rs.children].forEach((x,n)=>x.classList.toggle('active',n===cur));st.textContent=`${cur+1} / ${hits.length} 件`}function search(){clear();rs.innerHTML='';let s=q.value.trim();if(!s){st.textContent='';return}let lo=s.toLocaleLowerCase();for(let n of nodes()){let t=n.nodeValue,l=t.toLocaleLowerCase(),p=0,f=document.createDocumentFragment(),ok=false;while(1){let i=l.indexOf(lo,p);if(i<0){f.appendChild(document.createTextNode(t.slice(p)));break}ok=true;f.appendChild(document.createTextNode(t.slice(p,i)));let m=document.createElement('span');m.className='hit';m.textContent=t.slice(i,i+s.length);f.appendChild(m);hits.push(m);p=i+s.length}if(ok)n.parentNode.replaceChild(f,n)}if(!hits.length){st.textContent='見つかりません';return}hits.forEach((h,i)=>{let b=document.createElement('button');b.className='result';let txt=h.parentElement.textContent.replace(/\\s+/g,' ');b.textContent=`${i+1}. ${txt.slice(0,130)}`;b.onclick=()=>go(i);rs.appendChild(b)});go(0)}q.oninput=search;q.onkeydown=e=>{if(e.key==='Enter'){e.preventDefault();go(e.shiftKey?cur-1:cur+1)}};prev.onclick=()=>go(cur-1);next.onclick=()=>go(cur+1);document.getElementById('clear').onclick=()=>{q.value='';clear();rs.innerHTML='';st.textContent=''}})();'''
T='<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>__TITLE__ — 設定資料</title><style>'+CSS+'</style></head><body><div id="search"><input id="q" type="search" placeholder="キーワードを検索…"><button id="prev">↑</button><button id="next">↓</button><button id="clear">×</button><div id="status" class="status"></div><div id="results" class="results"></div></div><main><h1>__TITLE__</h1>__BODY__</main><script>'+JS+'</script></body></html>'
Path('index.html').write_text(T.replace('__TITLE__',html.escape(title)).replace('__BODY__',body),encoding='utf-8')
print('Built',title)
