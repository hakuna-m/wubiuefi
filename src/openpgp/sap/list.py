"""If you're looking for something, you'll find it here.
"""
#TODO: pgpwarn() is ugly. Kill it. Same goes for EXCEPT, WARN, and SUPRESS
import logging
import StringIO
import copy

from os import linesep

from openpgp.code import *

from openpgp.sap.exceptions import *

import openpgp.sap.pkt as PKT
import openpgp.sap.text as TXT
import openpgp.sap.crypto as CRYPT

from openpgp.sap.armory import looks_armored, list_armored
from openpgp.sap.msg.CompressedMsg import CompressedMsg
from openpgp.sap.msg.EncryptedMsg import EncryptedMsg
from openpgp.sap.msg.KeyMsg import SecretKeyMsg
from openpgp.sap.msg.KeyMsg import StoredKeyMsg
from openpgp.sap.msg.KeyMsg import PublicKeyMsg
from openpgp.sap.msg.LiteralMsg import LiteralMsg
from openpgp.sap.msg.SignedMsg import SignedMsg
from openpgp.sap.pkt.Packet import Tag, pktclass
from openpgp.sap.util.misc import unique_order, intersect_order


class DummyMsg: pass # only to preserve the flow of packet sequence parsing

def deliteralize(msgs):
    """String-ify literal messages.
    
    :Parameters:
        - `msgs`: list of message instances

    :Returns: list of same messages, except that all literals will have been
        magically converted to strings

    Sample literal output::
        
        Filename: the_file.txt
        Modified: 1234567890
        Format: t
        
        This is the literal text found in the_file.txt.


        Filename: the_next_file.txt
        Modified: 1234567891
        Format: t
        
        And now some literal text found in the_next_file.txt.


    :note: Debate whether or not this should function should be encapsulated in
        `list_as_signed()`. It's not since this one is more of an output-only
        convenience.

    :TODO: ADD TESTS!
    """
    outlist = []

    for msg in msgs:

        if hasattr(msg, 'literals'):

            for pkt in msg.literals:
                msg = linesep.join(["Filename: %s" % pkt.body.filename,
                                    "Modified: %s" % pkt.body.modified,
                                    "Format: %s%s" % (pkt.body.format, linesep),
                                    pkt.body.data,
                                    linesep]) # leave enough room for next one

        outlist.append(msg)        

    return outlist
     

# Upon encountering an error in sequence matching, the helper functions will
# return all the packets sent to them, including those that matched the
# sequence, and a warning will be issued. The packets will be returned as
# leftovers. This way, all messages that are returned are complete and capable.
def find_msg(pkts):
    """Find a single OpenPGP message in a list of packets.

    :Parameters:
        - `pkts`: list of OpenPGP packet instances

    :Returns: tuple (message, [leftover packets])

    Packet lists must start with a potentially valid sequence in order for any
    message to be found. In other words, an out of place packet at the
    beginning of the packet list will invalidate all potential messages
    following it.
    """
    msg, leftovers = None, pkts

    if len(pkts) != 0:

        #try:
        #    msg_type = pkts[0].tag.type

        #except AttributeError: # catch non-existent pkts[0].tag.type
        #    pgpwarn(PGPMessageWarning, "find_msg() found a list item which does not resemble a packet instance.")

        # let AttributeError fly, since should be a
        # good packet list to begin with
        msg_type = pkts[0].tag.type

        # match encrypted message
        if msg_type in [PKT_SYMENCDATA, PKT_SYMENCINTDATA, PKT_PUBKEYSESKEY, PKT_SYMKEYSESKEY]:
            msg, leftovers = find_encrypted_msg(pkts)

        # match signed message
        elif msg_type in [PKT_SIGNATURE, PKT_ONEPASS]:
            msg, leftovers = find_signed_msg(pkts)

        # match compressed message
        elif msg_type in [PKT_COMPRESSED]:
            msg, leftovers = find_compressed_msg(pkts)

        # match literal message
        elif msg_type in [PKT_LITERAL]:
            msg, leftovers = find_literal_msg(pkts)

        # match public, secret, and stored keys
        elif msg_type in [PKT_PUBLICKEY, PKT_PRIVATEKEY]:
            msg, leftovers = find_key_msg(pkts)

        elif pkts[0].tag.type in [PKT_MARKER]: # hacky-poo
            msg = DummyMsg()
            msg._seq = pkts[0]
            leftovers = pkts[1:]

    return msg, leftovers

def find_compressed_msg(pkts):
    """Find a compressed OpenPGP message in a list of packets.

    :Parameters:
        - `pkts`: list of OpenPGP packet instances

    :Returns:
        - tuple (CompressedMsg_instance, leftover_pkts):
            - `CompressedMsg_instance`: instance of the CompressedMsg class
            - `leftover_pkts`: list of packets that did not contribute to
              the message
    """
    if PKT_COMPRESSED == pkts[0].tag.type:
        msg = CompressedMsg()
        msg._seq = [pkts[0]]
        msg.compressed = pkts[0]
        return msg, pkts[1:]

    else:
        return None, pkts

