"""Public key RFC 2440.5.5.1.1

A public key or "certificate" organizes large numbers in the form of
"multi-precision integers" (MPIs) that comprise the non-private
portion of a public key algorithm.

..make a note of the different algorithms and the order in which
their respective keys physically appear in the packet (same goes for
secret keys, in fact it's more important since the order must be known
to decrypt them properly).
"""
import sha
import md5

import openpgp.sap.util.strnum as STN

from openpgp.code import *
from openpgp.sap.exceptions import *

import MPI
from Packet import Packet


class PublicKey(Packet):
    __doc__ = """Public Key Packet
    """ + Packet._ivars

    def __init__(self, *args, **kwords):
        try:
            self.fill(args[0])    
        except IndexError:
            pass

    def fill_body(self, d):
        self.body = PublicKeyBody(d)

class PublicKeyBody:
    _title = """Public Key
    """
    _ivars = """ 
    :IVariables:
        - `version`: integer key packet version (2, 3, or 4)
        - `created`: integer timestamp of creation (seconds since Jan 1, 1970)
        - `alg`: integer public key algorithm (rfc2440 9.1)
        - `fingerprint`: string key fingerprint in hexidecimal (all capitals)
        - `id`: string key id hexidecimal (all capitals)
        - `_mpi_d`: string of all raw MPI data (in order)
        - `_d`: string of raw packet body data
        - `expires`: **version 2 & 3 only** int days until expiration
        - `RSA_n`: **RSA keys only** MPI instance "n", RSA public modulus
        - `RSA_e`: **RSA keys only** MPI instance "e", RSA public encryption exponent
        - `DSA_p`: **DSA keys only** MPI instance "p", DSA prime
        - `DSA_q`: **DSA keys only** MPI instance "q", DSA order
        - `DSA_g`: **DSA keys only** MPI instance "g", DSA group generator
        - `DSA_y`: **DSA keys only** MPI instance "y", DSA public key
        - `ELGAMAL_p`: **ElGamal keys only** MPI instance "p", ElGamal prime
        - `ELGAMAL_g`: **ElGamal keys only** MPI instance "g", ElGamal group generator
        - `ELGAMAL_y`: **ElGamal keys only** MPI instance "y", ElGamal public key
        """
    _notes = """
    Note that the MPI attributes (`RSA_n`, `DSA_p`, etc.) point to an MPI
    *instance(see `packet.MPI.MPI`). Access the MPI *integer value*
    for that object like this: `pubkey.DSA_y.value` or
    `pubkey.ELGAMAL_y.value`.
    """
    __doc__ = ''.join([_title, _ivars, _notes])

    def __init__(self, *args, **kwords):
        try:
            self.fill(args[0])    
        except IndexError:
            pass

    def __set_v4(self, created=0):
        d = []
        d.append('\x04')

        if 0 != created:
            d.append(STN.int2quadoct(created))
        else: # TODO for the time being
            d.append('?\n0\xef')

        return ''.join(d)

    # TODO should self.created be a float (it is in pgpmsg.py)? 
    # note: the reason for all the __version_d, __xxxxx_d business is
    # to be able to reconstruct the /actual data used/ in the key - 
    # as opposed to the /data sent to be used/. theoretically, they 
    # should be the same. data d sent to create the packet may be 
    # longer than necessary but still able to construct a valid key.
    # in any case, the fingerprint generated should use the actual
    # key data no matter what. the question is whether or not to
    # report extraneous data being sent.
    # TODO Maybe I missed something in the docs, since it states plainly that
    # "the two-octet packet length" is used.. but does the packet necessarily
    # have to have two octets (sure, the size range makes sense)? Does this
    # refer to the packet length specified in the packet header? V3 vs. V4?
    # Evidently, the length is just translated to a scalar double octet.
    # TODO speedup? (length = len(..).. cat then len()?). Later. 
    def fill(self, d):
        self._d = d
        idx = 0
        __version_d = d[idx:idx+1]
        self.version, idx = STN.strcalc(STN.str2int, __version_d, idx)

        if self.version in [2, 3, 4]:
            __created_d = d[idx:idx+4] 
            self.created, idx = STN.strcalc(STN.str2int, __created_d, idx)

            if self.version in [2, 3]:
                self.__expires_d = d[idx:idx+2]
                self.expires, idx = STN.strcalc(STN.str2int, self.__expires_d, idx)

            __alg_d = d[idx:idx+1]
            self.alg, idx = STN.strcalc(STN.str2int, __alg_d, idx)

            # resolve MPIs
            if self.alg in [ASYM_RSA_EOS, ASYM_RSA_E, ASYM_RSA_S]:
                self.RSA_n, idx = MPI.strcalc_mpi(d[idx:], idx)
                self.RSA_e, idx = MPI.strcalc_mpi(d[idx:], idx)
                self._mpi_d = self.RSA_n._d + self.RSA_e._d
            elif ASYM_DSA == self.alg:
                self.DSA_p, idx = MPI.strcalc_mpi(d[idx:], idx)
                self.DSA_q, idx = MPI.strcalc_mpi(d[idx:], idx)
                self.DSA_g, idx = MPI.strcalc_mpi(d[idx:], idx)
                self.DSA_y, idx = MPI.strcalc_mpi(d[idx:], idx)
                self._mpi_d = self.DSA_p._d + self.DSA_q._d + self.DSA_g._d + self.DSA_y._d
            elif self.alg in [ASYM_ELGAMAL_E, ASYM_ELGAMAL_EOS]:
                self.ELGAMAL_p, idx = MPI.strcalc_mpi(d[idx:], idx)
                self.ELGAMAL_g, idx = MPI.strcalc_mpi(d[idx:], idx)
                self.ELGAMAL_y, idx = MPI.strcalc_mpi(d[idx:], idx)
                self._mpi_d = self.ELGAMAL_p._d + self.ELGAMAL_g._d + self.ELGAMAL_y._d
            else:
                raise NotImplementedError("Unsupported key algorithm. Received alg->(%s)" % self.alg)

            # set fingerprint
            if self.version in [2, 3]:
                integer_data = self.RSA_n._int_d + self.RSA_e._int_d
                self.fingerprint = md5.new(integer_data).hexdigest().upper()
                # see fingerprint/id notes in doc/NOTES.txt
                self.id = STN.str2hex(self.RSA_n._int_d[-8:])
            elif 4 == self.version:
                f = ['\x99']
                f_data = ''.join([__version_d, __created_d, __alg_d, self._mpi_d])
                length = len(f_data)
                hi = (chr((0xffff & length) >> 8)) # high order packet length
                lo = (chr(0xff & length)) # low order packet length
                f.append(hi + lo) 
                f.append(f_data)
                self.fingerprint = sha.new(''.join(f)).hexdigest().upper()
                # see fingerprint/id notes in doc/NOTES.txt
                self.id = self.fingerprint[-16:]

        else: # unsupported packet version
            raise NotImplementedError("Unsupported key version: %s" % self.version)
        return idx

#    def set_DSA(self, prime, order, grp_gen, pubkey, created=0):
#        d = []
#        d.append(self.__set_v4(created))
#        d.append('\x11') # public key algorithm 17 (DSA)
#
#        for i in [prime, order, grp_gen, pubkey]: # note the order above
#            d.append(MPI.MPI(int=i)._d)
#
#        self.fill(''.join(d))
#
#    def set_RSA(self, m, e):
#        raise NotImplementedError
#
#    def set_ELGAMAL(self, p, g, y):
#        raise NotImplementedError
