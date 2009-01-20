"Signature packets RFC 2440.5.2"

import binascii

import openpgp.sap.util.strnum as STN

from Packet import Packet
import MPI

from openpgp.sap.exceptions import *
from openpgp.code import *

class SignatureSubpacketValueError(PGPError): pass

class Signature(Packet):
    __doc__ = """Signature Packet
    """ + Packet._ivars

    def __init__(self, *args, **kwords):
        try:
            self.fill(args[0])    
        except IndexError:
            pass

    def fill_body(self, d):
        self.body = SignatureBody(d)

# TODO Exception for v3 w/ hash_len != 5, right now it's just passed over.
class SignatureBody:
    """Signature Body

    :IVariables:

        - `version`: integer version of signature packet (2, 3, 4)
        - `type`: integer type of signature packet (this attribute
          is generally referred to in hex terms; 0x01, etc.)
        - `keyid`: string (caps hex) ID of signing public key if
          present, or ''
        - `created`: integer signature creation timestamp or 0 if none
          was present
        - `alg_pubkey`: integer public key algorithm version
        - `alg_hash`: integer hash algorithm version
        - `hash_frag`: string of first (high) 2 octets in signed hash
          value 
        - `hashed_data`: string of data used in signature hashes (from
          version to the end of the hashed subpackets)
        - `_d`: string of raw packet body data
        - `hashed_subpkts`: list of `SignatureSubpacket` instances
          (empty for version 3 signatures)
        - `unhashed_subpkts`: list of `SignatureSubpacket` instances
          (empty for version 3 signatures)
        - `DSA_r`: **DSA keys only** MPI instance DSA value "r"
        - `DSA_s`: **DSA keys only** MPI instance DSA value "s"
        - `RSA`: **RSA keys only** MPI instance RSA value m**d
        - `ELGAMAL_a`: **ElGamal keys only** MPI instance ElGamal
          value "a"
        - `ELGAMAL_b`: **ElGamal keys only** MPI instance ElGamal
          value "b"
    """
    def __init__(self, *args, **kwords):
        try:
            self.fill(args[0])
        except IndexError:
            pass

    def fill(self, d):
        self._d = d
        version_d = d[0]
        self.version, idx = STN.strcalc(STN.str2int, d[0], 0)

        if self.version in [2, 3]:
            hash_len, idx = STN.strcalc(STN.str2int, d[idx:idx+1], idx)
            self.type, idx = STN.strcalc(STN.str2int, d[idx:idx+1], idx)
            self.created, idx = STN.strcalc(STN.str2int, d[idx:idx+4], idx)
            self.hashed_data = d[2:idx]
            self.keyid, idx = STN.strcalc(STN.str2hex, d[idx:idx+8], idx)
            self.alg_pubkey, idx = STN.strcalc(STN.str2int, d[idx:idx+1], idx)
            self.alg_hash, idx = STN.strcalc(STN.str2int, d[idx:idx+1], idx)
            self.hashed_subpkts = [] # dummy settings to make searches easier
            self.unhashed_subpkts = [] #

        elif 4 == self.version:
            import struct
            _type_d, idx = STN.strcalc(None, d[idx:idx+1], idx)
            self.type = STN.str2int(_type_d)
            self.alg_pubkey, idx = STN.strcalc(STN.str2int, d[idx:idx+1], idx)
            self.alg_hash, idx = STN.strcalc(STN.str2int, d[idx:idx+1], idx)
            # hashed subpackets
            subpkts_len, idx = STN.strcalc(STN.str2int, d[idx:idx+2], idx)
            self.hashed_subpkts = self.__resolve_subpkts(d[idx:idx+subpkts_len])
            # hashed data & trailer - should '>i' ever return more than 4 chars?
            hashed_data = d[0:idx+subpkts_len]
            bigend = struct.pack('>i', len(hashed_data))[-4:] 
            self.hashed_data = ''.join([hashed_data, version_d, '\xff', bigend])
            idx = idx + subpkts_len
            # unhashed subpackets
            subpkts_len, idx = STN.strcalc(STN.str2int, d[idx:idx+2], idx)
            self.unhashed_subpkts = self.__resolve_subpkts(d[idx:idx+subpkts_len])
            idx = idx + subpkts_len
            # attribute convenience
            self.keyid = self.__set_subpkt_attr(SIGSUB_SIGNERID) or ''
            self.created = self.__set_subpkt_attr(SIGSUB_CREATED) or 0

        else:
            raise PGPValueError("Unsupported signature version. Received->(%s)" % str(self.version))

        self.hash_frag, idx = STN.strcalc(None, d[idx:idx+2], idx)

        if self.alg_pubkey in [ASYM_RSA_S, ASYM_RSA_EOS]:
            self.RSA, idx = MPI.strcalc_mpi(d[idx:], idx)

        elif ASYM_DSA == self.alg_pubkey:
            self.DSA_r, idx = MPI.strcalc_mpi(d[idx:], idx)
            self.DSA_s, idx = MPI.strcalc_mpi(d[idx:], idx)

        elif self.alg_pubkey in [ASYM_ELGAMAL_EOS]:
            self.ELGAMAL_a, idx = MPI.strcalc_mpi(d[idx:], idx)
            self.ELGAMAL_b, idx = MPI.strcalc_mpi(d[idx:], idx)

        else:
            raise PGPValueError("Unsupported public-key algorithm (%d)." % self.alg_pubkey)

    # Convenience for setting subpacket data as signature body attributes,
    # assumes hashed_subpkts and unhashed_subpkts have been set.
    def __set_subpkt_attr(self, subtype):
        for k in self.hashed_subpkts:

            if k.type == subtype:
                return k.value

        for k in self.unhashed_subpkts:

            if k.type == subtype:
                return k.value

        return None

    # Do everything required to extract a field of subpackets.
    def __resolve_subpkts(self, d):
        idx = 0
        subpkt_list = []
        subpkt_data_len = len(d)

        while idx < subpkt_data_len:
            subpkt = SignatureSubpacket(d[idx:])
            subpkt_list.append(subpkt)
            idx += len(subpkt._d)

        return subpkt_list

