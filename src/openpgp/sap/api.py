"""Main implementation functions

Status:

  - string functions 95%, awaiting polish and more use
  - instance functions 90%, pending packet/message class overhaul
  - documentation 80%, waiting for usage/demos
  - tests 60%, need more tests for failure, attacks, and stress

Deliteral-izing
---------------
Deliteral-ization via the 'deliteral' keyword is available in string-like
contexts (*_str()). The philosophy goes like this: in a message-like context
(*_msg()) the literal message is as low as you can go, but in a string-like
context, you might expect to go a little lower. What this should look like is
debateable, since literal data packets hold filename, type, and modification
time along with the actual data. To maintain the return-as-string motif in
*_str() functions, the literal data is return as "text headers" as they might
expect to be found near the top of a clearsigned message.

Multiple OpenPGP Messages in a Single File
------------------------------------------
There is nothing restricting the number of legal OpenPGP messages in a single
file, though in practice we normally find only one message per file. Keyrings
are exceptions to this since a number of public or private keys are normally
kept together in a single file. The "raw" functions allow for multiple messages
(signed, encrypted, etc.) in a single file.  However, since the identification
of individual messages sharing one file is sketchy, this is discouraged and
output may be difficult to make sense of.

Unbound private subkeys
-----------------------
Across implementations, subkeys are not always bound in the private key
message. Unbound subkeys do not constitute part of a valid key message and
remain unrecognized in this implementation. Make sure all subkeys are bound if
you want to do anything with them.

:todo: All verification functions should accept an explicit time to verify
    against. Right now they just verify against the current time.
"""
import time # get rid of this in favor of hands on _cmp_expiration()

import logging

from os import linesep

from openpgp.code import *

import openpgp.sap.crypto as CRYPT

from openpgp.sap.exceptions import *

from list import list_as_signed, list_msgs, find_keys, find_key_prefs, deliteralize
from armory import looks_armored, list_armored, apply_armor
from pkt.Packet import create_Packet
from pkt.CompressedData import create_CompressedDataBody
from pkt.Signature import Signature
from pkt.Signature import create_SignatureSubpacket as create_SigSub
from pkt.OnePassSignature import create_OnePassSignatureBody
from msg.Msg import Msg
from msg.LiteralMsg import create_LiteralMsg
from util.strnum import hex2int

# For the sake of a complete log, the loops don't terminate in case there is
# more than one match.
# 12.1: If an implementation can decrypt a message that a keyholder doesn't
#   have in their preferences, the implementation SHOULD decrypt the message
#   anyway, but MUST warn the keyholder that the protocol has been violated.
def decrypt_msg(encmsg, **kw):
    """Decrypt an encrypted message.

    :Parameters:
        - `encmsg`: `openpgp.sap.pkt.EncryptedMsg.EncryptedMsg` instance

    :Keywords:
        - `passphrase`: string passphrase used to decrypt the private `key`
          (if publicly encrypted) or the symmetric key used to decrypt
          `encmsg` directly (if symmetrically encrypted)
        - `key`: decryption key (`msg.KeyMsg.PrivateKey` instance)
        - `decompress`: set to True to automatically strip a compressed message
          wrapper from decrypted material (otherwise, you must handle the
          possibility of working with a decrypted compressed message)

    :Returns: decrypted message (`openpgp.sap.msg.Msg.Msg` subclass instance)

    :note: According to RFC 2440 10.2, an encrypted message should yield only
        one OpenPGP message when decrypted (although it is possible for other
        messages to be embedded withing the single decrypted message). This is
        enforced here since oring everything but the first valid message found in the decrypted data.
    """
    passphrase = kw.get('passphrase')
    keymsg = kw.get('key')
    decomp = kw.get('decompress')
    clrmsg = None
    errmsg = '' # store exception information from bypassed failures in loops

    if encmsg.targets: # gather session key packets
        encpub = [p for p in encmsg.targets if PKT_PUBKEYSESKEY == p.tag.type]
        encsym = [p for p in encmsg.targets if PKT_SYMKEYSESKEY == p.tag.type]

    else: # defaults if no session packets exist?
        raise NotImplementedError("Unable to decrypt w/out a session packet.")

    if keymsg and encpub:
        keyids = keymsg.list_keyids()

        for keyid, sespkt in [(i,pkt) for i in keyids for pkt in encpub]:

            if keyid == sespkt.body.keyid:
                keypkt = keymsg.get_keypkt(keyid)

                try: # continue upon failure, a following target may work
                    clrmsg = CRYPT.decrypt(encmsg.encrypted, passphrase, sespkt, keypkt)
                    break

                except PGPCryptoError, m:
                    errmsg = m

    if encsym and not clrmsg: # no need to duplicate decryption

        for sespkt in encsym:

            try: # continue upon failure, a following target may work
                clrmsg = CRYPT.decrypt(encmsg.encrypted, passphrase, sespkt)
                break

            except PGPCryptoError, m:
                errmsg = m

    if clrmsg: # (should go together without question)
        return list_as_signed(clrmsg, decompress=decomp)[0]

    else: # previous errors may have been suppressed
        raise PGPCryptoError(errmsg or "Decryption failed. Check decryption key.")

