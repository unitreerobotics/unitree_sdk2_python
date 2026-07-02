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

HG_CMD_TOPIC = "rt/lowcmd"
HG_IMU_TORSO = "rt/secondary_imu"
HG_STATE_TOPIC = "rt/lowstate"

R1_NUM_MOTOR = 26

Kp = [
    200, 200, 200, 200, 200, 200,
    200, 200, 200, 200, 200, 200,
    300, 300,
    100, 100, 100, 100, 50,
    100, 100, 100, 100, 50,
    50, 10,
]

Kd = [
    3, 3, 3, 3, 3, 3,
    3, 3, 3, 3, 3, 3,
    5, 5,
    2, 2, 2, 2, 2,
    2, 2, 2, 2, 2,
    2, 0.1,
]

JOINT_IDX_IN_IDL = [
    0, 1, 2, 3, 4, 5,
    6, 7, 8, 9, 10, 11,
    12, 13,
    15, 16, 17, 18, 19,
    22, 23, 24, 25, 26,
    29, 30,
]


class Mode:
    PR = 0
    AB = 1


class R1JointIndex:
    LeftHipPitch = 0
    LeftHipRoll = 1
    LeftHipYaw = 2
    LeftKnee = 3
    LeftAnklePitch = 4
    LeftAnkleB = 4
    LeftAnkleRoll = 5
    LeftAnkleA = 5
    RightHipPitch = 6
    RightHipRoll = 7
    RightHipYaw = 8
    RightKnee = 9
    RightAnklePitch = 10
    RightAnkleB = 10
    RightAnkleRoll = 11
    RightAnkleA = 11
    WaistRoll = 12
    WaistYaw = 13
    LeftShoulderPitch = 14
    LeftShoulderRoll = 15
    LeftShoulderYaw = 16
    LeftElbow = 17
    LeftWristRoll = 18
    RightShoulderPitch = 19
    RightShoulderRoll = 20
    RightShoulderYaw = 21
    RightElbow = 22
    RightWristRoll = 23
    HEAD_PITCH = 24
    HEAD_YAW = 25


