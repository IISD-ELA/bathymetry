######################################################################################################

### Script for Bathymetry data processing to take raw transect data and produce useful outputs

### by Chris Hay, IISD-ELA
### date: 2022-12-16
### version: 15

### Written for Python 3 using ArcGIS Pro
### The script must be run in an environment with access to arcpy (e.g., in ArcGIS Pro Project's Python window)

### Parts of script
###   1) Variables
###   2) Raster DEM
###   3) Contour Lines
###   4) Tabular - area, volume, summary stats, metadata
###   5) Maps

######################################################################################################

### 1) Variables
###      This section is important to run before anything else.
###      This is where you will have to carefully enter file paths and metadata variables before each lake is run.

## Import arcpy and os before can do anything
from re import X
import arcpy
import os
from arcpy.sa import *

## Lake number you are currently working on - just number (e.g., "106" - include quotes; for two digit ones do e.g., "93" not "093")
lake_num = "304"
## Lake sublocation you are currently working on - usually LA for whole lake, or e.g., NB SB if a sub-basin - include quotes
lake_sub = "LA"

## Based on the above two, we will automatically create a few variables that are useful later - leave this section as is and continue on from next section
# Create new variable lake_name with underscore and no quotes
lake_name = lake_num + "_" + lake_sub
# Create new variable lake_name_space_quotes (has space instead of underscore and surrounded by single quotes)
lake_name_space = lake_num + " " + lake_sub
# Create new variable lake_name_space_quotes (has space instead of underscore and surrounded by single quotes)
lake_name_space_quotes = "'" +  lake_num + " " + lake_sub + "'"

## Metadata (this is used to populate fields in the table for step 4)
# External users (outside of IISD-ELA) will not understand the codes and initials used here, and the Google Sheet links will not work - you will have to make your own
# Most of the metadata values are available and should be copied from the file "Bathymetry Lake Survey Metadata_YYYY-MM-DD.xlsx", stored under SharePoint > ELA > Bathymetry > Metadata > LakeSurveying
# Master definitions (most trustworthy, updated) are in the IISD-ELA Data Dictionary: https://docs.google.com/spreadsheets/d/1mmCWmmsqkETSPaKjJ8EY9sornfC-6DifAap51m2godY/edit#gid=0
# Things that change more often lake to lake / run to run:
activity_start_date = '2022-08-15' # 'YYYY-MM-DD' date collected/sampled in field - "survey start date" from "IISD-ELA bathymetry metadata"
activity_end_date = '2022-08-15' # YYYY-MM-DD "survey end date" from "IISD-ELA bathymetry metadata"
monitoring_location_name = lake_name_space # Established in variables above (leave this as is!)
collected_by = 'UNK' # Researcher who was in the field / on the lake - "collected_by" in metadata sheet - userid (unique designation) from https://docs.google.com/spreadsheets/d/1YmwXRWOfR2mlMTZIOEzj0nYiCCt7KcDVZa02OmRRCxc/edit#gid=1069795151
update_date = '2022-12-08' # 'YYYY-MM-DD' current date running this script
lake_level_m = '53.580' # Copy from "IISD-ELA bathymetry metadata"
benchmark_id  = '23' # Copy from "IISD-ELA bathymetry metadata"
lake_level_m_asl = '414' # Copy from "IISD-ELA bathymetry metadata"
lake_level_asl_method = 'The benchmarks for L 303 and 304 are tied in to the master benchmark, which allows an estimate of elevation..' # Copy from "IISD-ELA bathymetry metadata"
general_comment = 'Lake levels asl are estimates and not accurately measured (to approx. 1 m).' # Copy from "IISD-ELA bathymetry metadata"
# Check these too, but know that they commonly or always stay the same.
dataset_code = 'B01' # Will always be this (general data set name for bathy tabular summary, volume, and area data) - code from https://docs.google.com/spreadsheets/d/1YmwXRWOfR2mlMTZIOEzj0nYiCCt7KcDVZa02OmRRCxc/edit#gid=627326291
method_sample_code = 'BFF' # Corresponds with "method sample" from metadata sheet and code from https://docs.google.com/spreadsheets/d/1YmwXRWOfR2mlMTZIOEzj0nYiCCt7KcDVZa02OmRRCxc/edit#gid=1092893358
method_process_code = 'BAP' # Will always be this if running this script. code from https://docs.google.com/spreadsheets/d/1YmwXRWOfR2mlMTZIOEzj0nYiCCt7KcDVZa02OmRRCxc/edit#gid=140073216
entered_by = 'LEH' # Typically Lee (whoever gets GPS points from fish finder into csv) - "entered_by" in metadata sheet - initials (unique designation) from https://docs.google.com/spreadsheets/d/1YmwXRWOfR2mlMTZIOEzj0nYiCCt7KcDVZa02OmRRCxc/edit#gid=1069795151
processed_by = 'CRJH' # Official initials of you running this script - make sure match unique designation from https://docs.google.com/spreadsheets/d/1YmwXRWOfR2mlMTZIOEzj0nYiCCt7KcDVZa02OmRRCxc/edit#gid=1069795151
validated_by = '' # As of writing this, no general defined validation process in place, so leave blank, but eventually - initials (unique designation) from https://docs.google.com/spreadsheets/d/1YmwXRWOfR2mlMTZIOEzj0nYiCCt7KcDVZa02OmRRCxc/edit#gid=1069795151
approved_by = '' # As of writing this, no approval process in place, so leave blank, but eventually - initials (unique designation) from https://docs.google.com/spreadsheets/d/1YmwXRWOfR2mlMTZIOEzj0nYiCCt7KcDVZa02OmRRCxc/edit#gid=1069795151
gear_type_code = 'F12' # Corresponds with "survey equipment" from metadata sheet and code from https://docs.google.com/spreadsheets/d/1YmwXRWOfR2mlMTZIOEzj0nYiCCt7KcDVZa02OmRRCxc/edit#gid=1295028502


## File paths for key locations
##   Make sure no \ at end, and must be in single quotes. Also, keep lowercase R, otherwise need to switch \ slash to / (Python rules).
##   See the How To document for some discussion on this. File paths will be different for each person running this script.

## Base paths

## Project (ArcGIS Pro Project folder)
prj_path = r'C:\Users\chay\OneDrive - IISD\Documents\Bathymetry\Workspaces\TransectsProcessingPipeline'

## Final outputs path, that is, SharePoint > ELA (wherever locally storing OneDrive shortcut folders, or temp folders to manually upload to there later)
final_outputs_path = r'C:\Users\chay\OneDrive - IISD\Documents'


## Final outputs paths
# These are all locations that are not purged or overwritten in the script.
# Copying outputs from intermediate to final locations is flagged where this occurs in the script, and manual checks are recommended at those points.

## Transects Geospatial Points (IISD-ELA) gdb
transect_points_gdb = final_outputs_path + r'\Bathymetry\Data\Transects\Geospatial\TransectPointsIISDELA.gdb'

