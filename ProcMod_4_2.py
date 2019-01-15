# Let op ! Python 3 ! gekoppeld aan ArcGisPro !

import sys, os, time
import arcpy

# Key-Value-regels printen tijdens de run ?
DoPrintKV = False

# -------------------------------------------------------------------

def MakeTableName ( IndStr ) :

  # Gebruik steeds dezelfde "struct"-time uit Init-Run
  DateTimeStr = time.strftime ( '%Y%m%d_%H%M%S', TmStruct )
  IndTableName = 'Ind_%s_%s'   % ( IndStr, DateTimeStr )

  return IndTableName

# -------------------------------------------------------------------

def GetNeeded ( IndName ) :

  # Open en lees de Indicator-uitvoer-tabel die eerder
  # in dezezelfde run is aangemaakt en maak er een Dictionary van
  # met Key = ContourID  en Value = Value
  theDict = {}
  TblName = MakeTableName ( IndName )
  TblFull = os.path.join ( GDBfull, TblName )
  Fields = [ 'ContourID', 'Value' ]
  with arcpy.da.SearchCursor ( TblFull, Fields ) as rows :
    for row in rows :
      ##print ( row )
      Key = row[0]
      Pos = Key.index ( ' * ' )
      Key = Key[Pos+3:]
      Val = row[1]
      Pos = Val.index ( ' ha' )
      Val = Val[:Pos]
      theDict[Key] = float(Val)

  print ( 'read %i values from "%s"' % ( len(theDict), TblName ) )

  return theDict

# -------------------------------------------------------------------

