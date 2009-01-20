"Basic packet support RFC 2440.4"

import types
import StringIO

from openpgp.sap.util import strnum as STN
from openpgp.sap.exceptions import *

pktclasses = {0:"Reserved",
              1:"PublicKeyEncryptedSessionKey",
              2:"Signature",
              3:"SymmetricKeyEncryptedSessionKey",
              4:"OnePassSignature",
              5:"SecretKey",
              6:"PublicKey",
              7:"SecretSubkey",
              8:"CompressedData",
              9:"SymmetricallyEncryptedData",
              10:"Marker",
              11:"LiteralData",
              12:"Trust",
              13:"UserID",
              14:"PublicSubkey",
              17:"UserAttribute",
              18:"SymmetricallyEncryptedIntegrityProtectedData",
              19:"ModificationDetectionCode",
              60:"TestPGP"}

def pktclass(i):
    """Return an OpenPGP packet class given packet type code.

    :Parameters:
        - `i`: integer OpenPGP packet type code

    :Returns: `OpenPGP.packet.Packet` subclass

    See rfc2440 4.3.

    Example:

        >>> userid = pktclass(13)()
        >>> userid.value = "Some Name <somename@email.com>"
    """
    if i in pktclasses:
        cn = pktclasses[i]
        mod = __import__("openpgp.sap.pkt.%s" % cn, None, None, [cn])
        pktclass = mod.__dict__[cn]
        return pktclass

    else:
        from Unknown import Unknown
        return Unknown

class Tag:
    """OpenPGP Packet Tag Class

    :IVariables:
        - `version`: 0 or 1, corresponding to "old" or "new"
        - `type`: integers 1 -> 63, corresponding to packet body
          type code (see `OpenPGP.constant.packets`)
        - `length_type`: (0,1,2,3) set only if packet tag is "old"
        - `_d`: data string used to create `Tag` instance
    """

    def __init__(self, *args, **kwords):
        try:
            self.fill(args[0])
        except IndexError:
            pass

    def fill(self, d):
        """tag.fill(d)

        Set the packet.Tag object's data, filling its attributes.
        Tag data (d) must be a single character that matches the
        OpenPGP packet tag standard (see rfc2004 4.2).

        :Parameters:
            - `d`: character (StringType, length == 1)

        :Returns: Nothing

        Example:

            >>> tag = packet.Tag()
            >>> d=chr(0x99)
            >>> tag.fill(d)
            >>> tag.version, tag.type, tag.length_type
            0, 3, 1
        """
        if 1 == len(d) and 128 == (ord(d) & 128): # length==1, left bit==1
            ord_d = ord(d)
            v = ord_d & 64 # tag version

            if 0 == v :
                self.version = 0
                self.type = (ord_d & 60) >> 2
                self.length_type = ord_d & 3

            elif 64 == v :
                self.version = 1
                self.type = ord_d & 63

            else:
                raise PGPError, "Fix me." # just to be sure

            self._d = d

        else: # did not pass test, but was at least a valid type
            raise PGPFormatError("Invalid tag data. Check len(d)=1, (ord(d) & 128)==128. Received->(%s)" % d)


class OldLength:
    """OpenPGP "Old Length" Class

    :IVariables:
        - `size`: integer number of octets occupied by packet body
        - `_d`: data string used to create `OldLength` instance
    """

    def __init__(self, *args, **kwords):
        try:
            self.fill(args[0])
        except IndexError:
            pass

    def fill(self, d):
        """oldlength.fill(d)

        Set the OldLength object's data, filling its attributes.
        Tag data (d) must be either 1, 2, or 4 octets containing
        the length (integer count) of the packet body
        (see rfc2004 4.2.1).

        :Parameters:
            - `d`: character (StringType, length == 1)

        :Returns: Nothing

        Example:

            >>> oldlength_octets = [0x88, 0x88]
            >>> oldlength_data_string = ''.join(map(chr, oldlength_octets))
            >>> oldlength = OldLength()
            >>> oldlength.fill(oldlength_data_string)
            >>> oldlength.size
            34952
        """
        if len(d) in [1, 2, 4]:
            self._d, self.size = d, STN.str2int(d)
        elif 0 == len(d):
            self._d, self.size = '', "UNDEFINED"
        else:
            raise PGPFormatError, "Old packet length data must come in 0, 1, 2, or 4 octets. Received->(%s octets)." % (str(len(d)))


