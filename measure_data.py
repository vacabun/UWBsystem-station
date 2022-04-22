
class MeasureData:
    def __init__(self, label_address: int, node_address: int, frame_num: int, asctime: str, distance: int):
        self.label_address = label_address
        self.node_address = node_address
        self.frame_num = frame_num
        self.asctime = asctime
        self.distance = distance