## Corrected lakes polygons geodatabase (GIS > Data & Metadata - on SharePoint)
corrected_lakes_gdb = final_outputs_path + r'\GIS\Data & Metadata\ELA Lakes\Polygons\Corrected\LakePolygons.gdb'

## DEMs/Rasters geodatabase (Bathymetry > Data - on SharePoint)
final_raster_dems_gdb = final_outputs_path + r'\Bathymetry\Data\DEMs (rasters)\DEMsRasters.gdb'

## Contours geodatabase (Bathymetry > Data - on SharePoint)
final_contours_gdb = final_outputs_path + r'\Bathymetry\Data\Contours (geospatial line files)\Contours.gdb'

## Maps folder (Bathymetry > Data - on SharePoint)
final_maps_folder = final_outputs_path + r'\Bathymetry\Data\Maps\Current ELA'

## CSVs folder (Database > Data > Data to Upload > Bathy - on SharePoint)
final_csvs_folder = final_outputs_path + r'\Database\Data and Metadata\Data\Data to Upload\Bathy'


## Inputs paths

## Transect csvs location (raw data that will be input - see how-to doc for info on formatting)
transects_path = prj_path + r"\Inputs\InputTransects"

## Bathymetry data template table (schema, used for part 4 tabular work) - assumes is located under project location (change if needed)
bathymetry_data_template_table = prj_path + r"\Inputs\TemplateTables\bathy_db_data_table_template.csv"

## Bathymetry metadata template table (schema, used for part 4 tabular work) - assumes is located under project location (change if needed)
bathymetry_meta_template_table = prj_path + r"\Inputs\TemplateTables\bathy_db_meta_table_template.csv"

## Bathymetry summary template table (schema, used for part 4 tabular work) - assumes is located under project location (change if needed)
bathymetry_summary_template_table = prj_path + r"\Inputs\TemplateTables\bathy_summary_stats_table_template.csv"

## URL for the best lakes polygon GIS file currently available
# At the time of writing this script, this is "ELA_LakesALL20141030" on ArcGIS Online (here is the link, need /0 to specify it at end))
# Make sure URL is in single quotes.
best_lakes_polygon = 'https://services8.arcgis.com/bbOf746oOv9MFzD7/arcgis/rest/services/ELA_LakesALL20141030/FeatureServer/0'


## Intermediate workspaces setup

## Create geodatabase for intermediate data (will be cleared and overwritten each time script is re-run)
# Skip this next step if you already have already created the Intmd.gdb (geodatabase for intermediate files) and do not want its contents erased.
# You may want to keep your intermediate files if you have returned to this section to change some variables but have not finished processing a lake (through to end of part 4)
# Otherwise, between processing different lakes, the Intmd.gdb should be cleared
arcpy.management.CreateFileGDB(prj_path, "Intmd.gdb")

## Create folder for intermediate csv data (will not be cleared and overwritten if folder already exists)
# Unlike the Intmd.gdb creation step, this step only creates the folder if it is not already there, otherwise it does nothing.
# This step will not clear the contents of the folder.
# The folder should be manually cleared regularly (e.g., between processing every few lakes), to avoid clutter and confusion.
arcpy.management.CreateFolder(prj_path, "Intmd_csvs")

# Set intermediate locations to simple variables so easy (short) to reference throughout script
intmd_gdb = prj_path + '\Intmd.gdb'
intmd_csvs = prj_path + '\Intmd_csvs'
# Set project to recognize current as where you are working (this allows for short layer references in the script)
aprx = arcpy.mp.ArcGISProject('CURRENT')
# Set default geodatabase and workspace to intermediate geodatabase (so that do not need to input it for each command - shorter, tidier script)
aprx.defaultGeodatabase = intmd_gdb
arcpy.env.workspace = intmd_gdb


######################################################################################################

### 2) Raster DEM
# Assumes you have run previous variables section

## Set up a rough lake polygon outline to work with

# Select just the lake you are interested in (by number specified at start) from the ArcGIS Online lake polygons file, and copy it into the Intmd.gdb
arcpy.analysis.Select(best_lakes_polygon, 'Lake_Selection','LakeNumber = ' + lake_num)

# Project coordinate system from WGS 1984 Web Mercator (auxiliary sphere) to NAD83 UTM zone 15N and put into Intmd.gdb
arcpy.management.Project('Lake_Selection', 'Lake_Sel_UTM',arcpy.SpatialReference('NAD 1983 UTM Zone 15N'))

# Make a copy of the lake polygon called "Lake_###_AA_Polygon", which will be worked on manually when switch to the how-to document
arcpy.conversion.FeatureClassToFeatureClass('Lake_Sel_UTM', intmd_gdb, 'Lake_' + lake_name + '_Polygon')

## Convert transect points from csv to geospatial points

# Convert associated transect coordinates csv table into geospatial points feature class (note that here you need os.path.join as Python workaround since backslash reserved for escapes)
arcpy.defense.CoordinateTableToPoint(os.path.join(transects_path, lake_name) + '.csv', 'Lake_Points', 'x', 'DD_2','y',arcpy.SpatialReference('WGS 1984'))

# Project points coordinate system to UTM
arcpy.management.Project('Lake_Points', 'Lake_Points_UTM',arcpy.SpatialReference('NAD 1983 UTM Zone 15N'))

## This is one "final output" from this exercise, so next lines are to copy it to the right places.
# Note this will fail if there is already a copy there (feature class with same name).
# Copy the transect geospatial points from Intmd.gdb to final IISD-ELA Transects Geospatial Points gdb
arcpy.conversion.FeatureClassToFeatureClass('Lake_Points_UTM', transect_points_gdb, 'Lake_' + lake_name + '_Transect_Points')

##########################################################################################
## STOP
##  Now you need to switch from running this script to some manual work - see the detailed instructions in the How To document.
##  Edit Lake_Sel_UTM polygon in Intmd.gdb to go around points and match satellite imagery... to get a "corrected" outline.
##  Also, collect METADATA for the imagery used when tracing the boundary.
##  Check for outliers and remove them.
## REFS
##  Detailed instructions for this are in the associated How To documentation, here:
##   SharePoint > ELA > Bathymetry\Metadata\Methods\Python Script and How To Doc\HowToDoc_BathymetryProcessing_IISD-ELA.docx
##  The metadata Excel file is here:
##   SharePoint > ELA > GIS\Data & Metadata\ELA Lakes\Polygons\Corrected\Metadata\LakePolygonsCorrected_Metadata.xlsx
##########################################################################################

