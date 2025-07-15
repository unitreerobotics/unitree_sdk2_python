import json
from ...rpc.client import Client
from .sport_api import *

# number of points expected by TrajectoryFollow
SPORT_PATH_POINT_SIZE = 30


class PathPoint:
    """Single trajectory point for TrajectoryFollow()."""
    def __init__(self, timeFromStart: float, x: float, y: float,
                 yaw: float, vx: float, vy: float, vyaw: float):
        self.timeFromStart = timeFromStart
        self.x = x
        self.y = y
        self.yaw = yaw
        self.vx = vx
        self.vy = vy
        self.vyaw = vyaw


class SportClient(Client):
    """
    Python wrapper for Unitree Go2 high-level / AI motion control (SDK ≥ V1.1.6).
    """

    def __init__(self, enableLease: bool = False):
        super().__init__(SPORT_SERVICE_NAME, enableLease)

    # --------------------------------------------------------------------- #
    #  Init – register every API ID exactly once                            #
    # --------------------------------------------------------------------- #
    def Init(self):
        self._SetApiVerson(SPORT_API_VERSION)

        # 1) legacy sport (basic posture, speed, etc.)
        legacy_ids = [
            SPORT_API_ID_DAMP, SPORT_API_ID_BALANCESTAND, SPORT_API_ID_STOPMOVE,
            SPORT_API_ID_STANDUP, SPORT_API_ID_STANDDOWN, SPORT_API_ID_RECOVERYSTAND,
            SPORT_API_ID_EULER, SPORT_API_ID_MOVE, SPORT_API_ID_SIT, SPORT_API_ID_RISESIT,
            SPORT_API_ID_SWITCHGAIT, SPORT_API_ID_TRIGGER, SPORT_API_ID_BODYHEIGHT,
            SPORT_API_ID_FOOTRAISEHEIGHT, SPORT_API_ID_SPEEDLEVEL, SPORT_API_ID_HELLO,
            SPORT_API_ID_STRETCH, SPORT_API_ID_TRAJECTORYFOLLOW, SPORT_API_ID_CONTINUOUSGAIT,
            SPORT_API_ID_WALLOW, SPORT_API_ID_DANCE1, SPORT_API_ID_DANCE2,
            SPORT_API_ID_SWITCHJOYSTICK, SPORT_API_ID_POSE, SPORT_API_ID_SCRAPE,
            SPORT_API_ID_FRONTFLIP, SPORT_API_ID_FRONTJUMP, SPORT_API_ID_FRONTPOUNCE,
            SPORT_API_ID_WIGGLEHIPS, SPORT_API_ID_GETSTATE, SPORT_API_ID_ECONOMICGAIT,
            SPORT_API_ID_HEART, SPORT_API_ID_STATICWALK, SPORT_API_ID_TROTRUN
        ]
        for api in legacy_ids:
            self._RegistApi(api, 0)

        # flips still exposed as “robot” IDs
        self._RegistApi(ROBOT_SPORT_API_ID_LEFTFLIP, 0)
        self._RegistApi(ROBOT_SPORT_API_ID_BACKFLIP, 0)

        # 2) AI / motion-switcher IDs (V2.0)
        switcher_ids = [
            ROBOT_SPORT_API_ID_HANDSTAND, ROBOT_SPORT_API_ID_FREEWALK,
            ROBOT_SPORT_API_ID_FREEBOUND, ROBOT_SPORT_API_ID_FREEJUMP,
            ROBOT_SPORT_API_ID_FREEAVOID, ROBOT_SPORT_API_ID_CLASSICWALK,
            ROBOT_SPORT_API_ID_WALKUPRIGHT, ROBOT_SPORT_API_ID_CROSSSTEP,
            ROBOT_SPORT_API_ID_AUTORECOVERY_SET, ROBOT_SPORT_API_ID_AUTORECOVERY_GET,
            ROBOT_SPORT_API_ID_SWITCHAVOIDMODE
        ]
        for api in switcher_ids:
            self._RegistApi(api, 0)

    # --------------------------------------------------------------------- #
    #  Legacy high-level wrappers                                           #
    # --------------------------------------------------------------------- #
    def Damp(self):               return self._Call(SPORT_API_ID_DAMP, "{}")[0]
    def BalanceStand(self):       return self._Call(SPORT_API_ID_BALANCESTAND, "{}")[0]
    def StopMove(self):           return self._Call(SPORT_API_ID_STOPMOVE, "{}")[0]
    def StandUp(self):            return self._Call(SPORT_API_ID_STANDUP, "{}")[0]
    def StandDown(self):          return self._Call(SPORT_API_ID_STANDDOWN, "{}")[0]
    def RecoveryStand(self):      return self._Call(SPORT_API_ID_RECOVERYSTAND, "{}")[0]

    def Euler(self, roll, pitch, yaw):
        return self._Call(SPORT_API_ID_EULER,
                          json.dumps({"x": roll, "y": pitch, "z": yaw}))[0]

    def Move(self, vx, vy, vyaw):
        return self._CallNoReply(SPORT_API_ID_MOVE,
                                 json.dumps({"x": vx, "y": vy, "z": vyaw}))

    def Sit(self):                return self._Call(SPORT_API_ID_SIT, "{}")[0]
    def RiseSit(self):            return self._Call(SPORT_API_ID_RISESIT, "{}")[0]
    def SwitchGait(self, t):      return self._Call(SPORT_API_ID_SWITCHGAIT,
                                                    json.dumps({"data": t}))[0]

    def BodyHeight(self, h):      return self._Call(SPORT_API_ID_BODYHEIGHT,
                                                    json.dumps({"data": h}))[0]
    def FootRaiseHeight(self, h): return self._Call(SPORT_API_ID_FOOTRAISEHEIGHT,
                                                    json.dumps({"data": h}))[0]
    def SpeedLevel(self, lvl):    return self._Call(SPORT_API_ID_SPEEDLEVEL,
                                                    json.dumps({"data": lvl}))[0]
    def Hello(self):              return self._Call(SPORT_API_ID_HELLO, "{}")[0]
    def Stretch(self):            return self._Call(SPORT_API_ID_STRETCH, "{}")[0]

    def ContinuousGait(self, flag):
        return self._Call(SPORT_API_ID_CONTINUOUSGAIT,
                          json.dumps({"data": flag}))[0]

    def EconomicGait(self, flag):
        return self._Call(SPORT_API_ID_ECONOMICGAIT,
                          json.dumps({"data": flag}))[0]

    # flips
    def LeftFlip(self): return self._Call(ROBOT_SPORT_API_ID_LEFTFLIP,
                                          json.dumps({"data": True}))[0]
    def BackFlip(self): return self._Call(ROBOT_SPORT_API_ID_BACKFLIP,
                                          json.dumps({"data": True}))[0]

    # moved gaits
    def StaticWalk(self): return self._Call(ROBOT_SPORT_API_ID_STATICWALK, "{}")[0]
    def TrotRun(self):    return self._Call(ROBOT_SPORT_API_ID_TROTRUN, "{}")[0]

    # --------------------------------------------------------------------- #
    #  Motion-switcher wrappers                                             #
    # --------------------------------------------------------------------- #
    def FreeWalk(self, f):   return self._Call(ROBOT_SPORT_API_ID_FREEWALK,
                                               json.dumps({"data": f}))[0]
    def FreeBound(self, f):  return self._Call(ROBOT_SPORT_API_ID_FREEBOUND,
                                               json.dumps({"data": f}))[0]
    def FreeJump(self, f):   return self._Call(ROBOT_SPORT_API_ID_FREEJUMP,
                                               json.dumps({"data": f}))[0]
    def FreeAvoid(self, f):  return self._Call(ROBOT_SPORT_API_ID_FREEAVOID,
                                               json.dumps({"data": f}))[0]

    def HandStand(self, f):  return self._Call(ROBOT_SPORT_API_ID_HANDSTAND,
                                               json.dumps({"data": f}))[0]
    def WalkUpright(self, f):return self._Call(ROBOT_SPORT_API_ID_WALKUPRIGHT,
                                               json.dumps({"data": f}))[0]
    def CrossStep(self, f):  return self._Call(ROBOT_SPORT_API_ID_CROSSSTEP,
                                               json.dumps({"data": f}))[0]
    def ClassicWalk(self, f):return self._Call(ROBOT_SPORT_API_ID_CLASSICWALK,
                                               json.dumps({"data": f}))[0]

    def AutoRecoverSet(self, f):
        return self._Call(ROBOT_SPORT_API_ID_AUTORECOVERY_SET,
                          json.dumps({"data": f}))[0]

    def AutoRecoverGet(self):
        code, data = self._Call(ROBOT_SPORT_API_ID_AUTORECOVERY_GET, "{}")
        return code, json.loads(data)["data"] if code == 0 else (code, None)

    def SwitchAvoidMode(self):
        return self._Call(ROBOT_SPORT_API_ID_SWITCHAVOIDMODE, "{}")[0]
