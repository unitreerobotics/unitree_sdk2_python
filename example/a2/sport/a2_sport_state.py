import sys
import time

from unitree_sdk2py.core.channel import ChannelFactoryInitialize, ChannelSubscriber
from unitree_sdk2py.idl.unitree_go.msg.dds_ import SportModeState_


TOPIC_HIGHSTATE = "rt/lf/sportmodestate"

FSM_STATE_STR = [
    "PASSIVE",
    "STAND_DOWN",
    "STAND_UP",
    "DEFAULT_MODE",
    "RUNNING_MODE",
    "CLIMB_MODE",
    "LEFT_SIDE_GAIT",
    "RIGHT_SIDE_GAIT",
    "HANDSTAND",
    "BIPED_STAND",
    "FRONT_FLIP",
    "BACK_FLIP",
    "RECOVERY",
    "BASE_HEIGHT_CTRL",
]


class Custom:
    def __init__(self):
        self.state = None

        self.suber = ChannelSubscriber(TOPIC_HIGHSTATE, SportModeState_)
        self.suber.Init(self.HighStateHandler, 10)

    def HighStateHandler(self, msg: SportModeState_):
        self.state = msg
        print(f"Position: {self.state.position[0]}, {self.state.position[1]}, {self.state.position[2]}")
        print(f"Velocity: {self.state.velocity[0]}, {self.state.velocity[1]}, {self.state.velocity[2]}")
        print(f"Mode: {FSM_STATE_STR[int(self.state.mode)]}")
        print(f"Progress: {self.state.progress}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} networkInterface")
        sys.exit(-1)

    ChannelFactoryInitialize(0, sys.argv[1])
    custom = Custom()

    while True:
        time.sleep(10)

