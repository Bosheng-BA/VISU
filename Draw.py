import plotly.graph_objects as go
import math
import os
import os.path
import pandas as pd
import plotly.graph_objects as go
from functools import partial
from bokeh.models import ColumnDataSource, CustomJS
from bokeh.palettes import Spectral4
from bokeh.plotting import figure, output_file, show
from bokeh.layouts import column
from bokeh.models import Slider, Button
from bokeh.io import curdoc
import time
import datetime


# 可视化路网寻路的过程
def create_bokeh_animation(network_point, network, pointcoordlist, t, v, pathpoint):
    # 设置输出文件
    output_file("bokeh_animation.html")

    # 创建一个空的 Figure 对象
    p = figure(title="Bokeh Animation", x_range=(20000, 26000), y_range=(6000, 9500), width=1200, height=600)

    # 绘制线路
    for point, connections in network_point.items():
        for connected_point, _ in connections.items():
            p.line(
                x=[point[0], connected_point[0]],
                y=[point[1], connected_point[1]],
                line_color='gray', line_width=3
            )

    # 绘制节点
    x_coords = [coord[0] for coord in pointcoordlist]
    y_coords = [coord[1] for coord in pointcoordlist]
    p.circle(x=x_coords, y=y_coords, size=5, color='yellow', legend_label="Nodes")

    # 添加障碍物的初始位置
    # obstacle_x = [24000]
    # obstacle_y = [7000]
    # p.circle(x=obstacle_x, y=obstacle_y, size=orad, color='red', legend_label="Obstacle")

    # 绘制最后得到的路径
    path_x = [pathpoint[i][0] for i in range(len(pathpoint))]
    path_y = [pathpoint[i][1] for i in range(len(pathpoint))]
    p.line(x=path_x, y=path_y, line_color='blue', line_width=3, legend_label="Final Path")

    show(p)


# 圆形障碍物情况
def create_bokeh_animation_with_path(network_point, network, pointcoordlist, t, v, path, pathpoint):
    output_file("bokeh_animation_with_path.html")

    p = figure(title="Bokeh Animation", x_range=(20000, 26000), y_range=(6000, 9500), width=1200, height=600)

    for point, connections in network_point.items():
        for connected_point, _ in connections.items():
            p.line(
                x=[point[0], connected_point[0]],
                y=[point[1], connected_point[1]],
                line_color='gray', line_width=3
            )

    x_coords = [coord[0] for coord in pointcoordlist]
    y_coords = [coord[1] for coord in pointcoordlist]
    p.circle(x=x_coords, y=y_coords, size=5, color='blackgrey', legend_label="Nodes")

    path_cost = [0]
    for i in range(len(path) - 1):
        start_node, end_node = path[i], path[i + 1]
        distance = network[start_node][end_node]
        path_cost.append(path_cost[-1] + distance)

    path_x = [pathpoint[i][0] for i in range(len(pathpoint))]
    path_y = [pathpoint[i][1] for i in range(len(pathpoint))]
    path_source = ColumnDataSource(data=dict(x=[], y=[]))
    p.line(x='x', y='y', line_color='red', line_width=3, legend_label="Path", source=path_source)

    end_t = t * v
    slider = Slider(start=0, end=end_t, value=0, step=1, title="Time")

    # 使用JavaScript回调
    slider_callback = CustomJS(
        args=dict(slider=slider, path_source=path_source, path_x=path_x,
                  path_y=path_y, path_cost=path_cost, v=v), code="""
        const time = slider.value;

        // Update path based on current time
        const visible_x = [];
        const visible_y = [];
        for (let i = 0; i < path_cost.length - 1; i++) {
            if (time * v >= path_cost[i]) {
                visible_x.push(path_x[i]);
                visible_y.push(path_y[i]);
            if (i < path_cost.length - 2 && time * v < path_cost[i + 1]) {
                visible_x.push(path_x[i + 1]);
                visible_y.push(path_y[i + 1]);
               }
        }
    }

         // Check if the last point of the path should be visible
         if (time * v >= path_cost[path_cost.length - 1]) {
             visible_x.push(path_x[path_x.length - 1]);
             visible_y.push(path_y[path_y.length - 1]);
          }

        path_source.data = {x: visible_x, y: visible_y};
        path_source.change.emit();
    """)

    slider.js_on_change('value', slider_callback)

    button = Button(label="Reset")
    button_callback = CustomJS(args=dict(slider=slider, path_source=path_source), code="""
            slider.value = 0;

            path_source.data = {x: [], y: []};
        path_source.change.emit();
    """)
    button.js_on_click(button_callback)

    layout = column(p, slider, button)
    show(layout)


