"""Basic signing and encrypting functions

CFB
---
`crypt_CFB()` takes care of both encryption and decryption for all symmetric
algorithms. Unfortunately, this function is a hand-made CFB machine which
actually uses PyCrypto's ECB modes over and over again. This is because I
didn't get PyCrypto's ``MODE_PGP`` (or ``MODE_CFB``) to do what I wanted.
Another try is definitely warranted, but for now `crypt_CFB()` works so I'm
sticking with it.

Pseudo-random number generation 
-------------------------------
The pseudo-random number generator used is the RandomPool/get_bytes()
combination provided by `Crypto.Util.randpool`. These are wrapped in
`gen_random()`. By default, `gen_random()` uses 256 bytes of entropy
(RandomPool initialized with 256).

**No checks are performed on the entropy state.**

Public key padding (OAEP & EME-PKCS1-v1_5)
------------------------------------------
Padding for encrypted public key values is creating using `gen_random()`
*one bit at a time* using the default poolsize. This is *very slow* and may
suck the system's entropy dry. The length of the entire padded message (the
"intended length") is fixed at 127 for all algorithms, pending some deeper,
hopefully definitive insight into what the best number is for each algorithm
and why.

ElGamal "k" Values
------------------
..are generated automatically and left to be discarded. One option might be to
store a hash of the ``k`` value used, which will mean opening this function up.
For now, ``k`` is just forced to be a 128-bit prime.


:todo: There's a lot of StringIO silliness here, which was short-lived attempt
    at doing incremental read/writes which is being taken over in 'snap'. The
    silliness should be removed.
"""

import sha
import md5

from StringIO import StringIO

import Crypto.Util.number as NUM

from openpgp.code import *

import openpgp.sap.util.strnum as STN

from openpgp.sap.exceptions import *
from openpgp.sap.pkt import MPI
from openpgp.sap.pkt.Packet import create_Packet
from openpgp.sap.pkt.Signature import create_SignatureBody
from openpgp.sap.pkt.MPI import create_MPI

# TODO unhashed_subpkts should include SIGSUB_SIGNERID?
# TODO hashed_subpkts should include SIGSUB_CREATED?
# TODO turn lazy int2str()[0] into if/else checks?
def hash_context(version, hashalg, sigtype, sigcontext, target, primary):
    """Perform the signature hash.

    :Parameters:
        - `version`: int signature version
        - `hashalg`: int hash code
        - `sigtype`: int signature type
        - `sigcontext`: read()-able instance
        - `target`: "appropriate" target (packet, message, etc..)
        - `primary`: primary key packet

    :Returns: string message hash
    """
    context = StringIO()

    if primary:
        # verify secret key bindings w/ only public portion of the key
        if primary.tag.type in [PKT_PRIVATEKEY, PKT_PRIVATESUBKEY]:
            primary_body_d = primary.body._d[:primary.body._private_idx]
        else:
            primary_body_d = primary.body._d
        # calc spliced length by hand, get double oct representation
        primary_body_d_len = STN.int2quadoct(len(primary_body_d))[-2:]

    if sigtype in [SIG_BINARY, SIG_TEXT]:

        if hasattr(target, 'literals'): # literal message exception
            data = ''.join([x.body.data for x in target.literals])
        elif target:
            try: # ..to use the data that comprises the message
                data = target.rawstr()
            except AttributeError:
                data = str(target)
        else:
            raise NotImplementedError("Invalid signature target.")

        if SIG_TEXT == sigtype: # normalize, canonicalize, and strip
            data = data.replace('\r\n', '\n').replace('\n', '\r\n').strip()

        context.write(data)

    ## user ID sigs ..woulda thought cert revocs were on sig pkts
    elif sigtype in [SIG_GENERIC, SIG_PERSONA, SIG_CASUAL, SIG_POSITIVE,
                     SIG_CERTREVOC]:

        userpkt = target # user ID or user attribute packet
        context.write('\x99')
        context.write(primary_body_d_len)                       # bind primary
        context.write(primary_body_d)                           # len & str

        if version in [2, 3]:
            pass

        elif 4 == version:

            if PKT_USERID == userpkt.tag.type:                  # header
                context.write('\xb4')
            elif PKT_USERATTR == userpkt.tag.type:
                context.write('\xd1')
            elif PKT_SIGNATURE == userpkt.tag.type:
                raise NotImplementedError("Signature revocation(?) in a quandry.")
            else:
                raise NotImplementedError("Certifications only for user ID/attribute?")

            context.write(STN.int2quadoct(userpkt.length.size)) # length

        context.write(userpkt.body._d)                          # data

    ## key packet sigs
    elif sigtype in [SIG_SUBKEYBIND, SIG_SUBKEYREVOC, SIG_DIRECT]:

        keypkt = target # target key pkt, primary or otherwise

        if primary and primary != keypkt: # explicit primary (prevent doubles)
            context.write('\x99')
            context.write(primary_body_d_len)
            context.write(primary_body_d)

        # verify secret key bindings with only public portion of the key
        if keypkt.tag.type in [PKT_PRIVATEKEY, PKT_PRIVATESUBKEY]:
            keypkt_body_d = keypkt.body._d[:keypkt.body._private_idx]
        else:
            keypkt_body_d = keypkt.body._d

        context.write('\x99')
        context.write(STN.int2quadoct(len(keypkt_body_d))[-2:])
        context.write(keypkt_body_d)

    elif SIG_KEYREVOC == sigtype:
        context.write(target.rawstr()) # the key (packet) being revoked

    ## weird sigs
    elif SIG_STANDALONE == sigtype:
        raise NotImplementedError, "Haven't got around to SIG_STANDALONE"
    elif SIG_TIMESTAMP == sigtype:
        raise NotImplementedError, "Haven't got around to SIG_TIMESTAMP"
    elif SIG_THIRDPARTY == sigtype:
        raise NotImplementedError, "Haven't got around to SIG_THIRDPARTY"
    else:
        raise NotImplementedError, "Signature type->(%s) is not supported" % sigtype

    context.write(sigcontext.read())
    context.seek(0)

    try:
        if hashalg == HASH_MD5:
            import md5
            hashed_target = md5.new(context.read()).digest()
        elif hashalg == HASH_SHA1:
            import sha
            hashed_target = sha.new(context.read()).digest()
        else:
            raise NotImplementedError, "Unsupported signature hash algorithm->(%s)" % sig.alg_hash
    finally:
        context.close()

    return hashed_target

