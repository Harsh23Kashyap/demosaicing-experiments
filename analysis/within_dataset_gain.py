"""Separate pooled and dataset-controlled diagnostic associations of Menon gain."""
import csv
import numpy as np
from scipy.stats import pearsonr
rows=list(csv.DictReader(open('source/combined_metrics_descriptors_80_original.csv')))
assert len(rows)==80 and len({r['image_id'] for r in rows})==80
fast=('bilinear','cdiff','malvar')
g=np.array([float(r['menon_psnr'])-max(float(r[m+'_psnr']) for m in fast) for r in rows])
datasets=np.array([r['dataset'] for r in rows]);unique=['kodak','mcm','bsd100','urban100']
for key in ('sat_mean','colour_variance'):
 x=np.array([float(r[key]) for r in rows]);pr=pearsonr(x,g)
 print('\n',key,'pooled r/p',pr.statistic,pr.pvalue)
 xr=x.copy();gr=g.copy()
 for d in unique:
  idx=(datasets==d);value=pearsonr(x[idx],g[idx]);print(d,int(idx.sum()),'r',value.statistic,'p',value.pvalue,'mean-x',x[idx].mean(),'mean-g',g[idx].mean())
  xr[idx]-=x[idx].mean();gr[idx]-=g[idx].mean()
 partial=pearsonr(xr,gr);print('dataset-controlled residual r',partial.statistic)
 # Pearson p from residuals would incorrectly use n-2 df. With three dataset dummies,
 # regression partial correlation t has df=n-3-2=n-5=75.
 from scipy.stats import t as student_t
 df=len(rows)-len(unique)-1;stat=partial.statistic*np.sqrt(df/(1-partial.statistic**2));p=2*student_t.sf(abs(stat),df)
 print('partial t',stat,'df',df,'p',p)
