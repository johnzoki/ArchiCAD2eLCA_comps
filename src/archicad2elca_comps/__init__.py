import argparse
from archicad2elca_comps.localization import Loc
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

	args = parser.parse_args()

	Loc(args.lang)
	
	extracted_elements = ifc_extractor()
	