"""Secret key RFC 2440.5.5.1.3

A secret key packet preserves all the information from its public key
counterpart and also contains the secret (or private) values used to
sign or decrypt messages.

The secret key values (also stored as `MPI` instances) are *normally*
encrypted and must *normally* be decrypted by means of a passphrase
string that has been subjected to a "string to key" operation dictated
by the secret key's `s2k_usg` and `s2k` attributes. For this reason,
the secret key `MPI` instances and `_secmpi_d` are not likely to be
set.  Instead, the `_enc_d` must first be decrypted. It is up to
higher powers to decide whether to use the decrypted data temporarily
or to set an instance's variables (in which case it should set the
variable names for the algorithm specified in the `SecretKeyBody`
docs).

If the secret key is not decrypted, all the instance's attributes will
be set accordingly.

The terms 'secret key' and 'private key' are interchangeable.
"""
# During testing, I encountered an accidental secret key packet
# in a decryption mishap: the (incorrectly) decrypted data of a
# symmetrically-encrypted packet just so happened to match up
# with a packet tag identifying a secret key with X length and
# it just so happened that there was enough decrypted garbage to
# meet the (also bogus) length requirement - AND it just so
# happened that s2k usage was flagged as 0, so all extra data in
# the packet body was conceivably secret key data (at which point
# things came to halt). 
import MPI, S2K

from openpgp.sap.util import strnum as STN
from PublicKey import PublicKey, PublicKeyBody


class SecretKey(PublicKey):
    __doc__ = """Secret Key Packet
    """ + PublicKey._ivars

    def __init__(self, *args, **kwords):
        try:
            self.fill(args[0])    
        except IndexError:
            pass

    def __str__(self):
        return "<SecretKey instance>"

    def fill_body(self, d):
        self.body = SecretKeyBody(d)


