import json

from ...rpc.client import Client
from .sport_api import *

"""
" SPORT_PATH_POINT_SIZE
"""
SPORT_PATH_POINT_SIZE = 30


"""
" class PathPoint
"""
class PathPoint:
    def __init__(self, timeFromStart: float, x: float, y: float, yaw: float, vx: float, vy: float, vyaw: float):
        self.timeFromStart = timeFromStart
        self.x = x
        self.y = y
        self.yaw = yaw
        self.vx = vx
        self.vy = vy
        self.vyaw = vyaw


"""
" class SportClient
"""
class SportClient(Client):
    def __init__(self, enableLease: bool = False):
        super().__init__(SPORT_SERVICE_NAME, enableLease)


    def Init(self):
        # set api version
        self._SetApiVerson(SPORT_API_VERSION)
        
        # regist api
        self._RegistApi(SPORT_API_ID_DAMP, 0)                  # Damp
        self._RegistApi(SPORT_API_ID_BALANCESTAND, 0)          # BalanceStand
        self._RegistApi(SPORT_API_ID_STOPMOVE, 0)              # StopMove
        self._RegistApi(SPORT_API_ID_STANDUP, 0)               # StandUp
        self._RegistApi(SPORT_API_ID_STANDDOWN, 0)             # StandDown
        self._RegistApi(SPORT_API_ID_RECOVERYSTAND, 0)         # RecoveryStand
        self._RegistApi(SPORT_API_ID_EULER, 0)                 # Euler
        self._RegistApi(SPORT_API_ID_MOVE, 0)                  # Move
        self._RegistApi(SPORT_API_ID_SIT, 0)                   # Sit
        self._RegistApi(SPORT_API_ID_RISESIT, 0)               # RiseSit
        self._RegistApi(SPORT_API_ID_SPEEDLEVEL, 0)            # SpeedLevel
        self._RegistApi(SPORT_API_ID_HELLO, 0)                 # Hello
        self._RegistApi(SPORT_API_ID_STRETCH, 0)               # Stretch
        self._RegistApi(SPORT_API_ID_CONTENT, 0)               # Content
        self._RegistApi(SPORT_API_ID_DANCE1, 0)                # Dance1
        self._RegistApi(SPORT_API_ID_DANCE2, 0)                # Dance2
        self._RegistApi(SPORT_API_ID_SWITCHJOYSTICK, 0)        # SwitchJoystick
        self._RegistApi(SPORT_API_ID_POSE, 0)                  # Pose
        self._RegistApi(SPORT_API_ID_SCRAPE, 0)                # Scrape
        self._RegistApi(SPORT_API_ID_FRONTFLIP, 0)             # FrontFlip
        self._RegistApi(SPORT_API_ID_FRONTJUMP, 0)             # FrontJump
        self._RegistApi(SPORT_API_ID_FRONTPOUNCE, 0)           # FrontPounce
        self._RegistApi(SPORT_API_ID_HEART, 0)                 # Heart
        self._RegistApi(SPORT_API_ID_STATICWALK, 0)            # StaticWalk
        self._RegistApi(SPORT_API_ID_TROTRUN, 0)               # TrotRun
        self._RegistApi(SPORT_API_ID_ECONOMICGAIT, 0)          # EconomicGait
        self._RegistApi(SPORT_API_ID_LEFTFLIP, 0)              # LeftFlip
        self._RegistApi(SPORT_API_ID_BACKFLIP, 0)              # BackFlip
        self._RegistApi(SPORT_API_ID_HANDSTAND, 0)             # HandStand
        self._RegistApi(SPORT_API_ID_FREEWALK, 0)              # FreeWalk
        self._RegistApi(SPORT_API_ID_FREEBOUND, 0)             # FreeBound
        self._RegistApi(SPORT_API_ID_FREEJUMP, 0)              # FreeJump
        self._RegistApi(SPORT_API_ID_FREEAVOID, 0)             # FreeAvoid
        self._RegistApi(SPORT_API_ID_CLASSICWALK, 0)           # ClassicWalk
        self._RegistApi(SPORT_API_ID_WALKUPRIGHT, 0)           # WalkUpright
        self._RegistApi(SPORT_API_ID_CROSSSTEP, 0)             # CrossStep
        self._RegistApi(SPORT_API_ID_AUTORECOVERY_SET, 0)      # AutoRecoverySet
        self._RegistApi(SPORT_API_ID_AUTORECOVERY_GET, 0)      # AutoRecoveryGet
        self._RegistApi(SPORT_API_ID_SWITCHAVOIDMODE, 0)       # SwitchAvoidMode

    # 1001
    def Damp(self):
        p = {}
        parameter = json.dumps(p)
        code, data = self._Call(SPORT_API_ID_DAMP, parameter)
        return code
    
    # 1002
    def BalanceStand(self):
        p = {}
        parameter = json.dumps(p)
        code, data = self._Call(SPORT_API_ID_BALANCESTAND, parameter)
        return code
    
    # 1003
    def StopMove(self):
        p = {}
        parameter = json.dumps(p)
        code, data = self._Call(SPORT_API_ID_STOPMOVE, parameter)
        return code

    # 1004
    def StandUp(self):
        p = {}
        parameter = json.dumps(p)
        code, data = self._Call(SPORT_API_ID_STANDUP, parameter)
        return code

    # 1005
    def StandDown(self):
        p = {}
        parameter = json.dumps(p)
        code, data = self._Call(SPORT_API_ID_STANDDOWN, parameter)
        return code

    # 1006
    def RecoveryStand(self):
        p = {}
        parameter = json.dumps(p)
        code, data = self._Call(SPORT_API_ID_RECOVERYSTAND, parameter)
        return code

    # 1007
    def Euler(self, roll: float, pitch: float, yaw: float):
        p = {}
        p["x"] = roll
        p["y"] = pitch
        p["z"] = yaw
        parameter = json.dumps(p)
        code, data = self._Call(SPORT_API_ID_EULER, parameter)
        return code

    # 1008
    def Move(self, vx: float, vy: float, vyaw: float):
        p = {}
        p["x"] = vx
        p["y"] = vy
        p["z"] = vyaw
        parameter = json.dumps(p)
        code = self._CallNoReply(SPORT_API_ID_MOVE, parameter)
        return code

    # 1009
    def Sit(self):
        p = {}
        parameter = json.dumps(p)
        code, data = self._Call(SPORT_API_ID_SIT, parameter)
        return code

    #1010
    def RiseSit(self):
        p = {}
        parameter = json.dumps(p)
        code, data = self._Call(SPORT_API_ID_RISESIT, parameter)
        return code

    # 1015
    def SpeedLevel(self, level: int):
        p = {}
        p["data"] = level
        parameter = json.dumps(p)
        code, data = self._Call(SPORT_API_ID_SPEEDLEVEL, parameter)
        return code

    # 1016
    def Hello(self):
        p = {}
        parameter = json.dumps(p)
        code, data = self._Call(SPORT_API_ID_HELLO, parameter)
        return code

    # 1017
    def Stretch(self):
        p = {}
        parameter = json.dumps(p)
        code, data = self._Call(SPORT_API_ID_STRETCH, parameter)
        return code

    # 1020
    def Content(self):
        p = {}
        parameter = json.dumps(p)
        code, data = self._Call(SPORT_API_ID_CONTENT, parameter)
        return code

    # 1022
    def Dance1(self):
        p = {}
        parameter = json.dumps(p)
        code, data = self._Call(SPORT_API_ID_DANCE1, parameter)
        return code

    # 1023
    def Dance2(self):
        p = {}
        parameter = json.dumps(p)
        code, data = self._Call(SPORT_API_ID_DANCE2, parameter)
        return code

    # 1027
    def SwitchJoystick(self, on: bool):
        p = {}
        p["data"] = on
        parameter = json.dumps(p)
        code, data = self._Call(SPORT_API_ID_SWITCHJOYSTICK, parameter)
        return code

    # 1028
    def Pose(self, flag: bool):
        p = {}
        p["data"] = flag
        parameter = json.dumps(p)
        code, data = self._Call(SPORT_API_ID_POSE, parameter)
        return code

    # 1029
    def Scrape(self):
        p = {}
        parameter = json.dumps(p)
        code, data = self._Call(SPORT_API_ID_SCRAPE, parameter)
        return code

    # 1030
    def FrontFlip(self):
        p = {}
        parameter = json.dumps(p)
        code, data = self._Call(SPORT_API_ID_FRONTFLIP, parameter)
        return code

    # 1031
    def FrontJump(self):
        p = {}
        parameter = json.dumps(p)
        code, data = self._Call(SPORT_API_ID_FRONTJUMP, parameter)
        return code

    # 1032
    def FrontPounce(self):
        p = {}
        parameter = json.dumps(p)
        code, data = self._Call(SPORT_API_ID_FRONTPOUNCE, parameter)
        return code

    # 1036
    def Heart(self):
        p = {}
        parameter = json.dumps(p)
        code, data = self._Call(SPORT_API_ID_HEART, parameter)
        return code
    
    # 2041
    def LeftFlip(self):
        p = {}
        parameter = json.dumps(p)
        code, data = self._Call(SPORT_API_ID_LEFTFLIP, parameter)
        return code

    # 2043
    def BackFlip(self):
        p = {}
        parameter = json.dumps(p)
        code, data = self._Call(SPORT_API_ID_BACKFLIP, parameter)
        return code

    # 2045
    def FreeWalk(self):
        p = {}
        parameter = json.dumps(p)
        code, data = self._Call(SPORT_API_ID_FREEWALK, parameter)
        return code

    # 2046
    def FreeBound(self, flag: bool):
        p = {}
        p["data"] = flag
        parameter = json.dumps(p)
        code, data = self._Call(SPORT_API_ID_FREEBOUND, parameter)
        return code
    
    # 2047
    def FreeJump(self, flag: bool):
        p = {}
        p["data"] = flag
        parameter = json.dumps(p)
        code, data = self._Call(SPORT_API_ID_FREEJUMP, parameter)
        return code

    # 2048
    def FreeAvoid(self, flag: bool):
        p = {}
        p["data"] = flag
        parameter = json.dumps(p)
        code, data = self._Call(SPORT_API_ID_FREEAVOID, parameter)
        return code
    
    # 2050
    def WalkUpright(self, flag: bool):
        p = {}
        p["data"] = flag
        parameter = json.dumps(p)
        code, data = self._Call(SPORT_API_ID_WALKUPRIGHT, parameter)
        return code

    # 2051
    def CrossStep(self, flag: bool):  
        p = {}
        p["data"] = flag
        parameter = json.dumps(p)
        code, data = self._Call(SPORT_API_ID_CROSSSTEP, parameter)
        return code
    
    # 1061
    def StaticWalk(self):
        p = {}
        parameter = json.dumps(p)
        code, data = self._Call(SPORT_API_ID_STATICWALK, parameter)
        return code
 
    # 1062
    def TrotRun(self):
        p = {}
        parameter = json.dumps(p)
        code, data = self._Call(SPORT_API_ID_TROTRUN, parameter)
        return code

    # 2044
    def HandStand(self, flag: bool):
        p = {}
        p["data"] = flag
        parameter = json.dumps(p)
        code, data = self._Call(SPORT_API_ID_HANDSTAND, parameter)
        return code
    # 2049
    def ClassicWalk(self, flag: bool):
        p = {}
        p["data"] = flag
        parameter = json.dumps(p)
        code, data = self._Call(SPORT_API_ID_CLASSICWALK, parameter)
        return code

    # 2054
    def AutoRecoverySet(self, enabled: bool):
        p = {}
        p["data"] = enabled
        parameter = json.dumps(p)
        code, data = self._Call(SPORT_API_ID_AUTORECOVERY_SET, parameter)
        return code

    # 2055
    def AutoRecoveryGet(self):
        p = {}
        parameter = json.dumps(p)
        code, data = self._Call(SPORT_API_ID_AUTORECOVERY_GET, parameter)
        if code == 0:
            d = json.loads(data)
            return code, d["data"]
        else:
            return code, None

    # 2058
    def SwitchAvoidMode(self):
        p = {}
        parameter = json.dumps(p)
        code, data = self._Call(SPORT_API_ID_SWITCHAVOIDMODE, parameter)
        return code
