import xml.etree.ElementTree as ET


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
    rtree = []

    # 1. Sorting: the spatial objects are sorted along one of the dimensions (e.g. x-coor). Quicksort or mergesort
    #    We can use Z - order or Hilbert curve to covert the multi-dimensional coordinates to 1D value.
    sorted_records = sort_records(records)

    # 2. Partitioning into tiles: the sorted objects are recursively partitioned into groups (tiles / blocks).
    # 3. building the tree: at each level of the tree, the blocks are grouped together to form the nodes.
    #    if the node exceeds the max capacity, it's split into two nodes.
    # 4. recursive process: repeat the above process, until all objects are included in leaf nodes.
    # 5. minimized overlap after the redistribution of the split nodes

    return rtree


def sort_records(records):
    sorted_records = []
    z_value = z_order_method(records)
    return sorted_records


def z_order_method(records):
    z_value = []

    return z_value


# read the records from datafile
read_records = read_records_from_osm("datafile3000.xml")
rtree = bulk_loading(read_records)