# Perhaps loop over session keys instead of assuming key_d == public sessions.
def decrypt_str(cphtxt, **kw):
    """Decrypt OpenPGP-encrypted data.

    :Parameters:
        - `cphtxt`: ciphertext string to decrypt

    :Keywords:
        - `passphrase`: string decryption passphrase (for either symmetric key
          encrypted ciphertext or protected decryption key)
        - `keys`: native OpenPGP or ASCII-armored string containing private
          (decryption) keys
        - `decompress`: set to True to automatically strip compressed material
          (output uncompressed string)
        - `deliteral`: set to True to automatically string-ify literal data
          (output literal packet information as headers and data)
        - `armor`: set to True to armor decrypted string output

    :Returns: str cleartext
    """
    output = ''
    # kw['passphrase'] passed to decrypt_msg()
    keystring = kw.pop('keys', '')
    # kw['decompress'] passed to decrypt_msg()
    delit = kw.pop('deliteral', False)
    armor = kw.pop('armor', False)
    encmsgs = _filter_msgs(list_as_signed(cphtxt), [MSG_ENCRYPTED])
    keys = _filter_msgs(list_as_signed(keystring), MSG_KEYS)
    clrmsgs = []

    if keys:

        for encmsg in encmsgs:
            success = False

            for key in keys:
                clrmsg = decrypt_msg(encmsg, key=key, **kw)
                clrmsgs.append(clrmsg)
                success = True
                break # per message, we only need one

            if success:
                break # ..like I said.. (need a "break 2" or something)

    else:

        for encmsg in encmsgs:
            clrmsg = decrypt_msg(encmsg, **kw)
            clrmsgs.append(clrmsg)
            success = True

    if delit:
        clrmsgs = deliteralize(clrmsgs)

    if armor:
        # exempt text from armoring
        #armored = []
        #for clrmsg in clrmsgs:
        #    if hasattr(clrmsg, 'rawstr'):
        #        clrmsg = apply_armor(clrmsg)
        #    armored.append(clrmsg)
        armored = [apply_armor(clrmsg) for clrmsg in clrmsgs]
        output = linesep.join(armored)

    else:
        #output = ''.join([clrmsg.rawstr() for clrmsg in clrmsgs])
        outlist = [] # clrmsgs might be text, so..

        for clrmsg in clrmsgs:

            if hasattr(clrmsg, 'rawstr'):
                clrmsg = clrmsg.rawstr()

            outlist.append(clrmsg)

        output = ''.join(outlist)

    return output


def encrypt_msg(msg, **kw):
    """Create an OpenPGP encrypted message.

    :Parameters:
        - `msg`: message instance to encrypt

    :Keywords:
        - `passphrase`: *optional* symmetric encryption passphrase
        - `keys`: *optional* list of tuples (``key``, [``keyids``]) to encrypt
          to. ``key`` is an `msg.KeyMsg.KeyMsg` instance and ``keyids`` is
          a list of strings identifying target encryption keys in ``key``

    :Returns: encrypted message instance

    :note: Since symmetric encryption does not consider algorithm
        preferences specified in public key messages, it does not use
        any compression. For safety reasons (for the time being), if a
        symmetric passphrase is used, public keys will be ignored.
    :note: The entire `keymsg` is needed to validate the encryption key(s) in
        question and sort out encryption and hashing preferences. Allowing
        multiple encryption keys per key message covers the range of
        possibilities (I think).
    :note: This function has nothing to do with user IDs. A function that
        retrieves keys or sends messages based on user IDs should check
        validity independently.
    :note: Even though the only thing encrypted is a string, a message instance
        is used to ensure that decrypted data is a message.
    """
    saplog = logging.getLogger('saplog')
    passphrase = kw.get('passphrase', '')
    keytargets = kw.get('keys')
    pkts = []
    # default MUSTs 12.1 says SYM_DES3 is an implied preference
    alg_sym, alg_hash, alg_comp = SYM_DES3, HASH_SHA1, COMP_UNCOMPRESSED

    if 'passphrase' in kw: # set symmetric if 'passphrase' keyword exists at all
        sespkt = CRYPT.encrypt_symmetric_session(alg_sym)
        enckey = CRYPT.string2key(sespkt.body.s2k, alg_sym, passphrase)
        pkts.append(sespkt)

    elif keytargets: # set public session keys
        preferred = find_key_prefs([p[0] for p in keytargets])

        if preferred['sym']:
            alg_sym = preferred['sym'][0]

        if preferred['hash']:
            alg_hash = preferred['hash'][0]

        if preferred['comp']:
            alg_comp = preferred['comp'][0]

        enckey = CRYPT.gen_random(CRYPT._keysize(alg_sym))

        for keymsg, targets in keytargets:

            for target in targets:

                if verify_block(keymsg, 'key', target):
                    keypkt = keymsg.get_keypkt(target)
                    sespkt = CRYPT.encrypt_public_session(keypkt, enckey, alg_sym)
                    pkts.append(sespkt)

                else:
                    saplog.warn("Skipping unbound Encryption key %s::%s." % (keymsg.primary_id, target))

    # create encrypted message
    if pkts:
        d_string = msg.rawstr()

        if alg_comp != COMP_UNCOMPRESSED: # compress msg string, if allowed
            compbody = create_CompressedDataBody(alg_comp, d_string)
            comppkt = create_Packet(PKT_COMPRESSED, compbody._d)
            d_string = comppkt.rawstr()

        encpkt = CRYPT.encrypt_integrity(alg_sym, enckey, d_string)
        pkts.append(encpkt)
        encmsg = list_msgs(pkts)[0]
        saplog.info("Encrypted message to %r recipients." % (len(pkts) - 1))

        return encmsg

    else:
        raise PGPError("No session keys created. Check target validity.")

def encrypt_str(clrtxt, **kw):
    """Encrypt a message with raw string data.

    :Parameters:
        - `clrtxt`: cleartext string to encrypt

    :Keywords:
        - `passphrase`: string symmetrical encryption passphrase
        - `keys`: native OpenPGP or ASCII-armored string containing public keys
        - `use_key`: [(primary, keyid), ..] specific encryption key(s)
        - `use_userid`: [(primary, userid), ..] encryption key(s) by user ID(s)
        - `lit_filename`: name of literal cleartext (NOT output)
        - `lit_modified`: modification time of literal cleartext (NOT output)
        - `armor`: set to True to armor encrypted string output

    :Returns: str ciphertext

    Be sure to use one of either `target_key`, `target_userid`, or `passphrase`
    to prevent unintentional encryption (a PGPError is raised if neither of
    these are given).
    """
    keystring = kw.pop('keys', '')
    encrypting_key = kw.pop('use_key', None)
    encrypting_userid = kw.pop('use_userid', None)
    # kw['passphrase'] passed to encrypt_msg()
    lit_filename = kw.pop('lit_filename', 'cleartext')
    lit_modified = kw.pop('lit_modified', 0)
    armor = kw.pop('armor', False)

    keys = _filter_msgs(list_as_signed(keystring), MSG_KEYS)

    opts = {}

    if encrypting_key:
        opts['keyids'] = encrypting_key

    elif encrypting_userid:
        opts['userids'] = encrypting_userid

    elif 'passphrase' not in kw:
        raise PGPError("Please specify encryption key by user ID, key ID or fingerprint.")

    keytargets = find_keys(keys, action='encrypt', **opts)

    literal = {'data': clrtxt, 'format': "b",
               'filename': lit_filename,
               'modified': lit_modified}

    msg = create_LiteralMsg([literal])

    cphmsg = encrypt_msg(msg, keys=keytargets, **kw)

    if armor:
        output = apply_armor(cphmsg)

    else:
        output = cphmsg.rawstr()

    return output

