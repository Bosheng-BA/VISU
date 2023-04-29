
import math
import pandas as pd
import geo
import datetime


# 转换路网的类型
def turn_network(network_point):
    neighbor_info = {key: list(value.keys()) for key, value in network_point.items()}
    return neighbor_info


# 将数字编号类型的路径序列转换为坐标类型
def list2node(list, pointcoordlist):
    plist = []
    for i in list:
        plist.append(pointcoordlist[i])
    return plist


# 打印出坐标类型的序列的point的信息
def print_plist(plist, points):
    for p in plist:
        for point in points:
            if point.xy == p:
                # print(f"Point: ptype={point.ptype}, name={point.name}, xy={point.xy}")
                print(f"Point: {point.ptype} {point.name} {point.xy}")


# 打印出一个路网的中每个point的neighbor point信息
def print_neighbor_info(neighbor_info, points):
    # 遍历新字典
    for key_xy, value_xys in neighbor_info.items():
        # 找到与键匹配的点并打印属性
        for point in points:
            if point.xy == key_xy:
                print(f"Key: ptype={point.ptype}, name={point.name}, xy={point.xy}")
                break

        # 找到与值匹配的点并打印属性
        for value_xy in value_xys:
            for point in points:
                if point.xy == value_xy:
                    print(f"Value: ptype={point.ptype}, name={point.name}, xy={point.xy}")
                    break


def create_neighbor_info_dataframe(neighbor_info, points):
    data = []

    # 遍历新字典
    for key_xy, value_xys in neighbor_info.items():
        key_info = None
        # 找到与键匹配的点并保存信息
        for point in points:
            if point.xy == key_xy:
                key_info = {"Point Type (Key)": point.ptype, "Point Name (Key)": point.name,
                            "Coordinates (Key)": point.xy}
                break

        # 找到与值匹配的点并保存信息
        for value_xy in value_xys:
            value_info = None
            for point in points:
                if point.xy == value_xy:
                    value_info = {"Point Type (Value)": point.ptype, "Point Name (Value)": point.name,
                                  "Coordinates (Value)": point.xy}
                    break

            if key_info is not None and value_info is not None:
                data.append({**key_info, **value_info})

    return pd.DataFrame(data)


def findpointtype(line1, line2, points):
    point_list_type = []
    point_list = [line1.xys[0], line1.xys[-1], line2.xys[0], line2.xys[-1]]
    for p in points:
        if p.xy in point_list:
            point_list_type.append(p.ptype)
    S = 'Stand'
    if S in point_list_type:
        return 1
    return 0


