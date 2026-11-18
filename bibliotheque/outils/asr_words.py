# Horodatage des mots : reconnaissance vocale (sherpa-onnx, zipformer francais) puis alignement sur le texte connu.
import sys, json, wave, re, unicodedata, difflib, numpy as np, sherpa_onnx
D='/home/claude/reel-p3/sherpa-onnx-streaming-zipformer-fr-2023-04-14/'; E='-epoch-29-avg-9-with-averaged-model.onnx'
wav,text=sys.argv[1],open(sys.argv[2]).read().strip()
r=sherpa_onnx.OnlineRecognizer.from_transducer(tokens=D+'tokens.txt',encoder=D+'encoder'+E,decoder=D+'decoder'+E,joiner=D+'joiner'+E,num_threads=2,sample_rate=16000,feature_dim=80,decoding_method='greedy_search')
w=wave.open(wav); sr=w.getframerate(); a=np.frombuffer(w.readframes(w.getnframes()),dtype=np.int16).astype(np.float32)/32768
s=r.create_stream(); s.accept_waveform(sr,a); s.accept_waveform(sr,np.zeros(int(sr*.8),dtype=np.float32)); s.input_finished()
while r.is_ready(s): r.decode_stream(s)
res=r.get_result_all(s); toks,ts=res.tokens,res.timestamps
# tokens -> mots entendus (un mot commence par '▁' ou un espace)
heard=[]
for tk,t in zip(toks,ts):
    if tk.startswith('▁') or tk.startswith(' ') or not heard: heard.append([tk.lstrip('▁ '),t])
    else: heard[-1][0]+=tk
norm=lambda x: re.sub(r'[^a-z0-9]','',unicodedata.normalize('NFD',x.lower()).encode('ascii','ignore').decode())
# le texte attendu, decoupe comme les sous-titres ; l'elision (c'est, l'argent) reste un seul mot
words=text.split(' '); exp=[norm(x) for x in words]
hs=[]; hi=[]                                   # mots entendus, apostrophes recollees
for h,t in heard:
    n=norm(h)
    if not n: continue
    hs.append(n); hi.append(t)
sm=difflib.SequenceMatcher(None,''.join(e+' ' for e in exp),''.join(h+' ' for h in hs),autojunk=False)
# position caractere -> temps (interpolation entre debuts de mots entendus)
hpos=np.cumsum([0]+[len(h)+1 for h in hs])[:-1]; epos=np.cumsum([0]+[len(e)+1 for e in exp])[:-1]
mp=[(bl.a+k,bl.b+k) for bl in sm.get_matching_blocks() for k in range(bl.size)]
ea=np.array([m[0] for m in mp]); hb=np.array([m[1] for m in mp])
htime=lambda c: float(np.interp(c,hpos,hi))
start=[htime(float(np.interp(p,ea,hb))) for p in epos]
ratio=sm.ratio(); miss=[words[i] for i,e in enumerate(exp) if e and e not in hs]
out=[{'w':words[i],'s':round(start[i],2)} for i in range(len(words))]
for i in range(1,len(out)): out[i]['s']=max(out[i]['s'],out[i-1]['s'])
json.dump({'ratio':round(ratio,3),'heard':' '.join(h for h,_ in heard),'words':out},open('words.json','w'),ensure_ascii=False,indent=0)
print('ressemblance',round(ratio,3)); print('entendu :',' '.join(h for h,_ in heard)); print('mots non reconnus :',miss)
print(' '.join(f"{o['w']}@{o['s']}" for o in out))