# see gnupg/g10/seskey.c:do_encode_md() and GnuPG Notes below
def pad_rsa(alg_hash, hashed_msg, rsa_n_bit_length):
    """Pad RSA signature hashed data with "full hash prefixes".

    :Parameters:
        - `alg_hash`: integer hash algorithm constant
        - `hashed_msg`: string of [already] hashed data
        - `rsa_n_bit_length`: integer RSA MPI "n" bit length
    
    :Returns: string hashed data padded according to rfc2440 5.2.2.
    """
    # "full hash prefixes"
    if HASH_MD5 == alg_hash:
        prefix = '\x30\x20\x30\x0C\x06\x08\x2A\x86\x48\x86\xF7\x0D\x02\x05\x05\x00\x04\x10'
    elif HASH_SHA1 == alg_hash:
        prefix = '\x30\x21\x30\x09\x06\x05\x2b\x0E\x03\x02\x1A\x05\x00\x04\x14'
    else:
        raise NotImplementedError, "Prefix unassigned for RSA signature hash->(%s)" % sig.alg_hash
    padlen = ((rsa_n_bit_length + 7)/8) - len(prefix) - len(hashed_msg) - 3
    padding = ''.join(['\xff' for x in range(padlen)])
    return ''.join(['\x00\x01', padding, '\x00', prefix, hashed_msg])

def sign(sigtype, target, signer, *args, **kwords):
    """Create a signature packet.

    :Parameters:
        - `sigtype`: integer signature type constant
        - `target`: variable type, message to sign
        - `signer`: private signing key packet instance

    :Keywords:
        - `passphrase`: string passphrase used to decrypt secret key
          values from `signer`
        - `primary`: `OpenPGP.packet.PublicKey.PublicKey` instance,
          needed if signature requires a primary key packet
        - `hashed_subpkts`: list of
          `OpenPGP.packet.Signature.SignatureSubpacket` instances
          to be included in the protected (hashed) portion of the
          signature
        - `unhashed_subpkts`: list of
          `OpenPGP.packet.Signature.SignatureSubpacket` instances
          to be included in the unprotected portion of the signature
        - `version`: integer signature version to force the
          signature version, this probably shouldn't be used at all
        - `created`: integer timestamp of signature creation, **v3
          signatures only**
        - `keyid`: string ID of signing key, **v3 signatures only**
        - `hashalg`: integer hash algorithm constant

    :Returns: signature packet instance

    Signature types (and `target` values)
    -------------------------------------
    - ``SIG_BINARY`` & ``SIG_TEXT`` requires `target` string or message
      instance (one of the `OpenPGP.message.Msg` subclasses)
    - ``SIG_GENERIC``, ``SIG_PERSONA``, ``SIG_CASUAL``, ``SIG_POSITIVE``
      requires `target` User ID or User Attribute packet, **requires**
      `primary` option
    - ``SIG_CERTREVOC`` requires `target` User ID or User Attribute packet and
      `primary` option (see `Cert revocation quirks`_)
    - ``SIG_SUBKEYBIND``, ``SIG_SUBKEYREVOC`` requires `target` PublicSubkey or
      SecretSubkey packet  **requires** `primary` option
    - ``SIG_DIRECT`` requires `target` PublicKey or PublicSubkey packet
      **requires** `primary` option **if** subkey is being signed
    - ``SIG_KEYREVOC`` requires `target` Public Key or Secret Key packet (no
      `primary` needed, already sent as `target`)
    - ``SIG_STANDALONE``: **not implemented** 
    - ``SIG_TIMESTAMP``: **not implemented**
    - ``SIG_THIRDPARTY``: **not implemented**

    Cert revocation quirks
    ----------------------
    I've only encountered certificate revocations as user ID/attribute
    revocations which, despite the draft, are calculated the same way as the
    generic, persona, etc. certifications; that is, the hash requires the user
    packet *and* the primary key packet.

    So it seems as though some extra voodoo is required for bona fide
    certification-as-signature revocations, which aren't implemented yet.
    
    :note: From here "on up," primary key infomation is gathered so long as it
        is accessible, whether or not it applies to the signature inquestion.
        The burden of reporting any missing information required to produce a
        signature is placed on `hash_message()`.
    """
    passphrase = kwords.get('passphrase') or ''
    version = kwords.get('version') or 4
    hashed_subpkts = kwords.get('hashed_subpkts') or [] # unhashed runs silent
    hashalg = kwords.get('hashalg') or HASH_SHA1
    primary = kwords.get('primary') or None
    keyalg = signer.body.alg

    try:
        seckey = decrypt_secret_key(signer, passphrase)[0] # only need first key
    except PGPFormatError, m:
        raise PGPFormatError("%s -check the decryption passphrase-" % m)


    int2str = STN.int2str
    ctx = StringIO() # signature context to hash
    ctx_write = ctx.write

    if 3 == version:                                     ################### v3
        ctx_write(int2str(sigtype)[0])                   # signature type
        ctx_write(int2str(kwords['created'])[:4])        # creation timestamp

    elif 4 == version:                                   ################### v4
        ctx_write('\x04')                                # version
        ctx_write(int2str(sigtype)[0])                   # signature type
        ctx_write(int2str(keyalg)[0])                    # public key alg
        ctx_write(int2str(hashalg)[0])                   # hash algorithm
        subhash = ''.join([x._d for x in hashed_subpkts])
        ctx_write(STN.prepad(2, int2str(len(subhash))))  # hashed len
        ctx_write(subhash)                               # hashed subpkts
        ctx_len = ctx.tell()
        ctx_write('\x04\xff')                            # start trailer
        ctx_write(STN.int2quadoct(ctx_len)[-4:])         # hashed data length
    
    else:
        raise NotImplementedError("Signature version->(%s) is not supported." % version)

    ctx.seek(0)
    ctx_hash = hash_context(version, hashalg, sigtype, ctx, target, primary)
    ctx.close()

    if keyalg in [ASYM_RSA_S, ASYM_RSA_EOS]:
        ctx_hash = pad_rsa(hashalg, ctx_hash, signer.body.RSA_n.bit_length)
        keytup = signer.body.RSA_n.value, seckey
        sigtup = sign_RSA(ctx_hash, keytup), # coerce tuple for sigtup-ling

    elif ASYM_ELGAMAL_EOS == keyalg:
        keytup = signer.body.ELGAMAL_p.value, signer.body.ELGAMAL_g.value, seckey
        sigtup = sign_ElGamal(ctx_hash, keytup)

    elif ASYM_DSA == keyalg:
        keytup = signer.body.DSA_y.value, signer.body.DSA_g.value, signer.body.DSA_p.value, signer.body.DSA_q.value, seckey
        sigtup = sign_DSA(ctx_hash, keytup)

    else:
        raise NotImplementedError("Public key alg->(%s) is not supported." % keyalg)

    kwords.update({'version':version, 'sigtype':sigtype, 'alg_pubkey':keyalg,
                   'alg_hash':hashalg, 'hash_frag':ctx_hash[:2],
                   'signature':[create_MPI(sigval) for sigval in sigtup]})

    body = create_SignatureBody(**kwords)

    return create_Packet(PKT_SIGNATURE, body._d)

