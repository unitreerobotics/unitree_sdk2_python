import sys
import time

import numpy as np

from unitree_sdk2py.core.channel import ChannelFactoryInitialize, ChannelPublisher, ChannelSubscriber
from unitree_sdk2py.idl.default import unitree_hg_msg_dds__LowCmd_
from unitree_sdk2py.idl.unitree_hg.msg.dds_ import LowCmd_, LowState_
from unitree_sdk2py.utils.crc import CRC
from unitree_sdk2py.utils.thread import RecurrentThread


SMALL_SHOULDER_ROLL = np.deg2rad(20.0)
SMALL_ELBOW = np.deg2rad(30.0)


class H2JointIndex:
    # Left leg
    LeftHipPitch = 0
    LeftHipRoll = 1
    LeftHipYaw = 2
    LeftKnee = 3
    LeftAnklePitch = 4
    LeftAnkleB = 4
    LeftAnkleRoll = 5
    LeftAnkleA = 5

    # Right leg
    RightHipPitch = 6
    RightHipRoll = 7
    RightHipYaw = 8
    RightKnee = 9
    RightAnklePitch = 10
    RightAnkleB = 10
    RightAnkleRoll = 11
    RightAnkleA = 11

    # Waist
    WaistYaw = 12
    WaistRoll = 13
    WaistPitch = 14

    # Left arm
    LeftShoulderPitch = 15
    LeftShoulderRoll = 16
    LeftShoulderYaw = 17
    LeftElbow = 18
    LeftWristRoll = 19
    LeftWristPitch = 20
    LeftWristYaw = 21

    # Right arm
    RightShoulderPitch = 22
    RightShoulderRoll = 23
    RightShoulderYaw = 24
    RightElbow = 25
    RightWristRoll = 26
    RightWristPitch = 27
    RightWristYaw = 28

    # Head
    HeadYaw = 29
    HeadPitch = 30

    kNotUsedJoint = 31  # NOTE: Weight


class Custom:
    def __init__(self):
        self.time_ = 0.0
        self.control_dt_ = 0.02
        self.duration_ = 3.0
        self.kp = 80.0
        self.kd = 1.5
        self.low_cmd = unitree_hg_msg_dds__LowCmd_()
        self.low_state = None
        self.first_update_low_state = False
        self.crc = CRC()
        self.done = False

        self.target_pos = [
            0.0, SMALL_SHOULDER_ROLL, 0.0, SMALL_ELBOW, 0.0, 0.0, 0.0,
            0.0, -SMALL_SHOULDER_ROLL, 0.0, SMALL_ELBOW, 0.0, 0.0, 0.0,
        ]

        self.arm_joints = [
            H2JointIndex.LeftShoulderPitch, H2JointIndex.LeftShoulderRoll,
            H2JointIndex.LeftShoulderYaw, H2JointIndex.LeftElbow,
            H2JointIndex.LeftWristRoll, H2JointIndex.LeftWristPitch,
            H2JointIndex.LeftWristYaw,
            H2JointIndex.RightShoulderPitch, H2JointIndex.RightShoulderRoll,
            H2JointIndex.RightShoulderYaw, H2JointIndex.RightElbow,
            H2JointIndex.RightWristRoll, H2JointIndex.RightWristPitch,
            H2JointIndex.RightWristYaw,
        ]

    def Init(self):
        # create publisher
        self.arm_sdk_publisher = ChannelPublisher("rt/arm_sdk", LowCmd_)
        self.arm_sdk_publisher.Init()

        # create subscriber
        self.lowstate_subscriber = ChannelSubscriber("rt/lowstate", LowState_)
        self.lowstate_subscriber.Init(self.LowStateHandler, 10)

    def Start(self):
        self.lowCmdWriteThreadPtr = RecurrentThread(
            interval=self.control_dt_, target=self.LowCmdWrite, name="control"
        )
        while not self.first_update_low_state:
            time.sleep(1)

        self.lowCmdWriteThreadPtr.Start()

    def LowStateHandler(self, msg: LowState_):
        self.low_state = msg

        if not self.first_update_low_state:
            self.first_update_low_state = True

    def LowCmdWrite(self):
        if self.low_state is None:
            return

        self.time_ += self.control_dt_

        if self.time_ < self.duration_:
            print("[Stage 1]: set arms to zero posture.")
            # [Stage 1]: set arms to zero posture
            self.low_cmd.motor_cmd[H2JointIndex.kNotUsedJoint].q = 1.0

            for i, joint in enumerate(self.arm_joints):
                ratio = np.clip(self.time_ / self.duration_, 0.0, 1.0)
                self.low_cmd.motor_cmd[joint].tau = 0.0
                self.low_cmd.motor_cmd[joint].q = (
                    (1.0 - ratio) * self.low_state.motor_state[joint].q
                )
                self.low_cmd.motor_cmd[joint].dq = 0.0
                self.low_cmd.motor_cmd[joint].kp = self.kp
                self.low_cmd.motor_cmd[joint].kd = self.kd

        elif self.time_ < self.duration_ * 3:
            print("[Stage 2]: lift arms up.")
            # [Stage 2]: lift arms up
            for i, joint in enumerate(self.arm_joints):
                ratio = np.clip((self.time_ - self.duration_) / (self.duration_ * 2), 0.0, 1.0)
                self.low_cmd.motor_cmd[joint].tau = 0.0
                self.low_cmd.motor_cmd[joint].q = (
                    ratio * self.target_pos[i] + (1.0 - ratio) * self.low_state.motor_state[joint].q
                )
                self.low_cmd.motor_cmd[joint].dq = 0.0
                self.low_cmd.motor_cmd[joint].kp = self.kp
                self.low_cmd.motor_cmd[joint].kd = self.kd

        elif self.time_ < self.duration_ * 6:
            print("[Stage 3]: set arms back to zero posture.")
            # [Stage 3]: set arms back to zero posture
            for i, joint in enumerate(self.arm_joints):
                ratio = np.clip((self.time_ - self.duration_ * 3) / (self.duration_ * 3), 0.0, 1.0)
                self.low_cmd.motor_cmd[joint].tau = 0.0
                self.low_cmd.motor_cmd[joint].q = (
                    (1.0 - ratio) * self.low_state.motor_state[joint].q
                )
                self.low_cmd.motor_cmd[joint].dq = 0.0
                self.low_cmd.motor_cmd[joint].kp = self.kp
                self.low_cmd.motor_cmd[joint].kd = self.kd

        elif self.time_ < self.duration_ * 7:
            print("[Stage 4]: release arm_sdk.")
            # [Stage 4]: release arm_sdk
            ratio = np.clip((self.time_ - self.duration_ * 6) / self.duration_, 0.0, 1.0)
            self.low_cmd.motor_cmd[H2JointIndex.kNotUsedJoint].q = 1.0 - ratio

        else:
            self.done = True

        self.low_cmd.crc = self.crc.Crc(self.low_cmd)
        self.arm_sdk_publisher.Write(self.low_cmd)


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
        if custom.done:
            print("Done!")
            sys.exit(-1)
