#Libraries
import rasterio 
import pandas as pd
import numpy as np
import geopandas as gpd
from rasterio.mask import mask
import os

#Function for zonal stats
def getFeatures(gdf):
	"""Function to parse features from GeoDataFrame in such a manner that rasterio wants them"""
	import json
	return [json.loads(gdf.to_json())['features'][0]['geometry']]

#Read in fao data 
faoData	 =	 pd.read_csv('/scratch/PI/gdaily/Jeff/worldBank/Data2/FAO_data/Inputs_LandUse_E_All_Data_iso3.csv', encoding = 'latin-1')
		

#Country DF
countryGPD		=	 gpd.read_file('/scratch/PI/gdaily/Jeff/worldBank/Data2/countries_iso3_NCI_May.shp')
countries		 =	 pd.unique(countryGPD['nev_name'])



pasture = '/scratch/PI/gdaily/Jeff/worldBank/Data2/pastureESA.tif'	
pasture_map						=	rasterio.open(pasture)

lulc = '/scratch/PI/gdaily/Jeff/worldBank/Data2/lulc.tif'
lulc_map				=	rasterio.open(lulc)	

size = '/scratch/PI/gdaily/Jeff/worldBank/Data2/areaPerPixel2.tif'
size_map =		rasterio.open(size)	

forest = '/scratch/PI/gdaily/Jeff/worldBank/Data2/secondaryESA.tif'
forest_map = rasterio.open(forest)


forest2= '/scratch/PI/gdaily/Jeff/worldBank/Data2/salehVeg/natural_filled.tif'
forest_yield_map = rasterio.open(forest2)


forest3= '/scratch/PI/gdaily/Jeff/worldBank/Data2/salehVeg/plantation_filled.tif'
plantation_yield_map = rasterio.open(forest3)

protected_area = '/scratch/PI/gdaily/Jeff/worldBank/Data2/pa_esa.tif'
protected_area_map = rasterio.open(protected_area)


cutOffValues = []
loopAgain = []
sizeOfPas = []
completedCountries = []






countries		 =	 pd.unique(countryGPD['nev_name'])
countries = list(countries)

countries.remove('United States of America')
countries.remove('Russia')
countries.remove('New Zealand')



dfToSave = pd.DataFrame(index = countries)
dfToSave['pastureSize'] = np.nan
dfToSave['pastureCutoff'] = np.nan
dfToSave['pastureAssigned'] = np.nan
dfToSave['forestSize'] = np.nan
dfToSave['forestCutoff'] = np.nan
dfToSave['forestAssigned'] = np.nan

