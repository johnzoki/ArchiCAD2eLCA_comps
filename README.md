# ArchiCAD2eLCA_comps
## Description
A Python project that extracts ArchiCAD composites out of IFC4-files and exports eLCA composites for easy LCA
Currently it only extracts comps of IFC-Walls or IFC-Slabs that where made of Ökobaudat-Material as XML-Files which can be used for the "imported templates" functionality on bauteileditor.de!
## Important Notes
ExtandToStructure should be in IFC-Properties of Psets_WallCommon before export!
These ArchiCAD Attributes must be given to all materials that wish to be imported to bauteileditor.de:
```
OBD_uuid
OBD_lifeTime
```
These are optional:
```
OBD_lifeTimeDelay
OBD_calcLca
OBD_isExtant
```
## Install via pip
```
python3 -m build
```
```
pip install .
```
## Parsing Arguments
|  args     |   Description                                                         |
|  -------  |   --------------------------------------
|  -h       |   Help-function to see all possible args                              |
|  -l       |   Sets language the ArchiCAD-file was exported from                   |
|  -f PATH  |   PATH is the path to your ifc-file you want to extract comps from    |
|  -e PATH  |   PATH is the path to your export-destination for your eLCA comps     |