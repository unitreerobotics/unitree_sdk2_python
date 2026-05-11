import json
from typing import Dict, Optional, Tuple

from ...rpc.client import Client
from .sport_api import *


"""
" class SportClient
"""
class SportClient(Client):
    def __init__(self):
        super().__init__(ROBOT_SPORT_SERVICE_NAME, False)

    def Init(self):
        # set api version
        self._SetApiVerson(ROBOT_SPORT_API_VERSION)

        # regist api
        self._RegistApi(ROBOT_SPORT_API_ID_DAMP, 0)
        self._RegistApi(ROBOT_SPORT_API_ID_BALANCESTAND, 0)
        self._RegistApi(ROBOT_SPORT_API_ID_STOPMOVE, 0)
        self._RegistApi(ROBOT_SPORT_API_ID_STANDUP, 0)
        self._RegistApi(ROBOT_SPORT_API_ID_STANDDOWN, 0)
        self._RegistApi(ROBOT_SPORT_API_ID_RECOVERYSTAND, 0)
        self._RegistApi(ROBOT_SPORT_API_ID_EULER, 0)
        self._RegistApi(ROBOT_SPORT_API_ID_MOVE, 0)
        self._RegistApi(ROBOT_SPORT_API_ID_SWITCHGAIT, 0)
        self._RegistApi(ROBOT_SPORT_API_ID_BODYHEIGHT, 0)
        self._RegistApi(ROBOT_SPORT_API_ID_SPEEDLEVEL, 0)
        self._RegistApi(ROBOT_SPORT_API_ID_SETAUTORECOVERY, 0)

        self._RegistApi(ROBOT_SPORT_API_ID_BODYPOSITION, 0)
        self._RegistApi(ROBOT_SPORT_API_ID_LEFTSIDEGAIT, 0)
        self._RegistApi(ROBOT_SPORT_API_ID_RIGHTSIDEGAIT, 0)
        self._RegistApi(ROBOT_SPORT_API_ID_HANDSTAND, 0)
        self._RegistApi(ROBOT_SPORT_API_ID_BIPEDSTAND, 0)
        self._RegistApi(ROBOT_SPORT_API_ID_FRONTFLIP, 0)
        self._RegistApi(ROBOT_SPORT_API_ID_BACKFLIP, 0)

        self._RegistApi(ROBOT_SPORT_API_ID_GETSTATE, 0)

    def Damp(self) -> int:
        p = {}
        parameter = json.dumps(p)
        code, data = self._Call(ROBOT_SPORT_API_ID_DAMP, parameter)
        return code

    def BalanceStand(self) -> int:
        p = {}
        parameter = json.dumps(p)
        code, data = self._Call(ROBOT_SPORT_API_ID_BALANCESTAND, parameter)
        return code

    def StopMove(self) -> int:
        p = {}
        parameter = json.dumps(p)
        code, data = self._Call(ROBOT_SPORT_API_ID_STOPMOVE, parameter)
        return code

    def StandUp(self) -> int:
        p = {}
        parameter = json.dumps(p)
        code, data = self._Call(ROBOT_SPORT_API_ID_STANDUP, parameter)
        return code

    def StandDown(self) -> int:
        p = {}
        parameter = json.dumps(p)
        code, data = self._Call(ROBOT_SPORT_API_ID_STANDDOWN, parameter)
        return code

    def RecoveryStand(self) -> int:
        p = {}
        parameter = json.dumps(p)
        code, data = self._Call(ROBOT_SPORT_API_ID_RECOVERYSTAND, parameter)
        return code

    def Euler(self, roll: float, pitch: float, yaw: float) -> int:
        p = {}
        p["x"] = roll
        p["y"] = pitch
        p["z"] = yaw
        parameter = json.dumps(p)
        code, data = self._Call(ROBOT_SPORT_API_ID_EULER, parameter)
        return code

    def Move(self, vx: float, vy: float, vyaw: float) -> int:
        p = {}
        p["x"] = vx
        p["y"] = vy
        p["z"] = vyaw
        parameter = json.dumps(p)
        code, data = self._Call(ROBOT_SPORT_API_ID_MOVE, parameter)
        return code

    def SwitchGait(self, gait_type: int) -> int:
        p = {}
        p["data"] = gait_type
        parameter = json.dumps(p)
        code, data = self._Call(ROBOT_SPORT_API_ID_SWITCHGAIT, parameter)
        return code

    def BodyHeight(self, height: float) -> int:
        p = {}
        p["data"] = height
        parameter = json.dumps(p)
        code, data = self._Call(ROBOT_SPORT_API_ID_BODYHEIGHT, parameter)
        return code

    def SpeedLevel(self, level: int) -> int:
        p = {}
        p["data"] = level
        parameter = json.dumps(p)
        code, data = self._Call(ROBOT_SPORT_API_ID_SPEEDLEVEL, parameter)
        return code

    def BodyPosition(self, x: float, y: float, z: float, yaw: float) -> int:
        p = {}
        p["x"] = x
        p["y"] = y
        p["z"] = z
        p["yaw"] = yaw
        parameter = json.dumps(p)
        code, data = self._Call(ROBOT_SPORT_API_ID_BODYPOSITION, parameter)
        return code

    def LeftSideGait(self, enter: int) -> int:
        p = {}
        p["data"] = enter
        parameter = json.dumps(p)
        code, data = self._Call(ROBOT_SPORT_API_ID_LEFTSIDEGAIT, parameter)
        return code

    def RightSideGait(self, enter: int) -> int:
        p = {}
        p["data"] = enter
        parameter = json.dumps(p)
        code, data = self._Call(ROBOT_SPORT_API_ID_RIGHTSIDEGAIT, parameter)
        return code

    def HandStand(self, enter: int) -> int:
        p = {}
        p["data"] = enter
        parameter = json.dumps(p)
        code, data = self._Call(ROBOT_SPORT_API_ID_HANDSTAND, parameter)
        return code

    def BipedStand(self, enter: int) -> int:
        p = {}
        p["data"] = enter
        parameter = json.dumps(p)
        code, data = self._Call(ROBOT_SPORT_API_ID_BIPEDSTAND, parameter)
        return code

    def FrontFlip(self) -> int:
        p = {}
        parameter = json.dumps(p)
        code, data = self._Call(ROBOT_SPORT_API_ID_FRONTFLIP, parameter)
        return code

    def BackFlip(self) -> int:
        p = {}
        parameter = json.dumps(p)
        code, data = self._Call(ROBOT_SPORT_API_ID_BACKFLIP, parameter)
        return code

    def SetAutoRecovery(self, switch_on: int) -> int:
        p = {}
        p["data"] = switch_on
        parameter = json.dumps(p)
        code, data = self._Call(ROBOT_SPORT_API_ID_SETAUTORECOVERY, parameter)
        return code

    def GetState(self) -> Tuple[int, Optional[Dict[str, str]]]:
        p = {}
        parameter = json.dumps(p)
        code, data = self._Call(ROBOT_SPORT_API_ID_GETSTATE, parameter)
        if code != 0:
            return code, None
        try:
            return code, json.loads(data) if data else {}
        except Exception:
            return code, None

