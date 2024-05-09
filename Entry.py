
class Rectangle:
    # find MBR
    def __init__(self, points):
        self.bottom_left = None
        self.top_right = None

        dimensions = len(points[0])
        self.bottom_left = [float('inf')] * dimensions
        self.top_right = [float('-inf')] * dimensions
        for point in points:
            for i in range(dimensions):
                self.bottom_left[i] = min(self.bottom_left[i], point[i])
                self.top_right[i] = max(self.top_right[i], point[i])

    def center(self):
        dimensions = len(self.top_right)
        Cpoint = []
        for i in range(dimensions):
            a = self.top_right[i]
            b = self.bottom_left[i]
            Cpoint.append((a+b)/2)
        return Cpoint


class Entry:
    def __init__(self, rectangle, child):
        self.rectangle = rectangle
        self.child = child

    def set_rectangle(self, points):
        set.rectangle = Rectangle(points)

    def set_child(self, new_child):
        set.child = new_child


class LeafEntry:
    # record from datafile
    def __init__(self, record):
        # record_id is a list that contains the block id and the slot of the record.
        self.record_id = (record[0], record[1])
        self.point = record[2:]

