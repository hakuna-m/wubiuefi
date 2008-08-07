#~ win32com.client.Dispatch("WbemScripting.SWbemLocator") but it doesn't
#~ seem to function on win 9x. This script is intended to detect the
#~ computer's network configuration (gateway, dns, ip addr, subnet mask).
#~ Does someone know how to obtain those informations on a win 9x ?
#~ Windows 9x came without support for WMI. You can download WMI Core from
#~ http://www.microsoft.com/downloads/details.aspx?FamilyId=98A4C5BA-337B-4E92-8C18-A63847760EA5&displaylang=en
#~ although the implementation is quite limited

import sys
import os
import _winreg
import subprocess
import ctypes
#import platform
from backends.shared_backend import Backend, Progress
import logging
log = logging.getLogger("WindowsBackend")


class WindowsBackend(Backend):
    '''
    Win32-specific backend
    '''

    def get_os_version(self):
        windows_version = None
        full_version = sys.getwindowsversion()
        major, minor, build, platform, txt = full_version
        #platform.platform(), platform.system(), platform.release(), platform.version()
        if platform == 0:
            version = 'win32'
        elif platform == 1:
            if major == 4:
                if minor == 0:
                    version = '95'
                elif minor == 10:
                    version = '98'
                elif minor == 90:
                    version = 'me'
        elif platform == 2:
            if major == 4:
                version = 'nt'
            elif major == 5:
                if minor == 0:
                    version = '2000'
                elif minor == 1:
                    version = 'xp'
                elif minor == 2:
                    version = '2003'
            elif major == 6:
                version = 'vista'
        return version

    def get_bootloader(self, windows_version):
        if windows_version in ['vista', '2008']:
            bootloader = 'vista'
        elif windows_version in ['nt', 'xp', '2000', '2003']:
            bootloader = 'xp'
        elif windows_version in ['95', '98']:
            bootloader = '98'
        else:
            bootloader = None
        return bootloader

    def get_drives(self):
        drives = []
        for drive in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            drive_path = drive.upper() + ':'
            drive_type = ctypes.windll.kernel32.GetDriveTypeW(unicode(drive_path)) #TBD win32file.GetDriveType(drive_path)
            drive_type = [None, None, 'removable', 'hd', 'remote', 'cd', 'ram'][drive_type] #TBD USB??
            if drive_type:
                drive = Blob()
                drive.path = drive_path
                drive.type = drive_type
                try:
                    volinfo = ctypes.windll.kernel32.GetVolumeInformationA(drive_path + '\\') #win32api.GetVolumeInformation(drive_path + '\\')
                    drive.filesystem = volinfo[-1] and volinfo[-1].lower()
                except:
                    drive.filesystem = None
                drives.append(drive)
        return drives

    def find_isos(self, paths):
        pass

    def find_cds(self, paths):
        pass

    def is_valid_iso(self, path):
        pass

    def is_valid_cd(self, path):
        pass

    def is_valid_isoinfo(self, isoinfo):
        pass

    def fetch_os_stuff(self):
        #http://effbot.org/zone/python-register.htm
        self.info.registry_key = "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\"  + APPLICATION_NAME
        self.info.uninstaller_key = "Uninstaller"
        uninstaller_key = self.info.registry_key + self.info.uninstaller_key
        try:
            self.info.uninstaller = _winreg.QueryValue(_winreg.HKEY_LOCAL_MACHINE, uninstaller_key)
        except:
            self.info.uninstaller = None
        self.info.is_installed = self.info.uninstaller and os.path.exists(self.info.uninstaller) or False
        self.info.windows_version = get_windows_version()
        self.info.bootloader = get_windows_bootloader(self.info.windows_version)
        self.info.drives = get_windows_drives()



 
