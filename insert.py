import xml.etree.ElementTree as ET
from Node import Node
from Entry import Entry, LeafEntry, Rectangle
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


def insert_one_by_one(blocks, num_of_entries):
    rtree = []
    root = Node()
    rtree.append(root)
    Node.set_max_entries(num_of_entries)
    for block in blocks:
        for record in block:
            r = LeafEntry(record)
            rtree = insert_to_tree(rtree, r)
    return rtree

def insert_to_tree(rtree, r):
    N = chooseSubtree()
    node_level = N.getLevel()
    if len(N.entries) < Node.max_entries:
        N.entries.append(r)
    else:
        n

# read the records from datafile
read_blocks = read_blocks_from_datafile("datafile3000.xml")
rtree = insert_one_by_one(read_blocks, Node.max_entries)
