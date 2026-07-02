import time
import sys

from unitree_sdk2py.core.channel import ChannelFactoryInitialize
from unitree_sdk2py.r1.video.video_client import VideoClient


if __name__ == "__main__":
    if len(sys.argv) > 1:
        ChannelFactoryInitialize(0, sys.argv[1])
    else:
        ChannelFactoryInitialize(0)

    client = VideoClient()
    client.SetTimeout(3.0)
    client.Init()

    print("##################GetImageSample###################")
    code, data = client.GetImageSample()

    if code != 0:
        print("get image sample error. code:", code)
    else:
        image_name = "./r1_front_image.jpg"
        print("ImageName:", image_name)

        with open(image_name, "+wb") as f:
            f.write(bytes(data))

    time.sleep(1)
