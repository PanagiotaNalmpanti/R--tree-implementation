from Node import Node
from Entry import Rectangle, Entry, LeafEntry

# Define LeafEntries
leaf_entry1 = LeafEntry([1, 0, -6.0, -5.0])
leaf_entry2 = LeafEntry([1, 1, -5.0, -3.0])
leaf_entry3 = LeafEntry([1, 2, -3.0, -4.0])
leaf_entry4 = LeafEntry([1, 3, -6.0, 7.0])
leaf_entry5 = LeafEntry([1, 4, 2.0, 3.0])
leaf_entry6 = LeafEntry([1, 5, 4.0, 5.0])
leaf_entry7 = LeafEntry([1, 6, -1.0, 0.0])
leaf_entry8 = LeafEntry([1, 7, 6.0, 8.0])
leaf_entry9 = LeafEntry([1, 8, 0.5, 1.5])
leaf_entry10 = LeafEntry([1, 9, -7.0, -6.0])

# Define Leaf Nodes
leaf_node1 = Node([leaf_entry1, leaf_entry2])
leaf_node2 = Node([leaf_entry3, leaf_entry4])
leaf_node3 = Node([leaf_entry5, leaf_entry6])
leaf_node4 = Node([leaf_entry7, leaf_entry8])
leaf_node5 = Node([leaf_entry9, leaf_entry10])

# Define Rectangles for Leaf Entries
rectangle1 = Rectangle([leaf_entry1.point, leaf_entry2.point])
rectangle2 = Rectangle([leaf_entry3.point, leaf_entry4.point])
rectangle3 = Rectangle([leaf_entry5.point, leaf_entry6.point])
rectangle4 = Rectangle([leaf_entry7.point, leaf_entry8.point])
rectangle5 = Rectangle([leaf_entry9.point, leaf_entry10.point])

# Define Entries with Rectangles and Leaf Nodes
entry1 = Entry(rectangle1, leaf_node1)
entry2 = Entry(rectangle2, leaf_node2)
entry3 = Entry(rectangle3, leaf_node3)
entry4 = Entry(rectangle4, leaf_node4)
entry5 = Entry(rectangle5, leaf_node5)

# Define Internal Node
internal_node1 = Node([entry1, entry2, entry3, entry4, entry5])

# Define Root Rectangle
root_rectangle1 = Rectangle([entry1.rectangle.bottom_left, entry1.rectangle.top_right,
                              entry2.rectangle.bottom_left, entry2.rectangle.top_right,
                              entry3.rectangle.bottom_left, entry3.rectangle.top_right,
                              entry4.rectangle.bottom_left, entry4.rectangle.top_right,
                              entry5.rectangle.bottom_left, entry5.rectangle.top_right])

# Define Root Entry
root_entry1 = Entry(root_rectangle1, internal_node1)

# Define Root Node
root_node = Node([root_entry1])

# Set parent-child relationships
leaf_node1.set_parent(internal_node1, 0)
leaf_node2.set_parent(internal_node1, 1)
leaf_node3.set_parent(internal_node1, 2)
leaf_node4.set_parent(internal_node1, 3)
leaf_node5.set_parent(internal_node1, 4)

internal_node1.set_parent(root_node, 0)

# Set max entries for the root node
Node.set_max_entries(3)

# Create the tree structure
tree = [root_node, internal_node1, leaf_node1, leaf_node2, leaf_node3, leaf_node4, leaf_node5]
print(tree)
