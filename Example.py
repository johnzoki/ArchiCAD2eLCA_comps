import os
import xml.etree.ElementTree as ET
from dataclasses import dataclass
ET.register_namespace('','https://www.bauteileditor.de')


@dataclass
class Element:
	"""Class for keeping track of SubElement Values of ElementTree"""
	uuid: str
	din276Code: str
	quantity: str
	refUnit: str
	name: str
	description: str
	elca_eol: str
	elca_recycling: str
	elca_seperation: str
	elca_rW: str
	elca_uValue: str

element_test = Element("a", 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k')

print(Element)
print(element_test)

@dataclass
class Component:
	"""Class for keeping track of Component Values of Components Tree"""
	isLayer: str
	processConfigUuid: str
	processConfigName: str
	lifeTime: str
	lifeTimeDelay: str
	calcLca: str
	isExtant: str
	layerPosition: str
	layerSize: str
	layerLength: str
	layerWidth: str


def save_comp(element_root, import_element):
	components_root = element_root[1]
	for layer_number, layer in enumerate(import_element[6], 1):
		ET.SubElement(components_root, 'component')

		component_isLayer = str(layer[0])
		component_processConfigUuid = str(layer[1])
		component_processConfigName = str(layer[2])
		component_lifeTime = str(layer[3])
		component_lifeTimeDelay = str(layer[4])
		component_calcLca = str(layer[5])
		component_isExtant = str(layer[6])
		component_layerPosotion = str(layer_number)
		component_layerSize = str(layer[8])
		component_layerAreaRatio = str(layer[9])
		component_layerLenght = str(layer[10])
		component_layerWidth = str(layer[11])

		components_root[-1].set('isLayer', component_isLayer)
		components_root[-1].set('processConfigUuid', component_processConfigUuid)
		components_root[-1].set('processConfigName', component_processConfigName)
		components_root[-1].set('lifeTime', component_lifeTime)	
		components_root[-1].set('lifeTimeDelay', component_lifeTimeDelay)
		components_root[-1].set('calcLca', component_calcLca)
		components_root[-1].set('isExtant', component_isExtant)
		components_root[-1].set('layerPosition', component_layerPosotion)
		components_root[-1].set('layerSize', component_layerSize)
		components_root[-1].set('layerAreaRatio', component_layerAreaRatio)
		components_root[-1].set('layerLength', component_layerLenght)
		components_root[-1].set('layerWidth', component_layerWidth)



def save_Elements(*Elements):
	for element_number, import_element in enumerate(Elements):
		
		'''
		set_elementVar(element)
		'''
		xml_template = ET.parse('sample.xml')
		element_root = xml_template.getroot()[0]

		element_uuid = str(import_element[0])
		element_din276Code = str(import_element[1])
		element_quantity = str(import_element[2])
		element_refUnit = str(import_element[3])
		element_name = str(import_element[4])
		element_description = str(import_element[5])
		
		elca_eol = str(import_element[7])
		elca_recycling = str(import_element[8])
		elca_seperation = str(import_element[9])
		elca_rW = str(import_element[10])
		elca_uValue = str(import_element[11])

		element_root.set('uuid', element_uuid)
		element_root.set('din276Code', element_din276Code)
		element_root.set('quantity', element_quantity)
		element_root.set('refUnit', element_refUnit)

		element_info_root = element_root[0]
		element_info_root[0].text = element_name
		element_info_root[1].text = element_description

		element_attributes_root = element_root[4]
		element_attributes_root[4][1].text = elca_uValue

		save_comp(element_root, import_element)

		xml_filename = f"eLCA_{element_uuid}.xml"
		xml_template.write('xml_export/' + xml_filename, encoding = "UTF-8", xml_declaration=True, short_empty_elements=False)

import element_import
save_Elements(element_import.Element1, element_import.Element2, element_import.Element3)