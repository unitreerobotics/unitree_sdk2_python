import sys
import time
import cv2
import numpy as np
from unitree_sdk2py.core.channel import ChannelFactoryInitialize
from unitree_sdk2py.go2.sport.sport_client import SportClient
from unitree_sdk2py.go2.video.video_client import VideoClient

def main():
    """
    Main function to control the robot's pose and capture images.
    """
    if len(sys.argv) > 1:
        ChannelFactoryInitialize(0, sys.argv[1])
    else:
        ChannelFactoryInitialize(0)

    # Create clients
    sport_client = SportClient()
    sport_client.SetTimeout(10.0)
    sport_client.Init()

    video_client = VideoClient()
    video_client.SetTimeout(3.0)
    video_client.Init()

    print("WARNING: Please ensure there are no obstacles around the robot.")
    input("Press Enter to continue...")

    try:
        while True:
            # Command the robot to stand in a balanced pose
            print("Commanding robot to stand...")
            sport_client.BalanceStand()
            time.sleep(2)  # Wait for the robot to stabilize

            # Capture an image
            print("Capturing image...")
            code, data = video_client.GetImageSample()

            if code == 0:
                # Convert to numpy image
                image_data = np.frombuffer(bytes(data), dtype=np.uint8)
                image = cv2.imdecode(image_data, cv2.IMREAD_COLOR)

                # Save the image with a timestamp
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                filename = f"capture_{timestamp}.jpg"
                cv2.imwrite(filename, image)
                print(f"Image saved as {filename}")
            else:
                print(f"Failed to capture image, error code: {code}")

            # Wait for a few seconds before repeating
            print("Waiting for 5 seconds...")
            time.sleep(5)

    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        # Optional: command the robot to lie down when exiting
        print("Commanding robot to lie down...")
        sport_client.StandDown()
        time.sleep(2)


if __name__ == "__main__":
    main()
