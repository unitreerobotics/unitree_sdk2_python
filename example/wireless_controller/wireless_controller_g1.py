import time
import sys
from unitree_sdk2py.core.channel import ChannelPublisher, ChannelFactoryInitialize

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


def encode_keys(keys):
    key_map = {key[0]: i for i, key in enumerate(key_state)}
    encoded_value = 0

    for key in keys:
        if key in key_map:
            encoded_value |= 1 << key_map[key]
        else:
            print(f"Warning: {key} is not a valid key")

    return encoded_value


if __name__ == "__main__":
    ChannelFactoryInitialize(0, sys.argv[1])

    pub = ChannelPublisher("rt/wirelesscontroller", WirelessController_)
    pub.Init()
    smp = unitree_go_msg_dds__WirelessController_()

    smp.ly = 0.5
    for i in range(100):
        pub.Write(smp, timeout=1.0)
        time.sleep(0.01)

    smp.ly = 0
    pub.Write(smp)

    # smp.keys = encode_keys(["L1", "B"])
    # for i in range(3):
    #     pub.Write(smp, timeout=1)
    #     time.sleep(0.1)

    pub.Close()
