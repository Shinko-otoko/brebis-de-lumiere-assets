import numpy as np, wave, subprocess, math, random, json, asyncio, re, os
from PIL import Image, ImageFilter, ImageDraw
from playwright.async_api import async_playwright
R='/home/claude/work/refs/'; FPS=25; AUD='/home/claude/work/talk/talk3.wav'
FONTS='file:///home/claude/kit/kit/reel/assets/fonts/'
CTA=float(open('cta3.txt').read())
HOOK=["Dieu voulait que tu entendes","ça aujourd'hui."]
TEXT="Dieu voulait que tu entendes ça aujourd'hui. Dieu t'aime, exactement comme tu es. Alors respire, et sois en paix. Dis amen, et abonne-toi pour recevoir un verset chaque jour."
w=wave.open(AUD); sr=w.getframerate(); a=np.frombuffer(w.readframes(w.getnframes()),dtype=np.int16).astype(float)/32768
dur=len(a)/sr; N=int(dur*FPS)+1
# ---------- lip sync features
hop=sr//FPS; win=int(sr*0.04); rms=[];cen=[]
for i in range(N):
    seg=a[max(0,i*hop-win//2):i*hop+win//2]
    if len(seg)<64: rms.append(0);cen.append(0);continue
    rms.append(math.sqrt((seg**2).mean()))
    sp=np.abs(np.fft.rfft(seg*np.hanning(len(seg)))); f=np.fft.rfftfreq(len(seg),1/sr)
    cen.append((sp*f).sum()/(sp.sum()+1e-9))
rms=np.array(rms);cen=np.array(cen);rs=np.convolve(rms,[.25,.5,.25],'same')
lv=rs/np.percentile(rs[rs>0.01],90)
state=[];prev='closed';hold=0
for i in range(N):
    l=lv[i]; s='closed' if l<0.12 else ('mid' if l<0.45 else 'wide')
    if s!='closed':
        if cen[i]<900 and l<0.8: s='o'
        elif cen[i]>2200 and l<0.9: s='ee'
        elif s=='wide' and l<=1.1 and i%7==0: s='mid'
    if s!=prev and hold<2: s=prev; hold+=1
    else:
        hold=0 if s!=prev else hold+1
    state.append(s);prev=s
random.seed(4);blink=[False]*N;t=1.2
while t<dur-0.5:
    f=int(t*FPS)
    for d in (1,2):
        if f+d<N: blink[f+d]=True
    t+=random.uniform(2.6,4.6)
# ---------- words timing (voiced-time proportional)
voiced=lv>0.10
words=TEXT.split(' ')
cum=np.cumsum(voiced)/FPS; tot=cum[-1]
wl=[len(x)+1 for x in words]; W_=sum(wl)
def vt2t(v): return float(np.searchsorted(cum,v))/FPS
wt=[];c=0
for x,l in zip(words,wl):
    wt.append((vt2t(c/W_*tot),vt2t((c+l)/W_*tot))); c+=l
# ---------- sprites w/ transparent background
S={k:Image.open(R+f).convert('RGB') for k,f in dict(closed='ref1.png',mid='ref2.png',wide='ref3.png',o='s_o.png',ee='s_ee.png',blink='s_blink.png',wave='ref4.png').items()}
W,H=S['closed'].size
def mask(box,fe):
    m=Image.new('L',(W,H),0);m.paste(255,box);return m.filter(ImageFilter.GaussianBlur(fe))
mm=mask((235,590,535,705),7);me=mask((225,495,545,590),6)
from PIL import ImageChops
def cutbg(im):
    # flood-fill from corners to find background -> alpha 0
    g=im.copy(); a=Image.new('L',im.size,255)
    mk=Image.new('L',(im.width+2,im.height+2),0)
    import numpy as _n
    arr=_n.array(im).astype(int); bg=arr[5,5]
    dist=_n.abs(arr-bg).sum(axis=2)
    cand=(dist<30)
    from scipy import ndimage as ndi
    lab,n=ndi.label(cand); ids={lab[2,2],lab[2,-3],lab[-3,2],lab[-3,-3]}-{0}
    bgm=_n.isin(lab,list(ids))
    al=_n.where(bgm,0,255).astype('uint8')
    A=Image.fromarray(al).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(0.8))
    r=im.convert('RGBA'); r.putalpha(A); return r
cache={}
def sprite(mo,eye,wv):
    k=(mo,eye,wv)
    if k not in cache:
        f=S['wave' if wv else 'closed'].copy(); f.paste(S[mo],(0,0),mm); f.paste(S[eye],(0,0),me)
        cache[k]=cutbg(f)
    return cache[k]
# ---------- background
def make_bg():
    bg=Image.new('RGB',(1080,1920),(246,244,238)); d=ImageDraw.Draw(bg)
    for x in range(0,1080,60): d.line([(x,0),(x,1920)],fill=(240,238,232),width=2)
    for y in range(0,1920,60): d.line([(0,y),(1080,y)],fill=(240,238,232),width=2)
    d.rounded_rectangle((700,1210,830,1770),10,fill=(237,232,218)); d.rounded_rectangle((560,1350,970,1470),10,fill=(237,232,218))
    return bg
BG=make_bg()
# ---------- overlays via chromium
CSS=f"""@font-face{{font-family:Nunito;font-weight:900;src:url({FONTS}nunito-sans-latin-900-normal.woff2)}}
@font-face{{font-family:Nunito;font-weight:800;src:url({FONTS}nunito-sans-latin-800-normal.woff2)}}
html,body{{margin:0;background:transparent;width:1080px;height:1920px;position:relative}}
.hook{{position:absolute;left:50%;transform:translateX(-50%);font:900 68px/1.1 Nunito;background:#fff;color:#0A0A0A;padding:22px 44px;border-radius:30px;white-space:nowrap;box-shadow:0 10px 30px rgba(10,10,10,.12),0 0 0 2px rgba(10,10,10,.06)}}
.line{{position:absolute;left:340px;width:400px;height:8px;border-radius:5px;background:linear-gradient(90deg,#C9A24B,#8F6E2A)}}
#sub{{position:absolute;left:60px;width:960px;top:1480px;height:170px;display:flex;align-items:center;justify-content:center;text-align:center;font:800 76px/1.12 Nunito;color:#0A0A0A;text-shadow:0 2px 16px rgba(246,244,238,.95)}}
.w{{display:inline-block;margin:0 .13em}} .w.on{{color:#A67C1E}}"""
chunks=[];i=0
while i<len(words):
    j=min(len(words),i+3)
    # don't break right after short word at end; keep punctuation-ending chunks
    for k in range(i,j):
        if re.search(r'[.!?,]$',words[k]) and k>=i: j=k+1;break
    chunks.append((i,j));i=j
async def render_overlays():
    out={}
    async with async_playwright() as p:
        b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1080,'height':1920})
        html=f"<style>{CSS}</style><div class=hook style='top:470px'>{HOOK[0]}</div><div class=hook style='top:620px;color:#333'>{HOOK[1]}</div><div class=line style='top:760px'></div>"
        open('ov.html','w').write(html); await pg.goto('file:///home/claude/work/talk/ov.html'); await pg.evaluate('document.fonts.ready'); await pg.wait_for_timeout(400)
        await pg.screenshot(path='ov_hook.png',omit_background=True)
        for ci,(a_,b_) in enumerate(chunks):
            for cur in range(a_,b_):
                ws=''.join(f"<span class='w{' on' if k==cur else ''}'>{words[k]}</span>" for k in range(a_,b_))
                open('ov.html','w').write(f"<style>{CSS}</style><div id=sub>{ws}</div>"); await pg.goto('file:///home/claude/work/talk/ov.html'); await pg.evaluate('document.fonts.ready'); await pg.wait_for_timeout(120)
                fn=f'ov_s{cur}.png'; await pg.screenshot(path=fn,omit_background=True,clip={'x':0,'y':1460,'width':1080,'height':210}); out[cur]=fn
        await b.close()
    return out
