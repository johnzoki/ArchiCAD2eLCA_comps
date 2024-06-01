import argparse
from archicad2elca_comps.localization import Lang
from archicad2elca_comps.ifc_extractor import ifc_extractor


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

    args = parser.parse_args()

    Lang(args.lang)
    ifcfile_path = args.ifcfile

    extracted_elements = ifc_extractor(ifcfile_path=ifcfile_path)
