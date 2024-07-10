import os
import ifcopenshell
from dataclasses import dataclass
from enum import Enum
import uuid
from archicad2elca_comps.localization import Lang
from archicad2elca_comps.config import ifc_types
from archicad2elca_comps.config import reference_units

AC_lang_vars = Lang()


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
    din276Code: int
    refUnit: str
    comp_name: str
    layers: list
    comp_description: str | None = "Dieser Schichtaufbau wurde exportiert mit ArchiCAD2eLCA_comps: https://github.com/johnzoki/ArchiCAD2eLCA_comps"


@dataclass
class IfcLayer:
    """Class for keeping track of Layerinformation of a Element"""

    layer_material: str
    layer_size: float
    layer_position: int
    layer_uuid: str
    layer_lifeTime: int
    layer_lifeTimeDelay: int | None = 0
    calcLca: bool | None = True
    isExtant: bool | None = False


def get_uuid() -> str:
    """
    Returns a random uuid
    """
    return str(uuid.uuid4())


def property_finder(ifc_element, property_set, property_name) -> str:
    """
    Returns attribute values from RelatingPropertyDefinitions
    """
    for s in ifc_element.IsDefinedBy:
        if (
            hasattr(s, "RelatingPropertyDefinition")
            and s.RelatingPropertyDefinition.Name == property_set
        ):
            if hasattr(s.RelatingPropertyDefinition, "HasProperties"):
                for v in s.RelatingPropertyDefinition.HasProperties:
                    if v.Name == property_name:
                        return v.NominalValue.wrappedValue
            elif hasattr(s.RelatingPropertyDefinition, "Quantities"):
                for v in s.RelatingPropertyDefinition.Quantities:
                    if v.Name == property_name:
                        for attr, value in vars(v).items():
                            if attr.endswith("Value"):
                                return value
    return None


def get_din276Code(ifc_type, ifc_element):
    """
    Returns din276Codes of IfcElements by checking Pset information.

    Parameters:
        ifc_element:
            IfcElement in IFC-Model.
        ifc_type:
            IfcType of IfcElement.
    """
    if ifc_type == "IfcWall":
        return get_din276Code_wall(ifc_element)
    if ifc_type == "IfcSlab":
        return get_din276Code_slab(ifc_element)
    else:
        return 000


def get_din276Code_wall(ifc_element):
    """
    Returns din276Codes of IfcWall by checking Pset information.

    Parameters:
        ifc_element:
            IfcElement in IFC-Model.

    Compare:
        filename: KG.py;
        author: Jil Schneider
        project: Masterthesis Architektur
        title: Building as Material Resource - Life Cycle Assessment with OpenBIM
        date: 2021/02/19
    """
    reference = property_finder(ifc_element, "Pset_WallCommon", "Reference")
    isExternal = property_finder(ifc_element, "Pset_WallCommon", "IsExternal")
    isLoadBearing = property_finder(ifc_element, "Pset_WallCommon", "LoadBearing")
    isExtendToStructure = property_finder(
        ifc_element, "Pset_WallCommon", "ExtendToStructure"
    )
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
                elif (
                    not isLoadBearing
                    and not isExternal
                    and (isExtendToStructure and referenceForExternalWall in reference)
                ):
                    return 336
                    # Außenwandbekleidung, innen
                elif isLoadBearing and not isExternal and not isExtendToStructure:
                    return 341
                    # Tragende Innenwände
                elif not isLoadBearing and not isExternal and not isExtendToStructure:
                    return 342
                    # Nichttragende Innenwände
                elif (
                    not isLoadBearing
                    and not isExternal
                    and (isExtendToStructure and referenceForInternalWall in reference)
                ):
                    return 345
                    # Innenwandbekleidung
                elif not isLoadBearing and not isExternal and isExtendToStructure:
                    return 000
            else:
                raise IFCExportError("ExtantToStucture is missing in Pset_WallCommon")
        elif isExternal:
            return 330
            # Außenwände/Vertikale Baukonstruktionen, außen
        elif not isExternal:
            return 340
            # Innenwände/Vertikale Baukonstruktionen, innen
        else:
            raise IFCExportError("LoadBearing is missing in Pset_WallCommon")
    else:
        return 300
        # Bauwerk Baukonstruktionen


