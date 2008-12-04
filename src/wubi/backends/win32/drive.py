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

import os
import ctypes
import ctypes.wintypes
import logging
log = logging.getLogger("WindowsDrive")

class Drive(object):
    DRIVETYPE0 = 0
    REMOVABLE = 2
    HD = 3
    REMOTE = 4
    CD = 5
    RAM = 6

    def __init__(self, letter):
        drive_path = letter.upper()
        if not drive_path.endswith(':'): drive_path += ':'
        self.path = drive_path
        self.type_n = ctypes.windll.kernel32.GetDriveTypeW(unicode(drive_path))
        self.type = [None, None, 'removable', 'hd', 'remote', 'cd', 'ram'][self.type_n] #TBD USB??
        if self.path == 'A:' and self.type == 'removable':
            self.type = None #skip floppy: TBD do something reasonble
        if self.type:
            volinfo = self.get_volume_information()
            self.filesystem = volinfo[-1] and volinfo[-1]
            self.free_space_mb = 1.0*self.get_free_space()/1024**2

    def get_volume_information(self):
        DWORD = ctypes.wintypes.DWORD
        MAX_PATH_NULL = 255
        drive_path = self.path
        volume_serial_number = DWORD()
        maximum_component_length = DWORD()
        file_system_flags = DWORD()
        if hasattr(ctypes.windll.kernel32, "GetVolumeInformationW"):
            drive_path = unicode(drive_path)
            volume_name_buffer = ctypes.create_unicode_buffer(MAX_PATH_NULL)
            file_system_name_buffer = ctypes.create_unicode_buffer(MAX_PATH_NULL)
            gvi = ctypes.windll.kernel32.GetVolumeInformationW
        else:
            volume_name_buffer = ctypes.create_string_buffer(MAX_PATH_NULL)
            file_system_name_buffer = ctypes.create_string_buffer(MAX_PATH_NULL)
            gvi = ctypes.windll.kernel32.GetVolumeInformationA
        gvi(  drive_path,
                volume_name_buffer,
                MAX_PATH_NULL,
                ctypes.byref(volume_serial_number),
                ctypes.byref(maximum_component_length),
                ctypes.byref(file_system_flags),
                file_system_name_buffer,
                MAX_PATH_NULL)
        volume_information = (
                str(volume_name_buffer.value),
                volume_serial_number.value,
                maximum_component_length.value,
                file_system_flags.value,
                str(file_system_name_buffer.value).lower())
        return volume_information

    def get_free_space(self):
        drive_path = self.path
        freeuser = ctypes.c_int64()
        total = ctypes.c_int64()
        free = ctypes.c_int64()
        ctypes.windll.kernel32.GetDiskFreeSpaceExW(
                unicode(drive_path),
                ctypes.byref(freeuser),
                ctypes.byref(total),
                ctypes.byref(free))
        return freeuser.value

    def __str__(self):
        return "Drive(%s %s %s mb free %s)" % (self.path, self.type, self.free_space_mb, self.filesystem)
