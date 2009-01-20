"""String-to-key specifiers RFC 2440.3.7

Symmetrically encrypted data in OpenPGP is not actually encrypted
with the passphrase the user gives. Instead it is often hashed,
stretched, multiplied, and mutilated to generate an encryption key.
String-to-key specifiers specify what is needed to turn a
user-supplied passphrase into this encryption key. 

The `S2K` class discovers how many octets comprise it as it constructs
an instance. Therefore it must be passed a string at least long enough
to fulfill its needs. This is in contrast to bona fide packet body
classes which expect the exact string (no more) to create instances.
See the documentation for `strcalc_s2k()` for clarification.
"""
from openpgp.code import *

import openpgp.sap.util.strnum as STN

class S2K:
    """String to Key Specifier

    :IVariables:
        - `type`: integer S2K type
        - `alg_hash`: integer hash algorithm type
        - `salt`: string 8 octets of salt prepended to passphrase
        - `count`: integer octets hashed into key
        - `count_code`: integer count code (pre-shift)
        - `size`: integer octet length of the S2K instance
        - `_d`: string used to build the S2K instance
    """
    def __init__(self, *args, **kwords):
        try:
            self.fill(args[0])    
        except IndexError:
            pass

    def fill(self, d):
        """
        """
        idx = 0
        self.type, idx = STN.strcalc(STN.str2int, d[idx:idx+1], idx)
        self.alg_hash, idx = STN.strcalc(STN.str2int, d[idx:idx+1], idx)

        if self.type in [0x01, 0x03]:
            self.salt, idx = STN.strcalc(None, d[idx:idx+8], idx)

            if 0x03 == self.type:
                c, idx = STN.strcalc(STN.str2int, d[idx:idx+1], idx)
                self.count_code = c
                self.count = (16 + (c & 15)) << ((c >> 4) + 6)

        self._d = d[0:idx]
        #hexify = lambda s: ''.join(['\\x%s' % hex(ord(c))[2:].zfill(2) for c in s])
        #print hexify(self._d)
        self.size = len(self._d)

# No default salt since it is a crypto-thing.
def create_S2K(*args, **kwords):
    """Create an S2K (string-to-key specifier) instance.
    
    :Parameters:
        - `args`: parameter list
        - `kwords`: keyword parameter dictionary 

    :Keywords:
        - `alg_hash`: integer hash algorithm constant (default SHA1)
        - `salt`: string 8 octet salt **Required for types 1 & 3**
        - `type`: *optional* integer S2K type (default 3)
        - `count`: *optional* integer count code (< 128) used for type 3
          only (default 99)

    :Returns: `S2K` instance

    :note: All keyword parameters can be specified in a dictionary,
        sent as a single parameter (args[0]).
    """
    try:
        kwords = args[0]
    except IndexError:
        pass

    if 'type' in kwords:
        s2ktype = kwords['type']
    else:
        s2ktype = 3
    if 'alg_hash' in kwords:
        alg_hash = kwords['alg_hash']
    else:
        alg_hash = HASH_SHA1

    d = []
    if 0 == s2ktype:
        d.append('\x00')
        d.append(STN.int2str(alg_hash)[0])
    elif 1 == s2ktype:
        d.append('\x01')
        d.append(STN.int2str(alg_hash)[0])
        d.append(kwords['salt'][:8])
    elif 3 == s2ktype:
        d.append('\x03')
        d.append(STN.int2str(alg_hash)[0])
        d.append(kwords['salt'][:8])
        if 'count' in kwords:
            if 0 < kwords['count'] < 128:
                d.append(STN.int2str(kwords['count']))
            else:
                raise PGPValueError, "S2K count value %s out of range." % kwords['count']
        else:
            d.append('\x63') # 99
    return S2K(''.join(d))

# TODO Slice-copying large chunks of the data string (taking place
# right before this function is called) could be replaced by
# piecing things together with the complete data string, using the
# index along the way, then only slicing that which was used for the
# instance.
def strcalc_s2k(d, idx):
    """Return a S2K instance and an incremented index.

    :Parameters:
        - `d`: string of data starting with the first octet of the
          string-to-key specifier
        - `idx`: integer position in external data string

    :Returns: tuple (S2K_instance, new_index) (see `S2K tuple`_)

    .. _S2K tuple:

    S2K tuple:

        - `S2K_instance`: S2K instance created using string `d`
        - `new_index`: integer original `idx` parameter
          incremented by the octet length of the S2K instance

    To eliminate look-ahead code when parsing string-to-key data,
    this function automates the creation of the S2K instance and
    the incrementing of the index position in the data string `d`.

    :Note: `MPI` instances work the same way. `strcalc_s2k()`
        basically saves "look ahead" code from showing up wherever `S2K`
        instances are looked for. It might feel safer to do the look
        aheads rather than trust this code with the whole of the data
        used to build the S2K instance, but boy would it make the calling
        code look ugly.
    """
    s2k = S2K(d)
    return s2k, idx + s2k.size
