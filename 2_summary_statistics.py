# -*- coding: utf-8 -*-
"""
Created on Thu Oct  3 07:35:14 2024

@author: archibaldc
"""

# Summarise 
# - SSP1.2.6 2041-2060 

#Time period 2041-2060:
#  Ensemble average temperature: 23.28°C
#  Temperature difference compared to historical worldclim data: 1.54°C
#  Temperature difference compared to CSIRO historical data: 1.31°C
    
# - SSP: ssp370

# Time period 2041-2060:
#  Ensemble average temperature: 23.83°C
#  Temperature difference compared to historical worldclim data: 2.09°C
#  Temperature difference compared to CSIRO historical data: 1.86°C

################ Set up ################
# Load python modules
import numpy as np
import pandas as pd
import rasterio
from rasterio.enums import Resampling
from rasterio.fill import fillnodata
from rasterio.warp import reproject

# NLUM
# Open NLUM mask raster and get metadata
with rasterio.open(r'N:\Data-Master\National_Landuse_Map\NLUM_2010-11_mask.tif') as rst:
   
    # Read geotiff to numpy array
    NLUM_mask = rst.read(1) # Loads a 2D masked array with nodata masked out
    
    # Load a 2D masked array with nodata masked out
    NLUM_ID_raster = rst.read(1, masked=True) 
    
    # Create a 0/1 binary mask
    NLUM_mask_bin = NLUM_ID_raster.mask == False
    
    # Get transform and metadata and update parameters
    meta = rst.meta.copy()
    meta.update(compress='lzw', driver='GTiff', nodata='255') # dtype='int32', nodata='-99')
    [meta.pop(key) for key in ['dtype', 'nodata']] # Need to add dtype and nodata manually when exporting GeoTiffs
    
    # Set up some data structures to enable conversion on 1D arrays to 2D
    array_2D = np.zeros(NLUM_ID_raster.shape)
    xy = np.nonzero(NLUM_mask)


cell_zones_df_file = "N:\LUF-Modelling\Biodiversity-footprint\Data\Agriculture\cell_zones_df.h5"

cell_df = pd.read_hdf(cell_zones_df_file, columns=['CELL_ID','X','Y','CELL_HA'])
      

speciesList = ['Calyptorhynchus_baudinii', 'Hemibelideus_lemuroides', 'Malurus_coronatus', 'Phascolarctos_cinereus', 'Pseudochirops_archeri', 'Pseudochirulus_cinereus']

