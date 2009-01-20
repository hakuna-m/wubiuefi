"""Multi-precision integers RFC 2440.3.2

Multi-precision integers are big-endian integers prefixed with a
length specifier and are used to represent very long numbers.

Note the difference between the MPI attributes `size` and `length`.
The `length` is the `MPI` header length, determined by the bit length,
which gives the "number of octets occupied by the integer portion of
the MPI." The `size` is the size of the entire `MPI` (header and
integer). Effectively, this just means that:

    - size == length + 2  
    - int_data == data[2:]
    - value ~ int_data (int_data converted to a numeric value)

The MPI does not know in advance how many octets comprise it, therefore
it must be passed a string at least long enough to fulfill its needs.
This is in contrast to bona fide packet body classes which expect the
exact string (no more) to create instances.
"""
import openpgp.sap.util.strnum as STN

from openpgp.sap.exceptions import *

# The use of 'length' and 'size' attributes try to preserve the naming
# conventions used for Length, Type, and Packet objects, where 'size'
# refers to the size of the entire object in question (here, the
# entire MPI object) and 'length' specifies the length of "internal" 
# components.
# TODO leftover ugliness in check()
class MPI:
    """Multi-Precision Integer

    :IVariables:
        - `length`: integer length (octet count) of the MPI integer
          string (not including the MPI length header)
        - `bit_length`: integer (number count) of the bits used in MPI
          integer
        - `value`: MPI integer value
        - `size`: integer size of the entire MPI (2 octet length
          specifier + integer)
        - `_d`: string used to build the MPI
        - `_int_d`: MPI integer data string
    """
    def __init__(self, *args, **kwords):
        if kwords.has_key('int'):
            self.__create(kwords['int'])
        else:
            try:
                self.fill(args[0])    
            except IndexError:
                pass

    # TODO no sleep ~ questionable tactics
    def fill(self, d):
        import struct
        idx = 0
        self._length_d, idx = STN.strcalc(None, d[idx:idx+2], idx)

        self.bit_length = STN.str2int(self._length_d)
        self.length = STN.mpilen2int(self._length_d)

        self._d = d[0:2+self.length]
        self._int_d = d[idx:idx+self.length]
        self.size = len(self._d) # explicitly..

        i = struct.unpack('>'+str(len(self._int_d))+'s', self._int_d)[0]
        self.value = STN.str2int(i) 

        if self.check():
            pass
        else:
            raise self.err[0], self.err[1]

    def check(self):
        int_len = len(self._int_d)

        if int_len == self.length:

            if self.size == int_len + 2:
                return 1

            else:
                m = "MPI's specified size (%s) does not match actual size (%s)." % (self.size, int_len + 2)

        else:
            m = "MPI length (%s) does not match header (%s)." % (int_len, self.length)

        raise PGPFormatError(m)

def create_MPI(i):
    """Create an MPI out of an integer.

    :Parameters:
        - `i`: integer

    :Returns: `MPI` instance
    """
    d = []
    i_d = STN.int2str(i)
    i_length = len(i_d)
    bit_count = STN.sigbits(i_d[0]) + (8 * (i_length - 1))
    i_length_str = STN.int2str(bit_count)

    if 2 < len(i_length_str):
        raise ValueError, "int is larger than two octets can specify - int occupies %s octets" % str(i_length)

    elif 1 == len(i_length_str):
        i_length_str = ''.join(['\x00', i_length_str])

    d.append(i_length_str)
    d.append(i_d)

    return MPI(''.join(d))

# TODO Slice-copying large chunks of the data string (taking place
# right before this function is called) could be replaced by
# piecing things together with the complete data string, using the
# index along the way, then only slicing that which was used for the
# instance.
def strcalc_mpi(d, idx):
    """Return a MPI instance and an incremented index.

    :Parameters:
        - `d`: string of data starting with the first octet of the MPI
        - `idx`: integer position in external data string

    :Returns:
        - tuple (MPI_instance, new_index):
            - `MPI_instance`: MPI instance created using string `d`
            - `new_index`: integer original `idx` parameter
              incremented by the octet length of the S2K instance

    To eliminate look-ahead code when parsing MPI data, this function
    automates the creation of the MPI instance and the incrementing of
    the index position in the data string `d`.

    :Note: `S2K` instances work the same way. `strcalc_mpi()`
        basically saves "look ahead" code from showing up wherever `MPI`
        instances are looked for. It might feel safer to do the look
        aheads rather than trust this code with the whole of the data
        used to build the MPI instance, but boy would it make the calling
        code look ugly.
    """
    mpi = MPI(d)
    return mpi, idx + mpi.size