class SignatureSubpacket:
    """Signature Subpacket

    :IVariables:
        - `type`: integer subpacket type constant
        - `value`: value of subpacket (see source)
        - `critical`: integer 0 or 1 indicating whether the subpacket
          deserves special attention (1) or not (0)
        - `_d`: string data used to build instance

    It's safe to call this class with more data than is required by
    the subpacket.
    """
    def __init__(self, *args, **kwords):
        try:
            self.fill(args[0])
        except IndexError:
            pass

    # TODO should SIGSUB_CREATED, SIGSUB_REVOCABLE, etc. be a float? ..not yet
    def fill(self, d):
        ord_d = ord(d[0])

        if ord_d < 192:
            slice = d[0]
            size = ord_d

        elif 192 <= ord_d < 255:
            slice = d[:2]
            #size = size + STN.doubleoct2int(slice)
            size = STN.doubleoct2int(slice)

        elif 255 == ord_d:
            slice = d[:5]
            #size = size + STN.pentoct2int(slice)
            size = STN.pentoct2int(slice)

        len_slice = len(slice)
        self._d = d[:len_slice+size]
        type_d = d[len_slice:len_slice+1]
        self.type = 127 & ord(type_d)
        self.critical = 128 & ord(type_d)
        value_d = d[len_slice+1:len_slice+size]

        if SIGSUB_SIGNERID == self.type:
            self.value = STN.str2hex(value_d[:8])

        elif self.type in [SIGSUB_CREATED, SIGSUB_EXPIRES, SIGSUB_KEYEXPIRES]:
            self.value = STN.str2int(value_d[:4])            
            self.value = STN.str2int(value_d)            

        elif self.type in [SIGSUB_EXPORTABLE, SIGSUB_REVOCABLE, SIGSUB_PRIMARYUID]:
            self.value = STN.str2int(value_d[:1])

            if self.value not in [0, 1]:
                raise SignatureSubpacketValueError, "Subpacket (# %s) value must be 0 or 1." % (str(subtype))

        elif SIGSUB_TRUST == self.type: # level, amount
            self.value = (STN.str2int(value_d[0]), STN.str2int(value_d[1]))

        elif self.type in [SIGSUB_SYMCODE, SIGSUB_HASHCODE, SIGSUB_COMPCODE, SIGSUB_KEYSERVPREFS, SIGSUB_KEYFLAGS, SIGSUB_FEATURES]:
            self.value = [ord(x) for x in value_d]

        elif SIGSUB_REVOKER == self.type:
            cls = STN.str2int(value_d[0])
            alg = STN.str2int(value_d[1])
            fprint = STN.str2hex(value_d[2:22])
            self.value = (cls, alg, fprint)

        elif SIGSUB_NOTE == self.type:
            flags = [STN.str2int(x) for x in value_d[:4]] # first four flag octs
            name_len = STN.str2int(value_d[4:6])
            val_len = STN.str2int(value_d[6:8])
            nam = value_d[8:8+name_len]
            val = value_d[8+name_len:8+name_len+val_len]
            self.value = (flags, nam, val)

        elif self.type in [SIGSUB_KEYSERV, SIGSUB_POLICYURL, SIGSUB_SIGNERUID, SIGSUB_REGEX]:
            self.value = value_d

        elif SIGSUB_REVOCREASON == self.type: # code, reason
            self.value = (STN.str2int(value_d[0]), value_d[1:])

        elif SIGSUB_SIGTARGET == self.type:
            raise NotImplementedError, "SIGTARGET not supported"

        else: # the subpacket has an unknown type, so just pack the data in
            self.value = value_d

