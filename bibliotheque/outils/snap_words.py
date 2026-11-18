# Recale les mots sur les blocs de voix reels (entre deux pauses), puis repartit les mots dans chaque bloc.
import json, wave, numpy as np, sys
J=json.load(open('words.json')); W=J['words']; LAG=0.3
w=wave.open(sys.argv[1]); sr=w.getframerate(); a=np.frombuffer(w.readframes(w.getnframes()),dtype=np.int16).astype(float)/32768
hop=sr//100; env=np.array([np.sqrt((a[i:i+hop]**2).mean()) for i in range(0,len(a)-hop,hop)]); v=env>0.02
segs=[]; s=None; gap=0
for i,x in enumerate(v):
    if x:
        if s is None: s=i
        gap=0
    elif s is not None:
        gap+=1
        if gap>=20: segs.append((s/100,(i-gap+1)/100)); s=None
if s is not None: segs.append((s/100,len(v)/100))
segs=[g for g in segs if g[1]-g[0]>0.12]
first=max(i for i,x in enumerate(W) if x['s']==W[0]['s'])   # mots de tete non reconnus
def seg_of(t): return min(range(len(segs)),key=lambda k:0 if segs[k][0]-.15<=t<=segs[k][1]+.05 else min(abs(t-segs[k][0]),abs(t-segs[k][1])))
k0=seg_of(W[first]['s']-LAG); assign=[]
for i,x in enumerate(W):
    k=max(0,k0-1) if i<first else seg_of(x['s']-LAG)
    if assign: k=max(k,assign[-1])
    assign.append(k)
out=[]
for k,(s0,s1) in enumerate(segs):
    idx=[i for i,a_ in enumerate(assign) if a_==k]
    if not idx: continue
    L=[len(W[i]['w'])+1 for i in idx]; c=0
    for i,l in zip(idx,L):
        out.append({'w':W[i]['w'],'s':round(s0+(s1-s0)*c/sum(L),2),'e':round(s0+(s1-s0)*(c+l)/sum(L),2)}); c+=l
json.dump(out,open('words_snap.json','w'),ensure_ascii=False)
print(len(segs),'blocs de voix,',len(out),'mots'); print(' '.join(f"{o['w']}@{o['s']}" for o in out))
