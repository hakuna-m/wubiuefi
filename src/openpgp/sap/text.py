"Textification"

from openpgp.code import *

_msg_msg = {MSG_SIGNED:"Signed Message",
            MSG_ENCRYPTED:"Encrypted Message",
            MSG_COMPRESSED:"Compressed Message",
            MSG_LITERAL:"Literal Message",
            MSG_PUBLICKEY:"Public Key Message",
            MSG_PRIVATEKEY:"Secret Key Message",
            MSG_STOREDKEY:"Stored Key Message",
            MSG_DUMMY:"Dummy Message"}

def msg_msg(msg_type):
    return _msg_msg[msg_type]

_pkt_msg = {PKT_RESERVED:"Reserved - a packet tag must not have this value",
            PKT_PUBKEYSESKEY:"Public-key encrypted session key packet",
            PKT_SIGNATURE:"Signature",
            PKT_SYMKEYSESKEY:"Symmetric-key encrypted session key",
            PKT_ONEPASS:"One-pass signature",
            PKT_PRIVATEKEY:"Secret key",
            PKT_PUBLICKEY:"Public key",
            PKT_PRIVATESUBKEY:"Secret subkey",
            PKT_COMPRESSED:"Compressed data",
            PKT_SYMENCDATA:"Symmetrically encrypted data",
            PKT_MARKER:"Marker",
            PKT_LITERAL:"Literal data",
            PKT_TRUST:"Trust",
            PKT_USERID:"User ID",
            PKT_PUBLICSUBKEY:"Public subkey",
            PKT_USERATTR:"User attribute",
            PKT_SYMENCINTDATA:"Sym. encrypted and integrity protected data",
            PKT_MODDETECT:"Modification detection code",
            PKT_TESTOPEN:"openpgp.snap test packet",
            PKT_61:"Private or Experimental Value",
            PKT_62:"Private or Experimental Value",
            PKT_63:"Private or Experimental Value"}

def pkt_msg(pkt_type):
    return _pkt_msg[pkt_type]

_sig_msg = {SIG_BINARY:"Signature of a binary document",
            SIG_TEXT:"Signature of a canonical text document",
            SIG_STANDALONE:"Standalone signature",
            SIG_GENERIC:"Generic user ID certification",
            SIG_PERSONA:"Persona user ID certification",
            SIG_CASUAL:"Casual user ID certification",
            SIG_POSITIVE:"Positive user ID certification",
            SIG_SUBKEYBIND:"Subkey binding Signature",
            SIG_DIRECT:"Signature directly on a key",
            SIG_KEYREVOC:"Key revocation signature",
            SIG_SUBKEYREVOC:"Subkey revocation signature",
            SIG_CERTREVOC:"Certification revocation signature",
            SIG_TIMESTAMP:"Timestamp signature",
            SIG_THIRDPARTY:"Third-Party confirmation signature"}

def sig_msg(sig_type):
    return _sig_msg[sig_type]

_sigsub_msg = {SIGSUB_CREATED:"Signature Creation Time",
               SIGSUB_EXPIRES:"Signature Expiration Time",
               SIGSUB_EXPORTABLE:"Exportable Certification",
               SIGSUB_TRUST:"Trust Signature",
               SIGSUB_REGEX:"Regular Expression",
               SIGSUB_REVOCABLE:"Revocable",
               SIGSUB_KEYEXPIRES:"Key Expiration Time",
               SIGSUB_PLACEHOLDER:"Placeholder For Backward Compatibility",
               SIGSUB_SYMCODE:"Preferred Symmetric Algorithms",
               SIGSUB_REVOKER:"Revocation Key",
               SIGSUB_SIGNERID:"Issuer's Key ID",
               SIGSUB_NOTE:"Notation Data",
               SIGSUB_HASHCODE:"Preferred Hash Algorithms",
               SIGSUB_COMPCODE:"Preferred Compression Algorithms",
               SIGSUB_KEYSERVPREFS:"Key Server Preferences",
               SIGSUB_KEYSERV:"Preferred Key Server",
               SIGSUB_PRIMARYUID:"Primary User ID",
               SIGSUB_POLICYURL:"Policy URL",
               SIGSUB_KEYFLAGS:"Key Flags",
               SIGSUB_SIGNERUID:"Signer's User ID",
               SIGSUB_REVOCREASON:"Reason For Revocation",
               SIGSUB_FEATURES:"Features",
               SIGSUB_SIGTARGET:"Signature Target"}

def sigsub_msg(sigsub_type):
    return _sigsub_msg[sigsub_type]

