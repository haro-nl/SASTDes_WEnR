# Script to tie it all together

import os
import geopandas as gp

from sastdes import sast

# read contours shapefile and provide ID column
cntrs_directory = r'\\wur\dfs-root\PROJECTS\sastdes\Geodata_SAStDes\EU_NUTS\shp'
cntrs_shp = 'NUTS_Level2.shp'
cntrs_gdf = gp.read_file(os.path.join(cntrs_directory, cntrs_shp))
cntrs_gdf['ID'] = cntrs_gdf['NUTS_ID']

# list of desired indicators. This and previous block can possibly also be read from a steerfile
indicators = ['N22b', 'N22b_p', 'N40', 'Htls']

for indicator in indicators:
    indicator_vals = sast.do_iv(cntrs_gdf, indicator)

    cntrs_gdf.join(indicator_vals, on='ID', how='left')


# indicator_vals = sast.do_iv(cntrs_gdf, 'N22b_p')

# TODO: Htls werkt nog niet!
# TODO: check contour CRS == source data CRS.
#       issue: different representation of the same CRS
# TODO: for categorical stats: simply divide by total number of pixels (assuming all pixels have equal are in the proj
#       done, 17-01-2019 2139hours
# TODO: multiply categorical results with cell size for true acreage, when relative to is None
#       done, 17-01-2019 2214 hours
# TODO: append subsequent IVs to same gdf
#       done, using join on left, but needs to be tested
# TODO: count functie ook als count/km2
# TODO: shape properties such as area,
# TODO: make scripts and functions verbose; report on progress


print(cntrs_gdf.head())
