class CLocation:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.z = 0
        self.container_id = None  # 应该存放的集装箱位置

    def set_container_id(self, c_id):
        self.container_id = c_id

    def set_location(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def set_x(self, x):
        self.x = x

    def set_y(self, y):
        self.y = y

    def set_z(self, z):
        self.z = z

    def get_location(self):
        return self.x, self.y, self.z


class CLocationLeftBackDown(CLocation):
    def __init__(self):
        super(CLocationLeftBackDown, self).__init__()


class CLocationRightFrontUp(CLocation):
    def __init__(self):
        super(CLocationRightFrontUp, self).__init__()
