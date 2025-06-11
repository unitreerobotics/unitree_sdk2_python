"""
Service name and API version
"""
SPORT_SERVICE_NAME = "sport"
SPORT_API_VERSION  = "1.0.0.1"

# ------------------------------------------------------------------ #
#  High-level / legacy IDs (kept from ≤ V1.1.5)                       #
# ------------------------------------------------------------------ #
SPORT_API_ID_DAMP               = 1001
SPORT_API_ID_BALANCESTAND       = 1002
SPORT_API_ID_STOPMOVE           = 1003
SPORT_API_ID_STANDUP            = 1004
SPORT_API_ID_STANDDOWN          = 1005
SPORT_API_ID_RECOVERYSTAND      = 1006
SPORT_API_ID_EULER              = 1007
SPORT_API_ID_MOVE               = 1008
SPORT_API_ID_SIT                = 1009
SPORT_API_ID_RISESIT            = 1010
SPORT_API_ID_SWITCHGAIT         = 1011
SPORT_API_ID_TRIGGER            = 1012
SPORT_API_ID_BODYHEIGHT         = 1013
SPORT_API_ID_FOOTRAISEHEIGHT    = 1014
SPORT_API_ID_SPEEDLEVEL         = 1015
SPORT_API_ID_HELLO              = 1016
SPORT_API_ID_STRETCH            = 1017
SPORT_API_ID_TRAJECTORYFOLLOW   = 1018
SPORT_API_ID_CONTINUOUSGAIT     = 1019
SPORT_API_ID_CONTENT            = 1020
SPORT_API_ID_WALLOW             = 1021
SPORT_API_ID_DANCE1             = 1022
SPORT_API_ID_DANCE2             = 1023
SPORT_API_ID_GETBODYHEIGHT      = 1024
SPORT_API_ID_GETFOOTRAISEHEIGHT = 1025
SPORT_API_ID_GETSPEEDLEVEL      = 1026
SPORT_API_ID_SWITCHJOYSTICK     = 1027
SPORT_API_ID_POSE               = 1028
SPORT_API_ID_SCRAPE             = 1029
SPORT_API_ID_FRONTFLIP          = 1030
SPORT_API_ID_FRONTJUMP          = 1031
SPORT_API_ID_FRONTPOUNCE        = 1032
SPORT_API_ID_WIGGLEHIPS         = 1033
SPORT_API_ID_GETSTATE           = 1034
SPORT_API_ID_HEART              = 1036

# ------------------------------------------------------------------ #
#  Base gaits moved to 106x in V 1.1.6                               #
# ------------------------------------------------------------------ #
SPORT_API_ID_STATICWALK         = 1061
SPORT_API_ID_TROTRUN            = 1062
SPORT_API_ID_ECONOMICGAIT       = 1063

# Aliases with ROBOT_ prefix (needed for RegistApi calls)
ROBOT_SPORT_API_ID_STATICWALK   = 1061
ROBOT_SPORT_API_ID_TROTRUN      = 1062
ROBOT_SPORT_API_ID_ECONOMICGAIT = 1063

# ------------------------------------------------------------------ #
#  Legacy flips                                                      #
# ------------------------------------------------------------------ #
ROBOT_SPORT_API_ID_LEFTFLIP     = 2041
ROBOT_SPORT_API_ID_BACKFLIP     = 2043

# ------------------------------------------------------------------ #
#  V2.0 motion-switcher / AI-mode IDs                                #
# ------------------------------------------------------------------ #
ROBOT_SPORT_API_ID_HANDSTAND        = 2044
ROBOT_SPORT_API_ID_FREEWALK         = 2045
ROBOT_SPORT_API_ID_FREEBOUND        = 2046
ROBOT_SPORT_API_ID_FREEJUMP         = 2047
ROBOT_SPORT_API_ID_FREEAVOID        = 2048
ROBOT_SPORT_API_ID_CLASSICWALK      = 2049
ROBOT_SPORT_API_ID_WALKUPRIGHT      = 2050
ROBOT_SPORT_API_ID_CROSSSTEP        = 2051
ROBOT_SPORT_API_ID_AUTORECOVERY_SET = 2054
ROBOT_SPORT_API_ID_AUTORECOVERY_GET = 2055
ROBOT_SPORT_API_ID_SWITCHAVOIDMODE  = 2058

# ------------------------------------------------------------------ #
#  Error codes                                                       #
# ------------------------------------------------------------------ #
SPORT_ERR_CLIENT_POINT_PATH = 4101
SPORT_ERR_SERVER_OVERTIME   = 4201
SPORT_ERR_SERVER_NOT_INIT   = 4202
