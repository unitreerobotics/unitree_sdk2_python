import json

from ...rpc.client import Client
from .r1_loco_api import *


class LocoClient(Client):
    def __init__(self):
        super().__init__(LOCO_SERVICE_NAME, False)
        self.continous_move_ = False

    def Init(self):
        self._SetApiVerson(LOCO_API_VERSION)

        self._RegistApi(ROBOT_API_ID_LOCO_GET_FSM_ID, 0)
        self._RegistApi(ROBOT_API_ID_LOCO_GET_FSM_MODE, 0)

        self._RegistApi(ROBOT_API_ID_LOCO_SET_FSM_ID, 0)
        self._RegistApi(ROBOT_API_ID_LOCO_SET_VELOCITY, 0)
        self._RegistApi(ROBOT_API_ID_LOCO_SET_SPEED_MODE, 0)

    def GetFsmId(self):
        code, data = self._Call(ROBOT_API_ID_LOCO_GET_FSM_ID, "{}")
        if code != 0:
            return code, None
        return code, json.loads(data).get("data")

    def GetFsmMode(self):
        code, data = self._Call(ROBOT_API_ID_LOCO_GET_FSM_MODE, "{}")
        if code != 0:
            return code, None
        return code, json.loads(data).get("data")

    def SetFsmId(self, fsm_id: int):
        parameter = json.dumps({"data": fsm_id})
        code, _ = self._Call(ROBOT_API_ID_LOCO_SET_FSM_ID, parameter)
        return code

    def SetVelocity(self, vx: float, vy: float, omega: float, duration: float = 1.0):
        parameter = json.dumps({"velocity": [vx, vy, omega], "duration": duration})
        code, _ = self._Call(ROBOT_API_ID_LOCO_SET_VELOCITY, parameter)
        return code

    def SetSpeedMode(self, speed_mode: int):
        parameter = json.dumps({"data": speed_mode})
        code, _ = self._Call(ROBOT_API_ID_LOCO_SET_SPEED_MODE, parameter)
        return code

    def Damp(self):
        return self.SetFsmId(1)

    def Start(self):
        return self.SetFsmId(811)

    def StandUp(self):
        return self.SetFsmId(4)

    def ZeroTorque(self):
        return self.SetFsmId(0)

    def StopMove(self):
        return self.SetVelocity(0.0, 0.0, 0.0)

    def Move(self, vx: float, vy: float, vyaw: float, continous_move: bool = None):
        if continous_move is None:
            continous_move = self.continous_move_
        duration = 864000.0 if continous_move else 1.0
        return self.SetVelocity(vx, vy, vyaw, duration)

    def SwitchMoveMode(self, flag: bool):
        self.continous_move_ = flag
        return 0
