import os
import ifcopenshell

def multi_layer(ifc_rel_aggregates):
	first_aggregate = ifc_rel_aggregates[0]
	element_comp = first_aggregate[5]
	for ifc_element_part in element_comp:
		print(ifc_element_part)
		ifc_element_part_name = ifc_element_part[2]
		print(f"Name of Element_Part: {ifc_element_part_name}")
		#print('ifc_element_part.IsDefinedBy')
		#print(ifc_element_part.IsDefinedBy)
		for i in ifc_element_part.IsDefinedBy:
			if i.is_a('IfcRelDefinesByProperties') and i.RelatingPropertyDefinition.is_a('IfcElementQuantity'):
				quant = i.RelatingPropertyDefinition.Quantities
				list_ifcQuantityLength = (q for q in quant if q.is_a('IfcQuantityLength'))
				for l in list_ifcQuantityLength:
					if l.get_info()['Name'] == 'Schichtdicke':
						width = l.get_info()['LengthValue']
						print(f"Width of Element_Part: {width}")
		print('')
	
def wall_single_layer(ifc_element):
	w_pset = ifcopenshell.util.element.get_psets(ifc_element)
	if w_pset.get("Qto_WallBaseQuantities"):
		if bool(w_pset.get("Qto_WallBaseQuantities").get("Width")):
			width = w_pset.get("Qto_WallBaseQuantities").get("Width")
	ifc_material = ifcopenshell.util.element.get_material(ifc_element)
	if ifc_material:
		if ifc_material.is_a('IfcMaterial'):
			material_name = ifc_material.Name
	print(material_name)
	print(width)

def get_name_and_width(m, ifc_element):
	print("Wandbezeichnung:")
	print(ifc_element)
	print('')
	element_ref = m.get_inverse(ifc_element)
	ifc_rel_aggregates = [rel for rel in element_ref if rel.is_a("IfcRelAggregates")]
	if ifc_rel_aggregates:
		multi_layer(ifc_rel_aggregates)
	else:
		print("No IfcRelAggregates found for Wall")
		wall_single_layer(ifc_element)

def run():
	m = ifcopenshell.open("ifc_import/TestIFC.ifc")
	walls = m.by_type("IfcWall")
	for wall in walls:
		get_name_and_width(m, wall)