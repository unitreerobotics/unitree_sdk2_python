import time
import sys

from unitree_sdk2py.core.channel import ChannelPublisher, ChannelFactoryInitialize
from unitree_sdk2py.core.channel import ChannelSubscriber
from unitree_sdk2py.idl.default import unitree_hg_msg_dds__LowCmd_
from unitree_sdk2py.idl.unitree_hg.msg.dds_ import LowCmd_
from unitree_sdk2py.idl.unitree_hg.msg.dds_ import LowState_
from unitree_sdk2py.utils.crc import CRC
from unitree_sdk2py.utils.thread import RecurrentThread
from unitree_sdk2py.comm.motion_switcher.motion_switcher_client import MotionSwitcherClient

import numpy as np

R1_NUM_MOTOR = 16

Kp = [
    100, 100, 100, 100, 50, 50, 50,  # left arm
    100, 100, 100, 100, 50, 50, 50,  # right arm
    50, 10  # head
]

Kd = [
    2, 2, 2, 2, 2, 2, 2,  # left arm
    2, 2, 2, 2, 2, 2, 2,  # right arm
    2, 0.1  # head
]

class R1JointIndex:
    LeftShoulderPitch = 0
    LeftShoulderRoll = 1
    LeftShoulderYaw = 2
    LeftElbow = 3
    LeftWristRoll = 4
    LeftWristPitch = 5
    LeftWristYaw = 6
    RightShoulderPitch = 7
    RightShoulderRoll = 8
    RightShoulderYaw = 9
    RightElbow = 10
    RightWristRoll = 11
    RightWristPitch = 12
    RightWristYaw = 13
    HEAD_PITCH = 14
    HEAD_YAW = 15

# Map local joint indices to the HG DDS motor slots.
joint_idx_in_idl = [
    15, 16, 17, 18, 19, 20, 21,
    22, 23, 24, 25, 26, 27, 28,
    29, 30
]

class Mode:
    PR = 0  # Series Control for Pitch/Roll Joints
    AB = 1  # Parallel Control for A/B Joints

class Custom:
    def __init__(self):
        self.time_ = 0.0
        self.control_dt_ = 0.002  # [2ms]
        self.duration_ = 2.0    # [2 s]
        self.counter_ = 0
        self.mode_pr_ = Mode.PR
        self.mode_machine_ = 0
        self.low_cmd = unitree_hg_msg_dds__LowCmd_()
        self.low_state = None
        self.update_mode_machine_ = False
        self.crc = CRC()

    def Init(self):
        self.msc = MotionSwitcherClient()
        self.msc.SetTimeout(5.0)
        self.msc.Init()

        while True:
            status, result = self.msc.CheckMode()
            if status != 0:
                raise RuntimeError(f"Failed to check motion mode: {status}")
            if not result['name']:
                break
            status, _ = self.msc.ReleaseMode()
            if status != 0:
                raise RuntimeError(f"Failed to release motion mode: {status}")
            time.sleep(1)

        # create publisher #
        self.lowcmd_publisher_ = ChannelPublisher("rt/lowcmd", LowCmd_)
        self.lowcmd_publisher_.Init()

        # create subscriber #
        self.lowstate_subscriber = ChannelSubscriber("rt/lowstate", LowState_)
        self.lowstate_subscriber.Init(self.LowStateHandler, 10)

    def Start(self):
        self.lowCmdWriteThreadPtr = RecurrentThread(
            interval=self.control_dt_, target=self.LowCmdWrite, name="control"
        )
        while self.update_mode_machine_ == False:
            time.sleep(1)

        if self.update_mode_machine_ == True:
            self.lowCmdWriteThreadPtr.Start()

    def LowStateHandler(self, msg: LowState_):
        if msg.crc != self.crc.Crc(msg):
            print("[ERROR] CRC Error")
            return

        self.low_state = msg
        self.mode_machine_ = msg.mode_machine

        if self.update_mode_machine_ == False:
            self.update_mode_machine_ = True

        self.counter_ +=1
        if (self.counter_ % 500 == 0) :
            self.counter_ = 0
            print(self.low_state.imu_state.rpy)

    def LowCmdWrite(self):
        if self.low_state is None:
            return

        self.time_ += self.control_dt_
        self.low_cmd.mode_pr = self.mode_pr_
        self.low_cmd.mode_machine = self.mode_machine_

        # Reset all controlled joints so inactive joints hold zero posture.
        for i in range(R1_NUM_MOTOR):
            joint = joint_idx_in_idl[i]
            self.low_cmd.motor_cmd[joint].mode = 1  # 1:Enable, 0:Disable
            self.low_cmd.motor_cmd[joint].tau = 0.
            self.low_cmd.motor_cmd[joint].q = 0.
            self.low_cmd.motor_cmd[joint].dq = 0.
            self.low_cmd.motor_cmd[joint].kp = Kp[i]
            self.low_cmd.motor_cmd[joint].kd = Kd[i]

        if self.time_ < self.duration_:
            # [Stage 1]: set arms and head to zero posture
            ratio = np.clip(self.time_ / self.duration_, 0.0, 1.0)
            for joint in joint_idx_in_idl:
                self.low_cmd.motor_cmd[joint].q = (1.0 - ratio) * self.low_state.motor_state[joint].q
        else:
            t = (self.time_ - self.duration_) % (self.duration_ * 4.0)
            phase_t = t % self.duration_
            max_angle = np.pi * 30.0 / 180.0
            angle_des = max_angle * np.sin(2.0 * np.pi * phase_t / self.duration_)

            if t < self.duration_ * 1.0:
                # [Stage 2]: swing wrist roll joints for 2 s
                self.low_cmd.motor_cmd[joint_idx_in_idl[R1JointIndex.LeftWristRoll]].q = angle_des
                self.low_cmd.motor_cmd[joint_idx_in_idl[R1JointIndex.RightWristRoll]].q = -angle_des
            elif t < self.duration_ * 2.0:
                # [Stage 3]: swing wrist pitch joints for 2 s
                self.low_cmd.motor_cmd[joint_idx_in_idl[R1JointIndex.LeftWristPitch]].q = angle_des
                self.low_cmd.motor_cmd[joint_idx_in_idl[R1JointIndex.RightWristPitch]].q = -angle_des
            elif t < self.duration_ * 3.0:
                # [Stage 4]: swing wrist yaw joints for 2 s
                self.low_cmd.motor_cmd[joint_idx_in_idl[R1JointIndex.LeftWristYaw]].q = angle_des
                self.low_cmd.motor_cmd[joint_idx_in_idl[R1JointIndex.RightWristYaw]].q = -angle_des
            else:
                # [Stage 5]: swing head yaw joint for 2 s
                self.low_cmd.motor_cmd[joint_idx_in_idl[R1JointIndex.HEAD_YAW]].q = angle_des

        self.low_cmd.crc = self.crc.Crc(self.low_cmd)
        self.lowcmd_publisher_.Write(self.low_cmd)

if __name__ == '__main__':

    print("WARNING: Please ensure there are no obstacles around the robot while running this example.")
    input("Press Enter to continue...")

    if len(sys.argv)>1:
        ChannelFactoryInitialize(0, sys.argv[1])
    else:
        ChannelFactoryInitialize(0)

    custom = Custom()
    custom.Init()
    custom.Start()

    while True:
        time.sleep(1)
