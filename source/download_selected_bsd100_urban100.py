#!/usr/bin/env python3
"""Download the exact BSD100 (20) and Urban100 (18) images used in the 80-image cohort."""
from pathlib import Path
from urllib.request import urlretrieve
FILES = {
 "BSD100": [2,3,17,19,30,43,54,61,4,13,15,27,28,37,40,48,12,47,81,95],
 "Urban100": [13,19,21,34,42,61,81,92,1,4,8,12,14,17,26,47,66,85],
}
BASE="https://raw.githubusercontent.com/jbhuang0604/SelfExSR/master/data/{dataset}/image_SRF_2/img_{num:03d}_SRF_2_HR.png"
root=Path(__file__).resolve().parent.parent/"images"
for dataset, nums in FILES.items():
    out=root/dataset.lower(); out.mkdir(parents=True,exist_ok=True)
    for num in nums:
        dest=out/f"img_{num:03d}.png"
        print(f"{dataset} {num:03d} -> {dest}")
        urlretrieve(BASE.format(dataset=dataset,num=num),dest)
print("Done: 38 images")
