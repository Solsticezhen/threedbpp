import copy
import pandas as pd
import numpy as np

from src.container import CContainer, CContainerType
from src.box import CBox, CBoxType


# 录入型号信息
def generate_types_from_txt():
    with open('./data/types.txt', 'r', encoding='utf-8') as data:
        lines = data.readlines()
        data.close()

    c_types = []
    b_types = []

    for line in lines[1:4]:
        info = line.strip("\n").split(" ")
        l = float(info[1])
        w = float(info[2])
        h = float(info[3])
        c_type = CContainerType()
        c_type.set_type(info[0], l, w, h)
        c_types.append(c_type)

        # container = CContainer()
        # container.set_type(c_type)
        # container.get_container_info()

    for line in lines[7:]:
        info = line.strip("\n").split(" ")
        l = float(info[1])
        w = float(info[2])
        h = float(info[3])
        top = int(info[-1])
        b_type = CBoxType()
        b_type.set_type(info[0], l, w, h, top)
        b_types.append(b_type)

        # box = CBox()
        # box.set_type(b_type)
        # box.get_box_info()
    return c_types, b_types


def generate_types_from_excel(filename, from_net):
    if from_net == 0:
        c_data = pd.read_excel(f'../data/{filename}/containers_info.xlsx', index_col=0)
        b_data = pd.read_excel(f'../data/{filename}/boxes_info.xlsx', index_col=0)
    else:
        c_data = pd.read_excel(f'./temp/data/{filename}/containers_info.xlsx', index_col=0)
        b_data = pd.read_excel(f'./temp/data/{filename}/boxes_info.xlsx', index_col=0)
    c_types = []
    b_types = []
    for idx, c_name in enumerate(c_data.index.values):
        l = float(c_data.loc[c_name, 'l'])
        w = float(c_data.loc[c_name, 'w'])
        h = float(c_data.loc[c_name, 'h'])
        c_type = CContainerType()
        c_type.set_type(c_name, l, w, h)
        c_types.append(c_type)

    for idx, b_name in enumerate(b_data.index.values):
        l = float(b_data.loc[b_name, 'l'])
        w = float(b_data.loc[b_name, 'w'])
        h = float(b_data.loc[b_name, 'h'])
        top = float(b_data.loc[b_name, 'top'])
        b_type = CBoxType()
        b_type.set_type(b_name, l, w, h, top)
        b_types.append(b_type)
    return c_types, b_types


# order
class COrder:
    def __init__(self, file, from_net):
        self.containers_list_2d = []
        self.containers_list_2d_used = []
        self.boxes_list_2d = []
        self.containers_dict = dict()
        self.boxes_dict = dict()
        # self.containers_types, self.boxes_types = generate_types_from_txt()
        self.containers_types, self.boxes_types = generate_types_from_excel(filename=file, from_net=from_net)
        self.smt = 0
        self.filename = file
        self.from_net = from_net  # 是否从网络来的

        # 个数字典
        for idx, c in enumerate(self.containers_types):
            self.containers_dict[c.type_name] = 0
        for idx, b in enumerate(self.boxes_types):
            self.boxes_dict[b.type_name] = 0

    def input_container_info_from_terminal(self):
        print("=====================请输入集装箱需求信息=====================")
        print("输入0：解决装箱可行性问题")
        print("输入1：解决单箱可行性问题")
        self.smt = int(input())

        if self.smt == 0:  # 装箱可行性问题
            print("----输入集装箱数量信息----")
            c_id = 0
            for idx, c_type in enumerate(self.containers_types):
                print("集装箱型号：{} 的个数：".format(c_type.type_name))
                c_num = int(input())
                # 字典记录
                self.containers_dict[c_type.type_name] = c_num

                # 列表拼接
                containers_list = []
                for i in range(c_num):
                    c = CContainer()
                    c.set_type(c_type)
                    c.set_id(c_id)
                    c_id += 1
                    containers_list.append(c)
                self.containers_list_2d.append(containers_list)
                self.containers_list_2d_used.append([])

        else:  # 单箱可行性问题
            print("------以下解决单箱可行性问题------")
            for idx, c_type in enumerate(self.containers_types):
                print(f"输入数字 {idx} 表示：使用1个集装箱，型号为：{c_type.type_name}")
            print("请输入数字：")
            c_id = int(input())

            for idx, c_type in enumerate(self.containers_types):
                if idx == c_id:
                    self.containers_dict[c_type.type_name] = 1
                    # 列表拼接
                    containers_list = []
                    c = CContainer()
                    c.set_type(c_type)
                    c.set_id(0)
                    containers_list.append(c)
                else:
                    self.containers_dict[c_type.type_name] = 0
                    containers_list = []

                self.containers_list_2d.append(containers_list)
                self.containers_list_2d_used.append([])

    def input_container_info_from_excel(self, filename):
        if self.from_net == 0:
            c_data = pd.read_excel(f'../data/{filename}/containers_info.xlsx', index_col=0)
        else:
            c_data = pd.read_excel(f'./temp/data/{filename}/containers_info.xlsx', index_col=0)

        c_id = 0
        for idx, c_type in enumerate(self.containers_types):
            c_num = int(c_data.loc[c_type.type_name, 'num'])
            # 字典记录
            self.containers_dict[c_type.type_name] = c_num
            # 列表拼接
            containers_list = []
            for i in range(c_num):
                c = CContainer()
                c.set_type(c_type)
                c.set_id(c_id)
                c_id += 1
                containers_list.append(c)
            self.containers_list_2d.append(containers_list)
            self.containers_list_2d_used.append([])

        if sum(self.containers_dict.values()) == 1:  # 解决单箱可行性问题
            self.smt = 1

    def input_box_info_from_terminal(self):
        print("=====================请输入货物需求信息=====================")
        b_id = 0
        for idx, b_type in enumerate(self.boxes_types):
            print("货物类别：{} 的个数：".format(b_type.type_name))
            b_num = int(input())
            # 字典记录
            self.boxes_dict[b_type.type_name] = b_num

            # 列表拼接
            boxes_list = []
            for i in range(b_num):
                b = CBox()
                b.set_type(b_type)
                b.set_id(b_id)
                b_id += 1
                boxes_list.append(b)
                # b.set_id(self.boxes_list_2d.index(b))
            self.boxes_list_2d.append(boxes_list)

        # for b in self.boxes_list_2d:
        #     b.set_id(self.boxes_list_2d.index(b))

    def input_box_info_from_excel(self, filename):
        if self.from_net == 0:
            b_data = pd.read_excel(f'../data/{filename}/boxes_info.xlsx', index_col=0)
        else:
            b_data = pd.read_excel(f'./temp/data/{filename}/boxes_info.xlsx', index_col=0)

        b_id = 0
        for idx, b_type in enumerate(self.boxes_types):
            b_num = int(b_data.loc[b_type.type_name, 'num'])
            # 字典记录
            self.boxes_dict[b_type.type_name] = b_num

            # 列表拼接
            boxes_list = []
            for i in range(b_num):
                b = CBox()
                b.set_type(b_type)
                b.set_id(b_id)
                b_id += 1
                boxes_list.append(b)
                # b.set_id(self.boxes_list_2d.index(b))
            self.boxes_list_2d.append(boxes_list)

    def output_order_info(self):
        # 信息输出
        for c_list in self.containers_list_2d:
            for c in c_list:
                c.get_container_info()
        for b_list in self.boxes_list_2d:
            for b in b_list:
                b.get_box_info()
                b.get_box_location()
