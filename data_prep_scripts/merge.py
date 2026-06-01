import geopandas as gpd
import pandas as pd
import numpy as np
import os
import shutil  
import pathlib
import rasterio
from glob import glob
from rasterio.merge import merge




def makeMosaic(q, out_fp ):

	src_files_to_mosaic = []
	dem_fps = glob(q)
	for fp in dem_fps:
		src = rasterio.open(fp)
		src_files_to_mosaic.append(src)
	mosaic, out_trans = merge(src_files_to_mosaic)
	out_meta = src.meta.copy()
	# Update the metadata
	out_meta.update({"driver": "GTiff",
					"height": mosaic.shape[1],
					"width": mosaic.shape[2],
					"transform": out_trans,
					"compress": 'lzw'
				}
				)	
	
	with rasterio.open(out_fp, "w", **out_meta, tiled=True, blockxsize=256, blockysize=256, BIGTIFF='YES') as dest:
		dest.write(mosaic)


"""
q = "/scratch/PI/gdaily/Jeff/worldBank/mayData/Results2_December/*/modifiedESA_mar6.tif"
out_fp = 	"/scratch/PI/gdaily/Jeff/worldBank/modifiedESA_mar6.tif"
makeMosaic(q, out_fp)
"""

		
q = "/scratch/PI/gdaily/Jeff/worldBank/mayData/Results2_December/*/modifiedBiomass_mar6.tif"
out_fp = 	"/scratch/PI/gdaily/Jeff/worldBank/modifiedBiomass_mar6.tif"
makeMosaic(q, out_fp)

"""
q = "/scratch/PI/gdaily/Jeff/worldBank/mayData/Results2_December/*/plantation_map_mar6.tif"
out_fp = 	"/scratch/PI/gdaily/Jeff/worldBank/plantation_map_mar6.tif"
makeMosaic(q, out_fp)

"""




