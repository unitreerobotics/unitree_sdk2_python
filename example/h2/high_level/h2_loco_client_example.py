import sys
import time
from dataclasses import dataclass

from unitree_sdk2py.core.channel import ChannelFactoryInitialize
from unitree_sdk2py.h2.loco.h2_loco_client import LocoClient


@dataclass
class TestOption:
    name: str
    id: int


option_list = [
    TestOption(name="damp", id=0),
    TestOption(name="start", id=1),
    TestOption(name="stand_up", id=2),
    TestOption(name="zero_torque", id=3),
    TestOption(name="stop_move", id=4),
    TestOption(name="get_fsm_id", id=5),
    TestOption(name="get_fsm_mode", id=6),
    TestOption(name="set_fsm_id", id=7),
    TestOption(name="set_velocity", id=8),
    TestOption(name="move", id=9),
    TestOption(name="switch_move_mode", id=10),
    TestOption(name="set_speed_mode", id=11),
]


class UserInterface:
    def __init__(self):
        self.test_option_ = None

    def convert_to_int(self, input_str):
        try:
            return int(input_str)
        except ValueError:
            return None

    def terminal_handle(self):
        input_str = input("Enter id or name: \n")

        if input_str == "list":
            self.test_option_.name = None
            self.test_option_.id = None
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
    print("WARNING: Please ensure there are no obstacles around the robot while running this example.")
    input("Press Enter to continue...")

    if len(sys.argv) > 1:
        ChannelFactoryInitialize(0, sys.argv[1])
    else:
        ChannelFactoryInitialize(0)

    test_option = TestOption(name=None, id=None)
    user_interface = UserInterface()
    user_interface.test_option_ = test_option

    sport_client = LocoClient()
    sport_client.SetTimeout(10.0)
    sport_client.Init()

    print("Input \"list\" to list all test option ...")
    while True:
        user_interface.terminal_handle()

        print(f"Updated Test Option: Name = {test_option.name}, ID = {test_option.id}\n")

        if test_option.id == 0:
            sport_client.Damp()
        elif test_option.id == 1:
            sport_client.Start()
        elif test_option.id == 2:
            sport_client.StandUp()
        elif test_option.id == 3:
            sport_client.ZeroTorque()
        elif test_option.id == 4:
            sport_client.StopMove()
        elif test_option.id == 5:
            code, fsm_id = sport_client.GetFsmId()
            print("GetFsmId:", code, fsm_id)
        elif test_option.id == 6:
            code, fsm_mode = sport_client.GetFsmMode()
            print("GetFsmMode:", code, fsm_mode)
        elif test_option.id == 7:
            sport_client.SetFsmId(4)
        elif test_option.id == 8:
            sport_client.SetVelocity(0.0, 0.0, 1.0, 4.0)
        elif test_option.id == 9:
            sport_client.Move(0.0, 0.0, 2)
        elif test_option.id == 10:
            sport_client.SwitchMoveMode(True)
        elif test_option.id == 11:
            sport_client.SetSpeedMode(1)

        time.sleep(1)