class NewLength:
    """OpenPGP "New Length" Class

    :IVariables:
        - `size`: integer number of octets occupied by packet body
        - `_d`: data string used to create `NewLength` instance
    """

    def __init__(self, *args, **kwords):
        try:
            self.fill(args[0])
        except IndexError:
            pass

    def fill(self, d):
        """newlength.fill(d)

        Set the NewLength object's data, filling its attributes.
        Tag data (d) must be either 1, 2, or 5 octets containing
        the length (integer count) of the packet body
        (see rfc2004 4.2.2).

        :Parameters:
            - `d`: character (StringType, length == 1)

        :Returns: Nothing

        Example:

            >>> newlength_octets = [0xff, 0x92, 0xdf, 0x7c, 0xbb]
            >>> newlength_data_string = ''.join(map(chr, length_octet_list))
            >>> newlength = NewLength()
            >>> newlength.fill(newlength_data_string)
            >>> newlength.size
            2464119995
        """
        self._d = d
        # use length_list to check for illegal final partials
        size, length_list = self.get_size(d)
        # catch last partial
        if 224 <= self.get_size(length_list[-1])[0] <= 254:
            raise PGPFormatError, "Last length specifier must not be a partial length."
        else:
            self.size = size

    def get_size(self, d):
        """Get total octet count of a body specified by new length header octs.

        :Parameters:
            - `d`: string of "new" length octets, note that this string
              cannot be made up of arbitrary bytes, and must conform
              to the rules of new length values (rfc2440 4.2.2)

        :Returns: XXXXXXX TODO

        Example:

            >>> newlength_octets = [0xff, 0x92, 0xdf, 0x7c, 0xbb]
            >>> newlength_data_string = ''.join(map(chr, length_octet_list))
            >>> newlength = NewLength()
            >>> newlength.get_size(newlength_data_string)
            2464119995
        """
        idx = size = 0
        # the length_list is to keep track of data (d) actually used -
        # it's possible that a string of partials could terminate with
        # leftover octets
        length_list = []
        if 0 < len(d):
            for L in [(x, ord(x)) for x in d]:
                if L[1] < 192:
                    size = size + L[1]
                    length_list.append(L[0])
                    break
                elif 192 <= L[1] <= 223:
                    slice = d[idx:idx+2]
                    s = STN.doubleoct2int(slice)
                    if 192 <= s <= 8383: # ?? dunno about this restriction
                        size = size + s
                        length_list.append(slice)
                    else:
                        raise PGPFormatError("New double octet lengths are confined to the range 192 <= x <= 8383. Received: data->(%s) length->(%s)" % (d, size))
                    break
                elif 255 == L[1]:
                    slice = d[idx:idx+5]
                    size = size + STN.pentoct2int(slice)
                    length_list.append(slice)
                    break
                elif 224 <= L[1] <= 254: # partials
                    slice = d[idx:idx+1]
                    size = size + STN.partial2int(slice)
                    length_list.append(slice)
                    idx = idx + 1
        else:
            raise PGPFormatError("Length must have at least one octet. Received len(d) == 0.")

        return size, length_list


