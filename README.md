# Nature's Frontiers

Code repository to accompany Polasky, et al. (Science 2026).

Folder `natures_frontiers` contains code to generate country-level inputs from the global datasets,
including country-scale slices, scenario generation, model evaluation, and summary statistics at the
"spatial decision unit" (SDU) scale. See `scripts/preprocess.py`. It also does postprocessing
(`scripts/postprocess.py`) after the optimization to generate summary tables and maps.

Folder `NaturesFrontiers.jl` contains the Julia code that was used for the optimization. It reads
the outputted value tables from `preprocess.py` and creates an h5 file for each country containing
the frontier and summary statistics.
