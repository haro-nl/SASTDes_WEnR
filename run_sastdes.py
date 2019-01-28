"""
Main script for the SASTDes project.

Returns one or more indicator values (IV) for each polygon in *contours* as a n*m table where n=#contours, m=# IVs

Requires python 3.7, plus varios opensource packages.


IVs must be defined in \sastdes\iv_definitions. Allowed methods for IV calculation are:
categorical:
  summary stats for one or more categories of a catogorical source raster per contour.
  eg: %sq km forest per contour

sum_stat:
  summary stats for a calculated surface source raster per contour.
  eg: mean elevation per contour

count_within_contour:
  of points in source point dataset per contour, or per sq km per contour
  eg: number of hotels, or hotels/km^2 per contour

intersect:
  summary statistics (count, % area or sq km) of polygons in source data for each contour
  eg: national parks per contour

line_length:
  length of a line dataset within 10km of each contour
  eg: coastline length per contour

By: Hans Roelofsen, WEnR team Biodiversiteit & Beleid. Januari 2019
"""


import os
import geopandas as gp
from sastdes import sast

# read contours shapefile and provide ID column
cntrs_directory = r'\\wur\dfs-root\PROJECTS\sastdes\Geodata_SAStDes\test_contours'
cntrs_shp = 'test_contours_HR20190128.shp'
cntrs_gdf = gp.read_file(os.path.join(cntrs_directory, cntrs_shp))
cntrs_gdf.set_index(keys='NUTS_NAME', inplace=True)


# list of desired indicators. This and previous block can possibly also be read from a steerfile
indicators = ['N22b', 'N22b_p', 'N40', 'Htls', 'Htls_sq_km', 'N37', 'G12a', 'G12b', 'E7b_a', 'E7b_b', 'E7b_c', 'N6b']

for indicator in indicators:

    indicator_val = sast.do_iv(cntrs_gdf, indicator)
    cntrs_gdf = cntrs_gdf.join(indicator_val, how='left')
    # except Exception as e:
    #     print('\t{0}'.format(e))

print(cntrs_gdf.drop('geometry', axis=1))
# print(cntrs_gdf.loc['DE30'])
cntrs_gdf.drop('geometry', axis=1).to_csv(r'd:\Sast_Runs\20190128_out\sastdes.csv', sep=';')

# TODO: Htls_sq_km geeft een raar resultaat terug!

# TODO: line intersection length per contour!
#       Done, 28 jan 2019 zei het op een lelijke hacky manier.
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



