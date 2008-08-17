#~ win32com.client.Dispatch("WbemScripting.SWbemLocator") but it doesn't
#~ seem to function on win 9x. This script is intended to detect the
#~ computer's network configuration (gateway, dns, ip addr, subnet mask).
#~ Does someone know how to obtain those informations on a win 9x ?
#~ Windows 9x came without support for WMI. You can download WMI Core from
#~ http://www.microsoft.com/downloads/details.aspx?FamilyId=98A4C5BA-337B-4E92-8C18-A63847760EA5&displaylang=en
#~ although the implementation is quite limited

#http://effbot.org/zone/python-register.htm
#http://www.google.com/codesearch?hl=en&q=GetVolumeInformationA+ctypes+show:o8kEK9H1ulQ:lGMUvEL_snU:EVcgF71zwXs&sa=N&cd=1&ct=rc&cs_p=http://gentoo.osuosl.org/distfiles/BitTorrent-5.0.7.tar.gz&cs_f=BitTorrent-5.0.7/BTL/likewin32api.py#l55
    # other nice functions in there :)


import sys
import os
import _winreg
import subprocess
import ctypes
#import platform
from drive import Drive
from registry import get_registry_value
from memory import get_total_memory_mb
from backends.common.backend import Backend
from backends.common.mappings import lang_country2linux_locale
import logging
log = logging.getLogger("WindowsBackend")


class WindowsBackend(Backend):
    '''
    Win32-specific backend
    '''

    def get_registry_value(self, key, subkey, attr):
        return get_registry_value(key, subkey, attr)

    def get_windows_version2(self):
        windows_version2 = self.get_registry_value(
                "HKEY_LOCAL_MACHINE",
                "SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion",
                "ProductName")
        log.debug("windows_version2=%s" % windows_version2)
        return windows_version2

    def get_windows_sp(self):
        windows_sp = self.get_registry_value(
                "HKEY_LOCAL_MACHINE",
                "SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion",
                "CSDVersion")
        log.debug("windows_sp=%s" % windows_sp)
        return windows_sp

    def get_windows_build(self):
        windows_build  = self.get_registry_value(
                "HKEY_LOCAL_MACHINE",
                "SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion",
                "CurrentBuildNumber")
        log.debug("windows_build=%s" % windows_build)
        return windows_build

    def get_processor_name(self):
        processor_name = get_registry_value(
            "HKEY_LOCAL_MACHINE",
            "HARDWARE\\DESCRIPTION\\System\\CentralProcessor\\0",
            "ProcessorNameString")
        log.debug("processor_name=%s" %processor_name)
        return processor_name

    def get_windows_version(self):
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
        log.debug("windows version=%s" % version)
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
        log.debug("bootloader=%s" % bootloader)
        return bootloader

    def get_drives(self):
        drives = []
        for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            drive = Drive(letter)
            if drive.type:
                log.debug("drive=%s"% str(drive))
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

    def get_uninstaller_path(self, uninstaller_key):
        try:
            uninstaller_path = _winreg.QueryValue(_winreg.HKEY_LOCAL_MACHINE, uninstaller_key)
        except:
            uninstaller_path = None
        log.debug("uninstaller_path=%s" % uninstaller_path)
        return uninstaller_path

    def get_is_installed(self, uninstaller_path):
        is_installed = uninstaller_path and os.path.exists(uninstaller_path) and True or False
        log.debug("is_installed=%s" % is_installed)
        return is_installed

    def get_registry_key(self):
        registry_key = "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\"  + self.info.application_name
        log.debug("registry_key=%s" % registry_key)
        return registry_key

    def get_is_running_from_cd(self):
        #TBD
        is_running_from_cd = False
        log.debug("is_running_from_cd=%s" % is_running_from_cd)
        return is_running_from_cd

    def get_windows_language_code(self):
        windows_language_code = self.get_registry_value(
                "HKEY_CURRENT_USER",
                "\\Control Panel\\International",
                "sLanguage")
        log.debug("windows_language_code=%s" % windows_language_code)
        return windows_language_code

    def get_locale(self, language_country):
        locale = lang_country2linux_locale.get(language_country, None)
        if not locale:
            locale = lang_country2linux_locale.get(en_US)
        log.debug("locale=%s" % locale)
        return locale

    def get_total_memory_mb(self):
        total_memory_mb = get_total_memory_mb()
        log.debug("total_memory_mb=%s" % total_memory_mb)
        return total_memory_mb

    def get_windows_username(self):
        windows_username = os.getenv("username")
        log.debug("windows_username=%s" % windows_username)
        return windows_username

    def get_keyboard_layout(self):
        keyboard_layout = ctypes.windll.user32.GetKeyboardLayout(0)
        log.debug("keyboard_layout=%s" % keyboard_layout)
        return keyboard_layout

        #~ lower word is the locale identifier (higher word is a handler to the actual layout)
        #~ IntOp $hkl $0 & 0xFFFFFFFF
        #~ IntFmt $hkl "0x%08X" $hkl
        #~ IntOp $localeid $0 & 0x0000FFFF
        #~ IntFmt $localeid "0x%04X" $localeid
        #~ ReadINIStr $layoutcode $PLUGINSDIR\data\keymaps.ini "keymaps" "$localeid"
        #~ ReadINIStr $keyboardvariant $PLUGINSDIR\data\variants.ini "hkl2variant" "$hkl"
        #~ #${debug} "hkl=$hkl, localeid=$localeid, layoutcode=$layoutcode, keyboardvariant=$keyboardvariant"
        #~ ${if} "$layoutcode" != ""
        #~ return
        #~ ${endif}
        #~ safetynet:
        #~ StrCpy $layoutcode "$country"
        #~ ${StrFilter} "$layoutcode" "-" "" "" "$layoutcode" #lowercase
        #~ ${debug} "LayoutCode=$LayoutCode"


    def get_system_drive(self):
        system_drive = os.getenv("SystemDrive")
        system_drive = Drive(system_drive)
        log.debug("system_drive=%s" % system_drive)
        return system_drive

    def fetch_basic_os_specific_info(self):
        self.info.registry_key = self.get_registry_key()
        self.info.uninstaller_subkey = "Uninstaller"
        uninstaller_key = self.info.registry_key + self.info.uninstaller_subkey
        self.info.uninstaller_path = self.get_uninstaller_path(uninstaller_key)
        self.info.is_installed = self.get_is_installed(self.info.uninstaller_path)
        self.info.windows_version = self.get_windows_version()
        self.info.windows_version2 = self.get_windows_version2()
        self.info.windows_sp = self.get_windows_sp()
        self.info.windows_build = self.get_windows_build()
        self.info.windows_username = self.get_windows_username()
        #~ self.info.windows_language_code = self.get_windows_language_code()
        self.info.keyboard_layout = self.get_keyboard_layout()
        self.info.processor_name = self.get_processor_name()
        self.info.bootloader = self.get_bootloader(self.info.windows_version)
        self.info.total_memory_mb = self.get_total_memory_mb()
        self.info.system_drive = self.get_system_drive()
        self.info.drives = self.get_drives()
        self.info.is_running_from_cd = self.get_is_running_from_cd()
        self.info.locale = self.get_locale(self.info.language)