# Clean up attributes to get rid of the piles of irrelevant fields (carried over from ArcGIS Online original lake polygon)
arcpy.DeleteField_management('Lake_' + lake_name + '_Polygon', ["OGF_ID", "WBDY_TYPE", "OFF_NAME", "GEL_IDENT", "PERMANENCY", "ACCURACY", "VERISTT_FL", "VERISTT_DT", "COMMENTS", "SYS_AREA", "SYS_PERIM", "GEO_UPD_DT", "EFF_DATE", "Layer", "RefName", "LakeNumber", "Shape_Leng", "CreationDate", "Creator", "EditDate", "Editor", "MonitoringLocationName", "CENTROID_X", "CENTROID_Y", "MaxDepth_m", "MaxDepthMeta", "BathyDate_yr", "RecentFishSurvey_yr", "Manipulations", "FishSpecies", "MaxDepth_txt", "Location_ID", "monitoring_location_id"])

# Add field (column) called 'monitoring_location_name' to attribute table
arcpy.management.AddField('Lake_' + lake_name + '_Polygon','monitoring_location_name','TEXT')

# Populate "monitoring_location_name" column with "lake_name_space_quotes" (established at start) for all records
arcpy.management.CalculateField('Lake_' + lake_name + '_Polygon', "monitoring_location_name", lake_name_space_quotes,"PYTHON3")

## This is one "final output" from this exercise, so next lines are to copy it to the right places.
# Note that this will fail if there is already a copy there (feature class with same name).
# Copy from Intmd.gdb to Corrected Lakes gdb
arcpy.conversion.FeatureClassToFeatureClass('Lake_' + lake_name + '_Polygon',corrected_lakes_gdb,'Lake_' + lake_name + '_Polygon') 

# Select Layer By Location tool - this takes only the transect points that intersect with the lake polygon
# (in some cases there may be points outside the lake outline polygon, e.g., error outliers)
arcpy.analysis.Intersect(['Lake_' + lake_name + '_Polygon','Lake_Points_UTM'], 'Lake_Points_UTM_Int', 'ALL', None, 'INPUT')

# Turn polygon outline into points
arcpy.management.GeneratePointsAlongLines('Lake_' + lake_name + '_Polygon', 'Lake_Corrected_Outline_Points', "DISTANCE", "3 Meters")

# Add field (column) called 'z' to attribute table
arcpy.management.AddField('Lake_Corrected_Outline_Points','z','DOUBLE')

# Populate field with zeroes (outline is at lake edge, therefore depth is 0 metres)
arcpy.management.CalculateField('Lake_Corrected_Outline_Points','z',0,'PYTHON3')

# Merge outline and inner lake points
arcpy.management.Merge(['Lake_Corrected_Outline_Points','Lake_Points_UTM_Int'],'Lake_Points_Merged')

##########################################################
#####
###   The following steps must be run one at a time.
##

# Create raster via interpolation: "Topo to Raster" (this step may take a minute)
with arcpy.EnvManager(mask="Lake_" + lake_name + "_Polygon"):
    arcpy.ddd.TopoToRaster("Lake_Points_Merged z PointElevation", "Raster_TopoToR", 1, "Lake_" + lake_name + "_Polygon", 20, None, None, "NO_ENFORCE", "SPOT", 20, None, 1, 0, 0, 200, None, None, None, None, None, None, None, None)

# Low Pass Filter to slightly blur out artifacts and improve coastline
out_raster1 = arcpy.sa.Filter("Raster_TopoToR", "LOW", "DATA"); out_raster1.save("Raster_LPF")

# Rename layer from out_raster1 to Raster_LPF (for some reason Arc doesn't add layer with name we want) - to avoid potential errors
for lyr in aprx.listMaps(aprx.activeMap.name)[0].listLayers():
    if "out_raster1" in lyr.name:
        layerName = str(lyr.name)
        lyr.name = lyr.name.replace(layerName, "Raster_LPF")

# Further obscure artifacts by blurring a bit more using Focal Statistics
with arcpy.EnvManager(mask="Lake_" + lake_name + "_Polygon"):
    out_raster2 = arcpy.ia.FocalStatistics("Raster_LPF", "Circle 5 CELL", "MEAN", "DATA", 90); out_raster2.save("Raster_FocalStats")

# Rename layer from out_raster2 to Raster_FocalStats (for some reason Arc doesn't add layer with name we want) - to avoid potential errors
for lyr in aprx.listMaps(aprx.activeMap.name)[0].listLayers():
    if "out_raster2" in lyr.name:
        layerName = str(lyr.name)
        lyr.name = lyr.name.replace(layerName, "Raster_FocalStats")

# Get rid of any potential edge errors > 0 by converting them to 0
# Note that the Raster Calculator tool in Python looks different from typical tool scripts, but this should work.(note - raster calculator in Python is unusual / hard to get working - but this worked!)
# You need the Spatial Analyst license for this tool, this is why we load it at the start: from arcpy.sa import *
out_raster3 = Con(Raster("Raster_FocalStats") > 0, 0, Raster("Raster_FocalStats"))
out_raster3.save(intmd_gdb + r"\Raster_Zero")

# Rename layer from out_raster3 to Raster_Zero (for some reason Arc doesn't add layer with name we want) - to avoid potential errors
for lyr in aprx.listMaps(aprx.activeMap.name)[0].listLayers():
    if "out_raster3" in lyr.name:
        layerName = str(lyr.name)
        lyr.name = lyr.name.replace(layerName, "Raster_Zero")

# The raster edges (shoreline) are still not necessarily at 0 (may be slightly below zero).
#  Later steps for producing contours and tabular data will work around this.
#  It is better to work around than force the raster (i.e. add a 0 depth outline) since that just causes further artifacts later.

# Manual check reminder - examine the raster to confirm it look goods and makes sense.
# Run the following to print out possibly useful summary text that will show in the Python window.
print("\n~*~*~*~ MANUAL CHECK REMINDER ~*~*~*~\
\n\nExamine in the map the raster you produced,\
\nto confirm it looks good and makes sense.\
\nIf necessary, re-run previous steps to produce a better raster.\
\n\n(The raster DEM is in the intmd.gdb)\
\nRaster: Raster_Zero\n")

# Once you've manually confirmed, continue running the script.

## This is one "final output" from this exercise, so next lines are to copy it to the right places.
# Note this will fail if there is already a copy there (feature class with same name).
# Copy the raster from Intmd.gdb to Final DEM Rasters gdb
arcpy.management.CopyRaster(intmd_gdb + r"\Raster_Zero",final_raster_dems_gdb + r'\Lake_' + lake_name + '_Raster_DEM')

# Make the raster positive (multiply by -1) for later steps (contours and table)
out_raster4 = Raster("Raster_Zero") * -1
out_raster4.save(intmd_gdb + r"\Raster_Zero_Positive")

# Rename layer from out_raster4 to Raster_Zero_Positive (for some reason Arc doesn't add layer with name we want) - to avoid potential errors
for lyr in aprx.listMaps(aprx.activeMap.name)[0].listLayers():
    if "out_raster4" in lyr.name:
        layerName = str(lyr.name)
        lyr.name = lyr.name.replace(layerName, "Raster_Zero_Positive")

