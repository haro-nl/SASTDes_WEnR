# contains functions for the following methods to calculate an indicator given a contour
#   categorical_stats
#   summary_stats
#   count_within_contour
#   count_within_sq_km (needs to be combined with above)
#   intersect
# Hans Roelofsen, WEnR, 23 januari 2019

import os
import numpy as np
import rasterstats
import pandas as pd
import geopandas as gp

from sastdes import sast


def categorical_stats(contours, source_data, cat_list, cat_map, **kwds):
    # Function to get total acreage of all classes in *cat_list*  from *source_data* for each contour in *contours*
    # output is either presented in <linear unit *source_data*>^2 or as percentage of total contour area

    # pixel count of all found categories for each contour
    raw_results = rasterstats.zonal_stats(contours, source_data, categorical=True, category_map=cat_map)

    # pixel count of requested categories for each contour
    reduced_results = sast.reduce_category_stats(raw_results, cat_list)

    # multiply pixel count with pixel size in *source_data* linear unit to get acreage. Assumes meter as linear unit
    results_m2 = np.multiply(reduced_results, sast.get_pixel_area(source_data))
    results = np.divide(results_m2, 1000000)  # results in square km

    # Give results as percentage of total #pixels of each contour, if requested.
    if kwds.get('relative', None) == 'perc':
        totals = sast.reduce_category_stats(raw_results, sast.get_all_categories(raw_results))
        results = np.multiply(np.divide(reduced_results, totals), 100)
    else:
        pass

    # compile new dataframe with 2 cols: {ID, IVs}
    out = pd.DataFrame({'values': results}, index=contours.index)

    if not out.empty:
        return out
    else:
        raise Exception('Congratulations, you managed to create an empty empty dataframe for '
                        '{0} in {1}'.format(source_data, contours))


def summary_stats(contours, source_data, sum_stat):
    # returns summary statistic *sum_stat* of *source_data* for each contour in *contours*

    results = rasterstats.zonal_stats(contours, source_data, stats=sum_stat)
    # retrieve statistic of interest from output dictionary. Note that *sum_stat* cannot be an iterable!
    results = [result[sum_stat] for result in results]

    out = pd.DataFrame({'values': results}, index=contours.index)

    if not out.empty:
        return out
    else:
        raise Exception('Empty dataframe generated for {0} of {1} in {2}'.format(sum_stat, source_data, contours))


def count_within_contour(contours, source_data):
    # returns count of *source_data* Points in each contour in *contours*
    # only works for gdf in same CRS

    # read source data and check for geometry type
    src = gp.read_file(source_data)
    if any(src.geom_type != 'Point'):
        raise Exception('Source data {0} should contain Point geometry only'.format(os.path.basename(source_data)))

    contours['contourID'] = contours.index

    src_with_contour = gp.sjoin(src, contours, how='inner', op='intersects', rsuffix='_contours',
                                lsuffix='_source')  # spatial join
    src_with_contour['values'] = 1  # counter attribute
    src_dissolve = src_with_contour.dissolve(by='contourID', aggfunc='sum')  # dissolve by contours ID

    # Reattach to original contours to ensure all contours are returned
    contours_with_count = pd.merge(contours, src_dissolve, how='left', left_index=True, right_index=True)

    if not contours_with_count.empty:
        return contours_with_count.drop(labels=[lab for lab in list(contours_with_count) if lab is not 'values'],
                                 axis=1)
    else:
        raise Exception('Empty geodataframe for {0} in {1}'.format(os.path.basename(source_data), contours))


def count_within_sq_km(contours, source_data):
    # returns count of *source_data* points per square km for each contour in *contours*
    # requires identical and projected CRS in meters for both *contours* and *source_data*
    # Hans Roelofsen, WEnR, 22 january 2019

    # TODO: probably possible to call count_within_contour function, instead of replicating code

    # read source data and check for geometry type
    src = gp.read_file(source_data)
    if any(src.geom_type != 'Point'):
        raise Exception('Source data {0} should contain Point geometry only'.format(os.path.basename(source_data)))

    # tidy up *contours* data
    contours['contourID'] = contours.index
    contours['area_sq_km'] = np.divide(contours.area, 1000000)
    # contours.drop([lab for lab in list(contours) if lab not in ['geometry', 'contourID', 'area_sq_km']], inplace=True, axis=1)

    # associate each point in *source_data* with the ID of *contours* it intersects with
    src_with_contour_id = gp.sjoin(src, contours, how='inner', op='intersects', rsuffix='_contours',
                                   lsuffix='_source')
                                   
    # add counter colomn and drop redundant columns
    src_with_contour_id['counter'] = 1
    src_with_contour_id.drop([lab for lab in list(src_with_contour_id) if lab not in ['counter', 'geometry', 'contourID']],
                             inplace=True, axis=1)

    # dissolve by ID of the *contours* feature
    src_dissolve = src_with_contour_id.dissolve(by='contourID', aggfunc='sum')

    # new DF with all contours + count per contour
    contour_with_count = pd.merge(contours, src_dissolve, how='left', left_index=True, right_index=True)

    # calculate features from *source_data* per sq km for each feature in *contours*
    contour_with_count['values'] = np.divide(contour_with_count['counter'], contour_with_count['area_sq_km'])

    if not contour_with_count.empty:
        return contour_with_count.drop([lab for lab in list(contour_with_count) if lab is not 'values'], axis=1)
    else:
        raise Exception('Empty geodataframe for {0} in {1}'.format(os.path.basename(source_data), contours))


