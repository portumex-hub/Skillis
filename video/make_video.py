import subprocess, numpy as np, wave, os, sys
P,C,OUT=sys.argv[1:4]; M=P+'/media/ppt/media/'
os.makedirs(OUT+'/clips',exist_ok=True); W,H,FPS=1920,1080,30
def run(c): subprocess.run(c,check=True)
seq=[('logo',M+'image-1-2.jpg',3.5)]
for n in ['flat','ig1','ig5','ig2','ig3','ig4','costra','combo']: seq.append(('card',f'{C}/{n}.png',3.6))
for f in ['image-8-2.jpg','image-8-4.jpg','image-8-1.jpg']: seq.append(('photo',M+f,3.0))
dense={5,6,7,9,10,11,13,14,16,19,21}
for s in range(1,22):
    seq.append(('slide',f'{P}/hd-{s:02d}.png',8 if s in dense else 6))
    if s==4: seq += [('photo',M+'image-4-2.jpg',3),('photo',M+'image-4-1.jpg',3)]
    if s==18: seq += [('photo',M+'image-1-1.jpg',3)]
seq.append(('logo',M+'image-1-2.jpg',5))
F=0.35; clips=[]
for n,(k,f,d) in enumerate(seq):
    o=f'{OUT}/clips/{n:03d}.mp4'; fr=int(d*FPS)
    fade=f'fade=t=in:st=0:d={F},fade=t=out:st={d-F}:d={F}'
    if k=='slide': vf=f'scale={W}:{H},{fade}'
    elif k=='logo': vf=f'scale=-2:600,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:color=0x5A9E32,{fade}'
    else:
        pre='scale=2400:-2,crop=2400:1350,' if k=='photo' else 'scale=2400:1350,'
        vf=pre+f"zoompan=z='1+0.07*on/{fr}':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d=1:s={W}x{H}:fps={FPS},{fade}"
    run(['ffmpeg','-v','error','-y','-loop','1','-i',f,'-t',str(d),'-r',str(FPS),'-vf',vf,'-c:v','libx264','-preset','veryfast','-crf','20','-pix_fmt','yuv420p',o])
    clips.append(o)
total=sum(x[2] for x in seq); print('dur',total)
open(f'{OUT}/list.txt','w').write(''.join(f"file '{c}'\n" for c in clips))
# ---- Música: indie/alt-pop alegre, 124 BPM, Re mayor, I-V-vi-IV ----
sr=44100; bpm=124; b=60/bpm; N=int((total+2)*sr); L=np.zeros(N); R=np.zeros(N)
rng=np.random.default_rng(3)
f=lambda m:440*2**((m-69)/12)
def add(sig,t,g,pan=0.0):
    i=int(t*sr); j=min(N,i+len(sig))
    if i>=N: return
    L[i:j]+=g*(1-max(pan,0))*sig[:j-i]; R[i:j]+=g*(1+min(pan,0))*sig[:j-i]
def env(n,a=0.005,dec=8.0):
    t=np.arange(n)/sr; e=np.exp(-dec*t); k=int(a*sr); e[:k]*=np.linspace(0,1,k); return e
def lp(x,a):  # one-pole lowpass
    y=np.empty_like(x); s=0.0
    for i,v in enumerate(x): s+=a*(v-s); y[i]=s
    return y
cache={}
def saw(m,dur,dec,det=0.12,cut=0.18):
    key=('s',m,dur,dec)
    if key in cache: return cache[key]
    n=int(dur*sr); t=np.arange(n)/sr; x=np.zeros(n)
    for dv in (-det,0,det):
        ph=(t*f(m+dv))%1; x+=2*ph-1
    x=lp(x/3,cut)*env(n,0.004,dec); cache[key]=x; return x
def pluck(m,dur):  # guitarra limpia brillante (Karplus-Strong)
    key=('p',m,dur)
    if key in cache: return cache[key]
    n=int(dur*sr); p=int(sr/f(m)); buf=rng.uniform(-1,1,p); out=np.zeros(n)
    for i in range(n): out[i]=buf[i%p]; buf[i%p]=0.997*0.5*(buf[i%p]+buf[(i+1)%p])
    cache[key]=out; return out
def kick():
    n=int(.25*sr); t=np.arange(n)/sr; fr=50+110*np.exp(-t*30)
    return np.sin(2*np.pi*np.cumsum(fr)/sr)*np.exp(-t*12)
def snare():
    n=int(.2*sr); t=np.arange(n)/sr
    return (0.6*rng.uniform(-1,1,n)*np.exp(-t*22)+0.4*np.sin(2*np.pi*190*t)*np.exp(-t*30))
def hat(o=False):
    n=int((.18 if o else .04)*sr); x=rng.uniform(-1,1,n); x=x-lp(x,0.5); return x*np.exp(-np.arange(n)/sr*(14 if o else 90))
def clap():
    n=int(.15*sr); x=rng.uniform(-1,1,n); e=np.zeros(n)
    for d in (0,.01,.02): k=int(d*sr); e[k:]+=np.exp(-np.arange(n-k)/sr*35)
    return x*e*0.5
K,S,HC,HO,CL=kick(),snare(),hat(),hat(True),clap()
prog=[(62,'D',[62,66,69]),(57,'A',[61,64,69]),(59,'Bm',[62,66,71]),(55,'G',[62,67,71])]
riff=[0,2,4,2, 7,4,2,4]  # índices de escala Re mayor para el arpegio/hook
scale=[62,64,66,67,69,71,73,74,76,78,79,81]
bar=0; t=0.0; intro=4; total_bars=int(total/(4*b))+1
while t<total:
    root,_,ch=prog[bar%4]; full = intro<=bar<total_bars-2
    for be in range(4):
        tb=t+be*b
        if bar>=2: add(K,tb,0.85)
        if bar>=2 and be in (1,3): add(S,tb,0.45); add(CL,tb,0.35,0.2)
        for e8 in range(2):
            te=tb+e8*b/2
            add(HC if e8==0 else HO,te,0.10 if e8==0 else 0.07,-0.3)
            # bajo en corcheas (indie driving)
            add(saw(root-24,b/2*0.95,6,0.05,0.08),te,0.55)
            # guitarra rítmica en contratiempo
            if e8==1 and bar>=1:
                for k,m in enumerate(ch): add(pluck(m,b*0.6),te+k*0.008,0.14,-0.5)
        # pad brillante
        if be==0 and full:
            for m in ch: add(saw(m+12,4*b,0.6,0.15,0.06),tb,0.07,0.4)
    # hook melódico (sintetizador tipo lead) en compases pares
    if full:
        for i,ix in enumerate(riff):
            m=scale[(ix+[0,4,5,3][bar%4])%len(scale)]+12
            add(saw(m,b*0.45,7,0.08,0.25),t+i*b/2,0.11,0.3)
    t+=4*b; bar+=1
n=int(total*sr); mix=np.stack([L[:n],R[:n]],1)
fi,fo=int(1*sr),int(3*sr); g=np.ones(n); g[:fi]=np.linspace(0,1,fi); g[-fo:]=np.linspace(1,0,fo)
mix*=g[:,None]; mix=np.tanh(1.6*mix/np.max(np.abs(mix)))*0.9
with wave.open(f'{OUT}/music.wav','wb') as w:
    w.setnchannels(2);w.setsampwidth(2);w.setframerate(sr);w.writeframes((mix*32767).astype(np.int16).tobytes())