# this uses new-style snap packets for easy attribute->stringification
#def gen_key_str(**kw):
#    """Generate a public/private key pair. DEMO ONLY.
#
#    :Keywords:
#        - `passphrase`: string passphrase
#        - `userid`: string user ID
#        - `dsa_prv`: tuple of private DSA values
#        - `dsa_pub`: tuple of public DSA values
#        - `elgamal_prv`: tuple of private ElGamal key values
#        - `elgamal_pub`: tuple of public ElGamal key values
#        - `armor`: set to True to amor output
#
#    :Returns: tuple (public key, private key)
#
#    Keys will be DSA/ElGamal. If no user ID is given, no user ID packet will
#    be bound to the primary DSA key.
#
#    :note: This is really for test convenience and demonstration purposes.
#    """
#    import openpgp.snap.pkt as Snappy
#
#    userid = kw['userid']


# Results in a one-pass signed message.
# For keys/user IDs only: EXPORTABLE TRUST REGEX KEYEXPIRES REVOKER SYMCODE
#   HASHCODE COMPCODE KEYSERV PRIMARYUID
# Unsupported: KEYFLAGS KEYSERVPREFS
#   FEATURES should prolly be left blank in the interest of exchange
# all messages are either 1pass or detached - including notary sigs
# which will be 1pass, literal, sig <- everything will be like that
# up to later sig machines to extract this information and use it
# however
#
# TODO ``nested-ness``: ???for wrapping a one-pass message with a
#    notary sig on preceeding sigs indicating a flat nest???
# TODO test for signing key other than the primary
# TODO test lone (not necessarily SIG_STANDALONE) signature packet from
#   'target' == None.
def sign_msg(sigtype, key, **kw):
    """Create a signed message or detached signature instance.

    :Parameters:
        - `sigtype`: integer signature type constant
        - `key`: signing key message `openpgp.sap.msg.KeyMsg.SecretKeyMsg`
          instance

    :Keywords:
        - `passphrase`: string passphrase for secret signing key
        - `target`: message to sign
        - `target_key`: TUP (primary, keyid) key ID or fingerprint of key packet in `target` key
        - `target_userid`: TUP (primary, uid) user ID or unambiguous substring thereof in `target` key
        - `hashed`: list of hashed signature subpacket (key, value) tuples
        - `unhashed`: list of unhashed signature subpacket (key, value) tuples
        - `use_key`: *optional* string hex key ID for specifying which signing
          subkey to use (default signer is the primary key)
        - `detach`: boolean, set to True to return a lone signature packet
          instance (default False)

    :Returns: `openpgp.sap.msg.SignedMsg.SignedMsg` or
        `openpgp.sap.pkt.Signature.Signature` instance, depending on whether or
        not the `detach` option was set

    A message (`target`) is signed and returned as a signed message. If the
    intent is to apply a signature to a public key message component (ex: a
    direct signature on a key or a certification binding a user ID to the
    primary key), send the key as the `target` and use either `target_key` or
    `userid` to specify which component to sign.

    In every case, the resulting signature packet (alone) can be retrieved
    using the optional keyword `detach`.

    Signature types and appropriate values
    --------------------------------------
    ``SIG_BINARY`` & ``SIG_TEXT`` sign a literal message or detatched string.

    Signatures on public key block leaders (primary signing keys, subkeys, user
    IDs and user attributes) require a public key message and appropriate
    target. These signatures include ``SIG_GENERIC``, ``SIG_PERSONA``,
    ``SIG_CASUAL``, ``SIG_POSITIVE``, ``SIG_SUBKEYBIND``, ``SIG_SUBKEYREVOC``,
    ``SIG_DIRECT``, and ``SIG_KEYREVOC``.

    **The following signature types are not implemented:** ``SIG_CERTREVOC``,
    ``SIG_STANDALONE``, ``SIG_TIMESTAMP``, and ``SIG_THIRDPARTY``.

    Signature subpacket values
    --------------------------
    - ``SIGSUB_CREATED``: (0x02, t) - time at which the signature was created,
      0 <= t <= 4294967295
    - ``SIGSUB_EXPIRES``: (0x03, t) - number of seconds after creation time for
      which signature remains valid, 0 <= t
    - ``SIGSUB_REVOCABLE``: (0x07, b) - whether or not the signature may be
      revoked, b is either True or False
    - ``SIGSUB_KEYEXPIRES``: (0x09, t) - number of seconds after creation that
      the applicable key is valid, 0 <= t
    - ``SIGSUB_REVOKER``: (0x0C, (c, a, f) - which key may revoke the
      signature, c:0x80 (for now), a:public key algorithm code, and
      f:40-character key fingerprint
    - ``SIGSUB_SIGNERID``: (0x10, i) - signing key's ID, i:16 octets key ID of
      signing key
    - ``SIGSUB_NOTE``: (0x14, (f, n, v)) - a notation on the signature (open to
      interpretation), n:notation name string, v:notation value string, f:list
      of notation flags (see rfc2440 5.2.3.16 for details) or None for default
      text notations (see `pkt.Signature.create_SignatureSubpacket`)
    - ``SIGSUB_POLICYURL``: (0x1A, p) - p:string URL containing signature
      policy information
    - ``SIGSUB_SIGNERUID``: (0x1C, i) - i:user ID string identifying the
      signing key
    - ``SIGSUB_REVOCREASON``: (0x1D, (c, r)) - c:reason code, r:str reason (see
      RFC 2440 5.2.3.23 for details)
    - ``SIGSUB_SIGTARGET``: (0x1F, (k, h, s)) - target this signature should be
      applied to (used only for signature types 0x30, 0x40, and 0x50), k:public
      key algorithm code, h:hash algorithm code, and s:hash of target signature packet

    'Hashed' subpacket information is protected (verifiable) by the signature
    itself while 'unhashed' subpackets remain unprotected (unverifiable).

    :note: Signature types and the contexts they are forced into are not
        necessarily regulated (for example, it may be possible to create an
        inappropriate type of signature for a given target). Errors may be
        noticed down the line, most likely during the creation of the signature
        hash. In any case, it's best to plan ahead.
    :note: The status of the private signing key may not be available within
        the signing key message (ex. a private signing subkey may not have a
        signature packet binding it to the primary). It is up to you the caller
        to handle this.
    """
    saplog = logging.getLogger('saplog')
    msg = kw.get('target')
    keyid = kw.get('use_key', key.primary_id)
    opts = {'passphrase':kw.get('passphrase')}
    hashed = kw.get('hashed') or []
    pending_unhashed = kw.get('unhashed', [])
    # get rid of certain overlapping subpacket types
    nonex = [0x14, 0x1c] # may exist in hashed and unhashed
    hashed_types = [x[0] for x in hashed] # subpacket x: (type, value)
    unhashed = []

    for p in pending_unhashed:

        if p[0] in hashed_types and p[0] in nonex:
            pass
        else:
            unhashed.append(p)

    # pack up subpacket instances
    opts['hashed_subpkts'] = [create_SigSub(x[0], x[1]) for x in hashed]
    opts['unhashed_subpkts'] = [create_SigSub(x[0], x[1]) for x in unhashed]

    if MSG_LITERAL == msg.type:
        s = ''.join([p.body.data for p in msg.literals])
        keypkt = key.get_keypkt(keyid)
        sigpkt = CRYPT.sign(sigtype, s, keypkt, **opts)
        # create one-pass packet
        op_opts = {'sigtype':sigtype,
                  'alg_hash':HASH_SHA1, # no MUSTs involved, take it easy
                  'alg_pubkey':key._b_primary.leader.body.alg,
                  'keyid':keyid,
                  'nest':1} # fix at 1 since not handling parallel sigs
        onepassbody = create_OnePassSignatureBody(op_opts)
        onepasspkt = create_Packet(PKT_ONEPASS, onepassbody._d)
        sigmsg = list_msgs([onepasspkt] + msg._seq + [sigpkt])[0]

    elif msg.type in MSG_KEYS:

        if 'target_userid' in kw:
            keytarget = kw['target_userid']
            blocktype = 'userid'

        elif 'target_key' in kw:
            keytarget = kw['target_key']
            blocktype = 'key'

        else:
            keytarget = msg.primary_fprint
            blocktype = 'key'

        block = msg.get_block(blocktype, keytarget)

        if block:
            keypkt = key.get_keypkt(keyid)
            opts['primary'] = msg._b_primary.leader
            sigpkt = CRYPT.sign(sigtype, block.leader, keypkt, **opts)
            block.add_sig(sigpkt) # now that the block has its new sigpkt..
            sigmsg = msg # ..the keymsg is the signed msg

        else:
            raise PGPError("Signature target was not found.")

    else:
        raise NotImplementedError("Unsupported message type->(%s)." % msg.type)

    if kw.get('detach'): # a lot of overhead just to end up with sigpkt
        return sigpkt
    else:
        return sigmsg