# 多飞机情况
def create_bokeh_animation_with_paths(network_point, network, pointcoordlist, v, t, pathlist, pathpointlist, blockinfo,
                                      path_coordlist):
    output_file("bokeh_animation_with_paths.html")

    p = figure(title="Bokeh Animation", x_range=(20000, 26000), y_range=(6000, 9500), width=1200, height=600)
    colors = ['red', 'green', 'blue', 'purple', 'orange', 'brown', 'pink', 'black']

    for point, connections in network_point.items():
        for connected_point, _ in connections.items():
            p.line(
                x=[point[0], connected_point[0]],
                y=[point[1], connected_point[1]],
                line_color='gray', line_width=3
            )

    x_coords = [coord[0] for coord in pointcoordlist]
    y_coords = [coord[1] for coord in pointcoordlist]
    p.circle(x=x_coords, y=y_coords, size=5, color='yellow', legend_label="Nodes")

    for flightnum, path in enumerate(path_coordlist):
        path_x = [path_coordlist[flightnum][i][0] for i in range(len(path_coordlist[flightnum]))]
        path_y = [path_coordlist[flightnum][i][1] for i in range(len(path_coordlist[flightnum]))]
        p.line(x=path_x, y=path_y, line_color=colors[flightnum % len(colors)], line_alpha=0.4, line_width=2,
               legend_label=f"Static Path {flightnum + 1}")

    path_sources = []
    for flightnum, path in enumerate(path_coordlist):
        path_x = [path_coordlist[flightnum][i][0] for i in range(len(path_coordlist[flightnum]))]
        path_y = [path_coordlist[flightnum][i][1] for i in range(len(path_coordlist[flightnum]))]
        path_source = ColumnDataSource(data=dict(x=[], y=[]))
        path_sources.append(path_source)
        p.line(x='x', y='y', line_color=colors[flightnum % len(colors)], line_width=3,
               legend_label=f"Path {flightnum + 1}", source=path_source)

    path_costlist = []
    path_cost = [0]

    for flight in pathlist:
        for i in range(len(flight) - 1):
            start_node, end_node = flight[i], flight[i + 1]
            distance = network[start_node][end_node]
            path_cost.append(path_cost[-1] + distance)
        path_costlist.append(path_cost)

    stat_time = 0
    max_end_time = 0
    for flight, pathblock in blockinfo.items():
        for node, during in pathblock.items():
            if during[1] > max_end_time:
                max_end_time = during[1]

    # t = (max_end_time - stat_time)
    # print("maxtime", max_end_time)

    slider = Slider(start=0, end=t, value=0, step=1, title="Time")

    # 使用JavaScript回调
    slider_callback = CustomJS(
        args=dict(slider=slider, path_sources=path_sources, pathlist=path_coordlist, path_costlist=path_costlist, v=10),
        code="""
        const time = slider.value;

        for (let flightnum = 0; flightnum < path_sources.length; flightnum++) {
            const path_x = pathlist[flightnum].map(point => point[0]);
            const path_y = pathlist[flightnum].map(point => point[1]);
            const path_cost = path_costlist[flightnum];

            // Update path based on current time
            const visible_x = [];
            const visible_y = [];
            const time1 = time - flightnum*v;

            for (let i = 0; i < path_cost.length - 1; i++) {
                if (time1  >= path_cost[i]) {
                    visible_x.push(path_x[i]);
                    visible_y.push(path_y[i]);

                    if (i < path_cost.length - 2 && time1 < path_cost[i + 1]) {
                        visible_x.push(path_x[i + 1]);
                        visible_y.push(path_y[i + 1]);
                    }
                }
            }

            // Check if the last point of the path should be visible
            if (time1 >= path_cost[path_cost.length - 1]) {
                visible_x.push(path_x[path_x.length - 1]);
                visible_y.push(path_y[path_y.length - 1]);
            }

            path_sources[flightnum].data = {x: visible_x, y: visible_y};
            path_sources[flightnum].change.emit();
        }
    """)

    slider.js_on_change('value', slider_callback)

    button = Button(label="Reset")
    button_callback = CustomJS(args=dict(slider=slider, path_sources=path_sources), code="""
        slider.value = 0;

        for (let flightnum = 0; flightnum < path_sources.length; flightnum++) {
             path_sources[flightnum].data = {x: [], y: []};
             path_sources[flightnum].change.emit();
             }
    """)
    button.js_on_click(button_callback)

    layout = column(p, slider, button)
    show(layout)


