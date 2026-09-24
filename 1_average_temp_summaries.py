# -*- coding: utf-8 -*-
"""
Created on Thu Sep 19 13:20:02 2024

@author: archibaldc
"""
# Timelines

# National emission reductions targets, set any time between October and Feburary

import rasterio
import numpy as np


# File paths
historical_file = "N:/Data-Master/WorldClim_CMIP6/Australia/Archive/Historical_1970-2000/AUS_wc2.1_2.5m_bio_1.tif"

future_files = {
     'ssp126': {
        '2081-2100': [
            "N:/Data-Master/WorldClim_CMIP6/Australia/Australia_5km/Future_scenarios_2020-2100/BCC-CSM2-MR/ssp126/wc2.1_2.5m_bioc_BCC-CSM2-MR_ssp126_2081-2100_AUS_5km.tif",
            "N:/Data-Master/WorldClim_CMIP6/Australia/Australia_5km/Future_scenarios_2020-2100/CanESM5/ssp126/wc2.1_2.5m_bioc_CanESM5_ssp126_2081-2100_AUS_5km.tif",
            "N:/Data-Master/WorldClim_CMIP6/Australia/Australia_5km/Future_scenarios_2020-2100/CNRM-CM6-1/ssp126/wc2.1_2.5m_bioc_CNRM-CM6-1_ssp126_2081-2100_AUS_5km.tif",
            "N:/Data-Master/WorldClim_CMIP6/Australia/Australia_5km/Future_scenarios_2020-2100/CNRM-ESM2-1/ssp126/wc2.1_2.5m_bioc_CNRM-ESM2-1_ssp126_2081-2100_AUS_5km.tif",
            "N:/Data-Master/WorldClim_CMIP6/Australia/Australia_5km/Future_scenarios_2020-2100/IPSL-CM6A-LR/ssp126/wc2.1_2.5m_bioc_IPSL-CM6A-LR_ssp126_2081-2100_AUS_5km.tif",
            "N:/Data-Master/WorldClim_CMIP6/Australia/Australia_5km/Future_scenarios_2020-2100/MIROC6/ssp126/wc2.1_2.5m_bioc_MIROC6_ssp126_2081-2100_AUS_5km.tif",
            "N:/Data-Master/WorldClim_CMIP6/Australia/Australia_5km/Future_scenarios_2020-2100/MIROC-ES2L/ssp126/wc2.1_2.5m_bioc_MIROC-ES2L_ssp126_2081-2100_AUS_5km.tif",
            "N:/Data-Master/WorldClim_CMIP6/Australia/Australia_5km/Future_scenarios_2020-2100/MRI-ESM2-0/ssp126/wc2.1_2.5m_bioc_MRI-ESM2-0_ssp126_2081-2100_AUS_5km.tif"
        ],
        '2061-2080': [
            "N:/Data-Master/WorldClim_CMIP6/Australia/Australia_5km/Future_scenarios_2020-2100/BCC-CSM2-MR/ssp126/wc2.1_2.5m_bioc_BCC-CSM2-MR_ssp126_2061-2080_AUS_5km.tif",
            "N:/Data-Master/WorldClim_CMIP6/Australia/Australia_5km/Future_scenarios_2020-2100/CanESM5/ssp126/wc2.1_2.5m_bioc_CanESM5_ssp126_2061-2080_AUS_5km.tif",
            "N:/Data-Master/WorldClim_CMIP6/Australia/Australia_5km/Future_scenarios_2020-2100/CNRM-CM6-1/ssp126/wc2.1_2.5m_bioc_CNRM-CM6-1_ssp126_2061-2080_AUS_5km.tif",
            "N:/Data-Master/WorldClim_CMIP6/Australia/Australia_5km/Future_scenarios_2020-2100/CNRM-ESM2-1/ssp126/wc2.1_2.5m_bioc_CNRM-ESM2-1_ssp126_2061-2080_AUS_5km.tif",
            "N:/Data-Master/WorldClim_CMIP6/Australia/Australia_5km/Future_scenarios_2020-2100/IPSL-CM6A-LR/ssp126/wc2.1_2.5m_bioc_IPSL-CM6A-LR_ssp126_2061-2080_AUS_5km.tif",
            "N:/Data-Master/WorldClim_CMIP6/Australia/Australia_5km/Future_scenarios_2020-2100/MIROC6/ssp126/wc2.1_2.5m_bioc_MIROC6_ssp126_2061-2080_AUS_5km.tif",
            "N:/Data-Master/WorldClim_CMIP6/Australia/Australia_5km/Future_scenarios_2020-2100/MIROC-ES2L/ssp126/wc2.1_2.5m_bioc_MIROC-ES2L_ssp126_2061-2080_AUS_5km.tif",
            "N:/Data-Master/WorldClim_CMIP6/Australia/Australia_5km/Future_scenarios_2020-2100/MRI-ESM2-0/ssp126/wc2.1_2.5m_bioc_MRI-ESM2-0_ssp126_2061-2080_AUS_5km.tif"
        ],
        '2041-2060': [
            "N:/Data-Master/WorldClim_CMIP6/Australia/Australia_5km/Future_scenarios_2020-2100/BCC-CSM2-MR/ssp126/wc2.1_2.5m_bioc_BCC-CSM2-MR_ssp126_2041-2060_AUS_5km.tif",
            "N:/Data-Master/WorldClim_CMIP6/Australia/Australia_5km/Future_scenarios_2020-2100/CanESM5/ssp126/wc2.1_2.5m_bioc_CanESM5_ssp126_2041-2060_AUS_5km.tif",
            "N:/Data-Master/WorldClim_CMIP6/Australia/Australia_5km/Future_scenarios_2020-2100/CNRM-CM6-1/ssp126/wc2.1_2.5m_bioc_CNRM-CM6-1_ssp126_2041-2060_AUS_5km.tif",
            "N:/Data-Master/WorldClim_CMIP6/Australia/Australia_5km/Future_scenarios_2020-2100/CNRM-ESM2-1/ssp126/wc2.1_2.5m_bioc_CNRM-ESM2-1_ssp126_2041-2060_AUS_5km.tif",
            "N:/Data-Master/WorldClim_CMIP6/Australia/Australia_5km/Future_scenarios_2020-2100/IPSL-CM6A-LR/ssp126/wc2.1_2.5m_bioc_IPSL-CM6A-LR_ssp126_2041-2060_AUS_5km.tif",
            "N:/Data-Master/WorldClim_CMIP6/Australia/Australia_5km/Future_scenarios_2020-2100/MIROC6/ssp126/wc2.1_2.5m_bioc_MIROC6_ssp126_2041-2060_AUS_5km.tif",
            "N:/Data-Master/WorldClim_CMIP6/Australia/Australia_5km/Future_scenarios_2020-2100/MIROC-ES2L/ssp126/wc2.1_2.5m_bioc_MIROC-ES2L_ssp126_2041-2060_AUS_5km.tif",
            "N:/Data-Master/WorldClim_CMIP6/Australia/Australia_5km/Future_scenarios_2020-2100/MRI-ESM2-0/ssp126/wc2.1_2.5m_bioc_MRI-ESM2-0_ssp126_2041-2060_AUS_5km.tif"
        ],
        '2021-2040': [
            "N:/Data-Master/WorldClim_CMIP6/Australia/Australia_5km/Future_scenarios_2020-2100/CanESM5/ssp126/wc2.1_2.5m_bioc_CanESM5_ssp126_2021-2040_AUS_5km.tif",
            "N:/Data-Master/WorldClim_CMIP6/Australia/Australia_5km/Future_scenarios_2020-2100/CNRM-CM6-1/ssp126/wc2.1_2.5m_bioc_CNRM-CM6-1_ssp126_2021-2040_AUS_5km.tif",
            "N:/Data-Master/WorldClim_CMIP6/Australia/Australia_5km/Future_scenarios_2020-2100/CNRM-ESM2-1/ssp126/wc2.1_2.5m_bioc_CNRM-ESM2-1_ssp126_2021-2040_AUS_5km.tif",
            "N:/Data-Master/WorldClim_CMIP6/Australia/Australia_5km/Future_scenarios_2020-2100/IPSL-CM6A-LR/ssp126/wc2.1_2.5m_bioc_IPSL-CM6A-LR_ssp126_2021-2040_AUS_5km.tif",
            "N:/Data-Master/WorldClim_CMIP6/Australia/Australia_5km/Future_scenarios_2020-2100/MIROC6/ssp126/wc2.1_2.5m_bioc_MIROC6_ssp126_2021-2040_AUS_5km.tif",
            "N:/Data-Master/WorldClim_CMIP6/Australia/Australia_5km/Future_scenarios_2020-2100/MIROC-ES2L/ssp126/wc2.1_2.5m_bioc_MIROC-ES2L_ssp126_2021-2040_AUS_5km.tif",
            "N:/Data-Master/WorldClim_CMIP6/Australia/Australia_5km/Future_scenarios_2020-2100/MRI-ESM2-0/ssp126/wc2.1_2.5m_bioc_MRI-ESM2-0_ssp126_2021-2040_AUS_5km.tif"
        ]
        
    },
   
    'ssp245': {
        '2081-2100': [
            "N:/Data-Master/WorldClim_CMIP6/Australia/Australia_5km/Future_scenarios_2020-2100/BCC-CSM2-MR/ssp245/wc2.1_2.5m_bioc_BCC-CSM2-MR_ssp245_2081-2100_AUS_5km.tif",
            "N:/Data-Master/WorldClim_CMIP6/Australia/Australia_5km/Future_scenarios_2020-2100/CanESM5/ssp245/wc2.1_2.5m_bioc_CanESM5_ssp245_2081-2100_AUS_5km.tif",
            "N:/Data-Master/WorldClim_CMIP6/Australia/Australia_5km/Future_scenarios_2020-2100/CNRM-CM6-1/ssp245/wc2.1_2.5m_bioc_CNRM-CM6-1_ssp245_2081-2100_AUS_5km.tif",
            "N:/Data-Master/WorldClim_CMIP6/Australia/Australia_5km/Future_scenarios_2020-2100/CNRM-ESM2-1/ssp245/wc2.1_2.5m_bioc_CNRM-ESM2-1_ssp245_2081-2100_AUS_5km.tif",
            "N:/Data-Master/WorldClim_CMIP6/Australia/Australia_5km/Future_scenarios_2020-2100/IPSL-CM6A-LR/ssp245/wc2.1_2.5m_bioc_IPSL-CM6A-LR_ssp245_2081-2100_AUS_5km.tif",
            "N:/Data-Master/WorldClim_CMIP6/Australia/Australia_5km/Future_scenarios_2020-2100/MIROC6/ssp245/wc2.1_2.5m_bioc_MIROC6_ssp245_2081-2100_AUS_5km.tif",
            "N:/Data-Master/WorldClim_CMIP6/Australia/Australia_5km/Future_scenarios_2020-2100/MIROC-ES2L/ssp245/wc2.1_2.5m_bioc_MIROC-ES2L_ssp245_2081-2100_AUS_5km.tif",
            "N:/Data-Master/WorldClim_CMIP6/Australia/Australia_5km/Future_scenarios_2020-2100/MRI-ESM2-0/ssp245/wc2.1_2.5m_bioc_MRI-ESM2-0_ssp245_2081-2100_AUS_5km.tif"
        ],
        '2061-2080': [
            "N:/Data-Master/WorldClim_CMIP6/Australia/Australia_5km/Future_scenarios_2020-2100/BCC-CSM2-MR/ssp245/wc2.1_2.5m_bioc_BCC-CSM2-MR_ssp245_2061-2080_AUS_5km.tif",
            "N:/Data-Master/WorldClim_CMIP6/Australia/Australia_5km/Future_scenarios_2020-2100/CanESM5/ssp245/wc2.1_2.5m_bioc_CanESM5_ssp245_2061-2080_AUS_5km.tif",
            "N:/Data-Master/WorldClim_CMIP6/Australia/Australia_5km/Future_scenarios_2020-2100/CNRM-CM6-1/ssp245/wc2.1_2.5m_bioc_CNRM-CM6-1_ssp245_2061-2080_AUS_5km.tif",
            "N:/Data-Master/WorldClim_CMIP6/Australia/Australia_5km/Future_scenarios_2020-2100/CNRM-ESM2-1/ssp245/wc2.1_2.5m_bioc_CNRM-ESM2-1_ssp245_2061-2080_AUS_5km.tif",
            "N:/Data-Master/WorldClim_CMIP6/Australia/Australia_5km/Future_scenarios_2020-2100/IPSL-CM6A-LR/ssp245/wc2.1_2.5m_bioc_IPSL-CM6A-LR_ssp245_2061-2080_AUS_5km.tif",
            "N:/Data-Master/WorldClim_CMIP6/Australia/Australia_5km/Future_scenarios_2020-2100/MIROC6/ssp245/wc2.1_2.5m_bioc_MIROC6_ssp245_2061-2080_AUS_5km.tif",
            "N:/Data-Master/WorldClim_CMIP6/Australia/Australia_5km/Future_scenarios_2020-2100/MIROC-ES2L/ssp245/wc2.1_2.5m_bioc_MIROC-ES2L_ssp245_2061-2080_AUS_5km.tif",
            "N:/Data-Master/WorldClim_CMIP6/Australia/Australia_5km/Future_scenarios_2020-2100/MRI-ESM2-0/ssp245/wc2.1_2.5m_bioc_MRI-ESM2-0_ssp245_2061-2080_AUS_5km.tif"
        ],
        '2041-2060': [
            "N:/Data-Master/WorldClim_CMIP6/Australia/Australia_5km/Future_scenarios_2020-2100/BCC-CSM2-MR/ssp245/wc2.1_2.5m_bioc_BCC-CSM2-MR_ssp245_2041-2060_AUS_5km.tif",
            "N:/Data-Master/WorldClim_CMIP6/Australia/Australia_5km/Future_scenarios_2020-2100/CanESM5/ssp245/wc2.1_2.5m_bioc_CanESM5_ssp245_2041-2060_AUS_5km.tif",
            "N:/Data-Master/WorldClim_CMIP6/Australia/Australia_5km/Future_scenarios_2020-2100/CNRM-CM6-1/ssp245/wc2.1_2.5m_bioc_CNRM-CM6-1_ssp245_2041-2060_AUS_5km.tif",
            "N:/Data-Master/WorldClim_CMIP6/Australia/Australia_5km/Future_scenarios_2020-2100/CNRM-ESM2-1/ssp245/wc2.1_2.5m_bioc_CNRM-ESM2-1_ssp245_2041-2060_AUS_5km.tif",
            "N:/Data-Master/WorldClim_CMIP6/Australia/Australia_5km/Future_scenarios_2020-2100/IPSL-CM6A-LR/ssp245/wc2.1_2.5m_bioc_IPSL-CM6A-LR_ssp245_2041-2060_AUS_5km.tif",
            "N:/Data-Master/WorldClim_CMIP6/Australia/Australia_5km/Future_scenarios_2020-2100/MIROC6/ssp245/wc2.1_2.5m_bioc_MIROC6_ssp245_2041-2060_AUS_5km.tif",
            "N:/Data-Master/WorldClim_CMIP6/Australia/Australia_5km/Future_scenarios_2020-2100/MIROC-ES2L/ssp245/wc2.1_2.5m_bioc_MIROC-ES2L_ssp245_2041-2060_AUS_5km.tif",
            "N:/Data-Master/WorldClim_CMIP6/Australia/Australia_5km/Future_scenarios_2020-2100/MRI-ESM2-0/ssp245/wc2.1_2.5m_bioc_MRI-ESM2-0_ssp245_2041-2060_AUS_5km.tif"
        ],
        '2021-2040': [
            "N:/Data-Master/WorldClim_CMIP6/Australia/Australia_5km/Future_scenarios_2020-2100/CanESM5/ssp245/wc2.1_2.5m_bioc_CanESM5_ssp245_2021-2040_AUS_5km.tif",
            "N:/Data-Master/WorldClim_CMIP6/Australia/Australia_5km/Future_scenarios_2020-2100/CNRM-CM6-1/ssp245/wc2.1_2.5m_bioc_CNRM-CM6-1_ssp245_2021-2040_AUS_5km.tif",
            "N:/Data-Master/WorldClim_CMIP6/Australia/Australia_5km/Future_scenarios_2020-2100/CNRM-ESM2-1/ssp245/wc2.1_2.5m_bioc_CNRM-ESM2-1_ssp245_2021-2040_AUS_5km.tif",
            "N:/Data-Master/WorldClim_CMIP6/Australia/Australia_5km/Future_scenarios_2020-2100/MIROC6/ssp245/wc2.1_2.5m_bioc_MIROC6_ssp245_2021-2040_AUS_5km.tif",
            "N:/Data-Master/WorldClim_CMIP6/Australia/Australia_5km/Future_scenarios_2020-2100/MIROC-ES2L/ssp245/wc2.1_2.5m_bioc_MIROC-ES2L_ssp245_2021-2040_AUS_5km.tif",
            "N:/Data-Master/WorldClim_CMIP6/Australia/Australia_5km/Future_scenarios_2020-2100/MRI-ESM2-0/ssp245/wc2.1_2.5m_bioc_MRI-ESM2-0_ssp245_2021-2040_AUS_5km.tif"
        ]

    
    },
    
    'ssp370': {
        '2081-2100': [
            "N:/Data-Master/WorldClim_CMIP6/Australia/Australia_5km/Future_scenarios_2020-2100/BCC-CSM2-MR/ssp370/wc2.1_2.5m_bioc_BCC-CSM2-MR_ssp370_2081-2100_AUS_5km.tif",
            "N:/Data-Master/WorldClim_CMIP6/Australia/Australia_5km/Future_scenarios_2020-2100/CanESM5/ssp370/wc2.1_2.5m_bioc_CanESM5_ssp370_2081-2100_AUS_5km.tif",
            "N:/Data-Master/WorldClim_CMIP6/Australia/Australia_5km/Future_scenarios_2020-2100/CNRM-CM6-1/ssp370/wc2.1_2.5m_bioc_CNRM-CM6-1_ssp370_2081-2100_AUS_5km.tif",
            "N:/Data-Master/WorldClim_CMIP6/Australia/Australia_5km/Future_scenarios_2020-2100/CNRM-ESM2-1/ssp370/wc2.1_2.5m_bioc_CNRM-ESM2-1_ssp370_2081-2100_AUS_5km.tif",
            "N:/Data-Master/WorldClim_CMIP6/Australia/Australia_5km/Future_scenarios_2020-2100/IPSL-CM6A-LR/ssp370/wc2.1_2.5m_bioc_IPSL-CM6A-LR_ssp370_2081-2100_AUS_5km.tif",
            "N:/Data-Master/WorldClim_CMIP6/Australia/Australia_5km/Future_scenarios_2020-2100/MIROC6/ssp370/wc2.1_2.5m_bioc_MIROC6_ssp370_2081-2100_AUS_5km.tif",
            "N:/Data-Master/WorldClim_CMIP6/Australia/Australia_5km/Future_scenarios_2020-2100/MIROC-ES2L/ssp370/wc2.1_2.5m_bioc_MIROC-ES2L_ssp370_2081-2100_AUS_5km.tif",
            "N:/Data-Master/WorldClim_CMIP6/Australia/Australia_5km/Future_scenarios_2020-2100/MRI-ESM2-0/ssp370/wc2.1_2.5m_bioc_MRI-ESM2-0_ssp370_2081-2100_AUS_5km.tif"
        ],
        '2061-2080': [
            "N:/Data-Master/WorldClim_CMIP6/Australia/Australia_5km/Future_scenarios_2020-2100/BCC-CSM2-MR/ssp370/wc2.1_2.5m_bioc_BCC-CSM2-MR_ssp370_2061-2080_AUS_5km.tif",
            "N:/Data-Master/WorldClim_CMIP6/Australia/Australia_5km/Future_scenarios_2020-2100/CanESM5/ssp370/wc2.1_2.5m_bioc_CanESM5_ssp370_2061-2080_AUS_5km.tif",
            "N:/Data-Master/WorldClim_CMIP6/Australia/Australia_5km/Future_scenarios_2020-2100/CNRM-CM6-1/ssp370/wc2.1_2.5m_bioc_CNRM-CM6-1_ssp370_2061-2080_AUS_5km.tif",
            "N:/Data-Master/WorldClim_CMIP6/Australia/Australia_5km/Future_scenarios_2020-2100/CNRM-ESM2-1/ssp370/wc2.1_2.5m_bioc_CNRM-ESM2-1_ssp370_2061-2080_AUS_5km.tif",
            "N:/Data-Master/WorldClim_CMIP6/Australia/Australia_5km/Future_scenarios_2020-2100/IPSL-CM6A-LR/ssp370/wc2.1_2.5m_bioc_IPSL-CM6A-LR_ssp370_2061-2080_AUS_5km.tif",
            "N:/Data-Master/WorldClim_CMIP6/Australia/Australia_5km/Future_scenarios_2020-2100/MIROC6/ssp370/wc2.1_2.5m_bioc_MIROC6_ssp370_2061-2080_AUS_5km.tif",
            "N:/Data-Master/WorldClim_CMIP6/Australia/Australia_5km/Future_scenarios_2020-2100/MIROC-ES2L/ssp370/wc2.1_2.5m_bioc_MIROC-ES2L_ssp370_2061-2080_AUS_5km.tif",
            "N:/Data-Master/WorldClim_CMIP6/Australia/Australia_5km/Future_scenarios_2020-2100/MRI-ESM2-0/ssp370/wc2.1_2.5m_bioc_MRI-ESM2-0_ssp370_2061-2080_AUS_5km.tif"
        ],
        '2041-2060': [
            "N:/Data-Master/WorldClim_CMIP6/Australia/Australia_5km/Future_scenarios_2020-2100/BCC-CSM2-MR/ssp370/wc2.1_2.5m_bioc_BCC-CSM2-MR_ssp370_2041-2060_AUS_5km.tif",
            "N:/Data-Master/WorldClim_CMIP6/Australia/Australia_5km/Future_scenarios_2020-2100/CanESM5/ssp370/wc2.1_2.5m_bioc_CanESM5_ssp370_2041-2060_AUS_5km.tif",
            "N:/Data-Master/WorldClim_CMIP6/Australia/Australia_5km/Future_scenarios_2020-2100/CNRM-CM6-1/ssp370/wc2.1_2.5m_bioc_CNRM-CM6-1_ssp370_2041-2060_AUS_5km.tif",
            "N:/Data-Master/WorldClim_CMIP6/Australia/Australia_5km/Future_scenarios_2020-2100/CNRM-ESM2-1/ssp370/wc2.1_2.5m_bioc_CNRM-ESM2-1_ssp370_2041-2060_AUS_5km.tif",
            "N:/Data-Master/WorldClim_CMIP6/Australia/Australia_5km/Future_scenarios_2020-2100/IPSL-CM6A-LR/ssp370/wc2.1_2.5m_bioc_IPSL-CM6A-LR_ssp370_2041-2060_AUS_5km.tif",
            "N:/Data-Master/WorldClim_CMIP6/Australia/Australia_5km/Future_scenarios_2020-2100/MIROC6/ssp370/wc2.1_2.5m_bioc_MIROC6_ssp370_2041-2060_AUS_5km.tif",
            "N:/Data-Master/WorldClim_CMIP6/Australia/Australia_5km/Future_scenarios_2020-2100/MIROC-ES2L/ssp370/wc2.1_2.5m_bioc_MIROC-ES2L_ssp370_2041-2060_AUS_5km.tif",
            "N:/Data-Master/WorldClim_CMIP6/Australia/Australia_5km/Future_scenarios_2020-2100/MRI-ESM2-0/ssp370/wc2.1_2.5m_bioc_MRI-ESM2-0_ssp370_2041-2060_AUS_5km.tif"
        ],
        '2021-2040': [
            "N:/Data-Master/WorldClim_CMIP6/Australia/Australia_5km/Future_scenarios_2020-2100/CanESM5/ssp370/wc2.1_2.5m_bioc_CanESM5_ssp370_2021-2040_AUS_5km.tif",
            "N:/Data-Master/WorldClim_CMIP6/Australia/Australia_5km/Future_scenarios_2020-2100/CNRM-CM6-1/ssp370/wc2.1_2.5m_bioc_CNRM-CM6-1_ssp370_2021-2040_AUS_5km.tif",
            "N:/Data-Master/WorldClim_CMIP6/Australia/Australia_5km/Future_scenarios_2020-2100/CNRM-ESM2-1/ssp370/wc2.1_2.5m_bioc_CNRM-ESM2-1_ssp370_2021-2040_AUS_5km.tif",
            "N:/Data-Master/WorldClim_CMIP6/Australia/Australia_5km/Future_scenarios_2020-2100/IPSL-CM6A-LR/ssp370/wc2.1_2.5m_bioc_IPSL-CM6A-LR_ssp370_2021-2040_AUS_5km.tif",
            "N:/Data-Master/WorldClim_CMIP6/Australia/Australia_5km/Future_scenarios_2020-2100/MIROC6/ssp370/wc2.1_2.5m_bioc_MIROC6_ssp370_2021-2040_AUS_5km.tif",
            "N:/Data-Master/WorldClim_CMIP6/Australia/Australia_5km/Future_scenarios_2020-2100/MIROC-ES2L/ssp370/wc2.1_2.5m_bioc_MIROC-ES2L_ssp370_2021-2040_AUS_5km.tif",
            "N:/Data-Master/WorldClim_CMIP6/Australia/Australia_5km/Future_scenarios_2020-2100/MRI-ESM2-0/ssp370/wc2.1_2.5m_bioc_MRI-ESM2-0_ssp370_2021-2040_AUS_5km.tif"
        ]
        
    }
}