# Tacking on the '_type' attribute to be able to distinguish target symmetric
# session keys from public key session keys seems pretty ugly, but it's more
# obvious than using a unique attribute like 's2k'.
# Also, the if/elif can be rearranged to avoid repetition.
def find_encrypted_msg(pkts):
    """Find an encrypted OpenPGP message in a list of packets.

    :Parameters:
        - `pkts`: list of OpenPGP packet instances

    :Returns:
        - tuple (EncryptedMsg_instance, leftover_pkts):
            - `EncryptedMsg_instance`: instance of the EncryptedMsg class
            - `leftover_pkts`: list of packets that did not contribute to
    """
    first_pkt_type = pkts[0].tag.type
    encmsg = EncryptedMsg()

    if (first_pkt_type in [PKT_SYMENCDATA, PKT_SYMENCINTDATA]):
        encmsg.targets = None
        encmsg._seq = [pkts[0]]
        #encmsg.ciphertext = pkts[0].body.data
        encmsg.encrypted = pkts[0]
        #if PKT_SYMENCDATA == pkts[0].tag.type:
        #    encmsg.integrity = 0
        #elif PKT_SYMENCINTDATA == pkts[0].tag.type:
        #    encmsg.integrity = 1
        return encmsg, pkts[1:]

    elif first_pkt_type in [PKT_PUBKEYSESKEY, PKT_SYMKEYSESKEY]:
        seq = []
        idx = 0

        try:
            encmsg.targets = []

            while pkts[idx].tag.type in [PKT_PUBKEYSESKEY, PKT_SYMKEYSESKEY]:
                seq.append(pkts[idx])
                encmsg.targets.append(pkts[idx])
                idx += 1

            if pkts[idx].tag.type in [PKT_SYMENCDATA, PKT_SYMENCINTDATA]:
                seq.append(pkts[idx])
                encmsg._seq = seq
                encmsg.encrypted = pkts[idx]

                if PKT_SYMENCDATA == pkts[idx].tag.type:
                    encmsg.integrity = 0
                elif PKT_SYMENCINTDATA == pkts[idx].tag.type:
                    encmsg.integrity = 1

                return encmsg, pkts[idx+1:]

            else:
                raise PGPMessageWarning("No encrypted data followed session keys.")

        except IndexError, AttributeError:
            raise PGPMessageWarning("Encrypted message is missing critical packets.")
    
    return None, pkts

def find_key_msg(pkts):
    """Find a public key message (or derivative) in a list of packets.

    :Parameters:
        - `pkts`: list of OpenPGP packet instances

    :Returns: 
        - tuple (PublicKeyMsg_instance, leftover_pkts):
            - `PublicKeyMsg_instance`: instance of PublicKeyMsg class
            - `leftover_pkts`: list of packets that did not contribute to the message

    The public key message content is organized only by packet type
    and does not reconcile packet data. Specifically, signature
    packets following the public key packet are not verified as
    *revocation* signatures, and the signature packet following each
    public subkey is not verified as a signature which *binds the
    subkey to the primary public key*.
    """
    if PKT_PRIVATEKEY == pkts[0].tag.type:
        keymsg = SecretKeyMsg(pkts)

    elif PKT_PUBLICKEY == pkts[0].tag.type and PKT_TRUST in [x.tag.type for x in pkts]:
        keymsg = StoredKeyMsg(pkts)

    elif PKT_PUBLICKEY == pkts[0].tag.type:
        keymsg = PublicKeyMsg(pkts)

    else:
        return None, pkts

    leftovers = pkts[len(keymsg.seq()):]

    return keymsg, leftovers 

# set 'data' attribute
# TODO reconcile LiteralMsg = (LITERAL + LITERAL + LITERAL + ...)
#      right now this still uses the single literal packet to define
#      the literal message
def find_literal_msg(pkts):
    """Find a literal OpenPGP message in a list of packets.

    :Parameters:
        - `pkts`: list of OpenPGP packet instances

    :Returns: tuple (LiteralMsg_instance, leftover_pkts) where
        ``LiteralMsg_instance`` is an instance of the `LiteralMsg`
        class and ``leftover_pkts`` is a list of packets that did not
        contribute to the message
    """
    lit = LiteralMsg()
    lit.literals, lit._seq = [], []
    idx = 0

    while 0 != len(pkts[idx:]) and PKT_LITERAL == pkts[idx].tag.type:
        lit._seq.append(pkts[idx]) # redundant, yes, just preserving _seq-ness
        lit.literals.append(pkts[idx])
        idx += 1

    if 1 <= len(lit.literals):
        return lit, pkts[idx:]

    else:
        return None, pkts