#                                                                         ##
#                    The previous steps had to be run one at a time.     ###
#    The following steps may be able to run more than one at a time.    ####
#                                                                      #####
############################################################################

######################################################################################################

###   3) Contour Lines
# Assumes you have run all previous sections

## Determine contour intervals - two will be created for usability convenience

# Get max depth number
max_depth = (arcpy.GetRasterProperties_management("Raster_Zero_Positive", "MAXIMUM"))

# Change max depth from result to float
max_depth = max_depth.getOutput(0)
max_depth=float(max_depth)

# Assign a contour intervals based on the max depth (i.e. minimum) - aiming for about 5 to 10 levels (best readability on maps)
# Contour interval A:
#   0.25 for 0 < x <= 2
#   0.5 for 2 < x <= 5
#   1.0 for 5 < x <= 12
#   2.0 for 12 < x <= 25
#   5.0 for 25 < x <= 55
#   10.0 for 55 < x <= 150
#   25.0 for 150 < x
# Contour interval B: Provides another option, ensures there's always contours 1 or less
#   0.5 for 0 < x <= 2
#   1.0 for 2 < x <= 5
#   2.0 for 5 < x <= 12
#   1.0 for 12 < x <= 25
#   1.0 for 25 < x <= 55
#   1.0 for 55 < x <= 150
#   1.0 for 150 < x

if (max_depth <= 2):
    contour_interval_a = 0.25
    contour_interval_b = 0.5
elif (max_depth <= 5):
    contour_interval_a = 0.5
    contour_interval_b = 1.0
elif (max_depth <= 12):
    contour_interval_a = 1.0
    contour_interval_b = 2.0
elif (max_depth <= 25):
    contour_interval_a = 2.0
    contour_interval_b = 1.0
elif (max_depth <= 55):
    contour_interval_a = 5.0
    contour_interval_b = 1.0
elif (max_depth <= 150):
    contour_interval_a = 10.0
    contour_interval_b = 1.0
else:
    contour_interval_a = 25.0
    contour_interval_b = 1.0

## FYI print a note to show what the a and b contour intervals will be
print("Contour interval A: " + str(contour_interval_a) + "m")
print("Contour interval B: " + str(contour_interval_b) + "m")

## Make contours A using interval from above
arcpy.sa.Contour("Raster_Zero_Positive", 'Lake_ContoursIntmdA', contour_interval_a, 0, 1, "CONTOUR", None)

## Make contours B using interval from above
arcpy.sa.Contour("Raster_Zero_Positive", 'Lake_ContoursIntmdB', contour_interval_b, 0, 1, "CONTOUR", None)

## For each of those two, need to do some extra cleanup...

# Remove all contour = 0 values and then add corrected lake outline (with field "Contour" Double No Nulls with value at 0) - this is the next several steps.

# Select all but contour = 0 values for each
# A
arcpy.analysis.Select('Lake_ContoursIntmdA', 'Lake_ContoursIntmdA_NoZeroes','Contour > 0')
# B
arcpy.analysis.Select('Lake_ContoursIntmdB', 'Lake_ContoursIntmdB_NoZeroes','Contour > 0')

# Turn polygon outline into line
arcpy.management.PolygonToLine('Lake_' + lake_name + '_Polygon', 'Lake_Outline', "IGNORE_NEIGHBORS")

# Add field (column) called 'Contour' to attribute table
arcpy.management.AddField('Lake_Outline','Contour','DOUBLE')

# Populate field with zeroes (outline is at lake edge, therefore depth 0 is metres)
arcpy.management.CalculateField('Lake_Outline','Contour',0,'PYTHON3')

# We want to include the actual contour interval in the feature class name, so set the interval as a string variable and replace the period character (".", not allowed) with "pt"
# A
contour_interval_a_str = str(contour_interval_a)
contour_interval_a_str_pt = contour_interval_a_str.replace(".", "pt")

# B
contour_interval_b_str = str(contour_interval_b)
contour_interval_b_str_pt = contour_interval_b_str.replace(".", "pt")

# Merge outline with zero-removed contours
# A
arcpy.management.Merge('Lake_Outline;Lake_ContoursIntmdA_NoZeroes', 'Lake_' + lake_name + '_A_Contours_' + contour_interval_a_str_pt + 'm', '', 'NO_SOURCE_INFO')
# B
arcpy.management.Merge('Lake_Outline;Lake_ContoursIntmdB_NoZeroes', 'Lake_' + lake_name + '_B_Contours_' + contour_interval_b_str_pt + 'm', '', 'NO_SOURCE_INFO')

# Clean up attributes to get rid of the piles of irrelevant fields (carried over from ArcGIS Online original lake polygon)
# A
arcpy.DeleteField_management('Lake_' + lake_name + '_A_Contours_' + contour_interval_a_str_pt + 'm', ["ORIF_FID", "GEO_UPD_DT", "WBDY_TYPE", "OFF_NAME", "GEL_IDENT", "PERMANENCY", "ACCURACY", "VERISTT_FL", "VERISTT_DT", "COMMENTS", "SYS_AREA", "SYS_PERIM", "EFF_DATE", "Layer", "RefName", "LakeNumber", "Shape_Leng", "CreationDate", "Creator", "MonitoringLocationName", "CENTROID_X", "CENTROID_Y", "MaxDepth_m", "MaxDepthMeta", "BathyDate_yr", "RecentFishSurvey_yr", "Manipulations", "FishSpecies", "MaxDepth_txt", "Location_ID", "ORIF_FID", "Id", "OGF_ID", "Location", "Sublocation", "EditDate", "Editor", "monitoring_location_id", "ORIG_FID"])
# B
arcpy.DeleteField_management('Lake_' + lake_name + '_B_Contours_' + contour_interval_b_str_pt + 'm', ["ORIF_FID", "GEO_UPD_DT", "WBDY_TYPE", "OFF_NAME", "GEL_IDENT", "PERMANENCY", "ACCURACY", "VERISTT_FL", "VERISTT_DT", "COMMENTS", "SYS_AREA", "SYS_PERIM", "EFF_DATE", "Layer", "RefName", "LakeNumber", "Shape_Leng", "CreationDate", "Creator", "MonitoringLocationName", "CENTROID_X", "CENTROID_Y", "MaxDepth_m", "MaxDepthMeta", "BathyDate_yr", "RecentFishSurvey_yr", "Manipulations", "FishSpecies", "MaxDepth_txt", "Location_ID", "ORIF_FID", "Id", "OGF_ID", "Location", "Sublocation", "EditDate", "Editor", "monitoring_location_id", "ORIG_FID"])

