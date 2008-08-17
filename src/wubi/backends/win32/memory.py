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
