import math

from src.location import CLocationLeftBackDown
from src.box import CBox


class CStack:
    def __init__(self, top_b: CBox):
        self.id = None
        self.boxes_list = [top_b]
        self.location = None
        self.rotate = 0  # 是否有旋转
        self.top_box = top_b  # 第一层是谁
        self.height = top_b.type.h_b
        self.lx = 0  # 底面长度
        self.ly = 0  # 底面宽度
        self.value = 0  # 有效体积

    def set_id(self, s_id):
        self.id = s_id

    def set_location(self, c, x, y):
        locate = CLocationLeftBackDown()
        locate.set_container_id(c.c_id)
        locate.set_location(x, y, z=0)
        self.location = locate

    def insert_down(self, target_box):
        self.boxes_list.append(target_box)
        self.height += target_box.type.h_b/1000  # 增加stack高度

        # h_tmp = self.height
        # for box in self.boxes_list:
        #     box.set_box_location_left_back_down(0, 0, h_tmp - box.type.h_b)
        #     box.set_box_location_right_front_up()

    def rotate_stack(self):
        self.rotate += 1
        # self.lx, self.ly = self.ly, self.lx
        for box in self.boxes_list:
            box.set_rotate()

    def cal_value(self):
        self.lx = self.boxes_list[-1].type.w_b / 1000
        self.ly = self.boxes_list[-1].type.l_b / 1000
        for box in self.boxes_list:
            self.value += box.type.v_b / math.pow(1000, 3)

    def get_info(self):
        for box in self.boxes_list:
            box.get_box_info()
            box.get_box_location()
        print()

    # def choose_top_level(self, c_type, containers_list, boxes_list_unload):
    #     """
    #     选择堆栈的第一个箱子（放在最顶部）
    #     :param c_type:
    #     :param containers_list:
    #     :param boxes_list_unload:
    #     :return:
    #     """
    #     if len(boxes_list_unload) == 0:
    #         print("没有剩余货物了，堆叠生成结束")
    #         return False
    #
    #     find_top_box = 0  # 是否还存在顶层物品作为堆栈的顶层
    #     top_box_possible = None
    #     min_s = 1e6
    #     for box in boxes_list_unload:
    #         if box.type.top_b == 0:  # 不是顶层货品，记录其底面积情况
    #             if box.type.l_b * box.type.w_b < min_s and \
    #                     box.type.h_b < containers_list[c_type][0].type.h_c:
    #                 top_box_possible = box
    #                 min_s = box.type.l_b * box.type.w_b
    #                 continue
    #         if box.type.h_b < containers_list[c_type][0].type.h_c:
    #             # 有顶层货品，直接生成堆栈
    #             top_box_possible = box
    #             find_top_box = 1
    #             break
    #
    #     if top_box_possible is not None:
    #         # 如果不以顶层物品作为堆栈的顶层，寻找最小面积的物品作为顶层
    #         self.boxes_list_2d.append(top_box_possible)  # 最顶层的货
    #         boxes_list_unload.remove(top_box_possible)  # 货物列表删去这个货
    #     else:
    #         print("出错！找不到箱子做堆栈了！")
    #         return False

    # def create_total_stack(self, c_type, containers_list, boxes_list_unload):
    #     if len(self.boxes_list_2d) == 0:
    #         print("装入错误！")
    #         return False
    #
    #     h_limit = containers_list[c_type][0].type.h_c
    #     h = self.boxes_list_2d[0].type.h_b
    #
    #     while h_limit > h:
    #         s_up = cal_s(self.boxes_list_2d)
    #         box_type_count = dict()  # 嵌套字典：{货物类型1：{底面积：xx, 余数：xx}, xxx}
    #         for box in boxes_list_unload:
    #             box_s = box.type.s_b
    #             if box.type not in list(box_type_count.keys()):
    #                 inner_dict = {'box_s_total': box_s, 'count': 1}
    #                 box_type_count[box.type] = inner_dict
    #             else:
    #                 box_type_count[box.type]['box_s_total'] += box_s
    #                 box_type_count[box.type]['count'] += 1
