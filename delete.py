from insert import *


def delete(rtree, leaf):
    root = rtree[0]
    N = FindLeaf(leaf, root)  # remove the leaf entry if it exists

    if N is None:
        print("There is no such entry in the rtree")

    else:
        print("Deleting", leaf.point)
        # now if the node does not have enough entries
        if len(N.entries) < Node.min_entries:
            print("condense")
            CondenseTree(rtree, N)
        else:
            print("adjust")
            AdjustRectangles(N)


def FindLeaf(leaf, root):
    nodes_to_examine = [root]
    while nodes_to_examine:
        current_node = nodes_to_examine.pop()

        # if it is a leaf node
        if isinstance(current_node.entries[0], LeafEntry):
            # search for the target entry
            for e in current_node.entries:
                if e.record_id == leaf.record_id and e.point == leaf.point:
                    current_node.entries.remove(e)
                    return current_node

        # if it is internal node
        else:
            for e in current_node.entries:
                # check if the entry's rectangle overlaps with the point of the target entry
                if e.rectangle.overlaps_with_point(leaf.point):

                    nodes_to_examine.append(e.child)

    return None  # entry not found


def CondenseTree(rtree, N):
    eliminated_nodes = []
    while N.parent is not None:
        # if the node does not have enough entries
        if len(N.entries) < Node.min_entries:
            # insert the node to the eliminated list
            eliminated_nodes.append(N)
            # remove the corresponding entry from the parent
            parent = N.parent
            parent.entries.remove(parent.entries[N.parent_slot])
            # update parent slot for remaining entries
            for i, entry in enumerate(parent.entries):
                entry.child.parent_slot = i
            rtree.remove(N)

            # Remove children of the node if node is internal
            if isinstance(N.entries[0], Entry):
                remove_children(rtree, N)
            N = parent
        else:
            # adjust the MBR recursively
            AdjustRectangles(N)
            break

    root = rtree[0]
    # if the root has one entry, make its child the new root
    if len(root.entries) == 1 and isinstance(root.entries[0], Entry):
        root.child.set_parent(None, None)
        new_root = root.entries[0].child
        rtree.remove(root)
        rtree[0] = new_root

    # set overflow treatment level based on the last node's level
    Node.set_overflow_treatment_level(rtree[-1].getLevel())

    # ReInsert entries from eliminated nodes
    for node in eliminated_nodes:
        # get all leaf entries of the node
        leaf_entries = get_leaf_entries(node)
        # insert them to the rtree
        for leaf in leaf_entries:
            insert_to_tree(rtree, leaf)


def remove_children(rtree, N):
    children_to_remove = [N]
    while children_to_remove:
        current_child = children_to_remove.pop(0)
        # if the node is internal
        if isinstance(current_child.entries[0], Entry):
            for entry in current_child.entries:
                children_to_remove.append(entry.child)
                rtree.remove(entry.child)


def get_leaf_entries(N):
    leaf_entries = []
    nodes_to_visit = [N]

    while nodes_to_visit:
        current_node = nodes_to_visit.pop()
        if isinstance(current_node.entries[0], LeafEntry):
            for entry in current_node.entries:
                leaf_entries.append(entry)
        # if the node is not leaf, add its children to the  list of nodes to visit
        else:
            for entry in current_node.entries:
                nodes_to_visit.append(entry.child)
    return leaf_entries


def load_rtree_from_xml(file):
    rtree = ET.parse(file)
    root = rtree.getroot()
    nodes = []

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
                entries.append(Entry(rectangle, None))  # create an Entry object and append it to the entries list

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

        Node.set_overflow_treatment_level(nodes[-1].getLevel())  # gets the level of the last node

    return nodes

# ### example
# rtree = load_rtree_from_xml("indexfile.xml")
# delete(rtree, LeafEntry([9,56,41.4867382,26.158758])) # must choose a leaf entry like LeafEntry([block_id, slot, lat, lon])
