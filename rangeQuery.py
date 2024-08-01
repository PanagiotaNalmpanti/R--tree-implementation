import time
from Entry import LeafEntry, Entry, Rectangle
import xml.etree.ElementTree as ET
from Node import Node


def find_rectangle_points_for_range_query(rec, root):
        res = []
        if isinstance(root.entries[0], Entry):
            for entry in root.entries:
                if rec.overlaps_with_rectangle(entry.rectangle):
                    result.extend(rec.rectangle.find_rectangle_points_for_range_query(rec, entry.child))
        else:
            for leaf_entry in root.entries:
                if rec.overlaps_with_point(leaf_entry.point):
                    result.append(leaf_entry)
        return res


def linear_search_in_datafile_RQ(file, rectangle):
    result = []
    tree = ET.parse(file)
    root = tree.getroot()

    for block_elem in root.findall("Block"):
        if int(block_elem.get("id")) == 0:
            continue

        for record in block_elem.findall("Record"):
            coordinates = record.find(".//coordinates").text.split()
            point = list(map(float, coordinates))
            if rectangle.overlaps_with_point(point):
                record_id = int(record.find(".//record_id").text)
                name = record.find(".//name").text
                result.append([record_id, name, point])
    return result


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


# range query using R-tree
tree = load_rtree_from_xml("indexfile.xml")
# length = len(tree[-1].entries[0].point)
# print("Length: ", length)
# qpoint = [0] * length
# print(qpoint)

points = [[2, 1], [1, 4]]
rectangle = Rectangle([[2, 1], [1, 4]])  # random points to create a rectangle for the range query

start_time = time.time()
query_points = find_rectangle_points_for_range_query(rectangle, tree[0])
end_time = time.time()
print("Range Query using R-tree algorithm: ", end_time - start_time, " sec")

# range query using linear search
datafile = "datafile.xml"
start_time = time.time()
result = linear_search_in_datafile_RQ(datafile, rectangle)
end_time = time.time()
print("Range query using linear search algorithm: ", end_time - start_time, " sec")
