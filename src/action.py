import base64
import copy
import io
import math
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from mpl_toolkits import mplot3d
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import seaborn as sns
from pylab import mpl
# 设置显示中文字体
mpl.rcParams["font.sans-serif"] = ["SimHei"]
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
import matplotlib
matplotlib.use('Agg')  # 使用无界面后端，例如Agg

from src.container import CContainer
from src.box import CBox
from src.order import COrder
from src.stack import CStack
# from src.twodbpp import CAlgorithm2DBPP
from src.twodbpp_scip import CAlgorithm2DBPP
from src.layout import CLayout


stack_s_use_ratio = 0.6  # stack的面积利用率


def find_unsatisfied_box(c_2d, b_2d):  # 识别超长超宽超高货物，并作删除处理
    find_box = []
    c_l, c_w, c_h, c_s = [], [], [], []

    for c_list in c_2d:
        if len(c_list) == 0:
            continue
        c_l.append(c_list[0].type.l_c)
        c_w.append(c_list[0].type.w_c)
        c_h.append(c_list[0].type.h_c)
        c_s.append(c_list[0].type.l_c * c_list[0].type.w_c)

    for b_idx, b_list in enumerate(b_2d):
        if len(b_list) == 0:
            continue
        max_lw = max(b_list[0].type.l_b, b_list[0].type.w_b) / 1000

        if max_lw > max(max(c_l), max(c_w)):
            print(f"货物类别：{b_list[0].type.type_name} 超长")
            find_box.append(b_idx)
            continue

        if b_list[0].type.h_b/1000 > max(c_h):
            print(f"货物类别：{b_list[0].type.type_name} 超高")
            find_box.append(b_idx)
            continue

        if b_list[0].type.l_b/1000 * b_list[0].type.w_b/1000 > max(c_s):
            print(f"货物类别：{b_list[0].type.type_name} 超底面积")
            find_box.append(b_idx)
            continue

    if len(find_box) != 0:
        print("有不符合全部箱型的货物类别")
    return find_box


def delete_unsatisfied_box(b_2d, b_dict, find_box):
    if len(find_box) == 0:
        return 1

    for idx, b_idx in enumerate(find_box):
        b_name = b_2d[b_idx][0].type.type_name
        b_dict[b_name] = 0
        b_2d[b_idx].clear()
        print(f"货物类别：{b_name} 已移除")


def input_box(c: CContainer, b: CBox):
    """
    给集装箱c装入一个货物b
    :param c:
    :param b:
    :return:
    """
    box = b
    if c.inside_v + box.type.v_b > c.type.v_b:  # 体积不满足
        print("集装箱已超载！")
        return False
    if c.inside_s + box.type.l_b * box.type.w_b > c.type.l_b * c.type.w_b:  # 不能堆在底面
        if box.type.top_b == 1:  # 顶层货物
            if c.inside_s_top + box.type.l_b * box.type.w_b > c.type.l_b * c.type.w_b:  # 顶层货物不能放完
                print("顶层货物超载！")
                return False
    c.boxes_list.append(box)


def check_stopping_generate(b_2d: list):
    is_done = 1
    for i in b_2d:
        if len(i) != 0:
            is_done = 0
            break
    if is_done == 1:
        print("所有的货类均已放置完毕，可终止stack的生成过程")
    return is_done


def update_boxes_dict(box: CBox, b_dict: dict):
    b_dict[box.type.type_name] -= 1


def update_containers_dict(container: CContainer, c_dict: dict):
    c_dict[container.type.type_name] -= 1


def cal_box_s(boxes_list):
    # 记录各类的底面情况
    s_list = []
    l_list = []
    w_list = []
    for idx, b_list in enumerate(boxes_list):
        if type(b_list) == list:
            if len(b_list) == 0:  # 没有该类货物了
                s_list.append(0)
                l_list.append(0)
                w_list.append(0)
            else:
                s_list.append(b_list[0].type.s_b)
                l_list.append(b_list[0].type.l_b)
                w_list.append(b_list[0].type.w_b)
        else:
            s_list.append(b_list.type.s_b)
            l_list.append(b_list.type.l_b)
            w_list.append(b_list.type.w_b)
    return s_list, l_list, w_list


