from gurobipy import *
from src.container import CContainer


class CAlgorithm2DBPP:
    def __init__(self, c: CContainer, stacks_tmp: list, smt: int):
        self.container = c
        self.stacks = stacks_tmp
        self.layout = []
        self.smt = smt

    def solve_by_gurobi(self):
        model = Model()

        # 定义决策变量
        p = {}  # stack是否被装箱
        x = {}  # stack的左上角横坐标
        y = {}  # stack的左上角纵坐标
        r = {}  # stack是否旋转（=0不旋转，即长边对长边，宽边对宽边）
        lij = {}  # stack_i是否在stack_j的左方
        bij = {}  # stack_i是否在stack_j的上方

        for i, stack in enumerate(self.stacks):
            p[i] = model.addVar(0, 1, vtype=GRB.BINARY, name=f'stack_{i}_in_c')
            x[i] = model.addVar(0, self.container.type.w_c, vtype=GRB.CONTINUOUS, name=f'stack_{i}_x')
            y[i] = model.addVar(0, self.container.type.l_c, vtype=GRB.CONTINUOUS, name=f'stack_{i}_y')
            r[i] = model.addVar(0, 1, vtype=GRB.BINARY, name=f'stack_{i}_is_rotate')
            for j, stack2 in enumerate(self.stacks):
                if i != j:
                    lij[i, j] = model.addVar(0, 1, vtype=GRB.BINARY, name='stack_' + str(i) + '_left_' + str(j))
                    bij[i, j] = model.addVar(0, 1, vtype=GRB.BINARY, name='stack_' + str(i) + '_up_' + str(j))

        # 定义目标函数
        obj = LinExpr(0)
        for i, s in enumerate(self.stacks):
            obj += p[i] * s.value
        model.setObjective(obj, GRB.MAXIMIZE)

        # 定义约束
        # 约束1：x,y不越界
        for i, s in enumerate(self.stacks):
            model.addConstr(x[i] + s.lx * (1 - r[i]) + s.ly * r[i] - self.container.type.w_c * (1 - p[i]) <= self.container.type.w_c,
                            name=f'stack_{i}_x_in_c')

            model.addConstr(y[i] + s.ly * (1 - r[i]) + s.lx * r[i] - self.container.type.l_c * (1 - p[i]) <= self.container.type.l_c,
                            name=f'stack_{i}_y_in_c')

        # 约束2：位置关系
        for i, s1 in enumerate(self.stacks):
            for j, s2 in enumerate(self.stacks):
                if i != j:
                    model.addConstr(lij[i, j] + lij[j, i] + bij[i, j] + bij[j, i]
                                    + (2 - p[i] - p[j]) >= 1, name=f'location_guarantee_{i}_{j}')

        # 约束3：坐标关系
        for i, s1 in enumerate(self.stacks):
            for j, s2 in enumerate(self.stacks):
                if i != j:
                    model.addConstr(x[i] + s1.lx * (1 - r[i]) + s1.ly * r[i] - self.container.type.w_c * (1 - lij[i, j])
                                    <= x[j], name=f'coordinate_on_x_{i}_{j}')
                    model.addConstr(y[i] + s1.ly * (1 - r[i]) + s1.lx * r[i] - self.container.type.l_c * (1 - bij[i, j])
                                    <= y[j], name=f'coordinate_on_y_{i}_{j}')

        # 有效不等式： 底面积不能超
        lhs = LinExpr(0)
        for i, s in enumerate(self.stacks):
            lhs.addTerms(s.lx * s.ly, p[i])
        model.addConstr(lhs <= self.container.type.s_c, name='total_s')
        lhs.clear()

        model.write('2dbpp.lp')
        if self.smt == 1:
            model.setParam(GRB.Param.TimeLimit, 100)
        else:
            model.setParam(GRB.Param.TimeLimit, 30)
        model.optimize()
        print('obj: ', model.ObjVal)

        # for key in p.keys():
        #     if p[key].x > 0:
        #         print(p[key].VarName + ' = ', p[key].x)
        #         print(x[key].VarName + ' = ', x[key].x)
        #         print(y[key].VarName + ' = ', y[key].x)
        #         print(r[key].VarName + ' = ', r[key].x)
        p_value, x_value, y_value, r_value = [], [], [], []
        for key in p.keys():
            p_value.append(p[key].x)
            x_value.append(round(x[key].x, 3))
            y_value.append(round(y[key].x, 3))
            r_value.append(r[key].x)

        return p_value, x_value, y_value, r_value, model.ObjVal
