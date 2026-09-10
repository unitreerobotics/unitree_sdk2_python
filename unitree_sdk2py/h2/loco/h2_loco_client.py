import json

from ...rpc.client import Client
from .h2_loco_api import *

"""
" class SportClient
"""
class LocoClient(Client):
    def __init__(self):
        super().__init__(LOCO_SERVICE_NAME, False)
        self.continous_move_ = False
        self.first_shake_hand_stage_ = -1

    def Init(self):
        # set api version
        self._SetApiVerson(LOCO_API_VERSION)

        # regist api
        self._RegistApi(ROBOT_API_ID_LOCO_GET_FSM_ID, 0)
        self._RegistApi(ROBOT_API_ID_LOCO_GET_FSM_MODE, 0)
        self._RegistApi(ROBOT_API_ID_LOCO_GET_BALANCE_MODE, 0)
        self._RegistApi(ROBOT_API_ID_LOCO_GET_SWING_HEIGHT, 0)
        self._RegistApi(ROBOT_API_ID_LOCO_GET_STAND_HEIGHT, 0)
        self._RegistApi(ROBOT_API_ID_LOCO_GET_PHASE, 0)  # deprecated
        self._RegistApi(ROBOT_API_ID_LOCO_GET_ARM_SDK_STATUS, 0)
        self._RegistApi(ROBOT_API_ID_LOCO_GET_AVAILABLE_FSM_IDS, 0)

        self._RegistApi(ROBOT_API_ID_LOCO_SET_FSM_ID, 0)
        self._RegistApi(ROBOT_API_ID_LOCO_SET_BALANCE_MODE, 0)
        self._RegistApi(ROBOT_API_ID_LOCO_SET_SWING_HEIGHT, 0)
        self._RegistApi(ROBOT_API_ID_LOCO_SET_STAND_HEIGHT, 0)
        self._RegistApi(ROBOT_API_ID_LOCO_SET_VELOCITY, 0)
        self._RegistApi(ROBOT_API_ID_LOCO_SET_ARM_TASK, 0)
        self._RegistApi(ROBOT_API_ID_LOCO_SET_SPEED_MODE, 0)
        self._RegistApi(ROBOT_API_ID_LOCO_SET_PUNCH_API, 0)
        self._RegistApi(ROBOT_API_ID_LOCO_SET_ARM_SDK_STATUS, 0)

    # 7101
    def SetFsmId(self, fsm_id: int):
        p = {}
        p["data"] = fsm_id
        parameter = json.dumps(p)
        code, data = self._Call(ROBOT_API_ID_LOCO_SET_FSM_ID, parameter)
        return code

    # 7102
    def SetBalanceMode(self, balance_mode: int):
        p = {}
        p["data"] = balance_mode
        parameter = json.dumps(p)
        code, data = self._Call(ROBOT_API_ID_LOCO_SET_BALANCE_MODE, parameter)
        return code

    # 7103
    def SetSwingHeight(self, swing_height: float):
        p = {}
        p["data"] = swing_height
        parameter = json.dumps(p)
        code, data = self._Call(ROBOT_API_ID_LOCO_SET_SWING_HEIGHT, parameter)
        return code

    # 7104
    def SetStandHeight(self, stand_height: float):
        p = {}
        p["data"] = stand_height
        parameter = json.dumps(p)
        code, data = self._Call(ROBOT_API_ID_LOCO_SET_STAND_HEIGHT, parameter)
        return code

    # 7105
    def SetVelocity(self, vx: float, vy: float, omega: float, duration: float = 1.0):
        p = {}
        velocity = [vx, vy, omega]
        p["velocity"] = velocity
        p["duration"] = duration
        parameter = json.dumps(p)
        code, data = self._Call(ROBOT_API_ID_LOCO_SET_VELOCITY, parameter)
        return code

    # 7106
    def SetTaskId(self, task_id: float):
        p = {}
        p["data"] = task_id
        parameter = json.dumps(p)
        code, data = self._Call(ROBOT_API_ID_LOCO_SET_ARM_TASK, parameter)
        return code

    # 7107
    def SetSpeedMode(self, speed_mode: int):
        p = {}
        p["data"] = speed_mode
        parameter = json.dumps(p)
        code, data = self._Call(ROBOT_API_ID_LOCO_SET_SPEED_MODE, parameter)
        return code

    # 7108
    def SetPunchApi(self, punch_api):
        p = {}
        p["data"] = punch_api
        parameter = json.dumps(p)
        code, data = self._Call(ROBOT_API_ID_LOCO_SET_PUNCH_API, parameter)
        return code

    # 7109
    def SetArmSdkStatus(self, arm_sdk_status: bool):
        p = {}
        p["data"] = arm_sdk_status
        parameter = json.dumps(p)
        code, data = self._Call(ROBOT_API_ID_LOCO_SET_ARM_SDK_STATUS, parameter)
        return code

    def Damp(self):
        self.SetFsmId(1)

    def Start(self):
        self.SetFsmId(601)

    def Squat(self):
        self.SetFsmId(2)

    def Sit(self):
        self.SetFsmId(3)

    def StandUp(self):
        self.SetFsmId(4)

    def ZeroTorque(self):
        self.SetFsmId(0)

    def StopMove(self):
        self.SetVelocity(0.0, 0.0, 0.0)

    def HighStand(self):
        UINT32_MAX = (1 << 32) - 1
        self.SetStandHeight(UINT32_MAX)

    def LowStand(self):
        UINT32_MIN = 0
        self.SetStandHeight(UINT32_MIN)

    def Move(self, vx: float, vy: float, vyaw: float, continous_move: bool = None):
        if continous_move is None:
            continous_move = self.continous_move_
        duration = 864000.0 if continous_move else 1
        self.SetVelocity(vx, vy, vyaw, duration)

    def BalanceStand(self):
        self.SetBalanceMode(0)

    def ContinuousGait(self, flag: bool):
        self.SetBalanceMode(1 if flag else 0)

    def SwitchMoveMode(self, flag: bool):
        self.continous_move_ = flag
        return 0

    def WaveHand(self, turn_flag: bool = False):
        self.SetTaskId(1 if turn_flag else 0)

    def ShakeHand(self, stage: int = -1):
        if stage == 0:
            self.first_shake_hand_stage_ = False
            self.SetTaskId(2)
        elif stage == 1:
            self.first_shake_hand_stage_ = True
            self.SetTaskId(3)
        else:
            self.first_shake_hand_stage_ = not self.first_shake_hand_stage_
            return self.SetTaskId(3 if self.first_shake_hand_stage_ else 2)

    def EnableArmSDK(self):
        self.SetArmSdkStatus(True)

    def DisableArmSDK(self):
        self.SetArmSdkStatus(False)

    def GetFsmId(self):
        p = {}
        parameter = json.dumps(p)
        code, data = self._Call(ROBOT_API_ID_LOCO_GET_FSM_ID, parameter)
        if code != 0:
            return code, None
        js = json.loads(data)
        return code, js.get("data")

    def GetFsmMode(self):
        p = {}
        parameter = json.dumps(p)
        code, data = self._Call(ROBOT_API_ID_LOCO_GET_FSM_MODE, parameter)
        if code != 0:
            return code, None
        js = json.loads(data)
        return code, js.get("data")

    def GetBalanceMode(self):
        p = {}
        parameter = json.dumps(p)
        code, data = self._Call(ROBOT_API_ID_LOCO_GET_BALANCE_MODE, parameter)
        if code != 0:
            return code, None
        js = json.loads(data)
        return code, js.get("data")

    def GetSwingHeight(self):
        p = {}
        parameter = json.dumps(p)
        code, data = self._Call(ROBOT_API_ID_LOCO_GET_SWING_HEIGHT, parameter)
        if code != 0:
            return code, None
        js = json.loads(data)
        return code, js.get("data")

    def GetStandHeight(self):
        p = {}
        parameter = json.dumps(p)
        code, data = self._Call(ROBOT_API_ID_LOCO_GET_STAND_HEIGHT, parameter)
        if code != 0:
            return code, None
        js = json.loads(data)
        return code, js.get("data")

    def GetPhase(self):
        p = {}
        parameter = json.dumps(p)
        code, data = self._Call(ROBOT_API_ID_LOCO_GET_PHASE, parameter)
        if code != 0:
            return code, None
        js = json.loads(data)
        return code, js.get("data")

    def GetArmSdkStatus(self):
        p = {}
        parameter = json.dumps(p)
        code, data = self._Call(ROBOT_API_ID_LOCO_GET_ARM_SDK_STATUS, parameter)
        if code != 0:
            return code, None
        js = json.loads(data)
        return code, js.get("data")

    def GetAvailableFsmIds(self):
        p = {}
        parameter = json.dumps(p)
        code, data = self._Call(ROBOT_API_ID_LOCO_GET_AVAILABLE_FSM_IDS, parameter)
        if code != 0:
            return code, None, None
        js = json.loads(data)
        return code, js.get("ids", []), js.get("names", [])