# REM: keep sigsub names up to date with the constants in code.py
def sign_str(sigtype, key, **kw):
    """Create a signed message or detached signature.

    :Parameters:
        - `sigtype`: (int) signature type code
        - `key`: (str) native or ASCII-armored private signing key

    :Keywords:
        - `target`: str signed data (may contain target key)
        - `target_key`: tuple (primary, keyid) key to sign
        - `target_userid`: tuple (primary, userid) user ID to sign
        - `use_key`: tuple (primary, keyid) signing key
        - `use_userid`: tuple (primary, userid) primary associated with
          user ID (user ID must be unambiguous, pointing to only one primary)
        - `passphrase`: str private signing key passphrase
        - `sig_signerid`: str key ID of signing key
        - `sig_created`: int timestamp when the signature was created
        - `sig_expires`: int timestamp when the signature itself will expire
        - `sig_keyexpires`: int timestamp past signature creation when the
          target key will expire
        - `sig_note`: list of (str name, str value) tuples
        - `sig_policyurl`: list of policy URL strings
        - `sig_revoker`: tuple (int class, int alg, str fprint) designating a
          foreign revoking key - 'class' should be '0x80' for now, 'alg' should
          be the integer code of the public key algorithm, and 'fprint' should
          be the 40-character hex fingerprint of the revocation key
        - `lit_filename`: str name of signed literal
        - `lit_modified`: int modification time of signed literal
        - `detach`: bool whether or not to return a detached signature
        - `armor`: set to True to armor string output

    :Returns: signed string

    Signature subpackets
    --------------------
    Signature subpackets are created using the ``sig_XXX`` keywords. All
    specifed signature subpackets will be hashed. By default, the signature
    creation time is hashed and the signing key ID is unhashed.

    :note: Yes, `use_key` looks redundant with respect to
        `sig_signerid`, but it felt better to leave things as is since the act
        of setting it should be explicit and a keyword like
        ``sig_signerid_bool`` sounded funny.
    :note: If no signing key is specified, the first primary in `keys` will be
        used.

    :todo: `use_userid` (primary, userid) specifier is redundant right now
        since the user ID is just used to identify a key message and
        `sign_msg()` will wind up using the primary anyway. The intent (todo)
        is to prefer a signing subkey over the primary.
    :todo: The entire `msg_d` string is used to create a single literal packet,
        that is, this function cannot sign multiple files sent as individual
        literals in a literal message. For the time being, this is probably
        good enough, but some option should exist to pack up multiple files in
        a single literal message.

    :see: `sign_msg()`
    """
    saplog = logging.getLogger("saplog")
    msg_d = kw.get('target', '')
    passwd = kw.get('passphrase')
    signing_userid = kw.get('use_userid') # (primary, uid)
    signing_key = kw.get('use_key') # (primary, keyid)
    detach = kw.get('detach') # can be passed silently
    lit_filename = kw.get('lit_filename', 'signed')
    lit_modified = kw.get('lit_modified', 0)
    armor = kw.pop('armor', False)
    msg = None
    opts = {}

    if signing_userid:
        opts['userids'] = [signing_userid]

    if signing_key:
        opts['keyids'] = [signing_key]

    keys = _filter_msgs(list_as_signed(key), MSG_KEYS)
    signers = find_keys(keys, action='sign', **opts)

    if 1 == len(signers):
        keymsg = signers[0][0] # signing key message
        keypkt = keymsg.get_keypkt(signers[0][1][0]) # get keypkt w/ fprint
        keyid = keypkt.body.id
        sigopts = {'use_key':keyid}
        target = kw.get('target')

        if target:
            sigopts['target_key'] = target # set prior to resolving message

        if passwd:
            sigopts['passphrase'] = passwd

        if True == detach:
            sigopts['detach'] = True

        # resolve subpackets
        sigopts['hashed'], sigopts['unhashed'] = [], []

        if 'sig_signerid' in kw:
            sigopts['hashed'].append((0x10, kw['sig_signerid']))

        if 'sig_created' in kw: # signature creation time
            sigopts['hashed'].append((0x02, kw['sig_created']))

        if 'sig_expires' in kw: # signature expiration
            sigopts['hashed'].append((0x03, kw['sig_expires']))

        if 'sig_keyexpires' in kw: # key expiration
            sigopts['hashed'].append((0x09, int(kw['sig_keyexpires'])))

        if 'sig_note' in kw: # signature notations

            for n, v in kw['sig_note']:

                if '@' not in n:
                    saplog.warn("Please use name@space when possible: %s" % n)

                sigopts['hashed'].append((0x14, (None, n.strip(), v.strip())))

        if 'sig_policyurl' in kw: # policy URL
            sigopts['hashed'].append((0x1A, kw['sig_policyurl']))

        if 'sig_revoker' in kw: # signature revoker
            code, alg, fprint = kw['sig_revoker']
            sigopts['hashed'].append((0x0C, (code, alg, fprint.strip())))

        # resolve signed target
        if sigtype in [SIG_BINARY, SIG_TEXT]:
            literal = {'data':msg_d, 'filename':lit_filename, 'modified':lit_modified}

            if SIG_BINARY == sigtype: #
                literal['format'] = 'b'

            elif SIG_TEXT == sigtype: #
                literal['format'] = 't'

            msg = create_LiteralMsg([literal])

        else: # look for a key in the string
            targets = _filter_msgs(list_as_signed(msg_d), MSG_KEYS)
            target_userid = kw.get('target_userid') # (primary, uid)
            target_key = kw.get('target_key') # (primary, keyid)
            opts = {}

            if target_userid:
                opts['userids'] = [target_userid]
                sigopts['target_userid'] = target_userid[1]

            elif target_key:
                opts['keyids'] = [target_key]
                sigopts['target_key'] = target_key[1]

            targets = find_keys(targets, **opts)

            if targets:
                msg = targets[0][0] # force sig on first only

        if not msg:
            raise PGPError("Did not find anything to sign. Check your targets.")

        sigopts['target'] = msg
        signed = sign_msg(sigtype, keymsg, **sigopts)


        if armor:
            return apply_armor(signed)

        else:

            return signed.rawstr()

    elif 1 < len(signers):
        raise PGPError("Ambiguous signer. Please be more specific.")

    else:
        raise PGPError("No signing keys found. Check key, user ID.")

