#
# Copyright (c) 2007, 2008 Agostino Russo
# Python port of wubi/disckimage/main.c by Hampus Wessman
#
# Written by Agostino Russo <agostino.russo@gmail.com>
#
# win32.ui is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of
# the License, or (at your option) any later version.
#
# win32.ui is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

'''
Allocates disk space for the virtual disk
'''

import ctypes
from ctypes import c_long, byref
from winui import defs
import sys
import logging
log = logging.getLogger('Virtualdisk')

def create_virtual_disk(path, size_mb):
    '''
    Fast allocation of disk space
    This is done by using the windows API
    The initial and final block are zeroed
    '''
    log.debug(" Creating virtual disk %s of %sMB" % (path, size_mb))
    clear_bytes = 1000000
    if not size_mb or size_mb < 1:
        return

    # Get Permission
    grant_privileges()

    # Create file
    file_handle = defs.CreateFileW(
        unicode(path),
        defs.GENERIC_READ | defs.GENERIC_WRITE,
        0,
        defs.NULL,
        defs.CREATE_ALWAYS,
        defs.FILE_ATTRIBUTE_NORMAL,
        defs.NULL)
    if file_handle == defs.INVALID_HANDLE_VALUE:
        log.exception("Failed to create file %s" % path)

    # Set pointer to end of file */
    file_pos = defs.LARGE_INTEGER()
    file_pos.QuadPart = size_mb*1024*1024
    if not defs.SetFilePointerEx(file_handle, file_pos, 0, defs.FILE_BEGIN):
        log.exception("Failed to set file pointer to end of file")

    # Set end of file
    if not defs.SetEndOfFile(file_handle):
        log.exception("Failed to extend file. Not enough free space?")

    # Set valid data (if possible), ignore errors
    call_SetFileValidData(file_handle, file_pos)

    # Set pointer to beginning of file
    file_pos.QuadPart = 0
    result = defs.SetFilePointerEx(
                   file_handle,
                   file_pos,
                   defs.NULL,
                   defs.FILE_BEGIN)
    if not result:
        log.exception("Failed to set file pointer to beginning of file")

    # Zero chunk of file
    zero_file(file_handle, clear_bytes)

    # Set pointer to end - clear_bytes of file
    file_pos.QuadPart = size_mb*1024*1024 - clear_bytes
    result = defs.SetFilePointerEx(
                   file_handle,
                   file_pos,
                   defs.NULL,
                   defs.FILE_BEGIN)
    if not result:
        log.exception("Failed to set file pointer to end - clear_bytes of file")

    # Zero file
    zero_file(file_handle, clear_bytes)

    defs.CloseHandle(file_handle)

def grant_privileges():
    # For version < Windows NT, no privileges are involved
    full_version = sys.getwindowsversion()
    major, minor, build, platform, txt = full_version
    if platform < 2:
        log.debug("Skipping grant_privileges, because Windows 95/98/ME was detected")
        return

    # SetFileValidData() requires the SE_MANAGE_VOLUME_NAME privilege, so we must enable it
    #   on the process token. We don't attempt to strip the privilege afterward as that would
    #  introduce race conditions. */
    handle = ctypes.c_long(0)
    if defs.OpenProcessToken(defs.GetCurrentProcess(), defs.TOKEN_ADJUST_PRIVILEGES|defs.TOKEN_QUERY, byref(handle)):
        luid = defs.LUID()
        if defs.LookupPrivilegeValue(defs.NULL, defs.SE_MANAGE_VOLUME_NAME, byref(luid)):
            tp = defs.TOKEN_PRIVILEGES()
            tp.PrivilegeCount = 1
            tp.Privileges[0].Luid = luid
            tp.Privileges[0].Attributes = defs.SE_PRIVILEGE_ENABLED
            if not defs.AdjustTokenPrivileges(handle, defs.FALSE, byref(tp), 0, defs.NULL, defs.NULL):
                log.debug("grant_privileges: AdjustTokenPrivileges() failed.")
        else:
            log.debug("grant_privileges: LookupPrivilegeValue() failed.")
        defs.CloseHandle(handle)
    else:
        log.debug("grant_privileges: OpenProcessToken() failed.")

def call_SetFileValidData(file_handle, size_bytes):
    # No need, Windows 95/98/ME do this automatically anyway.
    full_version = sys.getwindowsversion()
    major, minor, build, platform, txt = full_version
    if platform < 2:
        log.debug("Skipping SetFileValidData, because Windows 95/98/ME was detected")
        return
    try:
        SetFileValidData = ctypes.windll.kernel32.SetFileValidData
    except:
        log.debug("Could not load SetFileValidData.")
        return
    SetFileValidData(file_handle, size_bytes)

def zero_file(file_handle, clear_bytes):
   bytes_cleared = 0
   buf_size = 1000
   n_bytes_written = c_long(0)
   write_buf = "0"*buf_size

   while bytes_cleared < clear_bytes:
       bytes_to_write = buf_size
       if (bytes_to_write > clear_bytes - bytes_cleared):
           bytes_to_write = clear_bytes - bytes_cleared
       result = defs.WriteFile(
                   file_handle,
                   write_buf,
                   bytes_to_write,
                   byref(n_bytes_written),
                   defs.NULL)
       if not result or not n_bytes_written.value:
           log.exception("WriteFile() failed!")
       bytes_cleared += n_bytes_written.value