def sign_DSA(msg, key_tuple, k=None):
    """Create a DSA signature.

    :Parameters:
        - `msg`: string of data signature applies to 
        - `key_tuple`: tuple of DSA integers (y, g, p, q, x)
          (see `DSA tuple`_)
        - `k`: random integer 2 < k < q (automatically generated by
          default)

    :Returns: tuple (integer, integer) DSA signature values (r, s)

    .. _DSA tuple:

    DSA tuple:

        - `y`: integer DSA public key
        - `g`: integer DSA group
        - `p`: integer DSA prime
        - `q`: integer DSA order
        - `x`: integer DSA secret value
    """
    import Crypto.PublicKey.DSA as DSA
    if k is None: # generate our own k value (2 < k < q)
        import Crypto.Util.number as NUM
        import Crypto.Util.randpool as RND
        rnd = RND.RandomPool()
        q = key_tuple[3]
        while 1:
            k = NUM.getRandomNumber(8*len(STN.int2str(q)), rnd.get_bytes)
            if 2 < k < q:
                break
    dsa = DSA.construct(key_tuple) # note change in ordering
    return dsa.sign(msg, k)

def sign_ElGamal(msg, key_tuple, k=None):
    """Create an ElGamal signature.

    :Parameters:
        - `msg`: string of data signature applies to 
        - `key_tuple`: tuple ElGamal key integers (p, g, x)
          (see `ElGamal key tuple`_)
        - `k`: integer (must be relatively prime to p-1)

    :Returns: tuple (integer, integer) ElGamal signature values (a, b)
    
    .. _ElGamal key tuple:

    ElGamal key tuple:
            
        - `p`: integer ElGamal prime
        - `g`: integer ElGamal random "g" value
        - `x`: integer ElGamal private key
    """
    import Crypto.PublicKey.ElGamal as ELG
    if k is None: # generate our own prime k value (k relatively prime to p-1)
        import Crypto.Util.number as NUM
        import Crypto.Util.randpool as RND
        rnd = RND.RandomPool()
        q = key_tuple[0] # no restrictions on bit length for k, good enough?
        k = NUM.getPrime(8*len(STN.int2str(q)), rnd.get_bytes)
    elg = ELG.construct((key_tuple[0], key_tuple[1], 0, key_tuple[2]))
    return elg.sign(msg, k)

def sign_RSA(msg, key_tuple):
    """Create a RSA signature.

    :Parameters:
        - `msg`: string of data signature applies to 
        - `key_tuple`: tuple RSA key integers (n, d)
          (see `RSA key tuple`_)

    :Returns: integer RSA signature value

    .. _RSA key tuple:

    RSA key tuple:

        - `n`: integer RSA product of primes p & q
        - `d`: integer RSA decryption key
    """
    import Crypto.PublicKey.RSA as RSA
    rsa = RSA.construct((key_tuple[0], 0L, key_tuple[1]))
    return rsa.sign(msg, None)[0]

def verify(signature, target, signer, *args, **kwords):
    """Verify a string and signature against a public key.

    :Parameters:
        - `signature`: `OpenPGP.packet.Signature.Signature` instance
          signature to verify
        - `target`: signed material (see `sign()` for details)
        - `signer`: verifying public key or public subkey packet instance

    :Keywords:
        - `primary`: `OpenPGP.packet.PublicKey.PublicKey` instance
          for signatures that use a primary key in the hash

    :Returns: integer 1 (successful verification) or 0 (failure)

    :note: If the signing key is a primary key packet, the keyword `primary`
        does not need to be given.
    """
    primary = kwords.get('primary')
    version = signature.body.version
    hashalg = signature.body.alg_hash
    sigtype = signature.body.type
    keyalg = signature.body.alg_pubkey

    if signer.body.alg != keyalg: # matching algs assumes correct MPI attrs
        raise PGPCryptoError("Signature alg %s did not match signing key alg %s" % (keyalg,signer.body.alg))

    if not primary and signer.tag.type in [PKT_PUBLICKEY, PKT_PRIVATEKEY]:
        primary = signer

    ctx = StringIO(signature.body.hashed_data)
    ctx_hash = hash_context(version, hashalg, sigtype, ctx, target, primary)
    ctx.close()
 
    if keyalg in [ASYM_RSA_EOS, ASYM_RSA_S, ASYM_ELGAMAL_EOS]: # not DSA
        ctx_hash = pad_rsa(hashalg, ctx_hash, signer.body.RSA_n.bit_length)

    key = signer.body
    sig = signature.body

    try: 

        if keyalg in [ASYM_RSA_S, ASYM_RSA_EOS]:
            keytup = key.RSA_n.value, key.RSA_e.value

        elif ASYM_ELGAMAL_EOS == keyalg:
            sigtup = sig.ELGAMAL_a.value, sig.ELGAMAL_b.value
            keytup = key.ELGAMAL_p.value, key.ELGAMAL_g.value, key.ELGAMAL_y.value

        elif ASYM_DSA == keyalg:
            sigtup = sig.DSA_r.value, sig.DSA_s.value
            keytup = key.DSA_y.value, key.DSA_g.value, key.DSA_p.value, key.DSA_q.value

    except AttributeError: # if sig alg != key alg, MPI attributes don't match
        raise AttributeError("Possible key/sig alg mismatch: sig alg->(%s) key alg->(%s)" % (keyalg, signer.body.alg))

    if keyalg in [ASYM_RSA_S, ASYM_RSA_EOS]:
        return verify_RSA(ctx_hash, sig.RSA.value, keytup)

    elif ASYM_ELGAMAL_EOS == keyalg:
        return verify_ElGamal(ctx_hash, sigtup, keytup)

    elif ASYM_DSA == keyalg:
        return verify_DSA(ctx_hash, sigtup, keytup)

    else:
        raise NotImplementedError, "Unsupported public key alg->(%s)." % key.alg_pubkey

def verify_DSA(msg, sig_tuple, key_tuple):
    """Verify a DSA signature.

    :Parameters:
        - `msg`: string of data signature applies to 
        - `sig_tuple`: tuple of DSA signature integers (r, s)
          (see `DSA signature tuple`_)
        - `key_tuple`: tuple of DSA key integers (y, g, p, q)
          (see `DSA key tuple`_)
    
    :Returns: integer 1 or 0, for verification true or false

    .. _DSA signature tuple:

    DSA signature tuple:

            - `r`: integer DSA "r"
            - `s`: integer DSA "s"
            
    .. _DSA key tuple:

    DSA key tuple:

            - `y`: integer DSA public key
            - `g`: integer DSA group
            - `p`: integer DSA prime
            - `q`: integer DSA order
    """
    import Crypto.PublicKey.DSA as DSA
    dsa = DSA.construct(key_tuple) # note change in ordering
    return dsa.verify(msg, sig_tuple)

