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
DWORD = ctypes.wintypes.DWORD

class MEMORYSTATUS(ctypes.Structure):
    _fields_ = [
        ('dwLength', DWORD),
        ('dwMemoryLoad', DWORD),
        ('dwTotalPhys', DWORD),
        ('dwAvailPhys', DWORD),
        ('dwTotalPageFile', DWORD),
        ('dwAvailPageFile', DWORD),
        ('dwTotalVirtual', DWORD),
        ('dwAvailVirtual', DWORD),
        ]

def get_total_memory_mb():
    memory_status = MEMORYSTATUS()
    memory_status.dwLength = ctypes.sizeof(MEMORYSTATUS)
    ctypes.windll.kernel32.GlobalMemoryStatus(ctypes.byref(memory_status))
    total_memory = memory_status.dwTotalPhys
    total_memory_mb = 1.0*total_memory/1024**2
    return total_memory_mb
