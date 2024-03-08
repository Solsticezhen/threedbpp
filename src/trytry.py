import pandas as pd
import numpy as np
import time
import os

from src.action import find_unsatisfied_box, delete_unsatisfied_box, generate_stacks, input_stack_in_container, draw_packing_result, output_total_info
from src.order import COrder


def optimize(casename, from_net=0):
    # casename = '测试1'
    if from_net == 0:
        # 指定输出目录路径
        directories = ["../result/pictures", "../result/result_files"]
        # 检查目录下是否存在名为 filename的文件夹
        for di in directories:
            folder_path = os.path.join(di, casename)
            if not os.path.exists(folder_path):
                # 如果不存在，则创建文件夹
                os.makedirs(folder_path)
    else:  # 从网络来的
        # 指定输出目录路径
        directories = ["./temp/result/pictures", "./temp/result/result_files"]
        # 检查目录下是否存在名为 filename的文件夹
        for di in directories:
            folder_path = os.path.join(di, casename)
            if not os.path.exists(folder_path):
                # 如果不存在，则创建文件夹
                os.makedirs(folder_path)

    is_solve = 1
    order = COrder(casename, from_net)
    # order.input_container_info_from_terminal()  # 从txt读取
    # order.input_box_info_from_terminal()
    order.input_box_info_from_excel(casename)  # 从标准excel读取
    order.input_container_info_from_excel(casename)
    # order.output_order_info()

    start = time.time()
    c_2d = order.containers_list_2d
    b_2d = order.boxes_list_2d
    b_dict = order.boxes_dict
    c_dict = order.containers_dict
    c_2d_use = order.containers_list_2d_used
    smt = order.smt

    find_box = find_unsatisfied_box(c_2d, b_2d)
    if len(find_box) > 0:
        is_solve = -1  # 存在不满足箱型大小的货物
        if smt == 1:
            print("存在不满足箱型大小的货物，问题不可行")
            # is_solve = 0

    delete_unsatisfied_box(b_2d, b_dict, find_box)

    while sum(b_dict.values()) >= 0:
        if sum(c_dict.values()) == 0:
            is_solve = -2  # 货物过多，集装箱容量不足
            if smt == 0:
                print("集装箱不足！")
            else:
                print("集装箱无法装入，问题不可行")
            break

        max_type_idx, max_layout, max_ratio, max_b_2d_new, max_b_dict_new = \
            generate_stacks(c_2d, b_2d, b_dict, smt)
        # print(order.containers_list_2d[max_type_idx][0].type.type_name)
        # print(max_layout.p)
        # print(max_ratio)
        # print(max_b_dict_new)

        input_stack_in_container(c_2d, c_dict, max_type_idx, max_layout, c_2d_use)

        b_2d = max_b_2d_new
        b_dict = max_b_dict_new

        done = 1
        for i in b_2d:
            if len(i) != 0:
                done = 0
                break
        if done == 1:
            break

    end = time.time()
    duration = end - start  # 计算用时

    # print(order.containers_dict)
    print("求解用时：{:.2f}秒".format(duration))
    tables = []
    images = []
    table = output_total_info(is_solve, c_2d_use, order, duration, casename, from_net)
    tables.append(table)

    if is_solve == 1:
        for c_list in c_2d_use:
            for c in c_list:
                c.get_contain_box_info()
                table_html = c.output_contain_box_solution(casename, from_net)  # 输出集装箱装载情况到excel
                tables.append(table_html)
                print("=====================")

    # 绘制排样图
    if is_solve == 1:
        for c_list in c_2d_use:
            for c in c_list:
                # 绘制排样结果图
                img_data = draw_packing_result(c, order, from_net)
                images.append(img_data)

    return tables, images
# optimize('测试1', from_net=0)
