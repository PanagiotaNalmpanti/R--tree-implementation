import xml.etree.ElementTree as ET
from Node import Node
from Entry import Entry, LeafEntry, Rectangle
from insert import insert_to_tree
import time


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
    Node.set_max_entries(len(blocks[0]))
    return blocks


def z_order_method(coordinates):
    scaled_coords = [int(float(co) * 10 ** 10) for co in coordinates]
    bits = 32
    bin_coord = [[int(bit) for bit in bin(co)[2:].zfill(bits)] for co in scaled_coords]
    z_value_bin = ''.join([str(dim[i]) for i in range(bits) for dim in bin_coord])
    z_value = int(z_value_bin, 2)
    return z_value


def leaf_entries_from_node(node):
    leaf_ent = []
    if node.is_leaf():
        for entry in node.entries:
            leaf_ent.append(entry)
    else:
        for entry in node.entries:
            leaf_entries_from_node(entry.child)
    return leaf_ent


def leaf_nodes_from_node(node):
    leaf_nodes = []
    if node.is_leaf():
        leaf_nodes.append(node)
    else:
        for entry in node.entries:
            leaf_nodes_from_node(entry.child)
    return leaf_nodes


def bulk_loading(blocks_from_file):
    max_entries = Node.max_entries
    leaf_entries = []
    for block in blocks_from_file:
        for record in block:  # create entries of type LeafEntry
            new_leaf_entry = LeafEntry(record)
            leaf_entries.append(new_leaf_entry)

    # sorting the entries using the z-order method
    sorted_leaf_entries = sorted(leaf_entries, key=lambda entry: z_order_method(entry.point))

    # creating new leaf nodes
    leaf_nodes = []
    current_entries = []
    Node.set_max_entries(round(0.8 * max_entries))
    entries_left = []
    for entry in sorted_leaf_entries:
        if len(current_entries) < Node.max_entries:
            current_entries.append(entry)
        else:  # if we reach the maximum number of entries, we create a new node + list of entries
            new_node = Node(current_entries)
            leaf_nodes.append(new_node)
            current_entries = [entry]

    # if the current entries are more than the minimum number, we create a new leaf node
    if len(current_entries) >= Node.min_entries:
        new_node = Node(current_entries)
        leaf_nodes.append(new_node)
    else:  # else we insert the entries in a list with entries for future insertion
        entries_left.extend(current_entries)

    # for each node, we calculate the MBR
    for node in leaf_nodes:
        points = [entry.point for entry in node.entries]  # points of all entries of the node
        node.mbr = Rectangle(points)

    entries = [Entry(node.mbr, node) for node in leaf_nodes]  # instances of Entry(Rectangle, child)

    internal_nodes = []
    current_entry_list = []

    for entry in entries:
        if len(current_entry_list) < Node.max_entries:
            current_entry_list.append(entry)
        else:
            new_node = Node(current_entry_list)
            internal_nodes.append(new_node)
            # setting the parent
            for e in current_entry_list:
                e.child.set_parent(new_node, current_entry_list.index(e))  # set_parent(parent, parent_slot)
            current_entry_list = [entry]

    if current_entry_list:
        new_node = Node(current_entry_list)
        internal_nodes.append(new_node)
        for e in current_entry_list:
            e.child.set_parent(new_node, current_entry_list.index(e))

    if len(internal_nodes) == 1:
        # if there is only one node in the list, then we set it as root
        root = internal_nodes[0]
        tree = [root]
        for node in leaf_nodes:
            tree.append(node)

        Node.set_max_entries(max_entries)
        for leaf_entry in entries_left:
            insert_to_tree(tree, leaf_entry)
    else:
        # if the entries are less than the minimum, we append them to entries_left for future insertion
        if len(internal_nodes[-1].entries) < Node.min_entries:
            leaf_entries_from_last_node = leaf_entries_from_node(internal_nodes[-1])
            entries_left.extend(leaf_entries_from_last_node)
            leaf_nodes_from_last_node = leaf_nodes_from_node(internal_nodes[-1])

            # remove the leaf nodes that are connected with the last internal node
            for leaf_node in leaf_nodes_from_last_node:
                if leaf_node in leaf_nodes:
                    leaf_nodes.remove(leaf_node)

            # remove the last internal node
            internal_nodes = internal_nodes[:-1]

    # creating upper-level internal nodes
    upper_level_internal_nodes = internal_nodes
    while len(upper_level_internal_nodes) > 1:
        next_level_nodes = []
        group_of_nodes = []
        for node in upper_level_internal_nodes:
            if len(group_of_nodes) < Node.max_entries:
                group_of_nodes.append(node)
            else:  # creating a new internal node, using group_of_nodes
                mbr = Rectangle([entry.mbr.bottom_left for entry in group_of_nodes] + [entry.mbr.top_right for entry in group_of_nodes])
                new_internal = Node([Entry(mbr, node) for node in group_of_nodes])
                next_level_nodes.append(new_internal)

                for slot, entry in enumerate(new_internal.entries):
                    entry.child.set_parent(new_internal, slot)

                group_of_nodes = [node]

        if group_of_nodes:
            mbr = Rectangle([entry.mbr.bottom_left for entry in group_of_nodes] + [entry.mbr.top_right for entry in group_of_nodes])
            new_internal = Node([Entry(mbr, node) for node in group_of_nodes])
            next_level_nodes.append(new_internal)

            for slot, entry in enumerate(new_internal.entries):
                entry.child.set_parent(new_internal, slot)

        upper_level_internal_nodes = next_level_nodes

    # if there is only one node left, then it's the root
    if len(upper_level_internal_nodes) == 1:
        root = upper_level_internal_nodes[0]

    # constructing the final tree : [root + internal nodes + leaf nodes]
    tree = [root] + [node for node in upper_level_internal_nodes if node != root] + leaf_nodes

    Node.set_max_entries(max_entries)

    # insert the leaf entries (records) that are left from the node that was not inserted in the tree
    for leaf_entry in entries_left:
        insert_to_tree(tree, leaf_entry)

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


blocks_from_file = read_blocks_from_datafile("datafile.xml")
start_time = time.time()
rtree = bulk_loading(blocks_from_file)
end_time = time.time()

print("Build the rtree by inserting the records bottom up: ", end_time - start_time, " sec")
print("The tree has ", len(rtree), " nodes: ")
for i, node in enumerate(rtree):
    print("node", i, "level=", node.getLevel(), "num of entries = ", len(node.entries))
    for j, entry in enumerate(node.entries):
        if isinstance(entry, LeafEntry):
            print("       leaf_entry", j, ":", entry.record_id, entry.point)
        else:
            print("       entry", j, ":", entry.rectangle.bottom_left, " ", entry.rectangle.top_right)

print("\n")

save_to_xml(rtree, "indexfile.xml")
