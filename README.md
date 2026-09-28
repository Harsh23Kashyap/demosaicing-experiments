# Classical Bayer demosaicing experiment audit

This repository records an audit of the 80-image demosaicing study and a fresh runtime run. It is a working research artifact, **not** a claim that all experiments or a manuscript are finalized.

## Provenance

The historical experiment source bundle's `SHA256SUMS` verified on extraction. `source/combined_metrics_descriptors_80_original.csv` is unchanged from that bundle (SHA-256 `63ec1fdc22c0b40c420a0ea9cf151ea3774e17465d50201658b9ede31a881f50`). The `source/*.py` scripts are copied from the original bundle; `final80_variant_original.py` only changes an absolute `/tmp/pipeline` import path to a relative path so it can run elsewhere. This is a copy of historical experiment code, not a freshly validated implementation of every methodological detail.

The 80 source images are **not** committed. The 20 BSD100 and 18 Urban100 images from the bundle can be reconstructed by `python source/download_selected_bsd100_urban100.py` (download provenance in the source script), then verified against the original bundle's `SHA256SUMS` separately. Kodak/McMaster images were not in that ZIP and are not redistributed. Original images and benchmark terms must be checked before any release.

## Final measured-fast tier correction

The historical CSV's `best_fast_method` and `menon_gain_vs_best_fast_db` fields reflect an earlier method tier that **included Alleysson**. The revised manuscript instead defines fast methods as bilinear, colour-difference, and Malvar, with Alleysson a quality comparator. Do not use the two stale CSV fields for final-tier gain analysis.

Run `python analysis/recompute.py` to derive `results/final_tier_metrics_80.csv` and `results/dataset_gain_t95.csv` from each row's six PSNR columns. Recalculation gives Malvar 59/80 fast wins, mean Menon gain +1.085041 dB, 19/80 nonpositive. Figure `figures/dataset_gain_t95_recomputed.png` uses the derived per-image gains. Its 95% intervals use `scipy.stats.t.interval(0.95, n-1, loc=mean, scale=stats.sem(gains))` independently within each dataset. This documents the **new calculation**, not proof that the original plotted bars used the same method.

## Fresh timing run

`python analysis/benchmark_runtime.py --image-root images` runs the 38 supplied BSD100/Urban100 images with the original pipeline plus its final Alleysson variant, one untimed warm-up and three `perf_counter_ns` timed calls per image/method. Within-pair medians are recorded row by row; Table 1-style medians are taken across the 38 images. The timing includes method execution only, not descriptor computation or image I/O. `results/runtime_environment.json` captures the actual sandbox CPU, kernel and library versions; `results/runtime_38_new_run.csv` contains all 228 image-method rows with individual samples. These are a new machine run and **must not be presented as the original manuscript's timing values**.

| Method | Fresh median (ms) |
|---|---:|
| Nearest | 5.848 |
| Bilinear | 19.720 |
| Colour-difference | 38.568 |
| Malvar | 16.478 |
| Alleysson | 86.223 |
| Menon | 68.758 |

The broad measured-fast/slow ordering persists, but implementation/platform differences change absolute times. These figures are not universal hardware benchmarks.

## Gaps before submission

- Recover or legally reacquire and checksum the exact Kodak/McMaster images before independently reproducing all 80 image reconstructions. The 80-image statistical recomputation currently uses the historical per-image measurements in the source CSV.
- Determine whether the depth-2 selector feature set was selected before looking at outcomes or after the fact; the author is handling this provenance question. Do not overstate the out-of-sample 78.75% if there was post-hoc selection.
- Audit individual method implementations, image preprocessing, descriptor definitions, scalar metrics and visual crop provenance against source data; test constant-image CFA behavior and inspect boundary handling.
- Select an artifact access/archival route compatible with dataset licenses and venue anonymity. No DOI or anonymous reviewer access is claimed here.
- Update manuscript Figure 2 caption to explicitly name the new Student-t CI method if replacing the figure, and Table 1 footnote to identify a *fresh* environment if replacing timings. Do not silently mix old and new measurement systems.

## Dependencies

Python 3.10; versions tested in `requirements.txt`, with exact runtime package versions and machine details in `results/runtime_environment.json`. Install with `python -m pip install -r requirements.txt`. This repository intentionally excludes raw licensed images and secrets.

## Independent pixel-level replay and proxy exploration

