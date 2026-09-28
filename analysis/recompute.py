"""Recompute final measured-fast comparisons and per-dataset 95% t intervals.

The original 80-row CSV's `best_fast_method` and gain columns belong to an
older tier that included Alleysson. This script never overwrites that source.
"""
import argparse
import csv
from pathlib import Path
import numpy as np
from scipy import stats

FAST = ('bilinear', 'cdiff', 'malvar')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=Path, default=Path('source/combined_metrics_descriptors_80_original.csv'))
    parser.add_argument('--output', type=Path, default=Path('results/final_tier_metrics_80.csv'))
    parser.add_argument('--summary', type=Path, default=Path('results/dataset_gain_t95.csv'))
    args = parser.parse_args()
    with args.input.open(newline='') as f:
        rows = list(csv.DictReader(f))
    if len(rows) != 80 or len({r['image_id'] for r in rows}) != 80:
        raise ValueError('Expected 80 distinct images')
    derived = []
    for row in rows:
        fast = max(FAST, key=lambda m: float(row[f'{m}_psnr']))
        gain = float(row['menon_psnr']) - float(row[f'{fast}_psnr'])
        derived.append({'image_id':row['image_id'], 'dataset':row['dataset'],
                        'best_measured_fast_method':fast,
                        'best_measured_fast_psnr':row[f'{fast}_psnr'],
                        'menon_psnr':row['menon_psnr'],
                        'menon_gain_vs_final_fast_db':f'{gain:.12g}'})
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=derived[0].keys());w.writeheader();w.writerows(derived)
    summary=[]
    for dataset in ('kodak','mcm','bsd100','urban100'):
        a=np.array([float(r['menon_gain_vs_final_fast_db']) for r in derived if r['dataset']==dataset])
        n=len(a); mean=float(np.mean(a)); sem=float(stats.sem(a))
        low,high=stats.t.interval(.95,n-1,loc=mean,scale=sem)
        summary.append({'dataset':dataset,'n':n,'mean_gain_db':f'{mean:.9f}',
                        'ci_method':'two-sided Student t, per-image gain, df=n-1',
                        'ci95_low_db':f'{low:.9f}','ci95_high_db':f'{high:.9f}'})
    with args.summary.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=summary[0].keys());w.writeheader();w.writerows(summary)
    gains=np.array([float(r['menon_gain_vs_final_fast_db']) for r in derived])
    print('Fast-method counts:',{m:sum(r['best_measured_fast_method']==m for r in derived) for m in FAST})
    print('Overall mean:',float(gains.mean()),'nonpositive:',int(sum(gains<=0)))
    print('Paired gain t-test:',stats.ttest_1samp(gains,0))
    for row in summary:print(row)

if __name__=='__main__':main()
