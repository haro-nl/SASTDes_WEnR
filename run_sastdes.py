# Script to tie it all together

import os
import geopandas as gp

from sastdes import sast

cntrs_directory = r'\\wur\dfs-root\PROJECTS\sastdes\Geodata_SAStDes\EU_NUTS\shp'
cntrs_shp = 'NUTS_Level2.shp'
cntrs_gdf = gp.read_file(os.path.join(cntrs_directory, cntrs_shp))
cntrs_gdf['ID'] = cntrs_gdf['NUTS_ID']

indicators = ['N22b', 'N40', 'Htls']
indicator_vals = sast.do_iv(cntrs_gdf, 'Htls')

# TODO: Htls werkt nog niet!
# TODO: check contour CRS == source data CRS
# TODO: for categorical stats: simply divide by total number of pixels (assuming all pixels have equal are in the proj
# TODO: alles in GIT
# TODO: append subsequent IVs to same gdf
# TODO: count functie ook als count/km2
# TODO: shape properties such as area,

print(indicator_vals.head())
