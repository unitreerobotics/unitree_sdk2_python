"""
" service name
"""
AUDIOHUB_SERVICE_NAME = "audiohub"


"""
" service api version
"""
AUDIOHUB_API_VERSION = "1.0.0.1"


"""
" api id
"""
# API ID  |  FUNCTION
# 1001    |  audio list
# 1002    |  select a recording and start playing it
# 1003    |  pause
# 1004    |  unsuspend
# 1005    |  select the previous recording and start playing
# 1006    |  select the next recording and start playing
# 1007    |  set play mode (no cycle, single cycle, list loop)
# 1008    |  select a recording and rename it
# 1009    |  select a recording and delete it. (If the recording is being played,
#            a pop-up message is displayed to confirm that the recording cannot 
#            be played after deletion.)
# 1010    |  get play mode (no cycle, single cycle, list loop)


AUDIOHUB_API_ID_AUDIO_PLAYER_AUDIO_LIST = 1001
AUDIOHUB_API_ID_AUDIO_PLAYER_SELECT_START_PLAY = 1002
AUDIOHUB_API_ID_AUDIO_PLAYER_PAUSE = 1003
AUDIOHUB_API_ID_AUDIO_PLAYER_UNSUSPEND = 1004
AUDIOHUB_API_ID_AUDIO_PLAYER_SELECT_PREV_START_PLAY = 1005
AUDIOHUB_API_ID_AUDIO_PLAYER_SELECT_NEXT_START_PLAY = 1006
AUDIOHUB_API_ID_AUDIO_PLAYER_SET_PLAY_MODE = 1007
AUDIOHUB_API_ID_AUDIO_PLAYER_SELECT_RENAME = 1008
AUDIOHUB_API_ID_AUDIO_PLAYER_SELECT_DELETE = 1009
AUDIOHUB_API_ID_AUDIO_PLAYER_GET_PLAY_MODE = 1010

# API ID  |  FUNCTION
# 2001    |  upload audio file

AUDIOHUB_API_ID_AUDIO_PLAYER_UPLOAD_AUDIO_FILE = 2001

# API ID  |  FUNCTION
# 3001    |  play start_obstacle_avoidance audio
# 3002    |  play exit_obstacle_avoidance audio
# 3003    |  play start_companion_mode audio
# 3004    |  play exit_companion_mode audio

AUDIOHUB_INTERNAL_CORPUS_BASE = 3000
AUDIOHUB_API_ID_INTERNAL_CORPUS_PLAY_START_OBSTACLE_AVOIDANCE = 1
AUDIOHUB_API_ID_INTERNAL_CORPUS_PLAY_EXIT_OBSTACLE_AVOIDANCE = 2
AUDIOHUB_API_ID_INTERNAL_CORPUS_PLAY_START_COMPANION_MODE = 3
AUDIOHUB_API_ID_INTERNAL_CORPUS_PLAY_EXIT_COMPANION_MODE = 4

# API ID  |  FUNCTION
# 4001    |  enter megaphone
# 4002    |  exit megaphone
# 4003    |  upload

AUDIOHUB_API_ID_ENTER_MEGAPHONE = 4001
AUDIOHUB_API_ID_EXIT_MEGAPHONE = 4002
AUDIOHUB_API_ID_UPLOAD_MEGAPHONE = 4003

# API ID  |  FUNCTION
# 5001       Select internal long corpus to play
# 5002       Internal long corpus playback completed notification
# 5003       Stops playing current internal long corpus

AUDIOHUB_API_ID_INTERNAL_LONG_CORPUS_SELECT_TO_PLAY = 5001
AUDIOHUB_API_ID_INTERNAL_LONG_CORPUS_PLAYBACK_COMPLETED = 5002
AUDIOHUB_API_ID_INTERNAL_LONG_CORPUS_STOP_PLAYING = 5003



