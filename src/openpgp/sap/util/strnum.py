"""Number/string conversions

These functions cover common OpenPGP number and string conversions.
"""
# TODO examples for all these are (duh) screwed up in HTML documentation
#      gotta come up with some way to represent byte/hex data nicely
#      without going overboard for the sake of examples
#
# TODO int2quadoct & pentoct2int is the only pair that doesn't look like
#      one. the reason for pentoct2int was to preserve the 5-bytes passed
#      through to strcalc for easy indexing
import struct
import binascii

def strcalc(func, arg, idx):
    """Get value of string->number calculation and incremented index.
    
    :Parameters:
        - `func`: function to use for calculation (must accept `arg`)
        - `arg`: string argument to function `func`
        - `idx`: integer variable to increment by len(`arg`), normally
          just 'idx'

    :Returns: tuple (incremented index, return value from `func`)

    Since many string->number calculations operate on sequential
    chunks of data, it's nice to have a counter incremented by the
    difference of the data's length at hand immediately after the
    calculation. This is basically to provide a nice flow from chunk
    to chunk.

    Example:

        >>> data = '\\xac\\x13\\x0d\\x00\\xff\\xff\\xff\\xff'
        >>> idx, val1 = strcalc(str2int, data[0:3], 0)
        >>> idx, val2 = strcalc(str2int, data[idx:idx+1], idx)
        >>> idx, val3 = strcalc(str2int, data[idx:idx+4], idx)
        >>> val1, val2, val3 # 0xac,0x13,0x0d 0x00 0xff,0xff,0xff,0xff
        11277069, 0, 4294967295
    """
    a = """
    """
    if None == func:
        return arg, idx + len(arg)

    return func(arg), idx + len(arg)

def str2int(s):
    """Convert data string into a number.
    
    :Parameters:
        - `s`: data string

    :Returns: integer representation of string s

    Example: 

        >>> str2int('\\x21q\\xad\\t')
        561097993
        >>> str2int('\\xb0\\x32\\x7a\\xfc')
        2956098300L

    :note: This functions tries to return the number as an int(), but will
        return a long() if an OverflowError is triggered. Don't know if this is
        good behavior..
    """
    l = 0L

    for i in map(ord, s):
        l = (l * 256) + i

    try:
        return int(l)

    except OverflowError:
        return l

# TODO gotta be a better way, and how does this mesh with endian-ness?
def int2str(n):
    """Convert an integer to a string. 

    :Parameters:
        - `n`: integer to convert to string

    :Returns: string 

    This is a simple transformation using the builtin hex() function
    to return the number. 
    
    **Note:** I'm not sure what the relationship between hex()
    representations and endian issues are, these need to be tested.
    
    Example:

        >>> strnums.int2str(34728919023)
        '\\x08\\x16\\x01?\\xef'
    """
    h = hex(n)[2:] # chop off the '0x' 
    if h[-1] in ['l', 'L']:
        h = h[:-1]
    if 1 == len(h) % 2: # odd string, add '0' to beginning
        h = ''.join(['0', h])
    return binascii.unhexlify(h)

# TODO struct doesn't explicitly force this into four octets, does it? 
def int2quadoct(i):
    """ Convert a number to a quadruple octet.

    :Parameters:
        - `i`: number (int or long) note: the number **must** fit into
          four octets

    :Returns: string of four octets representing the number

    Example: 

        >>> int2quadoct(561097993)
        '!q\\xad\\t'
    """
    import sys
    try:
        return struct.pack('>I', i)

    except OverflowError:
        raise ValueError("Number exceeded octet range. Received %s" % i)

    except struct.error:
        raise ValueError("Please use a number. Received %s" % i)
        print sys.exc_info()[:2]



def pentoct2int(s):
    """Convert a "new length" five-octet string to a number.

    :Parameters:
        - `s`: five-octet string ("new length" specifier) note: the
          first octet **must** be 0xff

    :Returns: integer length of body

    This function just chops off the first octet (which must be 0xff)
    and returns the integer value of the following four octets.

    Example::

        >>> TODO

    **Do we really need this?**
    """
    if '\xff' == s[0]:
        return str2int(s[1:5])
    else:
        raise ValueError("First octet must be 0xff.")

# rfc2440 4.2.2.2
def doubleoct2int(s):
    """Convert a double octet into an integer. 
    
    :Parameters:
        - `s`: double octet string

    :Returns: integer number of octets occupied by following body

    See rfc2440 4.2.2.2.

    Example:

        >>> doubleoct2int('\\xf0\\xa3')
        12643
    """
    return ((ord(s[0]) - 192) << 8) + (ord(s[1])) + 192

def hex2int(d):
    """Get the integer value of a string.

    :Parameters:
        - `d`: alphanumeric/hex string

    :Returns: integer

    Hex strings should be preceded with '0x'.
    """
    try:
        return int(d)

    except ValueError:

        if d[:2] in ['0x', '0X']:
            return str2int(hex2str(d[2:]))

        raise

