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
    Node.set_overflow_treatment_level(1)
    root = Node()
    rtree.append(root)
    Node.set_max_entries(num_of_entries)
    for block in blocks:
        for record in block:
            r = LeafEntry(record)
            insert_to_tree(rtree, r)
    return rtree


def insert_to_tree(rtree, r):
    N = ChooseSubtree(rtree, r)

    # If N can take another entry
    if len(N.entries) < Node.max_entries:
        N.entries.append(r)
        adjust_rectangles(N)
    else:
        N.entries.append(r)
        # treatment
        level = N.getLevel()
        overflowTreatment(N, rtree, level)


def ChooseSubtree(rtree, r):
    N = rtree[0]

    # if root is empty return it
    if len(N.entries) == 0:
        return N

    # while node N is not a LeafEntry instance
    while not isinstance(N.entries[0], LeafEntry):
        # check if N points to leafs
        if isinstance(N.entries[0].child.entries[0], LeafEntry):
            # determine minimum overlap cost
            min_overlap_cost = float('inf')
            min_area_cost = float('inf')
            chosen = None
            # for every entry in node
            for i, entry in enumerate(N.entries):
                overlap_enlargement = entry.rectangle.calculate_overlap_enlargement(r, i, N)
                area_enlargement = entry.rectangle.calculate_area_enlargement(r)

                if overlap_enlargement < min_overlap_cost or (
                        overlap_enlargement == min_overlap_cost and area_enlargement < min_area_cost):
                    min_overlap_cost = overlap_enlargement
                    min_area_cost = area_enlargement
                    chosen = entry

        # children of N is not leafs
        else:
            min_overlap_cost = float('inf')
            min_area_cost = float('inf')
            chosen = None

            for entry in N.entries:
                area_enlargement = entry.rectangle.calculate_area_enlargement(r)
                new_area = area_enlargement + entry.rectangle.calculate_area()

                if area_enlargement < min_area_cost or (area_enlargement == min_area_cost and new_area < min_area):
                    min_area_cost = area_enlargement
                    min_area = new_area
                    chosen = entry
        N = chosen.child
    return N  # This is the suitable leaf node for the new leaf entry = record to be inserted


