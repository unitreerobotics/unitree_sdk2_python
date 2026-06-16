import sys
import time
from dataclasses import dataclass
from typing import Optional

from unitree_sdk2py.core.channel import ChannelFactoryInitialize
from unitree_sdk2py.as2.sport.sport_client import SportClient


@dataclass
class TestOption:
    name: str
    id: int


option_list = [
    TestOption(name="damp", id=0),
    TestOption(name="balance_stand", id=1),
    TestOption(name="stop_move", id=2),
    TestOption(name="stand_down", id=3),
    TestOption(name="recovery_stand", id=4),
    TestOption(name="move", id=5),
    TestOption(name="switch_gait", id=6),
    TestOption(name="speed_level", id=7),
    TestOption(name="get_state", id=8),
    TestOption(name="recovery_switch", id=9),
    TestOption(name="body_height", id=10),
    TestOption(name="stand_up", id=11),
    TestOption(name="enter_leftside_gait", id=12),
    TestOption(name="exit_leftside_gait", id=13),
    TestOption(name="enter_handstand", id=14),
    TestOption(name="exit_handstand", id=15),
    TestOption(name="front_flip", id=16),
    TestOption(name="back_flip", id=17),
    TestOption(name="pose", id=18),
    TestOption(name="euler", id=19),
    TestOption(name="switch_joystick", id=20),
]


class UserInterface:
    def __init__(self):
        self.test_option_: Optional[TestOption] = None

    def convert_to_int(self, input_str: str):
        try:
            return int(input_str)
        except ValueError:
            return None

    def terminal_handle(self):
        input_str = input().strip()

        if input_str == "list":
            for option in option_list:
                print(f"{option.name}, id: {option.id}")
            return

        for option in option_list:
            if input_str == option.name or self.convert_to_int(input_str) == option.id:
                self.test_option_.name = option.name
                self.test_option_.id = option.id
                print(f"Test: {self.test_option_.name}, test_id: {self.test_option_.id}")
                return

        print("No matching test option found.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} networkInterface")
        sys.exit(-1)

    ChannelFactoryInitialize(0, sys.argv[1])

    test_option = TestOption(name="balance_stand", id=1)
    user_interface = UserInterface()
    user_interface.test_option_ = test_option

    sport_client = SportClient()
    sport_client.SetTimeout(25.0)
    sport_client.Init()

    print('Input "list " to list all test option ...')
    res_count = 0
    dt = 0.02  # 50Hz
    next_tick = time.monotonic()
    while True:
        next_tick += dt

        user_interface.terminal_handle()

        res = 1
        if test_option.id < 0:
            # only for list/invalid input
            time.sleep(0.02)
            continue
        if test_option.id == 0:
            res = sport_client.Damp()
        elif test_option.id == 1:
            res = sport_client.BalanceStand()
        elif test_option.id == 2:
            res = sport_client.StopMove()
        elif test_option.id == 3:
            res = sport_client.StandDown()
        elif test_option.id == 4:
            res = sport_client.RecoveryStand()
        elif test_option.id == 5:
            res = sport_client.Move(0.0, 0.0, 0.5)
        elif test_option.id == 6:
            res = sport_client.SwitchGait(0)
        elif test_option.id == 7:
            res = sport_client.SpeedLevel(1)
        elif test_option.id == 8:
            state_map = {}
            res = sport_client.GetState(state_map)
            print(f"fsm_id: {state_map['fsm_id']}")
            print(f"fsm_name: {state_map['fsm_name']}")
            print(f"speed_level: {state_map['speed_level']}")
            print(f"auto_recovery_switch: {state_map['auto_recovery_switch']}")
            print(f"process_state: {state_map['process_state']}")
        elif test_option.id == 9:
            res = sport_client.SetAutoRecovery(0)
        elif test_option.id == 10:
            res = sport_client.BodyHeight(0.3)
        elif test_option.id == 11:
            res = sport_client.StandUp()
        elif test_option.id == 12:
            res = sport_client.LeftSideGait(1)
        elif test_option.id == 13:
            res = sport_client.LeftSideGait(0)
        elif test_option.id == 14:
            res = sport_client.HandStand(1)
        elif test_option.id == 15:
            res = sport_client.HandStand(0)
        elif test_option.id == 16:
            res = sport_client.FrontFlip()
        elif test_option.id == 17:
            res = sport_client.BackFlip()
        elif test_option.id == 18:
            res = sport_client.BodyPosition(0.2, 0.2, -0.2, 0.2)
        elif test_option.id == 19:
            res = sport_client.Euler(0.2, 0.3, 0.3)
        elif test_option.id == 20:
            res = sport_client.SwitchJoystick(0)

        if res < 0:
            res_count += 1
            print(f"Request error for: {option_list[test_option.id].name}, code: {res}, count: {res_count}")
        else:
            res_count = 0
            print(f"Request successed: {option_list[test_option.id].name}, code: {res}")

        time.sleep(max(0.0, next_tick - time.monotonic()))
