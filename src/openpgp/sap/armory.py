"""Conversions to and from the ASCII-armored format

OpenPGP data is often shared in a text-based, "ASCII-armored" format. The
`list_armored()` function receives a text string and returns a list of
`Armored` class instances which organize information regarding a discrete
ASCII-armored block of data.

- Armored instances will organize block titles, headers, message data, and
  verify checksums. But..
- Armored instances *do not* regard the encoded message data's validity as
  OpenPGP data (consequently, they will not reconcile the encoded message
  data with the "type" declared in the block title).
"""
import os
import base64

import util.strnum as STN

from openpgp.code import *
from openpgp.sap.exceptions import *

armor_header_lines = ['-----BEGIN PGP MESSAGE-----',
                      '-----BEGIN PGP SIGNED MESSAGE-----',
                      '-----BEGIN PGP PUBLIC KEY BLOCK-----',
                      '-----BEGIN PGP PRIVATE KEY BLOCK-----',
                      '-----BEGIN PGP SIGNATURE-----',
                      '-----BEGIN PGP FLOTSAM-----'] # misc armoring

#class PGPArmorFailure(PGPFailure): pass
#class PGPChksumFailure(PGPArmorFailure): pass

# TODO resolve newline issues:
# 7.1: "any trailing whitespace (spaces, and tabs, 0x09) at the end of
#       any line is ignored when the cleartext signature is calculated."
# Since new lines must be included in signed data, my assumption is that
# a with line consisting of only '\n', the '\n'  will be preserved (but
# in the case of 'This is my line\n', it won't). Therefore, I'm appending
# an extra '' in the case of signed data that ends with an empty line to
# coerce a new os.linesep into the final output.
# Something has to be wrong with this but I'm not sure what..
#
# TODO for armored signatures, return the signature data in the data
# attribute (should read as standalone signature), and and the cleartext
# data to something like, um, obj.cleartext
class Armored:
    """ASCII-armored text (under construction)

    :IVariables:
        - `title`: string, apparent ASCII-armored message type (the
          data within need not correspond to the type implied by the
          title)
        - `headerlines`: list of strings, one string per line of
          header data (this list does not organize the header data)
        - `data`: string of unarmored data
    """
    # ignore the line after the chksum
    def chew(self, line):
        """A big fat kludge.

        Pending a nicer way to parse Armored stuff, this and `list_armored()`
        work together, going line by line to figure out where in the armored
        text we are and where to put it.
        """
        self.__dict__.setdefault('_in_armor', 0)
        # if we encounter a starting block before another has finished,
        # the previous data is ditched and we start again
        if line in armor_header_lines:
            if self.__dict__.has_key('title') and 'SIGNED MESSAGE' == self.title and '-----BEGIN PGP SIGNATURE-----' == line:
                if '' == self.__datalines[-1]:
                    self.__datalines.append('') # ugh.
                self.signed = os.linesep.join(self.__datalines)
                self._in_armor = self._armor_get_headers = 1
                return 0 # restart gathering signature subsection headers
            else:
                # 15 ~ index after '-----BEGIN PGP '
                self.title = line[15:].rstrip('-----')
                self.headerlines = []
                self._in_armor = self._armor_get_headers = 1
        elif self._in_armor and self._armor_get_headers:
            if 0 == len(line):
                self._armor_get_headers = 0
                self._armor_get_data = 1
                self.__datalines = []
            else:
                self.headerlines.append(line)
        elif self._in_armor and self._armor_get_data:
            # check for signed message first since it accomodates empy lines
            # (possible IndexError for line[0])
            if 0 < len(line) and '=' == line[0]:
                self.chksum = STN.str2int(base64.decodestring(line[1:5]))
                self.data = base64.decodestring(''.join(self.__datalines))
                self._armor_get_data = self._in_armor = 0
                return 1
            else:
                self.__datalines.append(line)
        return 0

    def selfcheck(self):
        if 'SIGNED MESSAGE' == self.title:
            return 1 # oh, how useful is this..?
        else:
            dsum = crc24(self.data)
            if dsum == self.chksum:
                return 1
            else:
                raise PGPFormatError("Data did not match chksum. Received chksum->(%s), Calculated chksum->(%s))" % (self.chksum, dsum))
    # rfc2440 6.2 OpenPGP should consider improperly formatted Armor
    # Headers to be corruption of the ASCII Armor.
    def resolve_headers(self):
        raise NotImplementedError
        headers = '  '.join(self._headers) # _headers should be a list!

# crc24() ruthlessly copied from pgpmsg.py:
# Copyright (C) 2003  Jens B. Jorgensen <jbj1@ultraemail.net>
def crc24(s):
    crc24_init = 0xb704ce
    crc24_poly = 0x1864cfb
    crc = crc24_init

    for i in list(s):
        crc = crc ^ (ord(i) << 16)

        for j in range(0, 8):
            crc = crc << 1

            if crc & 0x1000000:
                crc = crc ^ crc24_poly

    return crc & 0xffffff

def list_armored(d):
    """Find ASCII-armored data in a string.

    :Parameters:
        - `d`: string of ASCII-armored data

    :Returns: list of `Armored` instances

    The Armored instance's `data` attribute is not necessarily a
    valid OpenPGP message (sequences of OpenPGP packets defined in
    rfc2440 10.2), but rather the string of data encoded and bounded
    according to the OpenPGP ASCII-armored format. Use this data to
    find packets.
    """
    ascmsg = Armored()
    msg_list = []

    for line in [x.rstrip() for x in d.split(os.linesep)]:

        if 1 == ascmsg.chew(line):

            if ascmsg.selfcheck():
                msg_list.append(ascmsg)
            else:
                raise PGPFormatError("Received bad armored block.") # useful??

            # signed message data will only register as completed once it
            # has received the header of the next SIGNATURE block (line)
            # therefore, 'line' has to be sent back to the new ascmsg object
            if 'SIGNED MESSAGE' == ascmsg.title:
                ascmsg = Armored()
                ascmsg.chew(line)
            else:
                ascmsg = Armored()

    return msg_list