class Packet:
    _ivars = """
    :IVariables:
        - `tag`: packet tag object (see `OpenPGP.packet.Tag`)
        - `length`: an instance of either OldLength or NewLength
          (see documentation for `OpenPGP.packet.OldLength` and
          `OpenPGP.packet.NewLength`)
        - `body`: packet type instance  (see documentation for "Supported
          Packet Types" listed in packet module documentation)
        - `size`: integer octet count of entire packet
    """
    __doc__ = """OpenPGP Packet Class
    """ + _ivars

    def __init__(self, *args, **kwords):
        try:
            self.fill(args[0])
        except IndexError:
            pass

    def rawstr(self):
        try:
            return ''.join([self.tag._d, self.length._d, self.body._d])
        except:
            raise PGPFormatError("Packet data is incomplete, cannot return raw string.")

    #def __getattr__(self, name):
    #    if '_d' == name:
    #        try:
    #            return ''.join([self.tag._d, self.length._d, self.body._d])
    #        except:
    #            raise PGPPacketError, "Packet data is incomplete, cannot return _d."
    #    else:
    #        return self.__dict__[name]

    def __nonzero__(self): # egads
        return True

    def fill(self, d):
        """Set the Packet instances's data, filling its attributes.

        :Parameters:
            - `d`: string of OpenPGP packet data

        :Returns: Nothing

        Tag data (d) must be a string of valid OpenPGP packet data
        (tag, length, body, and possibly partial length/body
        interlacing).

        Example:

            >>> tag = chr(0xb4) # old version, user id (type 13), single octet length
            >>> length = chr(0x17) # body occupies next 23 octets
            >>> body = "Tester <test@email.com>"
            >>> pkt = Packet(tag+length+body)
            >>> pkt.tag.type, pkt.length.size, pkt.body.value
            13, 23, 'Tester <test@email.com>'
        """
        # Partial Length Mechanics (..elif 1 == self.tag.version..): Body
        # length is determined locally (with the help of str2int
        # functions) to accomodate a flow between partial body fragments,
        # concluding fragments, and complete packet bodies (append to
        # list, concatenate the list at the end). The actual length object
        # is determined after the fact and must match up with the body
        # data recovered in order to pass a selfcheck().
        # TODO see how much of the new length logic can use NewLength.data2size.
        self.tag = Tag(d[0:1])
        if 0 == self.tag.version: # old
            lo = [1, 2, 4, 0][self.tag.length_type] # [length octs][length type]
            idx = 1 + lo
            self.length = OldLength(d[1:idx])

            if 'UNDEFINED' == self.length.size:
                self.fill_body(d[idx:])
            else:
                self.fill_body(d[idx:idx+self.length.size])

        elif 1 == self.tag.version: # new
            idx = 1
            bodydata, lengthdata = [], []
            L1 = d[idx:idx+1]
            L1_ord = ord(L1)

            while 224 <= L1_ord <= 254: # catch partials
                size, idx = STN.strcalc(STN.partial2int, L1, idx)

                if 0 == len(lengthdata) and 512 > size:
                    raise PGPFormatError("First partial length MUST be at least 512 octets long. Received: length.size->(%s) length.data->(%s)" % (len(lengthdata), hex(L1_ord)))

                else:
                    lengthdata.append(L1)
                    bodydata.append(d[idx:idx+size])
                    idx = idx + size
                    L1 = d[idx:idx+1]
                    L1_ord = ord(L1)

            if L1_ord < 192:
                size, idx = STN.strcalc(STN.str2int, L1, idx)
                lengthdata.append(L1)
                bodydata.append(d[idx:idx+size])

            elif 192 <= L1_ord <= 223:
                lengthdata.append(d[idx:idx+2])
                size, idx = STN.strcalc(STN.doubleoct2int, d[idx:idx+2], idx)
                bodydata.append(d[idx:idx+size])

            elif 255 == L1_ord:
                lengthdata.append(d[idx:idx+5])
                size, idx = STN.strcalc(STN.pentoct2int, d[idx:idx+5], idx)
                bodydata.append(d[idx:idx+size])

            else:
                raise PGPError, "Extreme weirdness. Fix source."
            self.length = NewLength(''.join(lengthdata))
            self.fill_body(''.join(bodydata))

        self.size = len(self.tag._d) + len(self.length._d) + len(self.body._d)

        if self.check():
            return 1
        else:
            raise self.err[0], self.err[1]

    # is this really necessary?
    # TODO - tag.type == body.type
    def check(self):
        """Check the packet instance's attributes.

        :Returns: 1 if everything checks out

        Conditions that must be true:

            - pkt.tag most significant bit set
            - pkt.tag occupies only 1 octet: 'len(pkt.tag) == 1'
            - packet length matches body length: 'pkt.length.size == len(pkt.body._d)'
        """
        if 0x80 == 0x80 & ord(self.tag._d):
            if 1 == len(self.tag._d):
                if len(self.body._d) == self.length.size or 'UNDEFINED' == self.length.size:
                    return 1
                else:
                    self.err = (PGPValueError, "Packet length size doesn't match body size.")
            else:
                self.err = (PGPValueError, "Packet tag length must == 1. It isn't.")
        else:
            self.err = (PGPValueError, "Packet tag must have leftmost bit set to 1.")
        return 0

def create_NewLength(length, partial=False):
    """Create a NewLength instance.

    :Parameters:
        - `length`: integer octet count of corresponding packet body
        - `partial`: optional True or False (default False), whether
          or not this is a partial length

    :Returns: `OpenPGP.packet.NewLength` instance
    """
    if length < 192:
        return NewLength(chr(length))
    elif 192 <= length < 8383:
        return NewLength(STN.int2doubleoct(length))
    elif length <= 4294967295: # five oct header
        return NewLength('\xff' + STN.int2quadoct(length))
    else:
        raise PGPFormatError("Subpacket value exceeded maximum size.")

# Stuck on new versions.
def create_Tag(pkttype):
    """Create a Tag (packet tag) instance

    :Parameters:
        - `pkttype`: integer packet type constant (see
          `OpenPGP.constant.packets`)

    :Returns: `OpenPGP.packet.Tag` instance

    :note: Only "new" version tags will be created.
    """
    if 0 <= pkttype <= 63:
        tag_d = STN.int2str(192 | pkttype) # 192 forces new version
        return Tag(tag_d)
    else:
        raise PGPFormatError("Tag type must be in the range 0<=t<=63. Received->(%s)." % pkttype)

# Stuck on new packets. Also, grabbing the data from the tag, length and
# body to pass through packet creation is kind of redundant but seems like
# the right thing to do.
# Perhaps an option to stream, creating partial packets/block series..
def create_Packet(pkttype, body_d):
    """Create a Packet instance of the appropriate type.

    :Parameters:
        - `pkttype`: integer packet type constant (see
          `OpenPGP.constant.packets`)
        - `body_d`: string comprising the packet body

    :Returns: `Packet` subclass instance
    """
    tag_d = create_Tag(pkttype)._d
    length_d = create_NewLength(len(body_d))._d
    return pktclass(pkttype)(tag_d + length_d + body_d)
