import os
import numpy as np
import rasterstats
import pandas as pd
import geopandas as gp
import rasterio
import datetime

from sastdes import iv_specs
from sastdes import category_maps

# Several helper functions for SASTDes project
# Hans Roelofsen, WEnR 16 jan 2019


def reduce_category_stats(category_stats, relevant_classes):
    # function to reduce category stats to total number for relevant classes
    # e.g. category_stats = {'contour_1':{'urban':465, 'pine_forest':132, 'broadleaf_forest':557, 'water':998},
    #                        'contour_2':{'urban':150, 'pine_forest':400, 'broadleaf_forest':10, 'water':965}}'
    #      relevant_classes=['pine_forest', 'broadleaf_forest']
    # return {'contour_1':689, 'contour_2':410}
    out = []
    for contour_dict in category_stats:
        out.append(np.sum([v for k, v in contour_dict.items() if k in relevant_classes]))
    return out


def get_all_categories(category_stats):
    # returns all unique categories found in all contours that were superimposed on the raster
    all_cats = []
    for x in category_stats:
        all_cats = all_cats + list(x.keys())
    return set(all_cats)


def get_pixel_area(raster):
    # recover pixel area in the linear unit of the CRS of a raster file. Assumes linear unit is meters!
    with rasterio.open(raster) as rast:
        gt = rast.affine
        xsize = np.int16(gt[0])
        ysize = np.int16(-gt[4])
        pixel_size = np.multiply(xsize, ysize)
        return pixel_size


def categorical_stats(contours, source_data, cat_list, cat_map, **kwds):
    # Function to get total acreage of all classes in *cat_list*  from *source_data* for each contour in *contours*
    # output is either presented in <linear unit *source_data*>^2 or as percentage of total contour area

    # pixel count of all found categories for each contour
    raw_results = rasterstats.zonal_stats(contours, source_data, categorical=True, category_map=cat_map)

    # pixel count of requested categories for each contour
    reduced_results = reduce_category_stats(raw_results, cat_list)

    # multiply pixel count with pixel size in *source_data* linear unit to get acreage. Assumes meter as linear unit
    results_m2 = np.multiply(reduced_results, get_pixel_area(source_data))
    results = np.divide(results_m2, 1000000)  # results in square km

    # Give results as percentage of total #pixels of each contour, if requested.
    if kwds.get('relative', None) == 'perc':
        totals = reduce_category_stats(raw_results, get_all_categories(raw_results))
        results = np.multiply(np.divide(reduced_results, totals), 100)
    else:
        pass

    # compile new dataframe with 2 cols: {ID, IVs}
    out = pd.DataFrame({'values': results}, index=contours.index)

    if not out.empty:
        return out
    else:
        raise Exception('Congratulations, you managed to create an empty empty dataframe generated for '
                        '{0} in {1}'.format(source_data, contours))


