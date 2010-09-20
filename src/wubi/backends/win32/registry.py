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

import _winreg
import logging
log = logging.getLogger("registry")

from winui.defs import KEY_SET_VALUE

def get_value(key, subkey, attr):
    key = getattr(_winreg, key)
    try:
        handle = _winreg.OpenKey(key, subkey)
    except:
        return None
    try:
        (value, type) = _winreg.QueryValueEx(handle, attr)
    except:
        return None
    _winreg.CloseKey(handle)
    return value

def set_value(key, subkey, attr, value):
    key = getattr(_winreg, key)
    try:
        handle = _winreg.OpenKey(key, subkey, sam=KEY_SET_VALUE)
    except:
        handle = _winreg.CreateKey(key, subkey)
    try:
        log.debug("Setting registry key %s %s %s %s" % (key, subkey, attr, value))
        _winreg.SetValueEx(handle, attr, 0, 1, value)
    except Exception, err:
        log.exception("Cannot set registry key %s\\%s = %s\n%s" % (subkey, attr, value, err))
    _winreg.CloseKey(handle)

def delete_key(key, subkey):
    key = getattr(_winreg, key)
    try:
        _winreg.DeleteKey(key, subkey)
    except Exception, err:
        log.exception("Cannot delete registry key %s\n%s" % (subkey, err))