def generate_stacks_for_one_container(c, b_2d, b_dict):
    stacks_tmp = []
    boxes_list_unload = copy.deepcopy(b_2d)
    boxes_dict = copy.deepcopy(b_dict)

    while True:
        stack_tmp = choose_top_level_for_stack(c, boxes_list_unload, boxes_dict)

        if stack_tmp is False:
            print("终止stack的生成过程")
            break
        if stack_tmp is None:
            continue

        create_total_stack(stack_tmp, c, boxes_list_unload, boxes_dict)
        h_top = stack_tmp.height

        for box in stack_tmp.boxes_list:
            box.set_box_location_left_back_down(0, 0, h_top - box.type.h_b/1000)
            box.set_box_location_right_front_up()
            h_top -= box.type.h_b/1000
        stacks_tmp.append(stack_tmp)
    # if sum(boxes_dict.values()) == 0:
    return stacks_tmp


def calculate_layout_cost(c, stacks_tmp, smt=0):
    if len(stacks_tmp) != 0:
        alg = CAlgorithm2DBPP(c, stacks_tmp, smt)
        p, x, y, r, obj = alg.solve_by_scip()
        # print(x)
        # print(y)
        # print(r)
        layout = CLayout(stacks_tmp, p, x, y, r)
        ratio = obj / c.type.v_c  # 箱子的满载率
        return layout, ratio, obj
    else:
        print("无stack生成，运行错误")
        return None, None, None


def delete_box_in_list(box, b_2d):
    box_target = None
    ls_target = None
    for idx, b_list in enumerate(b_2d):
        if len(b_list) == 0:
            continue
        if b_list[0].type.type_name != box.type.type_name:
            continue

        for b2 in b_list:
            if b2.id != box.id:
                continue
            box_target = b2
            break
        ls_target = idx
        break

    if ls_target is not None and box_target is not None:
        b_2d[ls_target].remove(box_target)
    else:
        print("装入stack后更新box_list出错！")
        return False


def update_boxes_list_and_dict(stacks_tmp, layout, b_2d, boxes_dict):
    for idx, s in enumerate(stacks_tmp):
        if layout.p[idx] == 1:
            # print(s.value)
            for box in s.boxes_list:
                delete_box_in_list(box, b_2d)
                # update box_dict
                update_boxes_dict(box, boxes_dict)


def choose_top_level_for_stack(c: CContainer, boxes_list_unload: list, boxes_dict: dict):
    """
    根据是否为顶层货品，以及底面积大小，选择堆栈的第一层的箱子（放在最顶部）
    :param c:
    :param boxes_list_unload:
    :param boxes_dict:
    :return:
    """
    is_done = check_stopping_generate(boxes_list_unload)  # 检查一次
    if is_done == 1:
        return False

    if c is None:
        print("没有这个类型的集装箱")
        return False

    # c = containers_list[c_type][0]
    find_top_box = 0  # 是否还存在顶层物品作为堆栈的顶层
    top_box_possible = None

    if len(boxes_list_unload[-1]) > 0 and boxes_list_unload[-1][0].type.h_b/1000 < c.type.h_c:
        find_top_box = 1
        b_type = -1
        top_box_possible = boxes_list_unload[b_type][0]

    else:  # 若无顶层货物，则选择最小面积货物作为第一层
        s_list, l_list, w_list = cal_box_s(boxes_list_unload)

        try:
            min_gt_0 = min(num for num in s_list if num > 0)  # 找最小底面积
            b_type = s_list.index(min_gt_0)

            if boxes_list_unload[b_type][0].type.h_b/1000 < c.type.h_c and \
                    max(boxes_list_unload[b_type][0].type.l_b,
                        boxes_list_unload[b_type][0].type.w_b)/1000 < max(c.type.l_c, c.type.w_c):
                top_box_possible = boxes_list_unload[b_type][0]
            else:
                # print(boxes_list_unload[b_type][0].type.h_b/1000)
                print("货类型号：{} 无法装入".format(boxes_list_unload[b_type][0].type.type_name))
                del boxes_dict[boxes_list_unload[b_type][0].type.type_name]
                boxes_list_unload.remove(boxes_list_unload[b_type])
                print("已删除无法装入货类的型号")
                return None
        except:
            print("所有货类均已放置")
            return False

    # 先尽可能全部生成
    # if c.inside_s + top_box_possible.type.s_b > c.type.s_c:
    #     print("箱子已满，无法再加入新的堆栈了")
    #     return False

    stack = CStack(top_box_possible)  # 新的堆栈
    stack.height = top_box_possible.type.h_b/1000  # 后续的height别再除1000了
    boxes_list_unload[b_type].remove(top_box_possible)  # 从原列表中移除
    update_boxes_dict(top_box_possible, boxes_dict)  # 更新货物数量字典
    # stack.get_info()

    return stack  # 返回新的堆栈


