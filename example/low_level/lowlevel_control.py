import time
import sys

from unitree_sdk2py.core.channel import ChannelPublisher, ChannelFactoryInitialize
from unitree_sdk2py.core.channel import ChannelSubscriber, ChannelFactoryInitialize
from unitree_sdk2py.idl.default import unitree_go_msg_dds__LowCmd_
from unitree_sdk2py.idl.unitree_go.msg.dds_ import LowCmd_
from unitree_sdk2py.utils.crc import CRC
from unitree_sdk2py.utils.thread import Thread
import unitree_legged_const as go2

crc = CRC()

if __name__ == '__main__':

    if len(sys.argv)>1:
        ChannelFactoryInitialize(0, sys.argv[1])
    else:
        ChannelFactoryInitialize(0)
    # Create a publisher to publish the data defined in UserData class
    pub = ChannelPublisher("rt/lowcmd", LowCmd_)
    pub.Init()
    
    cmd = unitree_go_msg_dds__LowCmd_()
    cmd.head[0]=0xFE
    cmd.head[1]=0xEF
    cmd.level_flag = 0xFF
    cmd.gpio = 0
    for i in range(20):
        cmd.motor_cmd[i].mode = 0x01  # (PMSM) mode
        cmd.motor_cmd[i].q= go2.PosStopF
        cmd.motor_cmd[i].kp = 0
        cmd.motor_cmd[i].dq = go2.VelStopF
        cmd.motor_cmd[i].kd = 0
        cmd.motor_cmd[i].tau = 0

    while True:        
        # Toque controle, set RL_2 toque
        cmd.motor_cmd[go2.LegID["RL_2"]].q = 0.0 # Set to stop position(rad)
        cmd.motor_cmd[go2.LegID["RL_2"]].kp = 0.0
        cmd.motor_cmd[go2.LegID["RL_2"]].dq = 0.0 # Set to stop angular velocity(rad/s)
        cmd.motor_cmd[go2.LegID["RL_2"]].kd = 0.0
        cmd.motor_cmd[go2.LegID["RL_2"]].tau = 1.0 # target toque is set to 1N.m

        # Poinstion(rad) control, set RL_0 rad
        cmd.motor_cmd[go2.LegID["RL_0"]].q = 0.0  # Taregt angular(rad)
        cmd.motor_cmd[go2.LegID["RL_0"]].kp = 10.0 # Poinstion(rad) control kp gain
        cmd.motor_cmd[go2.LegID["RL_0"]].dq = 0.0  # Taregt angular velocity(rad/ss)
        cmd.motor_cmd[go2.LegID["RL_0"]].kd = 1.0  # Poinstion(rad) control kd gain
        cmd.motor_cmd[go2.LegID["RL_0"]].tau = 0.0 # Feedforward toque 1N.m
        
        cmd.crc = crc.Crc(cmd)

        #Publish message
        if pub.Write(cmd):
            print("Publish success. msg:", cmd.crc)
        else:
            print("Waitting for subscriber.")

        time.sleep(0.002)