# Right now, a "signed message" according to this function is defined by
# rfc2440 10.2. However, according to the signature types in 5.2.1, there are
# clearly other possibilities: standalone, signature on a key packet, signature
# on a signature - which are all handled outside the "message" context. For
# now, I want to keep this function strictly message-focused until I can get my
# head clear on all the different signature possibilities. This is why a lone
# signature packet encountered here is dismissed as a leftover instead of being
# recognized as a standalone.
#
# The SignedMsg attributes set here are 'sigs', 'msg', and 'onepass'.
#
# My Grand Interpretation of Signatures
# -------------------------------------
# In practice, it looks as though signed data is always placed in a literal
# data packet and then used in a one-pass sequence or follows a signature
# packet. Also, it looks as though nested signatures only appear in
# ASCII-armored form. I haven't seen anything to the contrary in practice.
# 
# But the spec's Packet Composition suggests more possibilities that I'd like
# to handle - specifically, multiple "flat" signatures of common data and
# combinations of flat and nested signatures in the same message for
# compactness.
# 
# 'normal' signature: packet sequence sig, msg
# 'onepass' signature: packet sequence onepass, msg, sig
# 
# I'm going to assume the following: If a message intends to communicate
# complex flat or nested relationships between signatures and data, the various
# packets defining the relationship will *all* be visible individually - in
# other words, they will exist in the message *as packets*. Otherwise, if an
# entire signature message (complex or otherwise) is the target of new
# signature combinations, that the message-to-be-signed will be "hidden" in a
# literal or compressed data packet (I've not seen a compressed packet used
# like this yet).
#
# And I'm going to impose the following: A sequence of normal signature packets
# in a single message MUST describe a series of nested signatures. This is
# because I'm assuming that the now relatively uncommon sequence (signature,
# message) invariably meant "the signature applies to the message" as message
# was most likely a literal data packet. Also, it makes it easier to parse the
# sequence. :)
# 
# Therefore the sequence (sig, sig, sig, literal) MUST describe the relation:
# sign( sign( sign( literal ) ) )
# 
# So my goal is to make sense of an arbitrary yet legal sequence of packet
# using the reasoning above. Here goes:
def find_signed_msg(pkts):
    """Find a signed OpenPGP message in a list of packets.

    :Parameters:
        - `pkts`: list of OpenPGP packet instances

    :Returns:
        - `tuple`: (SignedMsg_instance, leftover_pkts):
            - `SignedMsg_instance`: instance of the `SignedMsg` class
            - `leftover_pkts`: list of packets that did not contribute to
              the `SignedMsg` instance
    """
    sigmsg = SignedMsg()
    sigmsg._seq = []
    sigmsg.sigs = []
    first_pkt_type = pkts[0].tag.type

    if PKT_SIGNATURE == first_pkt_type:
        sigmsg.sigs.append(pkts[0])
        sigmsg._seq.append(pkts[0])
        msg, leftovers = find_msg(pkts[1:])

        if msg is not None:
            sigmsg.msg = msg
            sigmsg._seq.append(msg)
            return sigmsg, leftovers

        else: # no message follows, must be detached - handle elsewhere
            return None, pkts

    elif PKT_ONEPASS == first_pkt_type:
        sigmsg.onepass = pkts[0]
        sigmsg._seq.append(pkts[0])
        msg, leftovers = find_msg(pkts[1:])

        if msg is not None:
            sigmsg.msg = msg
            sigmsg._seq.append(msg)

            try: # the one-pass message must be followed by a signature..
                if PKT_SIGNATURE == leftovers[0].tag.type:
                    sigmsg.sigs.append(leftovers[0])
                    sigmsg._seq.append(leftovers[0])
                    return sigmsg, leftovers[1:]

            except IndexError, AttributeError: # catch non-existent leftovers[0].tag.type
                pgpwarn(PGPMessageWarning, "Dismissing one-pass signed message: missing trailing signature.")

        # ..otherwise abort
        pgpwarn(PGPMessageWarning, "Dismissing one-pass signed message: missing signed message.")
        
    return None, pkts

def find_keys(keys, **kw):
    """Find keys based on actions or IDs.

    :Parameters:
        - `keys`: list of key message instances

    :Keywords:
        - `action`: optional 'sign' or 'encrypt' to target only keys of a
          certain type
        - `userids`: list of matchable tuples [(str primary, str userid)] where
          the userid may be a substring
        - `keyids`: list of matchable key IDs or fingerprints [(primary, keyid)]

    :Returns: list of (key, [matching_fprint, ..]) tuples for each viable key
        message

    :note: 'None' will will match in both the primary or and keyid in a list of
        them.
    """
    action = kw.get('action')
    uids = kw.get('userids', [])
    keyids = kw.get('keyids', [])
    keytargets = []

    for key in keys:
        _pids = [None, False, '', key.primary_id, key.primary_fprint]

        if uids: 
            _uids = [u for u in key._b_userids.keys() if
                        [(p,i) for (p,i) in uids if p in _pids and i in u]]

            if not _uids:
                continue

        keypkts = [key._b_primary.leader] # organize all the key packets
        keypkts.extend([b.leader for b in key._b_subkeys.list()])

        if action: # hang on to all keypkts which match the action algorithms

            if 'sign' == action:
                keypkts = [p for p in keypkts if p.body.alg in ASYM_SIGNING]

            elif 'encrypt' == action:
                keypkts = [p for p in keypkts if p.body.alg in ASYM_ENCRYPTING]

        if keyids:
            _keypkts = []

            for keypkt in keypkts:
                _target_ids = [None, keypkt.body.id, keypkt.body.fingerprint]

                for p, t in keyids:
        
                    if p in _pids and t in _target_ids:
                        _keypkts.append(keypkt)

            keypkts = _keypkts

        if keypkts:
            keytargets.append((key, [p.body.fingerprint for p in keypkts]))

    return keytargets

