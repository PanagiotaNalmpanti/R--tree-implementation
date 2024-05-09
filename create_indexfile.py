from Node import Node
from Entry import Rectangle, Entry, LeafEntry

# Define LeafEntries
leaf_entry1 = LeafEntry([1, 0, -6.0, -5.0])
leaf_entry2 = LeafEntry([1, 1, -5.0, -3.0])
leaf_entry3 = LeafEntry([1, 2, -3.0, -4.0])
leaf_entry4 = LeafEntry([1, 3, -6.0, 7.0])

# Define Leaf Nodes
leaf_node1 = Node([leaf_entry1, leaf_entry2])
leaf_node2 = Node([leaf_entry3, leaf_entry4])

# Define Rectangles for Leaf Entries
rectangle1 = Rectangle([leaf_entry1.point, leaf_entry2.point])
rectangle2 = Rectangle([leaf_entry3.point, leaf_entry4.point])

# Define Entries with Rectangles and Leaf Nodes
entry1 = Entry(rectangle1, leaf_node1)
entry2 = Entry(rectangle2, leaf_node2)

# Define Internal Node
internal_node1 = Node([entry1, entry2])

# Define Root Rectangle
root_rectangle1 = Rectangle([entry1.rectangle.bottom_left, entry1.rectangle.top_right,
                              entry2.rectangle.bottom_left, entry2.rectangle.top_right])

# Define Root Entry
root_entry1 = Entry(root_rectangle1, internal_node1)

# Define Root Node
root_node = Node([root_entry1])

# Set parent-child relationships
leaf_node1.set_parent(internal_node1, 0)
leaf_node2.set_parent(internal_node1, 1)

internal_node1.set_parent(root_node, 0)

# Set max entries for the root node
Node.set_max_entries(4)

# Create the tree structure
tree = [root_node, internal_node1, leaf_node1, leaf_node2]
print(tree)