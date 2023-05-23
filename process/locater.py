import json
from re import I
import numpy
import math
from typedef import position


class locater:
    def __init__(self) -> None:
        self.anthor_pose_map = {}
        with open("../anthor_3d.json", 'r') as load_f:
            anthors = json.load(load_f)
            for item in anthors:
                self.anthor_pose_map[item['address']] = position(
                    item['x'], item['y'], item['z'])

    def __init__(self, anthor_pose_map) -> None:
        self.anthor_pose_map = anthor_pose_map

    def locate(effective_landmark_indexes, distances):
        pass
