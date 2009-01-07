import ctypes
from winui.defs import NULL, FILE_SHARE_READ, FILE_SHARE_WRITE, GENERIC_READ, GENERIC_WRITE,CREATE_ALWAYS, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL
IOCTL_STORAGE_EJECT_MEDIA = 0x2D4808


def eject_cd(cd_path):
    #platform specific
    if not cd_path:
        return
    create_file = ctypes.windll.kernel32.CreateFileW
    cd_handle = create_file(
        r'\\\\.\\' + cd_path,
        GENERIC_READ,
        FILE_SHARE_READ|FILE_SHARE_WRITE,
        0,
        OPEN_EXISTING,
        0, 0)
    log.debug('Ejecting cd_handle=%s for drive=%s' % (cd_handle, cd_path))
    if cd_handle:
        x = ctypes.c_int()
        result = ctypes.windll.kernel32.DeviceIoControl(
            cd_handle,
            IOCTL_STORAGE_EJECT_MEDIA,
            0, 0, 0, 0, ctypes.byref(x), 0)
        ctypes.windll.kernel32.CloseHandle(cd_handle)
