# IISD-ELA Bathymetry Data Processing Repository
Materials for a bathymetry processing method that takes in raw coordinate data and puts out useful data products (geospatial lake polygon, contour lines, and DEM; tabular data; map PDFs). Requires ArcGIS Pro or related software.
* The _python script_ and _how-to doc_ should be used side-by-side to undertake raw data processing. They also explain setup and context.
* The _template tables_ folder holds csv files required for the tabular data production part of the script.
* The _example data_ folder holds a csv file of raw bathymetry transect coordinates that can be used to test the process.
* The _example metadata schema_ folder holds two csv files of example schema (i.e. column names) that may be used as part of a bathymetry metadata collection system.
* The _symbology layers_ folder holds ArcGIS Pro lyrx files which are used for the map production part of the process. The files hold symbol information (such as line width, colour, label settings, etc.) that can be applied to GIS feature classes on a map in ArcGIS Pro.