# Is there a better way to do this?
def int2doubleoct(i):
    """Convert an integer to a "new" version double octet length.
    
    :Parameters:
        - `i`: integer of double octet length

    :Returns: string - two octets, double length encoded

    **The integer `i` should be in the range 192 <= `i` <= 16319**. However
    this is not enforced. The reason for the recommendation is to keep double
    octet creation with "normal" OpenPGP bounds. The reason for the lack of
    enforcement is because it is assumed that these bounds will be tested before
    using this function anyway, and anything using this function without such a
    test probably doesn't care about "normal" OpenPGP bounds anyway.

        >>> int2doubleoct(12495)
        '\\xf0\\x0f'
    """
    if 192 <= i <= 447:
        return '\xc0' + chr(i - 192)
    else:
        n = i + (192 * 255)
        return chr(n >> 8) + chr(n & 255)

def int2partial(i):
    """Return the partial length byte for an appropriate length.
    
    :Parameters:
        - `i`: int or long  (i = 2**i for i in range 0 -> 30)

    :Returns: single character representing partial length 

    See RFC 2440 4.2.2.4.    
    """
    partial_map = [(0,1), (1,2), (2,4), (3,8), (4,16), (5,32), (6,64), (7,128),
                   (8,256), (9,512), (10,1024), (11,2048), (12,4096), (13,8192),
                   (14,16384), (15,32768), (16,65536), (17,131072), (18,262144),
                   (19,524288), (20,1048576), (21,2097152), (22,4194304),
                   (23,8388608), (24,16777216), (25,33554432), (26,67108864),
                   (27,134217728), (28,268435456), (29,536870912),
                   (30,1073741824)]
    # check that i is a power of 2
    for power, value in partial_map:

        if value == i:
            return chr(str2int(chr(224 + power)))

    raise ValueError, "Partial length must be in range 2**x for 0<=x<=30."

def partial2int(s):
    """Return the value of a partial length byte. 

    :Parameters:
        - `s`: partial length byte.

    :Returns: integer number of octets of following partial body
        fragment

    Partial lengths are single bytes (x) that express the length of a
    partial body fragment in terms of powers of 2. See rfc2440 4.2.2.4.

    Example:

        >>> TODO
    """
    return 1 << (ord(s) & 31)

# Multi-Precision Integers (MPIs)
def mpilen2int(s):
    """Find the octet length of an MPI integer given an MPI length string.

    :Parameters:
        - `s`: MPI length string, must be two octets long

    :Returns: integer number of octets occupied by the corresponding
        MPI integer

    Example:

        >>> TODO
    """
    if len(s) == 2:
        L = str2int(s)
        return (L + 7) / 8

    else:
        raise ValueError, "MPI length must be a 2 character string."

def sigbits(c):
    """Find out how many bits are used in an octet. 

    :Parameters:
        - `c`: a single character octet

    :Returns: integer (0-8) of significant bits

    This is used for MPI length [header] calculations since MPIs
    specify the number of significant bits in the following MPI
    integer (note the difference between an MPI (length+integer) and 
    *MPI integer* (integer part alone). 

    Since the length of a [very long] integer's string representation 
    in bits is primarily 8*string_length, only the first octet needs
    a precise bit count.

    Example:

        >>> TODO
    """
    i = str2int(c)
    bitmasks = [0x80, 0x40, 0x20, 0x10, 0x08, 0x04, 0x02, 0x01]
    for m in range(len(bitmasks)):
        if i & bitmasks[m] == bitmasks[m]:
            return 8 - m
    return 0

def str2hex(s):
    """Represent a binary string in hex.

    :Parameters:
        - `s`: string of binary data

    :Returns: string representing binary data in hex

    Note: all letters in the hex string are capitalized.
    """
    return binascii.hexlify(s).upper()

def str2pyhex(s):
    """Display copy/pasteable raw byte string.

    This is an untested convenience function which spits out a printable Python
    string which represents a hex-escaped character sequence.
    """
    return ''.join(['\\x' + hex(ord(c))[2:].zfill(2) for c in s])
    return ''.join(['\\x' + hex(ord(c))[2:].zfill(2) for c in s])

def hex2str(s):
    """Reduce a hex string to a binary representation of the same number.

    :Parameters:
        - `s`: string of hex data

    :Returns: string representing binary data in hex
    """
    return binascii.unhexlify(s)

def checksum(s):
    """Apply a simple checksum mod 65536 to a string.

    :Parameters:
        - `s`: string

    :Returns: integer checksum
    """
    csum = 0
    for b in s:
        csum += str2int(b)
    return csum % 65536

# possible to use s.zfill() somehow?
def prepad(length, s=''):
    """Prepend 0x00 octets to a string until it reaches a certain length.

    :Parameters:
        - `length`: integer final length of string

    :Returns: string
    """
    padlen = length - len(s)
    padded = []
    for i in range(padlen):
        padded.append('\x00')
    padded.append(s) 
    return ''.join(padded)