def verify_ElGamal(msg, sig_tuple, key_tuple):
    """Verify an ElGamal signature.

    :Parameters:
        - `msg`: string of data signature applies to 
        - `sig_tuple`: tuple of ElGamal signature integers (a, b)
          (see `ElGamal signature tuple`_)
        - `key_tuple`: tuple of ElGamal key integers (p, g, y)
          (see `ElGamal key tuple`_)

    :Returns: tuple (integer, None) where integer == 1 or 0, verification
        true or false
    
    .. _ElGamal signature tuple:

    ElGamal signature tuple:
            
        - `a`: integer ElGamal "a"
        - `b`: integer ElGamal "b"
            
    .. _ElGamal key tuple:

    ElGamal key tuple:
            
        - `p`: integer ElGamal prime
        - `g`: integer ElGamal group
        - `y`: integer ElGamal public key
    """
    import Crypto.PublicKey.ElGamal as ELG
    elg = ELG.construct(key_tuple) # note change in ordering
    return elg.verify(msg, sig_tuple)

def verify_RSA(msg, sig, key_tuple):
    """Verify a RSA signature.

    :Parameters:
        - `msg`: string of data signature applies to 
        - `sig`: integer RSA signature (RSA ciphertext)
        - `key_tuple`: tuple RSA key integers (n, e)
          (see `RSA key tuple`_)

    :Returns: tuple (integer, None) where integer == 1 or 0, verification
        true or false
    
    .. _RSA key tuple:

    RSA key tuple:

            - `n`: integer product rsa_p * rsa_q
            - `e`: integer RSA encryption key
    """
    import Crypto.PublicKey.RSA as RSA
    n = long(key_tuple[0]) # long() takes care of fastmath deps
    e = long(key_tuple[1])
    rsa = RSA.construct((n, e))
    return rsa.verify(msg, (sig,))

# GnuPG Signatures
# ----------------
#
# sig-check.c:check_key_signature2() is a good place to start looking for
# signature quirks.
#
# GnuPG V3 RSA Signatures
# -----------------------
# 
# The construction of the funky ASN.1 structure is handled in 
# g10/seskey.c:do_encode_md(). From the functions commentary:
#
#   /* We encode the MD in this way:
#    *
#    * 0  A PAD(n bytes)   0  ASN(asnlen bytes)  MD(len bytes)
#    *
#    * PAD consists of FF bytes.
#    */
#
# Which looks a little different from rfc2437 9.2.1:
#
#   5. Concatenate PS, the DER encoding T, and other padding to form
#      the encoded message EM as: EM = 01 || PS || 00 || T
#
# ..where T is ASN + MD and PS is the \xff padding.
#
# I did a dump of gpg's signature verification and the 'frame' that
# was constructed looked like:
#
#   \x00\x01\xff\xff ..(a bunch more \xff).. \x00
#   ..\x30\x21\x30\x09 ..(the SHA-1 "full hash prefix" from bis08 5.2.2)
#   ..\xAA\xBB\xCC.. (20 characters worth of the SHA-1 hashed data)
#
# ..which differed from GnuPG's commentary in that there was a \x01 between
# the first \x00 and the padding, and differed from rfc2437 9.2.1 which
# didn't mention the preceding \x00 (perhaps it's found elsewhere in ASN.1
# lore). In any case, the pattern I finally got to verify looked like:
#
#   sigdata = '\x00\x01' + PS + '\x00' + prefix + msg
#   SIGN(sigdata)
#
# for msg = HASH(data + siginfo), prefix = "full hash prefix," and
# PS = the same count of \xff from gpg --verify output.
#
# GnuPG calculates the number of padding (\xff) octets like this:
#
#   i = nframe - len - asnlen -3 ;
#   assert( i > 1 );
#   memset( frame+n, 0xff, i );
#
# where 
#  
#   nbits = mpi_get_nbits(pk->pkey[0])
#   nframe = (nbits+7) / 8 
#   len = number of octets in message digest (SHA1:20)
#   asnlen = number of octets in "full hash prefix" (SHA1:15)
#
# nbits = 1024 in the verification test performed, and without digging
# further into the structures, I'm assuming that this value refers to
# the number of bits in the RSA "n" (public modulus) value (I'm guessing
# that the "e"xponent value is always tiny in comparison).
# 
# The verbage in rfc2437 9.2.1 is pretty wishy on this, using terms like
# "intended length of encoded message." Anyway, it's nice to see something
# working.


def _import_cipher(algorithm):
    """Convenience function that returns cipher module.

    :Parameters:
        - `algorithm`: integer cipher algorithm constant

    :Returns: PyCrypto cipher module
    """
    if SYM_IDEA == algorithm:
        from Crypto.Cipher import IDEA
        return IDEA
    elif SYM_DES3 == algorithm:
        from Crypto.Cipher import DES3
        return DES3
    elif SYM_CAST5 == algorithm:
        from Crypto.Cipher import CAST
        return CAST
    elif SYM_BLOWFISH == algorithm:
        from Crypto.Cipher import Blowfish
        return Blowfish
    elif algorithm in [SYM_AES128, SYM_AES192, SYM_AES256]:
        from Crypto.Cipher import AES
        return AES
    else:
        raise NotImplementedError, "Can't handle cipher type->(%s)" % algorithm

def _keysize(algorithm):
    if algorithm in [SYM_CAST5, SYM_BLOWFISH, SYM_AES128]:
        return 16
    elif algorithm in [SYM_DES3, SYM_AES192]:
        return 24
    elif SYM_AES256 == algorithm:
        return 32
    else:
        raise NotImplementedError, "Unsupported symmetric key algorithm->(%s). Using GnuPG DUMMY?" % algorithm

