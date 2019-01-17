def get(source):
    # Return dictionary of pixel value:land use category for one of several categorical map sources. 
    # Hans Roelofsen, WEnR, 16/Jan/2019 16:09

    out = {'lc2000_etrs0.tif':{
            1:'Continous urban fabric',
            2:'Discontinous urban fabric',
            3:'Industrial or commercial units',
            4:'Road and rail networks',
            5:'Port areas',
            6:'Airports',
            7:'Mineral extractiuon sites',
            8:'Dump areas',
            9:'Construction sites',
            10:'Green urban areas',
            11:'Port and leisure facilities',
            12:'Non-irrigated arable land',
            13:'Permanently irrgated land',
            14:'Rice fields',
            15:'Vineyards',
            16:'Fruit trees and berry plantations',
            18:'Pastures',
            19:'Annual crops associated with permanent crops',
            20:'Complex cultivation patters',
            21:'Land princippaly occupied by agriculture',
            23:'Broad-leaf forest',
            24:'Coniferous forest',
            25:'Mixed forest',
            26:'Natural grasslands',
            27:'Moors and heathland',
            28:'Sclerrophyllous vegetation',
            29:'Transitional woodland-scrub',
            30:'Beaches, sand and dunes',
            31:'Bare rocks',
            32:'Sparsly vegetated areas',
            33:'Burnt areas',
            34:'Glaciers and snow',
            35:'Inland marshes',
            36:'Peat bogs',
            37:'Salt marshes',
            40:'Water Courses',
            41:'Water bodies',
            42:'Coastal lagoons',
            43:'Estuaries',
            44:'Sea and Ocean'}
    }
    try:
        out = out[source]
    except KeyError:
        raise Exception('No category map is available for {0}'.format(source))
    return out