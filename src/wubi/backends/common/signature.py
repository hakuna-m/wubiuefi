import os
import sys
from utils import read_file

from openpgp.sap.api import verify_str
#explicit imports required by pylauncher
import openpgp.sap.pkt.PublicKey
import openpgp.sap.pkt.UserID
import openpgp.sap.pkt.Trust

def verify_gpg_signature(detached_file, signature_file, key_file):
    signature = read_file(signature_file, binary=True)
    #not generic but ok if the signature is generated in linux
    #this is to avoid the signature to be misinterpreted when parsed in another OS
    signature = signature.replace('\n', os.linesep)
    key = read_file(key_file, binary=True)
    message = read_file(detached_file, binary=True)
    result = verify_str(signature, key, detached=message)
    return result == message

