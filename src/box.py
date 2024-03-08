import math
from src.location import CLocationLeftBackDown, CLocationRightFrontUp


class CBoxType:
    def __init__(self):
        self.type_name = None
        self.l_b = 0
        self.w_b = 0
        self.h_b = 0
        self.s_b = 0
        self.v_b = 0
        self.top_b = 0  # 是否为顶层货品

    def set_type(self, type_name, l_b, w_b, h_b, top_b):
        self.type_name = type_name
        self.l_b = l_b
        self.w_b = w_b
        self.h_b = h_b
        self.top_b = top_b  # 是否为顶层货品
        self.s_b = self.l_b * self.w_b
        self.v_b = self.l_b * self.w_b * self.h_b

    def __eq__(self, other):
        if self.type_name == other.type_name:
            return True
        else:
            return False


class CBox:
    def __init__(self):
        self.id = None
        self.type = None
        self.location_left_back_down = CLocationLeftBackDown()
        self.location_right_front_up = CLocationRightFrontUp()
        self.rotate = 0

    def set_id(self, id_b):
        self.id = id_b

    def set_type(self, type_b):
        self.type = type_b
        # self.type_name.v_b = self.type_name.l_b * self.type_name.w_b * self.type_name.h_b

    def set_rotate(self):
        self.rotate = 1

    def get_box_info(self):
        print("货物id号：{}".format(self.id))
        print("货物型号：{}".format(self.type.type_name))
        print("货物宽：{}mm，长：{}mm，高：{}mm，体积：{:.3f}m^3"
              .format(self.type.w_b, self.type.l_b, self.type.h_b, self.type.v_b / math.pow(1000, 3)))
        if self.type.top_b == 1:
            print("货物是顶层货")

    def set_box_location_left_back_down(self, x, y, z):
        self.location_left_back_down.set_location(x, y, z)

    def set_box_location_right_front_up(self):
        if self.rotate == 1:
            self.location_right_front_up.set_location(
                round(self.location_left_back_down.x + self.type.l_b / 1000, 3),
                round(self.location_left_back_down.y + self.type.w_b / 1000, 3),
                round(self.location_left_back_down.z + self.type.h_b / 1000, 3))
            # self.type.l_b, self.type.w_b = self.type.w_b, self.type.l_b  # 交换l,w
        else:
            self.location_right_front_up.set_location(
                round(self.location_left_back_down.x + self.type.w_b/1000, 3),
                round(self.location_left_back_down.y + self.type.l_b/1000, 3),
                round(self.location_left_back_down.z + self.type.h_b/1000, 3))

    def set_box_location_from_stack(self, s, r, c_id):
        # 左后下
        self.location_left_back_down.x = s.location.x
        self.location_left_back_down.y = s.location.y

        # 右前上
        if r == 0:  # 未旋转
            self.location_right_front_up.x = \
                round(self.location_left_back_down.x + self.type.w_b/1000, 3)
            self.location_right_front_up.y = \
                round(self.location_left_back_down.y + self.type.l_b/1000, 3)
        else:
            self.location_right_front_up.x = \
                round(self.location_left_back_down.x + self.type.l_b/1000, 3)
            self.location_right_front_up.y = \
                round(self.location_left_back_down.y + self.type.w_b/1000, 3)

        # 集装箱编号
        self.set_box_container_id(c_id)

    def set_box_container_id(self, c):
        self.location_left_back_down.container_id = c.c_id
        self.location_right_front_up.container_id = c.c_id

    def get_box_location(self):
        print("货物{}存储的集装箱号：{}".format(self.id, self.location_left_back_down.container_id))
        print("货物{}存储的左后下角位置元组：{}, {}, {}".format(self.id,
                                                  round(self.location_left_back_down.x, 3),
                                                  round(self.location_left_back_down.y, 3),
                                                  round(self.location_left_back_down.z, 3)))
        print("货物{}存储的右前上角位置元组：{}, {}, {}".format(self.id,
                                                  round(self.location_right_front_up.x, 3),
                                                  round(self.location_right_front_up.y, 3),
                                                  round(self.location_right_front_up.z, 3)))
        if self.rotate == 0:
            print(f"货物{self.id}没有平转，即货物宽边平行集装箱宽边（x轴），货物长边平行集装箱长边（y轴）")
        if self.rotate == 1:
            print(f"货物{self.id}需要平转，即货物宽边平行集装箱长边（y轴），货物长边平行集装箱宽边（x轴）")
