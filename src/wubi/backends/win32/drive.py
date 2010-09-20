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
            self.filesystem = self.get_filesystem()
            total, free = self.get_space()
            self.total_space_mb = 1.0*total/1024**2
            self.free_space_mb = 1.0*free/1024**2

    def is_fat(self):
        return self.filesystem in ["fat", "fat32", "vfat"]

    def get_filesystem(self):
        MAX_PATH = 255
        if not hasattr(ctypes.windll.kernel32, "GetVolumeInformationA"):
            return ""
        filesystem = ""
        path = self.path[0] + ':\\'
        buf = ctypes.create_string_buffer("", MAX_PATH)
        ctypes.windll.kernel32.GetVolumeInformationA(path, None, 0, None, None, None, buf, len(buf))
        if isinstance(buf.value, str):
            filesystem = buf.value.lower()
        return filesystem

    def get_space(self):
        drive_path = self.path
        freeuser = ctypes.c_int64()
        total = ctypes.c_int64()
        free = ctypes.c_int64()
        ctypes.windll.kernel32.GetDiskFreeSpaceExW(
                unicode(drive_path),
                ctypes.byref(freeuser),
                ctypes.byref(total),
                ctypes.byref(free))
        return total.value, freeuser.value

    def __str__(self):
        return "Drive(%s %s %s mb free %s)" % (self.path, self.type, self.free_space_mb, self.filesystem)
