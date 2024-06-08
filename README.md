# ArchiCAD2eLCA_comps
## Description
A Python project that extracts ArchiCAD composites out of IFC4-files and exports eLCA composites for easy LCA
Currently it only extracts comps of IFC-Walls that where made of Ökobaudat-Material as XML-Files which can be used for the "imported templates" functionality on bauteileditor.de!
## Important Notes
ExtandToStructure should be in IFC-Properties of Psets_WallCommon before export!
These ArchiCAD Attributes must be given to all materials that wish to be imported to bauteileditor.de:
OBD_uuid
OBD_lifeTime
These are optional:
OBD_lifeTimeDelay
OBD_calcLca
OBD_isExtant