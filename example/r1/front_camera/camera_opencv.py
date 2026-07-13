from unitree_sdk2py.core.channel import ChannelFactoryInitialize
from unitree_sdk2py.r1.video.video_client import VideoClient
import cv2
import numpy as np
import sys


if __name__ == "__main__":
    if len(sys.argv) > 1:
        ChannelFactoryInitialize(0, sys.argv[1])
    else:
        ChannelFactoryInitialize(0)

    client = VideoClient()
    client.SetTimeout(3.0)
    client.Init()

    code, data = client.GetImageSample()

    while code == 0:
        code, data = client.GetImageSample()

        image_data = np.frombuffer(bytes(data), dtype=np.uint8)
        image = cv2.imdecode(image_data, cv2.IMREAD_COLOR)

        cv2.imshow("r1_front_camera", image)
        if cv2.waitKey(20) == 27:
            break

    if code != 0:
        print("Get image sample error. code:", code)
    else:
        cv2.imwrite("r1_front_image.jpg", image)

    cv2.destroyWindow("r1_front_camera")