# Primary, user IDs user attribute blocks are scanned for preference
# information. This is a vote-processing deal that follows these rules:
# - a single key gets one set of votes determined by its first signature that
#   contains such a preference.
# - the 'top_choice' sets an arbitrary ceiling of value that is hopefully
#   larger than the length of any preference list. To be complete, this value
#   should be discovered by scanning all the preferences to begin with.
def find_key_prefs(keys):
    """Return a dictionary with an intersection of keys' preferences.
    
    :Parameters:
        - `keys`: list of `openpgp.sap.msg.KeyMsg.KeyMsg` subclass instances

    :Returns: dictionary with keys 'sym', 'hash', 'comp' set with list of
        appropriate codes in descending order of popularity
    """
    sym_v, hash_v, comp_v = [], [], []

    for key in keys:
        sym_b = hash_b = comp_b = None # for *_v extension capability below
        sigs = [] # where to look for preference blocks

        for block in key._b_userids.list() + key._b_userattrs:
            sigs.extend([s for s in block.local_bindings + block.local_direct])

        # grab hashed local signatures
        has_hashed = lambda x: hasattr(x, 'hashed_subpkts')

        for sig in [s for s in sigs if has_hashed(s.body)]:

            # sigs are all "equal," so just fill up the spaces asap
            if CRYPT.verify(sig, block.leader, key._b_primary.leader):

                for subpkt in sig.body.hashed_subpkts:

                    if SIGSUB_SYMCODE == subpkt.type:
                        sym_b = subpkt.value
                    elif SIGSUB_HASHCODE == subpkt.type:
                        hash_b = subpkt.value
                    elif SIGSUB_COMPCODE == subpkt.type:
                        comp_b = subpkt.value

                    if sym_b and hash_b and comp_b: # break out
                        break

            if sym_b and hash_b and comp_b: # still breaking out..
                break

        # extend with list of preferences if present, otherwise nullify
        if sym_b and sym_v is not None:
            sym_v.append(unique_order(sym_b))
        else:
            sym_v = None

        if hash_b and hash_v is not None:
            hash_v.append(unique_order(hash_b))
        else:
            hash_v = None

        if comp_b and comp_v is not None:
            comp_v.append(unique_order(comp_b))
        else:
            comp_v = None

    tally = {'sym':[], 'hash':[], 'comp':[]}

    if sym_v:
        tally['sym'] += intersect_order(sym_v)

    if hash_v:
        tally['hash'] += intersect_order(hash_v)

    if comp_v:
        tally['comp'] += intersect_order(comp_v)

    return tally



# is_msg()/is_pkt() are only here to help eliminate 'isinstance()' all over
#def is_msg(msg, code)
#    """
#    :todo: Write some tests.
#    """
#    if msg.type = code:
#        return True
#    return False
#
#def is_pkt(pkt, code)
#    """
#    :todo: Write some tests.
#    """
#    if pkt.type = code:
#        return True
#    return False

def list_msgs(pkts, **kw):
    """List OpenPGP message instances given a list of packet instances.

    :Parameters:
        - `pkts`: list of packet instances

    :Keywords:
        - `code`: optional message type code to match listed messages
        - `leftover`: a list used to append extraneous packets found after
          those which comprised valid messages. If no valid messages are found,
          the the entire packet sequence will be `leftover`.

    :Returns: list of OpenPGP message instances

    :todo: Double check (and hopefully eliminate) the deepcopy() of `pkts`.
    """
    pkts = copy.deepcopy(pkts) # see if this is necessary
    leftover = kw.get('leftover', [])
    code = kw.get('code', None)
    msgs = []
    i = 0
    m, l = find_msg(pkts)

    while m is not None:

        msgs.append(m)

        if 0 == len(l):
            break
        else:
            m, l = find_msg(l)

    if code:
        msgs = filter(lambda m: m.type == code, msgs)

    if l:
        leftover.extend(l)

    return msgs

def list_pkts(s, **kw):
    """Create a list of OpenPGP packet instances given a string of data.

    :Parameters:
        - `s`: string of native OpenPGP data (native or ASCII-armored)

    :Keywords:
        - `code`: optional packet type code to match listed packets

    :Returns: list of packet instances

    `list_pkts()` will return all OpenPGP packets found as various packet type
    instances.

    :TODO: It looks like an incomplete packet may be returned at the end of the
        list. Check this.
    """
    code = kw.get('code', None)

    if looks_armored(s):
        arm_d = [] # native data

        for arm in list_armored(s):
            # all armored data is caught, including clearsigned sigs
            # clearsigned text is ignored
            arm_d.append(arm.data)

        s = ''.join(arm_d)

    pkts = []
    idx = 0
    len_d = len(s)

    while idx < len_d:
        tag = Tag(s[idx]) # assume first octet starts packet tag (header)
        packet = pktclass(tag.type)(s[idx:]) 
        idx = idx + packet.size
        pkts.append(packet)

    if code:
        pkts = filter(lambda p: p.tag.type == code, pkts)

    return pkts