def get_din276Code_slab(ifc_element):
    """
    Returns din276Codes of IfcSlab by checking Pset information.

    Parameters:
        ifc_element:
            IfcElement in IFC-Model.

    Compare:
        filename: KG.py;
        author: Jil Schneider
        project: Masterthesis Architektur
        title: Building as Material Resource - Life Cycle Assessment with OpenBIM
        date: 2021/02/19
    """
    isExternal = property_finder(ifc_element, "Pset_SlabCommon", "IsExternal")
    isLoadBearing = property_finder(ifc_element, "Pset_SlabCommon", "LoadBearing")
    if hasattr(ifc_element, "PredefinedType"):
        enum = ifc_element.PredefinedType
    else:
        enum = None
    if enum == None or enum == "NOTDEFINED":
        enum = "STANDARD"

    if enum == "BASESLAB":
        return 322
        # Flachgründungen und Bodenplatten
    elif enum == "LANDING":
        return 351
        # Dachkonstruktionen
    elif isLoadBearing is not None:
        if enum == "ROOF" and isLoadBearing:
            return 361
            # Dachkonstruktionen
        elif enum == "ROOF" and not isLoadBearing:
            return 363
            # Dachbeläge
        elif isExternal is not None:
            if enum == "FLOOR" or (isLoadBearing and not isExternal):
                return 351
                # Deckenkonstruktionen
    else:
        return 300
        # Bauwerk Baukonstruktionen


def get_material_info(m, ifc_material):
    """
    Gets specific values in "AC_Pset_MaterialCustom" and name of a given material.

    Parameters:
        m:
            IFC-Model
        ifc_material:
            Given IfcMaterial of IfcElement or IfcElementPart
    """
    layer_uuid = None
    layer_lifeTime = None
    layer_lifeTimeDelay = None
    calcLca = None
    isExtant = None
    material_inverse = m.get_inverse(ifc_material)
    for i in material_inverse:
        if i.Name == "AC_Pset_MaterialCustom":
            for prop in i.Properties:
                if prop.is_a("IfcPropertySingleValue"):
                    if prop.Name == "OBD_uuid":
                        layer_uuid = prop.NominalValue[0]
                    elif prop.Name == "OBD_lifeTime":
                        layer_lifeTime = prop.NominalValue[0]
                    elif prop.Name == "OBD_lifeTimeDelay":
                        layer_lifeTimeDelay = prop.NominalValue[0]
                    elif prop.Name == "OBD_calcLca":
                        calcLca = prop.NominalValue[0]
                    elif prop.Name == "OBD_isExtant":
                        isExtant = prop.NominalValue[0]
            break

    ifc_material_name = ifc_material.Name
    return (
        ifc_material_name,
        layer_uuid,
        layer_lifeTime,
        layer_lifeTimeDelay,
        calcLca,
        isExtant,
    )


def multi_layer(m, ifc_element_parts):
    """
    Creates Objects from IfcLayer classes from Elements with multiple Layers.

    Parameters:
        m:
            IFC-Model
        ifc_rel_aggregates:
            Set of IfcElementParts of one IfcElement
    """
    comp_layer_list = []
    for layer_number, ifc_element_part in enumerate(ifc_element_parts, 1):
        ifc_material_name = None
        ifc_material = ifcopenshell.util.element.get_material(ifc_element_part)
        if ifc_material is not None and ifc_material.is_a("IfcMaterial"):
            (
                ifc_material_name,
                layer_uuid,
                layer_lifeTime,
                layer_lifeTimeDelay,
                calcLca,
                isExtant,
            ) = get_material_info(m, ifc_material)
        if ifc_material_name is None:
            raise FaultyElementAttributeError("Material_name is not defined")

        width = None
        quant = ifcopenshell.util.element.get_pset(
            ifc_element_part, "Component Quantities"
        )
        if quant:
            width = quant.get(AC_lang_vars.AC_quantity_thickness_name)
        if width is not None:
            l = IfcLayer(
                layer_material=ifc_material_name,
                layer_size=width,
                layer_position=layer_number,
                layer_uuid=layer_uuid,
                layer_lifeTime=int(layer_lifeTime),
                layer_lifeTimeDelay=(
                    int(layer_lifeTimeDelay)
                    if layer_lifeTimeDelay is not None
                    else IfcLayer.layer_lifeTimeDelay
                ),
                calcLca=calcLca if calcLca is not None else IfcLayer.calcLca,
                isExtant=isExtant if isExtant is not None else IfcLayer.isExtant,
            )
        comp_layer_list.append(l)
    if comp_layer_list:
        return comp_layer_list
    else:
        raise FaultyElementAttributeError("Empty Layer List")


