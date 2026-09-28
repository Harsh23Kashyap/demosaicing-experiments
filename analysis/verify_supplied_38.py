"""Recompute the historical quality/descriptor table on supplied images only.

Never substitute this subset for an independent reconstruction of Kodak or McMaster.
"""
import csv,sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'source'))
import pipeline
from final80_variant_original import dem_alleysson_final,artifact

METHODS={**pipeline.METHODS,'alleysson':dem_alleysson_final}

def main():
    root=Path(sys.argv[1] if len(sys.argv)>1 else 'images')
    original={r['image_id']:r for r in csv.DictReader(open('source/combined_metrics_descriptors_80_original.csv'))}
    keys=[k for k in original if k.startswith(('bsd100/','urban100/'))]
    if len(keys)!=38: raise ValueError(len(keys))
    report=[]
    for key in keys:
        p=root/key
        if not p.is_file(): raise FileNotFoundError(p)
        x=pipeline.load_rgb8(p)
        lin=pipeline.srgb_to_linear(x); m=pipeline.mosaic_rggb(lin)
        ref=pipeline.to_srgb8(lin)
        actual=pipeline.descriptors(x)
        for method,fn in METHODS.items():
            est=pipeline.to_srgb8(np.clip(fn(m),0,None))
            for metric,value in zip(('psnr','ssim','delta_e','edge_preservation'),pipeline.metrics(ref,est)):
                actual[f'{method}_{metric}']=value
            actual[f'{method}_artifact_score']=artifact(ref,est)
        for name,value in actual.items():
            old=float(original[key][name]); err=abs(value-old)
            report.append({'image_id':key,'column':name,'historical':old,
                           'recomputed':float(value),'absolute_error':float(err)})
        print(key,flush=True)
    with open('results/verification_38_quality_descriptors.csv','w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=report[0].keys());w.writeheader();w.writerows(report)
    print('Verified',len(keys),'images,',len(report),'numeric cells; largest absolute errors:')
    for r in sorted(report,key=lambda r:r['absolute_error'],reverse=True)[:12]:print(r)
    assert max(r['absolute_error'] for r in report)<1e-5,'Mismatch with historical table'
if __name__=='__main__':main()
