import sys
import time

import numpy as np

from unitree_sdk2py.core.channel import ChannelFactoryInitialize, ChannelPublisher, ChannelSubscriber
from unitree_sdk2py.idl.default import unitree_hg_msg_dds__LowCmd_
from unitree_sdk2py.idl.unitree_hg.msg.dds_ import LowCmd_, LowState_
from unitree_sdk2py.h2.loco.h2_loco_client import LocoClient
from unitree_sdk2py.utils.crc import CRC
from unitree_sdk2py.utils.thread import RecurrentThread


SMALL_SHOULDER_ROLL = np.deg2rad(20.0)
SMALL_ELBOW = np.deg2rad(30.0)
SMALL_HEAD_YAW = np.deg2rad(20.0)
SMALL_HEAD_PITCH = np.deg2rad(15.0)

ARM_SDK_SUPPORTED_FSM_IDS = {4, 703}


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
    HeadPitch = 29
    HeadYaw = 30

    kNotUsedJoint = 31  # NOTE: Weight


class Custom:
    def __init__(self):
        self.time_ = 0.0
        self.control_dt_ = 0.02
        self.duration_ = 3.0
        self.kp = 80.0
        self.kd = 1.5
        self.head_kp = 30.0
        self.head_kd = 1.0
        self.low_cmd = unitree_hg_msg_dds__LowCmd_()
        self.low_state = None
        self.first_update_low_state = False
        self.crc = CRC()
        self.done = False

        self.target_pos = [
            0.0, SMALL_SHOULDER_ROLL, 0.0, SMALL_ELBOW, 0.0, 0.0, 0.0,
            0.0, -SMALL_SHOULDER_ROLL, 0.0, SMALL_ELBOW, 0.0, 0.0, 0.0,
            SMALL_HEAD_PITCH, SMALL_HEAD_YAW,
        ]

        self.upper_body_joints = [
            H2JointIndex.LeftShoulderPitch, H2JointIndex.LeftShoulderRoll,
            H2JointIndex.LeftShoulderYaw, H2JointIndex.LeftElbow,
            H2JointIndex.LeftWristRoll, H2JointIndex.LeftWristPitch,
            H2JointIndex.LeftWristYaw,
            H2JointIndex.RightShoulderPitch, H2JointIndex.RightShoulderRoll,
            H2JointIndex.RightShoulderYaw, H2JointIndex.RightElbow,
            H2JointIndex.RightWristRoll, H2JointIndex.RightWristPitch,
            H2JointIndex.RightWristYaw,
            H2JointIndex.HeadPitch, H2JointIndex.HeadYaw,
        ]

        self.head_joints = {H2JointIndex.HeadYaw, H2JointIndex.HeadPitch}

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

    def SetJointCommand(self, joint, q):
        command = self.low_cmd.motor_cmd[joint]
        command.tau = 0.0
        command.q = q
        command.dq = 0.0
        if joint in self.head_joints:
            command.kp = self.head_kp
            command.kd = self.head_kd
        else:
            command.kp = self.kp
            command.kd = self.kd

    def LowCmdWrite(self):
        if self.low_state is None:
            return

        self.time_ += self.control_dt_

        if self.time_ < self.duration_:
            print("[Stage 1]: set arms and head to zero posture.")
            self.low_cmd.motor_cmd[H2JointIndex.kNotUsedJoint].q = 1.0

            for joint in self.upper_body_joints:
                ratio = np.clip(self.time_ / self.duration_, 0.0, 1.0)
                q = (1.0 - ratio) * self.low_state.motor_state[joint].q
                self.SetJointCommand(joint, q)

        elif self.time_ < self.duration_ * 3:
            print("[Stage 2]: lift arms and move head.")
            for i, joint in enumerate(self.upper_body_joints):
                ratio = np.clip((self.time_ - self.duration_) / (self.duration_ * 2), 0.0, 1.0)
                q = (
                    ratio * self.target_pos[i] + (1.0 - ratio) * self.low_state.motor_state[joint].q
                )
                self.SetJointCommand(joint, q)

        elif self.time_ < self.duration_ * 6:
            print("[Stage 3]: set arms and head back to zero posture.")
            for joint in self.upper_body_joints:
                ratio = np.clip((self.time_ - self.duration_ * 3) / (self.duration_ * 3), 0.0, 1.0)
                q = (1.0 - ratio) * self.low_state.motor_state[joint].q
                self.SetJointCommand(joint, q)

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

    loco_client = LocoClient()
    loco_client.SetTimeout(5.0)
    loco_client.Init()

    ret, fsm_id = loco_client.GetFsmId()
    if ret != 0:
        print(f"Failed to get H2 FSM ID, error code: {ret}")
        sys.exit(1)
    if fsm_id not in ARM_SDK_SUPPORTED_FSM_IDS:
        print(
            f"Current FSM {fsm_id} does not accept rt/arm_sdk commands. "
            f"Switch to one of {sorted(ARM_SDK_SUPPORTED_FSM_IDS)} first."
        )
        sys.exit(1)

    ret = loco_client.EnableArmSDK()
    if ret != 0:
        print(f"Failed to enable the external Arm SDK, error code: {ret}")
        sys.exit(1)

    exit_code = 0
    try:
        custom = Custom()
        custom.Init()
        custom.Start()

        while True:
            time.sleep(1)
            if custom.done:
                print("Done!")
                break
    except KeyboardInterrupt:
        print("Interrupted; releasing Arm SDK control.")
    finally:
        ret = loco_client.DisableArmSDK()
        if ret != 0:
            print(f"Failed to disable the external Arm SDK, error code: {ret}")
            exit_code = 1

    sys.exit(exit_code)
