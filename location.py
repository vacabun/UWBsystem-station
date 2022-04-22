import json
import numpy
import math
class Location:
    def __init__(self):
        self.position = numpy.array([[-0.5, -0.5],
                                     [5.5, -0.5],
                                     [5.5, 5.5],
                                     [-0.5, 5.5]])
        self.distances = []
        self.result = 0
        self.intersection = numpy.array([[0, 0], [0, 0], [0, 0]])

    def intersection(self, i1: int, i2: int):
        r1 = self.distances[i1]
        r2 = self.distance[i2]
        x1 = self.position[i1][0]
        y1 = self.position[i1][1]
        x2 = self.position[i2][0]
        y2 = self.position[i2][1]
        dd = (x1-x2)**2 + (y1-y2)**2

        if dd <= ((r1 + r2) ** 2):
            return [0,0]

    def trilateration_4(self):
        A = []
        B = []
        # trilateration using SVD
        for idx in range(4):
            if idx == 0:  # i:1 j:4
                x_coefficient = self.position[3][0] - self.position[idx][0]  # x3-xidx
                y_coefficient = self.position[3][1] - self.position[idx][1]  # y3-yidx
                b = 1 / 2 * (self.distances[idx] ** 2 - self.distances[3] ** 2 -
                             (x_coefficient ** 2 + y_coefficient ** 2)) \
                    + x_coefficient * self.position[3][0] + y_coefficient * self.position[3][1]
                A.append([x_coefficient, y_coefficient])
                B.append([b])
            else:
                x_coefficient = self.position[0][0] - self.position[idx][0]  # x1-xidx
                y_coefficient = self.position[0][1] - self.position[idx][1]  # y1-yidx
                b = 1 / 2 * (self.distances[idx] ** 2 - self.distances[0] ** 2 -
                             ((self.position[idx][0] - self.position[0][0]) ** 2 + (
                                     self.position[idx][1] - self.position[0][1]) ** 2)) \
                    + x_coefficient * self.position[0][0] + y_coefficient * self.position[0][1]
                A.append([x_coefficient, y_coefficient])
                B.append([b])
        B = numpy.array(B)
        A_pseudo = numpy.linalg.pinv(A)
        self.result = numpy.dot(A_pseudo, B)
        result_x = self.result[0]
        result_y = self.result[1]
        # return x, y position
        return result_x[0], result_y[0]

    def set_distances(self, distances):
        self.distances = distances

    def set_anthor_coor(self, anthor_node_configure):
        for index in range(len(anthor_node_configure)):
            self.position[index][0] = anthor_node_configure[index][0]
            self.position[index][1] = anthor_node_configure[index][1]


