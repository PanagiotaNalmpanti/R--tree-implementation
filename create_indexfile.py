from Node import Node
from Entry import Rectangle, Entry, LeafEntry
import xml.etree.ElementTree as ET


def build_xml(node_elem, N, nodes):
    for entry in N.entries:
        if isinstance(entry, Entry):
            child_index = nodes.index(entry.child)
            entry.to_xml(node_elem, child_index)
        else:
            entry.to_xml(node_elem)
    if N.parent is not None:
        parent_node_index = nodes.index(N.parent)
        ET.SubElement(node_elem, "ParentNodeIndex").text = str(parent_node_index)
        ET.SubElement(node_elem, "SlotInParent").text = str(N.parent_slot)


def save_rtree_to_xml(rtree, filename):
    root_elem = ET.Element("Nodes", max_entries=str(Node.max_entries))

    nodes = rtree  # Assuming tree is a list of nodes
    for node in nodes:
        node_elem = ET.SubElement(root_elem, "Node")
        build_xml(node_elem, node, nodes)

    xml_rtree = ET.ElementTree(root_elem)

    # Save to the specified filename with 'utf-8' encoding and pretty formatting
    xml_rtree.write(filename, encoding="utf-8", xml_declaration=True)


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
