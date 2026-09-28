"""Exploratory 38-image proxy-feature selector, NOT comparable to 80-image scores.

The proxy is an inexpensive bilinear demosaic of the Bayer samples; its output
is known before choosing between the other fast methods but itself has cost.
LOIO remains internal validation on the same cohort, not external validation.
"""
import csv,sys
from pathlib import Path
import numpy as np
from sklearn.model_selection import LeaveOneOut
from sklearn.tree import DecisionTreeClassifier
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'source'))
import pipeline

root=Path(sys.argv[1] if len(sys.argv)>1 else 'images')
rows=[r for r in csv.DictReader(open('source/combined_metrics_descriptors_80_original.csv'))
      if r['dataset'] in ('bsd100','urban100')]
if len(rows)!=38:raise ValueError('Expected 38 rows')
features=[]
for row in rows:
    x=pipeline.load_rgb8(root/row['image_id'])
    m=pipeline.mosaic_rggb(pipeline.srgb_to_linear(x))
    proxy=pipeline.linear_to_srgb(np.clip(pipeline.dem_bilinear(m),0,None))
    features.append(pipeline.descriptors(proxy))
labels=np.array([max(('bilinear','cdiff','malvar'),key=lambda name:float(r[f'{name}_psnr'])) for r in rows])
print('Constant majority baseline:', max((sum(labels==label),label) for label in set(labels)))
subsets={'saturation mean':['sat_mean'],'colour variance':['colour_variance'],
         'gradient structure':['grad_mean','grad_std'],
         'all nine':list(features[0])}
for title,cols in subsets.items():
    X=np.array([[r[col] for col in cols] for r in features])
    predictions=[]
    for train,test in LeaveOneOut().split(X):
        model=DecisionTreeClassifier(max_depth=2,random_state=42).fit(X[train],labels[train])
        predictions.append(model.predict(X[test])[0])
    print(title,sum(np.array(predictions)==labels),'/38')