# The CFB block-size shifts depend on PyCrypto's predefined block size
# per cipher. This function should be swapped out asap.
#def crypt_CFB(algorithm, key, instream, register, direction):
def crypt_CFB(instream, outstream, algorithm, key, register, direction):
    """'Crypt a string in cipher-feedback mode.

    :Parameters:
        - `instream`: StringIO/file incoming
        - `outstream`: StringIO/file outgoing
        - `algorithm`: integer symmetric cipher constant
        - `key`: string encryption/decryption key
        - `register`: string initialization vector (IV) to feed register
        - `direction`: string 'encrypt' or 'decrypt' setting CFB mode

    :Returns: string ciphertext or cleartext

    OpenPGP performs CFB shifts on blocks of characters the same size
    as the block used by the symmetric cipher - for example, CAST5
    works on 64-bit blocks, therefore CAST5 CFB shifts use 8 bytes at
    a time (the remaining cleartext bytes that do not completely fill
    an 8-byte block at the end of a message are XOR'ed with the
    "left-most" bytes of the encrypted mask).
    """
    ciphermod = _import_cipher(algorithm)
    cipher = ciphermod.new(key, ciphermod.MODE_ECB)
    encrypt = cipher.encrypt
    shift = ciphermod.block_size # number of bytes to process (normally 8)

    # after tweaking, there's still not much difference in speed (~2% max)
    int2str = STN.int2str
    str2int = STN.str2int
    apply_mask = lambda c,m: int2str(str2int(c) ^ str2int(m))
 
    if register is None:
        register = STN.prepad(shift) # use an IV full of 0x00

    if shift > len(register):
        raise PGPCryptoError, "CFB shift amount->(%s) can't be larger than the feedback register->(%s)." % (shift, len(register))
  
    while True:
        inblock = instream.read(shift) # block size = shift size
        chunk = StringIO()

        if inblock:
            mask = encrypt(register)
            chunk.seek(0)

            for i, c in enumerate(inblock):
                chunk.write(apply_mask(c, mask[i]))

            chunk.truncate()
            chunk.seek(0)
            outblock = chunk.read()

            if 'encrypt' == direction:
                register = outblock
            elif 'decrypt' == direction:
                register = inblock

            outstream.write(outblock)

        else:
            break

# A common function could be used for MPI parsing, but then it would have to
# maintain (non-existent) secure data handling as well.
# Integrity Protected Ugliness - bytes are reserved for the MDC to counter
# preceding packets with undefined length. This is inextricably tied to the
# SHA1 requirement of v1 integrity & MDC packets.
# TODO We could use some condensing here.
def decrypt(encpkt, passphrase='', sespkt=None, keypkt=None):
    """Decrypt messages in symmetrically encrypted packets (types 9 & 18).

    :Parameters:
        - `encpkt`: packet containing encrypted data (symmetrically
          encrypted or integrity protected packet, types 9 & 18)
        - `passphrase`: string decryption passphrase (see below)
        - `sespkt`: optional session key packet
        - `keypkt`: optional public key packet

    :Returns: string cleartext

    :Exceptions:
        - `PGPError`: implementation error
        - `PGPDecryptionFailure`: decryption failed
        - `PGPSessionDecryptionFailure`: session decryption failed

    This is the all-in-one handler for "normal" decryption - that is,
    decrypting symmetrically encrypted (type 9) and symmetrically
    encrypted integrity protected (type 18) data. By consolidating 
    everything to one function it will be easier (hopefully) to manage
    secure data handling in the future.

    Because this function focuses on decrypting information in packet
    types 9 and 18, decrypted data is by definition (or "will be", due
    to the mechanics of this function) the data used to build an
    OpenPGP message (not the message instance). It is up to the API
    layer to automate things like "if compressed, decompress" or "if
    signed, verify."
    """
    result = key = algorithm = None # key & algo set to force integrity failure 

    if sespkt:
        ses = sespkt.body

        if PKT_PUBKEYSESKEY == sespkt.tag.type:

            if ses.keyid == keypkt.body.id:

                try:
                    seckeys = decrypt_secret_key(keypkt, passphrase)

                except PGPError: # catch MPI value error due to ..
                    raise PGPCryptoError("Public key encrypted session key checksum failed.")

                if keypkt.body.alg in [ASYM_RSA_E, ASYM_RSA_EOS]:
                    cipher_tuple = (ses.RSA_me_modn.value,)
                    key_tuple = (keypkt.body.RSA_n.value, seckeys[0])

                elif keypkt.body.alg in [ASYM_ELGAMAL_E, ASYM_ELGAMAL_EOS]:
                    cipher_tuple = (ses.ELGAMAL_gk_modp.value, ses.ELGAMAL_myk_modp.value)
                    key_tuple = (keypkt.body.ELGAMAL_p.value, seckeys[0])

                else:
                    raise NotImplementedError("Unsupported public encryption algorithm->(%s)." % keypkt.body.alg)

            else: # shouldn't happen, programmer error
                raise PGPCryptoError("The public encryption key did not match the session key target.")

            # should be ready to decrypt session key with key tuple
            padded_key = decrypt_public(ses.alg_pubkey, key_tuple, cipher_tuple)

            if '\x02' == padded_key[0]: # handle EME-PKCS1-v1_5 encoding
                idx = padded_key.find('\x00') # 0x00 used as padding separator

                if -1 != idx and 8 <= idx:
                    message = padded_key[idx+1:]
                    algorithm = STN.str2int(message[0]) # required for both..
                    chksum = STN.str2int(message[-2:])
                    key = message[1:len(message)-2] # ..symencdata and symencintdata

                    if chksum != STN.checksum(key):
                        raise PGPCryptoError("Public Key encrypted session key checksum failed.")

                else:
                    raise PGPCryptoError("Misplaced \\x00 in session key padding, located at index->(%s)." % idx)

            else:
                raise PGPCryptoError("Session key didn't start with \\x02, received->()." % hex(ord(padded_key[0])))

        elif PKT_SYMKEYSESKEY == sespkt.tag.type: # using symmetric key session key
            algorithm = ses.alg
            key = string2key(ses.s2k, algorithm, passphrase)

            if ses.has_key:
                iv = STN.prepad(_import_cipher(algorithm).block_size)
                padded_key = decrypt_symmetric(algorithm, key, ciphertext, iv)
                algorithm = padded_key[0]
                key = padded_key[1:]

        else:
            raise NotImplementedError("Unrecognized session key type-(%s)." % sespkt.tag.type)

    # 'algorithm' & 'key' should be set, it's time to decrypt the message
    if PKT_SYMENCINTDATA == encpkt.tag.type:
        bs = _import_cipher(algorithm).block_size
        iv = STN.prepad(bs)
        cleartext = decrypt_symmetric(algorithm, key, encpkt.body.data, iv)
        prefix = cleartext[:bs+2]
        clearmsg_d = cleartext[bs+2:-22]
        mdc_d = cleartext[-22:]
        mdc = mdc_d[-20:]

        if mdc != sha.new(''.join([prefix, clearmsg_d, '\xd3\x14'])).digest():
            raise PGPCryptoError("Integrity hash check failed.")

    elif PKT_SYMENCDATA == encpkt.tag.type:

        if None == key == algorithm: # non-integrity allows default key & alg
            key = md5.new(passphrase).digest
            algorithm = SYM_IDEA

        clearmsg_d = decrypt_symmetric_resync(algorithm, key, encpkt.body.data)

    return clearmsg_d