def create_SignatureBody(*args, **kwords):
    """Assemble signature information into a SignatureBody instance.

    :Parameters:
        - `args`: parameter list
        - `kwords`: keyword parameter dictionary 
    
    :Keywords:
        - `sigtype`: integer signature type constant (see
          `OpenPGP.constant.signatures`)
        - `alg_pubkey`: integer signature algorithm (see
          `OpenPGP.constant.algorithms`)
        - `alg_hash`: integer signature algorithm (see
          `OpenPGP.constant.algorithms`)
        - `signature`: algorithm-dependent signature MPIs - DSA
          MPI tuple (``DSA_r``, ``DSA_s``), single RSA MPI ``RSA``, or
          ElGamal MPI tuple (``ELGAMAL_a``, ``ELGAMAL_b``) (see
          `DSA signature tuple`_, `RSA signature value`_, and `ElGamal
          signature tuple`_)
        - `hash_frag`: 2 octet string of signed hash fragment
        - `hashed_subpkts`: list of `SignatureSubpacket` instances
          included in the hashed (protected) portion of the signature
        - `unhashed_subpkts`: list of `SignatureSubpacket` instances
          included in the unhashed (unprotected) portion of the signature
        - `created`: integer timestamp of signature creation, **v3 only**
        - `keyid`: string ID of signing key **v3 only**

    :Returns: `SignatureBody` instance

    .. _DSA signature tuple:
    
    DSA signature tuple (``DSA_r``, ``DSA_s``):

        - `DSA_r`: `OpenPGP.packet.MPI` instance
        - `DSA_s`: `OpenPGP.packet.MPI` instance

    .. _RSA signature value:

    RSA signature value ``RSA``:

        - ``RSA``: `OpenPGP.packet.MPI` instance

    .. _ElGamal signature tuple:

    ElGamal signature tuple (``ELGAMAL_a``, ``ELGAMAL_b``):

        - ``ELGAMAL_a``: `OpenPGP.packet.MPI` instance
        - ``ELGAMAL_b``: `OpenPGP.packet.MPI` instance

    :note: This function only assembles the provided information into
        a signature packet, it does not reconcile anything - namely,
        the values of the MPIs with the signed data and hash fragment.
    
    :note: All keyword parameters can be specified in a dictionary,
        sent as a single parameter (args[0]).
    """
    try:
        kwords = args[0]
    except IndexError:
        pass

    version = kwords['version']
    sigtype = kwords['sigtype']
    alg_pubkey = kwords['alg_pubkey']
    alg_hash = kwords['alg_hash']
    signature = kwords['signature']
    hash_frag = kwords['hash_frag']
    hashed_subpkts = kwords.get('hashed_subpkts') # optional
    unhashed_subpkts = kwords.get('unhashed_subpkts') # optional

    _d = []
    _d.append(STN.int2str(version)[0])
                                                      ################# version
    if 3 == version:                                  #################       3
        _d.append('\x05')                             # hash length (required)
        _d.append(STN.int2str(sigtype)[0])            # signature type
        _d.append(STN.int2str(kwords['created'])[:4]) # creation timestamp
        _d.append(STN.hex2str(kwords['keyid'])[:8])   # signing key ID
        _d.append(STN.int2str(alg_pubkey)[0])         # public key algorithm
        _d.append(STN.int2str(alg_hash)[0])           # hash algorithm

    elif 4 == version:                                #################       4
        _d.append(STN.int2str(sigtype)[0])            # signature type
        _d.append(STN.int2str(alg_pubkey)[0])         # public key algorithm
        _d.append(STN.int2str(alg_hash)[0])           # hash algorithm

        if hashed_subpkts:                            # hashed subpackets
            _d.append(__cat_subpkt_block(hashed_subpkts))
        else:
            _d.append('\x00\x00')

        if unhashed_subpkts:                          # unhashed subpackets
            _d.append(__cat_subpkt_block(unhashed_subpkts))
        else:
            _d.append('\x00\x00')

    _d.append(hash_frag[:2])                          # hash fragment

    if alg_pubkey in [ASYM_RSA_S, ASYM_RSA_EOS]:      # RSA MPI
        _d.append(''.join([x._d for x in signature]))

    elif alg_pubkey in [ASYM_DSA, ASYM_ELGAMAL_EOS]:  # DSA MPIs
        _d.append(''.join([x._d for x in signature]))

    else:
        raise PGPValueError, "Unsupported signature algorithm %s." % algorithm

    return SignatureBody(''.join(_d))

