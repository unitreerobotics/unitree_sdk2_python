import json

from ...rpc.client import Client
from .obstacles_avoid_api import *


"""
" class ObstaclesAvoidClient
"""
class ObstaclesAvoidClient(Client):
    def __init__(self):
        super().__init__(OBSTACLES_AVOID_SERVICE_NAME, False)

    def Init(self):
        # set api version
        self._SetApiVerson(OBSTACLES_AVOID_API_VERSION)
        # regist api
        self._RegistApi(OBSTACLES_AVOID_API_ID_SWITCH_SET, 0)
        self._RegistApi(OBSTACLES_AVOID_API_ID_SWITCH_GET, 0)

    # 1001
    def SwitchSet(self, on: bool):
        p = {}
        p["enable"] = on
        parameter = json.dumps(p)

        code, data = self._Call(OBSTACLES_AVOID_API_ID_SWITCH_SET, parameter)
        return code

    # 1002
    def SwitchGet(self):
        p = {}
        parameter = json.dumps(p)

        code, data = self._Call(OBSTACLES_AVOID_API_ID_SWITCH_GET, parameter)
        if code == 0:
            d = json.loads(data)
            return code, d["enable"]
        else:
            return code, None