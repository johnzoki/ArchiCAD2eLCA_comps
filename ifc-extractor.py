import os
import ifcopenshell

def get_ifc_materials_and_thickness(ifc_element):
	material_thickness_list = []
	ifc_material = ifcopenshell.util.element.get_material(ifc_element)
	#ifc_layer = ifcopenshell.util.element.get_layers(ifc_element)
	#print(ifc_material)
	#print(ifc_layer)
	if ifc_material:
		if ifc_material.is_a('IfcMaterial'):
			#print(ifc_material.get_info2())
			# If the material is an IfcMaterial entity, append its name and thickness (if available)
			#material_thickness_list.append((ifc_material.Name, None))
			#material_thickness_list.append((ifc_material.Name, ifc_material.))
			pass
		elif ifc_material.is_a('IfcMaterialLayerSetUsage'):
			# If the material is a layer set usage, loop over the layers and append their names and thicknesses
			for layer in ifc_material.ForLayerSet.MaterialLayers:
				pass
				#print(layer)
				#material_thickness_list.append((layer.Material.Name, layer.LayerThickness))
		else: 
			# If the material is not an IfcMaterial or a layer set usage, just append its type and None for thickness
			material_thickness_list.append((type(ifc_material.__name__), None))
	else:
		#If no material is found, append None for both material and thickness
		material_thickness_list.append((None, "penis"))
	return material_thickness_list


m = ifcopenshell.open("ifc_import/TestIFC.ifc")

walls_data = []
walls = m.by_type("IfcWall")
for wall in walls:
	materials_and_thickness = get_ifc_materials_and_thickness(wall)
	wall_tag = wall.get_info()['Name']
	wall_data = {wall_tag: materials_and_thickness}
	walls_data.append(wall_data)
	print("penis")
	print(wall.get_info_2())
	#print(wall_data)