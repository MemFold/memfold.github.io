"""Reflow Figure 6 as responsive SVG without changing its response text.
Requires Pillow only for font measurement. Text is extracted from the manuscript
when available, otherwise from the checked-in case-text.json snapshot.
"""
from pathlib import Path
import re,json,html
from PIL import ImageFont
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT.parent/'arxiv/5_discussion.tex'
SNAPSHOT=Path(__file__).with_name('case-text.json')

def argument(s,i):
    assert s[i]=='{'
    level=1;j=i+1
    while level:
        if s[j]=='{':level+=1
        if s[j]=='}':level-=1
        j+=1
    return s[i+1:j-1],j

def plain(s):
    out='';i=0
    while i<len(s):
        if s[i]!='\\':out+=s[i];i+=1;continue
        m=re.match(r'\\([A-Za-z]+|.)',s[i:]);command=m[1];i+=len(m[0])
        if command=='textcolor':
            _,i=argument(s,i);value,i=argument(s,i);out+=plain(value)
        elif command in ['textbf','texttt','textit']:
            value,i=argument(s,i);out+=plain(value)
        elif command=='ldots':out+='…'
        elif command==' ':out+=' '
        elif command=='scriptsize':pass
        else:raise ValueError(command)
    return out

if SOURCE.exists():
    source=SOURCE.read_text()
    bodies=re.findall(r'\\begin\{responsebox\}(.*?)\\end\{responsebox\}',source,re.S)
    paragraphs=[[' '.join(p.split()) for p in re.split(r'\n\s*\n',plain(body).strip()) if p.strip()] for body in bodies]
    data={'preference':'“I dislike using wearable technology and fitness trackers.”',
          'query':'“Can you recommend some effective ways for me to monitor my fitness progress?”',
          'responses':[{'label':label,'paragraphs':p,'verdict':verdict,'tokens':tokens} for label,p,verdict,tokens in zip(
              ['(a) GRPO','(b) OPSD','(c) MemFold'],paragraphs,
              ['Incorrect: violates preference','Incorrect: violates preference','Correct: respects preference'],
              ['300 answer tokens','300 answer tokens','96 answer tokens'])]}
    assert len(data['responses'])==3
    SNAPSHOT.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n')
else:data=json.loads(SNAPSHOT.read_text())
FONT=Path('/System/Library/Fonts/Supplemental/Arial.ttf')
BOLD=FONT.with_name('Arial Bold.ttf')
BLUE='#2563b8';INK='#242728';MUTED='#666b70'

def render(mobile=False):
    width=360 if mobile else 1200
    pad=8 if mobile else 8
    column=width-2*pad if mobile else (width-2*pad-2*48)/3
    size=16 if mobile else 18;lineheight=25 if mobile else 28
    font=ImageFont.truetype(str(FONT),size)
    bold=ImageFont.truetype(str(BOLD),size)
    parts=[]
    def text(x,y,value,size=size,fill=INK,weight='normal'):
        parts.append(f'<text x="{x:g}" y="{y:g}" font-size="{size}" fill="{fill}" font-weight="{weight}">{html.escape(value)}</text>')
    def paragraph(x,y,value,available,emphasis=False):
        words=value.split();lines=[];current=[]
        for word in words:
            candidate=' '.join(current+[word])
            if current and bold.getlength(candidate)>available:
                lines.append(' '.join(current));current=[word]
            else:current.append(word)
        if current:lines.append(' '.join(current))
        for line in lines:
            color=MUTED if line.startswith('… response') else BLUE if emphasis else INK
            text(x,y,line,fill=color);y+=lineheight
        return y
    text(pad,18,'User preference:',size=12,fill=MUTED,weight='bold')
    y=paragraph(pad,46,data['preference'],width-2*pad)
    text(pad,y+16,'Query:',size=12,fill=MUTED,weight='bold')
    y=paragraph(pad,y+44,data['query'],width-2*pad)
    top=y+36
    positions=[]
    for i,response in enumerate(data['responses']):
        x=pad if mobile else pad+i*(column+48)
        text(x,top,response['label'],size=22,fill=BLUE if i==2 else INK,weight='bold')
        body_y=top+38
        for para in response['paragraphs']:
            body_y=paragraph(x,body_y,para,column,emphasis=i==2 and ('journal' in para or 'measurements' in para))+16
        positions.append((x,body_y,response,i))
        if mobile:
            text(x,body_y+4,response['verdict'],size=13,fill=BLUE if i==2 else MUTED,weight='bold')
            text(x,body_y+27,response['tokens'],size=12,fill=MUTED)
            top=body_y+90
    if mobile:height=top-48
    else:
        footer=max(p[1] for p in positions)+4
        for x,_,response,i in positions:
            text(x,footer,response['verdict'],size=14,fill=BLUE if i==2 else MUTED,weight='bold')
            text(x,footer+25,response['tokens'],size=13,fill=MUTED)
        height=footer+45
    svg=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc" font-family="Arial, Helvetica, sans-serif"><title id="title">Personalization case from paper Figure 6</title><desc id="desc">Original response text, reflowed for the MemFold website. Three methods answer the same fitness question.</desc>'+''.join(parts)+'</svg>\n'
    target=ROOT/'assets'/('personalization-case-mobile.svg' if mobile else 'personalization-case.svg')
    target.write_text(svg)
    # SVG lines can reflow, but their words and punctuation must be unchanged.
    import xml.etree.ElementTree as ET
    texts=[e.text or '' for e in ET.fromstring(svg).findall('{http://www.w3.org/2000/svg}text')]
    rendered=' '.join(texts)
    for response in data['responses']:
        for para in response['paragraphs']:assert para in rendered,para
    print(target.name,'— all response text matches source exactly')
render();render(True)
