import time
import sys

from unitree_sdk2py.core.channel import ChannelFactoryInitialize
from unitree_sdk2py.idl.default import unitree_go_msg_dds__LowCmd_
from unitree_sdk2py.utils.crc import CRC

crc = CRC()

PosStopF = 2.146e9
VelStopF = 16000.0

if __name__ == "__main__":
    ChannelFactoryInitialize(0)

    cmd = unitree_go_msg_dds__LowCmd_()
    cmd.head[0] = 0xFE
    cmd.head[1] = 0xEF
    cmd.level_flag = 0xFF
    cmd.gpio = 0
    for i in range(20):
        cmd.motor_cmd[i].mode = 0x01
        cmd.motor_cmd[i].q = PosStopF
        cmd.motor_cmd[i].kp = 0
        cmd.motor_cmd[i].dq = VelStopF
        cmd.motor_cmd[i].kd = 0
        cmd.motor_cmd[i].tau = 0

    cmd.motor_cmd[0].q = 0.0
    cmd.motor_cmd[0].kp = 0.0
    cmd.motor_cmd[0].dq = 0.0
    cmd.motor_cmd[0].kd = 0.0
    cmd.motor_cmd[0].tau = 1.0

    cmd.motor_cmd[1].q = 0.0
    cmd.motor_cmd[1].kp = 10.0
    cmd.motor_cmd[1].dq = 0.0
    cmd.motor_cmd[1].kd = 1.0
    cmd.motor_cmd[1].tau = 0.0

    now = time.perf_counter()
    

    cmd.crc = crc.Crc(cmd)

    print("CRC:", cmd.crc, "Time cost:", (time.perf_counter() - now)*1000)
