import time
import numpy as np
from enum import IntEnum
from unitree_sdk2py.core.channel import ChannelPublisher, ChannelFactoryInitialize
import sys

# from user_data import *
from unitree_sdk2py.idl.unitree_hg.msg.dds_ import LowCmd_
from unitree_sdk2py.idl.default import unitree_hg_msg_dds__LowCmd_
import unitree_sdk2py.idl.unitree_hg.msg.dds_ as dds
from unitree_sdk2py.utils.crc import CRC


kTopicArmSDK = "rt/lowcmd"
kPi = 3.141592654
kPi_2 = 1.57079632
kNumMotors = 35

if __name__ == "__main__":

    if len(sys.argv)>1:
        ChannelFactoryInitialize(0, sys.argv[1])
    else:
        ChannelFactoryInitialize(0)
    
    # 初始化发布节点
    low_cmd_publisher = ChannelPublisher(kTopicArmSDK, LowCmd_)
    low_cmd_publisher.Init()
    # 初始化LowCmd_
    msg = unitree_hg_msg_dds__LowCmd_()
    # CRC校验实例
    crc = CRC()
    # 控制时间参数
    control_dt = 0.02
    init_time = 20
    init_time_steps = int(init_time / control_dt)

    # 控制参数设置
    msg.mode_pr = 0
    msg.mode_machine = 4
    for i in range(init_time_steps):
        for idx in range(kNumMotors):
                msg.motor_cmd[idx].mode = 0x01
        msg.crc = crc.Crc(msg)
        # print(msg.crc)
        low_cmd_publisher.Write(msg)
        time.sleep(control_dt)

    print("Done!")
    exit()
