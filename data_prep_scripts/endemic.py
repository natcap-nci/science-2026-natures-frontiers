#Libraries
import geopandas as gpd
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt 
import seaborn as sns
import rasterio
from rasterio.mask import mask
from rasterio.plot import show
from glob import glob
import os

#Function for zonal stats
def getFeatures(gdf):
	"""Function to parse features from GeoDataFrame in such a manner that rasterio wants them"""
	import json
	return [json.loads(gdf.to_json())['features'][0]['geometry']]



#Non user specified data files
lulc_map_file	=	'/home/groups/gdaily/global2/ESA_landcover/lulc.tif'
aoi_file 		= 	'/scratch/PI/gdaily/Jeff/worldBank/Data/countries_iso3.shp'
bird_files		=	'/home/groups/gdaily/global2/BOTW.gdb'
reptile_files	=	'/home/groups/gdaily/global2/reptileRangeMaps/REPTILES.shp'
amphibian_files	=	'/home/groups/gdaily/global2/amphibianRangeMaps/AMPHIBIANS.shp'
mammal_files	=	'/home/groups/gdaily/global2/mammalRangeMaps/MAMMALS.shp'



outputDirectory	=	'/scratch/PI/gdaily/Jeff/worldBank/Results2'

#Read in area of interest
aoi_base				=	gpd.read_file(aoi_file)



countryList				=	pd.unique(aoi_base['nev_name'])


for country in countryList:	
	#Directory Management
	countryDirectory	=   str(outputDirectory + '/' +  str(country) + '/')
	if not os.path.exists(countryDirectory):
		os.makedirs(countryDirectory)
	
	aoi						=	aoi_base[aoi_base['nev_name']	==	country]
	aoi 					=	aoi.dissolve(by = 'nev_name')
	coords					=	getFeatures(aoi)

	#Read in land cover map and clip land cover map 
	lulc_map				=	rasterio.open(lulc_map_file)
	lulc_raw, lulc_affine 	= 	mask(lulc_map, shapes=coords, crop=True)
	lulc_raw				=	lulc_raw[0,:,:]

	#Rasterize shapefiles
	def speciesRichness(file, name):
		
		#Make a data frame to hold summary statistics for red list species
		subRL				   =   pd.DataFrame()
		
		#Read in data files the try except handles differences in file formats across taxa
		try:
			shapeFiles			=	gpd.read_file(file, layer='All_Spp', bbox = tuple(aoi.total_bounds))	
			species				=	pd.unique(shapeFiles['SCINAME'])
		except:
			shapeFiles			=	gpd.read_file(file, bbox = tuple(aoi.total_bounds))	
			species				=	pd.unique(shapeFiles['binomial'])
		
		#Make a base array to calculate your regional species pool 
		outArray			=	np.zeros(shape = [int(lulc_raw.shape[0]), int(lulc_raw.shape[1])])
		
		#Loop through speices and rasterize them 
		for i in species:
			try:
				sub 	=	shapeFiles[shapeFiles['SCINAME'] == i]
			except:
				sub		=	shapeFiles[shapeFiles['binomial'] == i]
				
			#Add each species binary occurance to your species pool
			range 	=	sub['SHAPE_Area']
			sub		=	rasterio.features.rasterize(shapes=sub['geometry'], 
										out_shape=tuple([int(lulc_raw.shape[0]), int(lulc_raw.shape[1])]), 
										transform=lulc_affine, dtype = np.int16, all_touched = True)
			sub[sub >1] = 1.0
			sub = sub / range
			outArray += sub 
		#Clean up our species pool and return it to our dictionary 
		outArray		=	np.nan_to_num(outArray)
		outArray		=	np.where(lulc_raw > 0, outArray, np.nan)
		outArray		=	outArray.astype('float32')
		
		

				
		
		with rasterio.Env():
			profile = lulc_map.profile
			profile = {k: v for k, v in lulc_map.profile.items() if k not in ['blockxsize', 'blockysize']}
			profile.update(
				dtype=rasterio.float32,
				count=1,
				driver="GTiff",
				height=lulc_raw.shape[0],
				width=lulc_raw.shape[1],
				transform=lulc_affine)
			
			
			print(profile)
			print(outArray.shape)
		
			with rasterio.open(str(countryDirectory + name + '.tif'), 'w', **profile, tile = False) as dst:
				dst.write_band(1,outArray)

		
		

			
		
	speciesRichness(amphibian_files, 'AmphibiansEndemic')
	speciesRichness(bird_files, 'BirdsEndemic')
	speciesRichness(mammal_files, 'MammalsEndemic')
	speciesRichness(reptile_files, 'ReptilesEndemic')















