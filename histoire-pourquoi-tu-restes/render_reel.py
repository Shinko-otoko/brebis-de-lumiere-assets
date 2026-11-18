import json, math, os, re, asyncio, subprocess, glob
from PIL import Image
from playwright.async_api import async_playwright
R='/home/claude/histoire-claire'; OUT=R+'/reel'; os.chdir(OUT)
FPS=25; WW,HH=1080,1920; AUD=R+'/voix/talk.wav'; FONTS='file:///home/claude/dl_assets/repo/fonts/'
WJ=json.load(open(R+'/voix/words_snap.json')); words=[x['w'] for x in WJ]; wt=[(x['s'],x['e']) for x in WJ]
dur=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',AUD])); N=int(dur*FPS)+1
def W(i): return wt[i][0]
idx=lambda w,after=0: next(k for k,x in enumerate(words) if x==w and wt[k][0]>=after)
t_ret=W(idx('Elle')); t_soir=W(idx('Un'))-0.15; t_q1=W(idx('Franchement,',10)); t_sourit=W(idx('Claire',13.5)); t_ans=W(idx('Je',16))
t_sil=W(idx('Un',22))-0.1; t_amour=W(idx("L'amour")); t_ref=W(idx('Première')); t_cta=W(idx('Si',33))
def frames(d): return sorted(glob.glob(f'{R}/{d}/*.png'))
F1=[Image.open(f).convert('RGBA') for f in frames('fr1')]; F2=[Image.open(f).convert('RGBA') for f in frames('fr2')]
START=Image.open(R+'/start_1080.png').convert('RGBA'); DECOR=Image.open(R+'/decor_1080.png').convert('RGBA')
ss=lambda x:(lambda y:y*y*(3-2*y))(max(0,min(1,x)))
def zoom(im,z,cx,cy):
    if abs(z-1)<1e-3: return im
    cw,ch=WW/z,HH/z; x0=min(max(cx-cw/2,0),WW-cw); y0=min(max(cy-ch/2,0),HH-ch)
    return im.transform((WW,HH),Image.EXTENT,(x0,y0,x0+cw,y0+ch),Image.BICUBIC)
def clipf(seq,t,t0,speed=1.0): return seq[max(0,min(len(seq)-1,int((t-t0)*speed*FPS)))]
# plan : (a,b,source,zoom0,zoom1,cx,cy)
SC=[(0,t_soir,'start',1.0,1.12,540,1000),
    (t_soir,t_sourit,'s1',1.0,1.0,540,1000),
    (t_sourit,t_ans,'s1end',1.0,1.28,300,900),
    (t_ans,t_sil,'s2',1.0,1.0,540,1000),
    (t_sil,t_amour,'s2end',1.0,1.3,800,900),
    (t_amour,t_cta,'decor',1.0,1.1,540,1000),
    (t_cta,dur+1,'start',1.12,1.0,540,1000)]
def src_frame(sc,t):
    a,b,s,z0,z1,cx,cy=sc
    if s=='start': im=START
    elif s=='decor': im=DECOR
    elif s=='s1': im=clipf(F1,t,t_soir-0.0)   # la question se joue pendant l'annonce
    elif s=='s1end': im=F1[-1]
    elif s=='s2': im=clipf(F2,t,t_ans-0.1)
    elif s=='s2end': im=F2[-1]
    z=z0+(z1-z0)*ss((t-a)/max(.1,b-a)); return zoom(im,z,cx,cy)
