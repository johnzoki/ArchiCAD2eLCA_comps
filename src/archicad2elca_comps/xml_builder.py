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
    description: str | None = ""
    elca_eol: str | None = ""
    elca_recycling: str | None = ""
    elca_seperation: str | None = ""
    elca_rW: str | None = ""
    elca_uValue: str | None = ""
    quantity: str | None = "1"


@dataclass
class ElcaComponent:
    """Class for keeping track of Component Values of Components Tree"""

    processConfigUuid: str
    processConfigName: str
    layerPosition: str
    layerSize: str
    lifeTime: str
    lifeTimeDelay: str | None = "0"
    isLayer: str | None = "true"
    calcLca: str | None = "true"
    isExtant: str | None = "false"
    layerAreaRatio: str | None = "1.0"
    layerLength: str | None = "1.0"
    layerWidth: str | None = "1.0"


def save_comp(element_root, element):
    components_root = element_root[1]
    for layer in element.layers:
        ET.SubElement(components_root, "component")

        c = ElcaComponent(
            # isLayer=layer.is_layer,
            processConfigUuid=str(layer.layer_uuid),
            processConfigName=str(layer.layer_material),
            lifeTime=str(layer.layer_lifeTime),
            lifeTimeDelay=str(layer.layer_lifeTimeDelay),
            calcLca=str(layer.calcLca).lower(),
            isExtant=str(layer.isExtant).lower(),
            layerPosition=str(layer.layer_position),
            layerSize=str(layer.layer_size),
            # layerAreaRatio=layer.layer_areaRatio,
            # layerLength=layer.layer_length,
            # layerWidth=layer.layer_width,
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


def xml_builder(exportfolder_path, elements):
    ET.register_namespace("", "https://www.bauteileditor.de")
    for element in elements:
        xml_template = ET.parse(
            files("archicad2elca_comps.resources").joinpath("elca_template.xml")
        )
        element_root = xml_template.getroot()[0]

        e = ElcaElement(
            uuid=str(element.uuid),
            din276Code=str(element.din276Code),
            refUnit=str(element.refUnit),
            name=str(element.comp_name),
            description=str(element.comp_description),
            # elca_eol=element.elca_eol,
            # elca_recycling=element.elca_recycling,
            # elca_seperation=element.elca_seperation,
            # elca_rW=element.elca_rW,
            # elca_uValue=element.elca_uValue,
            # quantity=element.quantity,
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

        save_comp(element_root, element)

        xml_filename = f"eLCA_{e.uuid}.xml"
        xml_template.write(
            exportfolder_path + "/" + xml_filename,
            encoding="UTF-8",
            xml_declaration=True,
            short_empty_elements=False,
        )

        print(f"{xml_filename} has been written to {exportfolder_path}")

    print("\nDONE! Xml_builder has exported all Elements as eLCA readable XMLs!")