def list_as_signed(pgp_d, **kw):
    """With respect to the API, list useful OpenPGP items.

    :Parameters:
        - `pgp_d`: str either ASCII-armored text or native OpenPGP data -
          armored text may contain multiple armored blocks, while native
          OpenPGP data should exist as a single unbroken string

    :Keywords:
        - `leftover`: *optional* list to which leftover (non-message)
          packets will be appended - this will include repeats of
          detached or standalone signature packets 
        - `decompress`: set to True to auto-decompress compressed messages
        - `detached`: detached string, signed by signatures in `pgp_d`

    :Returns: list of message instances and special signature tuples

    This function takes OpenPGP data and returns a list of items that are
    "useful" for the API. In particular, this includes detached, standalone,
    and key signature tuples (hence, "as_signed") which are returned as::

        ([det_sig1, det_sig2, ..], string) # detached signatures
        ([key_sig1, key_sig2, ..], key) # key_sigs within a key message
        ([standalone_sig], None) # standalone signature

    :note: This is basically a `list_msgs()` which works with armored strings.
        One important difference is that the focus is turned away from packets
        (leftover) toward 'usable things' with respect to the API.
    :note: I'm debating whether or not to scrap the whole ([sigs], target)
        tuple deal and automagically convert detached sigs and clearsigned sigs
        to signed messages, using filename='' and modified='' for both,
        format='b' for detached and format='t' for clearsigned. Higher up, this
        will have the consequence of spitting out the signed stuff (could be a
        lot) with some literal packet header junk prepended. Right now, only
        detached and clearsigned stuff are sent out as tuples. It's just ugly
        worrying about whether we're working with instances or tuples all over
        the place (or ignoring the possibilities and just letting an exception
        be raised).
    """
    saplog = logging.getLogger("saplog")
    det_d = kw.get('detached', None)

    # stringify pgp_d and det_d
    if not pgp_d:
        return [] # det_d requires detached signatures, so it's safe to return

    #elif hasattr(pgp_d, 'read'): #elif isinstance(pgp_d, (StringIO, file)):
    #    pgp_d = pgp_d.read()

    elif isinstance(pgp_d, str):
        pass

    else:
        raise TypeError("Invalid OpenPGP type. Please send string, file, or StringIO.")

    if det_d:
        if hasattr(det_d, 'read'):
            det_d = det_d.read()
        elif isinstance(det_d, str):
            pass
        else:
            raise Hell

    players = [] # bona fide messages and detached signature tuples

    # similar "looks_armored" deal in list_pkts(), perhaps can consolidate
    if looks_armored(pgp_d):
        arm_d = [] # native data

        for arm in list_armored(pgp_d):

            if 'signed' in arm.__dict__: # distinguished a clearsigned message

                # this is where we can just create a signed message,
                # literalname = '', modified = 0, format = 't'

                sigs = [p for p in list_pkts(arm.data) if PKT_SIGNATURE == p.tag.type]
                players.append((sigs, arm.signed))
            else:
                arm_d.append(arm.data)

        pgp_d = ''.join(arm_d)

    leftover = []
    msgs = list_msgs(list_pkts(pgp_d), leftover=leftover)
    detached_sigs = []
    detached_types = [SIG_BINARY, SIG_TEXT]
    standalone_types = [SIG_STANDALONE, SIG_TIMESTAMP, SIG_THIRDPARTY]

    for pkt in leftover:                            # distinguish leftover..

        if PKT_SIGNATURE == pkt.tag.type:

            if pkt.body.type in detached_types:     # ..detached sigs from..
                detached_sigs.append(pkt)

            elif pkt.body.type in standalone_types: #..standalone sigs
                standalone_sigs.append(pkt)
                players.append(([pkt],None))

    if kw.get('decompress'):

        for i in range(len(msgs)): 

            if MSG_COMPRESSED == msgs[i].type:
                saplog.info("Decompressing compressed message (%r)." % TXT.alg_comp_msg(msgs[i].compressed.body.alg))
                compmsg = msgs.pop(i)
                compplayers = list_as_signed(compmsg.compressed.body.data)

                for j in range(len(compplayers)): # to preserve the order in..
                    msgs.insert(i+j, compplayers[j]) # ..which they appeared

    if detached_sigs:
        players.append((detached_sigs, det_d))

    players += msgs

    if isinstance(kw.get('leftover'), list):
        kw['leftover'].extend(leftover)

    return players

