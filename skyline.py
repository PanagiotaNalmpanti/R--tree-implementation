from Entry import LeafEntry, Entry, Rectangle
import xml.etree.ElementTree as ET
from Node import Node
import heapq
import math


# Calculate the min distance from a query point to a MBR
def mindist(qpoint, rectangle):
    dist = 0
    for q_coord, bl, tr in zip(qpoint, rectangle.bottom_left, rectangle.top_right):
        if q_coord < bl:
            dist += (bl - q_coord) ** 2
        elif q_coord > tr:
            dist += (q_coord - tr) ** 2
    return math.sqrt(dist)


def is_dominated(point, spoints):
    for Spoint in spoints:
        if all(a <= b for a, b in zip(Spoint, point)):
            return True
    return False


def dominates(a, b):
    less_in_one_dimension = False # less in at least one dimension
    less_or_equal_in_all_dimensions = True

    for ai, bi in zip(a, b):
        if ai > bi:
            less_or_equal_in_all_dimensions = False
            break
        if ai < bi:
            less_in_one_dimension = True

    return less_in_one_dimension and less_or_equal_in_all_dimensions


# used in the priority queue to process entries based on their minimum distance
class QEntry:
    def __init__(self, mindist, node_or_entry):
        self.mindist = mindist
        self.node_or_entry = node_or_entry

    def __lt__(self, other):
        return self.mindist < other.mindist


def BBS(rtree, qpoint):
    pq = [QEntry(0, 0)]
    skyline = []

    while pq:
        queue_entry = heapq.heappop(pq)
        index = queue_entry.node_or_entry
        node = rtree[index]

        if node.is_leaf():
            for entry in node.entries:
                if not is_dominated(entry.point, skyline):
                    for s in list(skyline):
                        if dominates(entry.point, s):
                            skyline.remove(s)
                    skyline.append(entry.point)

        else:
            for entry in node.entries:
                if entry.child is not None:
                    emindist = mindist(qpoint, entry.rectangle)
                    child_index = rtree.index(entry.child)
                    heapq.heappush(pq, QEntry(emindist, child_index))


    return skyline


def load_rtree_from_xml(filename):
    rtree = ET.parse(filename)
    root = rtree.getroot()
    nodes = []  # store the final tree

    # load and set the max_entries of the tree nodes
    max_entries = int(root.attrib.get("max_entries"))
    Node.set_max_entries(max_entries)

    # start rebuilding all the Node objects
    for node_elem in root.findall("Node"):
        entries = []  # temp list to hold the entries of each Node
        child_indexes = []

        # for every Entry in the Node, rebuild the Entry object and append it to the entries list
        if node_elem.find("Entry") is not None:
            for entry_elem in node_elem.findall("Entry"):
                rectangle_elem = entry_elem.find("Rectangle")
                bottom_left = [float(coord) for coord in rectangle_elem.find("BottomLeft").text.split()]
                top_right = [float(coord) for coord in rectangle_elem.find("TopRight").text.split()]
                rectangle = Rectangle([bottom_left, top_right])

                child_index_elem = entry_elem.find("ChildNodeIndex")
                # save the indexes of the children in order to set them later when all the node have been constructed
                if child_index_elem is not None:
                    child_index = int(child_index_elem.text)
                    child_indexes.append(child_index)
                entries.append(Entry(rectangle, None))

        # for every LeafEntry in the Node, rebuild the LeafEntry object and append it to the entries list
        elif node_elem.find("LeafEntry") is not None:
            for entry_elem in node_elem.findall("LeafEntry"):
                record_id_elem = entry_elem.find("RecordID")
                point_elem = entry_elem.find("Point")
                record_id = tuple(map(int, record_id_elem.text.split(",")))
                point = [float(coord) for coord in point_elem.text.split()]
                record = [record_id[0], record_id[1]] + [float(coord) for coord in point]
                leaf_entry = LeafEntry(record)
                entries.append(leaf_entry)

        parent_index_elem = node_elem.find("ParentNodeIndex")
        # if current Node has a parent it has already been constructed and inserted in the nodes list
        if parent_index_elem is not None:
            parent_node = nodes[int(parent_index_elem.text)]  # find parent node
            slot_in_parent = int(node_elem.find("SlotInParent").text)  # find the corresponding slot in parent node
            node = Node(entries, parent_node, slot_in_parent)  # creates node and sets parent
            parent_node.entries[slot_in_parent].set_child(node)  # sets the parent's corresponding entry's child
        else:
            node = Node(entries)  # only for root node
        nodes.append(node)

        Node.set_overflow_treatment_level(nodes[-1].getLevel())

    return nodes


# Retrieve specific records from the datafile based on a list of LeafEntry objects
def get_record_from_datafile(points, filename):
    # Group points by block_id
    points_by_block = {}
    for point in points:
        block_id = point.record_id[0]
        points_by_block.setdefault(block_id, []).append(point)

    # Fetch records for each block
    records = []
    for block_id, entries in points_by_block.items():
        block_records = read_block_from_datafile(block_id, filename)
        for entry in entries:
            slot = entry.record_id[1]
            records.append(block_records[slot])

    return records


# Read all records from a specific block in an XML
def read_block_from_datafile(block_id, filename):
    rtree = ET.parse(filename)
    root = rtree.getroot()

    # Find the block with the given id
    block = root.find(f".//Block[@id='{block_id}']")
    if block is None:
        return []  # Block not found

    # Extract records from the block
    records = []
    for record_elem in block.findall(".//Record"):
        record_id = int(record_elem.find(".//record_id").text)
        name = record_elem.find(".//name").text
        coordinates = list(map(float, record_elem.find(".//coordinates").text.split()))
        records.append([record_id, name, *coordinates])

    return records



### Skyline testing
rtree = load_rtree_from_xml("indexfile1.xml")

length = len(rtree[-1].entries[0].point)
print("Length:", length)

qpoint = [0] * length
result = BBS(rtree, qpoint)
print("Result of skyline algorithm:", result)