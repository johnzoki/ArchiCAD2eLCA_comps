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

class IFCExportError(Exception):
	def __init__(self, message, errors):
		super().__init__(message)
		self.errors = errors

@dataclass
class IfcElement:
	"""Class for saving Elementsattributes of Elements"""
	uuid: str
	din276: str
	refUnit: str
	comp_name: str
	layers: list
	comp_description: str | None=None

@dataclass
class IfcLayer:
	"""Class for keeping track of Layerinformation of a Element"""
	layer_material: str #done
	layer_width: float #done
	layer_position: int #done
def get_uuid():
	return str(uuid.uuid4())

def property_finder(ifc_element, property_set, property_name):
    for s in ifc_element.IsDefinedBy:
        if hasattr(s, 'RelatingPropertyDefinition'):
            if s.RelatingPropertyDefinition.Name == property_set:
                if hasattr(s.RelatingPropertyDefinition, 'HasProperties'):
                    for v in s.RelatingPropertyDefinition.HasProperties:
                        if v.Name == property_name:
                            return v.NominalValue.wrappedValue
                elif hasattr(s.RelatingPropertyDefinition, 'Quantities'):
                    for v in s.RelatingPropertyDefinition.Quantities:
                        if v.Name == property_name:
                            for attr, value in vars(v).items():
                                if attr.endswith('Value'):
                                    return value
    return None

def get_din276(ifc_element):
	reference = property_finder(ifc_element, "Pset_WallCommon", "Reference")
	isExternal = property_finder(ifc_element, "Pset_WallCommon", "IsExternal")
	isLoadBearing = property_finder(ifc_element, "Pset_WallCommon", "LoadBearing")
	isExtendToStructure = property_finder(ifc_element, "Pset_WallCommon", "ExtendToStructure")
	if isExternal is not None:
		if isLoadBearing is not None:
			if isExtendToStructure is not None:
				if isLoadBearing and isExternal and not isExtendToStructure:
					return 331
					# Tragende Außenwände
				elif not isLoadBearing and isExternal and not isExtendToStructure:
					return 332
					# Nichttragende Außenwände
				elif not isLoadBearing and isExternal and isExtendToStructure:
					return 335
					# Außenwandbekleidung, außen
				elif not isLoadBearing and not isExternal and (isExtendToStructure and referenceForExternalWall in reference):
					return 336
					# Außenwandbekleidung, innen
				elif isLoadBearing and not isExternal and not isExtendToStructure:
					return 341
					# Tragende Innenwände
				elif not isLoadBearing and not isExternal and not isExtendToStructure:
					return 342
					# Nichttragende Innenwände
				elif not isLoadBearing and not isExternal and (isExtendToStructure and referenceForInternalWall in reference):
					return 345
					# Innenwandbekleidung
				elif not isLoadBearing and not isExternal and isExtendToStructure:
					return 000
			else:
				raise IFCExportError('ExtantToStucture is missing in Pset_WallCommon')
		elif isExternal:
			return 330
			# Außenwände/Vertikale Baukonstruktionen, außen
		elif not isExternal:
			return 340
			# Innenwände/Vertikale Baukonstruktionen, innen
		else:
			raise IFCExportError('LoadBearing is missing in Pset_WallCommon')
	else:
		return 300
		# Bauwerk Baukonstruktionen

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
		uuid = get_uuid()
		din276 = get_din276(wall)
		refUnit = 'm'

		element_dict.setdefault((comp_name, comp_type), IfcElement(uuid=uuid, din276=din276, refUnit=refUnit, comp_name=comp_name, layers=layer_list))
	for element in list(element_dict.values()):
		print(element)