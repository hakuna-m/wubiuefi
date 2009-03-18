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

import ctypes
from winui.defs import NULL, FILE_SHARE_READ, FILE_SHARE_WRITE, GENERIC_READ, GENERIC_WRITE,CREATE_ALWAYS, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL
IOCTL_STORAGE_EJECT_MEDIA = 0x2D4808


def eject_cd(cd_path):
    #platform specific
    if not cd_path:
        return
    create_file = ctypes.windll.kernel32.CreateFileA
    cd_handle = create_file(
        "\\\\.\\%s" % cd_path[:2],
        GENERIC_READ,
        FILE_SHARE_READ|FILE_SHARE_WRITE,
        0,
        OPEN_EXISTING,
        0, 0)
    if cd_handle:
        x = ctypes.c_int()
        result = ctypes.windll.kernel32.DeviceIoControl(
            cd_handle,
            IOCTL_STORAGE_EJECT_MEDIA,
            0, 0, 0, 0, ctypes.byref(x), 0)
        ctypes.windll.kernel32.CloseHandle(cd_handle)