class SecretKeyBody(PublicKeyBody):
    _title = """Secret Key
    """
    _ivars = PublicKeyBody._ivars + """
        - `_private_idx`: integer start of (raw) private data in body
        - `s2k_usg`: integer string-to-key usage
        - `s2k`: S2K instance
        - `alg_sym`: integer symmetric key algorithm constant used to
          encrypt secret key material (only available if string-to-key
          usage `s2k_usg` != 0)
        - `iv`: string initialization vector for encrypted key
          material
        - `_enc_d`: string of encrypted MPI data (for v3 keys, this
          string includes the MPI headers as well as the values)
        - `_secmpi_d`: string of decrypted or unencrypted key material
        - `RSA_d`: **RSA keys only** Secret MPI instance, RSA "d"
          decryption key
        - `RSA_p`: **RSA keys only** Secret MPI instance, RSA "p"
          secret prime
        - `RSA_q`: **RSA keys only** Secret MPI instance, RSA "q"
          secret prime
        - `RSA_u`: **RSA keys only** Secret MPI instance, RSA "u"
          multiplicative inverse p mod q
        - `DSA_x`: **DSA keys only** Secret MPI instance, DSA "x"
          secret exponent
        - `ELGAMAL_x`: **ElGamal keys only** Secret MPI instance,
          ElGamal "x" secret exponent
        - `chksum`: integer cleartext secret key checksum value or
          `None` (only available if secret key data is unencrypted)
    """
    _notes = PublicKeyBody._notes
    __doc__ = ''.join([_title, _ivars, _notes])

    def __init__(self, *args, **kwords):
        try:
            self.fill(args[0])    
        except IndexError:
            pass

    # IV length == cipher blocksize
    def fill(self, d):
        idx = PublicKeyBody.fill(self, d)
        self._private_idx = idx # marks start of private data

        self.s2k_usg, idx = STN.strcalc(STN.str2int, d[idx:idx+1], idx)

        if 0 == self.s2k_usg: # unencrypted MPIs
            self.__resolve_secmpi(idx)

        else:

            if self.s2k_usg in [254, 255]: # encrypted MPIs
                self.alg_sym, idx = STN.strcalc(STN.str2int, d[idx:idx+1], idx)
                self.s2k, idx = S2K.strcalc_s2k(d[idx:], idx)

                if 0 == self.alg_sym: # plaintext or unencrypted data
                    self.__resolve_secmpi(idx)
                    return
                elif 1 == self.alg_sym: # IDEA [IDEA]
                    self.iv, idx = STN.strcalc(None, d[idx:idx+8], idx)
                elif 2 == self.alg_sym: # Triple-DES DES-EDE, 168 bit key derived from 192
                    raise NotImplementedError, "3DES"
                elif 3 == self.alg_sym: # CAST5 (128 bit key, as per RFC2144)
                    self.iv, idx = STN.strcalc(None, d[idx:idx+8], idx)
                elif 4 == self.alg_sym: # Blowfish (128 bit key, 16 rounds)
                    self.iv, idx = STN.strcalc(None, d[idx:idx+8], idx)
                elif self.alg_sym in [5, 6]: # Reserved
                    raise NotImplementedError, "Reserved"
                elif 7 == self.alg_sym: # AES with 128-bit key [AES]
                    raise NotImplementedError, "AES 128"
                elif 8 == self.alg_sym: # AES with 192-bit key
                    raise NotImplementedError, "AES 192"
                elif 9 == self.alg_sym: # AES with 256-bit key
                    raise NotImplementedError, "AES 256"
                elif 10 == self.alg_sym: # Twofish with 256-bit key [TWOFISH]
                    raise NotImplementedError, "Twofish"
                elif self.alg_sym in range(100, 111): #100-110 Private/Experimental
                    raise NotImplementedError, "Private/Experimental"
                else:
                    raise ValueError, "Unsupported symmetric encryption algorithm->(%s)" % (str(self.alg_sym))

            else: # s2k usage specifies the symmetric algorithm
                self.alg_sym = self.s2k_usg
                self.iv, idx = STN.strcalc(None, d[idx:idx+8], idx)

            # encrypted data: MPIs + chksum/hash
            if 3 == self.version and self.s2k_usg in [254, 255]:
                if 255 == self.s2k_usg: # checksum is stored in the clear
                    self._enc_d = d[:-2]
                    self.chksum = d[-2:]
                elif 254 == self.s2k_usg: # nothing was specifically mentioned
                    self._enc_d = d[:-20] # about SHA1 in v3/RSA keys, but this
                    self.chksum = d[-20:] # should make sense given the above
            else:
                self._enc_d = d[idx:]

    # prolly turn this into a public method, since it's used 
    # with every encrypted v4 key.
    #  
    def __resolve_secmpi(self, idx):
        d = self._d
        # 1:RSA (Encrypt or Sign), 2:RSA Encrypt-Only, 3:RSA Sign-Only
        if self.alg in [1, 2, 3]:
            self.RSA_d, idx = MPI.strcalc_mpi(d[idx:], idx)
            self.RSA_p, idx = MPI.strcalc_mpi(d[idx:], idx)
            self.RSA_q, idx = MPI.strcalc_mpi(d[idx:], idx)
            self.RSA_u, idx = MPI.strcalc_mpi(d[idx:], idx)
            self._secmpi_d = self.RSA_d._d + self.RSA_p._d + self.RSA_q._d + self.RSA_u._d
        # 17:DSA (Digital Signature Algorithm)
        elif 17 == self.alg:
            self.DSA_x, idx = MPI.strcalc_mpi(d[idx:], idx)
            self._secmpi_d = self.DSA_x._d
        # 16:Elgamal (Encrypt-Only), 20:Elgamal (Encrypt or Sign)
        elif self.alg in [16, 20]:
            self.ELGAMAL_x, idx = MPI.strcalc_mpi(d[idx:], idx)
            self._secmpi_d = self.ELGAMAL_x._d
        else:
            self.err = (ValueError, "Unsupported key algorithm. Received alg->(%s)" % (str(self.alg)))

        if 255 == self.s2k_usg:
            self.chksum, idx = STN.strcalc(STN.str2int, d[idx:idx+2], idx)
        else:
            self.chksum = None
