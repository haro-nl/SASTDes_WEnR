def get():
    # dictionary of indicator properties.
    # Hans Roelofsen, WEnR, 16/Jan/2019 16:08
    # last update: 18 feb 2019



    return {'N22b':{
            'name': 'Forest_Area_EU',
            'label': 'Forest Area',
            'method': 'categorical',
            'source': r'\\wur\dfs-root\PROJECTS\sastdes\Geodata_SAStDes\LC2000_tiff\lc2000_etrs0.tif',
            'sum_stat': None,
            'classes': ['Broad-leaf forest', 'Coniferous forest', 'Mixed forest'],
            'relative_to': None},
        'N22b_p': {
            'name': 'Forest_Area_EU_percentage',
            'label': 'Forest Area',
            'method': 'categorical',
            'source': r'\\wur\dfs-root\PROJECTS\sastdes\Geodata_SAStDes\LC2000_tiff\lc2000_etrs0.tif',
            'sum_stat': None,
            'classes': ['Broad-leaf forest', 'Coniferous forest', 'Mixed forest'],
            'relative_to': 'perc'},
        'N40':{
            'name': 'Grassland_Area_EU',
            'label': 'Grassland Area',
            'method': 'categorical',
            'source': r'\\wur\dfs-root\PROJECTS\sastdes\Geodata_SAStDes\LC2000_tiff\lc2000_etrs0.tif',
            'sum_stat': None,
            'classes': ['Pastures', 'Natural grasslands', 'Mixed forest', 'Moors and heathland'],
            'relative_to': None},
        'Htls':{
            'name': 'Hotels_EU',
            'label': '# Hotels in contour',
            'method': 'count_within_contour',
            'source': r'\\wur\dfs-root\PROJECTS\sastdes\Geodata_SAStDes\Hotels_Europe_shp\Hotels_Cleaned_EU_05_FullTable_EPSG-3035.shp',
            'sum_stat': None,
            'classes': None,
            'relative_to': None},
        'Htls_sq_km': {
            'name': 'Hotels_EU',
            'label': '# Hotels per square km',
            'method': 'count_within_sq_km',
            'source': r'\\wur\dfs-root\PROJECTS\sastdes\Geodata_SAStDes\Hotels_Europe_shp\Hotels_Cleaned_EU_05_FullTable_EPSG-3035.shp',
            'sum_stat': None,
            'classes': None,
            'relative_to': None},
        'N37': {
            'name': 'Bare_rock',
            'label': 'Area of bare rocks',
            'method': 'categorical',
            'source': r'\\wur\dfs-root\PROJECTS\sastdes\Geodata_SAStDes\LC2000_tiff\lc2000_etrs0.tif',
            'sum_stat': None,
            'classes': ['Bare rocks'],
            'relative_to' :None},
        'G12a': {
            'name': 'Max altitude',
            'label': 'Maximum altitude',
            'method': 'sum_stat',
            'source': r'\\wur\dfs-root\PROJECTS\sastdes\Geodata_SAStDes\EU_DEM\EU_DEM_100m.tif',
            'sum_stat': 'max',
            'classes': None,
            'relative_to': None},
        'G12b': {
            'name': 'Altitude',
            'label': 'Mean altitude above mean sea level',
            'method': 'sum_stat',
            'source': r'\\wur\dfs-root\PROJECTS\sastdes\Geodata_SAStDes\EU_DEM\EU_DEM_100m.tif',
            'sum_stat': 'mean',
            'classes': None,
            'relative_to': None},
        'E7b_a': {
            'name': 'Percentage water bodies',
            'label': '% water bodies in destination',
            'method': 'intersect',
            'source': r'\\wur\dfs-root\PROJECTS\sastdes\Geodata_SAStDes\ESRI_major_inland_water_europe_shp\eur_inland_water_esri_epsg3035.shp',
            'sum_stat': None,
            'classes': None,
            'relative_to': 'percentage_per_contour'},
        'E7b_b': {
            'name': 'Count water bodies',
            'label': '# water bodies in destination',
            'method': 'intersect',
            'source': r'\\wur\dfs-root\PROJECTS\sastdes\Geodata_SAStDes\ESRI_major_inland_water_europe_shp\eur_inland_water_esri_epsg3035.shp',
            'sum_stat': None,
            'classes': None,
            'relative_to': 'count_per_contour'},
        'E7b_c': {
            'name': 'Area water bodies',
            'label': 'Acreage sq km water bodies in destination',
            'method': 'intersect',
            'source': r'\\wur\dfs-root\PROJECTS\sastdes\Geodata_SAStDes\ESRI_major_inland_water_europe_shp\eur_inland_water_esri_epsg3035.shp',
            'sum_stat': None,
            'classes': None,
            'relative_to': 'sq_km_per_contour'},
        'N6b': {
            'name': 'Shoreline length',
            'label': 'Shoreline lenght',
            'method': 'line_length',
            'source': r'\\wur\dfs-root\PROJECTS\sastdes\Geodata_SAStDes\natural_earth_coastlines\ne_10m_coastline_epsg3035_clip.shp',
            'sum_stat': None,
            'classes': None,
            'relative_to': None}
    }
