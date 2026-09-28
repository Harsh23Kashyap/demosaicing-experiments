"""Two rights-clean numerical figures from the archived 80-row table.

No benchmark pixels are read or plotted. Source CSV retains older fast labels;
Menon gain here is recalculated against bilinear/cdiff/Malvar PSNR columns.
"""
import csv,argparse
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.stats import pearsonr
p=argparse.ArgumentParser();p.add_argument('--output-dir',type=Path,default=Path('figures'));a=p.parse_args();a.output_dir.mkdir(parents=True,exist_ok=True)
rows=list(csv.DictReader(open('source/combined_metrics_descriptors_80_original.csv')))
assert len(rows)==80 and len({r['image_id'] for r in rows})==80
fast=['bilinear','cdiff','malvar'];datasets=['kodak','mcm','bsd100','urban100']
colours=dict(zip(datasets,['#0072B2','#D55E00','#009E73','#CC79A7']))
labels={'kodak':'Kodak (24)','mcm':'McMaster (18)','bsd100':'BSD100 (20)','urban100':'Urban100 (18)'}
sat=np.array([float(r['sat_mean']) for r in rows])
gain=np.array([float(r['menon_psnr'])-max(float(r[m+'_psnr']) for m in fast) for r in rows])
r,pval=pearsonr(sat,gain)
fig,ax=plt.subplots(figsize=(9.2,5.2),dpi=170)
for d in datasets:
 idx=[i for i,x in enumerate(rows) if x['dataset']==d]
 ax.scatter(sat[idx],gain[idx],s=39,alpha=.82,label=labels[d],color=colours[d],edgecolors='white',linewidths=.35)
ax.axhline(0,color='#343434',lw=1.1);ax.set_xlabel('Mean reference-image HSV saturation (diagnostic only)');ax.set_ylabel('Menon PSNR gain over best measured-fast method (dB)')
ax.text(.015,.965,f'n=80; Pearson r={r:.3f}',transform=ax.transAxes,va='top',fontsize=10)
ax.legend(ncols=2,loc='lower left',frameon=True,fontsize=9)
ax.grid(alpha=.18);ax.set_xlim(0,max(sat)*1.05)
fig.tight_layout();fig.savefig(a.output_dir/'fig_saturation_gain.png');plt.close(fig)

fig,ax=plt.subplots(figsize=(9.2,4.9),dpi=170)
for d in datasets:
 g=np.sort(gain[[i for i,x in enumerate(rows) if x['dataset']==d]])
 y=(np.arange(len(g))+.5)/len(g)
 ax.step(g,y,where='mid',label=labels[d],color=colours[d],linewidth=2)
ax.axvline(0,color='#343434',lw=1.1)
ax.set(xlabel='Menon PSNR gain over best measured-fast method (dB)',ylabel='Within-dataset fraction at or below gain')
ax.legend(loc='upper left',fontsize=9);ax.grid(alpha=.18)
fig.tight_layout();fig.savefig(a.output_dir/'fig_gain_ecdf.png');plt.close(fig)
print('n',len(rows),'r',r,'p',pval,'gain min/max',gain.min(),gain.max(),'nonpositive',sum(gain<=0))
