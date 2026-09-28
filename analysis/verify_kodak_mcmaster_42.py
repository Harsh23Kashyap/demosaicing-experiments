"""Private replay of 24 Kodak and 18 McMaster source images.

Download from official/public distributor pages cited in the README. Input
images must remain outside the repo. This code saves ONLY numeric comparisons
and source-file hashes, not raw images. Hashes describe this download and do
not prove which bytes were used in the original experiment.
"""
import argparse,csv,hashlib,sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'source'))
import pipeline
from final80_variant_original import dem_alleysson_final,artifact
METHODS={**pipeline.METHODS,'alleysson':dem_alleysson_final}
p=argparse.ArgumentParser();p.add_argument('--kodak-dir',type=Path,required=True);p.add_argument('--mcm-dir',type=Path,required=True);p.add_argument('--output',type=Path,default=Path('results/verification_kodak_mcm_42.csv'));p.add_argument('--dataset',choices=['kodak','mcm','both'],default='both');p.add_argument('--start',type=int,default=1);p.add_argument('--end',type=int,default=24);a=p.parse_args()
original={r['image_id']:r for r in csv.DictReader(open('source/combined_metrics_descriptors_80_original.csv'))}
entries=([(f'kodak/kodim{i:02d}.png',a.kodak_dir/f'kodim{i:02d}.png') for i in range(1,25)] if a.dataset in ('both','kodak') else []) + ([(f'mcm/{i}.tif',a.mcm_dir/f'{i}.tif') for i in range(1,19)] if a.dataset in ('both','mcm') else [])
entries=[(key,path) for key,path in entries if a.start <= int(path.stem.removeprefix('kodim')) <= a.end]
report=[];manifest=[]
for key,path in entries:
    if key not in original:raise KeyError(key)
    content=path.read_bytes();sha=hashlib.sha256(content).hexdigest()
    x=pipeline.load_rgb8(path);lin=pipeline.srgb_to_linear(x);m=pipeline.mosaic_rggb(lin);ref=pipeline.to_srgb8(lin)
    actual=pipeline.descriptors(x)
    for method,fn in METHODS.items():
        est=pipeline.to_srgb8(np.clip(fn(m),0,None))
        for metric,value in zip(('psnr','ssim','delta_e','edge_preservation'),pipeline.metrics(ref,est)):
            actual[f'{method}_{metric}']=value
        actual[f'{method}_artifact_score']=artifact(ref,est)
    manifest.append({'image_id':key,'downloaded_sha256':sha,'width':x.shape[1],'height':x.shape[0]})
    for name,value in actual.items():
        old=float(original[key][name]);report.append({'image_id':key,'column':name,'historical':old,'recomputed':float(value),'absolute_error':float(abs(value-old))})
    print(key,'max_abs_error',max(r['absolute_error'] for r in report if r['image_id']==key),flush=True)
a.output.parent.mkdir(parents=True,exist_ok=True)
for path,rows in [(a.output,report),(a.output.with_name('source_hashes_'+a.output.stem+'.csv'),manifest)]:
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
print('Verified',len(entries),'images,',len(report),'numeric cells; max abs error',max(r['absolute_error'] for r in report))
assert max(r['absolute_error'] for r in report)<1e-5
