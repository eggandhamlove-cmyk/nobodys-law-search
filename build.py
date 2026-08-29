import os, html
from pathlib import Path
import requests

TOKEN = os.environ["NOTION_TOKEN"]
PAGE_ID = os.environ.get("NOTION_PAGE_ID", "3c5a36e22f8980faa373c5a3b63518d3").replace("-", "")
API = "https://api.notion.com/v1"
HEADERS = {"Authorization": f"Bearer {TOKEN}", "Notion-Version": "2022-06-28"}
s = requests.Session(); s.headers.update(HEADERS)

def get(path, params=None):
    r = s.get(API + path, params=params, timeout=30); r.raise_for_status(); return r.json()

def children(block_id):
    out, cursor = [], None
    while True:
        p = {"page_size": 100}
        if cursor: p["start_cursor"] = cursor
        d = get(f"/blocks/{block_id}/children", p); out += d["results"]
        if not d.get("has_more"): return out
        cursor = d["next_cursor"]

def rich(xs):
    out = ""
    for x in xs or []:
        t = html.escape(x.get("plain_text", "")); a = x.get("annotations", {})
        if a.get("bold"): t = f"<strong>{t}</strong>"
        if a.get("italic"): t = f"<em>{t}</em>"
        if a.get("strikethrough"): t = f"<s>{t}</s>"
        if a.get("underline"): t = f"<u>{t}</u>"
        if a.get("code"): t = f"<code>{t}</code>"
        if x.get("href"): t = f'<a href="{html.escape(x["href"], quote=True)}" target="_blank" rel="noopener">{t}</a>'
        out += t
    return out

def render(bs):
    out=[]; ul=ol=False
    def close_lists():
        nonlocal ul,ol
        if ul: out.append("</ul>"); ul=False
        if ol: out.append("</ol>"); ol=False
    for b in bs:
        typ=b["type"]; d=b.get(typ,{})
        if typ=="bulleted_list_item":
            if ol: out.append("</ol>"); ol=False
            if not ul: out.append("<ul>"); ul=True
            nested=render(children(b["id"])) if b.get("has_children") else ""
            out.append(f"<li>{rich(d.get('rich_text'))}{nested}</li>"); continue
        if typ=="numbered_list_item":
            if ul: out.append("</ul>"); ul=False
            if not ol: out.append("<ol>"); ol=True
            nested=render(children(b["id"])) if b.get("has_children") else ""
            out.append(f"<li>{rich(d.get('rich_text'))}{nested}</li>"); continue
        close_lists()
        if typ=="paragraph":
            x=rich(d.get("rich_text")); out += [f"<p>{x}</p>"] if x else []
        elif typ in ("heading_1","heading_2","heading_3"):
            n=typ[-1]; out.append(f"<h{n}>{rich(d.get('rich_text'))}</h{n}>")
        elif typ=="quote": out.append(f"<blockquote>{rich(d.get('rich_text'))}</blockquote>")
        elif typ=="callout": out.append(f"<aside>{rich(d.get('rich_text'))}</aside>")
        elif typ=="divider": out.append("<hr>")
        elif typ=="code": out.append(f"<pre><code>{html.escape(''.join(x.get('plain_text','') for x in d.get('rich_text',[])))}</code></pre>")
        elif typ=="to_do":
            ck=" checked" if d.get("checked") else ""; out.append(f'<label class="todo"><input type="checkbox" disabled{ck}> {rich(d.get("rich_text"))}</label>')
        elif typ=="toggle":
            nested=render(children(b["id"])) if b.get("has_children") else ""; out.append(f"<details><summary>{rich(d.get('rich_text'))}</summary>{nested}</details>")
        elif typ=="child_page":
            # Child pages are rendered inline so one search covers the whole guide.
            nested=render(children(b["id"]))
            out.append(f"<section><h2>{html.escape(d.get('title',''))}</h2>{nested}</section>")
        elif typ=="table":
            rows=children(b["id"]); out.append('<div class="table"><table>')
            for row in rows:
                cells=row.get("table_row",{}).get("cells",[]); out.append("<tr>"+"".join(f"<td>{rich(c)}</td>" for c in cells)+"</tr>")
            out.append("</table></div>")
        else:
            x=rich(d.get("rich_text")); out += [f"<p>{x}</p>"] if x else []
    close_lists(); return "".join(out)

page=get(f"/pages/{PAGE_ID}"); title="Nobody's Law"
for v in page.get("properties",{}).values():
    if v.get("type")=="title": title="".join(x.get("plain_text","") for x in v.get("title",[])) or title; break
body=render(children(PAGE_ID))