def initial_network(network_point, init_lines, init_points, points):
    # remove the path Stand to normal
    del_dict = {}
    for p, connections in network_point.items():
        for point in points:
            if point.xy == p and point.ptype == 'Stand':
                for connected_point in connections.keys():
                    for point2 in points:
                        if point2.xy == connected_point and point2.ptype == 'normal':
                            del_dict[p] = connected_point
    for p, connections in del_dict.items():
        network_point[p].pop(connections)
    # # remove these paths' angle above 90
    # unreachable_init_lines = []
    # unreachable_point = {}
    # for i in range(len(init_lines)):
    #     for j in range(i+1, len(init_lines)):
    #         line1 = init_lines[i]
    #         line2 = init_lines[j]
    #         # line22 = lines[j]
    #
    #         coords1 = set(line1.xys)
    #         coords2 = set(line2.xys)
    #
    #         intersection_opt = coords1.intersection(coords2)
    #         if intersection_opt:  # 有交点
    #             intersection = list(intersection_opt)[0]
    #
    #             # 检查线段的端点是否具有 Stand 类型
    #             is_stand_type = False
    #             for point in points:
    #                 if point.xy in (
    #                         line1.xys[0], line1.xys[-1], line2.xys[0], line2.xys[-1]) and point.ptype == 'Stand':
    #                     is_stand_type = True
    #             #         break
    #             #
    #             # if is_stand_type:
    #             #     continue
    #
    #             if line1.xys[0] == intersection:
    #                 k1 = True
    #             else:
    #                 k1 = False
    #             if line2.xys[0] == intersection:
    #                 k2 = True
    #             else:
    #                 k2 = False
    #
    #             intersection_point = None
    #             for point in points:
    #                 if point.xy == intersection:
    #                     intersection_point = point
    #                     break
    #
    #             if k1 and (not k2):
    #                 angle = geo.angle(line1.xys[-2], line2.xys[0], line2.xys[1])
    #             if k2 and (not k1):
    #                 angle = geo.angle(line2.xys[-2], line1.xys[0], line1.xys[1])
    #
    #             # angle = angle_between_init_lines(line1, line2)
    #             # print("angle", i, j, "=", angle)
    #             angle = abs(math.degrees(angle))
    #
    #             if intersection_point is not None:
    #
    #                 if intersection_point.ptype == 'Stand':
    #                     continue
    #                 # pushback lines have the speed -VMAX
    #                 elif (line1.speed < 0 or line2.speed < 0) and angle < 90.0 \
    #                         and intersection_point.ptype == 'pushback':
    #                     # 有些含有pushback但是不是stand为起点
    #                     boolean_point_type = findpointtype(line1, line2, init_points)
    #                     point_list = [line1]
    #                     if boolean_point_type:
    #
    #                         # if angle smaller than 90 degrees, then add into unreachable point
    #                         if line1.speed < 0:
    #                             kk2 = -1 if k2 else 0
    #                             for p in points:
    #                                 if p.xy == line2.xys[kk2] and p.ptype == 'Stand':
    #                                     unreachable_point[line2.xys[0]] = line2.xys[kk2]
    #                                     # print('unreachable point of 2', line2.xys[0], 'is', line2.xys[kk2])
    #                         else:
    #                             kk1 = -1 if k1 else 0
    #                             for p in points:
    #                                 if p.xy == line2.xys[kk1] and p.ptype == 'Stand':
    #                                     unreachable_point[line1.xys[0]] = line1.xys[kk1]
    #                                     # print('unreachable point of 1', line1.xys[0], 'is', line1.xys[kk1])
    #
    #                 elif intersection_point.ptype == 'normal':
    #                     if not is_stand_type and angle > 90:  # 夹角大于90度
    #                         kk = - 1 if not k2 else 0
    #                         unreachable_point[line1.xys[0]] = line2.xys[kk]
    #                         unreachable_init_lines.append((i, j))
    #                 elif intersection_point.ptype == 'Runway':
    #                     if angle > 90:
    #                         kk = - 1 if not k2 else 0
    #                         unreachable_point[line1.xys[0]] = line2.xys[kk]
    #                         unreachable_init_lines.append((i, j))
    #
    # # 创建一个空字典，用于存储要删除的连接
    # connections_to_remove = {}
    #
    # for p, connections in unreachable_point.items():
    #     # 检查键 p 是否存在于 network_point 中
    #     # if p in network_point.keys():
    #     for point, point_dict in network_point.items():
    #         for subpoint in point_dict.keys():
    #             if subpoint == connections:
    #                 connections_to_remove[p] = connections
        # for point in network_point[p].keys():
        #     if point == connections:
        #         connections_to_remove[p] = connections

    # # 根据临时字典删除不可达连接
    # for p, connections in connections_to_remove.items():
    #     if p in network_point.keys():
    #         dictd = network_point[p]
    #         if connections in dictd.keys():
    #             network_point[p].pop(connections)
    return network_point


def blocknode(network, path, start_time):
    """

    """
    # start_time  # 此飞机的起始第一个点的时间
    # the current position of the obstacle
    block_timedict = {}
    path_cost = [0]


    for i in range(len(path) - 1):
        block_set = [start_time, start_time]

        path_cost.append(path_cost[-1] + network[path[i]][path[i + 1]])

        nextcost = network[path[i]][path[i + 1]]
        cost = 20 if nextcost > 20 else nextcost

        time1 = start_time + datetime.timedelta(seconds=path_cost[-2])  # block 开始时间
        time2 = time1 + datetime.timedelta(seconds=path_cost[-1]) + datetime.timedelta(seconds=cost)  # block 结束时间
        block_set[0] = time1
        block_set[1] = time2
        block_timedict[path[i]] = block_set

    return block_timedict

def blocknode2(network, path, start_time):
    """

    """
    # start_time  # 此飞机的起始第一个点的时间
    # the current position of the obstacle
    block_timedict2 = {}
    path_cost = [0]
    init_time = datetime.datetime(2023, 4, 17, 7, 0)
    s_t = (start_time - init_time).seconds
    # e_t = (start_time - init_time).seconds
    # block_set = [s_t, s_t]

    for i in range(len(path) - 1):
        block_set = [s_t, s_t]  # Initialize block_set as a new list with two elements

        path_cost.append(path_cost[-1] + network[path[i]][path[i + 1]])

        nextcost = network[path[i]][path[i + 1]]
        cost = 20 if nextcost > 20 else nextcost

        time1 = start_time + datetime.timedelta(seconds=path_cost[-2])  # block 开始时间
        time2 = time1 + datetime.timedelta(seconds=path_cost[-1]) + datetime.timedelta(seconds=cost)  # block 结束时间
        t1 = (time1 - init_time).seconds
        t2 = (time2 - init_time).seconds
        block_set[0] = t1
        block_set[1] = t2
        block_timedict2[i] = block_set

    return block_timedict2