def find_closest_value(arr: list, target: int):
    arr2 = [num for num in arr if num >= target]
    return min(arr2)


def find_closest_pair(a: int, b: int, a_list: list, b_list: list, box_list_unload, stack, h_limit):
    """
    找到和a,b最接近的、≥a和b的，在a_list和b_list的一对数
    :param h_limit:
    :param stack:
    :param box_list_unload:
    :param a:
    :param b:
    :param a_list:
    :param b_list:
    :return:
    """
    min_diff = float('inf')
    closest_pair = None
    closest_pair_index = None

    for i in range(len(a_list)):
        if len(box_list_unload[i]) == 0:
            continue

        if box_list_unload[i][0].type.top_b == 1:
            continue

        if box_list_unload[i][0].type.h_b/1000 + stack.height > h_limit:
            continue

        if a_list[i] >= a and b_list[i] >= b:
            diff_a = a_list[i] - a
            diff_b = b_list[i] - b
            total_diff = abs(diff_a) + abs(diff_b)
            if total_diff <= min_diff:
                min_diff = total_diff
                closest_pair = (a_list[i], b_list[i])
                closest_pair_index = i

    if closest_pair is not None:
        return closest_pair, closest_pair_index
    else:
        return None, None


def select_down_level(l_up, w_up, boxes_list_unload, stack: CStack, h_limit, boxes_dict):
    """
    找到最贴近栈低尺寸的box入栈，需要满足栈的高度约束
    注意，应在满足堆高条件下，再尽可能提高面积利用率，
    若上层与下层为不同货类，上层竹竿型、下层扁平型，上下面积相差大，则需要判断是否叠放
    即，计算下层货类自己堆叠的货物余量（mod求余数）。若剩余余量恰能满足，则进行叠放
    否则，将上层竹竿型货物单独放置成一个stack，以便后续2dbpp插空，提高面积利用效率。
    :param boxes_dict:
    :param h_limit:
    :param l_up:
    :param w_up:
    :param boxes_list_unload:
    :param stack:
    :return:
    """
    insert_success = 0
    s_list, l_list, w_list = cal_box_s(boxes_list_unload)
    # find_closest_value(s_list, l_up * w_up)
    closest_pair, index = find_closest_pair(l_up, w_up, l_list, w_list, boxes_list_unload, stack, h_limit)
    # print(f"index: {index}")
    if index is not None:
        select_box = boxes_list_unload[index][0]  # 锁定目标位置
        # select_box.get_box_info()
        if stack.height + select_box.type.h_b/1000 < h_limit:
            # 上下层异类且面积差别大，计算自堆叠余数
            if select_box.type.s_b * stack_s_use_ratio > stack.boxes_list[-1].type.s_b:
                down_num = boxes_dict[select_box.type.type_name]
                down_num_per_stack = math.floor(h_limit / (select_box.type.h_b / 1000))
                mod_num = down_num - math.floor(down_num / down_num_per_stack) * down_num_per_stack

                # 若自堆叠余数+现在的高度，不满足一箱要求：
                if mod_num == 0 or mod_num * select_box.type.h_b / 1000 + stack.height > h_limit:
                    insert_success = 0
                    print("货物插入下层会损坏stack的面积利用效率，不选择插入")
                else:  # 满足要求
                    stack.insert_down(select_box)
                    boxes_list_unload[index].remove(select_box)  # 删去box
                    update_boxes_dict(select_box, boxes_dict)
                    insert_success = 1

            else:
                stack.insert_down(select_box)
                boxes_list_unload[index].remove(select_box)  # 删去box
                update_boxes_dict(select_box, boxes_dict)
                insert_success = 1
        else:
            # print("货物超高，无法加入堆栈！")
            insert_success = 0

    else:  # 无法插入，保持不变
        insert_success = 0
    return insert_success


