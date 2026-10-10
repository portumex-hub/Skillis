import subprocess, numpy as np, wave, os, sys
P=sys.argv[1]; IMG=sys.argv[2]; OUT=sys.argv[3]
M=P+'/media/ppt/media/'
os.makedirs(OUT+'/clips',exist_ok=True)
W,H,FPS=1920,1080,30
def run(c): subprocess.run(c,check=True)
# (tipo, archivo, segundos, texto)
seq=[('logo',M+'image-1-2.jpg',4)]
for i in range(1,6): seq.append(('vert',f'{IMG}/{i}.jpg',3.2))
for f in ['image-3-2.jpg','image-3-1.jpg','image-2-1.jpg','image-3-3.jpg']: seq.append(('vert',M+f,3.2))
for f in ['image-8-2.jpg','image-8-4.jpg','image-8-1.jpg']: seq.append(('photo',M+f,3.2))
dense={5,6,7,9,10,11,13,14,16,19,21}
for s in range(1,22):
    seq.append(('slide',f'{P}/hd-{s:02d}.png',8 if s in dense else 6))
    if s==4: seq += [('photo',M+'image-4-2.jpg',3),('photo',M+'image-4-1.jpg',3)]
    if s==18: seq += [('photo',M+'image-1-1.jpg',3)]
seq.append(('logo',M+'image-1-2.jpg',5))
F=0.4; clips=[]
for n,(k,f,d) in enumerate(seq):
    o=f'{OUT}/clips/{n:03d}.mp4'; fr=int(d*FPS)
    fade=f'fade=t=in:st=0:d={F},fade=t=out:st={d-F}:d={F}'
    if k=='slide':
        vf=f'scale={W}:{H},{fade}'
    elif k=='logo':
        vf=f'scale=-2:600,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:color=0x5A9E32,{fade}'
    elif k=='photo':
        vf=(f'scale=2400:-2,crop=2400:1350,zoompan=z=\'1+0.10*on/{fr}\':x=\'iw/2-iw/zoom/2\':y=\'ih/2-ih/zoom/2\':d=1:s={W}x{H}:fps={FPS},{fade}')
    else: # vertical: fondo desenfocado + foto al centro
        vf=(f'split[a][b];[a]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},boxblur=30:3,eq=brightness=-0.15[bg];'
            f'[b]scale=-2:1000[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2,'
            f'zoompan=z=\'1+0.06*on/{fr}\':x=\'iw/2-iw/zoom/2\':y=\'ih/2-ih/zoom/2\':d=1:s={W}x{H}:fps={FPS},{fade}')
    run(['ffmpeg','-v','error','-y','-loop','1','-i',f,'-t',str(d),'-r',str(FPS),'-filter_complex' if k=='vert' else '-vf',vf,
         '-c:v','libx264','-preset','veryfast','-crf','20','-pix_fmt','yuv420p',o])
    clips.append(o)
total=sum(d for *_,d in seq); print('dur',total)
open(f'{OUT}/list.txt','w').write(''.join(f"file '{c}'\n" for c in clips))
# ---------- Música sintetizada (A mayor, 104 BPM, estilo huapango/norteño ligero) ----------
sr=44100; bpm=104; beat=60/bpm; N=int((total+1)*sr); mix=np.zeros(N)
rng=np.random.default_rng(7)
def ks(freq,dur,dec=0.996):
    n=int(dur*sr); p=int(sr/freq); buf=rng.uniform(-1,1,p); out=np.zeros(n)
    for i in range(n):
        out[i]=buf[i%p]; buf[i%p]=dec*0.5*(buf[i%p]+buf[(i+1)%p])
    return out
def add(sig,t,g):
    i=int(t*sr); j=min(N,i+len(sig))
    if i<N: mix[i:j]+=g*sig[:j-i]
note=lambda m:440*2**((m-69)/12)
chords={'A':[57,61,64,69],'D':[57,62,66,69],'E':[56,59,64,68],'F#m':[57,61,66,69]}
roots={'A':45,'D':38,'E':40,'F#m':42}
prog=['A','A','D','E','A','F#m','D','E']
cache={}
def pluck(m,d):
    k=(m,d)
    if k not in cache: cache[k]=ks(note(m),d)
    return cache[k]
kick=np.sin(2*np.pi*np.cumsum(np.linspace(120,45,int(.18*sr)))/sr)*np.exp(-np.linspace(0,8,int(.18*sr)))
shk=rng.uniform(-1,1,int(.05*sr))*np.exp(-np.linspace(0,10,int(.05*sr)))
t=0; bar=0
while t<total:
    c=prog[bar%len(prog)]
    for b in range(4):
        tb=t+b*beat
        add(kick,tb,0.5 if b in (0,2) else 0.25)
        add(pluck(roots[c]+(0 if b%2==0 else 7),beat*1.5),tb,0.45)  # bajo alternado (tonica-quinta)
        for s8 in (0,0.5):
            add(shk,tb+s8*beat,0.12 if s8 else 0.07)
            # rasgueo: arriba/abajo con micro-desfase
            ns=chords[c] if s8==0 else chords[c][::-1]
            for k,m in enumerate(ns): add(pluck(m+12,beat*0.9),tb+s8*beat+k*0.012,0.16 if s8==0 else 0.10)
        # melodía simple de requinto cada 2 barras
        if bar%2==1 and b in (1,3): add(pluck(chords[c][2]+24,beat),tb+beat*0.25,0.12)
    t+=4*beat; bar+=1
mix=mix[:int(total*sr)]
env=np.ones_like(mix); fi=int(1.5*sr); fo=int(3*sr)
env[:fi]=np.linspace(0,1,fi); env[-fo:]=np.linspace(1,0,fo)
mix=mix*env; mix=np.tanh(1.3*mix/np.max(np.abs(mix)))*0.85
st=np.stack([mix,np.roll(mix,int(.011*sr))*0.9],1)
with wave.open(f'{OUT}/music.wav','wb') as w:
    w.setnchannels(2);w.setsampwidth(2);w.setframerate(sr);w.writeframes((st*32767).astype(np.int16).tobytes())
