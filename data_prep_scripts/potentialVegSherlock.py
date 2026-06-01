#libs
import rasterio
import pandas as pd
import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import os
from rasterio.mask import mask
from rasterio import windows
import json
from scipy.ndimage import gaussian_filter

#Define custom functions for this script
def getFeatures(gdf):
	return [json.loads(gdf.to_json())['features'][0]['geometry']]


#Biome dictionary 
esaCodes	 = 	{
				'forest'			:	[50,60,61,62,70,71,72,80,81,82,90,100,110,120,121,122,150,152,153,160,170,180],
				'boreal'			:	[50,60,61,62,70,71,72,80,81,82,90,100,110,140,200,201,202,220,120,121,122,150,152,153,160,170,180],
				'shrub'				:	[120,121,122,130,140,150,152,153,180,200,201,202,50,60,61,62,70,71,72,80,81,82,90,100,110,160,170,180],
				'mangroves'			:	[160,170],		
				'desert'			:	[120,121,122,130,140,150,152,153,180,200,201,202]
				}
				
biomeCodes	=	{
				'forest'			:	[1,2,3,4],
				'boreal'			:	[5,6,11],
				'shrub'				:	[7,8,9,10,12,13],
				'mangroves'			:	[14],
				'desert'			:	[13]
				}
				
lulcF	= r"/scratch/PI/gdaily/Jeff/worldBank/Data/lulc.tif"
lulc 	=	rasterio.open(lulcF)

ecorF	= r"/scratch/PI/gdaily/Jeff/worldBank/Data/lulc1.tif"
ecor 	=	rasterio.open(ecorF)



clipCountry		=	 gpd.read_file('/scratch/PI/gdaily/Jeff/worldBank/Data/countries_iso3.shp')


#Read in Costa Rica shapefile
countryGPD		=	 gpd.read_file('/scratch/PI/gdaily/Jeff/worldBank/Data/westernCountries.shp')
aaa = 1
bbb = 1
countryList = ['Democratic Republic of the Congo', 
				'Republic of the Congo',
				'Central African Republic',
				'Ghana',
				'Angola',
				'India',
				'Spain',
				'Italy',
				'Greece',
				'Chile',
				'Argentina',
				'Australia',
				'Brazil',
				'Mexico',
				'United States of America']
				
#pd.unique(countryGPD['nev_name'])




for country in countryList:

	if country == 'Russia':
		aaa = 1
	elif country == 'United States of America':
		aaa = 1
	elif country == 'New Zealand':
		aaa = 2
	elif country == 'Antarctica':
		aaa = 2
	elif country == 'United States Minor Outlying Islands':
		aaa = 2
	elif country == 'Kiribati':
		aaa = 2
	elif country == 'France':
		aaa = 2
	elif country == 'Norway':
		aaa = 2
	elif country == 'French Southern and Antarctic Lands':
		aaa = 2

	else:
		aaa = 1



	if os.path.exists(str("/scratch/PI/gdaily/Jeff/worldBank/vegMaps6/" + country + ".tif")) == False:
		if bbb == 1:

			if aaa == 1:
				df = countryGPD[countryGPD['nev_name'] == country]
				coords = getFeatures(df)

				out_img, out_transform 	= 	mask(lulc, shapes=coords, crop=True)
				out_img = out_img[0]
				eco, eco_transform		=	mask(ecor, shapes = coords, crop = True)


					

				uniqueClasses = np.unique(out_img)
				uniqueClasses = uniqueClasses[np.where(uniqueClasses > 40)]
				maps = {}
				for i in uniqueClasses:
					
					maps[i] = np.zeros_like(out_img)
					maps[i][np.where(out_img == i)] = 1
					maps[i] = maps[i].astype(np.float)
									
					maps[i] = gaussian_filter(maps[i], sigma=22)



				finalMap = np.zeros_like(out_img)

				for key, item in biomeCodes.items():
					
					subClasses = esaCodes[key] 
					
					
					subClasses = list(set(subClasses).intersection(set(uniqueClasses)))
					maxValue = np.zeros_like(out_img)
					for i in subClasses:
						maxValue	=	np.maximum(maxValue, maps[i])

					finalMapA = np.zeros_like(out_img)

					for i in subClasses:
						finalMapA[np.where(maxValue == maps[i])] = i
						
						
					maskMap = 	np.zeros_like(finalMap)
					maskMap[np.isin(eco[0], biomeCodes[key])] = 1
					
				
					finalMap += finalMapA * maskMap
				


				
				finalMap[np.where(out_img == 0)] = 0	


				with rasterio.Env():
					profile = lulc.profile
					profile = {k: v for k, v in lulc.profile.items() if k not in ['blockxsize', 'blockysize']}
					profile.update(
						dtype=rasterio.uint8,
						count=1,
						driver="GTiff",
						height=finalMap.shape[0],
						width=finalMap.shape[1],
						transform=out_transform,
						compression = 'lzw')
					


					with rasterio.open(str("/scratch/PI/gdaily/Jeff/worldBank/vegMaps6/" + country + "W.tif"), 'w', **profile, tile = False) as dst:
						dst.write_band(1,finalMap)



				UnBuff = rasterio.open(str("/scratch/PI/gdaily/Jeff/worldBank/vegMaps6/" + country + "W.tif"))
				df = clipCountry[clipCountry['nev_name'] == country]
				coords = getFeatures(df)

				out_img, out_transform 	= 	mask(UnBuff, shapes=coords, crop=True)
				out_img = out_img[0]
				
				with rasterio.Env():
					profile = lulc.profile
					profile = {k: v for k, v in lulc.profile.items() if k not in ['blockxsize', 'blockysize']}
					profile.update(
						dtype=rasterio.uint8,
						count=1,
						driver="GTiff",
						height=out_img.shape[0],
						width=out_img.shape[1],
						transform=out_transform,
						compression = 'lzw')
					


					with rasterio.open(str("/scratch/PI/gdaily/Jeff/worldBank/vegMaps7/" + country + "W.tif"), 'w', **profile, tile = False) as dst:
						dst.write_band(1,out_img)