def create_total_stack(stack: CStack, c: CContainer, boxes_list_unload, boxes_dict):
    """
    根据集装箱高度，以及被选出来的首层货类，生成一个新的堆栈
    :param stack:
    :param c:
    :param boxes_list_unload:
    :param boxes_dict:
    :return:
    """

    is_done = check_stopping_generate(boxes_list_unload)  # 检查一次
    if is_done == 1:
        print("所有货物均装载完毕，停止当前stack的装载")
        return False

    if len(stack.boxes_list) == 0:
        print("没有顶层货物，装入错误！")
        return False

    h_limit = c.type.h_c
    h = stack.boxes_list[0].type.h_b/1000

    # 往stack中插入box
    while h_limit > h:
        is_done = check_stopping_generate(boxes_list_unload)  # 检查一次
        if is_done == 1:
            print("所有货物均装载完毕，停止当前stack的装载")
            break

        s_up, l_up, w_up = cal_box_s(stack.boxes_list)
        insert_success = select_down_level(l_up[-1], w_up[-1], boxes_list_unload, stack, h_limit, boxes_dict)
        if insert_success == 0:
            break
    print("stack已装载完毕")
    return stack

    # box_type_count = dict()  # 嵌套字典：{货物类型1：{底面积：xx, 余数：xx}, xxx}
    # for box in boxes_list_unload:
    #     box_s = box.type.s_b
    #     if box.type not in list(box_type_count.keys()):
    #         inner_dict = {'box_s_total': box_s, 'count': 1}
    #         box_type_count[box.type] = inner_dict
    #     else:
    #         box_type_count[box.type]['box_s_total'] += box_s
    #         box_type_count[box.type]['count'] += 1

    # h_sum = 0
    # while h_sum < containers_list[c_type][0].type.h_c:
    #     if h_sum > 0:
    #         s_list[-1] = 0  # 顶层货物不能放在中间层
    #
    #     try:
    #         min_gt_0 = min(number for number in s_list if number > 0)  # 最小底面积
    #     except:
    #         print("所有箱子均已放置")
    #         break
    #
    #     if min_gt_0 <= containers_list[c_type][0].type.s_c:  # 一箱能装下
    #         len(blu_temp[s_list.index(min_gt_0)])  # box个数
    #
    # if top_box_possible is not None:
    #     # 如果不以顶层物品作为堆栈的顶层，寻找最小面积的物品作为顶层
    #     boxes_list_2d.append(top_box_possible)  # 最顶层的货
    #     boxes_list_unload.remove(top_box_possible)  # 货物列表删去这个货
    # else:
    #     print("出错！找不到箱子做堆栈了！")
    #     return False


