import time
import os
import sys

from unitree_sdk2py.core.channel import ChannelFactortyInitialize
from unitree_sdk2py.go2.video.video_client import VideoClient

if __name__ == "__main__":
    if len(sys.argv)>1:
        ChannelFactortyInitialize(0, sys.argv[1])
    else:
        ChannelFactortyInitialize(0)

    client = VideoClient()
    client.SetTimeout(3.0)
    client.Init()

    print("##################GetImageSample###################")
    code, data = client.GetImageSample()

    if code != 0:
        print("get image sample error. code:", code)
    else:
        imageName = "./img.jpg"
        print("ImageName:", imageName)

        with open(imageName, "+wb") as f:
            f.write(bytes(data))

    time.sleep(1)