T='''<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>__TITLE__ — 設定資料</title><style>
:root{--pink:#ff3f8e}*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:#f4f4f4;color:#171717;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","Noto Sans JP",sans-serif;line-height:1.8}main{width:min(920px,100%);min-height:100vh;margin:auto;background:white;padding:100px 64px}h1{font-size:42px}h2{margin-top:48px;padding-bottom:8px;border-bottom:2px solid #171717}blockquote{border-left:4px solid var(--pink);padding-left:16px}aside{padding:12px 15px;background:#fafafa;border:1px solid #eee;border-radius:8px}pre{padding:14px;background:#181818;color:white;overflow:auto}.table{overflow:auto}table{border-collapse:collapse;width:100%}td{border:1px solid #ddd;padding:7px}.todo{display:block}
#search{position:fixed;z-index:20;right:16px;top:16px;width:min(410px,calc(100vw - 24px));background:#fffd;border:1px solid #ddd;border-radius:14px;box-shadow:0 10px 35px #0002;padding:12px;backdrop-filter:blur(12px)}#q{width:calc(100% - 125px);height:38px;border:1px solid #ccc;border-radius:8px;padding:0 10px;outline:none}#q:focus{border-color:var(--pink);box-shadow:0 0 0 3px #ff3f8e22}button{height:36px;min-width:35px;margin-left:4px;border:0;border-radius:8px;cursor:pointer}.status{font-size:11px;color:#777;margin-top:6px}.results{max-height:290px;overflow:auto}.result{display:block;width:100%;height:auto;text-align:left;margin:0;padding:8px;background:white;border-radius:0;border-top:1px solid #eee}.result.active{background:#ff3f8e12}.result small{display:block;color:#777}.hit{background:#ffe66b;border-radius:2px}.hit.current{background:var(--pink);color:white}
@media(max-width:600px){main{padding:110px 20px 60px}h1{font-size:30px}#search{right:8px;top:8px}}
</style></head><body><div id="search"><input id="q" type="search" placeholder="キーワードを検索…"><button id="prev">↑</button><button id="next">↓</button><button id="clear">×</button><div id="status" class="status"></div><div id="results" class="results"></div></div><main><h1>__TITLE__</h1>__BODY__</main><script>
(()=>{const q=document.getElementById('q'),st=document.getElementById('status'),rs=document.getElementById('results');let hits=[],cur=-1;function clear(){document.querySelectorAll('.hit').forEach(x=>{let p=x.parentNode;while(x.firstChild)p.insertBefore(x.firstChild,x);x.remove();p.normalize()});hits=[];cur=-1}function nodes(){let w=document.createTreeWalker(document.querySelector('main'),NodeFilter.SHOW_TEXT,{acceptNode:n=>n.nodeValue.trim()?NodeFilter.FILTER_ACCEPT:NodeFilter.FILTER_REJECT}),a=[],n;while(n=w.nextNode())a.push(n);return a}function go(i){if(!hits.length)return;hits.forEach(x=>x.classList.remove('current'));cur=(i+hits.length)%hits.length;hits[cur].classList.add('current');hits[cur].scrollIntoView({behavior:'smooth',block:'center'});[...rs.children].forEach((x,n)=>x.classList.toggle('active',n===cur));st.textContent=`${cur+1} / ${hits.length} 件`}function search(){clear();rs.innerHTML='';let s=q.value.trim();if(!s){st.textContent='';return}let lo=s.toLocaleLowerCase();for(let n of nodes()){let t=n.nodeValue,l=t.toLocaleLowerCase(),p=0,f=document.createDocumentFragment(),ok=false;while(1){let i=l.indexOf(lo,p);if(i<0){f.appendChild(document.createTextNode(t.slice(p)));break}ok=true;f.appendChild(document.createTextNode(t.slice(p,i)));let m=document.createElement('span');m.className='hit';m.textContent=t.slice(i,i+s.length);f.appendChild(m);hits.push(m);p=i+s.length}if(ok)n.parentNode.replaceChild(f,n)}if(!hits.length){st.textContent='見つかりません';return}hits.forEach((h,i)=>{let b=document.createElement('button');b.className='result';let txt=h.parentElement.textContent.replace(/\\s+/g,' '),ix=txt.toLocaleLowerCase().indexOf(lo),sn=txt.slice(Math.max(0,ix-45),ix+s.length+80);b.textContent=`${i+1}. ${sn}`;b.onclick=()=>go(i);rs.appendChild(b)});go(0)}q.oninput=search;q.onkeydown=e=>{if(e.key==='Enter'){e.preventDefault();go(e.shiftKey?cur-1:cur+1)}};document.getElementById('prev').onclick=()=>go(cur-1);document.getElementById('next').onclick=()=>go(cur+1);document.getElementById('clear').onclick=()=>{q.value='';clear();rs.innerHTML='';st.textContent=''};})();
</script></body></html>'''
Path("index.html").write_text(T.replace("__TITLE__",html.escape(title)).replace("__BODY__",body),encoding="utf-8")
print("Built", title)
