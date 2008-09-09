#http://effbot.org/zone/python-register.htm
#http://www.google.com/codesearch?hl=en&q=+ctypes+show:o8kEK9H1ulQ:lGMUvEL_snU:EVcgF71zwXs&sa=N&cd=1&ct=rc&cs_p=http://gentoo.osuosl.org/distfiles/BitTorrent-5.0.7.tar.gz&cs_f=BitTorrent-5.0.7/BTL/likewin32api.py#l55
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
from backends.common.helpers import run_command, cache
import logging
import shutil
log = logging.getLogger("WindowsBackend")


class WindowsBackend(Backend):
    '''
    Win32-specific backend
    '''

    def __init__(self, *args, **kargs):
        Backend.__init__(self, *args, **kargs)
        self.info.iso_extractor = os.path.join(self.info.bindir, '7z.exe')
        log.debug("7z=%s" % self.info.iso_extractor)

    def select_target_dir(self):
        targetdir = os.path.join(self.info.targetdrive, self.info.application_name)
        targetdir.replace(" ", "_")
        targetdir.replace("__", "_")
        gold_targetdir = targetdir
        if os.path.exists(targetdir) \
        and self.info.previous_targetdir != targetdir:
            for i in range(1000):
                targetdir = gold_targetdir + str(i)
                if os.path.exists(targetdir):
                    continue
        self.info.targetdir = targetdir
        if self.info.previous_targetdir:
            os.rename(self.info.previous_targetdir, self.info.targetdir)
        log.info("Installing into %s" % targetdir)

    def create_dir_structure(self):
        self.info.disksdir = os.path.join(self.info.targetdir, "disks")
        self.info.installdir = os.path.join(self.info.targetdir, "install")
        self.info.installbootdir = os.path.join(self.info.installdir, "boot")
        self.info.disksbootdir = os.path.join(self.info.disksdir, "boot")
        self.info.winbootdir = os.path.join(self.info.targetdir, "winboot")
        dirs = [
            self.info.targetdir,
            self.info.disksdir,
            self.info.installdir,
            self.info.installbootdir,
            self.info.disksbootdir,
            os.path.join(self.info.disksbootdir, "grub"),
            os.path.join(self.info.installbootdir, "grub"),]
        for d in dirs:
            if not os.path.isdir(d):
                log.debug("Creating dir %s" % d)
                os.mkdir(d)

    def uncompress_files(self):
        command1 = ["compact", os.path.join(self.info.targetdir), "/U", "/S", "/A", "/F"]
        command2 = ["compact", os.path.join(self.info.targetdir,"*.*"), "/U", "/S", "/A", "/F"]
        for command in [command1,command2]:
            try:
                runcommand(command)
            except Exception, err:
                log.exception(err)

    def create_uninstaller(self):
        uninstaller_name = "uninstall-%s.exe"  % self.info.application_name
        uninstaller_name.replace(" ", "_")
        uninstaller_name.replace("__", "_")
        uninstaller_path = os.path.join(self.info.targetdir, uninstaller_name)
        log.debug("Copying uninstaller %s -> %s" % (self.info.original_exe, uninstaller_path))
        shutil.copyfile(self.info.original_exe, uninstaller_path)

    def create_virtual_disks(self):
        pass #TBD

    def eject_cd(self):
        if not self.info.cd_drive: return
        #platform specific
        #IOCTL_STORAGE_EJECT_MEDIA 0x2D4808
        #FILE_SHARE_READ 1
        #FILE_SHARE_WRITE 2
        #FILE_SHARE_READ|FILE_SHARE_WRITE 3
        #GENERIC_READ 0x80000000
        #OPEN_EXISTING 3
        cd_handle = windll.kernel32.CreateFile(r'\\\\.\\' + self.info.cd_drive, 0x80000000, 3, 0, 3, 0, 0)
        log.debug("Ejecting cd_handle=%s for drive=%s" % (cd_handle, self.info.cd_drive))
        if cd_handle:
            x = ctypes.c_int()
            result = windll.kernel32.DeviceIoControl(cd_handle, 0x2D4808, 0, 0, 0, 0, ctypes.byref(x), 0)
            log.debug("EjectCD DeviceIoControl exited with code %s (1==success)" % result)
            windll.kernel32.CloseHandle(cd_handle)

    def reboot(self):
        command = ["shutdown", "-r", "-t", "00"]
        run_command(command) #TBD make async

    def copy_installation_files(self):
        self.info.custominstall = os.path.join(self.info.installdir, "custom-installation")
        src = os.path.join(self.info.datadir, "custom-installation")
        shutil.copytree(src, self.info.custominstall)
        src = os.path.join(self.info.rootdir, "winboot")
        shutil.copytree(src, self.info.targetdir)
        dest = os.path.join(self.info.custominstall, "hooks", "failure-command.sh")
        msg="The installation failed. Logs have been saved in: %s." \
            "\n\nNote that in verbose mode, the logs may include the password." \
            "\n\nThe system will now reboot."
        msg = msg % os.path.join(self.info.installdir, "installation-logs.zip")
        replace_line_in_file(dest, "msg=", "msg='%s'" % msg)

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

    def get_networking_info(self):
        return NotImplemented
        #~ win32com.client.Dispatch("WbemScripting.SWbemLocator") but it doesn't
        #~ seem to function on win 9x. This script is intended to detect the
        #~ computer's network configuration (gateway, dns, ip addr, subnet mask).
        #~ Does someone know how to obtain those informations on a win 9x ?
        #~ Windows 9x came without support for WMI. You can download WMI Core from
        #~ http://www.microsoft.com/downloads/details.aspx?FamilyId=98A4C5BA-337B-4E92-8C18-A63847760EA5&displaylang=en
        #~ although the implementation is quite limited

    def get_drives(self):
        drives = []
        for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            drive = Drive(letter)
            if drive.type:
                log.debug("drive=%s"% str(drive))
                drives.append(drive)
        return drives

    def get_uninstaller_path(self):
        try:
            uninstaller_path = _winreg.QueryValue(_winreg.HKEY_LOCAL_MACHINE, self.info.uninstaller_key)
        except:
            uninstaller_path = None
        log.debug("uninstaller_path=%s" % uninstaller_path)
        return uninstaller_path

    def get_registry_key(self):
        registry_key = "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\"  + self.info.application_name
        log.debug("registry_key=%s" % registry_key)
        return registry_key

    def get_windows_language_code(self):
        windows_language_code = self.get_registry_value(
                "HKEY_CURRENT_USER",
                "\\Control Panel\\International",
                "sLanguage")
        log.debug("windows_language_code=%s" % windows_language_code)
        return windows_language_code

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
        self.info.uninstaller_key = self.info.registry_key + self.info.uninstaller_subkey
        self.info.windows_version = self.get_windows_version()
        self.info.windows_version2 = self.get_windows_version2()
        self.info.windows_sp = self.get_windows_sp()
        self.info.windows_build = self.get_windows_build()
        self.info.windows_username = self.get_windows_username()
        #~ self.info.windows_language_code = self.get_windows_language_code()
        self.info.processor_name = self.get_processor_name()
        self.info.bootloader = self.get_bootloader(self.info.windows_version)
        self.info.system_drive = self.get_system_drive()
        self.info.drives = self.get_drives()

    def extract_file_from_iso(self, iso_path, file_path, output_dir=None, overwrite=False):
        '''
        platform specific
        '''
        iso_path = os.path.abspath(iso_path)
        file_path = os.path.normpath(file_path)
        if not output_dir:
            output_dir = tempfile.gettempdir()
        output_file = os.path.join(output_dir, os.path.basename(file_path))
        if os.path.exists(output_file):
            if overwrite:
                os.unlink(output_file)
            else:
                raise Exception("Cannot overwrite %s" % output_file)
        command = [self.info.iso_extractor, 'e', '-i!' + file_path, '-o' + output_dir, iso_path]
        try:
            output = run_command(command)
        except Exception, err:
            log.exception(err)
            output_file = None
        if output_file and os.path.isfile(output_file):
            return output_file

    def get_iso_search_paths(self):
        '''
        Gets default paths scanned for CD and ISOs
        '''
        paths = []
        paths += [self.info.exedir]
        #~ paths += [self.info.backupfolder]
        paths += [drive.path for drive in self.info.drives]
        paths += [os.environ.get("Desktop", None)]
        paths += ['/home/vm/cd'] #TBD quick test
        paths = [os.path.abspath(p) for p in paths]
        return paths

    def get_cd_search_paths(self):
        return [drive.path for drive in self.info.drives] # if drive.type == 'cd']

    def get_iso_file_names(self, iso_path):
        iso_path = os.path.abspath(iso_path)
        if (self.get_iso_file_names, iso_path) in cache:
            return cache[(self.get_iso_file_names, iso_path)]
        else:
            cache[(self.get_iso_file_names, iso_path)] = None
        command = [self.info.iso_extractor,'l',iso_path]
        try:
            output = run_command(command)
        except Exception, err:
            log.exception(err)
            log.debug("command >>%s" % " ".join(command))
            output = None
        if not output: return []
        lines = output.split(os.linesep)
        if lines < 10: return []
        lines = lines[7:-3]
        file_info = [line.split() for line in lines]
        file_names = [os.path.normpath(x[-1]) for x in file_info]
        cache[(self.get_iso_file_names, iso_path)] = file_names
        return file_names
