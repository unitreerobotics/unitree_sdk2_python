import time
import sys
from unitree_sdk2py.core.channel import ChannelSubscriber, ChannelFactoryInitialize
from unitree_sdk2py.b2.sport.sport_client import SportClient
import math
from dataclasses import dataclass

@dataclass
class TestOption:
    name: str
    id: int

option_list = [
    TestOption(name="Damp", id=0),         
    TestOption(name="BalanceStand", id=1),     
    TestOption(name="StopMove", id=2),   
    TestOption(name="StandUp", id=3),         
    TestOption(name="StandDown", id=4),    
    TestOption(name="RecoveryStand", id=5),  
    TestOption(name="Move", id=6),    
    TestOption(name="FreeWalk", id=7),       
    TestOption(name="ClassicWalk", id=8)    
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

    if len(sys.argv) < 2:
        print(f"Usage: python3 {sys.argv[0]} networkInterface")
        sys.exit(-1)

    print("WARNING: Please ensure there are no obstacles around the robot while running this example.\n"
      "NOTE: Some interfaces are not demonstrated in this example for safety reasons. "
      "If you need to use them, please contact technical support: https://serviceconsole.unitree.com/index.html#/")
    input("Press Enter to continue...")

    ChannelFactoryInitialize(0, sys.argv[1])

    test_option = TestOption(name=None, id=None) 
    user_interface = UserInterface()
    user_interface.test_option_ = test_option

    sport_client = SportClient()  
    sport_client.SetTimeout(10.0)
    sport_client.Init()

    print("Input \"list\" to list all test option ...")

    while True:
        user_interface.terminal_handle()

        print(f"Updated Test Option: Name = {test_option.name}, ID = {test_option.id}")

        if test_option.id == 0:
            print(f"ret:{sport_client.Damp()}")
        elif test_option.id == 1:
            print(f"ret:{sport_client.BalanceStand()}")
        elif test_option.id == 2:
            print(f"ret:{sport_client.StopMove()}")
        elif test_option.id == 3:
            print(f"ret:{sport_client.StandUp()}")
        elif test_option.id == 4:
            print(f"ret:{sport_client.StandDown()}")
        elif test_option.id == 5:
            print(f"ret:{sport_client.RecoveryStand()}")
        elif test_option.id == 6:
            print(f"ret:{sport_client.Move(0.5,0.0,0.0)}")
        elif test_option.id == 7:
            print(f"ret:{sport_client.FreeWalk()}")
        elif test_option.id == 8:
            print(f"ret:{sport_client.ClassicWalk(True)}")
            print(f"ret:{sport_client.Move(0.1,0.0,0.0)}")
            time.sleep(2)
            print(f"ret:{sport_client.ClassicWalk(False)}")
            print(f"ret:{sport_client.Move(-0.3,0.0,0.0)}")
            time.sleep(2)

        time.sleep(1)