# 'subpkts' is a list of subpackets.
def __cat_subpkt_block(subpkts):
    subpkt_d = ''.join([x._d for x in subpkts])
    subpkt_d_len = STN.int2str(len(subpkt_d))

    if 2 >= len(subpkt_d_len):
        return STN.prepad(2, subpkt_d_len) + subpkt_d
    else:
        raise PGPValueError, "Subpacket block length (%s) is unacceptable." % len(subpkt_d_len)

def create_SignatureSubpacket(type, value):
    """Create a SignatureSubpacket instance.

    :Parameters:
        - `type`: integer signature subpacket type constant
          (see `OpenPGP.constant.signatures`)
        - `value`: variable value depending on `type` (see
          `Subpacket types and values`_)

    :Returns: `SignatureSubpacket` instance

    .. _Subpacket types and values:

    Subpacket types and values:
 
        - ``SIGSUB_SIGNERID``: hex key ID string (16 octets)
        - ``SIGSUB_CREATED``: integer timestamp of signature
          creation(must resolve to 4 or less octets, restricting
          value to less than 4294967296)
        - ``SIGSUB_EXPIRES``, ``SIGSUB_KEYEXPIRES``: integer time past
          creation of signature or key expiration (must resolve to 4
          or less octets, restricting value to less than 4294967296)
        - ``SIGSUB_EXPORTABLE``, `SIGSUB_REVOCABLE``,
          ``SIGSUB_PRIMARYUID``: integer 1 or 0 for True or False
        - ``SIGSUB_TRUST``: tuple(integer level, integer amount)
        - ``SIGSUB_SYMCODE``, ``SIGSUB_HASHALGS``, ``SIGSUB_COMPALGS``,
          ``SIGSUB_KEYSERVPREFS``, ``SIGSUB_KEYFLAGS``,
          ``SIGSUB_FEATURES``: list of integers, see rfc2440 for
          specifics
        - ``SIGSUB_REVOKER``: tuple(integer class, integer algorithm,
          string 40 octet caps hex SHA1 fingerprint hash string
        - ``SIGSUB_NOTATION``: tuple([list of 4 flags], string name,
          string value) see rfc2440 for specifics, list of flags may
          be replaced with None for basic text notation
          [0x80, 0x0, 0x0, 0x0]
        - ``SIGSUB_KEYSERV``, ``SIGSUB_POLICYURL``,
          ``SIGSUB_SIGNERUID``, ``SIGSUB_REGEX``: string see rfc2440
          for specifics
        - ``SIGSUB_REVOCREASON``: tuple (integer code, string reason)
        - ``SIGSUB_SIGTARGET``: Not Implemented
    """
    from Packet import create_NewLength

    # set value_d
    if SIGSUB_SIGNERID == type:
        value_d = STN.hex2str(value)

        if len(value_d) != 8:
            raise SignatureSubpacketValueError("Length of subpacket key id (%s) is not 8 octets." % len(value))

    elif type in [SIGSUB_CREATED, SIGSUB_EXPIRES, SIGSUB_KEYEXPIRES]:
        value_d = STN.int2str(value)

        while len(value_d) < 4:
            value_d = '\x00' + value_d

        if len(value_d) > 4:
            raise SignatureSubpacketValueError("Length of subpacket time (%s) exceeds 4 octet limit." % len(value_d))

    elif type in [SIGSUB_EXPORTABLE, SIGSUB_REVOCABLE, SIGSUB_PRIMARYUID]:

        if value not in [0, 1]:
            raise SignatureSubpacketValueError("Subpacket (# %s) value must be 0 or 1." % (str(subtype)))
        else:
            value_d = STN.int2str(value)

    elif SIGSUB_TRUST == type: # level, amount
        value_d = STN.int2str(value[0]) + STN.int2str(value[1])

    elif type in [SIGSUB_SYMCODE, SIGSUB_HASHCODE, SIGSUB_COMPCODE,
                  SIGSUB_KEYSERVPREFS, SIGSUB_KEYFLAGS, SIGSUB_FEATURES]:
        value_d = ''.join([STN.int2str(x) for x in value])

    elif SIGSUB_REVOKER == type: #
        value_d = STN.int2str(value[0]) + STN.int2str(value[1]) + STN.hex2str(value[2])

    elif SIGSUB_NOTE == type: # [f1, f2, f3, f4], name, value
        # TODO need check for oversized flags
        if value[0]: # allow for basic text notations w/ "not value[0]"
            flag_d = ''.join([STN.int2str(x) for x in value[0]]) # first four flag octs
        else:
            flag_d = '\x80\x00\x00\x00'

        nam, val = value[1], value[2]
        namlen, vallen = STN.int2str(len(nam)), STN.int2str(len(val))

        if len(namlen) == 1:
            namlen = '\x00' + namlen
        elif len(namlen) > 2:
            raise SignatureSubpacketValueError("Length (%s) of subpacket notation 'name' exceeds 2 octet limit." % len(nam))

        if len(vallen) == 1:
            vallen = '\x00' + vallen
        elif len(vallen) > 2:
            raise SignatureSubpacketValueError("Length (%s) of subpacket notation 'value' exceeds 2 octet limit." % len(val))

        value_d = flag_d + namlen + vallen + nam + val

    elif type in [SIGSUB_KEYSERV, SIGSUB_POLICYURL, SIGSUB_SIGNERUID, SIGSUB_REGEX]:
        value_d = value

    elif SIGSUB_REVOCREASON == type: # code, reason
        value_d = STN.int2str(value[0]) + value[1]

    elif SIGSUB_SIGTARGET == type:
        raise NotImplementedError, "SIGTARGET not supported"

    else: # subpacket is an unknown type, so just pack the data in
        value_d = value

    # resolve length string
    len_d = len(value_d) + 1 # + 1 octet type
    slice = create_NewLength(len_d)._d

    # set type string (character)
    type_d = STN.int2str(type)[0]
    subpkt_d = ''.join([slice, type_d, value_d])

    return SignatureSubpacket(subpkt_d)
