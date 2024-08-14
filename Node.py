import math

from Entry import LeafEntry


class Node:
    max_entries = 4  # M
    min_entries = math.floor(max_entries * 0.5)  # m = 50% of M
    overflow_treatment_level = 1

    def __init__(self, entries=None, parent=None, parent_slot=None):
        if entries is None:
            self.entries = []
        else:
            self.entries = entries

        if parent is None:
            self.parent = None
            self.parent_slot = None
        else:
            self.parent = parent
            self.parent_slot = parent_slot

    def set_parent(self, parent, parent_slot):
        self.parent = parent
        self.parent_slot = parent_slot

    def set_parent_slot(self, parent_slot):
        self.parent_slot = parent_slot

    def getLevel(self):
        if self.parent is not None:
            return self.parent.getLevel() + 1
        else:
            return 0

    def is_leaf(self):
        if not self.entries:
            return False
        return isinstance(self.entries[0], LeafEntry)

    @classmethod
    def set_max_entries(cls, number):
        cls.max_entries = number
        cls.min_entries = math.floor(number/2.0)

    @classmethod
    def set_overflow_treatment_level(cls, leaf_level):
        cls.overflow_treatment_level = leaf_level

    @classmethod
    def increase_overflow_treatment_level(cls):
        cls.overflow_treatment_level += 1

    # def set_entries(self, entries):
    #     self.entries = entries

    def find_node_level(self):
        if self.parent is not None:
            return self.parent.find_node_level() + 1
        else:
            return 0
