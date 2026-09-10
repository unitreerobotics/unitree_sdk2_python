import time
import sys

from unitree_sdk2py.core.channel import ChannelPublisher, ChannelFactoryInitialize
from unitree_sdk2py.core.channel import ChannelSubscriber, ChannelFactoryInitialize
from unitree_sdk2py.idl.default import unitree_hg_msg_dds__LowCmd_
from unitree_sdk2py.idl.default import unitree_hg_msg_dds__LowState_
from unitree_sdk2py.idl.unitree_hg.msg.dds_ import LowCmd_
from unitree_sdk2py.idl.unitree_hg.msg.dds_ import LowState_
from unitree_sdk2py.utils.crc import CRC
from unitree_sdk2py.utils.thread import RecurrentThread
from unitree_sdk2py.comm.motion_switcher.motion_switcher_client import MotionSwitcherClient

import numpy as np

R1_NUM_MOTOR = 26

Kp = [
    200, 200, 200, 200, 200, 200,     # legs
    200, 200, 200, 200, 200, 200,     # legs
    300, 300,                         # waist
    100, 100, 100, 100, 50,           # arms
    100, 100, 100, 100, 50,           # arms
    50, 10                            # head
]

Kd = [
    3, 3, 3, 3, 3, 3,                 # legs
    3, 3, 3, 3, 3, 3,                 # legs
    5, 5,                             # waist
    2, 2, 2, 2, 2,                    # arms
    2, 2, 2, 2, 2,                    # arms
    2, 0.1                            # head
]

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

joint_idx_in_idl = [
    0, 1, 2, 3, 4, 5,
    6, 7, 8, 9, 10, 11,
    12, 13,
    15, 16, 17, 18, 19,
    22, 23, 24, 25, 26,
    29, 30
]

class Mode:
    PR = 0  # Series Control for Pitch/Roll Joints
    AB = 1  # Parallel Control for A/B Joints

class Custom:
    def __init__(self):
        self.time_ = 0.0
        self.control_dt_ = 0.002  # [2ms]
        self.duration_ = 3.0    # [3 s]
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

        status, result = self.msc.CheckMode()
        while result['name']:
            self.msc.ReleaseMode()
            status, result = self.msc.CheckMode()
            time.sleep(1)
        self.msc.ReleaseMode()

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
        self.low_state = msg

        if self.update_mode_machine_ == False:
            self.mode_machine_ = self.low_state.mode_machine
            self.update_mode_machine_ = True
        
        self.counter_ +=1
        if (self.counter_ % 500 == 0) :
            self.counter_ = 0
            print(self.low_state.imu_state.rpy)

    def LowCmdWrite(self):
        self.time_ += self.control_dt_

        if self.time_ < self.duration_ :
            # [Stage 1]: set robot to zero posture
            for i in range(R1_NUM_MOTOR):
                ratio = np.clip(self.time_ / self.duration_, 0.0, 1.0)
                self.low_cmd.mode_pr = Mode.PR
                self.low_cmd.mode_machine = self.mode_machine_
                self.low_cmd.motor_cmd[joint_idx_in_idl[i]].mode =  1 # 1:Enable, 0:Disable
                self.low_cmd.motor_cmd[joint_idx_in_idl[i]].tau = 0. 
                self.low_cmd.motor_cmd[joint_idx_in_idl[i]].q = (1.0 - ratio) * self.low_state.motor_state[joint_idx_in_idl[i]].q 
                self.low_cmd.motor_cmd[joint_idx_in_idl[i]].dq = 0. 
                self.low_cmd.motor_cmd[joint_idx_in_idl[i]].kp = Kp[i]
                self.low_cmd.motor_cmd[joint_idx_in_idl[i]].kd = Kd[i]

        elif self.time_ < self.duration_ * 2 :
            # [Stage 2]: swing ankle using PR mode
            max_P = np.pi * 30.0 / 180.0
            max_R = np.pi * 10.0 / 180.0
            t = self.time_ - self.duration_
            L_P_des = max_P * np.sin(2.0 * np.pi * t)
            L_R_des = max_R * np.sin(2.0 * np.pi * t)
            R_P_des = max_P * np.sin(2.0 * np.pi * t)
            R_R_des = -max_R * np.sin(2.0 * np.pi * t)

            self.low_cmd.mode_pr = Mode.PR
            self.low_cmd.mode_machine = self.mode_machine_
            self.low_cmd.motor_cmd[joint_idx_in_idl[R1JointIndex.LeftAnklePitch]].q = L_P_des
            self.low_cmd.motor_cmd[joint_idx_in_idl[R1JointIndex.LeftAnkleRoll]].q = L_R_des
            self.low_cmd.motor_cmd[joint_idx_in_idl[R1JointIndex.RightAnklePitch]].q = R_P_des
            self.low_cmd.motor_cmd[joint_idx_in_idl[R1JointIndex.RightAnkleRoll]].q = R_R_des

        else :
            # [Stage 3]: swing ankle using AB mode
            max_A = np.pi * 30.0 / 180.0
            max_B = np.pi * 10.0 / 180.0
            t = self.time_ - self.duration_ * 2
            L_A_des = max_A * np.sin(2.0 * np.pi * t)
            L_B_des = max_B * np.sin(2.0 * np.pi * t + np.pi)
            R_A_des = -max_A * np.sin(2.0 * np.pi * t)
            R_B_des = -max_B * np.sin(2.0 * np.pi * t + np.pi)

            self.low_cmd.mode_pr = Mode.AB
            self.low_cmd.mode_machine = self.mode_machine_
            self.low_cmd.motor_cmd[joint_idx_in_idl[R1JointIndex.LeftAnkleA]].q = L_A_des
            self.low_cmd.motor_cmd[joint_idx_in_idl[R1JointIndex.LeftAnkleB]].q = L_B_des
            self.low_cmd.motor_cmd[joint_idx_in_idl[R1JointIndex.RightAnkleA]].q = R_A_des
            self.low_cmd.motor_cmd[joint_idx_in_idl[R1JointIndex.RightAnkleB]].q = R_B_des
            
            max_WristYaw = np.pi * 30.0 / 180.0
            L_WristYaw_des = max_WristYaw * np.sin(2.0 * np.pi * t)
            R_WristYaw_des = max_WristYaw * np.sin(2.0 * np.pi * t)
            self.low_cmd.motor_cmd[joint_idx_in_idl[R1JointIndex.LeftWristRoll]].q = L_WristYaw_des
            self.low_cmd.motor_cmd[joint_idx_in_idl[R1JointIndex.RightWristRoll]].q = R_WristYaw_des
    

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