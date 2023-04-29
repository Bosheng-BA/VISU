import sys
import os.path
import tkinter
import airport
import traffic
import hmi
import hmi2
import findpath
import RSA4CEPO2
import time
import datetime
import helpfunction
import Draw
""" Default airport and traffic files """
DATA_PATH = "DATA"
APT_FILE = os.path.join(DATA_PATH, "tianjin_new.txt")
# FPL_FILE = os.path.join(DATA_PATH, "ZBTJ_20210725_Manex_STD.B&B.sim")
FPL_FILE = os.path.join(DATA_PATH, "ZBTJ_20210725_Manex_16R.B&B.sim")


if __name__ == "__main__":
    fpl_file = sys.argv[1] if 1 < len(sys.argv) else FPL_FILE
    # Load the airport and the traffic
    the_airport = airport.load(APT_FILE)

    the_traffic = traffic.load(the_airport, fpl_file)

    # Create the HMI
    main_hmi = hmi.HMI(the_airport, the_traffic)

    # Draw the airport and the traffic situation
    # main_hmi.time = main_hmi.traffic.t_min
    # hmi.draw_airport(main_hmi)
    # hmi.draw_traffic(main_hmi)
    #
    # # HMI main loop
    # main_hmi.mainloop()

    the_airport2 = airport.load2(APT_FILE)
    main_hmi2 = hmi2.HMI(the_airport2, the_traffic)
    main_hmi2.time = main_hmi2.traffic.t_min
    # hmi2.draw_airport(main_hmi2)
    # hmi2.draw_traffic(main_hmi2)
    # main_hmi2.mainloop()
    #
    # 单架飞机规划路径：
    # network_point, x, y, pointcoordlist, network = findpath.findRSApath(the_airport2)
    # s0 = findpath.findsource(points=the_airport2.points)
    # d0 = findpath.finddes(points=the_airport2.points)
    # s = pointcoordlist.index(s0)
    # # s = 12
    # d = pointcoordlist.index(d0)
    # orad = 500  # obstacle radius
    # ospeed = 2  # obstacle speed
    # (RSA4CEPO2.main(network, s, d, x, y, orad, ospeed, pointcoordlist, the_airport2, network_point))

    # 多飞机规划路径：
    # 初始化开始时间
    init_time = datetime.datetime(2023, 4, 17, 7, 0)
    pathlist = []  # 按照飞机的顺序储存飞机的节点序号路径
    path_coordlist = []  # 按照飞机的顺序储存飞机的节点坐标路径
    blockinfo = {} # 与实际小时分钟计数
    blockinfo2 = {} # 按照绝对时间计算

    # 为当前飞机规划路径
    network, pointcoordlist, network_cepo, in_angles, out_angles, in_angles_cepo, out_angles_cepo = \
        findpath.findRSApath(the_airport2)

    for flightnum in range(2):  # 这里我们考虑多架飞机的情况
        start_time = init_time + datetime.timedelta(seconds=10*flightnum)
        # 随机选择起点和终点
        source = findpath.findsource(the_airport2.points)
        destination = findpath.finddes(the_airport2.points)

        # # 为当前飞机规划路径
        # network, x, y, pointcoordlist, network = findpath.findRSApath(the_airport2, blocked_points)
        # s = pointcoordlist.index(source)
        source_flight = [155, 86]
        des_flight = [170, 164]
        # d = pointcoordlist.index(destination)
        # s = 76
        s = source_flight[flightnum]
        d = des_flight[flightnum]
        # d = pointcoordlist.index((21057, 9026))
        print("source:", s, ' destination:', d)

        if flightnum != 0:
            path = pathlist[-1]
            block_timedict = helpfunction.blocknode(network_cepo, path, start_time)
            blockinfo[flightnum-1] = block_timedict
            block_timedict2 = helpfunction.blocknode2(network_cepo, path, start_time)
            blockinfo2[flightnum-1] = block_timedict2

        path_set, length_set, plist, t, v = RSA4CEPO2.main(network_cepo, in_angles_cepo, out_angles_cepo, s, d,
                                                           flightnum, pathlist, pointcoordlist, the_airport2, network,
                                                           start_time, blockinfo, points=the_airport2.points)
        print("Flightnum :", flightnum)
        print('shortest path:', path_set, 'length:', length_set)

        # 更新blocked_points，考虑当前飞机的位置和前一架飞机的位置
        # ... 省略更新blocked_points的代码

        pathlist.append(path_set)
        path_coordlist.append(plist)

        # 暂停20秒
        time.sleep(10)

        # 更新开始时间
        start_time += datetime.timedelta(seconds=10)
        # Draw.create_bokeh_animation(network, network_cepo, pointcoordlist, t, v, plist)
    Draw.create_bokeh_animation_with_paths(network, network_cepo, pointcoordlist, v, t, pathlist, plist, blockinfo2,
                                           path_coordlist)
    # Draw.create_bokeh_animation_with_paths2(network_point, network, pointcoordlist, v, pathlist, plist, blockinfo2,
    #                                        path_coordlist)

