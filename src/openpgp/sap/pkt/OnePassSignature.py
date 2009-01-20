"""One-pass signature RFC 2440.5.4

"The One-Pass Signature packet precedes the signed data and contains enough
information to allow the receiver to begin calculating any hashes needed to
verify the signature. It allows the Signature Packet to be placed at the end of
the message, so that the signer can compute the entire signed message in one
pass."
"""
import openpgp.sap.util.strnum as STN

from Packet import Packet
from openpgp.sap.exceptions import *


class OnePassSignature(Packet):
    __doc__ = """One-Pass Signature Packet
    """ + Packet._ivars

    def __init__(self, *args, **kwords):
        try:
            self.fill(args[0])    
        except IndexError:
            pass

    def fill_body(self, d):
        self.body = OnePassSignatureBody(d)


class OnePassSignatureBody:
    """One-Pass Signature

    :IVariables:
        - `version`: integer (should be 3) version of the One Pass Signature
        - `type`: integer signature type
        - `alg_hash`: integer ID of hash algorithm
        - `alg_pubkey`: integer ID of public key algorithm
        - `keyid`: string ID of the signing key
        - `nest`: integer 0 or 1 indicating whether the signature is 
          nested (1) or not (0). A non-nested signature means
          that the following one-pass packet applies to the
          same data as this one and should not be considered
          part of this one-pass message's signed data.
        - `_d`: data string used to create object
    """
    def __init__(self, *args, **kwords):
        try:
            self.fill(args[0])    
        except IndexError:
            pass

    def fill(self, d):
        self._d = d
        self.version = STN.str2int(d[0:1])
        self.type = STN.str2int(d[1:2])
        self.alg_hash = STN.str2int(d[2:3])
        self.alg_pubkey = STN.str2int(d[3:4])
        self.keyid = STN.str2hex(d[4:12])
        self.nest = STN.str2int(d[12:13])


def create_OnePassSignatureBody(*args, **kwords):
    """Create a OnePassSignatureBody instance.

    :Parameters:
        - `args`: ordered parameters
        - `kwords`: parameter keywords
    
    :Returns: `OnePassSignatureBody` instance

    Parameter keywords:
        `sigtype`: integer signature type constant
        `alg_hash`: integer hash algorithm constant
        `alg_pubkey`: integer public key algorithm constant
        `keyid`: string 16-character hex signing key ID
        `nest`: integer nested status
        `version`: integer one-pass version
    """
    if 0 < len(args) and isinstance(args[0], dict):
        kwords = args[0]
    sigtype = kwords.get('sigtype')
    alg_hash = kwords.get('alg_hash')
    alg_pubkey = kwords.get('alg_pubkey')
    keyid = kwords.get('keyid')
    nest = kwords.get('nest')
    version = kwords.setdefault('version', 3)

    errmsg = None
    version_d = STN.int2str(version)
    if 1 < len(version_d):
        errmsg = "One-pass version length (%s octs) exceeded 1 octet limit." % len(version_d)
    sigtype_d = STN.int2str(sigtype)
    if 1 < len(sigtype_d):
        errmsg = "One-pass sigtype length (%s octs) exceeded 1 octet limit." % len(type_d)
    alg_hash_d = STN.int2str(alg_hash)
    if 1 < len(alg_hash_d):
        errmsg = "One-pass hash algorithm length (%s octs) exceeded 1 octet limit." % len(alg_hash_d)
    alg_pubkey_d = STN.int2str(alg_pubkey)
    if 1 < len(alg_pubkey_d):
        errmsg = "One-pass public key algorithm length (%s octs) exceeded 1 octet limit." % len(alg_pubkey_d)
    keyid_d = STN.hex2str(keyid)
    if 8 != len(keyid_d):
        errmsg = "One-pass key ID should be a 16 octet (not %s octs) hex string." % len(keyid)
    nest_d = STN.int2str(nest)
    if 1 < len(nest_d):
        errmsg = "One-pass nest length (%s octs) exceeded 1 octet limit." % len(nest_d)
    if errmsg:
        raise PGPValueError(errmsg)
    d = ''.join([version_d, sigtype_d, alg_hash_d, alg_pubkey_d, keyid_d, nest_d])
    return OnePassSignatureBody(d)

