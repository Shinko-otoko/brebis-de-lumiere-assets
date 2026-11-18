# Reel histoire : decors + sprites animes + textes par partie (piste 2) + sous-titres cales sur la voix (piste 3).
import json, math, os, re, asyncio, subprocess, glob, sys
import numpy as np
from PIL import Image
from playwright.async_api import async_playwright
R='/home/claude/histoire-marc'; OUT=R+'/reel'; os.chdir(OUT)
FPS=25; WW,HH=1080,1920; AUD=R+'/voix/talk.wav'; FONTS='file:///home/claude/dl_assets/repo/fonts/'
WJ=json.load(open(R+'/voix/words_snap.json')); words=[x['w'] for x in WJ]; wt=[(x['s'],x['e']) for x in WJ]
dur=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',AUD])); N=int(dur*FPS)+1
def W0(prefix,after=0.0): return next(wt[k][0] for k,x in enumerate(words) if x.startswith(prefix) and wt[k][0]>=after)
# ---------------- assets
def decor(name):
    im=Image.open(f'{R}/bibliotheque/decors/{name}.png').convert('RGB'); h=round(im.height*WW/im.width); im=im.resize((WW,h),Image.LANCZOS)
    y=(h-HH)//2; return im.crop((0,y,WW,y+HH))
DEC={k:decor(k) for k in ['D1_bureau','D2_couloir','D3_chambre_nuit','D4_chambre_leo','D5_bible']}
SPR={}
def sprite(name):
    if name not in SPR:
        fs=sorted(glob.glob(f'{R}/bibliotheque/sprites/{name}/[0-9]*.*')); SPR[name]=[Image.open(f).convert('RGBA') for f in fs]
    return SPR[name]
RS={}
def scaled(name,k,h):
    key=(name,k,h)
    if key not in RS:
        im=sprite(name)[k]; RS[key]=im.resize((max(1,round(im.width*h/im.height)),h),Image.LANCZOS)
    return RS[key]
# ---------------- plan (temps recales sur les mots prononces)
T=lambda p,after=0.0: W0(p,after)-0.15
t_ret=T('Et'); t_soir=T('Un'); t_fils=T('Son'); t_femme=T('Et',12); t_fige=T('Marc',16); t_nuit=T('Cette'); t_verset=T('Et',27)
t_lend=T('Le',36); t_porte=T('Il',39); t_cta=W0('Si',42)
L=lambda name,x,feet,h,mode='loop',t0=0.0,speed=1.0,frame=None: dict(name=name,x=x,feet=feet,h=h,mode=mode,t0=t0,speed=speed,frame=frame)
SC=[
 dict(a=0,b=t_ret,dec='D1_bureau',z=(1.0,1.05),cx=540,cy=1050,lay=[L('A1_marc_tape',560,1520,1000)]),
 dict(a=t_ret,b=t_soir,dec='D4_chambre_leo',z=(1.04,1.12),cx=540,cy=1150,lay=[L('A6_marc_leo_calin',560,1560,820,mode='hold',frame=-1)]),
 dict(a=t_soir,b=t_fils,dec='D1_bureau',z=(1.0,1.03),cx=540,cy=1050,lay=[L('A1_marc_tape',560,1520,1000,t0=1.3)]),
 dict(a=t_fils,b=t_femme,dec='D2_couloir',z=(1.0,1.03),cx=540,cy=1150,lay=[L('A2_leo_frappe',300,1600,560)]),
 dict(a=t_femme,b=t_fige,dec='D2_couloir',z=(1.0,1.04),cx=500,cy=1150,lay=[L('A3_claire_parle',250,1640,960),L('A2_leo_frappe',560,1600,560,mode='hold',frame=0)]),
 dict(a=t_fige,b=t_nuit,dec='D1_bureau',z=(1.0,1.22),cx=560,cy=900,lay=[L('A1_marc_tape',560,1520,1000,mode='hold',frame=0)]),
 dict(a=t_nuit,b=t_verset,dec='D3_chambre_nuit',z=(1.0,1.05),cx=540,cy=1200,lay=[L('A4_marc_prie',400,1620,760)]),
 dict(a=t_verset,b=t_lend,dec='D5_bible',z=(1.0,1.12),cx=560,cy=900,lay=[]),
 dict(a=t_lend,b=t_porte,dec='D1_bureau',z=(1.02,1.04),cx=540,cy=1050,lay=[L('A5_marc_ferme',560,1520,1000,mode='once',t0=1.4,speed=1.2)]),
 dict(a=t_porte,b=dur+1,dec='D4_chambre_leo',z=(1.0,1.06),cx=540,cy=1150,lay=[L('A6_marc_leo_calin',560,1560,820,mode='once')]),
]
OV=[('hook',0,t_ret-.05),('ret',t_ret+.1,t_soir-.1),('q_papa',W0('«',14),t_fige-.1),('fige1',W0('Il',18),t_nuit-.1),('fige2',W0('et',20),t_nuit-.1),
    ('q_seigneur',W0('«',24),t_verset-.1),('v1',W0('«',29),t_lend-.1),('v2',W0('Il',32.5),t_lend-.1),('q_tu',W0('«',41),t_cta-.1),('cta',t_cta+.05,dur+1)]