class Custom:
    def __init__(self):
        self.time_ = 0.0
        self.control_dt_ = 0.002
        self.duration_ = 3.0
        self.counter_ = 0
        self.mode_pr_ = Mode.PR
        self.mode_machine_ = 0
        self.low_cmd = unitree_hg_msg_dds__LowCmd_()
        self.low_state = None
        self.motor_q = [0.0] * R1_NUM_MOTOR
        self.motor_dq = [0.0] * R1_NUM_MOTOR
        self.gamepad_A = False
        self.gamepad_B = False
        self.gamepad_X = False
        self.gamepad_Y = False
        self.crc = CRC()

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

        self.lowcmd_publisher_ = ChannelPublisher(HG_CMD_TOPIC, LowCmd_)
        self.lowcmd_publisher_.Init()

        self.lowstate_subscriber = ChannelSubscriber(HG_STATE_TOPIC, LowState_)
        self.lowstate_subscriber.Init(self.LowStateHandler, 1)

        self.imutorso_subscriber = ChannelSubscriber(HG_IMU_TORSO, IMUState_)
        self.imutorso_subscriber.Init(self.ImuTorsoHandler, 1)

    def Start(self):
        self.lowCmdWriteThreadPtr = RecurrentThread(
            interval=self.control_dt_, target=self.LowCmdWrite, name="r1_lowcmd"
        )
        self.lowCmdWriteThreadPtr.Start()

    def _update_gamepad(self, wireless_remote):
        btn_value = struct.unpack_from("<H", bytes(wireless_remote), 2)[0]
        self.gamepad_A = bool(btn_value & (1 << 8))
        self.gamepad_B = bool(btn_value & (1 << 9))
        self.gamepad_X = bool(btn_value & (1 << 10))
        self.gamepad_Y = bool(btn_value & (1 << 11))

    def ImuTorsoHandler(self, msg: IMUState_):
        if self.counter_ % 500 == 0:
            rpy = msg.rpy
            print(f"IMU.torso.rpy: {rpy[0]:.2f} {rpy[1]:.2f} {rpy[2]:.2f}")

    def LowStateHandler(self, msg: LowState_):
        if msg.crc != self.crc.Crc(msg):
            print("[ERROR] CRC Error")
            return

        self.low_state = msg

        for i, idl_idx in enumerate(JOINT_IDX_IN_IDL):
            motor_state = msg.motor_state[idl_idx]
            self.motor_q[i] = motor_state.q
            self.motor_dq[i] = motor_state.dq
            if motor_state.motorstate and i <= R1JointIndex.RightAnkleRoll:
                print(f"[ERROR] motor {idl_idx} with code {motor_state.motorstate}")

        self._update_gamepad(msg.wireless_remote)

        if self.mode_machine_ != msg.mode_machine:
            if self.mode_machine_ == 0:
                print(f"R1 type: {msg.mode_machine}")
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
            print(f"All {R1_NUM_MOTOR} Motors:", end="")
            print("\nmode: ", end="")
            for idl_idx in JOINT_IDX_IN_IDL:
                print(f"{ms[idl_idx].mode},", end="")
            print("\npos: ", end="")
            for idl_idx in JOINT_IDX_IN_IDL:
                print(f"{ms[idl_idx].q:.2f},", end="")
            print("\nvel: ", end="")
            for idl_idx in JOINT_IDX_IN_IDL:
                print(f"{ms[idl_idx].dq:.2f},", end="")
            print("\ntau_est: ", end="")
            for idl_idx in JOINT_IDX_IN_IDL:
                print(f"{ms[idl_idx].tau_est:.2f},", end="")
            print("\ntemperature: ", end="")
            for idl_idx in JOINT_IDX_IN_IDL:
                print(f"{ms[idl_idx].temperature[0]},{ms[idl_idx].temperature[1]};", end="")
            print("\nvol: ", end="")
            for idl_idx in JOINT_IDX_IN_IDL:
                print(f"{ms[idl_idx].vol:.2f},", end="")
            print("\nsensor: ", end="")
            for idl_idx in JOINT_IDX_IN_IDL:
                print(f"{ms[idl_idx].sensor[0]},{ms[idl_idx].sensor[1]};", end="")
            print("\nmotorstate: ", end="")
            for idl_idx in JOINT_IDX_IN_IDL:
                print(f"{ms[idl_idx].motorstate},", end="")
            print("\nreserve: ", end="")
            for idl_idx in JOINT_IDX_IN_IDL:
                reserve = ms[idl_idx].reserve
                print(f"{reserve[0]},{reserve[1]},{reserve[2]},{reserve[3]};", end="")
            print()

    def Control(self):
        self.time_ += self.control_dt_

        q_target = [0.0] * R1_NUM_MOTOR
        dq_target = [0.0] * R1_NUM_MOTOR
        tau_ff = [0.0] * R1_NUM_MOTOR

        if self.time_ < self.duration_:
            for i in range(R1_NUM_MOTOR):
                ratio = np.clip(self.time_ / self.duration_, 0.0, 1.0)
                q_target[i] = (1.0 - ratio) * self.motor_q[i]
        elif self.time_ < self.duration_ * 2:
            self.mode_pr_ = Mode.PR
            max_p = np.pi * 30.0 / 180.0
            max_r = np.pi * 30.0 / 180.0
            t = self.time_ - self.duration_
            q_target[R1JointIndex.LeftAnklePitch] = max_p * np.sin(2.0 * np.pi * t)
            q_target[R1JointIndex.LeftAnkleRoll] = max_r * np.sin(2.0 * np.pi * t)
            q_target[R1JointIndex.RightAnklePitch] = max_p * np.sin(2.0 * np.pi * t)
            q_target[R1JointIndex.RightAnkleRoll] = -max_r * np.sin(2.0 * np.pi * t)
        else:
            self.mode_pr_ = Mode.AB
            max_a = np.pi * 30.0 / 180.0
            max_b = np.pi * 10.0 / 180.0
            t = self.time_ - self.duration_ * 2
            q_target[R1JointIndex.LeftAnkleA] = max_a * np.sin(np.pi * t)
            q_target[R1JointIndex.LeftAnkleB] = max_b * np.sin(np.pi * t + np.pi)
            q_target[R1JointIndex.RightAnkleA] = -max_a * np.sin(np.pi * t)
            q_target[R1JointIndex.RightAnkleB] = -max_b * np.sin(np.pi * t + np.pi)

        return q_target, dq_target, Kp, Kd, tau_ff

    def LowCmdWrite(self):
        if self.low_state is None:
            return

        q_target, dq_target, kp, kd, tau_ff = self.Control()

        self.low_cmd.mode_pr = self.mode_pr_
        self.low_cmd.mode_machine = self.mode_machine_

        for i, idl_idx in enumerate(JOINT_IDX_IN_IDL):
            motor_cmd = self.low_cmd.motor_cmd[idl_idx]
            motor_cmd.mode = 1
            motor_cmd.tau = tau_ff[i]
            motor_cmd.q = q_target[i]
            motor_cmd.dq = dq_target[i]
            motor_cmd.kp = kp[i]
            motor_cmd.kd = kd[i]

        self.low_cmd.crc = self.crc.Crc(self.low_cmd)
        self.lowcmd_publisher_.Write(self.low_cmd)


if __name__ == "__main__":
    print("WARNING: This example publishes low-level motor commands to R1.")
    print("Ensure the robot is supported, stable, and has clear space around it.")
    input("Press Enter to continue...")

    if len(sys.argv) < 2:
        print("Usage: r1_ankle_swing_example network_interface")
        sys.exit(0)

    ChannelFactoryInitialize(0, sys.argv[1])

    custom = Custom()
    custom.Init()
    custom.Start()

    while True:
        time.sleep(10)
