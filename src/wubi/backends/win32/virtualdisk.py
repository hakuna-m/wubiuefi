import ctypes
from ctypes import c_long
from winui.defs import *
import sys
import logging
log = logging.getLogger('Virtualdisk')

create_file = ctypes.windll.kernel32.CreateFileW
close_handle = ctypes.windll.kernel32.CloseHandle
set_file_pointer = ctypes.windll.kernel32.SetFilePointerEx
set_end_of_file = ctypes.windll.kernel32.SetEndOfFile
get_version = ctypes.windll.kernel32.GetVersion
write_file = ctypes.windll.kernel32.WriteFile

def create_virtual_disk(path, size_mb):
    log.debug(" Creating virtual disk %s of %sMB" % (path, size_mb))
    clear_bytes = 4000000
    if not size_mb or size_mb < 1:
        return

    # Create file
    file_handle = create_file(
        unicode(path),
        GENERIC_READ | GENERIC_WRITE,
        0,
        NULL,
        CREATE_ALWAYS,
        FILE_ATTRIBUTE_NORMAL,
        NULL)
    if file_handle == INVALID_HANDLE_VALUE:
        log.exception("Failed to create file %s" % path)

    # Set pointer to end of file */
    file_pos = ctypes.c_longlong(0)
    file_pos.QuadPart = size_mb*1024
    if not set_file_pointer(file_handle, file_pos, 0, FILE_BEGIN):
        log.exception("Failed to set file pointer to end of file")

    # Set end of file
    if not set_end_of_file(file_handle):
        log.exception("Failed to extend file. Not enough free space?")

    # Set valid data (if possible), ignore errors
    call_SetFileValidData(file_handle, c_longlong(size_mb*1024));

    # Set pointer to beginning of file
    file_pos.QuadPart = 0;
    result = set_file_pointer(
                   file_handle,
                   file_pos,
                   NULL,
                   FILE_BEGIN);
    if not result:
        log.exception("Failed to set file pointer to beginning of file")

    # Zero chunk of file
    zero_file(file_handle, clear_bytes)

    # Set pointer to end - clear_bytes of file
    file_pos.QuadPart = -clear_bytes-2;
    result = set_file_pointer(
                   file_handle,
                   file_pos,
                   NULL,
                   FILE_END);
    if not result:
        log.exception("Failed to set file pointer to end - clear_bytes of file")

    # Zero file
    zero_file(file_handle, clear_bytes)

    close_handle(file_handle)

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
    result = SetFileValidData(file_handle, size_bytes)

def zero_file(file_handle, clear_bytes):
   bytes_cleared = c_long(0)
   buf_size = 1000

   n_bytes_written = c_long(0)
   write_buf = "0"*buf_size

   while bytes_cleared < clear_bytes:
       bytes_to_write = buf_size
       if (bytes_to_write > clear_bytes - bytes_cleared):
           bytes_to_write = clear_bytes - bytes_cleared
       result = write_file(
                   file_handle,
                   write_buf,
                   bytes_to_write,
                   byref(n_bytes_written),
                   NULL);
       if not result or not n_bytes_written:
           log.exception("WriteFile() failed!")
       bytes_cleared += n_bytes_written
