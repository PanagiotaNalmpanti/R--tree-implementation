
from delete import *

# Define LeafEntries
leaf_entry1 = LeafEntry([1, 0, 0, 2])
leaf_entry2 = LeafEntry([1, 1, 1, 1])
leaf_entry3 = LeafEntry([1, 2, -1, -2])

leaf_entry4 = LeafEntry([1, 3, 0, -5])
leaf_entry5 = LeafEntry([1, 4, 2, -5])
leaf_entry6 = LeafEntry([1, 5, 3, -7])

leaf_entry7 = LeafEntry([1, 6, 5, 1])
leaf_entry8 = LeafEntry([1, 7, 5, -4])
leaf_entry9 = LeafEntry([1, 8, 7, -4])

leaf_entry10 = LeafEntry([1, 9, -3, -5])
leaf_entry11 = LeafEntry([1, 10, -6, -4])
leaf_entry12 = LeafEntry([1, 11, -5, -6])

leaf_entry13 = LeafEntry([1, 12, -3, 6])
leaf_entry14 = LeafEntry([1, 13, -4, 8])
leaf_entry15 = LeafEntry([1, 14, -5, 6])

# Define Leaf Nodes
leaf_node1 = Node([leaf_entry1, leaf_entry2, leaf_entry3])
leaf_node2 = Node([leaf_entry7, leaf_entry8, leaf_entry9])
leaf_node3 = Node([leaf_entry4, leaf_entry5, leaf_entry6])
leaf_node4 = Node([leaf_entry10, leaf_entry11, leaf_entry12])
leaf_node5 = Node([leaf_entry13, leaf_entry14, leaf_entry15])

# Define Rectangles for Leaf Entries
rectangle1 = Rectangle([leaf_entry1.point, leaf_entry2.point, leaf_entry3.point])
rectangle2 = Rectangle([leaf_entry7.point, leaf_entry8.point, leaf_entry9.point])
rectangle3 = Rectangle([leaf_entry4.point, leaf_entry5.point, leaf_entry6.point])
rectangle4 = Rectangle([leaf_entry10.point, leaf_entry11.point, leaf_entry12.point])
rectangle5 = Rectangle([leaf_entry13.point, leaf_entry14.point, leaf_entry15.point])

# Define Entries with Rectangles and Leaf Nodes
entry1 = Entry(rectangle1, leaf_node1)
entry2 = Entry(rectangle2, leaf_node2)
entry3 = Entry(rectangle3, leaf_node3)
entry4 = Entry(rectangle4, leaf_node4)
entry5 = Entry(rectangle5, leaf_node5)

# Define Internal Node
internal_node1 = Node([entry1, entry2, entry3])
internal_node2 = Node([entry4, entry5])

# Define Root Rectangle
root_rectangle1 = Rectangle([entry1.rectangle.bottom_left, entry1.rectangle.top_right,
                             entry2.rectangle.bottom_left, entry2.rectangle.top_right,
                             entry3.rectangle.bottom_left, entry3.rectangle.top_right])

root_rectangle2 = Rectangle([entry4.rectangle.bottom_left, entry4.rectangle.top_right,
                             entry5.rectangle.bottom_left, entry5.rectangle.top_right])

# Define Root Entry
root_entry1 = Entry(root_rectangle1, internal_node1)
root_entry2 = Entry(root_rectangle2, internal_node2)

# Define Root Node
root_node = Node([root_entry1, root_entry2])

# Set parent-child relationships
leaf_node1.set_parent(internal_node1, 0)
leaf_node2.set_parent(internal_node1, 1)
leaf_node3.set_parent(internal_node1, 2)
leaf_node4.set_parent(internal_node2, 0)
leaf_node5.set_parent(internal_node1, 1)

internal_node1.set_parent(root_node, 0)
internal_node2.set_parent(root_node, 1)

# Set max entries for the root node
Node.set_max_entries(4)

# Create the tree structure
rtree = [root_node, internal_node1, internal_node2, leaf_node1, leaf_node2, leaf_node3, leaf_node4, leaf_node5]

save_rtree_to_xml(rtree, "indexfile1.xml")
# rtree = load_rtree_from_xml("indexfile1.xml")


### Insert testing

# insert_to_tree(rtree, LeafEntry([1, 20, -3, -1]))
# insert_to_tree(rtree, LeafEntry([1, 30, -4, 1]))
# insert_to_tree(rtree, LeafEntry([1, 40, -4, -6]))
# insert_to_tree(rtree, LeafEntry([1, 50, -7, -7]))
# insert_to_tree(rtree, LeafEntry([1, 60, -6, -2]))
# insert_to_tree(rtree, LeafEntry([1, 70, -8, -2]))
# insert_to_tree(rtree, LeafEntry([1, 80, -9, -3]))
# #
# insert_to_tree(rtree, LeafEntry([1, 90, -4, -4]))
# insert_to_tree(rtree, LeafEntry([1, 90, -7, 1]))
# insert_to_tree(rtree, LeafEntry([1, 90, -6.5, -6]))  # must split here

save_rtree_to_xml(rtree, "indexfile1.xml")

# print rtree
print("max entries = ", Node.max_entries)
for i, n in enumerate(rtree):
    print("node ", i, "level ", n.getLevel())
    if isinstance(n.entries[0], LeafEntry):
        for j, entry in enumerate(n.entries):
            print("     leaf_entry ", j, ": ", entry.point)
    else:
        for j, entry in enumerate(n.entries):
            print("     entry ", j, ": ", entry.rectangle.bottom_left, " ", entry.rectangle.top_right)


### Delete testing

#tree = load_tree_from_xml("indexfile1.xml")
print("max entries = ", Node.max_entries)
print("min entries = ", Node.min_entries)

print("\n")

# print("Tree before deletions: ")
# for i, n in enumerate(rtree):
#     print("node ", i, "level ", n.getLevel())
#     if isinstance(n.entries[0], LeafEntry):
#         for j, entry in enumerate(n.entries):
#             print("     leaf_entry ", j, ": ", entry.point)
#     else:
#         for j, entry in enumerate(n.entries):
#             print("     entry ", j, ": ", entry.rectangle.bottom_left, " ", entry.rectangle.top_right)
#
# print("\n")

delete(rtree, LeafEntry([1, 11, -5, -6]))
delete(rtree, LeafEntry([1, 12, -3, 6]))
delete(rtree, LeafEntry([1, 9, -3, -5]))


# print("Tree after deletions: ")
# for i, n in enumerate(rtree):
#     print("node ", i, "level ", n.getLevel())
#     if isinstance(n.entries[0], LeafEntry):
#         for j, entry in enumerate(n.entries):
#             print("     leaf_entry ", j, ": ", entry.point)
#     else:
#         for j, entry in enumerate(n.entries):
#             print("     entry ", j, ": ", entry.rectangle.bottom_left, " ", entry.rectangle.top_right)