# Function to calculate mean temperature from raster file
def calculate_mean_temperature(raster_file):
    with rasterio.open(raster_file) as src:
        band1 = src.read(1)
        #print(f"Data from {raster_file}: min={band1.min()}, max={band1.max()}, nodata={src.nodata}")
        band1 = np.ma.masked_equal(band1, src.nodata)
        return np.ma.mean(band1)

# Loop through SSPs and time periods, calculate ensemble averages
for ssp, periods in future_files.items():
    print(f"\nSSP: {ssp}")
    for period, files in periods.items():
        all_means = []
        for future_file in files:
            future_mean = calculate_mean_temperature(future_file)
            all_means.append(future_mean)
        
        # Calculate the average ensemble temperature for this SSP and time period
        ensemble_mean = np.mean(all_means)
        difference_worldclim = ensemble_mean - 21.74
        difference_other = ensemble_mean - 21.97
        
        print(f"Time period {period}:")
        print(f"  Ensemble average temperature: {ensemble_mean:.2f}°C")
        print(f"  Temperature difference compared to historical worldclim data: {difference_worldclim:.2f}°C")
        print(f"  Temperature difference compared to CSIRO historical data: {difference_other:.2f}°C\n")

# Summarise total habitat for 15 and 2 degree total habitat area
# For the differences 
# Summarise shift
# Summarise refugia?
    
    
    
    
    
    