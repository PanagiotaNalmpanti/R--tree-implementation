import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
import sys
import math
block_size = 32 * 1024  # 32KB

def createBlocks(record_data):
    block0 = (len(record_data), math.ceil(sys.getsizeof(record_data) / block_size)+1)
    listOfRecords = []
    listOfBlocks = []
    listOfBlocks.append(block0)
    csize = 0
    i = 0

    for _ in record_data:
        print(csize+sys.getsizeof(record_data[i]))
        if csize+sys.getsizeof(record_data[i]) <= block_size:
           csize = csize-sys.getsizeof(record_data[i])
           listOfRecords.append(record_data[i])
           i += 1
        else:
            csize = 0
            listOfBlocks.append(listOfRecords)
    print(listOfBlocks)
    # print(sys.getsizeof(record_data)) # 2.05 blocks




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

        record_data.append([id, name, (lat, lon)])

# print(record_data)
createBlocks(record_data)
