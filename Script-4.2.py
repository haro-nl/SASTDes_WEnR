# Let op ! Python 3 ! gekoppeld aan ArcGisPro !
# Let op ! Aparte module bij dit script !

import sys, os, time, imp
import xlrd
import arcpy

import ProcMod_4_2 as ProcMod
imp.reload ( ProcMod )

# -------------------------------------------------------------------
#  RUN parameters, voor het gemak nog even hard gecodeerd

Xlsx = r'E:\Klussen\SASTDes\Version4\StuurSheet-4.xlsx'

##Contours = r'E:\Klussen\SASTDes\Data\gadm36_ESP_shp\gadm36_ESP_2.shp'
##CntrsIDfield = 'GID_2'

Contours = r'\\wurnet.nl\dfs-root\PROJECTS\SASTDes\Geodata_SAStDes\EU_NUTS\EU_NUTS_GISCO_2010.gdb\NUTS_Level0'
CntrsIDfield = 'NUTS_ID'

GDBcode = 'db05'

Path_GDBs = r'E:\Klussen\SASTDes\Data'

# Keuze workspaces ...
WS1 = sys.path[0]  # is het dir waar dit script staat
WS2 = 'in_memory'
arcpy.env.workspace = WS2
arcpy.env.scratchWorkspace = WS2

# Overschrijf bestaande data ?
arcpy.env.overwriteOutput = True

# Key-Value-regels printen tijdens de run ?
## staat nu in de Module-code ...
##DoPrintKV = False

# BreakAfter geeft aan of er uit de contour-verwerking-loop wordt gesprongen
# Zet op 9e99 voor UIT en op 1, 2, 3, 4, 5 oid voor AAN
BreakAfter = 9e99

# -------------------------------------------------------------------

def Init_Run ( xlsx_full, contours_full, gdb_path, gdb_code ) :

  global Table1, Run, TmStruct
  
  Table1 = os.path.join ( gdb_path, 'Database_General.gdb' )
  Table1 = os.path.join ( Table1, 'ProgramRuns' )
  Fields1 = [ 'RunID', 'Date_Text', 'Date_Sec', 'StuurSheet', 'Contours', 'DB_Code', 'Ended_OK' ]
  
  utc = time.time()
  sec = round ( utc )
  TmStruct= time.localtime ( utc )
  txt = time.strftime ( '%Y-%m-%d %H:%M:%S %z', TmStruct )
  
  # Zoek het hoogste run-nummer via search-cursor
  run_max = 0
  with arcpy.da.SearchCursor ( Table1, Fields1 ) as rows :
    for row in rows :
      run = row[0]
      indx = run.find('_')
      run = run[indx+1:]
      run = int ( run )
      run_max = max ( run, run_max )
      ##print ( run, run_max )

  # Maak een nieuw run-nummer (text,5cijfers,voorloopnullen)
  Run = 'Run_%05i' % (run_max+1)

  xls = os.path.basename ( xlsx_full )
  ftrs = os.path.basename ( contours_full )

  # verzamel alle verkregen veld-waarden in een list
  # Zelfde volgorde als fields-list !
  row = [ Run, txt, sec, xls, ftrs, gdb_code, 0 ]

  # voeg deze Run als record toe aan table via insert-cursor
  InCursor1 = arcpy.da.InsertCursor ( Table1, Fields1 )
  InCursor1.insertRow ( row )

  # Deze InsertCursor is klaar en kan/moet(?) weg
  del InCursor1
  
  print ( 'Started: %s' % Run )

  return # RunTableFull

# -------------------------------------------------------------------

print()
print ( '-'*75 )

# Maak de database-naam en check/verzeker het bestaan ervan
GDBnaam = 'Database-%s.gdb' % GDBcode
GDBfull = os.path.join ( Path_GDBs, GDBnaam )
if not arcpy.Exists ( GDBfull ) :
  arcpy.CreateFileGDB_management ( Path_GDBs, GDBnaam )
  ##TblTmplt = os.path.join ( Path_GDBs, 'Database_Templates.gdb' )
  ##TblTmplt = os.path.join ( TblTmplt, 'ProgramRuns_tmplt' )
  ##arcpy.CreateTable_management ( GDBfull, 'ProgramRuns', TblTmplt )

# Maak eerst een nieuw record aan voor deze programma-run
Init_Run ( Xlsx, Contours, Path_GDBs, GDBcode )

book = xlrd.open_workbook ( Xlsx )

# doe eerst even het sheet met de Indicator DataSet gegevens
sheet = book.sheets()[1]  # Neem "Sheet2"
SheetCols = {}
for i in range ( sheet.ncols ) :
  C = sheet.row_values(0)[i] # Veldnamen staan in de eerste (0) rij
  if C :
    SheetCols[C] = i # dict-key is kolomnaam, dict-value is kolomnummer
IndDataDict = {}
for r in range(1,sheet.nrows) :
  Doen = sheet.row_values(r)[SheetCols['Active']]
  Doen = str ( Doen )[:1].upper()
  Doen = Doen in [ 'J', 'Y', 'T', 'X', '1', '*' ]
  if not Doen :  continue   # regel is niet actief
  Ind = sheet.row_values(r)[SheetCols['Indicator_Data']]
  if not Ind :  continue    # Ind is leeg
  Pad = sheet.row_values(r)[SheetCols['data_path']]
  Set = sheet.row_values(r)[SheetCols['data_set' ]]
  IndDataDict[Ind] = [ Pad, Set ]