for species in  speciesList: 
    
    print("Start for "+ species)
    
    # Working directory
    wd = "N:\\Current-Users\\Carla-Archibald\\WWF\\habitat_suit_data\\" 
    
    # Output directory
    species_wd = wd + species + "\\"
    
    # Build data frame
    df_qwcna = pd.DataFrame({'Species':[],                                                                     # DONE
    'EOO based on occurance points area [km2]':[],                                                             # DONE
    'Historical quality weighted habitat area [km2]':[],                                                       # DONE                                                            
    '1.5 degree quality weighted habitat area (max) [km2]':[],                                                # DONE
    '1.5 degree absolute change in quality weighted habitat area (max) [km2]':[],                             # DONE
    '1.5 degree percent change in quality weighted habitat area (max) [%]':[],                                # DONE
    '1.5 degree absolute climate refugia (max) [km2]':[],
    '1.5 degree percentage climate refugia (max) [%]':[],
    '2.0 degree quality weighted habitat area (max) [km2]':[],                            
    '2.0 degree absolute change in quality weighted habitat area (max) [km2]':[],
    '2.0 degree percent change in quality weighted habitat area (max) [%]':[],
    '2.0 degree absolute climate refugia (max) [km2]':[],
    '2.0 degree percentage climate refugia (max) [%]':[]},
      dtype="float32")
    
    # Assign character columns as strings                       
    df_qwcna = df_qwcna.astype(dtype= {"Species":"string"})
        
    # Fill in df with Taxa, Species and Climate Scenario
    df_qwcna.at[0,'Species'] = species    
    
    # Open a new GeoTiFF file
    eooFile = species_wd + species + "_Extent_of_occurrence_buffered.tif"
   
    with rasterio.open(eooFile, 'r') as src:
        eoo_array = src.read()
        
        valid_indices = NLUM_mask_bin
        
        valid_values = eoo_array[0][valid_indices]

        # Flatten 2D array to 1D array of valid values only
        cell_df['EOO'] = valid_values
      
        # Sum
        eooSum = round(cell_df['EOO'].sum(), 0)

        # Add into df
        df_qwcna.at[0,'EOO based on occurance points area [km2]'] = eooSum
    
    # Open historical raster
    histFile = species_wd + "\\" + species + '_historic_baseline_1990_AUS_5km_EnviroSuit.tif'
    with rasterio.open(histFile) as src:
        dst_array_5km = src.read(1) # loads a 2D masked array of the year 2100         
    
        # Sum the array, should = 100
        dst_array_5km_sum = np.sum(dst_array_5km)
        
        # enumerate bands
        nbands = src.count
       
        # create a destination array
        dst_array = np.zeros((meta.get('height'), meta.get('width')), np.float64) - 9999
        
        # begin resampling for bands
        for i in range(1, nbands + 1):
              
            # reproject/resample input raster to match NLUM mask (meta)
            reproject(rasterio.band(src,1), dst_array, src_crs = src.crs, src_nodata=0, src_transform = src.transform, dst_nodata=0, dst_transform = meta.get('transform'), dst_crs = meta.get('crs'), resampling = Resampling.nearest)
    
            # fill nodata using inverse distance weighted averaging and mask to NLUM
            dst_array_filled = fillnodata(dst_array, mask=NLUM_mask, max_search_distance=100.0, smoothing_iterations=0)
            
            # recallibrate from 5km to 1km
            dst_array_clipped_div = np.float64(np.where(NLUM_mask == 1, dst_array_filled / 100, 0))
            dst_array_clipped_div[dst_array_clipped_div > 1] = 0
            np.max(dst_array_clipped_div)
               
            # set no data based on NLUM 
            dst_array_clipped_div_recal_out = np.where(NLUM_mask == 1, dst_array_clipped_div, -9999)
    
            # Round and add data to cell_df dataframe
            dst_array_clipped_div_recal_out_base = dst_array_clipped_div_recal_out[NLUM_mask == 1]    
                
            cell_df['ENVIRO-SUIT_HISTORICAL_1km'] = dst_array_clipped_div_recal_out_base.astype(np.float64)
            cell_df['ENVIRO-SUIT_HISTORICAL_1km'] = cell_df['ENVIRO-SUIT_HISTORICAL_1km'].replace({-9999.0: 0})    
            cell_df['ENVIRO-SUIT_HISTORICAL-EOO_Bound-1km'] = cell_df['ENVIRO-SUIT_HISTORICAL_1km'] * cell_df['EOO']
            
            histSum = round(cell_df['ENVIRO-SUIT_HISTORICAL-EOO_Bound-1km'].sum(), 0)
                     
    
        # Add into df
        df_qwcna.at[0,'Historical quality weighted habitat area [km2]'] = histSum
                       
     
    # 1.5 warming scenario
    ssp126_2050_File = species_wd + species + '_GCM-Ensembles_ssp126_2050_AUS_5km_EnviroSuit_max.tif'
    with rasterio.open(ssp126_2050_File) as src:
        dst_array_5km = src.read(1) # loads a 2D masked array of the year 2100         
    
        # Sum the array, should = 100
        dst_array_5km_sum = np.sum(dst_array_5km)
        
        # enumerate bands
        nbands = src.count
       
        # create a destination array
        dst_array = np.zeros((meta.get('height'), meta.get('width')), np.float64) - 9999
        
        # begin resampling for bands
        for i in range(1, nbands + 1):
              
            # reproject/resample input raster to match NLUM mask (meta)
            reproject(rasterio.band(src,1), dst_array, src_crs = src.crs, src_nodata=0, src_transform = src.transform, dst_nodata=0, dst_transform = meta.get('transform'), dst_crs = meta.get('crs'), resampling = Resampling.nearest)
    
            # fill nodata using inverse distance weighted averaging and mask to NLUM
            dst_array_filled = fillnodata(dst_array, mask=NLUM_mask, max_search_distance=100.0, smoothing_iterations=0)
            
            # recallibrate from 5km to 1km
            dst_array_clipped_div = np.float64(np.where(NLUM_mask == 1, dst_array_filled / 100, 0))
            dst_array_clipped_div[dst_array_clipped_div > 1] = 0
            np.max(dst_array_clipped_div)
               
            # set no data based on NLUM 
            dst_array_clipped_div_recal_out = np.where(NLUM_mask == 1, dst_array_clipped_div, -9999)
    
            # Round and add data to cell_df dataframe
            dst_array_clipped_div_recal_out_base = dst_array_clipped_div_recal_out[NLUM_mask == 1]    
                
            cell_df['ENVIRO-SUIT_1.5_warming_1km'] = dst_array_clipped_div_recal_out_base.astype(np.float64)
            cell_df['ENVIRO-SUIT_1.5_warming_1km'] = cell_df['ENVIRO-SUIT_1.5_warming_1km'].replace({-9999.0: 0})    
            cell_df['ENVIRO-SUIT_1.5_warming_1km_EOO_Bound-1km'] = cell_df['ENVIRO-SUIT_1.5_warming_1km'] * cell_df['EOO']
            cell_df['REFUGIA_1.5_warming_1km'] = cell_df['ENVIRO-SUIT_HISTORICAL-EOO_Bound-1km'] * cell_df['ENVIRO-SUIT_1.5_warming_1km'] 

            ssp126_2050 = round(cell_df['ENVIRO-SUIT_1.5_warming_1km_EOO_Bound-1km'].sum(), 0)
            
            # Calculate absolute change by minusing the historical by the future suitability and divide by 100 to get the quality weighted km2      
            absChange = round(ssp126_2050 - histSum / 100 , 0)
           
            # Convert the above number to a percentage
            percChange =  round(((ssp126_2050 - histSum)/  histSum) * 100, 0)

            # Refugia
            absRefugia = round(cell_df['REFUGIA_1.5_warming_1km'].sum(), 0)

            # Refugia
            percRefugia = round((absRefugia /  histSum) * 100, 0)
    
            # Add into df
            df_qwcna.at[0,'1.5 degree quality weighted habitat area (max) [km2]'] = ssp126_2050
            df_qwcna.at[0,'1.5 degree absolute change in quality weighted habitat area (max) [km2]'] = absChange
            df_qwcna.at[0,'1.5 degree percent change in quality weighted habitat area (max) [%]'] = percChange
            df_qwcna.at[0,'1.5 degree absolute climate refugia (max) [km2]'] = absRefugia
            df_qwcna.at[0,'1.5 degree percentage climate refugia (max) [%]'] = percRefugia


    # 2.0 warming scenario
    ssp370_2050_File = species_wd + species + '_GCM-Ensembles_ssp370_2050_AUS_5km_EnviroSuit_max.tif'
    with rasterio.open(ssp370_2050_File) as src:
        dst_array_5km = src.read(1) # loads a 2D masked array of the year 2100         
    
        # Sum the array, should = 100
        dst_array_5km_sum = np.sum(dst_array_5km)
        
        # enumerate bands
        nbands = src.count
       
        # create a destination array
        dst_array = np.zeros((meta.get('height'), meta.get('width')), np.float64) - 9999
        
        # begin resampling for bands
        for i in range(1, nbands + 1):
              
            # reproject/resample input raster to match NLUM mask (meta)
            reproject(rasterio.band(src,1), dst_array, src_crs = src.crs, src_nodata=0, src_transform = src.transform, dst_nodata=0, dst_transform = meta.get('transform'), dst_crs = meta.get('crs'), resampling = Resampling.nearest)
    
            # fill nodata using inverse distance weighted averaging and mask to NLUM
            dst_array_filled = fillnodata(dst_array, mask=NLUM_mask, max_search_distance=100.0, smoothing_iterations=0)
            
            # recallibrate from 5km to 1km
            dst_array_clipped_div = np.float64(np.where(NLUM_mask == 1, dst_array_filled / 100, 0))
            dst_array_clipped_div[dst_array_clipped_div > 1] = 0
            np.max(dst_array_clipped_div)
               
            # set no data based on NLUM 
            dst_array_clipped_div_recal_out = np.where(NLUM_mask == 1, dst_array_clipped_div, -9999)
    
            # Round and add data to cell_df dataframe
            dst_array_clipped_div_recal_out_base = dst_array_clipped_div_recal_out[NLUM_mask == 1]    
                
            cell_df['ENVIRO-SUIT_2.0_warming_1km'] = dst_array_clipped_div_recal_out_base.astype(np.float64)
            cell_df['ENVIRO-SUIT_2.0_warming_1km'] = cell_df['ENVIRO-SUIT_2.0_warming_1km'].replace({-9999.0: 0})    
            cell_df['ENVIRO-SUIT_2.0_warming_1km_EOO_Bound-1km'] = cell_df['ENVIRO-SUIT_2.0_warming_1km'] * cell_df['EOO']
            cell_df['REFUGIA_2.0_warming_1km'] = cell_df['ENVIRO-SUIT_HISTORICAL-EOO_Bound-1km'] * cell_df['ENVIRO-SUIT_2.0_warming_1km'] 


            ssp370_2050 = round(cell_df['ENVIRO-SUIT_2.0_warming_1km_EOO_Bound-1km'].sum(), 0)
            
            # Calculate absolute change by minusing the historical by the future suitability and divide by 100 to get the quality weighted km2      
            absChange = round(ssp370_2050 - histSum / 100 , 0)  
           
            # Convert the above number to a percentage
            percChange =  round(((ssp370_2050 - histSum)/  histSum) * 100, 0)
            
            # Refugia
            absRefugia = round(cell_df['REFUGIA_2.0_warming_1km'].sum(), 0)

            # Refugia
            percRefugia = round((absRefugia/  histSum) * 100, 0)
            
            # Add into df
            df_qwcna.at[0,'2.0 degree quality weighted habitat area (max) [km2]'] = ssp370_2050
            df_qwcna.at[0,'2.0 degree absolute change in quality weighted habitat area (max) [km2]'] = absChange
            df_qwcna.at[0,'2.0 degree percent change in quality weighted habitat area (max) [%]'] = percChange
            df_qwcna.at[0,'2.0 degree absolute climate refugia (max) [km2]'] = absRefugia
            df_qwcna.at[0,'2.0 degree percentage climate refugia (max) [%]'] = percRefugia
   

    df_qwcna.to_csv(species_wd + "Warming-scenario-summary_" + species + "_max.csv", index=False)
    print("Done for "+ species)
    
        
### END :) 