# -*- coding: utf-8 -*-
"""
Summary statistics for 1.5C- and 2C-aligned scenarios, all ensemble surfaces.

Created by Dr Carla Archibald, assisted troubleshooting via Claude Code.

"""

import numpy as np
import pandas as pd
import rasterio
from rasterio.enums import Resampling
from rasterio.fill import fillnodata
from rasterio.warp import reproject

# ---------------------------------------------------------------- settings
WD = "N:\\Current-Users\\Carla-Archibald\\WWF\\habitat_suit_data\\"
NLUM_FILE = r'N:\Data-Master\National_Landuse_Map\NLUM_2010-11_mask.tif'
CELL_FILE = r"N:\LUF-Modelling\Biodiversity-footprint\Data\Agriculture\cell_zones_df.h5"
OUT_FILE = WD + "Warming-scenario-summary_all_species_all_ensembles.csv"

SPECIES_LIST = ['Calyptorhynchus_baudinii', 'Hemibelideus_lemuroides',
                'Malurus_coronatus', 'Phascolarctos_cinereus',
                'Pseudochirops_archeri', 'Pseudochirulus_cinereus']

# label used in the output table
STAT_SUFFIX = {'Mean': '', 'Minimum': 'min', 'Maximum': 'max'}   # mean raster has no suffix

# scenario label
SCENARIOS = {'1.5': 'ssp126', '2.0': 'ssp370'}

# ---------------------------------------------------------------- NLUM mask
with rasterio.open(NLUM_FILE) as rst:
    NLUM_mask = rst.read(1)
    NLUM_ID_raster = rst.read(1, masked=True)
    NLUM_mask_bin = NLUM_ID_raster.mask == False  # noqa: E712
    meta = rst.meta.copy()

cell_df = pd.read_hdf(CELL_FILE, columns=['CELL_ID', 'X', 'Y', 'CELL_HA'])


# ---------------------------------------------------------------- helpers
def load_suitability_1km(path):
    """Read a 5 km suitability raster and return a 1D array (0-1) of 1 km
    NLUM cells. """
    with rasterio.open(path) as src:
        dst_array = np.zeros((meta.get('height'), meta.get('width')), np.float64) - 9999
        reproject(rasterio.band(src, 1), dst_array,
                  src_crs=src.crs, src_nodata=0, src_transform=src.transform,
                  dst_nodata=0, dst_transform=meta.get('transform'),
                  dst_crs=meta.get('crs'), resampling=Resampling.nearest)

    dst_array_filled = fillnodata(dst_array, mask=NLUM_mask,
                                  max_search_distance=100.0, smoothing_iterations=0)

    # rescale 0-100 -> 0-1; values above 1 after rescaling are set to 0 (as before)
    arr = np.float64(np.where(NLUM_mask == 1, dst_array_filled / 100, 0))
    arr[arr > 1] = 0

    out = arr[NLUM_mask == 1].astype(np.float64)
    out[out == -9999.0] = 0
    return out


def summarise(future_1km, eoo, hist_eoo, hist_sum):
    future_eoo = future_1km * eoo
    area = round(future_eoo.sum(), 0)
    abs_change = round(area - hist_sum, 0)                       # FIXED
    perc_change = round(((area - hist_sum) / hist_sum) * 100, 0)
    abs_refugia = round((hist_eoo * future_1km).sum(), 0)
    perc_refugia = round((abs_refugia / hist_sum) * 100, 0)
    return area, abs_change, perc_change, abs_refugia, perc_refugia


def raster_path(species, ssp, suffix):
    tag = ('_' + suffix) if suffix else ''
    return (WD + species + "\\" + species + '_GCM-Ensembles_' + ssp +
            '_2050_AUS_5km_EnviroSuit' + tag + '.tif')


# ---------------------------------------------------------------- pre-analysis check
# List every input file that is missing BEFORE any slow processing starts.
import os

missing = []
for species in SPECIES_LIST:
    species_wd = WD + species + "\\"
    for f in [species_wd + species + "_Extent_of_occurrence_buffered.tif",
              species_wd + species + '_historic_baseline_1990_AUS_5km_EnviroSuit.tif']:
        if not os.path.exists(f):
            missing.append(f)
    for suffix in STAT_SUFFIX.values():
        for ssp in SCENARIOS.values():
            f = raster_path(species, ssp, suffix)
            if not os.path.exists(f):
                missing.append(f)