# Add a field (column) for "monitoring_location_name" to the feature classes
# A
arcpy.management.AddField('Lake_' + lake_name + '_A_Contours_' + contour_interval_a_str_pt + 'm', "monitoring_location_name", "TEXT")
# B
arcpy.management.AddField('Lake_' + lake_name + '_B_Contours_' + contour_interval_b_str_pt + 'm', "monitoring_location_name", "TEXT")

# Populate "monitoring_location_name" column with "lake_name_space_quotes" (established at start) for all records
# A
arcpy.management.CalculateField('Lake_' + lake_name + '_A_Contours_' + contour_interval_a_str_pt + 'm', "monitoring_location_name", lake_name_space_quotes,"PYTHON3")
# B
arcpy.management.CalculateField('Lake_' + lake_name + '_B_Contours_' + contour_interval_b_str_pt + 'm', "monitoring_location_name", lake_name_space_quotes,"PYTHON3")

# Manual check reminder - examine the two feature classes to confirm they look good and make sense
# Run these lines to print out possibly useful summary text that will show in the Python window
print("\n~*~*~*~ MANUAL CHECK REMINDER ~*~*~*~\
\n\nExamine in the map and attribute table the two contour feature classes\
\nto confirm they look good and make sense.\
\n(Both are in the intmd.gdb)\
\n\nA contours: Lake_" + lake_name + "_Contours_" + contour_interval_a_str_pt + "m\
\nB contours: Lake_" + lake_name + "_Contours_" + contour_interval_b_str_pt + "m\n")

## These two are "final outputs" from this exercise, so next lines are to copy them to the right places
# Note this will fail if there is already a copy there (feature class with same name)
# A
# Copy from Intmd.gdb to final contours gdb
arcpy.conversion.FeatureClassToFeatureClass('Lake_' + lake_name + '_A_Contours_' + contour_interval_a_str_pt + 'm',final_contours_gdb,'Lake_' + lake_name + '_Contours_' + contour_interval_a_str_pt + 'm')
# B
# Copy from Intmd.gdb to final contours gdb
arcpy.conversion.FeatureClassToFeatureClass('Lake_' + lake_name + '_B_Contours_' + contour_interval_b_str_pt + 'm',final_contours_gdb,'Lake_' + lake_name + '_Contours_' + contour_interval_b_str_pt + 'm')

######################################################################################################

###   4) Tabular - area, volume, summary stats, metadata
# Assumes you have set up and run parts 1-3 (variables, raster, contours)

##  4.0) Table and interval setup

# Assign variable tabular depth interval to a number. Most data users expect 1 m intervals for the tabular data, but other intervals may be used if desired.
tabular_depth_interval = 1
# Print a note for what your tabular depth interval is
print("Tabular depth interval: " + str(tabular_depth_interval) + "m\n")

# Create a table based on data table template
arcpy.management.CreateTable(intmd_gdb, 'Lake_' + lake_name + '_Data_Table', bathymetry_data_template_table)

##  4.1) Tabular - area

##  4.11) Tabular - area - area_interval (i.e. contour type = CONTOUR_POLYGONS)

# Generate contour polygons (same as when made contours, but polygons instead of lines)
arcpy.sa.Contour("Raster_Zero_Positive", 'Lake_ContoursPoly', tabular_depth_interval, 0, 1, "CONTOUR_POLYGON", None)

# Note that a separate step to calculate area is not necessary.
# Area is already correctly calculated and provided from the generate contour polygons step, as the field "Shape_Area".

# Correct the lowest Contour minimum (assume this is where OBJECTID = 1) to change it to 0, not something close to zero
# (This is to resolve one of the side effects of raster coastline edges not being conformed to 0)
arcpy.management.CalculateField("Lake_ContoursPoly", "ContourMin", "Correct(!ContourMin!,!OBJECTID!)", "PYTHON3", """def Correct(contmin,oid):
    if oid == 1:
        return 0
    else:
        return contmin""", "TEXT", "NO_ENFORCE_DOMAINS")

# Add a field (column) for "characteristic_name" to the polygon feature class
arcpy.management.AddField("Lake_ContoursPoly", "characteristic_name", "TEXT")

# Populate "characteristic_name" column with "area_interval" for all records (these are area_interval values)
arcpy.management.CalculateField("Lake_ContoursPoly","characteristic_name","'area_interval'","PYTHON3")

# Append depth, area, and characteristic_name fields to table using field mapping (note I tried to make the field mapping shorter/cleaner than this, but then doesn't work)
arcpy.management.Append("Lake_ContoursPoly", "Lake_" + lake_name + "_Data_Table", "NO_TEST", 'characteristic_name "characteristic_name" true true false 8000 Text 0 0,First,#,Lake_ContoursPoly_Cleaned,characteristic_name,-1,-1;result_value "result_value" true true false 8000 Text 0 0,First,#,Lake_ContoursPoly_Cleaned,Shape_Area,-1,-1;depth_upper "depth_upper" true true false 8000 Text 0 0,First,#,Lake_ContoursPoly_Cleaned,ContourMin,-1,-1;depth_lower "depth_lower" true true false 8000 Text 0 0,First,#,Lake_ContoursPoly_Cleaned,ContourMax,-1,-1', '', '')


##  4.12) Tabular - area - area_cumulative (i.e. contour type = CONTOUR_SHELL)

# Generate contour shell polygons (basically, polygons that represent areas for the cumulative area concept)
arcpy.sa.Contour("Raster_Zero_Positive", 'Lake_ContoursPolyShellUp', tabular_depth_interval, 0, 1, "CONTOUR_SHELL_UP", None)

# Note that a separate step to calculate area is not necessary.
# Area is already correctly calculated and provided from the generate contour shell polygons step, as the field "Shape_Area".

# Correct the lowest Contour minimum (assume this is where OBJECTID = 1) to change it to 0, not something close to zero
# (this is to resolve one of the side effects of raster coastline edges not being conformed to 0)
arcpy.management.CalculateField("Lake_ContoursPolyShellUp", "ContourMin", "Correct(!ContourMin!,!OBJECTID!)", "PYTHON3", """def Correct(contmin,oid):
    if oid == 1:
        return 0
    else:
        return contmin""", "TEXT", "NO_ENFORCE_DOMAINS")

# Add a field (column) for "characteristic_name" to the shell polygon feature class
arcpy.management.AddField("Lake_ContoursPolyShellUp", "characteristic_name", "TEXT")

# Populate "characteristic_name" column with "area_cumulative" for all records (these are area_cumulative values)
arcpy.management.CalculateField("Lake_ContoursPolyShellUp","characteristic_name","'area_cumulative'","PYTHON3")