def decrypt_public(algorithm, key_tuple, cipher_tuple):
    """Decrypt public key encrypted data.

    :Parameters:
        - `algorithm`: integer public key algorithm constant
        - `key_tuple`: tuple containing a public and private integers of the
          target key, RSA values (n, d) or ElGamal values (p, x)
        - `cipher_tuple`: tuple containing the integers of the encrypted data,
          coerced RSA value (c, ) and ElGamal values (a, b)

    :Returns: string cleartext

    `decrypt_public()` works with public key encrypted information (information
    encrypted to public key values and decrypted using the corresponding secret
    key values). This function works with tuples of public key values and
    tuples of values that comprise the "ciphertext."

    **Use this function to decrypt public key encrypted session key packets.**

    RSA key tuple (n, d):
        - `n`: integer RSA product of primes p & q
        - `d`: integer RSA decryption key

    RSA cipher tuple (c, ):
        - `c`: integer m**e mod n

    ElGamal key tuple (p, x):
        - `p`: integer ElGamal prime
        - `x`: integer ElGamal private key

    ElGamal cipher tuple (a, b):
        - `a`: integer ElGamal value g**k mod p
        - `b`: integer ElGamal value m * y**k mod p

    Use this for decrypting public-key encrypted session keys.
    """
    key_tuple = tuple([long(i) for i in key_tuple]) # long(): fastmath dep

    if algorithm in [ASYM_RSA_EOS, ASYM_RSA_E]:
        from Crypto.PublicKey import RSA

        key = RSA.construct((key_tuple[0], 0L, key_tuple[1])) # L for fastmath
        a = STN.int2str(cipher_tuple[0])
        return key.decrypt((a,))

    elif algorithm in [ASYM_ELGAMAL_EOS, ASYM_ELGAMAL_E]:
        from Crypto.PublicKey import ElGamal

        key = ElGamal.construct((key_tuple[0], 0, 0, key_tuple[1]))
        a = STN.int2str(cipher_tuple[0])
        b = STN.int2str(cipher_tuple[1])
        return key.decrypt((a, b))

    else:
        raise NotImplementedError, "Unsupported asymmetric algorithm:%s" % algorithm

def decrypt_secret_key(keypkt, passphrase=''):
    """Retrieve decryption key values from a secret key packet.

    :Parameters:
        - `keypkt`: `OpenPGP.packet.SecretKey.SecretKey` instance or
          `OpenPGP.packet.SecretSubkey.SecretSubkey` instance
        - `passphrase`: optional decryption string

    :Returns: tuple of secret key integer values

    :Exceptions:
        - `PGPKeyDecryptionFailure`: secret key values did not encrypt
          properly

    Secret key tuples:
        - RSA keys: (d, p, q, u)
        - ElGamal keys: (x, )
        - DSA keys: (x, )

    :note: As far as key decryption goes, the only real check performed is the
        internal MPI check that the header, size, etc. make sense. Chances are
        slight that a failed decryption will render sensible MPIs. This is why
        the integrity checks are so important.
    """
    if not hasattr(keypkt.body, 's2k_usg'):
        raise PGPCryptoError("Key material does not contain secret key values (missing s2k usage).")

    if 0 == keypkt.body.s2k_usg:
        if keypkt.body.alg in [ASYM_RSA_E, ASYM_RSA_EOS]:
            key_tuple = (keypkt.body.RSA_d.value, keypkt.body.RSA_p.value, keypkt.body.RSA_q.value, keypkt.body.RSA_u.value)
        elif keypkt.body.alg in [ASYM_ELGAMAL_E, ASYM_ELGAMAL_EOS]:
            key_tuple = keypkt.body.ELGAMAL_x.value, # coerce tuple
        elif keypkt.body.alg in [ASYM_DSA]:
            key_tuple = keypkt.body.DSA_x.value, # coerce tuple

    else: # ..'idx' comes into play during the integrity check

        if 3 >= keypkt.body.version:

            if keypkt.body.alg in [ASYM_RSA_E, ASYM_RSA_EOS]:
                alg = keypkt.body.alg_sym

                if keypkt.body.s2k_usg in [254, 255]:
                    k = string2key(keypkt.body.s2k, alg, passphrase)

                else:
                    k = md5.new(passphrase).digest()

                # extra work required since MPIs integers are encrypted w/out
                # their lengths
                # create MPIs w/ encrypted integer octets 
                secRSA_d, idx = MPI.strcalc_mpi(keypkt.body._enc_d, 0)
                secRSA_p, idx = MPI.strcalc_mpi(keypkt.body._enc_d, idx)
                secRSA_q, idx = MPI.strcalc_mpi(keypkt.body._enc_d, idx)
                secRSA_u, idx = MPI.strcalc_mpi(keypkt.body._enc_d, idx)
                # decrypt integer octets
                RSA_d_int_d = decrypt_symmetric(alg, k, secRSA_d._int_d, keypkt.body.iv)
                RSA_p_int_d = decrypt_symmetric(alg, k, secRSA_d._int_d, keypkt.body.iv)
                RSA_q_int_d = decrypt_symmetric(alg, k, secRSA_d._int_d, keypkt.body.iv)
                RSA_u_int_d = decrypt_symmetric(alg, k, secRSA_d._int_d, keypkt.body.iv)
                # translate integer values
                RSA_d_value = STN.str2int(RSA_d_int_d)
                RSA_p_value = STN.str2int(RSA_p_int_d)
                RSA_q_value = STN.str2int(RSA_q_int_d)
                RSA_u_value = STN.str2int(RSA_u_int_d)

                key_tuple = (RSA_d_value, RSA_p_value, RSA_q_value, RSA_u_value)
                sec_d = ''.join([secRSA_d._d[:2], RSA_d_int_d, secRSA_p._d[:2], RSA_p_int_d, secRSA_q._d[:2], RSA_q_int_d, secRSA_q._d[:2], RSA_q_int_d])
            else:
                raise NotImplementedError("Unsupported v3 decryption key algorithm->(%s)." % keypkt.body.alg)

        elif 4 == keypkt.body.version:
            alg = keypkt.body.alg_sym
            k = string2key(keypkt.body.s2k, alg, passphrase)
            sec_d = decrypt_symmetric(alg, k, keypkt.body._enc_d, keypkt.body.iv)

            if keypkt.body.alg in [ASYM_RSA_E, ASYM_RSA_EOS, ASYM_RSA_S]:
                RSA_d, idx = MPI.strcalc_mpi(sec_d, 0)
                RSA_p, idx = MPI.strcalc_mpi(sec_d[idx:], idx)
                RSA_q, idx = MPI.strcalc_mpi(sec_d[idx:], idx)
                RSA_u, idx = MPI.strcalc_mpi(sec_d[idx:], idx)
                key_tuple = (RSA_d.value, RSA_p.value, RSA_q.value, RSA_u.value)

            elif keypkt.body.alg in [ASYM_ELGAMAL_E, ASYM_ELGAMAL_EOS]:
                ELGAMAL_x, idx = MPI.strcalc_mpi(sec_d, 0)
                key_tuple = ELGAMAL_x.value, # coerce tuple

            elif keypkt.body.alg in [ASYM_DSA]:
                DSA_x, idx = MPI.strcalc_mpi(sec_d, 0)
                key_tuple = DSA_x.value, # coerce tuple

            else:
                raise NotImplementedError("Unsupported public key algorithm->(%s)." % keypkt.body.alg)

        else:
            raise NotImplementedError, "Unsupported key version->(%s)." % keypkt.body.version

        # check integrity
        if 254 == keypkt.body.s2k_usg:

            if sec_d[idx:] != sha.new(sec_d[:idx]).digest():
                raise PGPCryptoError("Integrity hash check failed.")

        elif 255 == keypkt.body.s2k_usg:

            if keypkt.body.chksum != STN.checksum(sec_d):
                raise PGPCryptoError("Integrity checksum failed.")

    return key_tuple

