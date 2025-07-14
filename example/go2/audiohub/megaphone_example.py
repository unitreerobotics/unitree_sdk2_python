import time
import sys

from unitree_sdk2py.core.channel import ChannelFactoryInitialize
from unitree_sdk2py.go2.audiohub.audiohub_client import AudioHubClient

#from unitree_sdk2py.idl.idl_dataclass import IDLDataClass
#from unitree_sdk2py.utils.logger import setup_logging
#from unitree_sdk2py.sdk.sdk import create_standard_sdk

if __name__ == "__main__":
    
    if len(sys.argv) < 2:
        print(f"Usage: python3 {sys.argv[0]} networkInterface")
        sys.exit(-1)

    ChannelFactoryInitialize(0, sys.argv[1])

    # Initialize the SDK with a custom name, which is used to identify the SDK instance and its associated logs.
    #sdk = create_standard_sdk('UnitreeGo2SDK')

    # Create a robot instance using the DDS protocol. 
    # `domainId=0` is used as it is currently the standard for all Go2 robots, although a script to change this on the robot is planned.
    # `interface="eth0"` specifies the network interface the DDS should use.
    # Each robot is uniquely identified by a serial number, allowing for multiple robots to be managed by the SDK.
    # Check if the network interface argument is provided


    client = AudioHubClient()
    client.SetTimeout(3.0)
    client.Init()

    # Enable Megaphone
    client.MegaphoneEnter()

    # uploading mp3/wav
    #client.MegaphoneUpload("oiia-oiia-sound.mp3")
    client.MegaphoneUpload("oiia-oiia-sound.wav")
    time.sleep(5)

    # Disable Megaphone
    client.MegaphoneExit()