import os
import numpy as np
import rasterstats
import pandas as pd
import geopandas as gp
import rasterio
import datetime

from sastdes import iv_specs
from sastdes import category_maps
from sastdes import sast_method

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


def do_iv(contours, iv_name):
    # calculate values for indicator*iv_name* for each contour in *contours*
    # returns pandas dataframe with 2 cols: {ID:contours[ID];iv_name:values}

    # report on progress
    t0 = datetime.datetime.now()
    print('Commecing indicator {0} at {1}'.format(iv_name, t0.strftime("%Y-%m-%d %H:%M:%S")))

    # Recover the processeing specifications for the requested IV
    iv_params = iv_specs.get(iv_name)
    iv_method = iv_params['method']
    source_data = iv_params['source']

    # Double check the data types
    if not isinstance(contours, gp.geodataframe.GeoDataFrame):
        raise Exception('Contours should be a GeoDataFrame, currently is: {0}'.format(type(contours)))

    # Run the appropriate method
    if iv_method == 'categorical':
        iv_vals = sast_method.categorical_stats(contours=contours,
                                                source_data=source_data,
                                                cat_list=iv_params['classes'],
                                                cat_map=category_maps.get(os.path.basename(source_data)),
                                                relative=iv_params['relative_to'])

    elif iv_method == 'sum_stat':
        stat = iv_params['sum_stat']
        iv_vals = sast_method.summary_stats(contours=contours,
                                            source_data=source_data,
                                            sum_stat=stat)

    elif iv_method == 'count_within_contour':
        iv_vals = sast_method.count_within_contour(contours=contours,
                                                   source_data=source_data)

    elif iv_method == 'count_within_sq_km':
        iv_vals = sast_method.count_within_sq_km(contours=contours,
                                                 source_data=source_data)

    elif iv_method == 'intersect':
        relative = iv_params['relative_to']
        iv_vals = sast_method.intersect(contours=contours,
                                        source_data=source_data,
                                        relative_to=relative)

    # je moet wat....
    else:
        iv_vals = [0] * contours.shape[0]

    # rename the values column to the name of the indicator
    iv_vals.rename(columns={'values': iv_name}, inplace=True)

    # report on progress
    t1 = datetime.datetime.now()
    dt = t1 - t0
    print('\tdone at {0}, after {1} min, {2} seconds'.format(t1.strftime("%Y-%m-%d %H:%M:%S"), str(dt).split(':')[1],
                                                             str(dt).split(':')[2]))

    return iv_vals