# The loops do not terminate once a suitable item is found. If the list is
# small, no big deal anyway. If the list is large, this allows for the
# possibility of multiple matches. An improvement might be to pop out sigs
# already used.
def verify_block(key, blocktype, target, **kw):
    """Determine whether a key block is appropriate for use.

    **This function might be scrapped or hidden):** can just use
    verify_msg(([pkt], key), signer) where pkt is the block leader in question.

    :Parameters:
        - `key`: public or private key message (`openpgp.sap.msg.KeyMsg.KeyMsg`
          subclass instance)
        - `blocktype`: 'key' or 'userid'
        - `target`: string key ID or (unambiguous) substring of a user ID
          value

    :Keywords:
        - `revocs`: list to which applicable revocation signature packets will
          be appended

    :Returns: True if verified, None otherwise. If keyword `revocs` is set and
        pending revocations exist, they will be appended to it.

    A "block" is a section of a key message that includes a leader (a signing
    key, encrypting key, user ID, or user attribute) and all of its bindings
    (foreign and local).

    This function verifies that a particular block leader in a key message
    is bound properly to the primary key and that the primary key itself is
    still valid. Only local revocations and expirations (or the absence
    thereof) are used to determine the existence and validity of the binding.

    A revoked primary key invalidates the bindings to every one of the key's
    user IDs, attributes, and subkeys.

    **A foreign revocation does not invalidate a binding** because the validity
    of it is beyond the scope of `key` being evaluated (think in terms of
    "proving a negative"). Use the optional `revocs` keyword parameter to
    gather foreign revocations for later processing. The existence of a foreign
    revocation means nothing in itself. It must be verified independently.

    Effective and pending revocations
    ---------------------------------
    A list sent as the optional `revocs` keyword parameter will have appended
    to it *effective* or *pending* revocation packets depending on the outcome
    (True or False) of this function.

    If this function returns True, all potentially valid foreign revocations
    will be added to the `revocs` list. If one signature in such a list
    verifies (independent of this function, that is), the block leader should
    be considered revoked. On the other hand, if this function returns False -
    `revocs` will hold the list of effective revocation signatures.

    A side effect is that if a key is revoked locally as well as by a
    foreign key, the foreign revocation will not show up in the effective
    revocations list.

    Algorithm
    ---------
    - if the block is not primary and a local binding does not exist or
      fails to verify, FAIL
    - if a local revocation exists and verifies, FAIL
    - if the block is a key block,

      - if a local direct signature asserts a key expiration, and the
        timestamp and signature check out, FAIL
      - if a foreign revocation exists and local revocation permission
        verifies, *append the foreign revocation to a list of pending
        revocations* (see `Effective and pending revocations`_)

    ...in either the local sigs in the key's block or the sig's
    in the primary key's block

    :note: Block verification has nothing to do with foreign "trust levels"
        (certifications) of user IDs and attributes since these have nothing to
        do with the relationship between the ID or attribute and the primary
        key; a foreign key cannot revoke the *validity* of an ID or attribute
        by making some assertion of trust.
    :note: This function does not consider foreign direct signatures attempting
        to "expire" a key via subpackets since RFC 2440 provides an explicit
        signature type to do this (my interpretation).
    :note: Keywords aren't used since I wanted it to be obvious that only one
        block could be verified at a time.

    :todo: User attributes are not supported yet since I don't know of a nice
        way to identify one in a list of them.
    """
    saplog = logging.getLogger("saplog")
    saplog.info("Checking block bindings..")

    block = key.get_block(blocktype, target)
    pending_revocs, effective_revocs = [], []
    verified = expired = revoked = False
    exempt = [PKT_PUBLICKEY, PKT_PRIVATEKEY]
    nonexempt = [PKT_PUBLICSUBKEY, PKT_PRIVATESUBKEY, PKT_USERID, PKT_USERATTR]
    key_types = exempt + [PKT_PUBLICSUBKEY, PKT_PRIVATESUBKEY]
    local_sigs = block.local_direct + block.local_bindings

    # check local bindings (is the block valid in the first place?)
    if block.type in exempt:
        verified = True # no bindings are required by default

    elif block.type in nonexempt: # check primary (a bad primary spoils the lot)
        l = [] # (potential) revocation holder
        verified_primary = verify_block(key, 'key', key.primary_fprint, revocs=l)

        if verified_primary:
            pending_revocs.extend(l)

        else:
            saplog.warn("The primary key has been revoked: the enitre key message invalid.")
            effective_revocs.extend(l)

        # continue either way to get a full report (remember verified_primary)
        if block.local_bindings:

            for sig in block.local_bindings:

                if _cmp_expiration(sig, SIGSUB_EXPIRES): # ignore expired sig
                    saplog.info("A local binding has expired (skipping verification).")

                elif CRYPT.verify(sig, block.leader, key._b_primary.leader):

                    if _cmp_expiration(sig, SIGSUB_KEYEXPIRES):
                        expired = True
                        effective_revocs.append(sig)
                        saplog.info("The key has expired.")

                    else:
                        saplog.info("The subkey was properly bound.")

                        if verified_primary:
                            verified = True # one good binding trumps all bad
                else:
                    saplog.warn("The subkey binding failed. Very suspicious.")
        else:
            saplog.warn("The sub-block is unbound. Very suspicious.")
    else:
        raise NotImplementedError("Block type->(%s) cannot be verified." % block.type)

    # check local revocations
    for sig in block.local_revocs: # assuming an outside revoc did not sneak in

        if CRYPT.verify(sig, block.leader, key._b_primary.leader):
            revoked = True
            saplog.info("The key was revoked locally.")
            effective_revocs.append(sig)

        else:
            saplog.warn("A local revocation signature failed. Very suspicious.")

    # check key expiration via direct signature
    if block.type in key_types:

        for sig in block.local_direct:

            if _cmp_expiration(sig, SIGSUB_KEYEXPIRES, block.leader.body.created):

                if CRYPT.verify(sig, block.leader, key._b_primary.leader):
                    expired = True
                    effective_revocs.append(sig)
                    saplog.info("The key has expired.")

    # check for foreign revocations and corresponding local authorization
    for revoker in block.foreign_revocs:
        local_auths = []

        for auth in local_sigs: # check for designated revoker permission

            for sub in auth.body.hashed_subpkts:

                if sub.type == SIGSUB_REVOKER:
        # Funny thing: key revoker subpackets specify the designated revoker's
        # *fingerprint,* but the revoker can only announce its *key ID* in the
        # signatures it issues.
                    if sub.value[2][-16:] == revoker.body.keyid:
                        local_auths.append(auth)

        if local_auths:

            for perm in local_auths:

                if CRYPT.verify(perm, block.leader, key._b_primary.leader):
                    pending_revocs.append(revoker) # no effect on verifcation
                    saplog.info("Found an unresolved outside revocation.")

                else:
                    saplog.warn("Failed to authorize a foreign revocation.")

        else: # then we have a rogue revocation packet
            saplog.warn("Found a rogue foreign revocation.")

    if True == verified and False == revoked and False == expired:
        saplog.info("Key verified successfully.")

        if 'revocs' in kw:
            kw['revocs'].extend(pending_revocs)

        return True

    else:
        saplog.info("Key failed to verify.")

        if 'revocs' in kw:
            kw['revocs'].extend(effective_revocs)

        return None

