"""Literal Messages
"""
from openpgp.code import *
from Msg import Msg

class LiteralMsg(Msg):
    """
    :IVariables:
        - `literals`: list of `LiteralData` instances
        - `_seq`: list of items in message sequence
        - `_d`: string of data used to build message

    :CVariables:
        - `type`: constant MSG_LITERAL (see OpenPGP.constant.messages)
    """
    type = MSG_LITERAL

def create_LiteralMsg(literals):
    """Create a literal message out of a sequence of literal data parameters.

    :Parameters:
        - `literals`: list of dictionaries containing literal data
          parameters (see `Literal keys and values`_)

    :Returns: `OpenPGP.message.LiteralMsg.LiteralMsg` instance

    :Exceptions:
        - `PGPError`: literal message was not created, fix source

    .. _Literal keys and values:

    Literal keys and values:

        - `data`: string of literal data
        - `modified`: *optional* integer timestamp
        - `filename`: *optional* string filename
        - `format`: *optional* 'b' for binary or 't' for text (default
          binary)
    """
    from openpgp.sap.pkt.Packet import create_Packet
    from openpgp.sap.pkt.LiteralData import create_LiteralDataBody
    from openpgp.sap.list import find_literal_msg

    import time

    if isinstance(literals, dict): # to accomodate a single dictionary
        literals = [literals] # yikes

    litpkts = []
    i = 0

    for lit in literals: # assume 'data' is present, allow defaults for rest

        if not lit.has_key('modified'):
            lit['modified'] = int(time.time())

        if not lit.has_key('format'):
            lit['format'] = 'b'

        if not lit.has_key('filename'):
            lit['filename'] = "sap_out_%s" % i

        litbody = create_LiteralDataBody(lit)
        litpkts.append(create_Packet(PKT_LITERAL, litbody._d))

    litmsg = find_literal_msg(litpkts)[0]

    if litmsg:
        return litmsg
    else:
        raise Exception("Failed to create literal messge. Fix source.")