def decrypt_symmetric(algorithm, key, ciphertext, iv=None):
    """Decrypt symmetrically encrypted data.

    :Parameters:
        - `algorithm`: integer symmetric cipher constant
        - `key`: string encryption/decryption key
        - `ciphertext`: string of encrypted data
        - `iv`: string initialization vector

    :Returns: string - outgoing cleartext

    This function performs conventional CFB decryption on blocks the
    size of the cipher's blocksize. Unlike the other OpenPGP symmetric
    decryption function, this one requires an IV (`iv`).

    **Use this function to handle encrypted secret key data.** The
    following secret key quirks need to be handled elsewhere:

        - v3 MPI count-hopping (skipping over MPI length headers)
        - v3 PKCS encoding
        - v4 SHA1 hash verification
        - checksum verification
    """
    cipherstream = StringIO()
    clearstream = StringIO()
    
    cipherstream.write(ciphertext) # thwart cStringIO read-only restriction
    cipherstream.seek(0)
    crypt_CFB(cipherstream, clearstream, algorithm, key, iv, 'decrypt')

    clearstream.seek(0)

    clrtxt = clearstream.read()

    return clrtxt

def decrypt_symmetric_resync(algorithm, key, ciphertext):
    """Decrypt symmetrically encrypted data and "re-sync" after prefix.

    :Parameters:
        - `algorithm`: integer symmetric cipher constant
        - `key`: string encryption/decryption key
        - `ciphertext`: string of encrypted data

    :Returns: string cleartext

    Perform block-sized CFB "resynced" operations *without* an IV. A prefix of
    one block of random data and a two octet integrity check before the actual
    ciphertext is expected. Instead of carrying on the decryption in one pass,
    decryption is restarted after the prefix (at the beginning of the "useful"
    ciphertext) using part of the prefix as an IV. This process is called a
    "resync."
    
    **Use this function when working with symmetrically encrypted data packets.**

    :Exceptions:
        - `PGPDecryptionFailure`: decrypted "re-sync" prefix check failed
    """
    ciphermod = _import_cipher(algorithm)
    bs = ciphermod.block_size

    clearprefix, cipherprefix = StringIO(), StringIO()
    cipherprefix.write(ciphertext[:bs+2])
    cipherprefix.seek(0)
    crypt_CFB(cipherprefix, clearprefix, algorithm, key, None, 'decrypt')

    clearprefix.seek(0)
    clear_prefix = clearprefix.read()

    if clear_prefix[-2:] == clear_prefix[bs-2:bs]: # "resync"
        clearstream, cipherstream = StringIO(), StringIO()
        cipherstream.write(ciphertext[bs+2:])
        cipherstream.seek(0)
        crypt_CFB(cipherstream, clearstream, algorithm, key, ciphertext[2:bs+2], 'decrypt')

        clearstream.seek(0)
        cleartext = clearstream.read()
        return cleartext
    else:
        raise PGPCryptoError("Re-sync check failed.")

def encrypt_integrity(algorithm, key, msg):
    """Encrypt a message with integrity protection.

    :Parameters:
        - `msg`: string cleartext
        - `algorithm`: integer cipher constant
        - `key`: string encryption key

    :Returns: `OpenPGP.packet.SymmetricallyEncryptedIntegrityProtectedData.SymmetricallyEncryptedIntegrityProtectedData` instance

    :note: It is up to the caller to make sure that `msg` is a valid
        message string (compressed properly, etc.).
    :note: Integrity check via SHA-1 is hardcoded.
    """
    import Crypto.Util.randpool as RND
    from openpgp.sap.pkt.Packet import create_Packet

    bs = _import_cipher(algorithm).block_size
    rnd = RND.RandomPool(bs)
    prefix = rnd.get_bytes(bs)

    clearstream = StringIO()
    cipherstream = StringIO()

    clearstream.write(prefix)
    clearstream.write(prefix[-2:])
    clearstream.write(msg)
    clearstream.write('\xd3\x14')
    clearstream.write(sha.new(clearstream.getvalue()).digest()) # hash previous
    clearstream.seek(0) # again, magic .read() should handle this in crypt_CFB()

    cipherstream.write('\x01')
    cipherstream.seek(0, 2)
    clearstream.seek(0)
    crypt_CFB(clearstream, cipherstream, algorithm, key, None, 'encrypt')

    cipherstream.seek(0)
    ciphertext = cipherstream.read()

    return create_Packet(PKT_SYMENCINTDATA, ciphertext)

def encrypt_public(algorithm, msg, key_tuple):
    """Encrypt data to a public key.

    :Parameters:
        - `algorithm`: integer public key algorithm constant
        - `key_tuple`: tuple containing a public and private integers
          the target key, RSA values (n, d) or ElGamal values (p, g, y)
          (see `RSA key tuple`_ and `ElGamal key tuple`_)

    :Returns: tuple ciphertext (a, b) for ElGamal and (r,) for RSA

    .. _RSA key tuple:

    RSA key tuple (n, e):

        - `n`: integer RSA product of primes p & q
        - `e`: integer RSA encryption key
    
    .. _ElGamal key tuple:

    ElGamal key tuple (p, g, y):
                
        - `p`: integer ElGamal prime
        - `g`: integer ElGamal group generator
        - `y`: integer ElGamal public key
    """
    import Crypto.Util.number

    key_tuple = tuple([long(i) for i in key_tuple]) # fastmath dep

    if algorithm in [ASYM_RSA_EOS, ASYM_RSA_E]:
        from Crypto.PublicKey import RSA

        key = RSA.construct(key_tuple)
        k = ''

    elif algorithm in [ASYM_ELGAMAL_EOS, ASYM_ELGAMAL_E]:
        from Crypto.PublicKey import ElGamal

        key = ElGamal.construct(key_tuple)
        k = Crypto.Util.number.getPrime(128, gen_random)

    else:
        raise NotImplementedError, "Can't handle public encryption algorithm->(%s)" % algorithm

    enc_tup = key.encrypt(msg, k) # Crypto returns strings instead of integers.

    return tuple([STN.str2int(x) for x in enc_tup]) # Why?
    