countries = ['Belize', 'Italy', 'Spain', 'Costa Rica', 'Ghana', 'Panama', 'Germany', 'Austria', 'Argentina']
for country in countries:

	try:
	
		#country coords 
		aoi						=	countryGPD[countryGPD['nev_name']	==	country]
		aoi					 =	aoi.dissolve(by = 'nev_name')
		coords					=	getFeatures(aoi)

		#Pasture claims DF
		claim		=	faoData[faoData['iso'] == aoi.iso3.values[0]]
		claim		=	claim[claim['Item Code'] == 6655]['Y2017'].values[0]

		#Base land use map

		lulc_raw, lulc_affine	 =	 mask(lulc_map, shapes=coords, crop=True)
		lulc_raw				=	lulc_raw[0,:,:]


		#protected_area map 
		pa_raw, pa_affine	 =	 mask(protected_area_map, shapes=coords, crop=True)
		pa_raw				=	pa_raw[0,:,:]
		pa_raw[pa_raw == 1] = 1
		pa_raw[pa_raw != 1] = 0	
		#Pasture map 

		pasture_raw, pasture_affine	 =	 mask(pasture_map, shapes=coords, crop=True)
		pasture_raw						=	pasture_raw[0,:,:]

		#Size map 
		
		size_raw, size_affine			 =	 mask(size_map, shapes=coords, crop=True)
		size_raw						=	size_raw[0,:,:]
		size_raw[size_raw <0] = 0
				

		#Subset pasture map to only ESA pixels which can become pasture 
		viableToFlip	=	[30,40,100,110,120,121,122,130,140,150,152,153,180,200,201,202,203]
		result			 =	 np.where(np.isin(lulc_raw, viableToFlip) == True, 1, 0)
		result[pa_raw == 1] = 0
		
		

		#Select that number of pixels from the pasture map (highest values)
		result	=	result * pasture_raw
		
		#Make df 
		resultDF = pd.DataFrame()
		resultDF['pasture'] =  result.flatten()
		resultDF['size']	=	size_raw.flatten()
		resultDF['esa']		=	lulc_raw.flatten()
		resultDF['multiplier']	=	1.0
		
		resultDF.loc[resultDF[resultDF.esa <= 110].index, 'multiplier'] = 0.5
		
		resultDF	=	resultDF.sort_values(by = ['pasture'], ascending = False)
		resultDF['sizeAdj'] = resultDF['size'] * resultDF['multiplier']
		resultDF['cumulative'] = resultDF['sizeAdj'].cumsum()
		resultDF.reset_index(inplace = True, drop = True)

		

		#Figure out number of pixels you need to burn
		cutOff = resultDF[resultDF['cumulative'] <= claim * 10].pasture.values[-1]
		if cutOff <= 0: cutOff = 0.01
		result	=	np.where(result > cutOff, 1, 0)


		#Burn those onto the map
		final	 =	np.where(result == 1, lulc_raw + 4, lulc_raw)
		final	 =	final.astype(np.uint8)
		dfToSave.loc[country, 'pastureSize'] = claim * 10
		dfToSave.loc[country, 'pastureCutoff'] = cutOff

		dfToSave.loc[country, 'pastureAssigned'] = float(np.nanmax(resultDF['cumulative']))

		result = 0
		resultF = 0
		resultDF = 0
		

		#Forestry claims DF



		claimF = forestClaims[forestClaims['iso3'] == aoi.iso3.values[0]]
		claimF = float(claimF['productionNew'])
		
		
		claim1		=	faoData[faoData['iso'] == aoi.iso3.values[0]]
		claim1		=	claim1[claim1['Item Code'] == 6655]['Y2017'].values[0]

		
	
		
		forest_raw, forest_affine	 =	 mask(forest_map, shapes=coords, crop=True)
		forest_raw						=	forest_raw[0,:,:]


		forest_raw, forest_affine	 =	 mask(forest_map, shapes=coords, crop=True)
		forest_raw						=	forest_raw[0,:,:]
	
		
		#Subset pasture map to only ESA pixels which can become forestry 
		viableToFlip	=	[30,40,100,110,34,44,104,114,160,170,50,60,61,62,70,71,72,80,81,82,90]
		result0			 =	 np.where(np.isin(lulc_raw, viableToFlip) == True, 1, 0)
		result0[pa_raw == 1] = 0

		result = result0 * forest_raw
		forest_raw = 0




		natural_yield_raw, natural_yield_raw_affine	 =	 mask(forest_yield_map, shapes=coords, crop=True)
		natural_yield_raw						=	natural_yield_raw[0,:,:]
		natural_yield_raw[natural_yield_raw < 0] = 0

		result2 = result0 * natural_yield_raw
				

  
		plantation_yield_raw, natural_yield_raw_affine	 =	 mask(plantation_yield_map, shapes=coords, crop=True)
		plantation_yield_raw						=	plantation_yield_raw[0,:,:]
		plantation_yield_raw[plantation_yield_raw <0] = 0
		result3 = result0 * plantation_yield_raw
		
		
		
		  

		
		#Make df 
		resultDF = pd.DataFrame()
		resultDF['forestry'] =  result.flatten()
		resultDF['size']	=	size_raw.flatten()
		size_raw = 0
		resultDF['esa']		=	lulc_raw.flatten()
		lulc_raw = 0
		resultDF['natural_yeild'] = result2.flatten()
		result2 = 0
		resultDF['plantation_yield'] = result3.flatten()
		result3 = 0
		
		
		
		resultDF['multiplier']	=	1.0
		
		resultDF.loc[resultDF[resultDF.esa == 30].index, 'multiplier'] = 0.5
		resultDF.loc[resultDF[resultDF.esa == 34].index, 'multiplier'] = 0.5
		resultDF.loc[resultDF[resultDF.esa == 40].index, 'multiplier'] = 0.5
		resultDF.loc[resultDF[resultDF.esa == 44].index, 'multiplier'] = 0.5
		resultDF.loc[resultDF[resultDF.esa == 100].index, 'multiplier'] = 0.5
		resultDF.loc[resultDF[resultDF.esa == 104].index, 'multiplier'] = 0.5
		resultDF.loc[resultDF[resultDF.esa == 110].index, 'multiplier'] = 0.5
		resultDF.loc[resultDF[resultDF.esa == 114].index, 'multiplier'] = 0.5
		
		resultDF.drop(columns = ['esa'], inplace = True)
		
		resultDF	=	resultDF.sort_values(by = ['forestry'], ascending = False)
		resultDF['yieldAdj'] = resultDF['natural_yeild'] * resultDF['multiplier'] * resultDF['size'] * 100
		
		
		
		resultDF['size_cumulative'] = resultDF['size'].cumsum()
		resultDF[resultDF['size_cumulative'] <= claim1]['yieldAdj'] = resultDF['plantation_yield'] * resultDF['multiplier'] * resultDF['size'] * 100

		nyr = float(resultDF[resultDF['size_cumulative'] <= claim1].forestry.values[-1])
		print(nyr)

		resultDF.drop(columns = ['multiplier'], inplace = True)
		resultDF.drop(columns = ['size', 'size_cumulative'], inplace = True)
		
		resultDF['cumulative'] = resultDF['yieldAdj'].cumsum()
		resultDF.reset_index(inplace = True, drop = True)	

		

		natural_yield_raw = np.where(result >= nyr, plantation_yield_raw, natural_yield_raw)
		plantation_map = np.zeros_like(natural_yield_raw)
		plantation_map = np.where(result >= nyr, 1, 0)
		
		plantation_map = plantation_map.astype(np.uint8)

		plantation_yield_raw = 0
		#Figure out number of pixels you need to burn

		cutOffF = resultDF[resultDF['cumulative'] <= claimF].forestry.values[-1]
		
		if cutOffF <= 0: cutOffF = 0.01
		
		resultF	=	np.where(result >= cutOffF, 1, 0)
		resultF =	np.where(result == 0, 0, resultF)

		#Burn those onto the map
		final	 =	np.where(resultF == 1, final + 5, final)
		final	 =	final.astype(np.uint8)

		dfToSave.loc[country, 'forestCutoff'] = cutOffF
		dfToSave.loc[country, 'forestYield'] = claimF 		
		dfToSave.loc[country, 'forestAssigned'] = np.max(resultDF['cumulative'])
		resultF = 0
		resultDF = 0
		
		
		




		#Save file
		with rasterio.Env():
			profile = lulc_map.profile
			profile.update(
				dtype=rasterio.uint8,
				count=1,
				driver="GTiff",
				height=final.shape[0],
				width=final.shape[1],
				transform=pasture_affine,
				compress = 'lzw')
			
			
			file = "/scratch/PI/gdaily/Jeff/worldBank/mayData/Results2_December"
			file = os.path.join(file, country, 'plantation_map_jan28.tif')

			with rasterio.open(file, 'w', **profile, tile = False) as dst:
				dst.write_band(1,plantation_map)



		#Save file
		with rasterio.Env():
			profile = lulc_map.profile
			profile.update(
				dtype=rasterio.uint8,
				count=1,
				driver="GTiff",
				height=final.shape[0],
				width=final.shape[1],
				transform=pasture_affine,
				compress = 'lzw')
			
			
			file = "/scratch/PI/gdaily/Jeff/worldBank/mayData/Results2_December"
			file = os.path.join(file, country, 'modifiedESA_jan28.tif')

			with rasterio.open(file, 'w', **profile, tile = False) as dst:
				dst.write_band(1,final)
				
		with rasterio.Env():
			profile = lulc_map.profile
			profile.update(
				dtype=rasterio.float32,
				count=1,
				driver="GTiff",
				height=final.shape[0],
				width=final.shape[1],
				transform=pasture_affine,
				compress = 'lzw')
			
			
			file = "/scratch/PI/gdaily/Jeff/worldBank/mayData/Results2_December"
			file = os.path.join(file, country, 'modifiedBiomass_jan28.tif')

			with rasterio.open(file, 'w', **profile, tile = False) as dst:
				dst.write_band(1,natural_yield_raw)
				

		natural_yield_raw = 0
		print(country, cutOff, cutOffF)
		cutOffValues = cutOffValues + [cutOff]
		sizeOfPas = sizeOfPas + [claim / 10]
		completedCountries = completedCountries + [country] 
		

	except:
		print(str(country), 'failed')
		loopAgain = loopAgain + [country] 
dfToSave.to_csv("/scratch/PI/gdaily/Jeff/worldBank/resultDF_jan28.csv")

