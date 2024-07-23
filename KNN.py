import heapq
import math
import time

from Entry import LeafEntry, Entry, Rectangle
import xml.etree.ElementTree as ET
from Node import Node


def knn(root, qpoint, k):
    pq = []  # Elements are (distance, count, node/point, is_leaf)
    count = 0  # used to maintain the order of elements with the same distance in the queue
    visited = set()  # To keep track of visited nodes and leaf entries

    # Initialize the queue with the root
    for entry in root.entries:
        if id(entry) not in visited:
            visited.add(id(entry))

            if isinstance(entry, LeafEntry):
                point_dist = math.sqrt(sum([(a - b) ** 2 for a, b in zip(qpoint, entry.point)]))
                heapq.heappush(pq, (point_dist, count, entry, True))
            else:
                heapq.heappush(pq, (entry.rectangle.euclidean_distance(qpoint), count, entry.child, False))
            count += 1

    result = []
    while pq and len(result) < k:
        distance, _, current, is_leaf = heapq.heappop(pq)
        if is_leaf:
            result.append((distance, current.point, current.record_id))
        else:
            for entry in current.entries:
                entry_id = id(entry)
                if entry_id not in visited:
                    if isinstance(entry, LeafEntry):
                        point_dist = math.sqrt(sum([(a - b) ** 2 for a, b in zip(qpoint, entry.point)]))
                        heapq.heappush(pq, (point_dist, count, entry, True))
                    else:  # Internal Node
                        rectangle_distance = entry.rectangle.euclidean_distance(qpoint)
                        heapq.heappush(pq, (rectangle_distance, count, entry.child, False))
                    count += 1
    return result


def linear_search_in_datafile_KNN(qpoint, datafile, k):
    tree = ET.parse(datafile)
    root = tree.getroot()
    result = []

    for block_elem in root.findall("Block"):
        if int(block_elem.get("id")) == 0:
            continue

        # for every record in each block
        for record_elem in block_elem.findall("Record"):
            coordinates = record_elem.find(".//coordinates").text.split()
            point = list(map(float, coordinates)) # Converts the list of strings to a list of floats representing the point.
            point_dist = math.sqrt(sum([(a - b) ** 2 for a, b in zip(qpoint, point)]))
            result = [point, point_dist]
            result.append(result)

        return result[:k]


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


tree = load_rtree_from_xml("indexfile1.xml")

length = len(tree[-1].entries[0].point)
print(length)

#qpoint = [0] * length
qpoint = [3,-8]
k = 1

start_time = time.time()
k_nearest_neighbors = knn(tree[0], qpoint, k)
end_time = time.time()
print("\nKNN using knn algorithm in tree: ", end_time-start_time, " sec")

for distance, point, record_id in k_nearest_neighbors:
    print(f"Distance: {distance}")
    print(f"RecordID: {record_id}")
    print(f"Point: {point}")
    print("---------------------")

datafile = "datafile.xml"
start_time = time.time()
result_records = linear_search_in_datafile_KNN(qpoint, datafile, k)
end_time = time.time()
print("\nKNN using linear search in datafile: ", end_time-start_time, " sec")

for list in result_records:
    print(f"Distance: {list[1]}")
    print(f"Point: {list[0]}")
    print("---------------------")