# Maybe a check_time=True option to reconcile revocations with respect to
# timestamps. If sig was made before (foreign) revocation time, don't add
# foreign revocations to the outlist. But note what's happening in the logs.
#
# There's a lot of room to eliminate repetition, especially if verify_block()
# is merged (only verify a block leader once, hang on to results of signatures
# used to verify blocks, etc.). Swapping out the signed tuple for a more
# flexible keyword option could help out as well.
def verify_msg(signed, key, **kw):
    """Check a signed message against the appropriate public key.

    :Parameters:
        - `signed`: signed message instance, or tuple ([list of signature
          packets], corresponding message) representing a detached signature
          (or list of signatures) on a particular message
        - `key`: key to verify against (public key)

    :Keywords:
        - `revocs`: list (probably empty) to which all pending foreign
          revocation signature packets will be appended (see `verify_block()`)
        - `signer_fprint`: fingerprint of signing key - use this to force
          validation against a particular key packet in `key`

    :Returns: message that was verified (packet instance, message instance, or
        string) or None if nothing was verified

    All signatures in a signed message (`signed`) are verified against a key
    message (`key`). All signatures made by `key` must succeed **and** at least
    one signature must succeed in order to return True. Unassigned signatures
    in a signed message are also checked against the key message: failures pass
    silently but a successful unassigned signature contributes to verification.

    A successful signature verifies algorithmically against a *valid* key in
    the specified signing key. 'valid' means that the signing key is properly
    bound to the primary key (if it is not the primary key itself) and has not
    been revoked locally (at any time, for any reason).

    Because this function verifies against only one signing key, it is
    impossible to verify (in the same step) any applicable foreign revocations
    on that signing key message. Therefore, *foreign revocations do not figure
    into the final verdict*. Instead, they are made available as loose ends to
    be resolved elsewhere via `revocs`.

    Grey matter: revocations and key validity
    -----------------------------------------
    The verified signed message definition is cautious, unambiguous, and easy
    to implement: verification of all signatures made by a revoked key will
    fail. This blantantly disregards two common aspects of revocation: the time
    at which the revocation was issued and the reason for the revocation. The
    rationale is that keys which have been revoked for any reason cannot be
    assumed to enjoy the same degree of security that valid, "live" keys do.

    Timestamps and revocation reasons are standard notations and no more than
    standard notations.

    Verifying key message signatures
    --------------------------------
    Signatures *within* a key message can be verified as detached signatures::

        verify_msg(([sigpkt1, ..], signed_key), signing_key)

    ..where the list of signature packets (``sigpkt1``, etc.) must be a list of
    signatures already in ``signed_key``. When verifying self-signatures, use
    the same instance for both the ``signed_key`` and the ``signing_key``.

    Unfortunately, in order to cover the possibility that the signature packet
    *instances* are not the same instances in the key, signatures are matched
    by raw string value.

    Standalone signatures
    ---------------------
    Standalone signatures can be verified by passing them as a detached
    signature with no target message::

        ([sigpkt], None)

    :note: This function does not address verification of key messages as a
        whole since the same thing can (and would be) accomplished using
        successive calls to `verify_block()`.
    :note: Because of the interpretation of 'verified', it is not possible to
        positively (return True) verify a local primary revocation packet
        because the signing block will verify False. The focus here with
        respect to 'validity' is on the effects of the signature packets
        (rather, the existence of "negative effects") rather than just the
        algorithmic validity of them.

    :todo: As is, signatures are verified against an entire key message and a
        particular key in that key message cannot be singled out for
        verification
    """
    saplog = logging.getLogger("saplog")
    signer_fprint = kw.get('signer_fprint', None)
    success = False # the goal is to set this to True
    opts = {}
    pending, revocs = [], []

    # package pending verifications, sigs & msg are verified, msg is returned
    if isinstance(signed, tuple):
        sigs, msg = signed

        if hasattr(msg, 'type') and msg.type in MSG_KEYS:
            opts['primary'] = msg._b_primary.leader
            blocks = msg.list_blocks()

            for sig in sigs: # match the sig with the appropriate block leader

                for b in blocks: # may as well skip block leaders ([1:])
                    # there should be a better way to match, see func docs
                    if [s for s in b.seq()[1:] if s.rawstr() == sig.rawstr()]:
                        pending.append((sig, b.leader))
                        break

            if not pending:
                raise PGPError("No matching signatures in the key message.")

        else:

            if hasattr(msg, 'type') and MSG_SIGNED == msg.type:
                # assume the sig is singled out for verification
                msg = msg.msg

            for sig in sigs: # handles all other messages and None (standalone)
                pending.append((sig, msg))

    elif signed.type == MSG_SIGNED: # should be a SignedMsg
        sigs, msg = signed.sigs, signed.msg

        for sig in sigs:
            pending.append((sig, msg))

    else:
        raise NotImplementedError("Unable to verify %s." % signed)

    assigned = ex_verified = im_verified = 0 # Explicit/implicit verification..
    # ..is needed so that all assigned signatures are accounted for by explicit
    # verification and that implicit verification does not excuse failures for
    # assigned signatures. It's not used for much now, could use for nice logs.

    # verify all pending
    for sig, target in pending:
        keypkt = None
        signer_id = sig.body.keyid

        if signer_fprint: # forced a signer to verify against
            keypkt = key.get_keypkt(signer_fprint)
            signer_id = signer_fprint # this is ugly: it's used to match up the
            # packet and ID in the 'if keypt:' verify_block() part below

        elif signer_id in key.list_keyids(): # discover an sig-asserted signer
            keypkt = key.get_keypkt(signer_id)

        if keypkt: # either the sigpkt specified a key or an fprint was forced
            assigned += 1

            if CRYPT.verify(sig, target, keypkt, **opts):
                saplog.info("Verified a signature from ID:%r." % signer_id)
                ex_verified += 1

                if _cmp_expiration(sig, SIGSUB_EXPIRES): # if sig expired..
                        saplog.info("..but the signature has expired.") #..abort

                elif verify_block(key, 'key', signer_id, revocs=revocs):
                    success = True

                else: # room for timestamp/reason for revocation exceptions
                    pass
            else:
                saplog.warn("A signature from ID:%r failed." % signer_id)

        elif not signer_id: # try to verify unassigned sig !! not just else: !!
            matches = find_keys([key], action='sign')

            if matches:
                saplog.warn("Attempting to verify an unassigned signature.")

                for keyid in matches[0][1]:
                    keypkt = key.get_keypkt(keyid)
                    v = False

                    try:
                        v = CRYPT.verify(sig, target, keypkt, **opts)
                    except PGPCryptoError:
                        pass # this doesn't have to verify

                    if v:
                        im_verified += 1

                        if verify_block(key, 'key', keyid, revocs=revocs):
                            success = True

    #if 0 == assigned:
    #    saplog.warn("No matching key ID was found in key %r." % key.primary_id)

    if revocs and 'revocs' in kw:
        kw['revocs'].extend(revocs)

    if True == success:

        # if everything assigned was verified OR it verified as unassigned
        if (assigned and assigned == ex_verified) or im_verified:
            return msg # message that was signed or the key message

