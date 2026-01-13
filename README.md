# IISD-ELA Bathymetry Data Processing Repository
Materials for IISD-ELA's bathymetry processing method. Raw coordinates are processed into useful data products (geospatial lake polygon, contour lines, and DEM; tabular data; map PDFs). Requires ArcGIS Pro or related software.
* `PythonScript_BathymetryProcessing_IISD-ELA.py` and `HowToDoc_BathymetryProcessing_IISD-ELA.md` should be used side-by-side to undertake raw data processing. They also explain setup and context.
* `TemplateTables` holds csv files required for the tabular data production part of the script.
* `ExampleData` holds a csv file of raw bathymetry transect coordinates that can be used to test the process.
* `ExampleMetadataSchema` holds two csv files of example schema (i.e. column names) that may be used as part of a bathymetry metadata collection system.
* `SymbologyLayers` holds ArcGIS Pro lyrx files which are used for the map production part of the process. The files hold symbol information (such as line width, colour, label settings, etc.) that can be applied to GIS feature classes on a map in ArcGIS Pro.
* `media` contains images references in the how-to markdown doc, for image display in markdown (the files can be ignored).
* `CITATION.cff` is used to make the repository citable.