def generate_stacks(c_2d: list, b_2d: list, b_dict: dict, smt: int):
    """
    生成一次每类集装箱的堆叠，返回最少浪费成本的堆叠箱型、堆叠方式、堆叠布局、堆叠的空间浪费成本
    :param b_dict:
    :param c_2d:
    :param b_2d:
    :param smt:
    :return:
    """
    is_done = check_stopping_generate(b_2d)  # 检查一次
    if is_done == 1:
        return False

    c_can_place = 0
    for c_type in c_2d:
        if len(c_type) != 0:
            c_can_place = 1
    if c_can_place == 0:
        print("集装箱数量不足！")
        return False

    ratios = []
    max_ratio = 0
    max_stacks = []
    max_type_idx = None
    max_layout = None
    max_b_2d_new = None
    max_b_dict_new = None

    for cdx, c_type in enumerate(c_2d):
        if len(c_type) == 0:
            continue

        c = c_type[0]
        boxes_dict = copy.deepcopy(b_dict)
        stacks_tmp = generate_stacks_for_one_container(c, b_2d, boxes_dict)  # 启发式规则生成堆叠

        for idx, stack in enumerate(stacks_tmp):
            stack.set_id(idx)
            stack.cal_value()
            # stack.get_info()
            # print("------")

        if smt == 1:  # 是装箱可行性问题
            total_s = 0
            for s in stacks_tmp:
                total_s += s.boxes_list[-1].type.s_b
            if total_s > c.type.s_c:
                print("堆叠生成后，发现底面积超出，无法装入")
                return False

        layout, ratio, obj = calculate_layout_cost(c, stacks_tmp, smt)  # 2d-bpp

        # 更新box_list和boxes_dict
        b_2d_new = copy.deepcopy(b_2d)
        boxes_dict_new = copy.deepcopy(boxes_dict)
        update_boxes_list_and_dict(stacks_tmp, layout, b_2d_new, boxes_dict_new)

        # if layout is None:
        #     print("剩余的货物，无法入箱")
        #     break

        if smt == 1:  # 是装箱可行性问题
            # 检查一次
            if check_stopping_generate(b_2d) == 1:
                print("堆叠排布后，发现无法装入")
                return False

        # 记录满载率最大的箱型方案
        if sum(layout.p) != [] and ratio > max_ratio:
            max_ratio = ratio
            max_type_idx = cdx  # 放在哪一类的集装箱内（主要限制stack的高度）
            # max_stacks = stacks_tmp  # 所有货物组成的多个stack组合的列表（高度+底面积+top约束）
            max_layout = layout  # 2dbpp，可以放入一个箱子的最优解，里面每个stack的二维坐标
            max_b_2d_new = b_2d_new  # 剩余的box_list
            max_b_dict_new = boxes_dict_new  # 剩余的box_dict

        is_done = check_stopping_generate(b_2d_new)  # 检查一次
        if is_done == 1:
            print("当前节点，所有货物已全部装入，不用继续分支")
        else:
            # 需要进行分支
            print("货物仍有剩余，需要进行分支！")

    if max_type_idx is not None:
        return max_type_idx, max_layout, max_ratio, max_b_2d_new, max_b_dict_new
    else:
        print("所有能入箱的货物在之前都已经摆好了")
        return False


# 定义排序函数
def box_sort(obj):
    return (obj.location_left_back_down.x, obj.location_left_back_down.y, obj.location_left_back_down.z)


def stack_sort(obj):
    return (obj.location.x, obj.location.y)


def input_stack_in_container(c_2d, c_dict, max_type_idx, max_layout, c_used):
    """
    将堆叠正式放入箱中，更新坐标标签，箱id标签
    :param c_2d: 集装箱列表
    :param c_dict: 集装箱数量字典
    :param max_type_idx:  箱型索引
    :param max_layout:   stack布局
    :param c_used: 已使用的集装箱列表
    :return:
    """
    c = c_2d[max_type_idx][0]
    for idx, s in enumerate(max_layout.stacks):
        if max_layout.p[idx] > 0.9:
            # stack落位
            s.set_location(c, max_layout.x[idx], max_layout.y[idx])
            if max_layout.r[idx] > 0.9:
                s.rotate_stack()
            # stack中的box落位
            for box in s.boxes_list:
                box.set_box_location_from_stack(s, max_layout.r[idx], c)
            c.input_stack(s)

    # 处理完之后，放入c_used中
    c_used[max_type_idx].append(c)

    # 排序一下box_list
    c.boxes_list.sort(key=box_sort)
    c.stacks_list.sort(key=stack_sort)

    # 原c_2d删除c
    update_containers_dict(c, c_dict)
    c_2d[max_type_idx].remove(c)


