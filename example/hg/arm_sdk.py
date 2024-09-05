import time
import numpy as np
from enum import IntEnum
from unitree_sdk2py.core.channel import ChannelPublisher, ChannelFactoryInitialize

# from user_data import *
from unitree_sdk2py.idl.unitree_hg.msg.dds_ import LowCmd_
from unitree_sdk2py.idl.unitree_hg.msg.dds_ import MotorCmd_
from unitree_sdk2py.idl.default import unitree_hg_msg_dds__LowCmd_
import unitree_sdk2py.idl.unitree_hg.msg.dds_ as dds
print(dds.LowCmd_)
print(dds.MotorCmd_)

kTopicArmSDK = "rt/arm_sdk"
kPi = 3.141592654
kPi_2 = 1.57079632


class JointIndex(IntEnum):

    #   // Left arm
    kLeftShoulderPitch = 13
    kLeftShoulderRoll = 14
    kLeftShoulderYaw = 15
    kLeftElbow = 16
    kLeftWistYaw = 17
    kLeftWistPitch = 18
    kLeftWistRoll = 19
    #   // Right arm
    kRightShoulderPitch = 20
    kRightShoulderRoll = 21
    kRightShoulderYaw = 22
    kRightElbow = 23
    kRightWistYaw = 24
    kRightWistPitch = 25
    kRightWistRoll = 26

    kWaistYaw = 12


kNotUsedJoint = 27


if __name__ == "__main__":
    ChannelFactoryInitialize()

    # Create a publisher to publish the data defined in UserData class
    arm_sdk_publisher = ChannelPublisher('rt/arm_sdk', LowCmd_)
    # pub = ChannelPublisher("rt/lowcmd", LowCmd_)
    arm_sdk_publisher.Init()

    msg = unitree_hg_msg_dds__LowCmd_()

    weight = 0
    weight_rate = 0.2

    kp = 60
    kd = 1.5
    dq = 0
    tau_ff = 0

    control_dt = 0.02
    max_joint_velocity = 0.5

    delta_weight = weight_rate * control_dt
    max_joint_delta = max_joint_velocity * control_dt

    init_pos = np.zeros(15)
    target_pos = np.array(
        [
            0.0,
            kPi_2,
            0.0,
            kPi_2,
            0.0,
            0.0,
            0.0,
            0.0,
            -kPi_2,
            0.0,
            kPi_2,
            0.0,
            0.0,
            0.0,
            0.0,
        ]
    )
    print("Initailizing arms ...")

    init_time = 5
    init_time_steps = int(init_time / control_dt)

    for i in range(init_time_steps):
        weight += delta_weight
        weight = max(min(weight, 1.0), 0)
        msg.motor_cmd[kNotUsedJoint].q = weight * weight

        for idx, joint in enumerate(JointIndex):
            msg.motor_cmd[joint].q = init_pos[idx]
            msg.motor_cmd[joint].dq = dq
            msg.motor_cmd[joint].kp = kp
            msg.motor_cmd[joint].kd = kd
            msg.motor_cmd[joint].tau = tau_ff

        arm_sdk_publisher.Write(msg)

        time.sleep(control_dt)

    print("Done!")

    period = 5
    num_time_steps = int(period / control_dt)

    current_jpos_des = np.zeros_like(init_pos)

    for i in range(num_time_steps):
        for j in range(len(current_jpos_des)):
                delta = target_pos[j] - current_jpos_des[j]
                clamped_delta = np.clip(delta, -max_joint_delta, max_joint_delta)
                current_jpos_des[j] += clamped_delta
        
        for idx, joint in enumerate(JointIndex):
            msg.motor_cmd[joint].q = current_jpos_des[idx]
            msg.motor_cmd[joint].dq = dq
            msg.motor_cmd[joint].kp = kp
            msg.motor_cmd[joint].kd = kd
            msg.motor_cmd[joint].tau = tau_ff
        
        arm_sdk_publisher.Write(msg)
        
        time.sleep(control_dt)
    
    exit()