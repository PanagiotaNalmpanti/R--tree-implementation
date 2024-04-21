import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
import sys
import math

block_size = 32 * 1024  # 32KB


def createBlocks(record_data):
    block0 = (len(record_data), math.ceil(sys.getsizeof(record_data) / block_size) + 1)
    listOfRecords = []
    listOfBlocks = []
    listOfBlocks.append(block0)
    csize = 0

    for record in record_data:
        record_size = sys.getsizeof(record)
        if csize + record_size <= block_size:
            csize = csize + record_size
            listOfRecords.append(record)
        else:
            csize = 0
            listOfBlocks.append(listOfRecords)
            listOfRecords = []
            csize = csize + record_size
            listOfRecords.append(record)

    block0 = (len(record_data), len(listOfBlocks))
    listOfBlocks[0] = block0
    # print(block0)
    # print(len(listOfBlocks[1]))

    return listOfBlocks


def create_xml(blocks, records, xml):
    Blocks = ET.Element("Blocks")
    block0 = ET.SubElement(Blocks, "Block", id=str(0))
    ET.SubElement(block0, "number_of_records").text = str(records)
    ET.SubElement(block0, "number_of_blocks").text = str(len(blocks))

    for i, block in enumerate(blocks):
        if i != 0:
            blockEl = ET.SubElement(Blocks, "Block", id=str(i))

            for j, record in enumerate(block):
                recordEl = ET.SubElement(blockEl, "Record", id=str(j))
                ET.SubElement(recordEl, "id").text = str(record[0])
                ET.SubElement(recordEl, "name").text = str(record[1])
                ET.SubElement(recordEl, "coordinates").text = " ".join(map(str, record[2:])) # map: Applies str in each element of the record[2:] = coordinates

    tree = ET.ElementTree(Blocks)

    # write the tree into an XML file
    tree.write("datafile.xml", encoding='utf-8', xml_declaration=True)


# parse the .osm XML file
tree = ET.parse("map.osm")
root = tree.getroot()

# list to store the points only (node data)
record_data = []
tags = {}  # dictionary
for element in root:
    if element.tag == "node":
        id = element.attrib["id"]
        lat = element.attrib["lat"]
        lon = element.attrib["lon"]
        for tag in element.findall("tag"):
            tags[tag.attrib["k"]] = tag.attrib["v"]
        name = tags.get("name", "unknown")

        # coordinates = (lat,lon)
        record_data.append([id, name, lat, lon])

# print(record_data)
listOfBlocks = createBlocks(record_data)
create_xml(listOfBlocks, len(record_data), "datafile.xml")