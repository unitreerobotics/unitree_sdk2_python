from unitree_sdk2py.idl.default import *
from unitree_sdk2py.utils.crc import CRC

crc = CRC()

"""
" LowCmd CRC
"""
cmd = unitree_go_msg_dds__LowCmd_()
cmd.crc = crc.Crc(cmd)

state = unitree_go_msg_dds__LowState_()
state.crc = crc.Crc(state)

print("CRC[LowCmd, LowState]: {}, {}".format(cmd.crc, state.crc))