def intersect(contours, source_data, relative_to):
    # calculate count, area_sq_km, or area_perc of *source_data* features intersecting with each *contours* feature

    # add column to contours equalling the index, used later for removing features
    contours['contourID'] = contours.index

    # read source data. Add column ID containing just the index.
    src = gp.read_file(source_data)
    if any(src.geom_type != 'Polygon'):
        raise Exception('Source data {0} should contain Polygon geometry only'.format(os.path.basename(source_data)))
    src['sourceID'] = src.index

    # Overlay two datasets and add counter attribute
    intersect = gp.overlay(contours, src, how='intersection')

    # calculate area of remaining features, add counter attribute
    intersect['src_area_sq_km'] = np.divide(intersect.area, 1000000)
    intersect['counter'] = 1

    # dissolve on contourID to get agg_stats per contour ID
    count_per_contour = intersect.dissolve(by='contourID', aggfunc='sum')

    # reattach to original countours dataset. Drop geometry from count_per_contour to prevent geometry duplication
    contours_with_count = pd.merge(left=contours, right=count_per_contour.drop('geometry', axis=1),
                                   how='left', left_index=True, right_index=True)

    # return requested information
    if relative_to == 'count_per_contour':
        out = contours_with_count.drop([lab for lab in list(contours_with_count) if lab is not 'counter'],
                                       axis=1)
        return out.rename(columns={'counter': 'values'})

    if relative_to == 'sq_km_per_contour':
        out = contours_with_count.drop([lab for lab in list(contours_with_count) if lab is not 'src_area_sq_km'],
                                       axis=1)
        return out.rename(columns={'src_area_sq_km': 'values'})

    if relative_to == 'percentage_per_contour':
        contours_with_count['contour_area_sq_km'] = np.divide(contours_with_count.area, 1000000)
        contours_with_count['perc_per_contour'] = np.multiply(np.divide(contours_with_count['src_area_sq_km'],
                                                                        contours_with_count['contour_area_sq_km']), 100)
        out = contours_with_count.drop([lab for lab in list(contours_with_count) if lab is not 'perc_per_contour'],
                                       axis=1)
        return out.rename(columns={'perc_per_contour': 'values'})

    else:
        raise Exception('Invalid type provided for intersect method: {0}, should be one of count_per_contour, sq_km_per_contour or percentage_per_contour'.format(type))


def line_length(contours, source_data):
    # returns km of line in *source* located within 5.000 m from each feature in *contours*
    # used for e.g. associating coastline data with contours

    # add column to contours equalling the index, used later for dissolving
    contours['contourID'] = contours.index

    # read source data. Add column ID containing just the index.
    src = gp.read_file(source_data)
    # TODO: check if all source data are LineString or MultiLineString!
    # if any(src.geom_type != 'LineString') or any(src.geom_type != 'MultiLineString'):
    #     raise Exception('Source data {0} should contain Line geometry only'.format(os.path.basename(source_data)))
    src['sourceID'] = src.index

    # buffer to lines to 1 meter to generate polygons, much easier.
    src_buff = gp.GeoDataFrame(src['sourceID'], geometry=src.buffer(1))

    # buffer contours to accomodate lines near, but not intersecting the original source data
    cntrs_buff = gp.GeoDataFrame(contours['contourID'], geometry=contours.buffer(distance=5000))

    # Overlay two datasets and calculate area
    src_intersect = gp.overlay(src_buff, cntrs_buff, how='intersection')
    src_intersect['area_m2'] = src_intersect.area

    # dissolve to contourIDs
    src_diss = src_intersect.dissolve(by='contourID', aggfunc='sum')

    # calculate approximate line length per contourID as half of the dissolved feature area (because line.buffer was 1!)
    # Then divide by 1000 to get km instead of m
    src_diss['values'] = np.divide(src_diss['area_m2'], 2000)

    # rejoin to original contours dataframe to retain all contours.
    contours_with_line_length = pd.merge(contours, src_diss, how='left', left_index=True, right_index=True)
    return contours_with_line_length.drop([lab for lab in list(contours_with_line_length) if lab is not 'values'],
                                          axis=1)

