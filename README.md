# Nature's Frontiers

Code repository to accompany Polasky, et al. (Science 2026). Included as science-2026-natures-frontiers.zip, and also available via GitHub at [https://github.com/natcap-nci/science-2026-natures-frontiers](https://github.com/natcap-nci/science-2026-natures-frontiers)

Folder `natures_frontiers` contains code to generate country-level inputs from the global datasets,
including country-scale slices, scenario generation, model evaluation, and summary statistics at the
"spatial decision unit" (SDU) scale. See `scripts/preprocess.py`. It also does postprocessing
(`scripts/postprocess.py`) after the optimization to generate summary tables and maps. An example configuration file is included (`configs/2022_09_06.yml`). In order to run the code, the user needs to download the data from the inputs repository ([https://doi.org/10.5061/dryad.qjq2bvqw5](https://doi.org/10.5061/dryad.qjq2bvqw5)), separately download biodiversity data from IUCN as described in the inputs repo, update the config file to point to their local copies of the listed files, ensure they have a compatible python environment (see requirements in `setup.py`) and then run `python preprocess.py [config file path]` or `python postprocess.py [config file path]` as desired.

Folder `NaturesFrontiers.jl` contains the Julia code that was used for the optimization. It reads
the outputted value tables from `preprocess.py` and creates an h5 file for each country containing
the frontier and summary statistics. To run the optimization, ensure that the preprocessing is
complete, a compatible Julia environment has been constructed based on `Project.toml`, and then run
`Julia run_nci.jl [config file path]`.

Descriptions of the individual files within each package follow below.

## natures_frontiers/wbnci

The `wbnci` package contains the Python modules called by `scripts/preprocess.py` and `scripts/postprocess.py`. The preprocessing workflow uses these modules to build scenario rasters and aggregate ecosystem service values to SDUs; the postprocessing workflow uses them to generate summary tables, frontier plots, and maps from the optimization results.

**`__init__.py`** — Package initializer (empty).

**`lulc_codes.csv`** — CSV table defining all land use/land cover (LULC) codes used in the analysis and classifying each code as natural, cropland, grazing, forestry, and/or irrigated. Read by `utils.read_lulc_table` and used throughout the package.

**`lucodes.py`** — Lookup tables mapping LULC codes to display names, hex colors, and RGB tuples, and mapping coarser activity categories (Natural, Cropland, Grazing, Forestry, etc.) to colors. Used for map rendering and legends.

**`utils.py`** — Shared utility functions used across the package: reading the LULC code table, adding color tables to GeoTIFF rasters, converting GeoTIFF to PNG, reading SDU ID lists from shapefiles, and parsing CSV headers.

**`preprocessing.py`** — Core preprocessing infrastructure. Creates regular SDU grids (square or hexagonal), reclassifies LULC rasters for scenario generation, aggregates pixel-level ecosystem service values to SDU totals, and writes the per-scenario value tables that are read by the Julia optimizer.

**`scenario_creation.py`** — Generates the 13 land use scenario rasters for each country: `restoration`, `sustainable_current`, `extensification_current_practices`, `extensification_intensified_rainfed`, `extensification_intensified_irrigated`, `extensification_bmps_rainfed`, `extensification_bmps_irrigated`, `fixedarea_intensified_rainfed`, `fixedarea_intensified_irrigated`, `fixedarea_bmps_rainfed`, `fixedarea_bmps_irrigated`, `grazing_expansion`, and `forestry_expansion`, plus two auxiliary scenarios (`all_urban`, `all_econ`) used for biodiversity normalization. Each function reclassifies a base LULC raster according to eligibility criteria (slope, soil, irrigation suitability, protected area status).

**`cropland_suitability_masks.py`** — Generates binary suitability masks for cropland expansion and intensification scenarios by combining slope thresholds, rainfed/irrigated suitability layers, soil suitability, and protected area status. The masks produced here are inputs to `scenario_creation.py`.

**`biodiversity.py`** — Scores each land use scenario for biodiversity using a composite metric that takes the pixel-level maximum across six sub-metrics: species richness (via PREDICTS relationships), IUCN Red List species, endemic species, Key Biodiversity Areas overlap, ecoregion rarity, and forest landscape intactness. Outputs a normalized raster per scenario.

**`carbon_new.py`** — Calculates above- and below-ground carbon stocks per pixel from a land use raster using a zone-by-land-use lookup table. Carbon values are capped at the potential vegetation carbon for each zone to prevent non-natural classes from exceeding their natural reference.

**`cropland.py`** — Calculates per-pixel cropland economic value by matching each pixel's land use code to the appropriate value raster (current practices, intensified rainfed, or intensified irrigated), scaled by pixel area.

**`forestry.py`** — Calculates per-pixel forestry economic value for pixels assigned to forestry management classes, reading values from a pre-computed forestry production value raster.

**`grazing.py`** — Calculates per-pixel grazing economic value and methane emissions for pixels assigned to grazing classes, using potential grazing value and methane rasters scaled by pixel area.

**`other_wq.py`** — Retrieves pre-computed per-scenario nitrogen-in-drinking-water rasters from the inputs folder (currently only `noxn_in_drinking_water`), or writes a zero raster if the file is not present.

**`transition_cost.py`** — Retrieves pre-computed transition cost rasters for each scenario from the inputs folder, or writes a zero raster if not present.

**`precalc_rasters.py`** — An earlier version of `nitrate_cancer_cases.py` that retrieves pre-computed cancer case rasters; retained for compatibility.

**`evaluation.py`** — Utility for evaluating an arbitrary landscape raster against all ecosystem service models after the main analysis. Calls the individual model modules (biodiversity, carbon, cropland, forestry, grazing) and the transition cost function, assembling outputs in a single folder. Also contains a standalone `transition_cost` function that computes costs directly from scenario and baseline rasters.

**`reports.py`** — Post-processing module that generates summary outputs from optimization results: aggregates SDU value tables, merges baseline and optimization results, calculates normalized scores and distances from baseline, identifies Pareto points, writes `merged_summary_table.csv` and `nci_scores.csv`, generates frontier scatter plots, and creates LULC and activity-category map images.

**`solution_mapping.py`** — Converts optimization solutions stored in `solutions.h5` to spatial raster and PNG maps by tiling per-SDU scenario rasters according to the solution assignment. Also recodes detailed LULC maps to coarser activity categories and generates color-table legends.

**`agreement_maps.py`** — Generates spatial agreement maps showing, for each SDU, the most frequently assigned land management type across the set of Pareto-optimal solutions, along with the frequency of that modal assignment.

## NaturesFrontiers.jl

### src/

**`src/NaturalCapitalIndex.jl`** — Module entry point. Loads the three source files below and exports the public API used by `run_nci.jl`.

**`src/data_fns.jl`** — Data loading functions. Reads per-country CSV value tables from disk and assembles them into matrices indexed by spatial decision unit (SDU) and management scenario, which are the inputs to the optimizer.

**`src/optimization_fns.jl`** — Core optimization routines. Implements random weight-vector generation (uniformly sampled from the positive unit sphere), per-weight linear optimization across management scenarios, data normalization, and the main `random_sample_frontier` function that samples the Pareto frontier by solving many weighted-sum problems in parallel using Julia threads.

**`src/main_fns.jl`** — Top-level orchestration. The `do_nci` function runs the full optimization pipeline for one country: loads the 13 scenario value tables, runs the maximization frontier, runs the minimization frontier, and writes summary CSV tables and an HDF5 solutions archive (`solutions.h5`).

### docs/

**`docs/solution-docs.md`** — Describes the structure of the `solutions.h5` output files produced by the optimization, including how to read solutions from Python using `h5py`.

## data_prep_scripts

These scripts were used to prepare global input raster datasets that feed into the main
preprocessing pipeline (`natures_frontiers/scripts/preprocess.py`). In particular these scripts
allow users to create necessary biodiversity and LULC inputs from IUCN and ESA data sources that
could not be distributed with the inputs repository due to licensing.

**`speciesRichness.py`** — For each country, clips and rasterizes IUCN range maps for birds,
reptiles, amphibians, and mammals, weighting each species' presence by its inverse range size.
Produces per-country, per-taxa potential species richness rasters (`{Taxa}.tif`) used as inputs to
the biodiversity sub-metric in `wbnci/biodiversity.py`.

**`redList.py`** — Same structure as `speciesRichness.py`, but restricts rasterization to species
listed on the IUCN Red List. Produces per-country, per-taxa Red List species richness rasters
(`{Taxa}RL.tif`) used as inputs to the biodiversity sub-metric.

**`endemic.py`** — For each country, rasterizes IUCN range maps for four taxa and weights each species by the inverse of its range area (a range-size rarity metric). Produces per-country endemic-weighted richness rasters (`{Taxa}Endemic.tif`) used as inputs to the biodiversity sub-metric.

**`kbas.py`** — For each country, rasterizes the global Key Biodiversity Areas (KBA) polygon dataset, producing a per-country raster (`KBAs.tif`) indicating the count of KBAs overlapping each pixel. Used as an input to the biodiversity sub-metric.

**`ecoregions.py`** — For each country, rasterizes the Ecoregions 2017 polygon dataset, storing the shape area of each ecoregion at the pixel level to create an ecoregion-rarity weight raster (`ecoMaps.tif`). Used as an input to the biodiversity sub-metric.

**`potentialVegSherlock.py`** — Generates per-country potential vegetation rasters by applying Gaussian smoothing to ESA land cover classes and assigning each pixel to the dominant natural vegetation type within its ecoregion/biome. The resulting potential vegetation rasters are used in scenario creation (e.g., to define restoration targets) in `wbnci/scenario_creation.py`.

**`makeNewESAbasemaps.py`** — Creates modified per-country ESA land use basemaps by overlaying grazing and forestry production value rasters and using FAO national production statistics to determine the area assigned to pasture and managed forestry. Also generates a plantation map distinguishing plantation forest from natural forest cover. The outputs feed into the forestry and grazing input layers for the main analysis.

**`fillAndScaleForestry.py`** — Fills spatial gaps in global timber biomass rasters using Gaussian convolution, then scales the filled values by Net Primary Productivity (NPP) relative to the per-zone NPP mean, producing country-level forestry productivity rasters. The scaling accounts for variation in site productivity across zones and land cover types. Outputs are used as inputs to `wbnci/forestry.py`.

**`merge.py`** — Mosaics per-country output rasters (e.g., modified biomass rasters) into a single global raster using rasterio's merge function. Used to reassemble country-level outputs from `makeNewESAbasemaps.py` into global input layers.