def output_total_info(is_solve, c_2d, order: COrder, t, filename, from_net):
    data = None
    if is_solve == -1:  # 存在不满足箱型大小的货物
        data = pd.DataFrame({'err_msg': "存在不满足箱型大小的货物，问题不可行"})
    elif is_solve == -2:  # 货物过多，集装箱容量不足
        data = pd.DataFrame({'err_msg': "货物过多，集装箱容量不足"})
    elif is_solve == 1:
        data = pd.DataFrame(columns=['container_type', 'c_id', 'l', 'w', 'h', 'load_factor'])
        for b_type in order.boxes_types:
            data[b_type.type_name] = 0

        for idx, c_list in enumerate(c_2d):
            for jdx, c in enumerate(c_list):
                b_nums_dict = dict()
                for b_type in order.boxes_types:
                    b_nums_dict[b_type.type_name] = 0
                for b in c.boxes_list:
                    b_nums_dict[b.type.type_name] += 1

                series = pd.Series({
                    'container_type': c.type.type_name,
                    'c_id': c.c_id,
                    'l': c.type.l_c,
                    'w': c.type.w_c,
                    'h': c.type.h_c,
                    'load_factor': '{:.2%}'.format(c.inside_v / c.type.v_c),
                }, name=jdx)
                s2 = pd.Series(b_nums_dict, name='cnt')
                series = series.append(s2)
                series.name = 'jdx1'
                data = data.append(series)
        s_t = pd.Series({'time_cost': round(t, 2)}, name='t')
        data = data.append(s_t)
    if from_net == 0:
        data.to_excel("../result/result_files/{}/装箱方案总览.xlsx".format(filename), index=False, encoding='utf-8')
        return None
    else:
        data_name = "整体装箱方案"
        table_html = f'<h2>{data_name}</h2>' + data.to_html(index=False)
        # table_html = data.to_html(index=False)
        data.to_excel("./temp/result/result_files/{}/装箱方案总览.xlsx".format(filename), index=False, encoding='utf-8')
        return table_html


# 绘制立方体边框
def plot_linear_cube(ax, x, y, z, dx, dy, dz, color='red', linestyle=None, curves=None):
    xx = [x, x, x+dx, x+dx, x]  # 前后闭合的一个圈
    yy = [y, y+dy, y+dy, y, y]
    kwargs = {"alpha": 1, "color": color, "linewidth": 2.5, "zorder": 2}
    if linestyle:
        kwargs["linestyle"] = linestyle
    if curves is None:
        curves = []
    curves.extend(ax.plot3D(xx, yy, [z]*5, **kwargs))  # 上框
    curves.extend(ax.plot3D(xx, yy, [z+dz]*5, **kwargs))  # 下框
    # 补充4条侧棱
    curves.extend(ax.plot3D([x, x], [y, y], [z, z+dz], **kwargs))
    curves.extend(ax.plot3D([x, x], [y+dy, y+dy], [z, z+dz], **kwargs))
    curves.extend(ax.plot3D([x+dx, x+dx], [y+dy, y+dy], [z, z+dz], **kwargs))
    curves.extend(ax.plot3D([x+dx, x+dx], [y, y], [z, z+dz], **kwargs))
    return curves


# 立方体六面坐标
def cuboid_data2(o, size=(1, 1, 1)):
    X = [[[0, 1, 0], [0, 0, 0], [1, 0, 0], [1, 1, 0]],
         [[0, 0, 0], [0, 0, 1], [1, 0, 1], [1, 0, 0]],
         [[1, 0, 1], [1, 0, 0], [1, 1, 0], [1, 1, 1]],
         [[0, 0, 1], [0, 0, 0], [0, 1, 0], [0, 1, 1]],
         [[0, 1, 0], [0, 1, 1], [1, 1, 1], [1, 1, 0]],
         [[0, 1, 1], [0, 0, 1], [1, 0, 1], [1, 1, 1]]]
    X = np.array(X).astype(float)
    for i in range(3):
        X[:, :, i] *= size[i]
    X += np.array(o)
    return X


# 绘制立方体
def plotCubeAt2(positions, sizes=None, facecolors=None, edgecolor=None, **kwargs):
    if not isinstance(facecolors, (list, np.ndarray)):
        facecolors = ["C0"] * len(positions)
    if not isinstance(sizes, (list, np.ndarray)):
        sizes = [(1, 1, 1)] * len(positions)
    g = []
    c2 = None
    for p, s, c in zip(positions, sizes, facecolors):
        g.append(cuboid_data2(p, size=s))
        c2 = Poly3DCollection(np.concatenate(g), facecolors=facecolors, edgecolor=edgecolor, **kwargs)
    return c2


