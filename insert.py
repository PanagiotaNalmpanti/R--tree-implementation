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
    else:
        N.entries.append(r)
        # treatment
        calls = 0  # might need to be a parameter
        overflowTreatment(N, rtree, r, calls)
        calls += 1


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

def overflowTreatment(N, rtree, record, calls):
    if N.getLevel() != 0 and calls == 0:
        ReInsert(N)
    else:
        Split(N, Node.min_entries)


def Split(N, min_entries):
    split_axis = ChooseSplitAxis(N.entries, min_entries)
    group1, group2 = ChooseSplitIndex(N.entries, split_axis, min_entries)
    return group1, group2


def ChooseSplitAxis(entries, min_entries):
    min_margin_sum = float('inf')
    split_axis = None
    smargin = 0  # sum

    # check if the node is a leaf
    if isinstance(entries[0], LeafEntry):
        for axis in range(len(entries[0].point)):
            entries.sort(key=lambda entry: entry.point[axis])

            # loop through each possible split point, min_entries is the minimum number of entries required in each group after splitting
            for i in range(min_entries, len(entries) - min_entries+1):
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

    return split_axis # optimal split axis that minimizes the sum of margins for the given entries


def ChooseSplitIndex(entries, split_axis, min_entries):
    min_overlap_value = float('inf')
    min_area_value = float('inf')
    index = None

    # check if the node is a leaf
    if isinstance(entries[0],LeafEntry):
        entries.sort(key=lambda entry: entry.point[split_axis])
        for i in range(min_entries, len(entries) - min_entries + 1):

            #Create rectangles for the two groups of entries using their points
            rect1 = Rectangle([entry.point for entry in entries[:i]])
            rect2 = Rectangle([entry.point for entry in entries[i:]])
            overlap = rect1.calculate_overlap_value(rect2)
            area_sum = rect1.calculate_area()+rect2.calculate_area()

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


def ReInsert(N):
    node_entries = N.entries
    distances = []
    for entry in node_entries:
        distance = N.euclidean_distance(entry.point)
        distances.append((entry, distance))
    distances.sort(key=lambda x: x[1], reversed=True)  # RI2

    p = math.floor(len(node_entries) * 0.5)  # 50% of the entries that exist in node N
    entries_left = node_entries[p:]  # remove the first p entries from N
    N.set_entries(entries_left)  # set the new entries of N
    for entry in N.entries:
        entry.set_rectangle(
            entry.point)  # adjusting the bounding rectangle of N, by adjusting its children's rectangles

    for entry, _ in distances:  # starting from the maximum distance ( = far reinsert)
        insert_to_tree(rtree, entry)



# read the records from datafile
read_blocks = read_blocks_from_datafile("datafile3000.xml")
rtree = insert_one_by_one(read_blocks, Node.max_entries)
