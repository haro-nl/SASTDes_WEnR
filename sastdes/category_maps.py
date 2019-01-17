def get(source):
    # Return dictionary of pixel value:land use category for one of several categorical map sources. 
    # Hans Roelofsen, WEnR, 16/Jan/2019 16:09

    out = {'lc2000_etrs0.tif':
            {1: 'Continuous urban fabric',
             2: 'Discontinous urban fabric',
             3: 'Industrial or commercial units',
             4: 'Road and rail networks and assoc',
             5: 'Port areas',
             6: 'Airports',
             7: 'Mineral extraction sites',
             8: 'Dump sites',
             9: 'Construction sites',
             10: 'Green urban areas',
             11: 'Sport and leisure facilities',
             12: 'Non-irrigated arable land',
             13: 'Permanently irrigated land',
             14: 'Rice fields',
             15: 'Vineyards',
             16: 'Fruit trees and berry plantation',
             17: 'Olive groves',
             18: 'Pastures',
             19: 'Annual crops associated with per',
             20: 'Complex cultivation patterns',
             21: 'Land principally occupied by agr',
             22: 'Agro-forestry areas',
             23: 'Broad leaved forest',
             24: 'Coniferous forest',
             25: 'Mixed forest',
             26: 'Natural grasslands',
             27: 'Moors and heathland',
             28: 'Sclerophyllous vegetation',
             29: 'Transitional woodland-shrub',
             30: 'Beaches, dunes and sands',
             31: 'Bare rocks',
             32: 'Sparsely vegetated areas',
             33: 'Burnt areas',
             34: 'Glaciers and perpetual snow',
             35: 'Inland marhes',
             36: 'Peat bogs',
             37: 'Salt marshes',
             38: 'Salines',
             39: 'Intertidal flats',
             40: 'Water courses',
             41: 'Water bodies',
             42: 'Coastal lagoons',
             43: 'Estuaries'}
    }
    try:
        out = out[source]
    except KeyError:
        raise Exception('No category map is available for {0}, Perhaps try one of the following: '.format(source) +
                        ', '.join([k for k,v in out.items()]))
    return out