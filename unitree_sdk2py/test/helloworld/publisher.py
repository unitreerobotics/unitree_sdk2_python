import time

from unitree_sdk2py.core.channel import ChannelPublisher, ChannelFactortyInitialize
from helloworld import HelloWorld

ChannelFactortyInitialize()

pub = ChannelPublisher("topic", HelloWorld)
pub.Init()

for i in range(30):
    msg = HelloWorld("Hello world. time:" + str(time.time()))
    # msg.data = "Hello world. time:" + str(time.time())

    if pub.Write(msg, 0.5):
        print("publish success. msg:", msg)
    else:
        print("publish error.")

    time.sleep(1)

pub.Close()