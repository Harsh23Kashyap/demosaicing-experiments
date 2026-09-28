"""Reconstruct the three six-panel visual cases from source images.

Exact crops were recovered by matching reference panels to whole source
images; not inferred from image titles. Source images stay outside the repo.
"""
import argparse,sys
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'source'))
import pipeline
from final80_variant_original import dem_alleysson_final

CASES={
 'high_gain':('urban100/img_042.png',(64,128,192,192),'High Gain: urban100/img_042.png'),
 'counterexample':('urban100/img_081.png',(320,128,192,192),'Counterexample: urban100/img_081.png'),
 'near_tie':('bsd100/img_012.png',(256,128,192,192),'Near Tie: bsd100/img_012.png')}
METHODS={**pipeline.METHODS,'alleysson':dem_alleysson_final}
p=argparse.ArgumentParser();p.add_argument('--image-root',type=Path,required=True);p.add_argument('--output-dir',type=Path,default=Path('figures'));a=p.parse_args();a.output_dir.mkdir(parents=True,exist_ok=True)
for name,(rel,(x,y,w,h),title) in CASES.items():
    rgb=pipeline.load_rgb8(a.image_root/rel);lin=pipeline.srgb_to_linear(rgb);m=pipeline.mosaic_rggb(lin)
    images=[('Reference',rgb)]+[(label,pipeline.linear_to_srgb(np.clip(METHODS[method](m),0,None))) for label,method in
                               [('Bilinear','bilinear'),('Colour-diff.','cdiff'),('Malvar','malvar'),('Menon','menon'),('Alleysson','alleysson')]]
    fig,axes=plt.subplots(2,3,figsize=(13.2,9.6),dpi=150)
    for ax,(label,image) in zip(axes.flat,images):
        ax.imshow(image[y:y+h,x:x+w],interpolation='nearest');ax.set_title(label,fontsize=17,pad=8);ax.axis('off')
    fig.suptitle(title,fontsize=19)
    fig.subplots_adjust(left=.015,right=.985,bottom=.035,top=.88,wspace=.08,hspace=.21)
    out=a.output_dir/f'fig_case_{name}_regenerated.png';fig.savefig(out,dpi=150);plt.close(fig)
    print(rel,'crop',x,y,w,h,'->',out)
