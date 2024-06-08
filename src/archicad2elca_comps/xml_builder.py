import os
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from archicad2elca_comps import element_import
from importlib.resources import files


@dataclass
class ElcaElement:
    """Class for keeping track of SubElement Values of ElementTree"""

    uuid: str
    din276Code: int
    refUnit: str
    name: str
    description: str
    elca_eol: str
    elca_recycling: str
    elca_seperation: str
    elca_rW: str
    elca_uValue: float
    quantity: int | float | None = 1


@dataclass
class ElcaComponent:
    """Class for keeping track of Component Values of Components Tree"""

    isLayer: bool
    processConfigUuid: str
    processConfigName: str
    layerPosition: int
    layerSize: float
    lifeTime: float | int
    lifeTimeDelay: float | int | None = 0
    calcLca: bool | None = True
    isExtant: bool | None = False
    layerAreaRatio: float | None = 1.0
    layerLength: float | None = 1.0
    layerWidth: float | None = 1.0


def save_comp(element_root, import_element):
    components_root = element_root[1]
    for layer_number, layer in enumerate(import_element[6], 1):
        ET.SubElement(components_root, "component")

        c = ElcaComponent(
            isLayer=str(layer[0]).lower(),
            processConfigUuid=str(layer[1]),
            processConfigName=str(layer[2]),
            lifeTime=str(layer[3]),
            lifeTimeDelay=str(layer[4]),
            calcLca=str(layer[5]).lower(),
            isExtant=str(layer[6]).lower(),
            layerPosition=str(layer_number),
            layerSize=str(layer[8]),
            layerAreaRatio=str(layer[9]),
            layerLength=str(layer[10]),
            layerWidth=str(layer[11]),
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


def save_Elements(exportfolder_path, *Elements):
    for element_number, import_element in enumerate(Elements):
        xml_template = ET.parse(
            files("archicad2elca_comps.resources").joinpath("elca_template.xml")
        )
        element_root = xml_template.getroot()[0]

        e = ElcaElement(
            uuid=str(import_element[0]),
            din276Code=str(import_element[1]),
            quantity=str(import_element[2]),
            refUnit=str(import_element[3]),
            name=str(import_element[4]),
            description=str(import_element[5]),
            elca_eol=str(import_element[7]),
            elca_recycling=str(import_element[8]),
            elca_seperation=str(import_element[9]),
            elca_rW=str(import_element[10]),
            elca_uValue=str(import_element[11]),
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
            exportfolder_path + "/" + xml_filename,
            encoding="UTF-8",
            xml_declaration=True,
            short_empty_elements=False,
        )

        print(f"{xml_filename} has been written to {exportfolder_path}")


def xml_builder(exportfolder_path):
    ET.register_namespace("", "https://www.bauteileditor.de")
    save_Elements(
        exportfolder_path,
        element_import.Element1,
        element_import.Element2,
        element_import.Element3,
    )

    print("\nDONE! Xml_builder has exported all Elements as eLCA readable XMLs!")