# Here we ponder the question - what the heck is the "intended length of the
# encoded message?" (per EME-PKCS1-v1_5) Block size? Why not just say so?
def encrypt_public_session(keypkt, key, symalg):
    """Create a public-key encrypted session key.

    :Parameters:
        - `keypkt`: either an `OpenPGP.packet.PublicKey.PublicKey` (or
          subclass) instance or encryption passphrase string
        - `key`: string encryptrion algorithm used for `symalg`
        - `symalg`: integer symmetric encryption algorithm constant

    :Returns: `OpenPGP.packet.PublicKeyEncryptedSessionKey.PublicKeyEncryptedSessionKey` instance
    """
    from openpgp.sap.pkt.Packet import create_Packet
    from openpgp.sap.pkt.PublicKeyEncryptedSessionKey import create_PublicKeyEncryptedSessionKeyBody

    pubalg = keypkt.body.alg
    rnd_prefix = []

    i = 0 # fixing the "intended length" business to 127
    while i <= 63 - len(key): # seems proper, but probably inefficient
        rnd_byte = gen_random(1)

        if '\x00' != rnd_byte:
            rnd_prefix.append(rnd_byte)
            i += 1

    chksum = STN.int2str(STN.checksum(key))[:2]

    if pubalg in [ASYM_RSA_EOS, ASYM_RSA_E]:
        key_tup = (keypkt.body.RSA_n.value, keypkt.body.RSA_e.value)

    elif pubalg in [ASYM_ELGAMAL_EOS, ASYM_ELGAMAL_E]:
        key_tup = (keypkt.body.ELGAMAL_p.value, keypkt.body.ELGAMAL_g.value, keypkt.body.ELGAMAL_y.value)

    else:
        raise NotImplementedError("Unsupported public key algorithm->(%s)." % pubalg)

    padded_key = ''.join(['\x02', ''.join(rnd_prefix), '\x00',
                          STN.int2str(symalg)[0], key, chksum])

    cipher_tup = encrypt_public(pubalg, padded_key, key_tup)

    sesbody = create_PublicKeyEncryptedSessionKeyBody(
        keyid=keypkt.body.id, alg=pubalg, mpis=cipher_tup)

    return create_Packet(PKT_PUBKEYSESKEY, sesbody._d)

def encrypt_symmetric_session(algorithm):
    """Create a symmetrically-encrypted session key.

    :Parameters:
        - `algorithm`: integer symmetric key algorithm constant

    :Returns: `OpenPGP.packet.SymmetricKeyEncryptedSessionKey.SymmetricKeyEncryptedSessionKey` instance

    :note: If a local session key is present, `algorithm` denotes the
        algorithm used to encrypt it. Otherwise, `algorithm` specifies
        what is used to encrypt the corresponding symmetrically
        encrypted (possibly integrity protected) data packet.

    :note: This function does not support locally encrypted session
        keys - decryption passphrases are "passed through" to the
        corresponding symmetrically encrypted data. So this function
        basically just prepares a string-to-key specifier which should
        be used to create the actual encryption key.
    """
    from openpgp.sap.pkt.Packet import create_Packet
    from openpgp.sap.pkt.S2K import create_S2K
    from openpgp.sap.pkt.SymmetricKeyEncryptedSessionKey import create_SymmetricKeyEncryptedSessionKeyBody

    s2k = create_S2K(salt=gen_random(8))
    params = {'alg':algorithm, 's2k':s2k}
    sesbody = create_SymmetricKeyEncryptedSessionKeyBody(params)

    return create_Packet(PKT_SYMKEYSESKEY, sesbody._d)

def gen_random(numbytes, poolsize=None):
    """Retrieve random bytes.

    :Parameters:
        - `numbytes`: integer number of random bytes to retrieve
        - `poolsize`: integer size of random pool to choose bytes from
          (default 256)

    :Returns: string of random bytes
    """
    import Crypto.Util.randpool as RND
    if None == poolsize:
        if numbytes > 256:
            poolsize = numbytes
        else:
            poolsize = 256
    rnd = RND.RandomPool(poolsize)
    return rnd.get_bytes(numbytes) 

# make it so that passphrase accepts none
def string2key(s2k, k_sym, passphrase):
    """Turn a passphrase into an encryption/decryption key.

    :Parameters:
        - `s2k`: `OpenPGP.packet.S2K.S2K` instance
        - `k_sym`: integer symmetric key algorithm constant
        - `passphrase`: string passphrase

    :Returns: string encryption key
    """
    if HASH_MD5 == s2k.alg_hash:
        hasher = md5
    elif HASH_SHA1 == s2k.alg_hash:
        hasher = sha
    else:
        raise NotImplementedError("Unsupported hash algorithm->(%s)." % s2k.alg_hash)

    if None == passphrase:
        passphrase = ''
    len_passphrase = len(passphrase)

    if s2k.type in [1, 3]:
        salt = s2k.salt
    else:
        salt = ''

    if s2k.type == 3:
        count = s2k.count
    else:
        count = 0
    keysize = _keysize(k_sym)

    pos, run, result = 0, 0, ''
    while pos < keysize:
        md = [] # reset message digest "hash context" every run
        done = 0
        for i in range(run): # preloaded 0x00s depending on iteration "run"
            md.append('\x00')
        if count < (len_passphrase + len(salt)):
            count = len_passphrase + len(salt)
        while (count - done) > (len_passphrase + len(salt)):
            if (len(salt) > 0):
                md.append(salt)
            md.append(passphrase)
            done = done + len_passphrase + len(salt)
        for i in range(len(salt)):
            if done < count:
                md.append(salt[i])
                done += 1
        for i in range(len_passphrase):
            if done < count:
                md.append(passphrase[i]) 
                done += 1
        hash = hasher.new(''.join(md)).digest()
        size = len(hash)
        if (pos + size) > keysize:
            size = keysize - pos
        result = ''.join([result[:pos], hash[0:size]])
        pos += size
        run += 1
    return result




