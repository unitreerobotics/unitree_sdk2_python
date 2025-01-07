import time
import sys
from unitree_sdk2py.core.channel import ChannelSubscriber, ChannelFactoryInitialize

from unitree_sdk2py.idl.default import unitree_go_msg_dds__WirelessController_
from unitree_sdk2py.idl.unitree_go.msg.dds_ import WirelessController_


key_state = [
    ["R1", 0],
    ["L1", 0],
    ["start", 0],
    ["select", 0],
    ["R2", 0],
    ["L2", 0],
    ["F1", 0],
    ["F2", 0],
    ["A", 0],
    ["B", 0],
    ["X", 0],
    ["Y", 0],
    ["up", 0],
    ["right", 0],
    ["down", 0],
    ["left", 0],
]


def WirelessControllerHandler(msg: WirelessController_):
    global key_state
    print("lx: ", msg.lx)
    print("lx: ", msg.ly)
    print("lx: ", msg.rx)
    print("lx: ", msg.ry)
    print("keys: ", msg.keys)

    #Update key state
    for i in range(16):
        key_state[i][1] = (msg.keys & (1 << i)) >> i

    print(key_state)



if __name__ == "__main__":
    if len(sys.argv)>1:
        ChannelFactoryInitialize(0, sys.argv[1])
    else:
        ChannelFactoryInitialize(0)
        
    sub = ChannelSubscriber("rt/wirelesscontroller", WirelessController_)
    sub.Init(WirelessControllerHandler, 10)
    
    while True:
        time.sleep(10.0)