def overflowTreatment(N, rtree, level):
    if level == 0:
        # Split root
        entry_group1, entry_group2 = Split(N, Node.min_entries)

        new_node1 = Node(entry_group1)
        new_node2 = Node(entry_group2)

        # if the root has leaf entries
        if isinstance(entry_group1[0], LeafEntry):

            rect1 = Rectangle([entry.point for entry in entry_group1])
            rect2 = Rectangle([entry.point for entry in entry_group2])
            root_entry1 = Entry(rect1, new_node1)
            root_entry2 = Entry(rect2, new_node2)

            # updates
            new_root = Node([root_entry1, root_entry2])
            new_node1.set_parent(new_root, 0)
            new_node2. set_parent(new_root, 1)

        else:

            rect1_points = []
            for entry in entry_group1:
                rect1_points.append(entry.rectangle.top_right_point)
                rect1_points.append(entry.rectangle.bottom_left_point)
            rect1 = Rectangle(rect1_points)
            root_entry1 = Entry(rect1, new_node1)

            rect2_points = []
            for entry in entry_group2:
                rect2_points.append(entry.rectangle.top_right_point)
                rect2_points.append(entry.rectangle.bottom_left_point)
            rect2 = Rectangle(rect2_points)
            root_entry2 = Entry(rect2, new_node2)

            new_root = Node([root_entry1, root_entry2])
            new_node1.set_parent(new_root, 0)
            new_node2.set_parent(new_root, 1)

            # set the new nodes as parent of the children that were assigned to each of them
            for i, entry in enumerate(new_node1.entries):
                entry.child.set_parent(new_node1, i)
            for i, entry in enumerate(new_node2.entries):
                entry.child.set_parent(new_node2, i)

        rtree.remove(N)
        rtree.insert(0, new_root)
        rtree.insert(1, new_node1)
        rtree.insert(2, new_node2)

    elif level == Node.overflow_treatment_level:
        # ReInsert
        Node.increase_overflow_treatment_level()
        ReInsert(rtree, N)
    else:
        # Split node
        entry_group1, entry_group2 = Split(N, Node.min_entries)
        new_node1 = Node(entry_group1)
        new_node2 = Node(entry_group2)

        if isinstance(entry_group1[0], LeafEntry):
            # Split leaf
            rect1 = Rectangle([entry.point for entry in entry_group1])
            internal_entry1 = Entry(rect1, new_node1)
            rect2 = Rectangle([entry.point for entry in entry_group2])
            internal_entry2 = Entry(rect2, new_node2)

            N.parent.entries.remove(N.parent.entries[N.parent_slot])
            N.parent.entries.insert(N.parent_slot, internal_entry1)
            N.parent.entries.insert(N.parent_slot + 1, internal_entry2)

            new_node1.set_parent(N.parent, N.parent.entries.index(internal_entry1))
            new_node2.set_parent(N.parent, N.parent.entries.index(internal_entry2))

            for i, entry in enumerate(N.parent.entries):
                entry.child.set_parent_slot(i)

            # replace the old with the new nodes
            replace_index = rtree.index(N)
            rtree.insert(replace_index, new_node1)
            rtree.insert(replace_index + 1, new_node2)
            rtree.remove(N)

            # check if the parent has overflown
            if len(N.parent.entries) > Node.max_entries:
                overflowTreatment(N.parent, rtree, level-1)
            else:
                adjust_rectangles(N.parent)

        else:
            # Split internal
            rect1_points = []
            for entry in entry_group1:
                rect1_points.append(entry.rectangle.top_right_point)
                rect1_points.append(entry.rectangle.bottom_left_point)
            rect1 = Rectangle(rect1_points)
            internal_entry1 = Entry(rect1, new_node1)

            rect2_points = []
            for entry in entry_group2:
                rect2_points.append(entry.rectangle.top_right_point)
                rect2_points.append(entry.rectangle.bottom_left_point)
            rect2 = Rectangle(rect2_points)
            internal_entry2 = Entry(rect2, new_node2)

            N.parent.entries.remove(N.parent.entries[N.parent_slot])
            N.parent.entries.insert(N.parent_slot, internal_entry1)
            N.parent.entries.insert(N.parent_slot + 1, internal_entry2)

            new_node1.set_parent(N.parent, N.parent.entries.index(internal_entry1))
            new_node2.set_parent(N.parent, N.parent.entries.index(internal_entry2))

            # update parent slot for all children of the parent node that was expanded
            for i, entry in enumerate(N.parent.entries):
                entry.child.set_parent_slot(i)

            # update parent slot for all children of the new nodes
            for i, entry in enumerate(new_node1.entries):
                entry.child.set_parent(new_node1, i)
            for i, entry in enumerate(new_node2.entries):
                entry.child.set_parent(new_node2, i)

            # replace the old node with the new nodes
            replace_index = rtree(N)
            rtree.insert(replace_index, new_node1)
            rtree.insert(replace_index + 1, new_node2)
            rtree.remove(N)

            # check if the parent has overflown
            if len(N.parent.entries) > Node.max_entries:
                overflowTreatment(new_node1.parent, rtree, level-1)
            else:
                adjust_rectangles(new_node1.parent)


def Split(N, min_entries):
    split_axis = ChooseSplitAxis(N.entries, min_entries)
    group1, group2 = ChooseSplitIndex(N.entries, split_axis, min_entries)
    return group1, group2


def ReInsert(rtree, N):
    distances = []
    for entry in N.entries:
        distance = N.rectangle.euclidean_distance(entry.point)
        distances.append((entry, distance))
    distances.sort(key=lambda x: x[1], reversed=True)  # RI2

    p = int(round(0.3 * Node.max_entries))  # 30% of the entries that exist in node N
    for i in range(p):
        # remove the first p entries
        N.entries.remove(distances[i][0])

    # adjust the BR of the node
    adjust_rectangles(N)

    # reinsert the removed entries
    for i in range(p):
        insert_to_tree(rtree, distances[i][0])


def adjust_rectangles(N):
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
                new_points.append(entry.rectangle.bottom_left_point)
                new_points.append(entry.rectangle.top_right_point)

        # update the MBR of the parent entry
        N.parent.entries[N.parent_slot].set_rectangle(new_points)

        # move up to the parent node
        N = N.parent


