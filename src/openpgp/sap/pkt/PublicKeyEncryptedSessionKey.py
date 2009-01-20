"""Public key encrypted session key RFC 2440.5.1

A decryption key for a symmetrically encrypted message can be stored
as a "session key" in a public key encrypted session key packet.
Multiple packets of this type allow a single symmetric session key
to be encrypted to many public keys (in a series of public key
encrypted session key packets) so that many public keys can decrypt
the symmetrically encrypted data.
"""
import openpgp.sap.util.strnum as STN

import MPI

from openpgp.code import *

from Packet import Packet


class PublicKeyEncryptedSessionKey(Packet):
    __doc__ = """Public Key Encrypted Session Key Packet
    """ + Packet._ivars

    def __init__(self, *args, **kwords):
        try:
            self.fill(args[0])    
        except IndexError:
            pass

    def fill_body(self, d):
        self.body = PublicKeyEncryptedSessionKeyBody(d)


class PublicKeyEncryptedSessionKeyBody:
    """Public Key Encrypted Session Key

    :IVariables:
        - `version`: integer normally 3, possibly 2
        - `keyid`: string (caps hex) of target public key ID
        - `alg_pubkey`: integer public key algorithm constant
        - `RSA_me_modn`: **RSA `alg` only** MPI instance
        - `ELGAMAL_gk_modp`: **ElGamal `alg` only** MPI instance
        - `ELGAMAL_myk_modp`: **ElGamal `alg` only** MPI instance
    """
    def __init__(self, *args, **kwords):
        try:
            self.fill(args[0])
        except IndexError:
            pass
    
    def fill(self, d):
        self._d = d
        idx = 0
        self.version, idx = STN.strcalc(STN.str2int, d[idx:idx+1], idx)
        self.keyid, idx = STN.strcalc(STN.str2hex, d[idx:idx+8], idx) 
        self.alg_pubkey, idx = STN.strcalc(STN.str2int, d[idx:idx+1], idx)

        if self.alg_pubkey in [ASYM_RSA_EOS, ASYM_RSA_E, ASYM_RSA_S]:
            self.RSA_me_modn, idx = MPI.strcalc_mpi(d[idx:], idx)

        elif ASYM_ELGAMAL_E == self.alg_pubkey:
            self.ELGAMAL_gk_modp, idx = MPI.strcalc_mpi(d[idx:], idx)
            self.ELGAMAL_myk_modp, idx = MPI.strcalc_mpi(d[idx:], idx)

        else:
            raise PGPValueError, "Unsupported public key algorithm. Received alg_pubkey->(%s)" % self.alg_pubkey
 

def create_PublicKeyEncryptedSessionKeyBody(*args, **kwords):
    """
    """
    try:
        kwords = args[0]
    except IndexError:
        pass
    version = '\x03'
    keyid = STN.hex2str(kwords['keyid'])
    algorithm = STN.int2str(kwords['alg'])[0]
    if kwords['alg'] in [ASYM_RSA_EOS, ASYM_RSA_E, ASYM_RSA_S]:
        mpi_d = MPI.create_MPI(kwords['mpis'][0])._d
    elif ASYM_ELGAMAL_E == kwords['alg']:
        a_d = MPI.create_MPI(kwords['mpis'][0])._d
        b_d = MPI.create_MPI(kwords['mpis'][1])._d
        mpi_d = ''.join([a_d, b_d])
    else:
        raise PGPValueError, "Unsupported public key algorithm. Received alg->(%s)" % alg
    _d = ''.join([version, keyid, algorithm, mpi_d])
    return PublicKeyEncryptedSessionKeyBody(_d)

