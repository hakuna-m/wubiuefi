"Exceptions"

class PGPError(Exception): pass       # generic error in implementation use
class PGPFormatError(PGPError): pass  # invalid packet/message input
class PGPCryptoError(PGPError): pass  # generic encryption/signing error