# Nu de (eerste) sheet met de gewenste indicatoren
sheet = book.sheets()[0]  # Neem "Sheet1"
SheetCols = {}
for i in range ( sheet.ncols ) :
  C = sheet.row_values(0)[i] # Veldnamen staan in de eerste (0) rij
  if C :
    SheetCols[C] = i # dict-key is kolomnaam, dict-value is kolomnummer

print ( '%i Indicator lines ...' % (sheet.nrows-1) )
IndicatorsDone = []
for r in range(1,sheet.nrows) :
  # Begin met het IndctrID en check of het kan/mag/moet
  IndctrID = sheet.row_values(r)[SheetCols['Indicator_ID']]
  print()
  print ( ' --- "%s" = "%s" ---' % ( IndctrID, sheet.row_values(r)[SheetCols['Indicator_name']] ) )
  if not IndctrID :
    print ( 'No processing possible for this Indicator' )
    continue
    
  Doen = sheet.row_values(r)[SheetCols['Active']]
  Doen = str ( Doen )[:1].upper()
  Doen = Doen in [ 'J', 'Y', 'T', 'X', '1', '*' ]
  if not Doen :
    print ( 'No processing requested for this Indicator' )
    continue

  if IndctrID.upper() in IndicatorsDone :
    print ( 'Deze indicator "%s" is al geweest' % IndctrID )
    continue
  else :
    IndicatorsDone.append ( IndctrID.upper() )

  # Let op ... IndDat moet altijd bestaan, ook voor %-berekeningen !
  # Alles is alleen OK als IndDat in de IndDataDict voor komt
  OK = True
  IndDat = sheet.row_values(r)[SheetCols['Indicator_Data']]
  if not IndDat :   # is leeg
    OK = False
  if IndDat :   # is niet leeg
    OK = IndDat in IndDataDict
  if not OK :
    print ( 'Geen gegevens (in Sheet2) voor de opgegeven Indicator-Data "%s"' % IndDat )
    continue

  # Het InfoDictionary voor deze Indicator
  IndInfoDict = {}
  IndInfoDict['Run'] = Run
  IndInfoDict['DB'] = GDBnaam
  for K in SheetCols :
    V = sheet.row_values(r)[SheetCols[K]]
    if V :
      IndInfoDict [ K ] = V
  K = 'data_path' ; V = IndDataDict[IndDat][0] ; IndInfoDict [ K ] = V
  K = 'data_set'  ; V = IndDataDict[IndDat][1] ; IndInfoDict [ K ] = V

  # Bundel de belangrijkste global variabelen in een Dict
  GlobalNames = [  'WS1', 'Run', 'TmStruct', 'Contours', 'CntrsIDfield',
                   'GDBfull', 'Path_GDBs', 'IndInfoDict', 'BreakAfter' ]
  MainGlobals = {}
  for G in GlobalNames :
    PyCode = "MainGlobals['%s'] = %s" % ( G, G )
    ##print ( 'PyCode = "%s"' % PyCode )
    exec ( PyCode )

  # Roep de verwerkende routine aan binnen een andere module
  # Geef de gebundelde globale variabelen als argument door,
  # opdat ze in die module ook zichtbaar zijn/worden
  ProcMod.DoeDezeIndicator ( MainGlobals )

  if ( 'Results' not in IndInfoDict ) \
     or ( IndInfoDict['Results'] < 1 ) :
    print ( 'Geen resultaten voor deze Indicator-definitie "%s"' % IndctrID )
    continue

  # InfoDictionary verwerken naar Tabel
  Table3 = os.path.join ( Path_GDBs, 'Database_General.gdb' )
  Table3 = os.path.join ( Table3, 'Ind_Run_Info' )
  Fields3 = [ 'DB', 'Tabel', 'Sleutel', 'Waarde' ]
  InCursor3 = arcpy.da.InsertCursor ( Table3, Fields3 )
  V_DB    = IndInfoDict['DB']
  V_Tabel = IndInfoDict['Tabel']
  for K in IndInfoDict :
    if K not in [ 'DB', 'Tabel' ] :
      V = IndInfoDict[K]
      if isinstance ( V, str ) :
        if len(V) > 25 :
          V = V[:21] + ' ...'
      row = [ V_DB, V_Tabel, K, V ]        
      InCursor3.insertRow ( row )
  del InCursor3

  # test-situatie : spring uit de loop na de eerste Indicator
  ##break

# Gebruik een UpdateCursor op Table1 om daarvan het veld Ended_OK op "1" te zetten.
# Alleen voor deze Run natuurlijk.
Flds = [ 'RunID', 'Ended_OK' ]
with arcpy.da.UpdateCursor ( Table1, Flds ) as Rows :
  for row in Rows :
    if row[0] == Run :
      row[1] = 1
      Rows.updateRow ( row )

print ( '-'*75 )

