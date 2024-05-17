import xml.etree.ElementTree as ET
from Node import Node
from Entry import Entry, LeafEntry, Rectangle


def delete(rtree, leaf):
    root = rtree[0]
    N = FindLeaf(leaf, root) # remove the leaf entry if it exists

    if N is None:
        print("There is no such entry in the rtree")

    elif N is not None:
        # now if the node does not have enough entries
        if len(N.entries) < Node.min_entries:
            CondenseTree(rtree, N)
        else:
            AdjustRectangles(N)


def FindLeaf(leaf, root):
    node = root
    while not isinstance(node, LeafEntry):
        for entry in node.entries:
            if entry.rectangle.overlaps_with_point(leaf.point):
                node = entry.child
                break
        else:
            return Node # point not found in the rtree

    for entry in node.entries:
        if entry.record_id == leaf.record_id and entry.point == leaf.point:
            node.entries.remove(entry)
            return node




def AdjustRectangles(N):
    while N is not None and N.parent is not None:
        # if node is a leaf
        if isinstance(N.entries[0], LeafEntry):
            # gather the points
            new_points = []
            for entry in N.entries:
                new_points.append(entry.point)

        else:
            # gather the bounding points of all rectangles
            new_points = []
            for entry in N.entries:
                new_points.append(entry.rectangle.bottom_left)
                new_points.append(entry.rectangle.top_right)

        # update the MBR of the parent entry
        N.parent.entries[N.parent_slot].set_rectangle(new_points)

        # move up to the parent node
        N = N.parent




def load_rtree_from_xml(file):
    rtree = ET.parse(file)
    root = rtree.getroot()
    nodes =[]

    max_entries = int(root.attrib.get("max_entries"))
    Node.set_max_entries(max_entries)

    for N in root.findall("Node"):
        entries = []
        child_indices = []

        # internal nodes
        if N.find("Entry") is not None:
            for entry_elem in N.findall("Entry"):
                rectangle_elem = entry_elem.find("Rectangle")
                bottom_left = [float(coord) for coord in rectangle_elem.find("BottomLeft").text.split()]
                top_right = [float(coord) for coord in rectangle_elem.find("TopRight").text.split()]
                rectangle = Rectangle([bottom_left, top_right])

                child_index = entry_elem.find("ChildNodeIndex")
                if child_index is not None:
                    child_index = int(child_index.text)
                    child_indices.append(child_index)
                entries.append(Entry(rectangle, None)) # create an Entry object and append it to the entries list

        # leaf nodes
        elif N.find("LeafEntry") is not None:
            for entry_elem in N.findall("LeafEntry"):
                record_id = entry_elem.find("RecordID")
                point_elem = entry_elem.find("Point")
                record_id = tuple(map(int, record_id.text.split(",")))
                point = [float(coord) for coord in point_elem.text.split()]

                # record by combining the record ID and point coordinates
                record = [record_id[0], record_id[1]] + [float(coord) for coord in point]
                leaf_entry = LeafEntry(record)
                entries.append(leaf_entry)

        parent_node_index = N.find("ParentNodeIndex")
        if parent_node_index is not None:
            parent_node = nodes[int(parent_node_index.text)]
            parent_slot = int(N.find("SlotInParent").text)
            node = Node(entries, parent_node, parent_slot)  # create node and set parent
            parent_node.entries[parent_slot].set_child(node)  # sets the parent's corresponding entry's child
        else:
            node = Node(entries)  # root node only
        nodes.append(node)

        Node.set_overflow_treatment_level(nodes[-1].getLevel()) # gets the level of the last node

    return nodes


rtree = load_rtree_from_xml("indexfile3000.xml")

delete(rtree,LeafEntry())