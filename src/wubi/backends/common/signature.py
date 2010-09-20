# Copyright (c) 2008 Agostino Russo
#
# Written by Agostino Russo <agostino.russo@gmail.com>
#
# This file is part of Wubi the Win32 Ubuntu Installer.
#
# Wubi is free software; you can redistribute it and/or modify
# it under 5the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation; either version 2.1 of
# the License, or (at your option) any later version.
#
# Wubi is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

'''
Check sinature using openpgp and python-crypto
'''

import os
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