OV=[('hook',0,t_ret-.05),('ret',t_ret+.05,t_soir-.1),('q1',t_q1,t_sourit+.3),('q2',t_ans,t_sil-.1),('q3',t_amour,t_cta-.2),('cta',t_cta+.05,dur+1)]
CSS=f"""@font-face{{font-family:Nunito;font-weight:900;src:url({FONTS}nunito-sans-latin-900-normal.woff2)}}
@font-face{{font-family:Nunito;font-weight:800;src:url({FONTS}nunito-sans-latin-800-normal.woff2)}}
@font-face{{font-family:Lora;font-weight:600;src:url({FONTS}lora-latin-600-normal.woff2)}}
html,body{{margin:0;background:transparent;width:1080px;height:1920px;position:relative}}
.p{{position:absolute;left:50%;transform:translateX(-50%);font:900 62px/1.12 Nunito;background:#fff;color:#0A0A0A;padding:20px 40px;border-radius:30px;white-space:nowrap;box-shadow:0 10px 30px rgba(10,10,10,.14),0 0 0 2px rgba(10,10,10,.06)}}
.s{{color:#333}} .g{{color:#8F6E2A}} .big{{font-size:130px;padding:28px 70px}}
.q{{position:absolute;left:50%;transform:translateX(-50%);width:900px;font:600 54px/1.3 Lora;font-style:italic;background:rgba(255,253,247,.96);color:#2a2116;padding:30px 44px;border-radius:28px;text-align:center;box-shadow:0 10px 30px rgba(10,10,10,.16)}}
.ref{{display:block;font:800 36px Nunito;font-style:normal;color:#8F6E2A;margin-top:14px}}
.line{{position:absolute;left:340px;width:400px;height:8px;border-radius:5px;background:linear-gradient(90deg,#C9A24B,#8F6E2A)}}
#sub{{position:absolute;left:40px;width:1000px;top:1480px;height:170px;display:flex;align-items:center;justify-content:center;text-align:center}}
#sub span.box{{font:800 70px/1.12 Nunito;color:#0A0A0A;background:rgba(255,255,255,.88);padding:12px 26px;border-radius:24px}}
.w{{display:inline-block;margin:0 .1em}} .w.on{{color:#A67C1E}}"""
HT={'hook':"<div class=p style='top:200px'>« Pourquoi tu restes ? »</div><div class='p s' style='top:340px'>Sa réponse a fait taire</div><div class='p s' style='top:470px'>tout le monde</div><div class=line style='top:610px'></div>",
 'ret':"<div class=p style='top:220px'>Elle n'a pas parlé de lui</div>",
 'q1':"<div class=q style='top:220px'>« Franchement, pourquoi<br>tu restes avec Marc ? »</div>",
 'q2':"<div class=q style='top:200px'>« Je ne reste pas pour lui.<br>Je reste parce que Jésus m'a appris<br>à aimer, même quand c'est difficile.&nbsp;»</div>",
 'q3':"<div class=q style='top:240px'>« L'amour supporte tout,<br>il espère tout. »<span class=ref>1 Corinthiens 13:7</span></div>",
 'cta':"<div class='p g big' style='top:240px'>Dis amen</div><div class='p s' style='top:500px'>et abonne-toi</div>"}
chunks=[]; i=0
while i<len(words):
    j=min(len(words),i+3)
    for k in range(i,j):
        if re.search(r'[.!?,:…»]$',words[k]): j=k+1; break
    chunks.append((i,j)); i=j
async def render_texts():
    async with async_playwright() as p:
        b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':WW,'height':HH})
        async def shot(html,path,clip=None):
            open('ov.html','w').write('<meta charset=utf-8><style>'+CSS+'</style>'+html)
            await pg.goto('file://'+os.path.abspath('ov.html')); await pg.evaluate('document.fonts.ready'); await pg.wait_for_timeout(250)
            await pg.screenshot(path=path,omit_background=True,**({'clip':clip} if clip else {}))
        for k,h in HT.items(): await shot(h,f'ov_{k}.png')
        for a_,b_ in chunks:
            for cur in range(a_,b_):
                ws=''.join(f"<span class='w{' on' if k==cur else ''}'>{words[k]}</span>" for k in range(a_,b_))
                await shot(f"<div id=sub><span class=box>{ws}</span></div>",f'sub_{cur}.png',{'x':0,'y':1460,'width':1080,'height':210})
        await b.close()
asyncio.run(render_texts())
OVI={k:Image.open(f'ov_{k}.png').convert('RGBA') for k in HT}
SUB={k:Image.open(f'sub_{k}.png').convert('RGBA') for k in range(len(words))}
def spring(x): return 0 if x<=0 else 1-math.exp(-x*9)*math.cos(x*13)
def overlay(fr,im,a_,b_,t):
    k=spring((t-a_)/0.5) if t-a_<1 else 1; al=min(1,(t-a_)/0.12)*min(1,max(0,(b_-t)/0.18))
    if a_==0: k=1; al=min(1,max(0,(b_-t)/0.18))
    o=Image.new('RGBA',(WW,HH),(0,0,0,0)); o.paste(im,(0,int((1-k)*50)))
    if al<1: o.putalpha(o.getchannel('A').point(lambda v:int(v*al)))
    fr.alpha_composite(o)
XF=0.16
p=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{WW}x{HH}','-r',str(FPS),'-i','-','-i',AUD,'-c:v','libx264','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-shortest','reel_claire.mp4'],stdin=subprocess.PIPE)
for i in range(N):
    t=i/FPS; si=max(k for k,s in enumerate(SC) if t>=s[0]); fr=src_frame(SC[si],t).copy()
    if si>0 and t-SC[si][0]<XF: fr=Image.blend(src_frame(SC[si-1],t),fr,(t-SC[si][0])/XF)
    for k,a_,b_ in OV:
        if a_<=t<b_: overlay(fr,OVI[k],a_,b_,t)
    cw=max([k for k,(s,e) in enumerate(wt) if t>=s-0.02],default=None)
    if cw is not None and t<wt[-1][1]+0.5: fr.alpha_composite(SUB[cw],(0,1460))
    p.stdin.write(fr.convert('RGB').tobytes())
p.stdin.close(); p.wait(); print('ok',round(dur,2),N)
