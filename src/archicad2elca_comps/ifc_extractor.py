import os
import ifcopenshell

def get_ifc_materials_and_thickness(ifc_element, ifc_element_width):
	material_thickness_list = []
	ifc_material = ifcopenshell.util.element.get_material(ifc_element)

	if ifc_material:
		if ifc_material.is_a('IfcMaterial'):
			# If the material is an IfcMaterial entity, append its name and thickness (if available)
			material_thickness_list.append((ifc_material.Name, ifc_element_width))
		elif ifc_material.is_a('IfcMaterialLayerSetUsage'):
			# If the material is a layer set usage, loop over the layers and append their names and thicknesses
			for layer in ifc_material.ForLayerSet.MaterialLayers:
				pass
				#material_thickness_list.append((layer.Material.Name, layer.LayerThickness))
		else: 
			# If the material is not an IfcMaterial or a layer set usage, just append its type and None for thickness
			material_thickness_list.append((type(ifc_material.__name__), ifc_element_width))
	else:
		#If no material is found, append None for both material and thickness
		material_thickness_list.append((None, ifc_element_width))
	return material_thickness_list

def multi_layer(ifc_rel_aggregates):
	print("hi")
	
def single_layer():
	print("hi")

def get_name_and_width(m, ifc_element):
	print("Wandbezeichnung:")
	print(ifc_element)
	print('')
	element_ref = m.get_inverse(ifc_element)
	ifc_rel_aggregates = [rel for rel in element_ref if rel.is_a("IfcRelAggregates")]
	if ifc_rel_aggregates:
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
						if l[0] == 'Schichtdicke':
							for attribute in l:
								if type(attribute) == float:
									width = attribute
									print(f"Width of Element_Part: {width}")
			print('')
	else:
		print("No IfcRelAggregates found for Wall")

def run():
	m = ifcopenshell.open("ifc_import/TestIFC.ifc")
	walls = m.by_type("IfcWall")
	for wall in walls:
		get_name_and_width(m, wall)
	
	

"""
	walls_data = []
	walls = m.by_type("IfcWall")

	multi_layer(wall[3])
	print('')
	print('Wall:')
	print(walls[3])
"""
"""
	for wall in walls:
		w_pset = ifcopenshell.util.element.get_psets(wall)
		if w_pset.get("Qto_WallBaseQuantities"):
			if bool(w_pset.get("Qto_WallBaseQuantities").get("Width")):
				width = w_pset.get("Qto_WallBaseQuantities").get("Width")
		materials_and_thickness = get_ifc_materials_and_thickness(wall, width)
		wall_tag = wall.get_info()['Name']
		wall_data = {wall_tag: materials_and_thickness}
		walls_data.append(wall_data)
		w_pset = ifcopenshell.util.element.get_psets(wall)

		w_pset = ifcopenshell.util.element.get_psets(wall)
		print('')
		#print(wall_data)
		i = m.get_inverse(wall)
		d = wall.IsDefinedBy[1]
		q = d[5]
		u = q[4]
		#print(i)
		#multi_layer(wall
"""