if missing:
    print("MISSING INPUT FILES (fix names or STAT_SUFFIX at the top, then re-run):")
    for f in missing:
        print("  " + f)
    raise SystemExit(1)
print("All input files found.")

# ---------------------------------------------------------------- main loop
rows = []

for species in SPECIES_LIST:
    print("Start for " + species)
    species_wd = WD + species + "\\"

    # EOO
    with rasterio.open(species_wd + species + "_Extent_of_occurrence_buffered.tif") as src:
        eoo = src.read()[0][NLUM_mask_bin]
    eoo_sum = round(eoo.sum(), 0)

    # Historical (computed ONCE per species, shared by all ensemble rows)
    hist_1km = load_suitability_1km(
        species_wd + species + '_historic_baseline_1990_AUS_5km_EnviroSuit.tif')
    hist_eoo = hist_1km * eoo
    hist_sum = round(hist_eoo.sum(), 0)

    for stat_label, suffix in STAT_SUFFIX.items():
        row = {'Species': species,
               'Prediction': stat_label,
               'EOO based on occurrence points area [km2]': eoo_sum,
               'Historical quality weighted habitat area [km2]': hist_sum}

        for scen_label, ssp in SCENARIOS.items():
            fut_1km = load_suitability_1km(raster_path(species, ssp, suffix))
            area, d_abs, d_perc, r_abs, r_perc = summarise(fut_1km, eoo, hist_eoo, hist_sum)

            row[scen_label + ' degree quality weighted habitat area [km2]'] = area
            row[scen_label + ' degree absolute change in quality weighted habitat area [km2]'] = d_abs
            row[scen_label + ' degree percent change in quality weighted habitat area [%]'] = d_perc
            row[scen_label + ' degree absolute climate refugia [km2]'] = r_abs
            row[scen_label + ' degree percentage climate refugia [% of historical]'] = r_perc

        # difference between scenarios, in percentage points
        row['Difference 2.0 minus 1.5 degree, habitat change [pp]'] = (
            row['2.0 degree percent change in quality weighted habitat area [%]'] -
            row['1.5 degree percent change in quality weighted habitat area [%]'])
        row['Difference 2.0 minus 1.5 degree, refugia [pp]'] = (
            row['2.0 degree percentage climate refugia [% of historical]'] -
            row['1.5 degree percentage climate refugia [% of historical]'])

        rows.append(row)
        print("  done: " + species + " / " + stat_label)

    # save progress 
    pd.DataFrame(rows).to_csv(OUT_FILE.replace('.csv', '_partial.csv'), index=False)

summary = pd.DataFrame(rows)

# ---------------------------------------------------------------- sanity checks
problems = []

# 1. historical area must be identical across ensemble rows for a species
if not (summary.groupby('Species')['Historical quality weighted habitat area [km2]']
        .nunique() == 1).all():
    problems.append("Historical area differs across ensemble rows for some species.")

# 2. minimum <= mean <= maximum for habitat area and refugia, in each scenario
for scen in SCENARIOS:
    for col in [scen + ' degree quality weighted habitat area [km2]',
                scen + ' degree absolute climate refugia [km2]']:
        wide = summary.pivot(index='Species', columns='Prediction', values=col)
        bad = wide[~((wide['Minimum'] <= wide['Mean']) & (wide['Mean'] <= wide['Maximum']))]
        if len(bad) > 0:
            problems.append("min <= mean <= max violated for '" + col + "': " +
                            ", ".join(bad.index))

# 3. losses should be negative: sign of absolute change must match percent change
for scen in SCENARIOS:
    a = summary[scen + ' degree absolute change in quality weighted habitat area [km2]']
    p = summary[scen + ' degree percent change in quality weighted habitat area [%]']
    if not (np.sign(a) == np.sign(p)).all():
        problems.append("Sign of absolute and percent change disagree (" + scen + ").")

if problems:
    print("\nSANITY CHECK PROBLEMS:")
    for p in problems:
        print("  - " + p)
else:
    print("\nAll sanity checks passed.")

summary.to_csv(OUT_FILE, index=False)
print("Wrote " + OUT_FILE)

### END :) 