# ---------------- textes (rendus une fois en PNG transparents)
CSS=f"""@font-face{{font-family:Nunito;font-weight:900;src:url({FONTS}nunito-sans-latin-900-normal.woff2)}}
@font-face{{font-family:Nunito;font-weight:800;src:url({FONTS}nunito-sans-latin-800-normal.woff2)}}
@font-face{{font-family:Lora;font-weight:600;src:url({FONTS}lora-latin-600-normal.woff2)}}
html,body{{margin:0;background:transparent;width:1080px;height:1920px;position:relative}}
.p{{position:absolute;left:50%;transform:translateX(-50%);font:900 64px/1.12 Nunito;background:#fff;color:#0A0A0A;padding:20px 40px;border-radius:30px;white-space:nowrap;box-shadow:0 10px 30px rgba(10,10,10,.14),0 0 0 2px rgba(10,10,10,.06)}}
.s{{color:#333}} .g{{color:#8F6E2A}} .big{{font-size:132px;padding:28px 70px}}
.q{{position:absolute;left:50%;transform:translateX(-50%);width:880px;font:600 54px/1.3 Lora;font-style:italic;background:rgba(255,253,247,.96);color:#2a2116;padding:30px 44px;border-radius:28px;text-align:center;box-shadow:0 10px 30px rgba(10,10,10,.16)}}
.ref{{display:block;font:800 36px Nunito;font-style:normal;color:#8F6E2A;margin-top:14px}}
.line{{position:absolute;left:340px;width:400px;height:8px;border-radius:5px;background:linear-gradient(90deg,#C9A24B,#8F6E2A)}}
#sub{{position:absolute;left:40px;width:1000px;top:1480px;height:170px;display:flex;align-items:center;justify-content:center;text-align:center}}
#sub span.box{{font:800 70px/1.12 Nunito;color:#0A0A0A;background:rgba(255,255,255,.88);padding:12px 26px;border-radius:24px}}
.w{{display:inline-block;margin:0 .1em}} .w.on{{color:#A67C1E}}"""
HT={'hook':"<div class=p style='top:300px'>4 mots de sa femme</div><div class='p s' style='top:440px'>ont tout brisé en lui</div><div class=line style='top:575px'></div>",
 'ret':"<div class=p style='top:300px'>Jésus a recollé</div><div class='p s' style='top:440px'>les morceaux</div>",
 'q_papa':"<div class=q style='top:300px'>« Ne dérange pas papa. »</div>",
 'fige1':"<div class=p style='top:280px'>Il fait tout pour eux…</div>",
 'fige2':"<div class='p g' style='top:420px'>et il est en train de les perdre.</div>",
 'q_seigneur':"<div class=q style='top:300px'>« Seigneur, je ne sais plus<br>comment être là. »</div>",
 'v1':"<div class=q style='top:250px'>« En vain vous levez-vous matin,<br>vous couchez-vous tard… »</div>",
 'v2':"<div class=q style='top:520px'>« Il en donne autant à ses bien&#8209;aimés<br>pendant leur sommeil. »<span class=ref>Psaume 127:2</span></div>",
 'q_tu':"<div class=q style='top:300px'>« Tu voulais me montrer quoi ? »</div>",
 'cta':"<div class='p g big' style='top:260px'>Dis amen</div><div class='p s' style='top:520px'>et abonne-toi</div>"}
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
chunk_of={k:(a_,b_) for a_,b_ in chunks for k in range(a_,b_)}
ss=lambda x: (lambda y: y*y*(3-2*y))(max(0,min(1,x)))
def spring(x): return 0 if x<=0 else 1-math.exp(-x*9)*math.cos(x*13)
def scene_frame(sc,t):
    fr=DEC[sc['dec']].copy().convert('RGBA'); u=(t-sc['a'])
    for ly in sc['lay']:
        seq=sprite(ly['name']); n=len(seq)
        if ly['mode']=='hold': k=ly['frame']%n
        else:
            f=int((ly['t0']+u*ly['speed'])*FPS)
            k=f%n if ly['mode']=='loop' else min(f,n-1)
        im=scaled(ly['name'],k,ly['h']); fr.alpha_composite(im,(int(ly['x']-im.width/2),int(ly['feet']-im.height)))
    z0,z1=sc['z']; z=z0+(z1-z0)*ss(u/max(.1,sc['b']-sc['a']))
    if abs(z-1)>1e-3:
        cw,ch=WW/z,HH/z; x0=min(max(sc['cx']-cw/2,0),WW-cw); y0=min(max(sc['cy']-ch/2,0),HH-ch)
        fr=fr.transform((WW,HH),Image.EXTENT,(x0,y0,x0+cw,y0+ch),Image.BICUBIC)
    return fr
