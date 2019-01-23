# Script to tie it all together

import os
import geopandas as gp

from sastdes import sast

# read contours shapefile and provide ID column
cntrs_directory = r'\\wur\dfs-root\PROJECTS\sastdes\Geodata_SAStDes\EU_NUTS\shp'
cntrs_shp = 'NUTS_Level2.shp'
cntrs_gdf = gp.read_file(os.path.join(cntrs_directory, cntrs_shp))
cntrs_gdf.set_index(keys='NUTS_ID', inplace=True)
cntrs_gdf = cntrs_gdf.sample(20)

# list of desired indicators. This and previous block can possibly also be read from a steerfile
indicators = ['Htls_sq_km', 'Hans', 'Htls', 'G12a', 'G12b', 'N22b', 'N40', 'N22b_p', 'E7b_a', 'E7b_b', 'E7b_c']
# indicators = ['E7b_a', 'E7b_b', 'E7b_c']

for indicator in indicators:
    try:
        indicator_val = sast.do_iv(cntrs_gdf, indicator)
        cntrs_gdf = cntrs_gdf.join(indicator_val, how='left')
    except Exception as e:
        print('\t{0}'.format(e))

print(cntrs_gdf.drop('geometry', axis=1))
# print(cntrs_gdf.loc['DE30'])
cntrs_gdf.drop('geometry', axis=1).to_clipboard(sep=';')

# TODO: line intersection length per contour!
# TODO: ergens wordt ID extra aangemaakt als kolom
#       somehow, somewhere, this behaviour dissapeared
# TODO: df padded with NA when no IV available
#       only an issue when copying to clipboard
# TODO: poly-to-poly acreage
#       Done 23 jan 2019
# TODO: Htls werkt nog niet!.
#       Done 21 jan 2019
# TODO: check contour CRS == source data CRS.
#       issue: different representation of the same CRS
# TODO: for categorical stats: simply divide by total number of pixels (assuming all pixels have equal are in the proj
#       done, 17-01-2019 2139hours
# TODO: multiply categorical results with cell size for true acreage, when relative to is None
#       done, 17-01-2019 2214 hours
# TODO: append subsequent IVs to same gdf
#       done, using join on left, but needs to be tested. Done
# TODO: count functie ook als count/km2
#       done, 22-01-2019
# TODO: shape properties such as area,
# TODO: make scripts and functions verbose; report on progress
#       Done, 22-01-2019



