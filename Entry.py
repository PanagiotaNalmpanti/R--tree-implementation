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
            Cpoint.append((a + b) / 2)
        return Cpoint

    def calculate_overlap_enlargement(self, r, index, N):
        # create new rectangle including the points of the current rectangle and the point of the new record
        points_of_new_Rectangle = [self.bottom_left, self.top_right, r.point]
        new_rectangle = Rectangle(points_of_new_Rectangle)

        enlargement = 0
        # iterate over each entry in the node excluding the entry at the specified index. We don't need the overlap with itself.
        for i, entry in enumerate(N.entries):
            if i != index:
                # value represents the contribution of each entry to the enlargement of the new rectangle
                enlargement += entry.rectangle.calculate_value(new_rectangle)
        return enlargement

    def calculate_value(self, other_rectangle):
        overlap_value = 1

        for i in range(len(self.bottom_left_point)):
            # Calculate the overlap along each dimension
            overlap_extent = min(self.top_right_point[i], other_rectangle.top_right_point[i]) - max(
                self.bottom_left_point[i], other_rectangle.bottom_left_point[i])

            # If there's no overlap along any dimension, the overall overlap is 0
            if overlap_extent <= 0:
                return 0
            # Multiply the overlap extent along each dimension to get the total overlap value
            overlap_value *= overlap_extent

        return overlap_value

    def calculate_area_enlargement(self, r):
        # create new rectangle including the points of the current rectangle and the point of the new record
        points_of_new_Rectangle = [self.bottom_left, self.top_right, r.point]
        new_rectangle = Rectangle(points_of_new_Rectangle)

        # area enlargement cost by subtracting the area of the current rectangle from the area of the new rectangle
        before = self.calculate_area()
        after = new_rectangle.calculate_area()
        return after - before

    def calculate_area(self):
        # area of current rectangle
        area = 1
        # calculate the length of the side of the rectangle along each dimension
        for i in range(len(self.top_right)):
            area *= self.top_right[i] - self.bottom_left[i]
        return area


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