def overlay(fr,im,a_,b_,t):
    k=spring((t-a_)/0.5) if t-a_<1 else 1; al=min(1,(t-a_)/0.12)*min(1,max(0,(b_-t)/0.18))
    if a_==0: k=1; al=min(1,max(0,(b_-t)/0.18))   # hook visible des la 1re image (couverture, lecture sans le son)
    o=Image.new('RGBA',(WW,HH),(0,0,0,0)); o.paste(im,(0,int((1-k)*50)))
    if al<1: o.putalpha(o.getchannel('A').point(lambda v:int(v*al)))
    fr.alpha_composite(o)
XF=0.16
p=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{WW}x{HH}','-r',str(FPS),'-i','-','-i',AUD,'-c:v','libx264','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-shortest','reel_histoire.mp4'],stdin=subprocess.PIPE)
for i in range(N):
    t=i/FPS; si=max(k for k,s in enumerate(SC) if t>=s['a']) ; sc=SC[si]; fr=scene_frame(sc,t)
    if si>0 and t-sc['a']<XF: fr=Image.blend(scene_frame(SC[si-1],t),fr,(t-sc['a'])/XF)   # fondu tres court entre les plans
    for k,a_,b_ in OV:
        if a_<=t<b_: overlay(fr,OVI[k],a_,b_,t)
    cw=max([k for k,(s,e) in enumerate(wt) if t>=s-0.02],default=None)
    if cw is not None and t<wt[-1][1]+0.5: fr.alpha_composite(SUB[cw],(0,1460))
    p.stdin.write(fr.convert('RGB').tobytes())
p.stdin.close(); p.wait(); print('ok',round(dur,2),'s',N,'images')
