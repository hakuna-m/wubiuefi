"""Literal Data RFC 2440.5.9

"A Literal Data packet contains the body of a message; data that is not to be
further interpreted."

The term 'message' above does not refer to an OpenPGP message (10.2), but
rather that message which OpenPGP signed, verified, encrypted, etc..
"""
from Packet import Packet
import openpgp.sap.util.strnum as STN

from openpgp.sap.exceptions import *


class LiteralData(Packet):
    __doc__ = """Literal Data Packet
    """ + Packet._ivars

    def __init__(self, *args, **kwords):
        try:
            self.fill(args[0])    
        except IndexError:
            pass

    def fill_body(self, d):
        self.body = LiteralDataBody(d)

class LiteralDataBody:
    """Literal Data

    :IVariables:
        - `format`: string character 'b' or 't' indicating binary or text data
        - `fnlen`: integer number of filename octets
        - `modified`: integer timestamp of file modication time
        - `data`: string of literal data
        - `filename`: string of filename (assuming literal data is meant to be
          saved as a file) or `None`
        - `_d`: string of raw packet body data
    """

    def __init__(self, *args, **kwords):
        try:
            self.fill(args[0])    
        except IndexError:
            pass

    def fill(self, d):
        self._d = d
        self.format = d[0:1]
        self.fnlen = STN.str2int(d[1:2])
        idx = 2

        if 0 < self.fnlen:
            self.filename, idx = STN.strcalc(None, d[idx:idx+self.fnlen], idx)
        else:
            self.filename = None

        self.modified, idx = STN.strcalc(STN.str2int, d[idx:idx+4], idx)
        self.data = d[idx:]

def create_LiteralDataBody(*args, **kwords):
    """Create a LiteralDataBody instance.

    :Parameters:
        - `args`: parameter list, will accept keyword dictionary as
          args[0]
        - `kwords`: keyword parameters

    :Keywords:
        - `data`: string of literal data
        - `modified`: integer timestamp of file modification
        - `format`: character 'b' or 't' indicating binary or text
        - `filename`: optional filename associated with data

    :Returns: `LiteralDataBody` instance

    Use the filename '_CONSOLE' to signal extra-careful handling of
    output.
    """
    try:
        if isinstance(args[0], dict):
            kwords = args[0]
    except IndexError:
        pass

    data = kwords.get('data')

    if not data:
        data = ''

    modified = kwords.setdefault('modified', 0)
    format = kwords.setdefault('format', 'b')
    filename = kwords.setdefault('filename', 'outfile')

    if format not in ['b', 't']:
        raise PGPValueError, "Literal data format must be 'b' or 't'. Received->(%s)" % str(format)

    fnlen_d = STN.int2str(len(filename))

    if 1 < len(fnlen_d):
        raise PGPValueError, "Filename length (%s) exceeded 1 octet capacity." % len(fnlen_d)

    modified_d = STN.prepad(4, STN.int2str(modified))
    d = ''.join([format, fnlen_d, filename, modified_d, data])

    return LiteralDataBody(d)
