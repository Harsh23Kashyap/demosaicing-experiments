"""Benchmark six reconstructed methods on the exact 38-image supplied subset.

Each method gets one warm-up and three timed executions on each image. Captures
machine and library metadata. Runs sequentially to avoid local contention.
"""
import argparse,csv,json,os,platform,sys,time
from pathlib import Path
import numpy as np,scipy,PIL,skimage,colour_demosaicing
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'source'))
import pipeline
from final80_variant_original import dem_alleysson_final

METHODS=dict(pipeline.METHODS)
METHODS['alleysson']=dem_alleysson_final

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--image-root',type=Path,default=Path('images'))
    ap.add_argument('--output',type=Path,default=Path('results/runtime_38_new_run.csv'))
    ap.add_argument('--environment',type=Path,default=Path('results/runtime_environment.json'))
    args=ap.parse_args()
    images=sorted((args.image_root/'bsd100').glob('*.png'))+sorted((args.image_root/'urban100').glob('*.png'))
    if len(images)!=38:raise ValueError(f'Expected exact 38 images, got {len(images)}')
    env={'run_utc':__import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat(),
         'uname':platform.uname()._asdict(),'python':sys.version,
         'cpu_model':next((line.split(':',1)[1].strip() for line in Path('/proc/cpuinfo').read_text().splitlines() if line.startswith('model name')),'unknown'),
         'cpu_count_reported':os.cpu_count(), 'versions':{'numpy':np.__version__,'scipy':scipy.__version__,'Pillow':PIL.__version__,
         'scikit-image':skimage.__version__,'colour-demosaicing':colour_demosaicing.__version__},
         'timing':'perf_counter_ns, one untimed warm-up then three timed calls; median per image-method; medians across images',
         'image_count':len(images),'methods':list(METHODS)}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.environment.write_text(json.dumps(env,indent=2)+'\n')
    rows=[]
    for path in images:
        x=pipeline.load_rgb8(path)
        m=pipeline.mosaic_rggb(pipeline.srgb_to_linear(x))
        for name,fn in METHODS.items():
            fn(m)
            samples=[]
            for _ in range(3):
                t=time.perf_counter_ns();out=fn(m);samples.append((time.perf_counter_ns()-t)/1e6)
                if out.shape!=x.shape or not np.isfinite(out).all():raise ValueError((path,name,'invalid output'))
            rows.append({'image_id':f'{path.parent.name}/{path.name}','method':name,
                        'height':m.shape[0],'width':m.shape[1],
                        'sample_1_ms':samples[0],'sample_2_ms':samples[1],'sample_3_ms':samples[2],
                        'within_pair_median_ms':float(np.median(samples))})
        print(path,flush=True)
    with args.output.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
    print('Across-image medians (ms):')
    for name in METHODS:
        a=[r['within_pair_median_ms'] for r in rows if r['method']==name]
        print(name,round(float(np.median(a)),5))

if __name__=='__main__':main()