def verify_str(signed, keys, **kw):
    """Verify signed a signed string.

    :Parameters:
        - `signed`: string containing signed messages or detached signatures
        - `keys`: string containing one or more public keys

    :Keywords:
        - `detached`: str detached data - outside data that may be the target
          of detached signatures
        - `armor`: set to True to armor encrypted string output

    :Returns: str all verified messages or None if they did not all verify

    This function verifies everything in `signed` on a single level (it does
    not attempt to verify the entire depth of a signed nest). Applicable key
    signatures are verified against `keys`.

    There supported formats for signed material are:

        - a signed message (defined in 10.2) (native or ASCII-armored)
        - a single signature packet (native or ASCII-armored), which may be
          applied to information in some external, "detached" string
        - a "clearsigned" ASCII-armored message
        - a public or private key (native or ASCII-armored)

    :note: Take care when verifying key messages. A positive return only
        accounts for those signatures which were signed by `keys`.
    :note: Revocations should be accessible. They're not.
    :note: If the verified messages (which will be returned) are going to come
        from clearsigned text, set armor=True. That way the output will still
        be valid. Otherwise the clear text (which is not wrapped in a literal)
        might munge a native OpenPGP string.

    :todo: Make revocations (as ``revocs``) accessible.
    """
    saplog = logging.getLogger("saplog")
    keys = _filter_msgs(list_as_signed(keys), MSG_KEYS)
    det = kw.get('detached')
    armor = kw.pop('armor', False)
    verified_msgs = []

    for signed in list_as_signed(signed, detached=det, decompress=True):
        verified = False

        if hasattr(signed, 'type') and signed.type in MSG_KEYS: # handle keys
            block_sigs = []

            for b in signed.list_blocks():
                block_sigs.extend(b.get_sigs()) # foreign sigs will be ignored

            signed = (block_sigs, signed) # set as detached for verify_msg()

        for key in keys:
            verified = verify_msg(signed, key)

            if verified:
                verified_msgs.append(verified)
                break

        if not verified: # went through all keys, something should've worked
            return False

    verified_out = []

    if verified_msgs:

        for v in verified_msgs:

            if hasattr(v, 'rawstr'):

                if armor:
                    verified_out.append(apply_armor(v))
                else:
                    verified_out.append(v.rawstr())

            else:
                verified_out.append(v)

        if armor:
            return linesep.join(verified_out)

        return ''.join(verified_out)

