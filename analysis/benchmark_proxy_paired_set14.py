"""Paired same-machine Set14 component costs; policy proxy is not a validated predictor.

Each image/method has one warmup and three alternating-order measurements; we
report the within-image median and then across-image median. No IO/mosaic time.
Exclude Set14 img_003 because it is grayscale and img_009 (Lenna) before both
classifier evaluation and timing; the same 12 RGB files are used for both.
"""
import csv,sys,time,platform,datetime
from pathlib import Path
import numpy as np
from skimage.color import rgb2hsv
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'source'))
import pipeline

def benchmark(root,out):
    paths=[x for x in sorted(root.glob('*_HR.png')) if x.name not in ('img_003_SRF_2_HR.png','img_009_SRF_2_HR.png')]
    assert len(paths)==12,len(paths)
    rows=[]
    for path in paths:
        x=pipeline.load_rgb8(path);m=pipeline.mosaic_rggb(pipeline.srgb_to_linear(x))
        def proxy():
            rgb=pipeline.linear_to_srgb(np.clip(pipeline.dem_bilinear(m),0,None))
            return float(rgb2hsv(rgb)[...,1].mean())
        fn={'proxy_bilinear_saturation':proxy,'menon':lambda:pipeline.dem_menon(m),
            'malvar':lambda:pipeline.dem_malvar(m),'bilinear':lambda:pipeline.dem_bilinear(m),
            'cdiff':lambda:pipeline.dem_cdiff(m)}
        samples={k:[] for k in fn}
        for f in fn.values():f()
        names=list(fn)
        for repeat in range(3):
            for name in (names if repeat%2==0 else names[::-1]):
                t=time.perf_counter_ns();fn[name]();samples[name].append((time.perf_counter_ns()-t)/1e6)
        for name in names:
            rows.append({'image_id':path.name,'height':m.shape[0],'width':m.shape[1], 'method':name,
                         'median_ms':float(np.median(samples[name])), **{f'sample_{i+1}_ms':v for i,v in enumerate(samples[name])}})
        print(path.name,flush=True)
    out.parent.mkdir(parents=True,exist_ok=True)
    with out.open('w',newline='') as f:
        writer=csv.DictWriter(f,rows[0].keys());writer.writeheader();writer.writerows(rows)
    for name in names:
        print(name,'across-image median',float(np.median([r['median_ms'] for r in rows if r['method']==name])))
    print('machine',platform.uname(),'UTC',datetime.datetime.now(datetime.timezone.utc).isoformat())
if __name__=='__main__':benchmark(Path(sys.argv[1]),Path(sys.argv[2]))
