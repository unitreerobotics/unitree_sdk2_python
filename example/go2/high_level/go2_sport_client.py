#!/usr/bin/env python3
"""
Interactive high-level control demo for Unitree Go2 Edu
======================================================

* Connects via DDS to the robot (`eth0`, `enp2s0`, …).
* Lets you pick a command from a dynamic list and executes it via SportClient.
* Covers **all** V1.1.6 high-level / AI-switcher functions that are exposed in the
  current C++ header.  
  (`WalkStair` was removed in V1.1.6 → no longer listed or called.)

Run:

    python3 go2_sport_client.py <networkInterface>

Example:

    python3 go2_sport_client.py eth0
"""

import time
import sys
from dataclasses import dataclass

from unitree_sdk2py.core.channel import ChannelFactoryInitialize
from unitree_sdk2py.go2.sport.sport_client import SportClient


# --------------------------------------------------------------------------- #
#  Option definitions                                                         #
# --------------------------------------------------------------------------- #
@dataclass
class TestOption:
    name: str
    id: int


option_list = [
    # legacy “sport” basic control
    TestOption("damp", 0),
    TestOption("stand_up", 1),
    TestOption("stand_down", 2),
    TestOption("move_forward", 3),
    TestOption("move_lateral", 4),
    TestOption("move_rotate", 5),
    TestOption("stop_move", 6),
    TestOption("switch_gait_0", 7),
    TestOption("switch_gait_1", 8),
    TestOption("balanced_stand", 9),
    TestOption("recovery", 10),
    # legacy flips
    TestOption("left_flip", 11),
    TestOption("back_flip", 12),
    # AI / motion-switcher V2.0
    TestOption("free_walk", 13),
    TestOption("free_bound", 14),
    TestOption("free_avoid", 15),
    TestOption("walk_upright", 17),
    TestOption("cross_step", 18),
    TestOption("free_jump", 19),
    TestOption("hand_stand", 20),
    TestOption("classic_walk", 21),
    TestOption("static_walk", 22),
    TestOption("trot_run", 23),
    TestOption("auto_recover_on", 24),
    TestOption("auto_recover_off", 25),
    TestOption("switch_avoid_mode", 26),
]


# --------------------------------------------------------------------------- #
#  Simple terminal UI helper                                                 #
# --------------------------------------------------------------------------- #
class UserInterface:
    def __init__(self, option_holder: TestOption):
        self.option_holder = option_holder

    def _to_int(self, s):
        try:
            return int(s)
        except ValueError:
            return None

    def prompt(self):
        user_in = input("Enter command (type 'list' to see all commands): ").strip()

        # show list
        if user_in == "list":
            print("Available commands:")
            for opt in option_list:
                print(f"  {opt.name}  (id {opt.id})")
            return

        # match name or id
        for opt in option_list:
            if user_in == opt.name or self._to_int(user_in) == opt.id:
                self.option_holder.name = opt.name
                self.option_holder.id = opt.id
                print(f"Selected: {opt.name} (id {opt.id})")
                return

        print("No match. Type 'list' to see available commands.")


# --------------------------------------------------------------------------- #
#  Main demo                                                                  #
# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    # network interface must be provided
    if len(sys.argv) < 2:
        print(f"Usage: python3 {sys.argv[0]} <networkInterface>")
        sys.exit(-1)

    print("WARNING: ensure the robot has free space around it.")
    input("Press Enter to continue...")

    # DDS / RPC initialisation
    ChannelFactoryInitialize(0, sys.argv[1])

    # prepare option holder + UI
    current_opt = TestOption("", -1)
    ui = UserInterface(current_opt)

    # initialise SportClient
    sport = SportClient()
    sport.SetTimeout(10.0)
    sport.Init()

    # main loop
    while True:
        ui.prompt()
        cmd = current_opt.id

        # ---------- legacy sport ----------
        if   cmd == 0:  sport.Damp()
        elif cmd == 1:  sport.StandUp()
        elif cmd == 2:  sport.StandDown()
        elif cmd == 3:  sport.Move(0.3, 0,   0)
        elif cmd == 4:  sport.Move(0,   0.3, 0)
        elif cmd == 5:  sport.Move(0,   0,   0.5)
        elif cmd == 6:  sport.StopMove()
        elif cmd == 7:  sport.SwitchGait(0)
        elif cmd == 8:  sport.SwitchGait(1)
        elif cmd == 9:  sport.BalanceStand()
        elif cmd == 10: sport.RecoveryStand()
        elif cmd == 11: print("ret:", sport.LeftFlip())
        elif cmd == 12: print("ret:", sport.BackFlip())

        # ---------- AI / V2.0 switcher ----------
        elif cmd == 13: print("ret:", sport.FreeWalk(True))
        elif cmd == 14:
            print("ret:", sport.FreeBound(True)); time.sleep(2)
            print("ret:", sport.FreeBound(False))
        elif cmd == 15:
            print("ret:", sport.FreeAvoid(True)); time.sleep(2)
            print("ret:", sport.FreeAvoid(False))
        elif cmd == 17:
            print("ret:", sport.WalkUpright(True)); time.sleep(4)
            print("ret:", sport.WalkUpright(False))
        elif cmd == 18:
            print("ret:", sport.CrossStep(True)); time.sleep(4)
            print("ret:", sport.CrossStep(False))
        elif cmd == 19:
            print("ret:", sport.FreeJump(True)); time.sleep(4)
            print("ret:", sport.FreeJump(False))
        elif cmd == 20:
            print("ret:", sport.HandStand(True)); time.sleep(2)
            print("ret:", sport.HandStand(False))
        elif cmd == 21:
            print("ret:", sport.ClassicWalk(True)); time.sleep(2)
            print("ret:", sport.ClassicWalk(False))
        elif cmd == 22: print("ret:", sport.StaticWalk())
        elif cmd == 23: print("ret:", sport.TrotRun())
        elif cmd == 24: print("ret:", sport.AutoRecoverSet(True))
        elif cmd == 25: print("ret:", sport.AutoRecoverSet(False))
        elif cmd == 26: print("ret:", sport.SwitchAvoidMode())

        time.sleep(1)
