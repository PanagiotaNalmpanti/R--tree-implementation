import math
import sys
import xml.etree.ElementTree as ET
from Node import Node
from Entry import Entry, LeafEntry, Rectangle

block_size = 32 * 1024  # 32KB


def read_records_from_datafile(file):
    tree = ET.parse(file)
    root = tree.getroot()
    number_of_blocks = int(root.find('Block').find('number_of_blocks').text)
    record_data = []
    for id in range(1, number_of_blocks):
        block_id = id

        # Iterate through records within the block
        for record in root.find(f"Block[@id='{id}']").findall('Record'):
            slot = int(record.attrib['id'])

            coordinates_text = record.find('coordinates').text
            coordinates = coordinates_text.split()

            record_data.append([block_id, slot] + [float(coord) for coord in coordinates])
    return record_data


def bulk_loading(recs):
    sorted_records = sort_records(recs)
    #print(sorted_records)
    #blocks = createBlocks(sorted_records)

    #block_leaves = []
    #for block in blocks:
    #    for record in block:
    #        r = LeafEntry(record)
    #        b = Node()
    #        b.entries.append(r)
    #    block_leaves.append(b)

    tree = []
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
    block0 = (len(records), math.ceil(sys.getsizeof(records) / block_size) + 1)
    listOfRecords = []
    listOfBlocks = []
    listOfBlocks.append(block0)
    csize = 0

    for record in records:
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
    block0 = (len(records), len(listOfBlocks))
    listOfBlocks[0] = block0

    blocks = []
    number_of_blocks = len(listOfBlocks)
    for id in range(1, number_of_blocks):
        block_id = id
        block_records = []
        for rec_id, record in enumerate(listOfBlocks[id]):
            slot = rec_id
            coordinates = record[2:]
            block_records.append([block_id, slot] + [float(coord) for coord in coordinates])
        blocks.append(block_records)
    return blocks


def insert_to_tree(tree, r):
    N = chooseSubtree(tree, r)

    if len(N.entries) < Node.max_entries:
        N.entries.append(r)
        adjust_rectangles(N)

def chooseSubtree(tree, r):
    N = tree[0]
    if len(N.entries) == 0:
        return N


    N = tree[0]

    if len(N.entries) == 0:
        return N
    while not isinstance(N.entries[0], LeafEntry):
        if isinstance(N.entries[0].child.entries[0], LeafEntry):
            min_overlap_cost = float('inf')
            min_area_cost = float('inf')
            chosen = None
            for i,entry in enumerate(N.entries):
                overlap_enlargement = entry.rectangle.calculate_overlap_enlargement(r, i, N)
                area_enlargement = entry.rectangle.calculate_area_enlargement(r)
                if overlap_enlargement < min_overlap_cost or (overlap_enlargement == min_overlap_cost and area_enlargement < min_area_cost):
                    min_overlap_cost = overlap_enlargement
                    min_area_cost = area_enlargement
                    chosen = entry
        else:
            min_overlap_cost = float('inf')
            min_area_cost = float('inf')
            chosen = None
            for entry in N.entries:
                area_enlargement = entry.rectangle.calculate_area_enlargement(r)
                new_area = area_enlargement + entry.rectangle.calculate_area()
                if area_enlargement < min_area_cost or (area_enlargement == min_area_cost and new_area < min_area_cost):
                    min_area_cost = area_enlargement
                    min_area = new_area
                    chosen = entry
        N = chosen.child
    return N


def adjust_rectangles(N):
    while N is not None and N.parent is not None:
        if isinstance(N.entries[0], LeafEntry):
            new_points = []
            for entry in N.entries:
                new_points.append(entry.point)
        else:
            new_points = []
            for entry in N.entries:
                new_points.append(entry.rectangle.bottom_left)
                new_points.append(entry.rectangle.top_right)
        N.parent.entries[N.parent_slot].set


read_records = read_records_from_datafile("datafile3000.xml")
rtree = bulk_loading(read_records)
