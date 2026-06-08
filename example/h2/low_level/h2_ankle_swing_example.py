import sys
import time

import numpy as np

from unitree_sdk2py.comm.motion_switcher.motion_switcher_client import MotionSwitcherClient
from unitree_sdk2py.core.channel import ChannelFactoryInitialize, ChannelPublisher, ChannelSubscriber
from unitree_sdk2py.idl.unitree_hg.msg.dds_ import LowCmd_, LowState_
from unitree_sdk2py.utils.crc import CRC
from unitree_sdk2py.utils.thread import RecurrentThread


H2_NUM_MOTOR = 31
HG_CMD_TOPIC = "rt/lowcmd"
HG_STATE_TOPIC = "rt/lowstate"

Kp = [
    200, 200, 200, 200, 200, 200,     # legs
    200, 200, 200, 200, 200, 200,     # legs
    300, 300, 300,                    # waist
    100, 100, 100, 100, 50, 50, 50,   # arms
    100, 100, 100, 100, 50, 50, 50,   # arms
    50, 10                            # head
]

Kd = [
    3, 3, 3, 3, 3, 3,                 # legs
    3, 3, 3, 3, 3, 3,                 # legs
    5, 5, 5,                          # waist
    2, 2, 2, 2, 2, 2, 2,              # arms
    2, 2, 2, 2, 2, 2, 2,              # arms
    2, 0.1                            # head
]

joint_idx_in_idl = [
    0, 1, 2, 3, 4, 5,
    6, 7, 8, 9, 10, 11,
    12, 13, 14,
    15, 16, 17, 18, 19, 20, 21,
    22, 23, 24, 25, 26, 27, 28,
    29, 30
]


class Mode:
    PR = 0
    AB = 1


class H2JointIndex:
    LeftHipPitch = 0
    LeftHipRoll = 1
    LeftHipYaw = 2
    LeftKnee = 3
    LeftAnkleRoll = 4
    LeftAnkleRollRaw = 4
    LeftAnklePitch = 5
    LeftAnklePitchRaw = 5
    RightHipPitch = 6
    RightHipRoll = 7
    RightHipYaw = 8
    RightKnee = 9
    RightAnkleRoll = 10
    RightAnkleRollRaw = 10
    RightAnklePitch = 11
    RightAnklePitchRaw = 11
    WaistYaw = 12
    WaistRoll = 13
    WaistA = 13
    WaistPitch = 14
    WaistB = 14
    LeftShoulderPitch = 15
    LeftShoulderRoll = 16
    LeftShoulderYaw = 17
    LeftElbow = 18
    LeftWristRoll = 19
    LeftWristpitch = 20
    LeftWristyaw = 21
    RightShoulderPitch = 22
    RightShoulderRoll = 23
    RightShoulderYaw = 24
    RightElbow = 25
    RightWristRoll = 26
    RightWristpitch = 27
    RightWristyaw = 28
    HEAD_PITCH = 29
    HEAD_YAW = 30


