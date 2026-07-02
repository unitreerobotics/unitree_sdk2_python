from ...rpc.client import Client
from .video_api import *


class VideoClient(Client):
    def __init__(self):
        super().__init__(VIDEO_SERVICE_NAME, False)

    def Init(self):
        self._SetApiVerson(VIDEO_API_VERSION)
        self._RegistApi(VIDEO_API_ID_GETIMAGESAMPLE, 0)

    def GetImageSample(self):
        return self._CallBinary(VIDEO_API_ID_GETIMAGESAMPLE, [])

