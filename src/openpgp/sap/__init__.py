"""Somewhat academic PGP implementation

This package implements (most of) the OpenPGP standard as collection of
functions. For now, please try to stick with the string-based functions in
`api` since everything else depends on the class definitions in `pkt` and `msg`
which should be changing "soon."

Exceptions
``````````
Typical exceptions like ValueError and TypeError are allowed to pass through
to the caller. In a handful of cases, their default messages are replaced with
something a little more useful.

Three `exceptions` are introduced:
    - ``PGPError``: generic implementation errors
    - ``PGPFormatError``: errors found in formatting, invalid or ambiguous
      string data, packet sequences, etc..
    - ``PGPCryptoError``: errors in signing, verifying, encrypting, and
      decrypting. Each crypto function expects to return "successful" values:
      signatures are expected to verify, decryption is expected to produce
      clear text. Failures are regarded as errors.

``NotImplementedError`` is raised where some aspect of the standard is not yet
implemented *or* I intend the implementation to provide some kind of support.
"""