# when the time comes to have the API work on StringIO/files, there should
# be a complimentary API function like this one that will accept actual
# message instances (like this one accepts strings) as well as
# pseudo-messages (like this one accepts files). The actual messages (in
# memory already) will be rawstr()-inged to act like the pseudo-messages
# so that everything beneath can .seek() and .read(). Something like ..a
# pseudo-literalmsg which gives a list of literal files?? to work on.
#
# StringIO and string make anonymous literal messages
# can just add sio.name attribute for literal messages
#
# Modification times are ugly.
#def targets2literalmsg(targets, format='b'):
#    """Construct a literal message from a list of ...
#
#    :Parameters:
#        - `targets`: list of files, strings, or StringIO instances
#        - `format`: 'b' for binary or 't' for text mode
#
#    :Returns: `OpenPGP.message.LiteralMsg.LiteralMsg` instance or None
#        if no literal message was created
#
#    :note: All literal packets in the final message share the same
#        binary or text format.
#    """
#    if not isinstance(targets, list):
#        targets = [targets]
#
#    litparams = []
#
#    for t in targets:
#
#        if isinstance(t, StringIO.StringIO):
#            t.seek(0)
#
#            if hasattr(t, 'name'): # ?? name ??
#                filename = t.name
#
#                try:
#                    modified = int(os.path.getmtime(filename)) 
#
#                except:
#                    modified = 0
#            else:
#                filename = 'literal'
#
#        elif isinstance(t, file):
#            import os
#
#            t.seek(0)
#            filename = t.name.split(os.sep)[-1] # this might mess up escaped names
#            modified = int(os.path.getmtime(t.name)) # must use original name
#            data = t.read()
#
#        elif isinstance(t, str):
#            filename = 'literal'
#            modified = 0
#            data = t
#
#        else:
#            raise Hell
#
#        litparams.append({'filename':filename,
#                          'modified':modified,
#                          'data':data,
#                          'format':format})
#
#    from openpgp.sap.msg.LiteralMsg import create_LiteralMsg 
#    return create_LiteralMsg(litparams)
#
# msg classes might be better than msg.type integers
#def targets2msgs(targets, msgtypes=None):
#    """Find OpenPGP messages in a target list:
#
#    :Parameters:
#        - `targets`: list (or single item) of string, file, or
#          StringIO instances containing OpenPGP data
#        - `msgtypes`: *optional* list of integers, OpenPGP message
#          constants to filter message instances
#
#    :Returns: list of `OpenPGP.message.Msg` subclass instances
#    """
#    from openpgp.sap.msg.Msg import Msg
#
#    if not isinstance(targets, list):
#        targets = [targets]
#    
#    is_message = lambda m: isinstance(m, Msg)
#    is_message_type = lambda m: is_message(m) and m.type in msgtypes
#
#    msgs = []
#
#    for t in targets:
#
#        if is_message(t):
#
#            if msgtypes:
#                if t.type in msgtypes:
#                    msgs.append(t)
#            else:
#                msgs.append(t)
#        else:
#            #if isinstance(t, (StringIO, file)):
#            if hasattr(t, 'seek') and hasattr(t, 'read'):
#                t.seek(0)
#                s = t.read()
#            elif isinstance(t, str):
#                s = t
#            else:
#                raise TypeError("Don't know how to find messages in %s." % t.__class__)
#            
#            if msgtypes:
#                msgs.extend(filter(is_message_type, list_players(s, None)))
#            else:
#                msgs.extend(filter(is_message, list_players(s, None)))
#
#    return msgs
#
#def organize_msgs(pkts):
#    """Organize packet instances into lists comprising valid messages.
#
#    Please use list_pkts() instead.
#    
#    :Parameters:
#        - `pkts`: list of OpenPGP.packet.* instances
#
#    :Returns:
#        - tuple (messages, leftovers):
#            - `messages`: a list of (message_type, packet_list) tuples
#              where message_type is the constant value of the message
#              type (see OpenPGP.constant.messages) and packet_list is
#              the list of packet instances that comprise the respective
#              message type (see OpenPGP.packet.*).
#            - `leftovers`: a list of extraneous packets found after 
#              the packets which comporised valid messages. If no valid
#              messages were found, the "leftovers" will contain all of
#              the packets sent in pkts.
#
#    **Note:** pkts is used to build the message list and is not
#    likely to retain its original value after being passed to 
#    organize_msgs. Make a copy beforehand if necessary.
#    
#    organize_msgs() organizes a list of packet instances into "message
#    sublists," or smaller packet lists, each of which comprise a valid
#    OpenPGP message. The message sublists form the packet_list part of
#    a (message_type, packet_list) tuple. This way, the packet_lists
#    can be operated on easily via their corresponding message_type.
#
#    For an imaginary list of 12 packet instances pkts (pkt1-pkt12),
#    output from organize_msgs(pkts) might look like:
#
#        >>> organize_msgs(pkts)
#        ( # begin the list of messages
#          [(MSG_SIGNED,     [pkt1, pkt2, pkt3, pkt4, pkt5, pkt6]),
#           (MSG_COMPRESSED, [pkt7]), 
#           (MSG_ENCRYPTED,  [pkt8, pkt9, pkt10])],
#          # begin the list of leftovers
#          [pkt11, pkt12] 
#        )
#
#    The values MSG_SIGNED, MSG_COMPRESSED, and MSG_ENCRYPTED are
#    arbitrary constants defined in OpenPGP.constant.messages. Here, 
#    packets p1-p6 might comprise a "one-pass" signature where p1 is
#    the one-pass packet, p6 is the signature packet, and p2-p5
#    constitute a complete OpenPGP "sub" message. The second,
#    compressed message consists of a single compressed packet.
#    Finally, packets p8-p10 might be two session keys and one
#    encrypted packet, resulting in an encrypted message.
#
#    Packets p11 and p12 evidently did not make up a message 
#    (individually or combined) and were sent in the list of
#    "leftovers."
#        
#    Here's a more visual representation, this time using possible
#    output from the organization of six packets
#    (pkts=[pkt1, pkt2, pkt3, pkt4, pkt5, pkt6]).
#
#    +--------------------------------------------------------------------------+
#    |                organize_msgs(pkts) -> output_tuple                       |
#    +--------------------------------------------------------------------------+
#    |                            (output_tuple)                                |
#    +-----------------------------------------+--------------------------------+
#    |           [message tuple list],         |     [leftover packet list]     |
#    +--------------------+--------------------+--------------------------------+
#    |    (msg tuple1),   |    (msg tuple2)    | leftover pkt5, | leftover pkt6 |
#    +-------+------------+-------+------------+--------------------------------+
#    | type, | [pkt list] | type, | [pkt list] |                                |
#    +-------+------------+-------+------------+--------------------------------+
#    |       | pkt1, pkt2 |       | pkt3, pkt4 |                                |
#    +-------+------------+-------+------------+--------------------------------+
#
#    
#    In practice, simple use of these six packets would resemble:
#
#        >>> pkts = [pkt1, pkt2, pkt3, pkt4, pkt5, pkt6]
#        >>> msgs = organize_msgs(pkts)
#
#        >>> msgs[0] # message tuple list
#        >>> msgs[1] # leftover packet list
#
#        >>> msgs[0][0] # first message tuple
#        >>> msgs[0][1] # second message tuple
#
#        >>> msgs[1][0] # first leftover packet
#        >>> msgs[1][1] # second leftover packet
#
#        >>> msgs[0][0][0] # first message type
#        >>> msgs[0][1][0] # second message type
#
#        >>> msgs[0][0][1] # first message packet list
#        >>> msgs[0][0][1] # second message packet list
#
#        >>> for msg in msgs[0]:
#        >>>     print "received message type: %s" % msg[0]
#        >>>     print "comprised of packets: %s" % msg[1]
#
#        >>> print "..and was left with: %s" % msgs[1]
#    """
#    import copy
#
#    pkts = copy.deepcopy(pkts)
#    msgs = []
#    msg, leftovers = find_msg(pkts)
#    while msg is not None:
#        msgs.append((msg.type, msg._seq))
#        if 0 == len(leftovers):
#            break
#        else:
#            msg, leftovers = find_msg(leftovers)
#    return msgs, leftovers
#
#def list_keyids(s):
#    """Extract key target information from a string.
#
#    :Parameters:
#        - `s`: string to get key targets from
#
#    :Returns: list of key targets found in `s`
#
#    This function parses a string describing public key targets and returns a
#    formatted target list that suits `list_key_targets()`. `list_key_targets()`
#    is a support function that finds the desired key message and the applicable
#    part(s) of it. `parse_keyids()` simply determines a string pattern that
#    can communicate a list of targets.
#
#    Separate targets using double commas (``,,``)::
#       
#        "52173F06BF3E9588,, 9F6C5AAB67B39A06 ,, Pete Moss"
#        
#    Be more specific by using double colons (``::``) to combine a
#    primary signing key and a block leader::
#
#        "52173F06BF3E9588::Pete Moss,, 9F6C5AAB67B39A06::9F6C5AAB67B39A06"
#
#    See `list_key_targets()` for more on output format.
#
#    :note: Repetitions are ignored.
#    :note: Double-colons are only split once. '``KEYID``::' is
#        shorthand for '``KEYID``::``KEYID``', and user IDs which
#        include double colons may be preserved with '::' prependages.
#        For example, '::Weird UID (?!::%)' and
#        '``KEYID``::Weird UID (?!::%)' will both preserve
#        'Weird UID (?!::%)'.
#    """
#    ids = []
#    target_delim = ',,'
#    key_delim = '::'
#
#    for target in [t.strip() for t in s.split(target_delim)]:
#
#        if -1 != target.find(key_delim):
#            primary, leader = target.split(key_delim, 1)
#
#            if primary and leader:
#                t = (primary, leader)
#
#            elif primary:
#                t = (primary, None)
#
#            elif leader:
#                t = (None, leader)
#
#            if t not in ids:
#                ids.append(t)
#
#        elif target not in ids:
#            ids.append((None, target)) # None ~ unspecified primary
#
#    return ids
#
#
#def parse_keyids(s):
#    """Extract key target information from a string.
#
#    :Parameters:
#        - `s`: string to get key targets from
#
#    :Returns: list of key targets found in `s`
#
#    This function parses a string describing public key targets and returns a
#    formatted target list that suits `list_key_targets()`. `list_key_targets()`
#    is a support function that finds the desired key message and the applicable
#    part(s) of it. `parse_keyids()` simply determines a string pattern that
#    can communicate a list of targets.
#
#    Separate targets using double commas (``,,``)::
#       
#        "52173F06BF3E9588,, 9F6C5AAB67B39A06 ,, Pete Moss"
#        
#    Be more specific by using double colons (``::``) to combine a
#    primary signing key and a block leader::
#
#        "52173F06BF3E9588::Pete Moss,, 9F6C5AAB67B39A06::9F6C5AAB67B39A06"
#
#    See `list_key_targets()` for more on output format.
#
#    :note: Repetitions are ignored.
#    :note: Double-colons are only split once. '``KEYID``::' is
#        shorthand for '``KEYID``::``KEYID``', and user IDs which
#        include double colons may be preserved with '::' prependages.
#        For example, '::Weird UID (?!::%)' and
#        '``KEYID``::Weird UID (?!::%)' will both preserve
#        'Weird UID (?!::%)'.
#    """
#    ids = []
#    TARGET_DELIM = ',,'
#    KEY_DELIM = '::'
#
#    for target in [t.strip() for t in s.split(TARGET_DELIM)]:
#
#        if -1 != target.find(KEY_DELIM):
#            primary, leader = target.split(KEY_DELIM, 1)
#
#            if primary and leader:
#                t = (primary, leader)
#
#            elif primary:
#                t = (primary, None)
#
#            elif leader:
#                t = leader
#            #elif leader:
#            #    t = (None, leader)
#
#            if t not in ids:
#                ids.append(t)
#
#        elif target not in ids:
#            ids.append(target)
#
#    return ids
#
# Note to self: key IDs and user IDs cannot be used interchangeably in a block
# search - this would enable an attacker to use another's encrypting key ID as
# a user ID which could sneak the attacker's key into the encrypt-to list.
#def list_key_targets(key_d, keyids, mode='sign'):
#    """Retrieve a list of key messages and specified or implied key IDs.
#
#    :Parameters:
#        - `key_d`: key material - either a string, list of key
#          messages, or single key message instance
#        - `keyids`: list of strings or tuples identifying target key
#          messages (see `ID formats`_)
#        - `mode`: 'encrypt' or 'sign' limiting searches to pertinent
#          keys, default 'sign'
#
#    :Returns: list of tuples [(``keymsg``, [``target_keyids``]), ..]
#        where ``keymsg`` is a ``OpenPGP.message.KeyMsg.KeyMsg``
#        subclass instance and ``target_keyids`` is a list of key ID
#        hex strings matching keys suited to an operation `mode`.
#
#    The purpose of this function is to search a string (`key_d`) for
#    all keys (particular key packets) suited for some purpose (`mode`)
#    in key messages with at least one identifier in `keyids`. The idea
#    is that user IDs will identify key messages needed for some
#    purpose. Returning the appropriate keys in that key message is a
#    convenience which happens to match a useful keyword in
#    `OpenPGP.sap.api.encrypt_message()`.
#
#    To specify a particular key in a key message, use a
#    (``primary key ID``, ``target key ID``) tuple in `keyids`.
#
#    .. _ID formats:
#
#    ID formats
#
#        Key message IDs are key IDs, key fingerprints, complete user
#        IDs or user ID substrings. All key messages in `key_d` will
#        be searched for each ID in `keyids`. A sample `keyids` might look
#        like::
#
#            keyids = ['9CFBB7E5AE12E579',
#                      '228D8AB6CE7C6710318F3B3B52173F06BF3E9588',
#                      'Pete Moss <pmoss@earthlink.net>',
#                      'Smith']
#
#        To be more specific, use (``primary``, ``leader``) tuples,
#        where ``primary`` is the key ID or fingerprint of the primary
#        signing key and ``leader`` is the key ID, key fingerprint,
#        user ID, or user ID substring of the block leader in
#        question::
#
#            keyids = [('9CFBB7E5AE12E579', '9F6C5AAB67B39A06'),
#                      ('52173F06BF3E9588', 'Pete Moss'),
#                      '228D8AB6CE7C6710318F3B3B52173F06BF3E9588']
#        
#        Both single strings and tuples can be used in the same list.
#
#    :note: Storage searches disregard empty keyids, as may be found
#        in unassigned signature packets.
#    :note: To simply retrieve key messages containing some key or
#        user ID, let `mode` = 'sign' and disregard the accompanying
#        ``target_keyids`` list, empty or not (using 'sign' makes sure
#        that primary keys are included in the search, thereby including
#        all key messages).
#    :note: If an ID in `keyids` does not match a user ID, it will attempt
#        to match a key ID or fingerprint. All matching key IDs or
#        fingerprints in a key message will be returned, regardless of
#        their appropriateness for the given `mode`. This is a
#        lingering convenience that may/should disappear (it allows an
#        attacker to create a user ID value of a foreign key ID such
#        that the attacker's key message may show up in a list of
#        target key messages - use the tuple option to choose specific
#        keys safely).
#    :note: In other words, `mode` is only useful for working with
#        user IDs.
#    """
#    saplog = logging.getLogger("saplog")
#    key_targets = []
#    enc_algs = [ASYM_ELGAMAL_E, ASYM_ELGAMAL_EOS, ASYM_RSA_E, ASYM_RSA_EOS]
#    sig_algs = [ASYM_DSA, ASYM_ELGAMAL_EOS, ASYM_RSA_S, ASYM_RSA_EOS]
#    keymsgs = []
#
#    if isinstance(keyids, str) or isinstance(keyids, tuple):
#        keyids = [keyids] # accomodate singles
#
#    if not isinstance(key_d, list):
#        key_d = [key_d]
#
#    for k in key_d:
#
#        #if isinstance(k, MSG.KeyMsg.KeyMsg):
#        if hasattr(k, 'new_primary'): # tmp solution, new_primary is an OK id
#            keymsgs.append(k)
#
#        #elif isinstance(k, STORAGE.Storage):
#        elif hasattr(k, 'get_keymsgs'):
#
#            if mode in ['encrypt', 'verify']:
#                searches = {'keytype':"public"}
#
#            elif mode in ['decrypt', 'sign']:
#                searches = {'keytype':"private"}
#
#            else:
#                raise Hell
#            
#            # it's possible that a keyid is '' or none, ignore those for now
#            for keyid in [i for i in keyids if i]: # yo, i is better than k
#
#                if isinstance(keyid, tuple):
#                    searches['keyid'] = keyid[0] # dismiss second component
#
#                else:
#                    searches['keyid'] = keyid
#
#                keymsgs.extend(k.get_keymsgs(**searches))
#            
#        else:
#            keymsgs.extend(targets2msgs(k, MSG_KEYS))
#
#    if keymsgs:
#        # match key algorithm & mode
#        l_m = lambda m, k, a: m == mode and k.body.alg in a
#        # if mode=encrypt & "is encrypting key" or mode=sign & "is signing key"
#        l_n = lambda k: l_m('encrypt', k, enc_algs) or l_m('sign', k, sig_algs)
#        # match either tuple value if not represented in list
#        l_o = lambda m, t: (m == t[1] or m == t[0])
#        # check if tuple format just specifies primary (several ways)
#        l_p = lambda t: 1 == len(t) or t[0] == t[1] or None == t[1]
#
#        for keymsg in keymsgs:
#
#            m_keyids = [] # matching IDs per keymsg
#            keymap = keymsg.map_keyprints() # [(fprint, keyid), ..]
#            uids = keymsg._b_userids.keys()
#            allkeys = [b.leader for b in keymsg._b_subkeys.list()] # favor..
#            allkeys.append(keymsg._b_primary.leader) # ..subkeys before primary
#
#            for keyid in keyids:
#
#                if isinstance(keyid, tuple): # (primary, leader)
#
#                    # match primary ID or fprint
#                    if l_o(keyid[0], keymap[0]):
#
#                        # check for primary redundancy - keyid is (ID,ID)
#                        if l_p(keyid) and keymap[0][1] not in m_keyids:
#                            m_keyids.append(keymap[0][1])
#                            continue
#
#                        else:
#                            keyid = keyid[1] # pass on leader to matching below
#                    else:
#                        continue # primary didn't match, move on to next keyid
#                
#                if isinstance(keyid, str): # NOT elif: catches else:keyid above
#                    m = None
#
#                    # check user IDs
#                    if [u for u in uids if keyid in u]: # simple substring match
#
#                        for k in allkeys:
#
#                            if l_n(k) and k.body.id not in m_keyids:
#                                m_keyids.append(k.body.id)
#
#                    else: # check key fingerprints and IDs
#                        keyid_up = keyid.upper()
#
#                        for tup in keymap:
#
#                            if l_o(keyid_up, tup) and keyid_up not in m_keyids:
#                                m_keyids.append(tup[1]) # keep adding matches
#
#            if m_keyids:
#                key_targets.append((keymsg, m_keyids))
#    else:
#        saplog.warn("No key material is available. Check key file.")
#
#    return key_targets
#
