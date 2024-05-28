import os
import ifcopenshell
from dataclasses import dataclass
from enum import Enum
import uuid

class CompType(Enum):
	SINGLELAYER = 1
	MULTILAYER = 2

class FaultyElementAttributeError(Exception):
	def __init__(self, message, errors):
		super().__init__(message)
		self.errors = errors

@dataclass
class IfcElement:
	"""Class for saving Elementsattributes of Elements"""
	guid: str #done
	#din276: str
	#refUnit: str
	comp_name: str #done
	layers: list
	comp_description: str | None=None

@dataclass
class IfcLayer:
	"""Class for keeping track of Layerinformation of a Element"""
	layer_material: str #done
	layer_width: float #done
	layer_position: int #done
def get_guid():
	return str(uuid.uuid4())

def get_din276(ifc_element):
	pass

def multi_layer(ifc_rel_aggregates):
	first_aggregate = ifc_rel_aggregates[0]
	element_comp = first_aggregate[5]
	comp_layer_list = []
	for layer_number, ifc_element_part in enumerate(element_comp, 1):

		if len(ifc_element_part) <= 2:
			raise FaultyElementAttributeError('No Layername')
		ifc_element_part_name = ifc_element_part[2]

		width = None
		for i in ifc_element_part.IsDefinedBy:
			if i.is_a('IfcRelDefinesByProperties') and i.RelatingPropertyDefinition.is_a('IfcElementQuantity'):
				quant = i.RelatingPropertyDefinition.Quantities
				list_ifcQuantityLength = (q for q in quant if q.is_a('IfcQuantityLength'))
				for l in list_ifcQuantityLength:
					if l.get_info()['Name'] == 'Schichtdicke':
						width = l.get_info()['LengthValue']
						break

		if width is not None:
			l = IfcLayer(layer_material=ifc_element_part_name, layer_width=width, layer_position=layer_number)
		comp_layer_list.append(l)
	if comp_layer_list:
		return comp_layer_list
	else:
		raise FaultyElementAttributeError('Empty Layer List')
	
def wall_single_layer(ifc_element):
	w_pset = ifcopenshell.util.element.get_psets(ifc_element)
	pset_Qto_WallBaseQuantities = w_pset.get("Qto_WallBaseQuantities")
	width = None
	if pset_Qto_WallBaseQuantities:
		width = pset_Qto_WallBaseQuantities.get("Width")
	if width is None:
		raise FaultyElementAttributeError('Width is not defined')

	material_name = None
	ifc_material = ifcopenshell.util.element.get_material(ifc_element)
	if ifc_material is not None and ifc_material.is_a('IfcMaterial'):
		material_name = ifc_material.Name
	if material_name is None:
		raise FaultyElementAttributeError('Material_name is not defined')
	comp_layer_list = [IfcLayer(layer_material=material_name, layer_width=width, layer_position=1)]
	comp_name = material_name + " " + str(width * 100) + "cm"
	return comp_name, comp_layer_list

def get_name_and_width(m, ifc_element):
	element_ref = m.get_inverse(ifc_element)
	ifc_rel_aggregates = [rel for rel in element_ref if rel.is_a("IfcRelAggregates")]
	if ifc_rel_aggregates:
		psets = ifcopenshell.util.element.get_psets(ifc_element)
		comp_name = None
		if psets.get('ArchiCADProperties'):
			if psets.get('ArchiCADProperties').get('Mehrschichtige Bauteile'):
				comp_name = psets.get('ArchiCADProperties').get('Mehrschichtige Bauteile')
		if comp_name:
			comp_layer_list = multi_layer(ifc_rel_aggregates)
			return comp_name, comp_layer_list, CompType.MULTILAYER
		else:
			raise FaultyElementAttributeError('No Compname in ArchiCADProperties')	
	else:
		#No IfcRelAggregates found for Wall
		return (*wall_single_layer(ifc_element), CompType.SINGLELAYER)

def run():
	m = ifcopenshell.open("ifc_import/TestIFC.ifc")
	walls = m.by_type("IfcWall")
	element_dict = {}
	for wall in walls:
		try:
			comp_name, layer_list, comp_type = get_name_and_width(m, wall)
		except FaultyElementAttributeError:
			continue
		guid = get_guid()
		element_dict.setdefault((comp_name, comp_type), IfcElement(guid=guid, comp_name=comp_name, layers=layer_list))
	for element in list(element_dict.values()):
		print(element)