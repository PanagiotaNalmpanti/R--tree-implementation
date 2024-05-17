import sys
import xml.etree.ElementTree as ET

block_size = 32 * 1024  # 32KB
max_entries = 4


def read_records_from_osm(file):
    # parse the .osm XML file
    tree = ET.parse("map.osm")
    root = tree.getroot()

    # list to store the points only (node data)
    record_data = []
    tags = {}  # dictionary
    count = 0  # for testing only
    for element in root:
        if element.tag == "node":
            if count < 3000:  # for testing only
                count += 1  # for testing only
                id = element.attrib["id"]
                lat = element.attrib["lat"]
                lon = element.attrib["lon"]
                for tag in element.findall("tag"):
                    tags[tag.attrib["k"]] = tag.attrib["v"]
                name = tags.get("name", "unknown")

                # coordinates = (lat,lon)
                record_data.append([id, name, lat, lon])  # here you can add more dimensions

            else:  # for testing only
                break  # for testing only
    return record_data


# Sort-Tile-Recursive algorithm
def bulk_loading(records):
    sorted_records = sort_records(records)
    blocks_of_records = createBlocks(sorted_records)
    leaf_nodes = create_LeafNodes(blocks_of_records)
    tree = finalTree(leaf_nodes)
    return tree


def sort_records(records):
    sorted_records = sorted(records, key=lambda record: z_order_method(record[2:]))
    return sorted_records


def z_order_method(coordinates):
    scaled_coords = [int(float(co) * 10 ** 10) for co in coordinates]
    bits = 32
    bin_coord = [[int(bit) for bit in bin(co)[2:].zfill(bits)] for co in scaled_coords]
    z_value_bin = ''.join([str(dim[i]) for i in range(bits) for dim in bin_coord])
    z_value = int(z_value_bin, 2)
    return z_value


def createBlocks(records):
    blocks = []
    list_of_records = []
    count_size = 0
    for record in records:
        rec_size = sys.getsizeof(record)
        if count_size + rec_size <= block_size:
            count_size = count_size + rec_size
            list_of_records.append(record)
        else:
            count_size = 0
            blocks.append(list_of_records)
            list_of_records = []
            count_size = count_size + rec_size
            list_of_records.append(record)
    return blocks


def create_LeafNodes(blocks):
    leaf_nodes = []
    for block in blocks:
        mbr = calculateMBR(block)
        leaf_nodes.append((mbr, block))
    return leaf_nodes


def calculateMBR(block):
    length = len(block[0])
    bottom_left = [min(float(record[dim]) for record in block) for dim in range(2, length)]
    top_right = [max(float(record[dim]) for record in block) for dim in range(2, length)]
    mbr = (bottom_left, top_right)
    return mbr


def finalTree(nodes):
    if len(nodes) <= max_entries:  # we reached the root
        return nodes
    level = []  # list that contains the nodes of the current level
    for i in range(0, len(nodes), max_entries):
        children = nodes[i:i + max_entries]
        recs = []
        for child in children:
            for record in child[1]:
                recs.append(record)
        mbr = calculateMBR(recs)
        level.append((mbr, children))
    return finalTree(level)


def rtree_xml(rtree):
    root_element = ET.Element("R_Star_Tree")
    for node in rtree:
        root_element.append(build_xml(node))

    tree = ET.ElementTree(root_element)
    tree.write("bulk_loaded_tree.xml")


def build_xml(node):
    node_element = ET.Element("Node")
    mbr_element = ET.SubElement(node_element, "MBR")
    mbr_element.text = str(node[0])

    if isinstance(node[1][0], list):
        for record in node[1]:
            record_element = ET.SubElement(node_element, "Record")
            record_element.text = str(record)
    else:
        for child in node[1]:
            child_element = build_xml(child)
            node_element.append(child_element)
    return node_element


# read the records from datafile
read_records = read_records_from_osm("datafile3000.xml")
rtree = bulk_loading(read_records)
rtree_xml(rtree)
