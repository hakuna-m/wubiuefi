"Signed Messages"

from Msg import Msg

from openpgp.code import *
from openpgp.sap.exceptions import *


class SignedMsg(Msg):
    """Signed Message

    :IVariables:
        - `sigs`: list of `OpenPGP.packet.Signature` instances which
          sign `msg`
        - `msg`: `Msg` subclass instance (data signed by `sig`)
        - `_seq`: list of items in message sequence
        - `_d`: string of data used to build message

    :CVariables:
        - `type`: constant `MSG_SIGNED` (see `OpenPGP.constant.messages`)
    """
    type = MSG_SIGNED

    def list_target_keyids(self):
        """List all signing key IDs.
        """
        return [k.body.keyid for k in self.sigs if hasattr(k.body, 'keyid')]

