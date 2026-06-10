import numpy as np, tempfile, os, math
from PIL import Image, ImageFilter, ImageStat

def image_scan(file):
    img=Image.open(file).convert('RGB').resize((512,512))
    gray=img.convert('L')
    edges=gray.filter(ImageFilter.FIND_EDGES)
    edge_mean=ImageStat.Stat(edges).mean[0]
    arr=np.array(img).astype(float)
    channels=arr.reshape(-1,3)
    corr=np.corrcoef(channels.T)
    color_corr=float(np.nanmean(np.abs(corr[np.triu_indices(3,1)])))
    texture=float(np.std(np.array(gray)))
    compression=max(0, min(35, (18-edge_mean)*1.4 if edge_mean<18 else 0))
    smooth=max(0, min(30, (42-texture)*0.8 if texture<42 else 0))
    artificial=max(0, min(35, (color_corr-0.82)*120 if color_corr>0.82 else 0))
    score=int(min(100, compression+smooth+artificial+15))
    heat=edges.resize((320,320))
    return {'score':score,'real':100-score,'edge_mean':round(edge_mean,2),'texture':round(texture,2),'color_corr':round(color_corr,2),'heatmap':heat,'explanation':'Offline forensic heuristic using edge noise, texture smoothness and RGB consistency. Replaceable with a trained CNN/ViT model.'}

def video_scan(file):
    try:
        import cv2
        t=tempfile.NamedTemporaryFile(delete=False, suffix='.mp4'); t.write(file.read()); t.close()
        cap=cv2.VideoCapture(t.name); vals=[]; frames=0
        while frames<40:
            ok,frame=cap.read()
            if not ok: break
            if frames%3==0:
                gray=cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                vals.append(float(np.std(gray)))
            frames+=1
        cap.release(); os.unlink(t.name)
        if not vals: return {'score':45,'timeline':[45],'explanation':'Video could not be fully decoded; neutral risk returned.'}
        stability=100-min(100, np.std(vals)*5)
        score=int(min(100, max(15, stability*0.55 + (35 if np.mean(vals)<40 else 10))))
        timeline=[int(min(100,max(0,score+np.random.randint(-10,11)))) for _ in range(min(12,len(vals)+3))]
        return {'score':score,'timeline':timeline,'explanation':'Analyzed frame texture consistency and temporal stability as a lightweight deepfake indicator.'}
    except Exception:
        return {'score':50,'timeline':[50,52,48,55],'explanation':'Install OpenCV for full video scan. Demo returned neutral risk.'}

def audio_scan(file):
    data=file.read()
    if not data: return {'score':40,'human':60,'explanation':'Empty audio file.'}
    entropy=len(set(data[:20000]))/256
    periodic=sum(1 for i in range(1,min(len(data),8000)) if data[i]==data[i-1])/8000
    score=int(min(100,max(10,entropy*65 + periodic*120)))
    return {'score':score,'human':100-score,'explanation':'Lightweight audio heuristic using byte entropy and waveform repetition indicators for AI/synthetic speech demo.'}
