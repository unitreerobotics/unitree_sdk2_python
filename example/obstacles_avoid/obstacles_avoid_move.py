import time
import sys

from unitree_sdk2py.core.channel import ChannelFactoryInitialize
from unitree_sdk2py.go2.obstacles_avoid.obstacles_avoid_client import ObstaclesAvoidClient

if __name__ == "__main__":
    if len(sys.argv)>1:
        ChannelFactoryInitialize(0, sys.argv[1])
    else:
        ChannelFactoryInitialize(0)

    client = ObstaclesAvoidClient()
    client.SetTimeout(3.0)
    client.Init()

    client.SwitchSet(False)
    time.sleep(2)

    client.SwitchSet(True)
    time.sleep(2)

    client.UseRemoteCommandFromApi(True)
    time.sleep(2)
    while True:
        client.Move(0.5, 0.0, 0.0)
        time.sleep(0.02)
        