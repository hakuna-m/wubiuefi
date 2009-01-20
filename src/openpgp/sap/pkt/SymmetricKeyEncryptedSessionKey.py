"""Symmetric key encrypted session key RFC 2440.5.3

A decryption key for a symmetrically encrypted message can be stored
as a "session key" in a symmetric key encrypted session key packet.
Multiple packets of this type allow a session key for a single
symmetrically encrypted message to be accessed by multiple
passphrases, since each symmetric key encrypted session key can use
a different passphrase to encrypt the final decryption key.

It is possible that the symmetric key encrypted session key does not
in fact hold a session key (`enc_key`) at all. In this case, the
version (`version`), symmetric algorithm (`alg`), and string-to-key
specifier (`s2k`) are used to create the session key for the upcoming
symmetrically encrypted message directly.

:Note: Remember to work with this packet as a "whole packet" instead
    of in header/body parts. This is because the packet body (which
    is normally completely independent of header information) in this
    case depends on the packet length. Therefore the information
    reported as part of the body (that is whether or not it actually
    has an encrypted session key in `enc_key`) can be resolved only
    if the total packet is created.
"""
import openpgp.sap.util.strnum as STN

import S2K

from Packet import Packet

# This is the first class I've encountered where the packet body
# needs information from the packet header: if there are packets left
# over after the S2K information (according to the pkt.length.size),
# they make up (implicitly) the encrypted session key.
#
# The alternative would be to pass length information from the packet
# class to the body, which disturbs the uniformity of fill_body(???).
#
# We'll see what it looks like when packets are actually being built.
class SymmetricKeyEncryptedSessionKey(Packet):
    __doc__ = """Symmetric Key Encrypted Session Key Packet
    """ + Packet._ivars + """
        - `_enc_d`: string encrypted algorithm/session key data
        - `has_key`: True or False, depending on whether or not the
          session key exists
    """

    def __init__(self, *args, **kwords):
        try:
            self.fill(args[0])    
        except IndexError:
            pass

    def fill_body(self, d):
        self.body = SymmetricKeyEncryptedSessionKeyBody(d)
        # see if we have an encrypted session key
        bodylen = len(self.body._d)
        if self.length.size > bodylen:
            self.body._enc_d = d[bodylen:]
            self.body._d = ''.join([self.body._d, self.body._enc_d])
            self.body.has_key = True
        else:
            self.body.has_key = False

class SymmetricKeyEncryptedSessionKeyBody:
    """Symmetric Key Encrypted Session Key

    :IVariables:
        - `version`: integer symmetric session key packet version
        - `alg`: integer describing the symmetric algorithm used
        - `s2k`: S2K instance
        - `enc_key`: optional string (the encrypted session key)
          or `None` - remember to check for it's existence
        - `_d`: string of data used to build the body
    """
    def __init__(self, *args, **kwords):
        try:
            self.fill(args[0])    
        except IndexError:
            pass

    # TODO See if this look-back silliness can be rid of using a fixed
    # `d` during packet creation.
    def fill(self, d):
        """
        """
        self._d = d
        idx = 0
        self.version, idx = STN.strcalc(STN.str2int, d[idx:idx+1], idx)
        self.alg, idx = STN.strcalc(STN.str2int, d[idx:idx+1], idx)
        self.s2k, idx = S2K.strcalc_s2k(d[idx:], idx)
        # now we can't see packet size information from here, so the
        # SymmetricKeyEncryptedSessionKey class takes over in
        # fill_body to see if we have an encrypted session key

def create_SymmetricKeyEncryptedSessionKeyBody(*args, **kwords):
    """Create a SymmetricKeyEncryptedSessionKeyBody instance.

    :Parameters:
        - `args`: parameter list
        - `kwords`: keyword parameter list

    Keyword options:
        - `alg`: integer symmetric key algorithm
        - `s2k`: `OpenPGP.packet.S2K` instance
        - `version`: optional integer version number (default 4)

    :Returns: `SymmetricKeyEncryptedSessionKeyBody` instance
    """
    try:
        kwords = args[0]
    except IndexError:
        pass

    if 'version' in kwords:
        if 0 < version < 128:
            version = kwords['version']
        else:
            raise PGPValueError, "Symmetric session key version %s is out of range." % version
    else:
        version = 4

    d = []
    d.append(STN.int2str(version)[0])
    d.append(STN.int2str(kwords['alg'])[0])
    d.append(kwords['s2k']._d)
    return SymmetricKeyEncryptedSessionKeyBody(''.join(d))
