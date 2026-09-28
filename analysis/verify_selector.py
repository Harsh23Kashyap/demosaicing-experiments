"""Recheck observed depth-2 LOIO ablation scores from the historical 80-image table.

This verifies arithmetic, not whether the feature sets were pre-specified.
"""
import csv
import numpy as np
from scipy.stats import pearsonr
from sklearn.model_selection import LeaveOneOut
from sklearn.tree import DecisionTreeClassifier

rows=list(csv.DictReader(open('source/combined_metrics_descriptors_80_original.csv')))
FAST=('bilinear','cdiff','malvar')
labels=np.array([max(FAST,key=lambda m:float(r[f'{m}_psnr'])) for r in rows])
features={'saturation mean':['sat_mean'], 'colour variance':['colour_variance'],
          'gradient structure':['grad_mean','grad_std'],
          'all nine':['edge_density','grad_mean','grad_std','local_tex','hf_energy',
                      'colour_variance','sat_mean','sat_std','noise']}
print('Constant Malvar:',sum(labels=='malvar'),'/80')
for name,columns in features.items():
    X=np.array([[float(r[k]) for k in columns] for r in rows])
    predicted=[]
    for train,test in LeaveOneOut().split(X):
        model=DecisionTreeClassifier(max_depth=2,random_state=42).fit(X[train],labels[train])
        predicted.append(model.predict(X[test])[0])
    print(name, sum(np.array(predicted)==labels),'/80')
gain=np.array([float(r['menon_psnr'])-max(float(r[f'{m}_psnr']) for m in FAST) for r in rows])
for feature in ('sat_mean','colour_variance','sat_std','grad_std'):
    correlation,p=pearsonr([float(r[feature]) for r in rows],gain)
    print(feature, correlation,p)
