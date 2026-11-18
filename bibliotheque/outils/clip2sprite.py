# Video (ou image) sur fond creme uni -> sequence de sprites PNG transparents, recadres sur la meme boite.
# usage: python3 clip2sprite.py <video|image> <dossier_sortie> [--fps 25] [--scale 2]
import sys, os, json, subprocess, glob, numpy as np, argparse
from PIL import Image, ImageFilter
from scipy import ndimage as ndi
ap=argparse.ArgumentParser(); ap.add_argument('src'); ap.add_argument('out'); ap.add_argument('--fps',type=int,default=25); ap.add_argument('--scale',type=float,default=2.0); ap.add_argument('--tol',type=float,default=34)
a=ap.parse_args(); os.makedirs(a.out,exist_ok=True); tmp=a.out+'/_raw'; os.makedirs(tmp,exist_ok=True)
if a.src.lower().endswith(('.png','.jpg','.jpeg')): Image.open(a.src).convert('RGB').save(tmp+'/f_0001.png'); fps=a.fps
else:
    subprocess.run(['ffmpeg','-v','error','-y','-i',a.src,'-vf',f'fps={a.fps}',tmp+'/f_%04d.png'],check=True); fps=a.fps
fs=sorted(glob.glob(tmp+'/f_*.png'))
def key(im):
    arr=np.asarray(im).astype(np.int16)
    border=np.concatenate([arr[:6].reshape(-1,3),arr[-6:].reshape(-1,3),arr[:,:6].reshape(-1,3),arr[:,-6:].reshape(-1,3)])
    bg=np.median(border,axis=0)
    d=np.sqrt(((arr-bg)**2).sum(axis=2))
    cand=d<a.tol
    lab,_=ndi.label(cand)
    edge=np.unique(np.concatenate([lab[0],lab[-1],lab[:,0],lab[:,-1]])); edge=edge[edge>0]
    bgm=np.isin(lab,edge)
    fg=~bgm
    fg=ndi.binary_opening(fg,iterations=1)
    # garder les composantes importantes (supprime les petits points de compression)
    l2,n=ndi.label(fg)
    if n>1:
        sz=ndi.sum(fg,l2,range(1,n+1)); keep=np.zeros(n+1,bool); keep[1:]=sz>=max(60,sz.max()*0.002); fg=keep[l2]
    al=(fg*255).astype(np.uint8)
    A=Image.fromarray(al).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(0.9))
    r=im.convert('RGBA'); r.putalpha(A); return r, fg
frames=[]; box=None
for f in fs:
    r,fg=key(Image.open(f).convert('RGB'))
    ys,xs=np.where(fg)
    if len(xs):
        b=[xs.min(),ys.min(),xs.max()+1,ys.max()+1]
        box=b if box is None else [min(box[0],b[0]),min(box[1],b[1]),max(box[2],b[2]),max(box[3],b[3])]
    frames.append(r)
pad=4; W,H=frames[0].size; box=[int(max(0,box[0]-pad)),int(max(0,box[1]-pad)),int(min(W,box[2]+pad)),int(min(H,box[3]+pad))]
for k,r in enumerate(frames):
    c=r.crop(box)
    if a.scale!=1: c=c.resize((round(c.width*a.scale),round(c.height*a.scale)),Image.LANCZOS)
    c.save(f'{a.out}/{k:04d}.png')
for f in fs: os.remove(f)
os.rmdir(tmp)
meta={'frames':len(frames),'fps':fps,'size':[round((box[2]-box[0])*a.scale),round((box[3]-box[1])*a.scale)],'source':os.path.basename(a.src),'source_box':box,'scale':a.scale,'anchor':'bas-centre'}
json.dump(meta,open(a.out+'/sprite.json','w'),indent=1); print(a.out,meta['frames'],'images',meta['size'])