`python analysis/verify_supplied_38.py <path-to-extracted-images>` replays all
1,482 numeric quality and descriptor cells (38 images, six methods, five metrics,
nine descriptors) against the historical CSV. The maximum absolute error in the
saved verification table was 1.23e-9 (printed CSV precision). This does **not**
independently reproduce Kodak/McMaster. `python analysis/verify_selector.py`
rechecks the 80-row depth-2 LOIO and correlation arithmetic; it cannot determine
whether the predictor feature sets were selected before outcomes were inspected.

`python analysis/mosaic_proxy_38.py <path-to-extracted-images>` explores
pre-choice descriptors derived from a bilinear mosaic reconstruction. On these
38 images alone, constant Malvar gets 33/38 and depth-2 LOIO with proxy
saturation gets 35/38; the other inspected feature sets get 33/38. This is a
post-hoc exploratory, internally cross-validated result, **not** an external
validation or a prospective 80-image claim. Bilinear reconstruction and
nine-descriptor extraction add compute cost; their latency is not included in
the existing method timing table. No threshold is recommended for deployment.

Synthetic constant-image checks reveal a historical nearest-neighbour boundary
defect: odd height/width yields incorrect values in the last row/column. The
38 supplied benchmark images have even dimensions and reproduce the recorded
measurements; keep the historical implementation untouched when auditing those
numbers. A fixed implementation would need separate validation and labeling.

## Private source reacquisition and 80-image replay (28 Sep 2026)

The previous Kodak/McMaster gap is now narrowed. Kodak 24 PNGs were downloaded
from Rich Franzen's Kodak Lossless True Color Image Suite at
https://r0k.us/graphics/kodak/ ; the original McMaster 18 TIFFs were downloaded
from the university distributor at
https://www4.comp.polyu.edu.hk/~cslzhang/CDM_Dataset.htm (its protected
`McM.zip`). The 42 downloaded files were **not** added to this repository.
`results/reacquired_source_hashes_kodak_mcm_42.csv` records the hashes and
image sizes of these downloaded copies. These hashes are reproducible
fingerprints of this reacquisition, not proof of the unknown original run's
bytes. Running

```
python analysis/verify_kodak_mcmaster_42.py \
  --kodak-dir /path/to/kodak-pngs --mcm-dir /path/to/extracted/McM
```

reproduced all 1,638 historical numeric cells for those 42 images within
3.49e-9 absolute; `results/verification_kodak_mcm_42.csv` records each cell.
Combined with the earlier BSD100/Urban100 replay, all 80 rows (3,120
numerical descriptor/metric cells) now reproduce within saved CSV rounding.
This result does not identify the original machine's runtime, establish the
chronology of feature design, or grant image redistribution permission.

The Kodak host says it is the maintainer's *understanding* that Kodak released
images for unrestricted use, not a direct copyright license from Kodak. The
McMaster distributor asks for citation of Zhang et al. (2011) and gives the
ZIP password but does not state image redistribution terms. Retain source
images privately and resolve rights before sharing or archiving image bytes.

## Out-of-domain proxy check (exploratory, negative)

`python analysis/external_proxy_set14.py --source80 /path/to/all80 \
--set14 /path/to/Set14/image_SRF_2` fits the depth-2 proxy-saturation
classifier on all 80 source images, then applies it without refitting to the
Set14 HR images hosted in the SelfExSR repository:
https://github.com/jbhuang0604/SelfExSR/tree/master/data/Set14/image_SRF_2 .
This test excludes one grayscale source image and the Lenna image *before*
evaluation, leaving 12 RGB images. The training feature is HSV mean saturation
of a cheap bilinear reconstruction from the mosaic, not the full reference.
The test is a different super-resolution benchmark, not camera RAW. The
source-80 feature choice itself followed a 38-image exploratory analysis.

On Set14, the proxy tree selects the best measured-fast method for **7/12**
images, the same number as constant Malvar. Mean PSNR regret relative to the
per-image fast-tier oracle is **0.435 dB** for the tree versus **0.446 dB** for
Malvar, a 0.011 dB difference too small to support an improvement claim here.
The median bilinear-plus-descriptor acquisition cost was **175 ms/image** in
this new run, exceeding any earlier fast-tier per-image method median; proxy
cost is not included in the existing timing table. The 12 source file hashes,
per-image decisions and costs are in `results/external_proxy_set14_12.csv`.
No Set14 images are redistributed. This is a negative, small-sample check,
not validation of an efficient deployable selector.
