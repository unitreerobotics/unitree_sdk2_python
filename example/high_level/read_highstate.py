import time
import sys
from unitree_sdk2py.core.channel import ChannelSubscriber, ChannelFactoryInitialize

from unitree_sdk2py.idl.default import unitree_go_msg_dds__SportModeState_
from unitree_sdk2py.idl.unitree_go.msg.dds_ import SportModeState_


def HighStateHandler(msg: SportModeState_):
    print("Position: ", msg.position)
    print("Velocity: ", msg.velocity)
    print("Yaw velocity: ", msg.yaw_speed)
    print("Foot position in body frame: ", msg.foot_position_body)
    print("Foot velocity in body frame: ", msg.foot_speed_body)


if __name__ == "__main__":
    # sys.argv[1]: name of the network interface
    ChannelFactoryInitialize(0, sys.argv[1])
    sub = ChannelSubscriber("rt/sportmodestate", SportModeState_)
    sub.Init(HighStateHandler, 10)

    while True:
        time.sleep(10.0)
