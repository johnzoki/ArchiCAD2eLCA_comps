import os
import xml.etree.ElementTree as ET
from dataclasses import dataclass


@dataclass
class ElcaElement:
    """Class for keeping track of SubElement Values of ElementTree"""

    uuid: str
    din276Code: str
    refUnit: str
    name: str
    description: str
    elca_eol: str
    elca_recycling: str
    elca_seperation: str
    elca_rW: str
    elca_uValue: float | None = 1.0
    quantity: int | None = 1


@dataclass
class ElcaComponent:
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
    layerAreaRatio: str
    layerLength: float | None = 1.0
    layerWidth: float | None = 1.0


def save_comp(element_root, import_element):
    components_root = element_root[1]
    for layer_number, layer in enumerate(import_element[6], 1):
        ET.SubElement(components_root, "component")

        c = ElcaComponent(
            str(layer[0]),
            str(layer[1]),
            str(layer[2]),
            str(layer[3]),
            str(layer[4]),
            str(layer[5]),
            str(layer[6]),
            str(layer_number),
            str(layer[8]),
            str(layer[9]),
            str(layer[10]),
            str(layer[11]),
        )

        components_root[-1].set("isLayer", c.isLayer)
        components_root[-1].set("processConfigUuid", c.processConfigUuid)
        components_root[-1].set("processConfigName", c.processConfigName)
        components_root[-1].set("lifeTime", c.lifeTime)
        components_root[-1].set("lifeTimeDelay", c.lifeTimeDelay)
        components_root[-1].set("calcLca", c.calcLca)
        components_root[-1].set("isExtant", c.isExtant)
        components_root[-1].set("layerPosition", c.layerPosition)
        components_root[-1].set("layerSize", c.layerSize)
        components_root[-1].set("layerAreaRatio", c.layerAreaRatio)
        components_root[-1].set("layerLength", c.layerLength)
        components_root[-1].set("layerWidth", c.layerWidth)


def save_Elements(*Elements):
    for element_number, import_element in enumerate(Elements):

        """
        set_elementVar(element)
        """
        xml_template = ET.parse("sample.xml")
        element_root = xml_template.getroot()[0]

        e = ElcaElement(
            str(import_element[0]),
            str(import_element[1]),
            str(import_element[2]),
            str(import_element[3]),
            str(import_element[4]),
            str(import_element[5]),
            str(import_element[7]),
            str(import_element[8]),
            str(import_element[9]),
            str(import_element[10]),
            str(import_element[11]),
        )

        element_root.set("uuid", e.uuid)
        element_root.set("din276Code", e.din276Code)
        element_root.set("quantity", e.quantity)
        element_root.set("refUnit", e.refUnit)

        element_info_root = element_root[0]
        element_info_root[0].text = e.name
        element_info_root[1].text = e.description

        element_attributes_root = element_root[4]
        element_attributes_root[4][1].text = e.elca_uValue

        save_comp(element_root, import_element)

        xml_filename = f"eLCA_{e.uuid}.xml"
        xml_template.write(
            "xml_export/" + xml_filename,
            encoding="UTF-8",
            xml_declaration=True,
            short_empty_elements=False,
        )


import element_import

ET.register_namespace("", "https://www.bauteileditor.de")
save_Elements(element_import.Element1, element_import.Element2, element_import.Element3)
