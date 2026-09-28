"""Locked evaluation of one 80-image-trained proxy-saturation tree on Set14.

Model/feature choice follows a 38-image exploratory check; Set14 is not used
to tune it. Only 12 RGB Set14 images are used; grayscale img_003 and Lenna
img_009 are excluded before evaluation. Dataset is from SelfExSR's Set14 HR
mirror and not redistributed. This is an additional SR benchmark, not sensor RAW.
"""
import argparse,csv,hashlib,sys,time
from pathlib import Path
import numpy as np
from PIL import Image
from sklearn.tree import DecisionTreeClassifier,export_text
from sklearn.model_selection import LeaveOneOut
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'source'))
import pipeline

p=argparse.ArgumentParser();p.add_argument('--source80',type=Path,required=True);p.add_argument('--set14',type=Path,required=True);p.add_argument('--output',type=Path,default=Path('results/external_proxy_set14_12.csv'));a=p.parse_args()
source=list(csv.DictReader(open('source/combined_metrics_descriptors_80_original.csv')))
fast=('bilinear','cdiff','malvar')
X=[];y=[];acquire=[]
for row in source:
    key=row['image_id'];path=a.source80/key
    x=pipeline.load_rgb8(path);m=pipeline.mosaic_rggb(pipeline.srgb_to_linear(x))
    t=time.perf_counter_ns();proxy=pipeline.linear_to_srgb(np.clip(pipeline.dem_bilinear(m),0,None));sat=pipeline.descriptors(proxy)['sat_mean']
    acquire.append((time.perf_counter_ns()-t)/1e6);X.append([sat]);y.append(max(fast,key=lambda name:float(row[f'{name}_psnr'])))
X=np.array(X);y=np.array(y)
model=DecisionTreeClassifier(max_depth=2,random_state=42).fit(X,y)
print('Source 80: best-fast counts',{k:int(sum(y==k)) for k in fast},'fitted tree:')
print(export_text(model,feature_names=['proxy_saturation']))
print('Source 80 training accuracy',sum(model.predict(X)==y),'/80; proxy+feature median ms',np.median(acquire))
rows=[]
for path in sorted(a.set14.glob('*_HR.png')):
    if path.name in ('img_003_SRF_2_HR.png','img_009_SRF_2_HR.png'):continue
    im=Image.open(path)
    if im.mode!='RGB':raise ValueError((path,im.mode))
    x=pipeline.load_rgb8(path);lin=pipeline.srgb_to_linear(x);m=pipeline.mosaic_rggb(lin)
    ref=pipeline.to_srgb8(lin)
    t=time.perf_counter_ns();proxy=pipeline.linear_to_srgb(np.clip(pipeline.dem_bilinear(m),0,None));sat=pipeline.descriptors(proxy)['sat_mean'];proxy_ms=(time.perf_counter_ns()-t)/1e6
    score={name:pipeline.metrics(ref,pipeline.to_srgb8(np.clip(pipeline.METHODS[name](m),0,None)))[0] for name in fast}
    best=max(fast,key=lambda name:score[name]);pred=model.predict([[sat]])[0]
    rows.append({'image_id':path.name,'downloaded_sha256':hashlib.sha256(path.read_bytes()).hexdigest(), 'proxy_saturation':sat,
                 'proxy_feature_ms':proxy_ms,'predicted_method':pred,'best_fast_method':best,'malvar_psnr':score['malvar'],
                 'predicted_psnr':score[pred],'best_fast_psnr':score[best],
                 'predicted_regret_db':score[best]-score[pred], 'malvar_regret_db':score[best]-score['malvar']})
    print(path.name,'predicted',pred,'best',best,'proxy_ms',round(proxy_ms,1),flush=True)
a.output.parent.mkdir(exist_ok=True,parents=True)
with a.output.open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
print('External Set14 RGB subset n',len(rows),'predictor correct',sum(x['predicted_method']==x['best_fast_method'] for x in rows),
      'Malvar correct',sum(x['best_fast_method']=='malvar' for x in rows),'mean policy regret',np.mean([x['predicted_regret_db'] for x in rows]),
      'mean Malvar regret',np.mean([x['malvar_regret_db'] for x in rows]),'median proxy+feature ms',np.median([x['proxy_feature_ms'] for x in rows]))