def ChooseSplitAxis(entries, min_entries):
    min_margin_sum = float('inf')
    split_axis = None
    smargin = 0  # sum

    # check if the node is a leaf
    if isinstance(entries[0], LeafEntry):
        for axis in range(len(entries[0].point)):
            entries.sort(key=lambda entry: entry.point[axis])

            # loop through each possible split point, min_entries is the minimum number of entries required in each group after splitting
            for i in range(min_entries, len(entries) - min_entries + 1):
                # Create a rectangle from the points of the entries in each group
                rect1 = Rectangle([entry.point for entry in entries[:i]])
                rect2 = Rectangle([entry.point for entry in entries[i:]])
                smargin += rect1.calculate_margin() + rect2.calculate_margin()

            # update min sum margin
            if smargin < min_margin_sum:
                min_margin_sum = smargin
                split_axis = axis

    else:
        # Loop through each axis based on the dimensionality of the bounding rectangles of the entries
        for axis in range(len(entries[0].rectangle.bottom_left_point)):
            entries.sort(key=lambda entry: entry.rectangle.bottom_left_point[axis])

            # Loop through each possible split point
            for i in range(min_entries, len(entries) - min_entries + 1):
                # create a rectangle by combining the BR of the entries in each group
                rect1_points = []
                for entry in entries[:i]:
                    rect1_points.append(entry.rectangle.bottom_left_point)
                    rect1_points.append(entry.rectangle.top_right_point)
                rect1 = Rectangle(rect1_points)

                rect2_points = []
                for entry in entries[i:]:
                    rect2_points.append(entry.rectangle.bottom_left_point)
                    rect2_points.append(entry.rectangle.top_right_point)
                rect2 = Rectangle(rect2_points)

                smargin += rect1.calculate_margin() + rect2.calculate_margin()

            # select the best partition based on the sum of the MBRs margins
            if smargin < min_margin_sum:
                min_margin_sum = smargin
                split_axis = axis

    return split_axis  # optimal split axis that minimizes the sum of margins for the given entries


def ChooseSplitIndex(entries, split_axis, min_entries):
    min_overlap_value = float('inf')
    min_area_value = float('inf')
    index = None

    # check if the node is a leaf
    if isinstance(entries[0], LeafEntry):
        entries.sort(key=lambda entry: entry.point[split_axis])
        for i in range(min_entries, len(entries) - min_entries + 1):

            # Create rectangles for the two groups of entries using their points
            rect1 = Rectangle([entry.point for entry in entries[:i]])
            rect2 = Rectangle([entry.point for entry in entries[i:]])
            overlap = rect1.calculate_overlap_value(rect2)
            area_sum = rect1.calculate_area() + rect2.calculate_area()

            if overlap < min_overlap_value or (overlap == min_overlap_value and area_sum < min_area_value):
                min_overlap_value = overlap
                min_area_value = area_sum
                chosen_index = i

    else:
        entries.sort(key=lambda entry: entry.rectangle.bottom_left_point[split_axis])
        for i in range(min_entries, len(entries) - min_entries + 1):
            # Create rectangles for the two groups of entries using the bottom-left and top-right points of their BRs
            rect1_points = []
            for entry in entries[:i]:
                rect1_points.append(entry.rectangle.bottom_left_point)
                rect1_points.append(entry.rectangle.top_right_point)
            rect1 = Rectangle(rect1_points)

            rect2_points = []
            for entry in entries[i:]:
                rect2_points.append(entry.rectangle.bottom_left_point)
                rect2_points.append(entry.rectangle.top_right_point)
            rect2 = Rectangle(rect2_points)

            overlap = rect1.calculate_overlap_value(rect2)
            area_sum = rect1.calculate_area() + rect2.calculate_area()

            # Update if the current split results in a lower overlap value or, in case of a tie, a lower area sum
            if overlap < min_overlap_value or (overlap == min_overlap_value and area_sum < min_area_value):
                min_overlap_value = overlap
                min_area_value = area_sum
                chosen_index = i

    return entries[:chosen_index], entries[chosen_index:]





# read the records from datafile
read_blocks = read_blocks_from_datafile("datafile3000.xml")
rtree = insert_one_by_one(read_blocks, Node.max_entries)
