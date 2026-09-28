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
