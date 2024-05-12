import xml.etree.ElementTree as ET


def read_blocks_from_datafile(file):
    tree = ET.parse(file)
    root = tree.getroot()
    blocks = []
    number_of_blocks = int(root.find('Block').find('number_of_blocks').text)

    for id in range(1, number_of_blocks):
        block_id = id
        block_records = []

        # Iterate through records within the block
        for record in root.find(f"Block[@id='{id}']").findall('Record'):
            slot = int(record.attrib['id'])

            coordinates_text = record.find('coordinates').text
            coordinates = coordinates_text.split()

            block_records.append([block_id, slot] + [float(coord) for coord in coordinates])
        blocks.append(block_records)

    return blocks


# Sort-Tile-Recursive algorithm
def bulk_loading(blocks):
    rtree = []

    # 1. Sorting: the spatial objects are sorted along one of the dimensions (e.g. x-coor). Quicksort or mergesort
    # 2. Partitioning into tiles: the sorted objects are recursively partitioned into groups (tiles / blocks).
    # 3. building the tree: at each level of the tree, the blocks are grouped together to form the nodes.
    #    if the node exceeds the max capacity, it's split into two nodes.
    # 4. recursive process: repeat the above process, until all objects are included in leaf nodes.
    # 5. minimized overlap after the redistribution of the split nodes

    return rtree


# read the records from datafile
read_blocks = read_blocks_from_datafile("datafile3000.xml")
rtree = bulk_loading(read_blocks)