def _cmp_expiration(sig, subpkt_type, exp_base=None):
    """Compare a signature's expiration with the current time.

    :Parameters:
        - `sig`: `OpenPGP.packet.Signature` instance
        - `subpkt_type`: integer subpacket type constant, subpacket
          with expiration time (past creation) as value
        - `exp_base`: *optional* integer time base expirations from
          (use for key creation times)

    :Returns: False if no expiration or still good, True if expired

    :note: Only hashed subpackets are considered.
    """
    if 3 < sig.body.version: # only applies to v4+ sigs
        now = time.time()

        for expiration in [e for e in sig.body.hashed_subpkts if e.type == subpkt_type]:
            base_time = exp_base or sig.body.created

            if base_time + expiration.value < now:
                return True

    # v3 sigs don't have expiration, just move along
    return False

def _filter_msgs(msgs, msgtypes):
    f = lambda i: hasattr(i, 'type') and i.type in msgtypes
    return filter(f, msgs)

## Consider more ifs/thens to avoid setting redundant 'data' & 'armored_type'.
## if it outputs a list, it should handle a list in, to support
##   dicts = sap_out(decrypt_str(x,y,z))
#def sap_out(msg, filename, armored=False):
#    """Format "outgoing" OpenPGP messages.
#
#    :Parameters:
#        - `msg`: `openpgp.sap.msg.Msg` subclass instance or
#          `openpgp.sap.pkt.Signature.Signature` instance for detached
#          signatures
#        - `filename`: string requested output filename or None
#        - `armored`: boolean, whether or not to armor output (default
#          False)
#
#    :Returns: list of dictionaries containing file-like information
#
#    Given some kind of OpenPGP instance, this function prepares a
#    list of dictionaries, presumably for writing to a file (or
#    multiple files, keep reading).
#
#    File dictionary keys and values:
#        - `name`: string filename
#        - `data`: string file data
#
#    **Literal messages** yield one file per literal data packet and
#    ignore the `armored` parameter, since the output should not be
#    munged. Literal output tries to ignore the requested `filename`,
#    using it as a prependage to whatever filename has been given in
#    the literal packets.
#
#    **Compressed messages** assume that decompressed data yeilds a
#    *single* OpenPGP message (multiple literal packets count as a
#    single message) and are decompressed automatically, the results
#    are passed back to `sap_out()`.
#
#    **An arbitrary list of packets** will be output as such.
#    """
#    saplog = logging.getLogger("saplog")
#
#    if hasattr(msg, 'literals'): # is a LiteralMsg
#        f = []
#
#        for literal in msg.literals:
#            literal_name = literal.body.filename or 'literal'
#
#            if filename:
#                literal_name = "%s.%s"  % (filename, literal_name)
#
#            if '_CONSOLE' == literal_name:
#                saplog.warn("Passing over sensitive _CONSOLE file.")
#            else:
#                f.append({'name':literal_name, 'data':literal.body.data})
#
#        return f
#
#    elif hasattr(msg, 'compressed'): # is a CompressedMsg
#        saplog.info("Found compressed data, decompressing..")
#        decomp_msg = list_as_signed(msg.compressed.body.data)[0]
#
#        return sap_out(decomp_msg, filename, armored)
#
#    else:
#
#        if isinstance(msg, list): # arbitrary junk
#            saplog.warn("Creating absolute nonsense with %s packets." % len(msg))
#            data = ''.join([p.rawstr() for p in msg])
#            armored_type = 'junk'
#
#        else: # some other message or packet
#            data = msg.rawstr()
#
#            if isinstance(msg, Signature): # detached sig
#                armored_type = 'sig'
#
#            else:
#                armored_type = 'msg'
#
#                if hasattr(msg, 'primary_id'): # covers all key messages
#                    saplog.info("Recovered public key (ID: %r)" % msg.primary_id)
#
#        if armored:
#            data = apply_armor(msg) # can ditch "armored_type" above
#
#        return [{'name':filename, 'data':data}]
#

# Can of Worms (to be opened if SIG_CERTREVOC is allowed in key blocks):
#
# Revocations really should be made by nothing but the certifying or binding
# key. Because the information being certified/bound must be verified for use
# in the first place, the means to verify a revocation by that key will already
# exist - existence and verification of a single revocation packet is all that
# is required. In other words, the revocation is either good, bad, or
# non-existent.
#
# Verification of a revocation other than requires checking:
# 1) that it has been granted permission at all by either the
#   a) subkey's binding signature (from the primary key)
#   b) a direct signature from the primary key (in the subkey's block)
#   c) a direct signature on the primary key (in the primary key's block)
# 2) that the permission has not been revoked by
#   a) a certification revocation in the primary key's block
#   b) a certification revocation in the subkey's block
#   c) a certification revocation that itself was revoked by a
#      certification revocation (and on and on..)
# 3) that the revocation (and all of its dependencies) verifies.
#
# For keyserving purposes, revocations can not reliably be known to exist
# alongside the certifications they revoke. They should therefore exist for
# certain with the certifying key (not 'in' the certifying key). If a key
# message claims a certain certification, it should be willing to subject
# itself to further revocations made by the certifying key.
