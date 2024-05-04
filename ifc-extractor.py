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

m = ifcopenshell.open("ifc_import/TestIFC.ifc")

walls_data = []
walls = m.by_type("IfcWall")
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
	print(wall_data)