def create_bokeh_animation_with_paths2(network_point, network, pointcoordlist, v, pathlist, pathpointlist, blockinfo,
                                       path_coordlist):
    output_file("bokeh_animation_with_paths.html")

    p = figure(title="Bokeh Animation", x_range=(20000, 26000), y_range=(6000, 9500), width=1200, height=600)

    for point, connections in network_point.items():
        for connected_point, _ in connections.items():
            p.line(
                x=[point[0], connected_point[0]],
                y=[point[1], connected_point[1]],
                line_color='gray', line_width=3
            )

    x_coords = [coord[0] for coord in pointcoordlist]
    y_coords = [coord[1] for coord in pointcoordlist]
    p.circle(x=x_coords, y=y_coords, size=5, color='yellow', legend_label="Nodes")

    for flightnum, path in enumerate(path_coordlist):
        path_x = [path_coordlist[flightnum][i][0] for i in range(len(path_coordlist[flightnum]))]
        path_y = [path_coordlist[flightnum][i][1] for i in range(len(path_coordlist[flightnum]))]
        p.line(x=path_x, y=path_y, line_color='blue', line_alpha=0.6, line_width=2,
               legend_label=f"Static Path {flightnum + 1}")

    path_sources = []
    for flightnum, path in enumerate(path_coordlist):
        path_x = [path_coordlist[flightnum][i][0] for i in range(len(path_coordlist[flightnum]))]
        path_y = [path_coordlist[flightnum][i][1] for i in range(len(path_coordlist[flightnum]))]
        path_source = ColumnDataSource(data=dict(x=[], y=[]))
        path_sources.append(path_source)
        p.line(x='x', y='y', line_color='red', line_width=3, legend_label=f"Path {flightnum + 1}", source=path_source)

    stat_time = 0
    max_end_time = 0
    for flight, pathblock in blockinfo.items():
        for node, during in pathblock.items():
            if during[1] > max_end_time:
                max_end_time = during[1]

    t = (max_end_time - stat_time)

    slider = Slider(start=0, end=t, value=0, step=1, title="Time")

    # 使用JavaScript回调
    slider_callback = CustomJS(
        args=dict(slider=slider, path_sources=path_sources, pathlist=path_coordlist, blockinfo=blockinfo, v=20),
        code="""
        const time = slider.value;  // Update time based on slider value
        console.log("Blockinfo in CustomJS:", blockinfo);


        for (let flightnum = 0; flightnum < path_sources.length; flightnum++) {
            const path_x = pathlist[flightnum].map(point => point[0]);
            const path_y = pathlist[flightnum].map(point => point[1]);
            const path = pathlist[flightnum];
            const blocks = Object.values(blockinfo[flightnum]);  // Update the definition of blocks

        // Update path based on current time
            const visible_x = [];
            const visible_y = [];

        for (let i = 0; i < path.length - 1; i++) {
            const block = blocks[i];  // Update the definition of block
            const start_time = block[0];
            const end_time = block[1];

            if (i <= 0 && time > start_time) {
                visible_x.push(path_x[i]);
                visible_y.push(path_y[i]);
                }

            if (i >= 1 && time >= blocks[i - 1][0] && time <= end_time) {
                visible_x.push(path_x[i]);
                visible_y.push(path_y[i]);
                }
            }

        // Check if the last point of the path should be visible
        if (time >= blocks[blocks.length - 1][1]) {
                visible_x.push(path_x[path_x.length - 1]);
                visible_y.push(path_y[path_y.length - 1]);
                }
        
            path_sources[flightnum].data = { x: visible_x, y: visible_y };
            path_sources[flightnum].change.emit();
        }
    """)

    slider.js_on_change('value', slider_callback)

    button = Button(label="Reset")
    button_callback = CustomJS(args=dict(slider=slider, path_sources=path_sources), code="""
        slider.value = 0;

        for (let flightnum = 0; flightnum < path_sources.length; flightnum++) {
             path_sources[flightnum].data = {x: [], y: []};
             path_sources[flightnum].change.emit();
             }
    """)
    button.js_on_click(button_callback)

    layout = column(p, slider, button)
    show(layout)