# Append depth, area, and characteristic_name fields to table using field mapping (note that shortening this line of script was not possible)
arcpy.management.Append("Lake_ContoursPolyShellUp", "Lake_" + lake_name + "_Data_Table", "NO_TEST", 'characteristic_name "characteristic_name" true true false 8000 Text 0 0,First,#,Lake_ContoursPolyShellUp_Cleaned,characteristic_name,-1,-1;result_value "result_value" true true false 8000 Text 0 0,First,#,Lake_ContoursPolyShellUp_Cleaned,Shape_Area,-1,-1;depth_upper "depth_upper" true true false 8000 Text 0 0,First,#,Lake_ContoursPolyShellUp_Cleaned,ContourMin,-1,-1;depth_lower "depth_lower" true true false 8000 Text 0 0,First,#,Lake_ContoursPolyShellUp_Cleaned,ContourMax,-1,-1', '', '')


##  4.2) Tabular - volume

##  4.21) Tabular - volume - volume_cumulative (easier to do cumulative before interval for volume)

# Prep raster and polygon feature class and so will work properly as inputs for zonal statistics tool (work around limitations)

# Raster calculator multiply by 100 to avoid significant figure data loss and for easy re-conversion later
# from arcpy.sa import *
output_raster = Raster("Raster_Zero_Positive") * 100
output_raster.save(intmd_gdb + r"\Raster_Zero_Positive_x100")

# Add a field (column) for "ZoneContourLv100" to the contours poly shell up feature class, which is integer field type (long integer)
arcpy.management.AddField("Lake_ContoursPolyShellUp", "ZoneContourLv100", "LONG")

# Populate "ZoneContourLv100" column with integer (rounded) version of contour min * 100
arcpy.management.CalculateField("Lake_ContoursPolyShellUp", "ZoneContourLv100", "!ContourMin!*100", "PYTHON3")

# Run Zonal Statistics as Table to get mean depths for each zone
arcpy.sa.ZonalStatisticsAsTable("Lake_ContoursPolyShellUp", "ZoneContourLv100", "Raster_Zero_Positive_x100", "Zonal_Stats_Table", "DATA", "MEAN")

# The next several steps are basically just doing math on our zonal stats table outputs, to get the values we want.

# Add a float field (column) for actual mean depths ("MeanActual") to zonal stats table (will calculate in next step)
arcpy.management.AddField("Zonal_Stats_Table", "MeanActual", "FLOAT")

# Populate "MeanActual" column with the actual mean depths for all records (divide by 100, to correct for earlier multiplication)
arcpy.management.CalculateField("Zonal_Stats_Table", "MeanActual", "!MEAN!/100", "PYTHON3")

# We will want fields (columns) for upper and lower depths ("depth_upper", "depth_lower"), which is in the contours poly shell up feature class (as "ContourMin" and "ContourMax")
# Join contours poly shell up with the zonal stats table, to get that column (join on "ZoneContourLv100" which is in both tables)
arcpy.management.JoinField("Zonal_Stats_Table", "ZoneContourLv100", "Lake_ContoursPolyShellUp", "ZoneContourLv100", "ContourMin;ContourMax")

# Add a float field (column) for volume ("volume_cumulative") to zonal stats table (will calculate in next step)
arcpy.management.AddField("Zonal_Stats_Table", "volume_cumulative", "FLOAT")

# Calculate volume...
# The concepts and math are a bit tricky - explained in companion word doc (since long, and easier with diagrams)
arcpy.management.CalculateField("Zonal_Stats_Table", "volume_cumulative", "(!MeanActual! * !AREA!) - (!AREA! * !ContourMin!)", "PYTHON3")

# We need to finish adding the fields we require before appending the data into our running results table
# Add a field (column) for "characteristic_name" to the zonal stats table
arcpy.management.AddField("Zonal_Stats_Table", "characteristic_name", "TEXT")

# Populate "characteristic_name" column with "volume_cumulative" for all records (these are volume_cumulative values, vs. other rows for other chars already in the table)
arcpy.management.CalculateField("Zonal_Stats_Table","characteristic_name","'volume_cumulative'","PYTHON3")

# Append to our running results table the fields: cumulative volume, lower depth, upper depth, and characteristic_name fields (using field mapping)
arcpy.management.Append("Zonal_Stats_Table", "Lake_" + lake_name + "_Data_Table", "NO_TEST", 'characteristic_name "characteristic_name" true true false 8000 Text 0 0,First,#,"Zonal_Stats_Table",characteristic_name,0,255;result_value "result_value" true true false 8000 Text 0 0,First,#,"Zonal_Stats_Table",volume_cumulative,-1,-1;depth_upper "depth_upper" true true false 8000 Text 0 0,First,#,"Zonal_Stats_Table",ContourMin,-1,-1;depth_lower "depth_lower" true true false 8000 Text 0 0,First,#,"Zonal_Stats_Table",ContourMax,-1,-1', '', '')


#  4.22) Tabular - volume - volume_interval

# The concept is to get volume_interval by subtracting the volume_cumulative from the layer below the one in question

# Join to Lake_ContoursPoly the Zonal_Stats_Table (join on ContourMin, all you need is "volume_cumulative")
arcpy.management.JoinField("Lake_ContoursPoly", "ContourMin", "Zonal_Stats_Table", "ContourMin", "volume_cumulative")

# Add a field (column) for "volume_below_slice" to the zonal stats table
arcpy.management.AddField("Zonal_Stats_Table", "volume_below_slice", "FLOAT")

# Populate "volume_below_slice" column with "volume_cumulative" for all records
arcpy.management.CalculateField("Zonal_Stats_Table","volume_below_slice","!volume_cumulative!","PYTHON3")

# Join to Lake_ContoursPoly the Zonal_Stats_Table - purposefully incorrectly, to get offset rows needed for maths
# (join on ContourMin from Zonal_Stats_Table represents ContourMax in Lake_ContoursPoly table, all you need is "volume_below_slice")
arcpy.management.JoinField("Lake_ContoursPoly", "ContourMax", "Zonal_Stats_Table", "ContourMin", "volume_below_slice")

# Delete "volume_below_slice" field (column) from Zonal_Stats_Table (it's a temporary intermediate file anyway, but just in case)
arcpy.management.DeleteField("Zonal_Stats_Table", "volume_below_slice")

# Convert the null to zero for "volume_below_slice"
arcpy.management.CalculateField("Lake_ContoursPoly", "volume_below_slice", "NullToZero(!volume_below_slice!)", "PYTHON3", """def NullToZero(value):
  if value == None:
   return '0'
  else: return value""")

# Add a field (column) for "volume_interval" to the Lake_ContoursPoly attribute table
arcpy.management.AddField("Lake_ContoursPoly", "volume_interval", "FLOAT")

# Populate "volume_interval" column by calculation ("volume_cumulative" minus "volume_below_slice")
arcpy.management.CalculateField("Lake_ContoursPoly", "volume_interval", "!volume_cumulative! - !volume_below_slice!", "PYTHON3")

# Add a field (column) for "characteristic_name2" to the Lake_ContoursPoly attribute table
arcpy.management.AddField("Lake_ContoursPoly", "characteristic_name2", "TEXT")

