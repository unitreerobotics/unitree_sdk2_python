import struct
import sys
import time

import numpy as np

from unitree_sdk2py.comm.motion_switcher.motion_switcher_client import MotionSwitcherClient
from unitree_sdk2py.core.channel import ChannelFactoryInitialize, ChannelPublisher, ChannelSubscriber
from unitree_sdk2py.idl.default import unitree_hg_msg_dds__LowCmd_
from unitree_sdk2py.idl.unitree_hg.msg.dds_ import IMUState_, LowCmd_, LowState_
from unitree_sdk2py.utils.crc import CRC
from unitree_sdk2py.utils.thread import RecurrentThread

H2_NUM_MOTOR = 31

Kp = [
    150, 150, 150, 250, 60, 90,
    150, 150, 150, 250, 60, 90,
    200, 200, 200,
    90, 60, 20, 60, 4, 4, 4,
    90, 60, 20, 60, 4, 4, 4,
    30, 30,
]

Kd = [
    2.0, 2.0, 2.0, 2.0, 0.3, 0.1,
    2.0, 2.0, 2.0, 2.0, 0.3, 0.1,
    2.5, 5.0, 5.0,
    2.0, 1.0, 0.4, 1.0, 0.2, 0.2, 0.2,
    2.0, 1.0, 0.4, 1.0, 0.2, 0.2, 0.2,
    1.0, 1.0,
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
        self.control_dt_ = 0.002  # [2ms]
        self.duration_ = 3.0      # [3 s]
        self.counter_ = 0
        self.mode_pr_ = Mode.PR
        self.mode_machine_ = 0
        self.low_cmd = unitree_hg_msg_dds__LowCmd_()
        self.low_state = None
        self.crc = CRC()
        self.gamepad_A = False
        self.gamepad_B = False
        self.gamepad_X = False
        self.gamepad_Y = False

    def Init(self):
        self.msc = MotionSwitcherClient()
        self.msc.SetTimeout(5.0)
        self.msc.Init()

        status, result = self.msc.CheckMode()
        while result and result.get("name"):
            code, _ = self.msc.ReleaseMode()
            if code != 0:
                print("Failed to switch to Release Mode")
            time.sleep(5)
            status, result = self.msc.CheckMode()

        self.lowcmd_publisher_ = ChannelPublisher("rt/lowcmd", LowCmd_)
        self.lowcmd_publisher_.Init()

        self.lowstate_subscriber = ChannelSubscriber("rt/lowstate", LowState_)
        self.lowstate_subscriber.Init(self.LowStateHandler, 1)

        self.imutorso_subscriber = ChannelSubscriber("rt/secondary_imu", IMUState_)
        self.imutorso_subscriber.Init(self.ImuTorsoHandler, 1)

    def Start(self):
        self.lowCmdWriteThreadPtr = RecurrentThread(
            interval=self.control_dt_, target=self.LowCmdWrite, name="control"
        )
        self.lowCmdWriteThreadPtr.Start()

    def _update_gamepad(self, wireless_remote):
        btn_value = struct.unpack_from("<H", bytes(wireless_remote), 2)[0]
        self.gamepad_A = bool(btn_value & (1 << 8))
        self.gamepad_B = bool(btn_value & (1 << 9))
        self.gamepad_X = bool(btn_value & (1 << 10))
        self.gamepad_Y = bool(btn_value & (1 << 11))

    def ImuTorsoHandler(self, msg: IMUState_):
        rpy = msg.rpy
        if self.counter_ % 500 == 0:
            print(f"IMU.torso.rpy: {rpy[0]:.2f} {rpy[1]:.2f} {rpy[2]:.2f}")

    def LowStateHandler(self, msg: LowState_):
        if msg.crc != self.crc.Crc(msg):
            print("[ERROR] CRC Error")
            return

        self.low_state = msg

        for i in range(H2_NUM_MOTOR):
            if msg.motor_state[i].motorstate and i <= H2JointIndex.RightAnkleRoll:
                print(f"[ERROR] motor {i} with code {msg.motor_state[i].motorstate}")

        self._update_gamepad(msg.wireless_remote)

        if self.mode_machine_ != msg.mode_machine:
            if self.mode_machine_ == 0:
                print(f"H2 type: {msg.mode_machine}")
            self.mode_machine_ = msg.mode_machine

        self.counter_ += 1
        if self.counter_ % 500 == 0:
            self.counter_ = 0
            rpy = msg.imu_state.rpy
            print(f"IMU.pelvis.rpy: {rpy[0]:.2f} {rpy[1]:.2f} {rpy[2]:.2f}")

            print(f"gamepad_.A.pressed: {int(self.gamepad_A)}")
            print(f"gamepad_.B.pressed: {int(self.gamepad_B)}")
            print(f"gamepad_.X.pressed: {int(self.gamepad_X)}")
            print(f"gamepad_.Y.pressed: {int(self.gamepad_Y)}")

            ms = msg.motor_state
            print(f"All {H2_NUM_MOTOR} Motors:", end="")
            print("\nmode: ", end="")
            for i in range(H2_NUM_MOTOR):
                print(f"{ms[i].mode},", end="")
            print("\npos: ", end="")
            for i in range(H2_NUM_MOTOR):
                print(f"{ms[i].q:.2f},", end="")
            print("\nvel: ", end="")
            for i in range(H2_NUM_MOTOR):
                print(f"{ms[i].dq:.2f},", end="")
            print("\ntau_est: ", end="")
            for i in range(H2_NUM_MOTOR):
                print(f"{ms[i].tau_est:.2f},", end="")
            print("\ntemperature: ", end="")
            for i in range(H2_NUM_MOTOR):
                print(f"{ms[i].temperature[0]},{ms[i].temperature[1]};", end="")
            print("\nvol: ", end="")
            for i in range(H2_NUM_MOTOR):
                print(f"{ms[i].vol:.2f},", end="")
            print("\nsensor: ", end="")
            for i in range(H2_NUM_MOTOR):
                print(f"{ms[i].sensor[0]},{ms[i].sensor[1]};", end="")
            print("\nmotorstate: ", end="")
            for i in range(H2_NUM_MOTOR):
                print(f"{ms[i].motorstate},", end="")
            print("\nreserve: ", end="")
            for i in range(H2_NUM_MOTOR):
                print(
                    f"{ms[i].reserve[0]},{ms[i].reserve[1]},"
                    f"{ms[i].reserve[2]},{ms[i].reserve[3]};",
                    end="",
                )
            print()

    def LowCmdWrite(self):
        if self.low_state is None:
            return

        self.time_ += self.control_dt_
        self.low_cmd.mode_pr = self.mode_pr_
        self.low_cmd.mode_machine = self.mode_machine_

        for i in range(H2_NUM_MOTOR):
            self.low_cmd.motor_cmd[i].mode = 1
            self.low_cmd.motor_cmd[i].tau = 0.0
            self.low_cmd.motor_cmd[i].q = 0.0
            self.low_cmd.motor_cmd[i].dq = 0.0
            self.low_cmd.motor_cmd[i].kp = Kp[i]
            self.low_cmd.motor_cmd[i].kd = Kd[i]

        if self.time_ < self.duration_:
            # [Stage 1]: set robot to zero posture
            for i in range(H2_NUM_MOTOR):
                ratio = np.clip(self.time_ / self.duration_, 0.0, 1.0)
                self.low_cmd.motor_cmd[i].q = (1.0 - ratio) * self.low_state.motor_state[i].q
        elif self.time_ < self.duration_ * 2:
            # [Stage 2]: swing ankle using PR mode
            self.mode_pr_ = Mode.PR
            max_P = np.pi * 30.0 / 180.0
            max_R = np.pi * 10.0 / 180.0
            t = self.time_ - self.duration_
            L_P_des = max_P * np.sin(2.0 * np.pi * t)
            L_R_des = max_R * np.sin(2.0 * np.pi * t)
            R_P_des = max_P * np.sin(2.0 * np.pi * t)
            R_R_des = -max_R * np.sin(2.0 * np.pi * t)

            self.low_cmd.motor_cmd[H2JointIndex.LeftAnklePitch].q = L_P_des
            self.low_cmd.motor_cmd[H2JointIndex.LeftAnkleRoll].q = L_R_des
            self.low_cmd.motor_cmd[H2JointIndex.RightAnklePitch].q = R_P_des
            self.low_cmd.motor_cmd[H2JointIndex.RightAnkleRoll].q = R_R_des

        self.low_cmd.crc = self.crc.Crc(self.low_cmd)
        self.lowcmd_publisher_.Write(self.low_cmd)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: h2_ankle_swing_example network_interface")
        sys.exit(0)

    ChannelFactoryInitialize(0, sys.argv[1])

    custom = Custom()
    custom.Init()
    custom.Start()

    while True:
        time.sleep(10)
