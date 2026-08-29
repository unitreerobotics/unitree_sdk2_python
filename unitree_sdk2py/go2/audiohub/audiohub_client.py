import logging
import json

from ...rpc.client import Client
from .audiohub_api import *

from pydub import AudioSegment
import base64
import time
import uuid

CHUNK_SIZE = 61440

"""
" class AudioHubClient
"""
class AudioHubClient(Client):
    default_service_name = AUDIOHUB_SERVICE_NAME       

    def __init__(self, *args, **kwargs):
        #self.logger = logger.getChild(self.__class__.__name__) if logger else logging.getLogger(self.__class__.__name__)
        #self.communicator = communicator
        self.serviceName = AudioHubClient.default_service_name
        super().__init__(serviceName=self.serviceName, enabaleLease=False)

    def Init(self):
        # set api version
        self._SetApiVerson(AUDIOHUB_API_VERSION)
        
        # regist api
        self._RegistApi(AUDIOHUB_API_ID_AUDIO_PLAYER_AUDIO_LIST, 0)
        self._RegistApi(AUDIOHUB_API_ID_AUDIO_PLAYER_SELECT_START_PLAY, 0)
        self._RegistApi(AUDIOHUB_API_ID_AUDIO_PLAYER_PAUSE, 0)
        self._RegistApi(AUDIOHUB_API_ID_AUDIO_PLAYER_UNSUSPEND, 0)
        self._RegistApi(AUDIOHUB_API_ID_AUDIO_PLAYER_SET_PLAY_MODE, 0)
        self._RegistApi(AUDIOHUB_API_ID_AUDIO_PLAYER_SELECT_RENAME, 0)
        self._RegistApi(AUDIOHUB_API_ID_AUDIO_PLAYER_SELECT_DELETE, 0)
        self._RegistApi(AUDIOHUB_API_ID_AUDIO_PLAYER_GET_PLAY_MODE, 0)

        self._RegistApi(AUDIOHUB_API_ID_AUDIO_PLAYER_UPLOAD_AUDIO_FILE, 0)

        self._RegistApi(AUDIOHUB_INTERNAL_CORPUS_BASE + AUDIOHUB_API_ID_INTERNAL_CORPUS_PLAY_START_OBSTACLE_AVOIDANCE, 0)
        self._RegistApi(AUDIOHUB_INTERNAL_CORPUS_BASE + AUDIOHUB_API_ID_INTERNAL_CORPUS_PLAY_EXIT_OBSTACLE_AVOIDANCE, 0)
        self._RegistApi(AUDIOHUB_INTERNAL_CORPUS_BASE + AUDIOHUB_API_ID_INTERNAL_CORPUS_PLAY_START_COMPANION_MODE, 0)
        self._RegistApi(AUDIOHUB_INTERNAL_CORPUS_BASE + AUDIOHUB_API_ID_INTERNAL_CORPUS_PLAY_EXIT_COMPANION_MODE, 0)

        self._RegistApi(AUDIOHUB_API_ID_ENTER_MEGAPHONE, 0)
        self._RegistApi(AUDIOHUB_API_ID_EXIT_MEGAPHONE, 0)
        self._RegistApi(AUDIOHUB_API_ID_UPLOAD_MEGAPHONE, 0)

        self._RegistApi(AUDIOHUB_API_ID_INTERNAL_LONG_CORPUS_SELECT_TO_PLAY, 0)
        self._RegistApi(AUDIOHUB_API_ID_INTERNAL_LONG_CORPUS_PLAYBACK_COMPLETED, 0)
        self._RegistApi(AUDIOHUB_API_ID_INTERNAL_LONG_CORPUS_STOP_PLAYING, 0)

    # 1001
    def AudioPlayerGetAudioList(self):
        p = {}
        parameter = json.dumps(p)
        code, data = self._Call(AUDIOHUB_API_ID_AUDIO_PLAYER_AUDIO_LIST, parameter)
        if code == 0:
            return code, json.loads(data)
        else:
            return code, None
        
    # 1002
    def AudioPlayerPlayByUUID(self, uuid):
        p = {}
        p['unique_id'] = uuid
        parameter = json.dumps(p)
        code, data = self._Call(AUDIOHUB_API_ID_AUDIO_PLAYER_SELECT_START_PLAY, parameter)
        return code
    
    # 1003
    def AudioPlayerPause(self):
        p = {}
        parameter = json.dumps(p)
        code, data = self._Call(AUDIOHUB_API_ID_AUDIO_PLAYER_PAUSE, parameter)
        return code
    
    # 1004
    def AudioPlayerResume(self):
        p = {}
        parameter = json.dumps(p)
        code, data = self._Call(AUDIOHUB_API_ID_AUDIO_PLAYER_UNSUSPEND, parameter)
        return code
    
    # 1007
    #playmode: single_cycle, no_cycle, list_loop
    def AudioPlayerSetPlayMode(self, playMode): 
        p = {}
        p["play_mode"] = playMode
        parameter = json.dumps(p)
        code, data = self._Call(AUDIOHUB_API_ID_AUDIO_PLAYER_SET_PLAY_MODE, parameter)
        return code
    
    # 1008
    def AudioPlayerRenameRecord(self, uuid, newName): 
        p = {}
        p["unique_id"] = uuid
        p["new_name"] = newName
        parameter = json.dumps(p)
        code, data = self._Call(AUDIOHUB_API_ID_AUDIO_PLAYER_SELECT_RENAME, parameter)
        return code
    
    # 1009
    def AudioPlayerdeleteRecord(self, uuid): 
        p = {}
        p["unique_id"] = uuid
        parameter = json.dumps(p)
        code, data = self._Call(AUDIOHUB_API_ID_AUDIO_PLAYER_SELECT_DELETE, parameter)
        return code
    
    # 1009
    def AudioPlayerGetPlayMode(self): 
        p = {}
        parameter = json.dumps(p)
        code, data = self._Call(AUDIOHUB_API_ID_AUDIO_PLAYER_GET_PLAY_MODE, parameter)
        if code == 0:
            return code, json.loads(data)
        else:
            return code, None
    

    # 2001
    # Upload mp3 or wav
    def AudioPlayerUploadAudioFile(self, audiofile_path):
        if audiofile_path.endswith(".mp3"):
            # Convert MP3 to WAV
            audio = AudioSegment.from_mp3(audiofile_path)
            wav_file_path = audiofile_path.replace('.mp3', '.wav')
            audio.export(wav_file_path, format='wav')
        else:
            wav_file_path = audiofile_path

        # Read WAV file and split into chunks
        with open(wav_file_path, 'rb') as f:
            audio_data = f.read()

        chunks = [audio_data[i:i + CHUNK_SIZE] for i in range(0, len(audio_data), CHUNK_SIZE)]
        total_chunks = len(chunks)

        for index, chunk in enumerate(chunks):
            block_content = base64.b64encode(chunk).decode('utf-8')
            p = {
                'file_size': len(audio_data),
                'current_block_size': len(chunk),
                'file_type': 'wav',
                'file_md5': 'asdasd',  # Replace with actual MD5 hash
                'file_name': 'audio_' + str(uuid.uuid4())[:4],
                'create_time': int(time.time() * 1000),
                'block_content': block_content,
                'current_block_index': index + 1,
                'total_block_number': total_chunks
            }
            parameter = json.dumps(p)
            code, data = self._Call(AUDIOHUB_API_ID_AUDIO_PLAYER_UPLOAD_AUDIO_FILE, parameter)
            if code != 0:
                # Handle error
                #self.logger.error(f"Error uploading chunk {index + 1}/{total_chunks}: Error code: {code}")
                return code

        return code
    
    # 3001
    def InternalCorpusPlay(self, num):
        p = {}
        parameter = json.dumps(p)
        code, data = self._Call(AUDIOHUB_INTERNAL_CORPUS_BASE + num, parameter)
        return code
    
    #4001
    def MegaphoneEnter(self):
        p = {}
        parameter = json.dumps(p)
        code, data = self._Call(AUDIOHUB_API_ID_ENTER_MEGAPHONE, parameter)
        return code
    
    #4002
    def MegaphoneExit(self):
        p = {}
        parameter = json.dumps(p)
        code, data = self._Call(AUDIOHUB_API_ID_EXIT_MEGAPHONE, parameter)
        return code
    
    #4003
    def MegaphoneUpload(self, audiofile_path):
        if audiofile_path.endswith(".mp3"):
            # Convert MP3 to WAV
            audio = AudioSegment.from_mp3(audiofile_path)
            wav_file_path = audiofile_path.replace('.mp3', '.wav')
            audio.export(wav_file_path, format='wav')
        else:
            wav_file_path = audiofile_path

        # Read WAV file and split into chunks
        with open(wav_file_path, 'rb') as f:
            audio_data = f.read()

        chunks = [audio_data[i:i + CHUNK_SIZE] for i in range(0, len(audio_data), CHUNK_SIZE)]
        total_chunks = len(chunks)

        for index, chunk in enumerate(chunks):
            block_content = base64.b64encode(chunk).decode('utf-8')
            p = {
                'current_block_size': len(chunk),
                'block_content': block_content,
                'current_block_index': index + 1,
                'total_block_number': total_chunks
            }
            parameter = json.dumps(p)
            code, data = self._Call(AUDIOHUB_API_ID_UPLOAD_MEGAPHONE, parameter)
            if code != 0:
                # Handle error
                #self.logger.error(f"Error uploading chunk {index + 1}/{total_chunks}: Error code: {code}")
                return code

        return code
    
    #5001
    def InternalLongCorpusPlay(self, name, callback=None):
        p = {}
        p['corpus_name'] = name
        parameter = json.dumps(p)
        code, data = self._Call(AUDIOHUB_API_ID_INTERNAL_LONG_CORPUS_SELECT_TO_PLAY, parameter) 
        return code
    
    
    #5002
    def InternalLongCorpusPlaybackCompleted(self):
        p = {}
        parameter = json.dumps(p)
        code, data = self._Call(AUDIOHUB_API_ID_INTERNAL_LONG_CORPUS_PLAYBACK_COMPLETED, parameter) 
        return code
    

    #5003
    def InternalLongCorpusStop(self):
        p = {}
        parameter = json.dumps(p)
        code, data = self._Call(AUDIOHUB_API_ID_INTERNAL_LONG_CORPUS_STOP_PLAYING, parameter)
        return code
    
    