subs=asyncio.run(render_overlays())
hook=Image.open('ov_hook.png').convert('RGBA')
subimg={k:Image.open(v).convert('RGBA') for k,v in subs.items()}
# which word is current at time t
def cur_word(t):
    c=None
    for k,(s,e) in enumerate(wt):
        if t>=s-0.02: c=k
    return c
HOOK_END=wt[6][1]+0.6 if len(wt)>6 else 3.5   # until end of first sentence (7 words)
p=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','1080x1920','-r',str(FPS),'-i','-','-i',AUD,'-c:v','libx264','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-shortest','brebis_reel.mp4'],stdin=subprocess.PIPE)
for i in range(N):
    t=i/FPS; mo=state[i]; eye='blink' if blink[i] else 'closed'
    wv=(t>=CTA and (int((t-CTA)/0.4)%2==0 or t>dur-0.6))
    sp_=sprite(mo,eye,wv)
    dy=5*math.sin(2*math.pi*t/2.8)+(3 if mo=='wide' else 0); dx=2*math.sin(2*math.pi*t/4.1); ang=0.7*math.sin(2*math.pi*t/3.7)
    sp2=sp_.rotate(ang,resample=Image.BICUBIC,translate=(dx,dy),center=(W/2,H*0.62))
    lamb=sp2.crop((60,270,710,1110)).resize((585,756),Image.LANCZOS)   # lamb region
    fr=BG.convert('RGBA'); fr.alpha_composite(lamb,(247,760))
    if t<HOOK_END:
        pop=min(1,t/0.15); ov=hook if pop>=1 else hook.copy()
        if t>HOOK_END-0.2:
            al=max(0,(HOOK_END-t)/0.2); ov=hook.copy(); ov.putalpha(ov.getchannel('A').point(lambda v:int(v*al)))
        fr.alpha_composite(ov)
    cw=cur_word(t)
    if cw is not None and t<wt[-1][1]+0.5: fr.alpha_composite(subimg[cw],(0,1460))
    p.stdin.write(fr.convert('RGB').tobytes())
p.stdin.close();p.wait();print('done',N,dur,'hook_end',HOOK_END)
