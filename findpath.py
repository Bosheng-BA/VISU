import RSA4CEPO2
import airport
import os.path
import geo
import random
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import helpfunction


DATA_PATH = "DATA"
APT_FILE = os.path.join(DATA_PATH, "tianjin_new.txt")
airport_cepo: airport.Airport = airport.load2(APT_FILE)
airport_init: airport.Airport = airport.load(APT_FILE)


def themaxxy(network):
    max_x = float('-inf')
    max_y = float('-inf')

    for elem_dict in network.values():
        for coord, value in elem_dict.items():
            if isinstance(coord, tuple) and coord[0] > max_x:
                max_x = coord[0]
            if isinstance(coord, tuple) and coord[1] > max_y:
                max_y = coord[1]

    # print("最大的x值为：", max_x)
    # print("最大的y值为：", max_y)
    x = []
    y = []
    for i in range(max_x):
        x.append(i)
    y = x
    return x, y


def interactive_plot_network(network, x, y, pointcoordlist, plist):
    # 创建一个空的Figure对象
    fig = go.Figure()

    # 绘制线路
    for point, connections in network.items():
        for connected_point, _ in connections.items():
            fig.add_trace(go.Scatter(
                x=[point[0], connected_point[0]],
                y=[point[1], connected_point[1]],
                mode='lines',
                line=dict(color='gray', width=3)
            ))

    # 绘制节点
    x_coords = [coord[0] for coord in pointcoordlist]
    y_coords = [coord[1] for coord in pointcoordlist]
    fig.add_trace(go.Scatter(
        x=x_coords,
        y=y_coords,
        mode='markers',
        marker=dict(color='yellow', size=5)
    ))

    # 绘制最优路径
    for p in range(len(plist) - 1):
        fig.add_trace(go.Scatter(
            x=[plist[p][0], plist[p + 1][0]],
            y=[plist[p][1], plist[p + 1][1]],
            mode='lines',
            line=dict(color='red', width=3)
        ))

    # 更新图形布局
    fig.update_layout(
        title="Interactive Network Visualization",
        xaxis_title="X",
        yaxis_title="Y",
        showlegend=False
    )

    # 显示图形
    fig.show()


def findRSApath(airport_cepo):
    network = {}
    network_cepo = {}
    in_angles = {}
    out_angles = {}
    in_angles_cepo = {}
    out_angles_cepo = {}
    # print("the number of points", len(airport_cepo.points))
    # points, lines, runways = [], [], []
    points = airport_cepo.points
    runways = airport_cepo.runways
    lines = airport_cepo.lines
    init_lines = airport_init.lines
    points0 = airport_init.points
    # print("runway", runways)
    # for runway in runways:
    #     print(runway.xys)
    # point_xy_list = []
    for (i, point) in enumerate(points):
        network[point.xy] = {}
        in_angles[point.xy] = {}
        out_angles[point.xy] = {}
    for (i, line) in enumerate(lines):
        line_init = init_lines[i]
        length = geo.length(line_init.xys)
        length_cepo = abs(length / line.speed)
        # print(length)
        while length != 0.0:  # ignore the line with length '0'
            p1 = line_init.xys[0]
            p2 = line_init.xys[1]
            p3 = line_init.xys[-2]
            p4 = line_init.xys[-1]
            network[p1][p4] = length_cepo
            network[p4][p1] = length_cepo
            # for p in points:
            #     if p.xy == p1:
            #         pp = p
            in_angles[p1][p4] = geo.angle_2p(p1, p2)
            out_angles[p1][p4] = geo.angle_2p(p3, p4)
            in_angles[p4][p1] = geo.angle_2p(p4, p3)
            out_angles[p4][p1] = geo.angle_2p(p2, p1)
            # if line.speed < 0:
            #     in_angles[p1][p4] = geo.angle_2p(p1, p2)
            #     out_angles[p1][p4] = geo.angle_2p(p4, p3)
            #     in_angles[p4][p1] = geo.angle_2p(p4, p3)
            #     out_angles[p4][p1] = geo.angle_2p(p2, p1)
            # else:
            #     in_angles[p1][p4] = geo.angle_2p(p1, p2)
            #     out_angles[p1][p4] = geo.angle_2p(p3, p4)
            #     in_angles[p4][p1] = geo.angle_2p(p4, p3)
            #     out_angles[p4][p1] = geo.angle_2p(p2, p1)
            length = 0.0  # 注意浮点型

    for (i, runway) in enumerate(runways):
        p1 = runway.xys[0]
        p2 = runway.xys[1]
        length = geo.length(runway.xys)
        network[p1][p2] = length
        network[p2][p1] = length
        in_angles[p1][p2] = geo.angle_2p(p1, p2)
        out_angles[p1][p2] = geo.angle_2p(p1, p2)
        in_angles[p2][p1] = geo.angle_2p(p2, p1)
        out_angles[p2][p1] = geo.angle_2p(p2, p1)

    pointcoordlist = list(network.keys())
    # 处理路网

    network = helpfunction.initial_network(network, init_lines, points0, points)

    for i in range(len(pointcoordlist)):  # 形成和学长的一样的路网
        network_cepo[i] = {}
        in_angles_cepo[i] = {}
        out_angles_cepo[i] = {}
        listkey = list(network[pointcoordlist[i]].keys())
        for (j, keys) in enumerate(listkey):
            key = pointcoordlist.index(keys)
            # print(key)
            network_cepo[i][key] = network[pointcoordlist[i]][keys]
            in_angles_cepo[i][key] = in_angles[pointcoordlist[i]][keys]
            out_angles_cepo[i][key] = out_angles[pointcoordlist[i]][keys]


    # print(network_cepo)

    # print_network_info(network, points)
    """********* print network **********"""
    # neighbor_info = helpfunction.turn_network(network)
    # helpfunction.print_neighbor_info(neighbor_info, points)
    # # 使用函数创建包含neighbor_info字典中的信息和points列表中对应的点的信息的DataFrame
    # neighbor_info_dataframe = helpfunction.create_neighbor_info_dataframe(neighbor_info, points)
    return network, pointcoordlist, network_cepo, in_angles, out_angles, in_angles_cepo, out_angles_cepo


def findsource(points):
    source_points = [p for p in points if p.ptype == 'Stand']
    point = random.choice(source_points)
    # point = points[-10]
    print("Source:", point.ptype, point.name, point.xy)
    source = point.xy
    return source


def finddes(points):
    des_points = [p for p in points if p.ptype == 'Runway']
    point = random.choice(des_points)
    print("Destination:", point.ptype, point.name, point.xy)
    des = point.xy
    return des

