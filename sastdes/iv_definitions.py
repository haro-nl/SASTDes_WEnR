def get():
    # dictionary of indicator properties.
    # Hans Roelofsen, WEnR, 16/Jan/2019 16:08

    return {'N22b':{
            'name':'Forest_Area_EU',
            'label':'Forest Area',
            'method':'categorical',
            'source':r'\\wur\dfs-root\PROJECTS\sastdes\Geodata_SAStDes\LC2000_tiff\lc2000_etrs0.tif',
            'sum_stat':None,
            'classes':['Broad-leaf forest', 'Coniferous forest', 'Mixed forest'],
            'relative_to':None},
        'N22b_p': {
            'name': 'Forest_Area_EU_percentage',
            'label': 'Forest Area',
            'method': 'categorical',
            'source': r'\\wur\dfs-root\PROJECTS\sastdes\Geodata_SAStDes\LC2000_tiff\lc2000_etrs0.tif',
            'sum_stat': None,
            'classes': ['Broad-leaf forest', 'Coniferous forest', 'Mixed forest'],
            'relative_to': 'perc'},
        'N40':{
            'name':'Grassland_Area_EU',
            'label':'Grassland Area',
            'method':'categorical',
            'source':r'\\wur\dfs-root\PROJECTS\sastdes\Geodata_SAStDes\LC2000_tiff\lc2000_etrs0.tif',
            'sum_stat':None,
            'classes':['Pastures', 'Natural grasslands', 'Mixed forest', 'Moors and heathland'],
            'relative_to':None},
        'Htls':{
            'name':'Hotels_EU',
            'label':'# Hotels in contour',
            'method':'count_within_contour',
            'source':r'\\wur\dfs-root\PROJECTS\sastdes\Geodata_SAStDes\Hotels_Europe_shp\Hotels_Cleaned_EU_05_FullTable_EPSG-3035.shp',
            'sum_stat':None,
            'classes':None,
            'relative_to':None},
        'Htls_sq_km': {
            'name': 'Hotels_EU',
            'label': '# Hotels per square km',
            'method': 'count_within_sq_km',
            'source': r'\\wur\dfs-root\PROJECTS\sastdes\Geodata_SAStDes\Hotels_Europe_shp\Hotels_Cleaned_EU_05_FullTable_EPSG-3035.shp',
            'sum_stat': None,
            'classes': None,
            'relative_to': None},
        'G12mean':{
            'name':'Alt-mean',
            'label':'Mean altitude',
            'method':'sum_stat',
            'source':r'\\wur\dfs-root\PROJECTS\sastdes\Geodata_SAStDes\EU_DEM\EU_DEM_100m.tif',
            'sum_stat':'mean',
            'classes':None,
            'relative_to':None},
        'N37':{
            'name':'Bare_rock',
            'label':'Area of bare rocks',
            'method':'categorical',
            'source':r'\\wur\dfs-root\PROJECTS\sastdes\Geodata_SAStDes\LC2000_tiff\lc2000_etrs0.tif',
            'sum_stat':None,
            'classes':['Bare rocks'],
            'relative_to':None}
    }