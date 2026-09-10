import sys
import time

from unitree_sdk2py.core.channel import ChannelFactoryInitialize
from unitree_sdk2py.a2.audio.audio_client import AudioClient


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} networkInterface")
        sys.exit(-1)

    ChannelFactoryInitialize(0, sys.argv[1])

    audio_client = AudioClient()
    audio_client.SetTimeout(10.0)
    audio_client.Init()

    ret = audio_client.GetVolume()
    print("debug GetVolume: ", ret)

    audio_client.SetVolume(85)

    ret = audio_client.GetVolume()
    print("debug GetVolume: ", ret)

    audio_client.TtsMaker("大家好!我是宇树科技的机器人。语音开发测试例程运行成功！ 很高兴认识你！", 0)
    time.sleep(8)
    audio_client.TtsMaker("接下来测试灯带开发例程！", 0)
    time.sleep(1)
    audio_client.LedControl(255, 0, 0)
    time.sleep(1)
    audio_client.LedControl(0, 255, 0)
    time.sleep(1)
    audio_client.LedControl(0, 0, 255)

    time.sleep(3)
    audio_client.TtsMaker("测试完毕，谢谢大家！", 0)