# Populate "characteristic_name2" column with "volume_interval" for all records
arcpy.management.CalculateField("Lake_ContoursPoly","characteristic_name2","'volume_interval'","PYTHON3")

# Append to our running results table the fields: interval volume, lower depth, upper depth, and characteristic_name fields (using field mapping)
arcpy.management.Append("Lake_ContoursPoly", "Lake_" + lake_name + "_Data_Table", "NO_TEST", 'characteristic_name "characteristic_name" true true false 8000 Text 0 0,First,#,Lake_ContoursPoly,characteristic_name2,0,255;result_value "result_value" true true false 8000 Text 0 0,First,#,Lake_ContoursPoly,volume_interval,-1,-1;depth_upper "depth_upper" true true false 8000 Text 0 0,First,#,Lake_ContoursPoly,ContourMin,-1,-1;depth_lower "depth_lower" true true false 8000 Text 0 0,First,#,Lake_ContoursPoly,ContourMax,-1,-1', '', '')


##  4.3) Tabular - summary stats

# Four stats: retrieve or calculate the numbers from all over...

# area_surface = Shape_Area from Lake_ContoursPolyShellUp when ContourMin = 0
SC = arcpy.SearchCursor("Lake_ContoursPolyShellUp")
for row in SC:
    if row.getValue("ContourMin") == 0:
        area_surface = row.getValue("Shape_Area")
del row, SC
# optional - check if the value it fetched makes sense
area_surface = str(area_surface)
print("area_surface (m2) = " + area_surface)

# volume_total = volume_cumulative from Zonal_Stats_Table when ContourMin = 0
SC = arcpy.SearchCursor("Zonal_Stats_Table")
for row in SC:
    if row.getValue("ContourMin") == 0:
        volume_total = row.getValue("volume_cumulative")
del row, SC
# optional - check if the value it fetched makes sense
volume_total = str(volume_total)
print("volume_total (m3) = " + volume_total)

# depth_max
depth_max = max_depth # is already a variable I calculated/assigned from earlier (using "GetRasterProperties")
# optional - check value makes sense
depth_max = str(depth_max)
print("depth_max (m) = " + depth_max)

# depth_mean
depth_mean = arcpy.management.GetRasterProperties(intmd_gdb + r"\Raster_Zero_Positive", "MEAN")
# optional - check value makes sense
depth_mean = str(depth_mean)
print("depth_mean (m) = " + depth_mean)

# perimeter_surface = Shape_Length from Lake_Outline when OBJECTID = 1
SC = arcpy.SearchCursor("Lake_Outline")
for row in SC:
    if row.getValue("OBJECTID") == 1:
        perimeter_surface = row.getValue("Shape_Length")
del row, SC
# optional - check if the value it fetched makes sense
perimeter_surface = str(perimeter_surface)
print("perimeter_surface (m) = " + perimeter_surface)


# Copy summary stats template table csv into intmd.gdb as grid table to work on
arcpy.conversion.TableToTable(bathymetry_summary_template_table, intmd_gdb, "summary_stats_table")

# Calculate value field with an if then expression, depending on characteristic_name, using values established above
arcpy.management.CalculateField(intmd_gdb + r"\summary_stats_table", "result_value", "ApplySummaryStats(!result_value!,!characteristic_name!)", "PYTHON3", """def ApplySummaryStats(value,char):
    if char == 'area_surface':
        return area_surface
    elif char == 'volume_total':
        return volume_total
    elif char == 'depth_max':
        return depth_max
    elif char == 'depth_mean':
        return depth_mean
    elif char == 'perimeter_surface':
        return perimeter_surface
    else:
        return 'char not accounted for'""", "TEXT", "NO_ENFORCE_DOMAINS")

# Calculate value fields for depth_upper (essentially, replace "max_depth" with actual max_depth value, "zero" with 0, else keep whatever is there.
# Note this uses the "max_depth" variable (a number), not be be confused with the "depth_max" variable (the string version).
arcpy.management.CalculateField(intmd_gdb + r"\summary_stats_table", "depth_upper", "ApplyDepths(!depth_upper!)", "PYTHON3", """def ApplyDepths(depth_upper):
    if depth_upper == 'max_depth':
        return max_depth
    elif depth_upper == 'zero':
        return 0
    else:
        return depth_upper""", "TEXT", "NO_ENFORCE_DOMAINS")

# Calculate value fields for depth_lower (essentially, replace "max_depth" with actual max_depth value, "zero" with 0, else keep whatever is there.
# Note this uses the "max_depth" variable (a number), not be be confused with the "depth_max" variable (the string version).
arcpy.management.CalculateField(intmd_gdb + r"\summary_stats_table", "depth_lower", "ApplyDepths(!depth_lower!)", "PYTHON3", """def ApplyDepths(depth_lower):
    if depth_lower == 'max_depth':
        return max_depth
    elif depth_lower == 'zero':
        return 0
    else:
        return depth_lower""", "TEXT", "NO_ENFORCE_DOMAINS")

# Append to our running results table the fields: characteristic_name, result_value, lower depth, and upper depth fields (use field mapping)
arcpy.management.Append(intmd_gdb + r"\summary_stats_table", "Lake_" + lake_name + "_Data_Table", "NO_TEST", 'characteristic_name "characteristic_name" true true false 8000 Text 0 0,First,#,"summary_stats_table",characteristic_name,0,8000;result_value "result_value" true true false 8000 Text 0 0,First,#,"summary_stats_table",result_value,0,8000;depth_upper "depth_upper" true true false 8000 Text 0 0,First,#,"summary_stats_table",depth_upper,0,8000;depth_lower "depth_lower" true true false 8000 Text 0 0,First,#,"summary_stats_table",depth_lower,0,8000', '', '')


##  4.4) Tabular - final steps - write metadata and copy to final locations outside of intmd.gdb

# Certain metadata parameters go into the data table (every row).
# Other parameters (most) go into the metadata table.
# You should have already manually defined all these variables in the Part 1 variables section of this script.
# Many of these variables are different for each lake.

# Populate the fields with established variables using field calculator script... (a simple function for each column)

# First we do this for the data table (later, the metadata table)
# We are working directly in the "Lake_" + lake_name + "_Data_Table" gdb grid table

# dataset_code
arcpy.management.CalculateField("Lake_" + lake_name + "_Data_Table","dataset_code","WriteMetadata(!dataset_code!)", "PYTHON3",
"""def WriteMetadata(variable):
    return dataset_code""")
# monitoring_location_name
arcpy.management.CalculateField("Lake_" + lake_name + "_Data_Table","monitoring_location_name","WriteMetadata(!monitoring_location_name!)", "PYTHON3",
"""def WriteMetadata(variable):
    return monitoring_location_name""")
# activity_start_date
arcpy.management.CalculateField("Lake_" + lake_name + "_Data_Table","activity_start_date","WriteMetadata(!activity_start_date!)", "PYTHON3",
"""def WriteMetadata(variable):
    return activity_start_date""")
