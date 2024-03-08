from src.stack import CStack
import pandas as pd


class CContainerType:
    def __init__(self):
        self.type_name = None
        self.l_c = 0
        self.w_c = 0
        self.h_c = 0
        self.v_c = 0
        self.s_c = 0

    def set_type(self, type_name, l_c, w_c, h_c):
        self.type_name = type_name
        self.l_c = l_c
        self.w_c = w_c
        self.h_c = h_c
        self.v_c = self.l_c * self.w_c * self.h_c
        self.s_c = self.l_c * self.w_c


class CContainer:
    def __init__(self):
        self.c_id = None
        self.type = None
        self.boxes_list = list()  # 装载货物的列表
        self.stacks_list = list()  # 装载stack列表
        self.inside_v = 0  # 已装载的体积
        self.inside_s = 0  # 装载的底面积
        self.inside_s_top = 0  # 顶层货物占据的顶面积

    def set_id(self, id_c):
        self.c_id = id_c

    def set_type(self, type_c):
        self.type = type_c
        # self.type_name.v_b = self.type_name.l_b * self.type_name.w_b * self.type_name.h_b

    def input_stack(self, s: CStack):
        self.stacks_list.append(s)
        self.inside_v += s.value
        self.inside_s += s.lx * s.ly
        for box in s.boxes_list:
            self.boxes_list.append(box)

    def get_container_info(self):
        print("集装箱id号：{}".format(self.c_id))
        print("集装箱型号：{}".format(self.type.type_name))
        print("集装箱长：{:.3f}m，宽：{:.3f}m，高：{:.3f}m，体积：{:.3f}m^3"
              .format(self.type.l_c, self.type.w_c, self.type.h_c, self.type.v_c))

    def get_contain_box_info(self):
        self.get_container_info()
        print("集装箱装载体积：{:.3f}m^3， 满载率：{:.3f}".format(self.inside_v, self.inside_v / self.type.v_c))
        for box in self.boxes_list:
            print("------")
            box.get_box_info()
            box.get_box_location()

    def output_contain_box_solution(self, filename, from_net=0):
        data = pd.DataFrame(
            columns=['box_type', 'box_id', 'l', 'w', 'h', 'top', 'x', 'y', 'z',  'dx', 'dy', 'dz', 'rotate'])
        for idx, box in enumerate(self.boxes_list):
            series = pd.Series({
                'box_type': box.type.type_name,
                'box_id': box.id,
                'l': box.type.l_b, 'w': box.type.w_b, 'h': box.type.h_b, 'top': box.type.top_b,
                'x': round(box.location_left_back_down.x, 3),
                'y': round(box.location_left_back_down.y, 3),
                'z': round(box.location_left_back_down.z, 3),
                'dx': round(box.location_right_front_up.x, 3),
                'dy': round(box.location_right_front_up.y, 3),
                'dz': round(box.location_right_front_up.z, 3),
                'rotate': box.rotate}, name=idx)
            data = data.append(series)
        if from_net == 0:
            data.to_excel("../result/result_files/{}/集装箱{}_型号_{}_装箱方案.xlsx".format(filename, self.c_id, self.type.type_name),
                          index=False, encoding='utf-8')
            return None
        else:
            data.to_excel(
                "./temp/result/result_files/{}/集装箱{}_型号_{}_装箱方案.xlsx".format(filename, self.c_id, self.type.type_name),
                index=False, encoding='utf-8')

            # 将 DataFrame 转换为 HTML 表格字符串
            data_name = "集装箱{}_型号_{}_装箱方案".format(self.c_id, self.type.type_name)
            table_html = f'<h2>{data_name}</h2>' + data.to_html(index=False)
            return table_html
