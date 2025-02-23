import argparse
from archicad2elca_comps.localization import Lang
from archicad2elca_comps.ifc_extractor import ifc_extractor
from archicad2elca_comps.xml_builder import xml_builder


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--language",
        "-l",
        type=str,
        required=False,
        dest="lang",
        default="GERMAN",
        help="Set the language",
    )
    parser.add_argument(
        "--ifcfile",
        "-f",
        type=str,
        required=True,
        dest="ifcfile",
        help="Path to your IFC-File",
    )
    parser.add_argument(
        "--exportfolder",
        "-e",
        type=str,
        required=True,
        dest="exportfolder",
        help="Path to your ExportFolder",
    )

    args = parser.parse_args()

    Lang(args.lang)
    ifcfile_path = args.ifcfile
    exportfolder_path = args.exportfolder

    print(
        """ARCHICAD2ELCA_COMPS
        AUTOR: 
            name: Bergmann, John Herbert
            email: john.bergmann@rwth-aachen.de
        DESCRIPTION:
            A Python project that imports archicad composites out of ifc and archicad attributes.xml and exports eLCA composites for easy LCA.
        CLASSIFIERS:
            Programming Language :: Python :: 3
            License :: OSI Approved :: MIT License
            Operating System :: OS Independent
            Development Status :: 1 - Planning
        
        STARTING ...
        """
    )

    extracted_elements = ifc_extractor(ifcfile_path=ifcfile_path)
    xml_builder(exportfolder_path=exportfolder_path, elements=extracted_elements)
