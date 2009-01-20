"Implementation constants"

# Packet codes
PKT_RESERVED      = 0
PKT_PUBKEYSESKEY  = 1
PKT_SIGNATURE     = 2
PKT_SYMKEYSESKEY  = 3
PKT_ONEPASS       = 4
PKT_PRIVATEKEY    = 5
PKT_PUBLICKEY     = 6
PKT_PRIVATESUBKEY = 7
PKT_COMPRESSED    = 8
PKT_SYMENCDATA    = 9
PKT_MARKER        = 10
PKT_LITERAL       = 11
PKT_TRUST         = 12
PKT_USERID        = 13
PKT_PUBLICSUBKEY  = 14
PKT_USERATTR      = 17
PKT_SYMENCINTDATA = 18
PKT_MODDETECT     = 19
PKT_TESTOPEN      = 60 # snap-specific
PKT_61            = 61
PKT_62            = 62
PKT_63            = 63
# key packets
PKT_KEYS = [PKT_PUBLICKEY, PKT_PUBLICSUBKEY, PKT_PRIVATEKEY, PKT_PRIVATESUBKEY]

# Signature codes
SIG_BINARY      = 0  # 0x00
SIG_TEXT        = 1  # 0x01
SIG_STANDALONE  = 2  # 0x02
SIG_GENERIC     = 16 # 0x10
SIG_PERSONA     = 17 # 0x11
SIG_CASUAL      = 18 # 0x12
SIG_POSITIVE    = 19 # 0x13
SIG_SUBKEYBIND  = 24 # 0x18
SIG_DIRECT      = 31 # 0x1F
SIG_KEYREVOC    = 32 # 0x20
SIG_SUBKEYREVOC = 40 # 0x28
SIG_CERTREVOC   = 48 # 0x30
SIG_TIMESTAMP   = 64 # 0x40
SIG_THIRDPARTY  = 80 # 0x50

# Signature subpacket codes
SIGSUB_CREATED      = 2
SIGSUB_EXPIRES      = 3
SIGSUB_EXPORTABLE   = 4
SIGSUB_TRUST        = 5
SIGSUB_REGEX        = 6
SIGSUB_REVOCABLE    = 7
SIGSUB_KEYEXPIRES   = 9
SIGSUB_PLACEHOLDER  = 10
SIGSUB_SYMCODE      = 11
SIGSUB_REVOKER      = 12
SIGSUB_SIGNERID     = 16
SIGSUB_NOTE         = 20
SIGSUB_HASHCODE     = 21
SIGSUB_COMPCODE     = 22
SIGSUB_KEYSERVPREFS = 23
SIGSUB_KEYSERV      = 24
SIGSUB_PRIMARYUID   = 25
SIGSUB_POLICYURL    = 26
SIGSUB_KEYFLAGS     = 27
SIGSUB_SIGNERUID    = 28
SIGSUB_REVOCREASON  = 29
SIGSUB_FEATURES     = 30
SIGSUB_SIGTARGET    = 31

# Asymmetric (public) key codes
ASYM_RSA_EOS     = 1
ASYM_RSA_E       = 2
ASYM_RSA_S       = 3
ASYM_ELGAMAL_E   = 16
ASYM_DSA         = 17
ASYM_ELIP        = 18
ASYM_ECDSA       = 19
ASYM_ELGAMAL_EOS = 20
ASYM_DIFFHELL    = 21
ASYM_100         = 100
ASYM_101         = 101
ASYM_102         = 102
ASYM_103         = 103
ASYM_104         = 104
ASYM_105         = 105
ASYM_106         = 106
ASYM_107         = 107
ASYM_108         = 108
ASYM_109         = 109
ASYM_110         = 110
# encryption algorithms
ASYM_ENCRYPTING = [ASYM_ELGAMAL_E, ASYM_ELGAMAL_EOS, ASYM_RSA_E, ASYM_RSA_EOS]
# signing algorithms
ASYM_SIGNING = [ASYM_DSA, ASYM_ELGAMAL_EOS, ASYM_RSA_S, ASYM_RSA_EOS]

# Symmetric key codes
SYM_PLAIN     = 0
SYM_IDEA      = 1
SYM_DES3      = 2
SYM_CAST5     = 3
SYM_BLOWFISH  = 4
SYM_5         = 5
SYM_6         = 6
SYM_AES128    = 7
SYM_AES192    = 8
SYM_AES256    = 9
SYM_TWOFISH   = 10
SYM_100       = 100
SYM_101       = 101
SYM_102       = 102
SYM_103       = 103
SYM_104       = 104
SYM_105       = 105
SYM_106       = 106
SYM_107       = 107
SYM_108       = 108
SYM_109       = 109
SYM_110       = 110

# Hash codes
HASH_MD5       = 1
HASH_SHA1      = 2
HASH_RIPEMD160 = 3
HASH_4         = 4
HASH_5         = 5
HASH_6         = 6
HASH_7         = 7
HASH_SHA256    = 8
HASH_SHA384    = 9
HASH_SHA512    = 10
HASH_100       = 100
HASH_101       = 101
HASH_102       = 102
HASH_103       = 103
HASH_104       = 104
HASH_105       = 105
HASH_106       = 106
HASH_107       = 107
HASH_108       = 108
HASH_109       = 109
HASH_110       = 110

# Compression codes
COMP_UNCOMPRESSED = 0
COMP_ZIP          = 1
COMP_ZLIB         = 2
COMP_100         = 100
COMP_101         = 101
COMP_102         = 102
COMP_103         = 103
COMP_104         = 104
COMP_105         = 105
COMP_106         = 106
COMP_107         = 107
COMP_108         = 108
COMP_109         = 109
COMP_110         = 110

# Message codes (used for this implementation only)
MSG_SIGNED     = 1
MSG_ENCRYPTED  = 2
MSG_COMPRESSED = 3
MSG_LITERAL    = 4
MSG_PUBLICKEY  = 5
MSG_PRIVATEKEY = 6
MSG_STOREDKEY  = 7
MSG_DUMMY      = 8
# key messages
MSG_KEYS = [MSG_PUBLICKEY, MSG_PRIVATEKEY, MSG_STOREDKEY]

# Error codes
SUCCESS = 0
# parsing 200-299
# signing 300-399
# encrypting 400-499
# implementation specific 500+
ERROR = 999