def sum_stats(contours, source_data, sum_stat):
    # returns summary statistic *sum_stat* of *source_data* for each contour in *contours*
    results = rasterstats.zonal_stats(contours, source_data, stats=sum_stat)
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

    contours['ID'] = contours.index

    src_with_contour = gp.sjoin(src, contours, how='inner', op='intersects', rsuffix='_contours',
                                lsuffix='_source')  # spatial join
    src_with_contour['values'] = 1  # counter attribute
    src_dissolve = src_with_contour.dissolve(by='ID', aggfunc='sum')  # dissolve by contours ID

    if not src_dissolve.empty:
        return src_dissolve.drop(labels=[lab for lab in list(src_dissolve) if lab is not 'values'],
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
    contours['ID'] = contours.index
    contours['area_sq_km'] = np.divide(contours.area, 1000000)
    contours.drop([lab for lab in list(contours) if lab not in ['geometry', 'ID', 'area_sq_km']], inplace=True, axis=1)

    # associate each point in *source_data* with the ID of *contours* it intersects with
    src_with_contour_id = gp.sjoin(src, contours, how='inner', op='intersects', rsuffix='_contours',
                                   lsuffix='_source')
    # add counter colomn and drop redundant columns
    src_with_contour_id['counter'] = 1
    src_with_contour_id.drop([lab for lab in list(src_with_contour_id) if lab not in ['counter', 'geometry', 'ID']],
                             inplace=True, axis=1)

    # dissolve by ID of the *contours* feature
    src_dissolve = src_with_contour_id.dissolve(by='ID', aggfunc='sum')

    # new DF with all contours + count per contour
    contour_with_count = pd.merge(contours, src_dissolve, how='left', left_index=True, right_index=True)

    # calculate features from *source_data* per sq km for each feature in *contours*
    contour_with_count['values'] = np.divide(contour_with_count['counter'], contour_with_count['area_sq_km'])

    if not contour_with_count.empty:
        return contour_with_count.drop([lab for lab in list(contour_with_count) if lab is not 'values'], axis=1)
    else:
        raise Exception('Empty geodataframe for {0} in {1}'.format(os.path.basename(source_data), contours))


def intersect(contours, source_data, relative_to):
    # function calculate %count, %area_sq_km, or $area_perc of *source_data* features for each *contours* feature

    # add column to contours equalling the index, used later for removing features
    contours['contourID'] = contours.index

    # read source data
    src = gp.read_file(source_data)
    if any(src.geom_type != 'Polygon'):
        raise Exception('Source data {0} should contain Polygon geometry only'.format(os.path.basename(source_data)))

    # TODO: determine src primary key! Cannot be ID
    src['src_area_sq_km'] = np.divide(src.area, 1000000)
    src['sourceID'] = src[XXX]

    # Overlay two datasets and add counter attribute
    union = gp.overlay(contours, src, how='union')
    union['counter'] = 1

    # retain only features with values for both *contours* AND *source_data* primary keys.
    # Ie, remove features without any overlap
    union.dropna(axis=0, how='any', subset=['sourceID', 'contourID'], inplace=True)

    # dissolve on contour ID
    count_per_contour = union.dissolve(by='contourID', aggfunc='sum')

    # return requested information
    if relative_to == 'count_per_contour':
        return count_per_contour['counter']

    if relative_to == 'sq_km_per_contour':
        return count_per_contour['src_area_sq_km']

    if relative_to == 'percentage_per_contour':
        # TODO: contour square km nog bepalen!
        return np.multiply(np.divide(count_per_contour['src_area_sq_km'], count_per_contour['contour_sq_km']), 100)

    else:
        raise Exception('Invalid type provided for intersect method: {0}, should be one of count_per_contour, sq_km_per_contour or percentage_per_contour'.format(type))


def do_iv(contours, iv_name):
    # calculate values for indicator*iv_name* for each contour in *contours*
    # returns pandas dataframe with 2 cols: {ID:contours[ID];iv_name:values}

    # report on progress
    print('Commecing indicator {0} at {1}'.format(iv_name, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

    # Recover the processeing specifications for the requested IV
    iv_params = iv_specs.get(iv_name)
    method = iv_params['method']
    source_data = iv_params['source']

    # Double check the data types
    if not isinstance(contours, gp.geodataframe.GeoDataFrame):
        raise Exception('Contours should be a GeoDataFrame, currently is: {0}'.format(type(contours)))

    # Run the appropriate method
    if method == 'categorical':
        iv_vals = categorical_stats(contours=contours,
                                    source_data=source_data,
                                    cat_list=iv_params['classes'],
                                    cat_map=category_maps.get(os.path.basename(source_data)),
                                    relative=iv_params['relative_to'])

    elif method == 'sum_stat':
        stat = iv_params['sum_stat']
        iv_vals = sum_stats(contours=contours,
                            source_data=source_data,
                            sum_stat=stat)

    elif method == 'count_within_contour':
        iv_vals = count_within_contour(contours=contours,
                                       source_data=source_data)

    elif method == 'count_within_sq_km':
        iv_vals = count_within_sq_km(contours=contours,
                                     source_data=source_data)

    # je moet wat....
    else:
        iv_vals = [0] * contours.shape[0]

    # rename the values column to the name of the indicator
    iv_vals.rename(columns={'values': iv_name}, inplace=True)

    # report on progress
    print('\tdone at {0}'.format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

    return iv_vals