def ifc_element_single_layer(m, ifc_type, ifc_element):
    """
    Creates one Object from IfcLayer class from Element with just one Layers.

    Parameters:
        m:
            IFC-Model
        ifc_element:
            Given IfcElement
    """
    pset_BaseQuantities_name = "Qto_" + ifc_type[3:] + "BaseQuantities"
    ifc_element_psets = ifcopenshell.util.element.get_psets(ifc_element)
    pset_Qto_WallBaseQuantities = ifc_element_psets.get(pset_BaseQuantities_name)
    width = None
    if pset_Qto_WallBaseQuantities:
        width = pset_Qto_WallBaseQuantities.get("Width")
    if width is None:
        raise FaultyElementAttributeError("Width is not defined")

    ifc_material_name = None
    ifc_material = ifcopenshell.util.element.get_material(ifc_element)
    if ifc_material is not None and ifc_material.is_a("IfcMaterial"):
        (
            ifc_material_name,
            layer_uuid,
            layer_lifeTime,
            layer_lifeTimeDelay,
            calcLca,
            isExtant,
        ) = get_material_info(m, ifc_material)

    if ifc_material_name is None:
        raise FaultyElementAttributeError("Material_name is not defined")

    comp_layer_list = [
        IfcLayer(
            layer_material=ifc_material_name,
            layer_size=width,
            layer_position=1,
            layer_uuid=layer_uuid,
            layer_lifeTime=int(layer_lifeTime),
            layer_lifeTimeDelay=(
                int(layer_lifeTimeDelay)
                if layer_lifeTimeDelay is not None
                else IfcLayer.layer_lifeTimeDelay
            ),
            calcLca=calcLca if calcLca is not None else IfcLayer.calcLca,
            isExtant=isExtant if isExtant is not None else IfcLayer.isExtant,
        )
    ]
    comp_name = ifc_material_name + " " + str(width * 100) + "cm"
    return comp_name, comp_layer_list


def get_comp_type(m, ifc_type, ifc_element):
    """
    Decides if given IfcElement is a multilayered Element or singlelayered.

    Parameters:
        m:
            IFC-Model
        ifc_element:
            Given IfcElement
    """
    # check if ifc_element has IfcAggregates
    if len(ifc_element.IsDecomposedBy) != 0:
        AC_pset = ifcopenshell.util.element.get_pset(ifc_element, "ArchiCADProperties")
        comp_name = None
        if AC_pset:
            if AC_pset.get(AC_lang_vars.AC_multilayer_pset_name):
                comp_name = AC_pset.get(AC_lang_vars.AC_multilayer_pset_name)
        else:
            raise FaultyElementAttributeError(
                f"No Pset named {AC_lang_vars.AC_multilayer_pset_name} in ArchiCADProperties"
            )
        if comp_name:
            # define ifc_element_parts in multilayered ifc_element
            ifc_element_parts = ifc_element.IsDecomposedBy[0].RelatedObjects
            comp_layer_list = multi_layer(m, ifc_element_parts)
            return comp_name, comp_layer_list, CompType.MULTILAYER
        else:
            raise FaultyElementAttributeError("No Compname in ArchiCADProperties")

        element_ref = m.get_inverse(ifc_element)
        ifc_rel_aggregates = [
            rel for rel in element_ref if rel.is_a("IfcRelAggregates")
        ]

    else:
        return (
            *ifc_element_single_layer(m, ifc_type, ifc_element),
            CompType.SINGLELAYER,
        )


def get_refUnit(ifc_type):
    """
    Gets refUnit by IfcType that was defined in config.py.

    Parameters:
        ifc_type:
            IfcType of IfcElement
    """
    refUnit = reference_units[ifc_type]
    return refUnit


def ifc_extractor(ifcfile_path):
    """
    Creates Objects from IfcElement class from Elements and collects all neccessary data to do so.
    Returns these Objects to '__innit.py__' to later use them in the xml_builder.

    Parameters:
        ifcfile_path:
            Given path to IFC4-file, that is to be used for extracting comps
    """
    m = ifcopenshell.open(ifcfile_path)
    element_dict = {}
    for ifc_type in ifc_types:
        ifc_elements = m.by_type(ifc_type)
        for ifc_element in ifc_elements:
            try:
                comp_name, layer_list, comp_type = get_comp_type(
                    m, ifc_type, ifc_element
                )
            except FaultyElementAttributeError:
                continue
            uuid = get_uuid()
            din276Code = get_din276Code(ifc_type, ifc_element)
            refUnit = get_refUnit(ifc_type)

            element_dict.setdefault(
                (comp_name, comp_type),
                IfcElement(
                    uuid=uuid,
                    din276Code=din276Code,
                    refUnit=refUnit,
                    comp_name=comp_name,
                    layers=layer_list,
                ),
            )
        for element in list(element_dict.values()):
            print(element)

    print("\nDONE! Ifc_extractor has returned all Elements to '__init__'!\n")

    return element_dict.values()
