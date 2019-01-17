import os
import numpy as np
import rasterstats
import pandas as pd
import geopandas as gp

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


def categorical_stats(contours, source_data, cat_list, cat_map):
    # Function to get total acreage of all classes in *class_list*  from *source_data* for each contour
    # in *contours*.
    results = rasterstats.zonal_stats(contours, source_data, categorical=True, category_map=cat_map)
    results = reduce_category_stats(results, cat_list)
    out = pd.DataFrame({'id': contours['ID'], 'values': results})
    if not out.empty:
        return out
    else:
        raise Exception('Empty dataframe generated for {0} in {1}'.format(source_data, contours))


def sum_stats(contours, source_data, sum_stat):
    # returns summary statistic *sum_stat* of *source_data* for each contour in *contours*
    results = rasterstats.zonal_stats(contours, source_data, stats=sum_stat)
    out = pd.DataFrame({'id': contours['ID'], 'values': results})
    if not out.empty:
        return out
    else:
        raise Exception('Empty dataframe generated for {0} of {1} in {2}'.format(sum_stat, source_data, contours))


def count_within_contour(contours, source_data):
    # returns count of *source_data* features in each contour in *contours*
    src = gp.read_file(source_data)
    source_data_with_contour = gp.sjoin(source_data, contours, how='inner', op='intersects')
    source_data_with_contour['counter'] = 1
    source_data_count = source_data_with_contour.dissolve(by='ID', aggfunc='sum')
    out = pd.DataFrame({'ID': source_data['ID'], 'counted': source_data_count['counter']})
    return out


def do_iv(contours, iv_name):
    # calculate values for indicator*iv_name* for each contour in *contours*
    # returns pandas dataframe where ID:contours[ID], iv_name:values
    iv_params = iv_specs.get(iv_name)

    method = iv_params['method']
    source_data = iv_params['source']

    if method == 'categorical':
        class_list = iv_params['classes']
        iv_vals = categorical_stats(contours=contours, source_data=source_data, cat_list=class_list,
                                    cat_map=category_maps.get(os.path.basename(source_data)))

    elif method == 'sum_stat':
        stat = iv_params['sum_stat']
        iv_vals = sum_stats(contours=contours, source_data=source_data, sum_stat=stat)

    elif method == 'count':
        iv_vals = count_within_contour(contours, source_data)


    else:
        iv_vals = [0] * contours.shape[0]

    # rename the values column to the name of the indicator
    iv_vals.rename(columns={'values': iv_name}, inplace=True)
    return iv_vals