def looks_armored(d):
    """Determine whether a string is ASCII-armored.

    :Parameters:
        - `d`: string of OpenPGP data (armored or not)

    :Returns: boolean True if it looks armored, False otherwise

    :todo: For all intents and purposes this works. But it does not work the
        way it should. It just looks for a '-----BEGIN PGP' substring.
    """
    if -1 != d.find('-----BEGIN PGP'):
        return True
    else:
        return False

def apply_armor(target):
    """Create an ASCII-armored block.

    :Parameters:
        - `target`: message instance, signature packet, or list of packets

    :Returns: string of armored data

    Message instances will be armored as their appropriate type, lone signature
    packets will be armored as a lone, clearsigned signature, and any other
    packet, list of packets, or arbitrary strings will be armored as
    'PGP FLOTSAM'.

    Clearsigned text is automatically produced for a signed message which has
    only text signatures (``SIG_TEXT``) on a literal message.

    :note: The theory behind armoring arbitrary strings is that armoring is
        just a synonym for "encode as base64." The 'PGP FLOTSAM' label should
        be enough to flag such things as non-standard.
    :note: Single packet messages (ex. literal message made up of one literal
        packet) should be sent as a message instance to avoid being labeled as
        "flotsam."

    :todo: Automatically try to armor complete messages in a list of packets.
    :todo: Make clearsigning an option. See clearsigning conditions above.
    """
    from openpgp.sap.pkt.Signature import Signature as SIG_CLASS
    from openpgp.sap.msg.Msg import Msg as MSG_CLASS

    clearsign = False

    if isinstance(target, SIG_CLASS):
        header_line = "-----BEGIN PGP SIGNATURE-----"
        footer_line = "-----END PGP SIGNATURE-----"
        data = target.rawstr()

    elif isinstance(target, MSG_CLASS):

        if target.type in [MSG_COMPRESSED, MSG_ENCRYPTED, MSG_LITERAL]:
            header_line = "-----BEGIN PGP MESSAGE-----"
            footer_line = "-----END PGP MESSAGE-----"
            data = target.rawstr()

        elif MSG_PRIVATEKEY == target.type:
            header_line = "-----BEGIN PGP PRIVATE KEY BLOCK-----"
            footer_line = "-----END PGP PRIVATE KEY BLOCK-----"
            data = target.rawstr()

        elif MSG_PUBLICKEY == target.type:
            header_line = "-----BEGIN PGP PUBLIC KEY BLOCK-----"
            footer_line = "-----END PGP PUBLIC KEY BLOCK-----"
            data = target.rawstr()

        elif MSG_SIGNED == target.type:
            header_line = "-----BEGIN PGP MESSAGE-----"
            footer_line = "-----END PGP MESSAGE-----"
            text_sigs = [s for s in target.sigs if SIG_TEXT == s.body.type]
            len_text_sigs = len(text_sigs)

            # make sure there are text sigs at all before considering clearsigs
            if len_text_sigs and MSG_LITERAL == target.msg.type and len_text_sigs == len(target.sigs):
                clearsign = True
                data = ''.join([l.body.data for l in target.msg.literals])
                alg_hash = text_sigs[0].body.alg_hash
                # just munge footer since "END PGP SIGNED MESSAGE" not used
                sig_d_list = []

                for text_sig in text_sigs:
                    sig_d_list.append(apply_armor(text_sig))

                    if alg_hash != text_sig.body.alg_hash:
                        raise PGPFormatError("Clearsigs require the same hash for each signature. 1st sig hash->(%s) conflicts with a following sig->(%s)" % (alg_hash, text_sig.body.alg_hash))

                if HASH_SHA1 == alg_hash:
                    hash_header = "Hash: SHA1"

                elif HASH_MD5 == alg_hash:
                    hash_header = "Hash: MD5"

                header_line = os.linesep.join(["-----BEGIN PGP SIGNED MESSAGE-----", hash_header])
                footer_line = os.linesep.join(sig_d_list)

            else:
                data = target.rawstr()

        else: # dismiss marker and stored key messages
            raise NotImplementedError("Armoring of message type %s is not supported." % target.type)

    else: # handle funky lists of packets or strings

        if not isinstance(target, list):
            target = [target]

        header_line = "-----BEGIN PGP FLOTSAM-----"
        footer_line = "-----END PGP FLOTSAM-----"

        datalist = []
        for t in target:

            if hasattr(t, 'rawstr'):
                t = t.rawstr()

            datalist.append(t)

        #data = ''.join([p.rawstr() for p in target])
        data = ''.join(datalist)

    if clearsign:
        armored_d = data
        if data[-1:] != '\n': # \r\n, whatever.. just use a pointless chksum
            checksumline = os.linesep # to ensure some line separation
        else:
            checksumline = ''
    else:
        armored_d = base64.encodestring(data)
        checksumline = '=' + base64.encodestring(STN.int2str(crc24(data))) + os.linesep

    _d = header_line + (os.linesep * 2) + armored_d + checksumline + footer_line + os.linesep

    return _d
