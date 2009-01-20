"""Compressed Messages
"""
from openpgp.sap.exceptions import *
from openpgp.code import *
from Msg import Msg

class CompressedMsg(Msg):
    """Compressed Message

    :IVariables:
        - `compressed`: `OpenPGP.packet.CompressedData` instance
        - `_seq`: list of items in message sequence
        - `_d`: string of data used to build message

    :CVariables:
        - `type`: integer constant `MSG_COMPRESSED`
          (see `OpenPGP.constant.messages`)
    """
    type = MSG_COMPRESSED