def draw_packing_result(c: CContainer, order: COrder, from_net):
    # 绘制结果
    fig = plt.figure()
    # ax1 = mplot3d.Axes3D(fig, auto_add_to_figure=False)
    ax1 = mplot3d.Axes3D(fig)
    fig.add_axes(ax1)
    # 绘制容器
    curves = plot_linear_cube(ax1, 0, 0, 0, c.type.w_c, c.type.l_c, c.type.h_c)
    palette = sns.color_palette("deep", len(order.boxes_list_2d))  # 货类配色

    colors2 = []
    positions = []
    sizes = []
    for box in c.boxes_list:
        positions.append((box.location_left_back_down.x, box.location_left_back_down.y, box.location_left_back_down.z))
        if box.rotate == 0:
            sizes.append((box.type.w_b/1000, box.type.l_b/1000, box.type.h_b/1000))
        else:
            sizes.append((box.type.l_b/1000, box.type.w_b/1000, box.type.h_b/1000))
        for i in range(6):
            colors2.append(palette[order.boxes_types.index(box.type)])
        if box.type.top_b == 0:
            pc = plotCubeAt2(positions, sizes, facecolors=colors2, edgecolor="k", label=box.type.type_name)
        else:
            pc = plotCubeAt2(positions, sizes, facecolors=colors2, edgecolor="k", label=box.type.type_name)
        pc._facecolors2d = pc._facecolor3d  # 如果添加label出现错误时，则启用
        pc._edgecolors2d = pc._edgecolor3d  # 如果添加label出现错误时，则启用
        curve = ax1.add_collection3d(pc)
        if isinstance(curve, list):
            # ax.plot3D 可能返回一个列表，尤其是当绘制多个线段时
            curves.extend(curve)
        else:
            # 如果只返回一个曲线对象，直接添加到列表中
            curves.append(curve)

    # 背景调白
    ax1.w_xaxis.set_pane_color((1.0, 1.0, 1.0, 1.0))
    ax1.w_yaxis.set_pane_color((1.0, 1.0, 1.0, 1.0))
    ax1.w_zaxis.set_pane_color((1.0, 1.0, 1.0, 1.0))
    ax1.view_init(32, 32)

    # # 前3个参数用来调整各坐标轴的缩放比例
    ax1.get_proj = lambda: np.dot(mplot3d.Axes3D.get_proj(ax1), np.diag([0.7, 1, 0.5, 1]))
    # 设置成一个比较好的参数

    legend_elements = []
    for idx, types in enumerate(order.boxes_types):
        # legend_elements.append(Line2D([0], [0], color=palette[idx], lw=4, label=types.type_name))
        if types.top_b == 1:
            legend_elements.append(Patch(facecolor=palette[idx], edgecolor='k', label=types.type_name))
        else:
            legend_elements.append(Patch(facecolor=palette[idx], edgecolor='k', label=types.type_name))
    # plt.legend(loc='best', prop={'family': 'SimHei', 'size': 7})
    plt.legend(handles=legend_elements, loc='best', prop={'family': 'SimHei', 'size': 7})
    plt.xlabel("X轴：集装箱宽（m）")
    plt.ylabel("Y轴：集装箱长（m）")
    # plt.title(f"集装箱id:{c.c_id}，型号{c.type.type_name} 装箱方案", fontsize=100)
    plt.suptitle("集装箱ID:{}，型号{} \n 装箱方案满载率{:.2%}".format(c.c_id, c.type.type_name, c.inside_v/c.type.v_c))
    # plt.suptitle("满载率：{:.2%}".format(c.inside_v/c.type.v_c))
    if from_net == 0:
        plt.savefig(f'../result/pictures/{order.filename}/集装箱{c.c_id}_型号{c.type.type_name}_装载图.png',
                    bbox_inches="tight", dpi=600)
        return None
    else:
        # 将图形保存到内存中的 BytesIO 对象
        img = io.BytesIO()
        plt.savefig(f'./temp/result/pictures/{order.filename}/集装箱{c.c_id}_型号{c.type.type_name}_装载图.png',
                    bbox_inches="tight", dpi=600, format='png')
        plt.savefig(img, format='png')
        img.seek(0)
        img_data = base64.b64encode(img.getvalue()).decode()
        return img_data
    # plt.show()