# update_date
arcpy.management.CalculateField("Lake_" + lake_name + "_Data_Table","update_date","WriteMetadata(!update_date!)", "PYTHON3",
"""def WriteMetadata(variable):
    return update_date""")

# Secondly for the metadata table

# Copy metadata template table csv into intmd.gdb as grid table to work on
arcpy.conversion.TableToTable(bathymetry_meta_template_table, intmd_gdb, "Lake_" + lake_name + "_Metadata_Table")

# dataset_code
arcpy.management.CalculateField("Lake_" + lake_name + "_Metadata_Table","dataset_code","WriteMetadata(!dataset_code!)", "PYTHON3",
"""def WriteMetadata(variable):
    return dataset_code""")
# monitoring_location_name
arcpy.management.CalculateField("Lake_" + lake_name + "_Metadata_Table","monitoring_location_name","WriteMetadata(!monitoring_location_name!)", "PYTHON3",
"""def WriteMetadata(variable):
    return monitoring_location_name""")
# activity_start_date
arcpy.management.CalculateField("Lake_" + lake_name + "_Metadata_Table","activity_start_date","WriteMetadata(!activity_start_date!)", "PYTHON3",
"""def WriteMetadata(variable):
    return activity_start_date""")
# activity_end_date
arcpy.management.CalculateField("Lake_" + lake_name + "_Metadata_Table","activity_end_date","WriteMetadata(!activity_end_date!)", "PYTHON3",
"""def WriteMetadata(variable):
    return activity_end_date""")
# method_sample_code
arcpy.management.CalculateField("Lake_" + lake_name + "_Metadata_Table","method_sample_code","WriteMetadata(!method_sample_code!)", "PYTHON3",
"""def WriteMetadata(variable):
    return method_sample_code""")
# method_process_code
arcpy.management.CalculateField("Lake_" + lake_name + "_Metadata_Table","method_process_code","WriteMetadata(!method_process_code!)", "PYTHON3",
"""def WriteMetadata(variable):
    return method_process_code""")
# gear_type_code
arcpy.management.CalculateField("Lake_" + lake_name + "_Metadata_Table","gear_type_code","WriteMetadata(!gear_type_code!)", "PYTHON3",
"""def WriteMetadata(variable):
    return gear_type_code""")
# collected_by
arcpy.management.CalculateField("Lake_" + lake_name + "_Metadata_Table","collected_by","WriteMetadata(!collected_by!)", "PYTHON3",
"""def WriteMetadata(variable):
    return collected_by""")
# entered_by
arcpy.management.CalculateField("Lake_" + lake_name + "_Metadata_Table","entered_by","WriteMetadata(!entered_by!)", "PYTHON3",
"""def WriteMetadata(variable):
    return entered_by""")
# processed_by
arcpy.management.CalculateField("Lake_" + lake_name + "_Metadata_Table","processed_by","WriteMetadata(!processed_by!)", "PYTHON3",
"""def WriteMetadata(variable):
    return processed_by""")
# validated_by
arcpy.management.CalculateField("Lake_" + lake_name + "_Metadata_Table","validated_by","WriteMetadata(!validated_by!)", "PYTHON3",
"""def WriteMetadata(variable):
    return validated_by""")
# approved_by
arcpy.management.CalculateField("Lake_" + lake_name + "_Metadata_Table","approved_by","WriteMetadata(!approved_by!)", "PYTHON3",
"""def WriteMetadata(variable):
    return approved_by""")
# lake_level_m
arcpy.management.CalculateField("Lake_" + lake_name + "_Metadata_Table","lake_level_m","WriteMetadata(!lake_level_m!)", "PYTHON3",
"""def WriteMetadata(variable):
    return lake_level_m""")
# benchmark_id
arcpy.management.CalculateField("Lake_" + lake_name + "_Metadata_Table","benchmark_id","WriteMetadata(!benchmark_id!)", "PYTHON3",
"""def WriteMetadata(variable):
    return benchmark_id""")
# lake_level_m_asl
arcpy.management.CalculateField("Lake_" + lake_name + "_Metadata_Table","lake_level_m_asl","WriteMetadata(!lake_level_m_asl!)", "PYTHON3",
"""def WriteMetadata(variable):
    return lake_level_m_asl""")
# lake_level_asl_method
arcpy.management.CalculateField("Lake_" + lake_name + "_Metadata_Table","lake_level_asl_method","WriteMetadata(!lake_level_asl_method!)", "PYTHON3",
"""def WriteMetadata(variable):
    return lake_level_asl_method""")
# general_comment
arcpy.management.CalculateField("Lake_" + lake_name + "_Metadata_Table","general_comment","WriteMetadata(!general_comment!)", "PYTHON3",
"""def WriteMetadata(variable):
    return general_comment""")
# update_date
arcpy.management.CalculateField("Lake_" + lake_name + "_Metadata_Table","update_date","WriteMetadata(!update_date!)", "PYTHON3",
"""def WriteMetadata(variable):
    return update_date""")

# The two tables are now complete "final outputs", so the next lines are to copy them to the right places.

# Write data gdb table (grid) to csv export in intermediate CSVs folder
arcpy.conversion.TableToTable("Lake_" + lake_name + "_Data_Table",intmd_csvs,"Lake_" + lake_name + "_Data_Table.csv")

# Write metadata gdb table (grid) to csv export in intermediate CSVs folder
arcpy.conversion.TableToTable("Lake_" + lake_name + "_Metadata_Table",intmd_csvs,"Lake_" + lake_name + "_Metadata_Table.csv")

# Manual check reminder - go and open those CSVs to confirm they have values written in them and they makes sense.
# Run these lines to print out possibly useful summary text that will show in the Python window
print("\n~*~*~*~ MANUAL CHECK REMINDER ~*~*~*~\
\n\nOpen the two CSVs to confirm that they have\
\nvalues written in them and they make sense.\
\n\nCSVs folder location: " + intmd_csvs + \
"\nData csv: Lake_"  + lake_name + "_Data_Table\
\nMetadata csv: Lake_" + lake_name + "_Metadata_Table\n")

# Once you've checked and confirmed the data are good, you can run the next lines, which copy the tables into the folder for postgres database uploading (for FME Workbench Inputs)

# Write data gdb table (grid) to csv export in final CSVs folder
arcpy.conversion.TableToTable("Lake_" + lake_name + "_Data_Table",final_csvs_folder,"Lake_" + lake_name + "_Data_Table.csv")

# Write metadata gdb table (grid) to csv export in CSVs folder
arcpy.conversion.TableToTable("Lake_" + lake_name + "_Metadata_Table",final_csvs_folder,"Lake_" + lake_name + "_Metadata_Table.csv")

######################################################################################################

###   5) Maps
# This section is all done manually - there is no script.
# This is only included here so the parts of the process are outlined in both the script and the how-to document.

######################################################################################################