class Custom:
    def __init__(self):
        self.time_ = 0.0
        self.control_dt_ = 0.002
        self.duration_ = 3.0
        self.mode_pr_ = Mode.PR
        self.mode_machine_ = 0
        self.update_mode_machine_ = False

        self.low_cmd = LowCmd_()
        self.low_state = None
        self.crc = CRC()

    def Init(self):
        # try to shutdown motion control-related service
        self.msc = MotionSwitcherClient()
        self.msc.SetTimeout(5.0)
        self.msc.Init()

        status, result = self.msc.CheckMode()
        while result.get("name"):
            self.msc.ReleaseMode()
            status, result = self.msc.CheckMode()
            time.sleep(1)

        self.lowcmd_publisher_ = ChannelPublisher(HG_CMD_TOPIC, LowCmd_)
        self.lowcmd_publisher_.Init()

        self.lowstate_subscriber_ = ChannelSubscriber(HG_STATE_TOPIC, LowState_)
        self.lowstate_subscriber_.Init(self.LowStateHandler, 10)

    def Start(self):
        self.control_thread_ = RecurrentThread(
            interval=self.control_dt_, target=self.LowCmdWrite, name="control"
        )
        while not self.update_mode_machine_:
            time.sleep(0.1)
        self.control_thread_.Start()

    def LowStateHandler(self, msg: LowState_):
        self.low_state = msg
        if not self.update_mode_machine_:
            self.mode_machine_ = self.low_state.mode_machine
            self.update_mode_machine_ = True

    def LowCmdWrite(self):
        if self.low_state is None:
            return

        self.time_ += self.control_dt_

        # base fill for all joints we care about
        self.low_cmd.mode_pr = self.mode_pr_
        self.low_cmd.mode_machine = self.mode_machine_

        for i in range(H2_NUM_MOTOR):
            slot = joint_idx_in_idl[i]
            self.low_cmd.motor_cmd[slot].mode = 1
            self.low_cmd.motor_cmd[slot].tau = 0.0
            self.low_cmd.motor_cmd[slot].dq = 0.0
            self.low_cmd.motor_cmd[slot].kp = Kp[i]
            self.low_cmd.motor_cmd[slot].kd = Kd[i]

        if self.time_ < self.duration_:
            ratio = float(np.clip(self.time_ / self.duration_, 0.0, 1.0))
            for i in range(H2_NUM_MOTOR):
                slot = joint_idx_in_idl[i]
                self.low_cmd.motor_cmd[slot].q = (1.0 - ratio) * self.low_state.motor_state[slot].q
        elif self.time_ < self.duration_ * 2.0:
            self.mode_pr_ = Mode.PR
            self.low_cmd.mode_pr = self.mode_pr_
            max_P = np.pi * 30.0 / 180.0
            max_R = np.pi * 30.0 / 180.0
            t = self.time_ - self.duration_
            L_P_des = max_P * np.sin(2.0 * np.pi * t)
            L_R_des = max_R * np.sin(2.0 * np.pi * t)
            R_P_des = max_P * np.sin(2.0 * np.pi * t)
            R_R_des = -max_R * np.sin(2.0 * np.pi * t)
            self.low_cmd.motor_cmd[joint_idx_in_idl[H2JointIndex.LeftAnklePitch]].q = float(L_P_des)
            self.low_cmd.motor_cmd[joint_idx_in_idl[H2JointIndex.LeftAnkleRoll]].q = float(L_R_des)
            self.low_cmd.motor_cmd[joint_idx_in_idl[H2JointIndex.RightAnklePitch]].q = float(R_P_des)
            self.low_cmd.motor_cmd[joint_idx_in_idl[H2JointIndex.RightAnkleRoll]].q = float(R_R_des)
        else:
            self.mode_pr_ = Mode.AB
            self.low_cmd.mode_pr = self.mode_pr_
            max_A = np.pi * 30.0 / 180.0
            max_B = np.pi * 10.0 / 180.0
            t = self.time_ - self.duration_ * 2.0
            L_A_des = +max_A * np.sin(np.pi * t)
            L_B_des = +max_B * np.sin(np.pi * t + np.pi)
            R_A_des = -max_A * np.sin(np.pi * t)
            R_B_des = -max_B * np.sin(np.pi * t + np.pi)
            self.low_cmd.motor_cmd[joint_idx_in_idl[H2JointIndex.LeftAnklePitchRaw]].q = float(L_A_des)
            self.low_cmd.motor_cmd[joint_idx_in_idl[H2JointIndex.LeftAnkleRollRaw]].q = float(L_B_des)
            self.low_cmd.motor_cmd[joint_idx_in_idl[H2JointIndex.RightAnklePitchRaw]].q = float(R_A_des)
            self.low_cmd.motor_cmd[joint_idx_in_idl[H2JointIndex.RightAnkleRollRaw]].q = float(R_B_des)

        self.low_cmd.crc = self.crc.Crc(self.low_cmd)
        self.lowcmd_publisher_.Write(self.low_cmd)


if __name__ == "__main__":
    print("WARNING: Please ensure there are no obstacles around the robot while running this example.")
    input("Press Enter to continue...")

    if len(sys.argv) > 1:
        ChannelFactoryInitialize(0, sys.argv[1])
    else:
        ChannelFactoryInitialize(0)

    custom = Custom()
    custom.Init()
    custom.Start()

    while True:
        time.sleep(1)