_alg_pubkey_msg = {ASYM_RSA_EOS:"RSA (Encrypt or Sign)",
                   ASYM_RSA_E:"RSA Encrypt-Only",
                   ASYM_RSA_S:"RSA Sign-Only",
                   ASYM_ELGAMAL_E:"Elgamal (Encrypt-Only)",
                   ASYM_DSA:"DSA",
                   ASYM_ELIP:"Reserved for Elliptic Curve",
                   ASYM_ECDSA:"Reserved for ECDSA",
                   ASYM_ELGAMAL_EOS:"Elgamal (Encrypt or Sign)",
                   ASYM_DIFFHELL:"Reserved for Diffie-Hellman",
                   ASYM_100:"Private/Experimental algorithm",
                   ASYM_101:"Private/Experimental algorithm",
                   ASYM_102:"Private/Experimental algorithm",
                   ASYM_103:"Private/Experimental algorithm",
                   ASYM_104:"Private/Experimental algorithm",
                   ASYM_105:"Private/Experimental algorithm",
                   ASYM_106:"Private/Experimental algorithm",
                   ASYM_107:"Private/Experimental algorithm",
                   ASYM_108:"Private/Experimental algorithm",
                   ASYM_109:"Private/Experimental algorithm",
                   ASYM_110:"Private/Experimental algorithm"}

def alg_pubkey_msg(alg):
    return _alg_pubkey_msg[alg]

_alg_symkey_msg = {SYM_PLAIN:"Plaintext or unencrypted data",
                   SYM_IDEA:"IDEA [IDEA]",
                   SYM_DES3:"Triple-DES (DES-EDE, [SCHNEIER] - 168 bit key derived from 192)",
                   SYM_CAST5:"CAST5 (128 bit key, as per RFC2144)",
                   SYM_BLOWFISH:"Blowfish (128 bit key, 16 rounds) [BLOWFISH]",
                   SYM_5:"Reserved",
                   SYM_6:"Reserved",
                   SYM_AES128:"AES with 128-bit key [AES]",
                   SYM_AES192:"AES with 192-bit key",
                   SYM_AES256:"AES with 256-bit key",
                   SYM_TWOFISH:"Twofish with 256-bit key [TWOFISH]",
                   SYM_101:"Private/Experimental algorithm",
                   SYM_102:"Private/Experimental algorithm",
                   SYM_103:"Private/Experimental algorithm",
                   SYM_104:"Private/Experimental algorithm",
                   SYM_105:"Private/Experimental algorithm",
                   SYM_106:"Private/Experimental algorithm",
                   SYM_107:"Private/Experimental algorithm",
                   SYM_108:"Private/Experimental algorithm",
                   SYM_109:"Private/Experimental algorithm",
                   SYM_110:"Private/Experimental algorithm"}

def alg_symkey_msg(alg):
    return _alg_symkey_msg[alg]

_alg_comp_msg = {COMP_UNCOMPRESSED:"Uncompressed",
                 COMP_ZIP:"ZIP (RFC1951)",
                 COMP_ZLIB:"ZLIB (RFC1950)",
                 COMP_100:"Private/Experimental algorithm",
                 COMP_101:"Private/Experimental algorithm",
                 COMP_102:"Private/Experimental algorithm",
                 COMP_103:"Private/Experimental algorithm",
                 COMP_104:"Private/Experimental algorithm",
                 COMP_105:"Private/Experimental algorithm",
                 COMP_106:"Private/Experimental algorithm",
                 COMP_107:"Private/Experimental algorithm",
                 COMP_108:"Private/Experimental algorithm",
                 COMP_109:"Private/Experimental algorithm",
                 COMP_110:"Private/Experimental algorithm"}

def alg_comp_msg(alg):
    return _alg_comp_msg[alg]

_alg_hash_msg = {HASH_MD5:"MD5",
                 HASH_SHA1:"SHA-1",
                 HASH_RIPEMD160:"RIPE-MD/160",
                 HASH_4:"Reserved",
                 HASH_5:"Reserved",
                 HASH_6:"Reserved",
                 HASH_7:"Reserved",
                 HASH_SHA256:"SHA256",
                 HASH_SHA384:"SHA384",
                 HASH_SHA512:"SHA512",
                 HASH_100:"Private/Experimental algorithm",
                 HASH_101:"Private/Experimental algorithm",
                 HASH_102:"Private/Experimental algorithm",
                 HASH_103:"Private/Experimental algorithm",
                 HASH_104:"Private/Experimental algorithm",
                 HASH_105:"Private/Experimental algorithm",
                 HASH_106:"Private/Experimental algorithm",
                 HASH_107:"Private/Experimental algorithm",
                 HASH_108:"Private/Experimental algorithm",
                 HASH_109:"Private/Experimental algorithm",
                 HASH_110:"Private/Experimental algorithm"}

def alg_hash_msg(alg):
    return _alg_hash_msg[alg]
