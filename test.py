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
    main_hmi.time = main_hmi.traffic.t_min
    hmi.draw_airport(main_hmi)
    hmi.draw_traffic(main_hmi)

    # HMI main loop
    main_hmi.mainloop()

    the_airport2 = airport.load2(APT_FILE)
    main_hmi2 = hmi2.HMI(the_airport2, the_traffic)
    main_hmi2.time = main_hmi2.traffic.t_min
    hmi2.draw_airport(main_hmi2)
    hmi2.draw_traffic(main_hmi2)
    main_hmi2.mainloop()

# import datetime
#
# # 创建两个datetime.datetime对象
# time1 = datetime.datetime(2023, 4, 17, 7, 0, 0)
# time2 = datetime.datetime(2023, 4, 17, 7, 0, 20)
#
# # 计算它们之间的时间差
# time_difference = time2 - time1
# time_difference = time_difference.seconds
# print("Time difference:", time_difference)
#
# # 比较它们的大小
# if time2 > time1:
#     print("time2 is later than time1")
#
# # 使用datetime.timedelta对象更新一个datetime.datetime对象
# updated_time = time1 + datetime.timedelta(seconds=70)
# print("Updated time:", updated_time)
#
# # 更新一个datetime.time对象
# time_only = datetime.time(7, 0, 0)
# updated_time_only = (datetime.datetime.combine(datetime.date.today(), time_only)
#                      + datetime.timedelta(seconds=20)).time()
# print("Updated time only:", updated_time_only)
