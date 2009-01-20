"Encrypted Messages"

from openpgp.code import *
from openpgp.sap.exceptions import *
from Msg import Msg

#Each target in the `targets` list is a
#`SymmetricKeyEncryptedSessionKey` or `PublicKeyEncryptedSessionKey`
#instance. Each target has an added `_type` attribute. This is the
#integer type of the target's respective packet (1 for public key
#session key and 3 for symmetric key session key).
#The generic handling of encrypted messages looks like::
#
#    - Get the encrypted message.
#    - If there is a list of targets, 
#        - for each target in target list,
#            - see if we have secret keys that match
#                - if secret key is encrypted,
#                    - get the secret key passphrase and decrypt it, then
#                - attempt to decrypt encrypted message.
#            - see if there are symmetric keys,
#                - get a passphrase, then
#                - attempt to decrypt encrypted message.
#    - Otherwise,     
#        - if the message is symmetrically encrypted, 
#            - attempt decryption with MD5/IDEA.
#        - if it is integrity protected,
#            - raise hell since session packets (targets) are required.
#
#Alternately, instead of running automated "for target, check
#matching, decrypt" attempts, it might be nice to "list targets,
#flag matching, allow target choice and then attempt decryption."
class EncryptedMsg(Msg):
    """
    :IVariables:
        - `targets`: list of receiving public or symmetric key targets
          (list of `PublicKeyEncryptedSessionKey` and/or
          `SymmetricKeyEncryptedSessionKey` packets)
        - `encrypted`: encrypted packet (either a
          `SymmetricallyEncryptedData` packet or a
          `SymmetricallyEncryptedIntegrityProtectedData` packet))
        - `integrity`: integer 1 or 0 indicating integrity protected
          encrypted data (1) or not (0) (see above)
        - `_seq`: list of items in message sequence
        - `_d`: string of data used to build message

    :CVariables:
        - `type`: constant MSG_ENCRYPTED (see OpenPGP.constant.messages)
    """
    type = MSG_ENCRYPTED

    def list_target_keyids(self):
        return [k.body.keyid for k in self.targets if hasattr(k.body, 'keyid')]

