import math
import sys
import xml.etree.ElementTree as ET

import insert
from Node import Node
from Entry import Entry, LeafEntry, Rectangle
from insert import insert_to_tree

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

    # create entries type LeafEntry
    leaf_entries = []
    for record in sorted_records:
        entry = LeafEntry(record)
        leaf_entries.append(entry)

    tree = []
    rtree = insert_bottom_up(tree, leaf_entries)
    return rtree


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


def insert_bottom_up(tree, leaf_entries):
    # Create leaf nodes
    leaf_nodes = []
    current_entries = []
    for record in leaf_entries:
        if len(current_entries) < Node.max_entries:
            current_entries.append(record)
        else:
            new_node = Node(current_entries)
            leaf_nodes.append(new_node)
            current_entries = [record]

    entries_left = []  # last entries that do not reach the minimum number a node should have
    if len(current_entries) >= Node.min_entries:
        new_node = Node(current_entries)
        leaf_nodes.append(new_node)
    else:
        entries_left.append(current_entries)

    # create entries (type Entry, parents of the leaf nodes) that contain the MBR of the leaf nodes
    entries = []
    for node in leaf_nodes:
        points = [entry.point for entry in node.entries]
        node.mbr = Rectangle(points)
        entries.append(Entry(node.mbr, node))  # Entry(Rectangle, child)

    internal_nodes = []
    current_entries = []
    for entry in entries:
        if len(current_entries) < Node.max_entries:
            current_entries.append(entry)
        else:
            new_node = Node(current_entries)
            internal_nodes.append(new_node)
            # set the parent
            for e in current_entries:
                e.child.set_parent(new_node, current_entries.index(e))  # set_parent(parent, parent_slot)
            current_entries = [entry]

    if len(current_entries) > 0:
        new_node = Node(current_entries)
        internal_nodes.append(new_node)
        for e in current_entries:
            e.child.set_parent(new_node, current_entries.index(e))
    if len(internal_nodes) == 1:
        root = internal_nodes[0]  # if there is only one node in the list, then we set it as root
        tree = [root]
        for node in leaf_nodes:
            tree.append(node)

        overflow_treatment_level = tree[-1].getLevel()
        for entry in entries_left:
            insert.insert_to_tree(tree, entry)
    else:
        if len(internal_nodes[-1].entries) < Node.min_entries:
            entries_from_last_internal = internal_nodes[-1].entries
            last_leaf_nodes = [entry.child for entry in entries_from_last_internal]
            leaf_entr = [entry.entries for entry in last_leaf_nodes]
            entries_left.extend(entry for entry in leaf_entr)

            for leaf_node in last_leaf_nodes:  # remove leaf nodes that are connected with the last internal node
                if leaf_node in leaf_nodes:
                    leaf_nodes.remove(leaf_node)

            internal_nodes = internal_nodes[:-1]  # remove the last internal node

    # create upper-level internal nodes
    upper_level_internal_nodes = internal_nodes
    while len(upper_level_internal_nodes) > 1:
        next_level_nodes = []
        set_of_nodes = []
        for node in upper_level_internal_nodes:
            if len(set_of_nodes) < Node.max_entries:
                set_of_nodes.append(node)
            else:
                # create new node
                entr = []
                for n in set_of_nodes:
                    for e in n.entries:
                        entr.append(e)
                mbr = Rectangle([e.rectangle.bottom_left for e in entr] +
                                [e.rectangle.top_right for e in entr])
                set_of_entries = [Entry(mbr, node) for node in set_of_nodes]
                new_node = Node(set_of_entries)
                next_level_nodes.append(new_node)

                for slot, entry in enumerate(new_node.entries):
                    entry.child.set_parent(new_node, slot)
                set_of_nodes = [node]

        if len(set_of_nodes) > 0:
            # create new node
            entr = []
            for n in set_of_nodes:
                for e in n.entries:
                    entr.append(e)
            mbr = Rectangle([e.rectangle.bottom_left for e in entr] +
                            [e.rectangle.top_right for e in entr])
            set_of_entries = [Entry(mbr, node) for node in set_of_nodes]
            new_node = Node(set_of_entries)
            next_level_nodes.append(new_node)

            for slot, entry in enumerate(new_node.entries):
                entry.child.set_parent(new_node, slot)

        upper_level_internal_nodes = next_level_nodes

    if len(upper_level_internal_nodes) == 1:  # if there is only one node left, then it's the root
        root = upper_level_internal_nodes[0]

    # construct the final tree
    temp = upper_level_internal_nodes
    for node in temp:
        if node != root:
            upper_level_internal_nodes.append(node)
    tree = [root] + upper_level_internal_nodes + leaf_nodes

    # insert the leaf entries (records) that are left from the node that was not inserted in the tree
    overflow_treatment_level = tree[-1].getLevel()
    for entry in entries_left:
        insert.insert_to_tree(tree, entry)

    return tree


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


def save_to_xml(tree, file):
    root_elem = ET.Element("Nodes", max_entries=str(Node.max_entries))
    nodes = tree
    for node in nodes:
        node_elem = ET.SubElement(root_elem, "Node")
        build_xml(node_elem, node, nodes)
    xml_tree = ET.ElementTree(root_elem)
    xml_tree.write(file, encoding="utf-8", xml_declaration=True)


read_records = read_records_from_datafile("datafile3000.xml")
rtree = bulk_loading(read_records)
save_to_xml(rtree, "indexfile3000_bulk.xml")