def DoeDezeIndicator ( GlobalsDict ) :

  # globaal gemaakt (test)
  ##global Geom1, Geom2, OutRas, NeedDict, Contours

  # Globaal gebruikt : WS1 Run TmStruct Contours CntrsIDfield
  #                    GDBfull Path_GDBs IndInfoDict

  for G in list(GlobalsDict.keys()) :
    code = "global %s ; %s = GlobalsDict['%s']" % ( G, G, G )
    ##print ( 'code = "%s"' % code )
    exec ( code )

  SR1 = arcpy.Describe ( Contours ).spatialReference

  OK = True
  
  # de Indicator invoer data
  IndData = IndInfoDict['Indicator_Data'].upper()
  IndFullPath = os.path.join ( IndInfoDict['data_path'], IndInfoDict['data_set'] )
  if IndData.startswith ( 'CORINE' ) or ( IndData == 'LC2000' ) :
    IndRas = IndFullPath
    # Maak een raster-object van de raster-naam-string (werkt mischien iets sneller)
    IndRas = arcpy.Raster ( IndRas )
    IndExt = arcpy.Describe ( IndRas ).extent
    SR2 = arcpy.Describe ( IndRas ).spatialReference
    CellAreaM2 = 100 * 100    # Belangrijk bij oppervlakteberekening !

  elif IndData.startswith ( 'EU_DEM' ) :
    IndRas = IndFullPath
    # Maak een raster-object van de raster-naam-string (werkt mischien iets sneller)
    IndRas = arcpy.Raster ( IndRas )
    IndExt = arcpy.Describe ( IndRas ).extent
    SR2 = arcpy.Describe ( IndRas ).spatialReference

  elif IndData.startswith ( 'HOTEL' ) :
    IndFC = r'E:\Klussen\SASTDes\Data\Hotels_Europe.gdb\Hotels_Cleaned_EU_05_FullTable'
    IndExt = arcpy.Describe ( IndFC ).extent
    SR2 = arcpy.Describe ( IndFC ).spatialReference
    ##print ( 'SR1 == SR2 ? %s' % bool(SR1==SR2) )

  else :
    print ( 'Unkown IndicatorDataSet "%s" ... no results' % IndData )
    OK = False
    ##return

  # de korte naam van de Contouren dataset, voor in het ContourID
  # Haal er een stukje af want het veld is niet breed genoeg.
  CntrsNm = os.path.basename ( Contours )
  if CntrsNm[-4:].lower() == '.shp' :
    CntrsNm = CntrsNm[:-4]

  # Begin nu onderscheid te maken naar de verschillende "methodes"
  # zoals aangegeven in de stuur-sheet.
  Method = IndInfoDict['Method']

  T0 = time.time()
  Results = []        # Hierin komen de resultaten als (Key,Value) tuples

  if not OK : pass

  elif Method == 'S' :
    # Doe de Raster-Statistieken via een een alles-tegelijk-tool-aanpak
    ZSTpath = WS1
    ZSTname = 'ZonalStats.dbf'
    ZSTname = 'ZonalStats_%s_%s.dbf' % ( Run, os.path.splitext(os.path.basename(IndRas.name))[0] )
    ZonalStatsTable = os.path.join ( ZSTpath, ZSTname )
    # De ZonalStatistieken hoeven alleen de eerste keer gemaakt te worden
    # voor dit IndRas en deze Run
    if not arcpy.Exists ( ZonalStatsTable ) :
      print ( 'Creating ZonalStatisticsTable "%s" ...' % ZSTname )
      arcpy.gp.ZonalStatisticsAsTable_sa ( Contours, CntrsIDfield, IndRas,
                                           ZonalStatsTable, "DATA", "ALL" )
    StatClass = IndInfoDict['Class'].upper()
    StatFields = arcpy.ListFields ( ZonalStatsTable, '*' )
    StatFields = [ F.name.upper() for F in StatFields ]
    if not StatClass.upper() in StatFields :
      print ( 'Unknown statistic type "%s"' % StatClass )
    else :
      StatFields = [ CntrsIDfield, StatClass ]
      with arcpy.da.SearchCursor ( ZonalStatsTable, StatFields ) as rows :
        for row in rows :
          ID = row[0]
          Val = row[1]
          Val = '%i m' % round(Val)
          CntrID = '%s * %s' % ( CntrsNm, ID )
          Results.append ( ( CntrID, Val ) )

  # ------------------------------------------------------

  elif Method == 'A' :

    arcpy.env.extent = Contours

    # Doe de Area-berekeningen via een een alles-tegelijk-tool-aanpak
    TApath = WS1
    TAname = 'TabltArea_%s_%s.dbf' % ( Run, os.path.splitext(os.path.basename(IndRas.name))[0] )
    TabAreaTable = os.path.join ( TApath, TAname )
    if arcpy.Exists ( TabAreaTable ) :
      print ( 'ReUsing TabArea-Table "%s" ...' % TAname )
    else :
      ##print ( 'TApath = "%s" ...' % TApath )
      print ( 'Creating TabArea-Table "%s" ...' % TAname )
      arcpy.gp.TabulateArea_sa ( Contours, CntrsIDfield, IndRas, 'VALUE', TabAreaTable )
    global TAfields1
    TAfields1 = arcpy.ListFields ( TabAreaTable, 'VALUE_*' )
    TAfields1 = [ F.name for F in TAfields1 ]
    TAfields2 = [ CntrsIDfield ]
    ClassString = IndInfoDict['Class']
    if isinstance ( ClassString, float ) :
      ClassString = str ( int ( ClassString ) )
    ClassList = ' '.join(ClassString.split(',')).split()
    for Val in ClassList :
      ValField = 'VALUE_%s' % Val
      if ValField in TAfields1 :
        TAfields2.append ( ValField )
      else :
        print ( 'Field(value) "%s" not found in table "%s"' % ( ValField, TAname ) )
    with arcpy.da.SearchCursor ( TabAreaTable, TAfields2 ) as rows :
      for row in rows :
        ID = row[0]
        Val = 0
        for i in range ( 1, len(row) ) :
          Val += row[i]
        Val = round ( Val / 10000 ) # van m2 naar ha, geen decimalen
        Val = '%i ha' % Val
        CntrID = '%s * %s' % ( CntrsNm, ID )

        Results.append ( ( CntrID, Val ) )

  # ------------------------------------------------------

  elif Method in [ 'A2', 'A%', 'Apb', 'S2', 'T' ] :

    # Hier volgen de methodes die resultaten berekenen per Contour-polygon
    # binnen een SearchCursor-for-loop
    
    if Method == 'A%' :  # voorbereiding
      NeedName = IndInfoDict['Needs']
      NeedDict = GetNeeded ( NeedName )

    if Method == 'T' :  # voorbereiding
      # Maak een Layer-object van/voor de Features
      # Om later te kunnen gaan selecteren-per-lokatie
      arcpy.MakeFeatureLayer_management ( in_features = IndFC,
                                          out_layer = "PuntenLayer" )

    # Zet de env.extent op "alle contouren".
    # Het gaat mis als dit in een eerdere gang al eens kleiner is gezet
    arcpy.env.extent = arcpy.Describe ( Contours ).extent

    # Creeer een SearchCursor over de Contour-polygonen-tabel en for-loop de polygonen
    with arcpy.da.SearchCursor ( Contours, [ 'SHAPE@', CntrsIDfield ] ) as rows :
      Tel = 0
      for row in rows :
        Tel += 1
        if Tel > BreakAfter : break      # SnelStop voor bij testen

        PolygonID = str(row[1])
        CntrID = '%s * %s' % ( CntrsNm, PolygonID )
        ##print ( CntrID )

        Geom1 = row[0]    # Geometry , is in SR1
        # Het polygoon her-projecteren van SR1 (Contour-data) naar SR2 (Indicator-data)
        Geom2 = Geom1.projectAs ( SR2 ) # de parameter {transformation_name} kan/moet er ooit nog bij
        CntrExt = Geom2.extent

        # ..................................................................
        if Method == 'T' :
          arcpy.env.extent = "MINOF" #CntrExt
          # Punten tellen die binnen het Contour vallen
          # middels de eerder aangemaakte "PuntenLayer"
          arcpy.SelectLayerByLocation_management ( in_layer = "PuntenLayer",
                                                   select_features = Geom2,
                                                   overlap_type = "INTERSECT",
                                                   selection_type = "NEW_SELECTION" )
          ##Val = MyCount ( "PuntenLayer" )
          Val = int ( arcpy.GetCount_management ( "PuntenLayer" ).getOutput(0) )
          Val = '%i #' % Val
          Results.append ( ( CntrID, Val ) )
        # ..................................................................
        elif Method == 'A%' :
          # Values worden berekend uit vorige waarden en Shape.Area
          if not PolygonID in NeedDict :
            print ( 'Skipped contour "%s" : Area "%s" not found' % ( PolygonID, NeedName ) )
            continue
          AreaInd = NeedDict[PolygonID]
          AreaAll = Geom2.area / 10000  # in hectares
          Val = '%.1f %%' % ( 100*AreaInd/AreaAll )
          Results.append ( ( CntrID, Val ) )
        # ..................................................................
        elif Method in [ 'A2','Apb' ] :
          if Method == 'Apb' :
            # Geom2 omvormen van contour naar punt-buffer
            Pnt1 = Geom2.centroid   # is Point object
            Pnt2 = arcpy.PointGeometry ( Pnt1, SR2 )
            BufDist = IndInfoDict['Buf_m']
            Geom2 = Pnt2.buffer ( BufDist )  # een nieuwe Geom2 !
            CntrExt = Geom2.extent
          # Area Values worden via GIS functies berekend uit een raster
          if CntrExt.disjoint ( IndExt ) :
            ##print ( 'CntrExt : %9i , %9i, %9i, %9i' % ( CntrExt.XMin, CntrExt.XMax, CntrExt.YMin, CntrExt.YMax ) )
            ##print ( ' IndExt : %9i , %9i, %9i, %9i' % (  IndExt.XMin,  IndExt.XMax,  IndExt.YMin,  IndExt.YMax ) )
            print ( 'Geen overlap tussen Contour "%s" en Indicator' % PolygonID )
            continue

          arcpy.env.extent = "MINOF" #CntrExt
          OutRas = arcpy.sa.ExtractByMask ( IndRas, Geom2 )

          # ---test--- bewaar het (laatste) rastertje
          if True : # Method == 'Apb' :
            Rastertje = os.path.join ( os.path.dirname(sys.argv[0]), 'MaskRas.tif' )
            OutRas.save ( Rastertje )
            ##print ( 'Voor MaskRastertje zie "%s"' % Rastertje )

          if not OutRas.maximum :  # is None en dat geeft aan dat alles NoData is
            print ( '%s >>> All NoData !!!' %  CntrID )
            continue
          
          # Verzamel de oppervlakten van de klasses in ClassList
          # als/via cellen count uit de VAT van OutRas
          ClassString = IndInfoDict['Class']
          if isinstance ( ClassString, float ) :
            ClassString = str ( int ( ClassString ) )
          ##ClassList = ClassString.split(',')
          ##ClassList = [ C.strip() for C in ClassList ]
          ClassList = ' '.join(ClassString.split(',')).split()
          ##print ( ClassList )
          CountSum = 0
          with arcpy.da.SearchCursor ( repr(OutRas), [ 'VALUE', 'COUNT' ] ) as rowws :
            for roww in rowws :
              Val = roww[0]
              Cnt = roww[1]
              if str(Val) in ClassList :
                CountSum += Cnt
          # Maak hectares van de getelde cellen.
          m2 = CountSum * CellAreaM2
          ha = m2 / 10000
          Val = '%i ha' % round ( ha )
          Results.append ( ( CntrID, Val ) )
        # ..................................................................
        elif Method == 'S2' :
          # Deze methode "S2" als alternatief voor de snellere procedure "S"
          # Clip een rastertje en vraag Min, Mean of Max
          if CntrExt.disjoint ( IndExt ) :
            print ( 'Geen overlap tussen Contour "%s" en Indicator' % PolygonID )
            continue
          arcpy.env.extent = CntrExt
          OutRas = arcpy.sa.ExtractByMask ( IndRas, Geom2 )
          # ---test--- bewaar het (laatste) rastertje
          if False : # False of True
            Rastertje = os.path.join ( os.path.dirname(sys.argv[0]), 'MaskRas.tif' )
            OutRas.save ( Rastertje )
            ##print ( 'Voor MaskRastertje zie "%s"' % Rastertje )
          if not OutRas.maximum :  # is None en dat geeft aan dat alles NoData is
            print ( '%s >>> All NoData !!!' %  CntrID )
            continue
          StatClass = IndInfoDict['Class'].upper()
          if StatClass == 'MIN'  : Val = OutRas.minimum
          if StatClass == 'MEAN' : Val = OutRas.mean
          if StatClass == 'MAX'  : Val = OutRas.maximum
          Val = '%i m' % round(Val)
          Results.append ( ( CntrID, Val ) )
        # ..................................................................
      ##for
    ##with
    try : del OutRas
    except : pass

  # ------------------------------------------------------
  else :
    print ( 'Unkown Calculation Method Code "%s" ... no results' % Method )
    OK = False

  IndID = IndInfoDict['Indicator_ID']
  Tel = len ( Results )
  IndInfoDict['Results'] = Tel
  if Tel > 0 :
    # Maak een tabel voor deze Indicator
    IndTblName = MakeTableName ( IndID )
    IndTblFull = os.path.join ( GDBfull, IndTblName )
    IndTblTmplt = os.path.join ( Path_GDBs, 'Database_General.gdb' )
    IndTblTmplt = os.path.join ( IndTblTmplt, 'Ind_tmplt' )
    arcpy.CreateTable_management ( out_path = GDBfull,
                                   out_name = IndTblName,
                                   template = IndTblTmplt )

    print ( 'Created : "%s"' % IndTblFull )
    IndInfoDict['Tabel'] = IndTblName

    # Activeer een InsertCursor voor deze nieuwe Values-tabel
    Fields2 = [ 'ContourID', 'Value' ]
    InCursor2 = arcpy.da.InsertCursor ( IndTblFull, Fields2 )
    # Result-records toevoegen
    for KVtuple in Results :
      if DoPrintKV :
        print ( 'Key: "%s"  >  Value: "%s"' % KVtuple )
      InCursor2.insertRow ( KVtuple )
    # Uitvoer-tabel is klaar, InsertCursor kan/moet weg
    del InCursor2

    T1 = time.time()
    print ( '%i contouren verwerkt in %i sec' % ( Tel , T1-T0 ) )
  ##else :
  ##  IndInfoDict['Tabel'] = 'NONE (no results)'
  ##  print ( '!!! No results !!! no table for this indicator "%s" !!!' % IndID )

  return

# -------------------------------------------------------------------

if __name__ == '__main__' :
  print ( '<<< This python module "%s" is not meant to be executed as a main program >>>'
          % os.path.basename ( sys.argv[0] ) )
