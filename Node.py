import math


class Node:
    max_entries = 4  # M
    min_entries = math.floor(max_entries * 0.5)  # m = 50% of M

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

    @classmethod
    def set_max_entries(cls, number):
        cls.max_entries = number
        cls.min_entries = math.floor(number/2.0)

    def getLevel(self):

        return level

