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

import sys
import os
import _winreg
import ctypes
#import platform
from drive import Drive
from virtualdisk import create_virtual_disk
from eject import eject_cd
import registry
from memory import get_total_memory_mb
from wubi.backends.common.backend import Backend
from wubi.backends.common.utils import run_command, replace_line_in_file, read_file, write_file, join_path, remove_line_in_file
from wubi.backends.common.mappings import country2tz, name2country, gmt2country, country_gmt2tz, gmt2tz
from os.path import abspath, isfile, isdir
import mappings
import shutil
import logging
log = logging.getLogger('WindowsBackend')


class WindowsBackend(Backend):
    '''
    Win32-specific backend
    '''

    def __init__(self, *args, **kargs):
        Backend.__init__(self, *args, **kargs)
        self.info.iso_extractor = join_path(self.info.bin_dir, '7z.exe')
        self.info.cpuid = join_path(self.info.bin_dir, 'cpuid.dll')
        log.debug('7z=%s' % self.info.iso_extractor)
        self.cache = {}

    def fetch_host_info(self):
        log.debug("Fetching host info...")
        self.info.registry_key = self.get_registry_key()
        self.info.windows_version = self.get_windows_version()
        self.info.windows_version2 = self.get_windows_version2()
        self.info.windows_sp = self.get_windows_sp()
        self.info.windows_build = self.get_windows_build()
        self.info.gmt = self.get_gmt()
        self.info.country = self.get_country()
        self.info.timezone = self.get_timezone()
        self.info.host_username = self.get_windows_username()
        self.info.user_full_name = self.get_windows_user_full_name()
        self.info.user_directory = self.get_windows_user_dir()
        self.info.windows_language_code = self.get_windows_language_code()
        self.info.windows_language = self.get_windows_language()
        self.info.processor_name = self.get_processor_name()
        self.info.bootloader = self.get_bootloader(self.info.windows_version)
        self.info.system_drive = self.get_system_drive()
        self.info.drives = self.get_drives()
        drives = [(d.path[:2].lower(), d) for d in self.info.drives]
        self.info.drives_dict = dict(drives)

    def select_target_dir(self):
        target_dir = join_path(self.info.target_drive.path, self.info.distro.installation_dir)
        target_dir.replace(' ', '_')
        target_dir.replace('__', '_')
        gold_target_dir = target_dir
        if os.path.exists(target_dir):
            raise Exception("Cannot install into %s.\nThere is another file or directory with this name.\nPlease remove it before continuing." % target_dir)
        self.info.target_dir = target_dir
        log.info('Installing into %s' % target_dir)
        self.info.icon = join_path(self.info.target_dir, self.info.distro.name + '.ico')

    def uncompress_target_dir(self, associated_task):
        if self.info.target_drive.is_fat():
            return
        try:
            command = ['compact', self.info.target_dir, '/U', '/A', '/F']
            run_command(command)
            command = ['compact', join_path(self.info.target_dir,'*.*'), '/U', '/A', '/F']
            run_command(command)
        except Exception, err:
            log.error(err)

    def uncompress_files(self, associated_task):
        if self.info.target_drive.is_fat():
            return
        command1 = ['compact', join_path(self.info.install_boot_dir), '/U', '/A', '/F']
        command2 = ['compact', join_path(self.info.install_boot_dir,'*.*'), '/U', '/A', '/F']
        for command in [command1,command2]:
            log.debug(" ".join(command))
            try:
                run_command(command)
            except Exception, err:
                log.error(err)

    def create_uninstaller(self, associated_task):
        uninstaller_name = 'uninstall-%s.exe'  % self.info.application_name
        uninstaller_name.replace(' ', '_')
        uninstaller_name.replace('__', '_')
        uninstaller_path = join_path(self.info.target_dir, uninstaller_name)
        if os.path.splitext(self.info.original_exe)[-1] == '.exe':
            log.debug('Copying uninstaller %s -> %s' % (self.info.original_exe, uninstaller_path))
            shutil.copyfile(self.info.original_exe, uninstaller_path)
        registry.set_value('HKEY_LOCAL_MACHINE', self.info.registry_key, 'UninstallString', uninstaller_path)
        registry.set_value('HKEY_LOCAL_MACHINE', self.info.registry_key, 'InstallationDir', self.info.target_dir)
        registry.set_value('HKEY_LOCAL_MACHINE', self.info.registry_key, 'DisplayName', self.info.distro.name)
        registry.set_value('HKEY_LOCAL_MACHINE', self.info.registry_key, 'DisplayIcon', self.info.icon)
        registry.set_value('HKEY_LOCAL_MACHINE', self.info.registry_key, 'DisplayVersion', self.info.version_revision)
        registry.set_value('HKEY_LOCAL_MACHINE', self.info.registry_key, 'Publisher', self.info.distro.name)
        registry.set_value('HKEY_LOCAL_MACHINE', self.info.registry_key, 'URLInfoAbout', self.info.distro.website)
        registry.set_value('HKEY_LOCAL_MACHINE', self.info.registry_key, 'HelpLink', self.info.distro.support)

    def create_virtual_disks(self, associated_task):
        self.info.disks_dir
        for disk in ["root", "home", "usr", "swap"]:
            path = join_path(self.info.disks_dir, disk + ".disk")
            size_mb = int(getattr(self.info, disk + "_size_mb"))
            if size_mb:
                create_virtual_disk(path, size_mb)

    def reboot(self):
        command = ['shutdown', '-r', '-t', '00']
        run_command(command) #TBD make async

    def copy_installation_files(self, associated_task):
        self.info.custominstall = join_path(self.info.install_dir, 'custom-installation')
        src = join_path(self.info.data_dir, 'custom-installation')
        dest = self.info.custominstall
        log.debug('Copying %s -> %s' % (src, dest))
        shutil.copytree(src, dest)
        src = join_path(self.info.root_dir, 'winboot')
        if isdir(src): # make runpy will fail otherwise as winboot will not be there
            dest = join_path(self.info.target_dir, 'winboot')
            log.debug('Copying %s -> %s' % (src, dest))
            shutil.copytree(src, dest)
        dest = join_path(self.info.custominstall, 'hooks', 'failure-command.sh')
        msg=_('The installation failed. Logs have been saved in: %s.' \
            '\n\nNote that in verbose mode, the logs may include the password.' \
            '\n\nThe system will now reboot.')
        msg = msg % join_path(self.info.install_dir, 'installation-logs.zip')
        msg = "msg=\"%s\"" % msg
        msg = str(msg.encode('utf8'))
        replace_line_in_file(dest, 'msg=', msg)
        src = join_path(self.info.image_dir, self.info.distro.name + '.ico')
        dest = self.info.icon
        log.debug('Copying %s -> %s' % (src, dest))
        shutil.copyfile(src, dest)

    def get_windows_version2(self):
        windows_version2 = registry.get_value(
                'HKEY_LOCAL_MACHINE',
                'SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion',
                'ProductName')
        log.debug('windows_version2=%s' % windows_version2)
        return windows_version2

    def get_windows_sp(self):
        windows_sp = registry.get_value(
                'HKEY_LOCAL_MACHINE',
                'SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion',
                'CSDVersion')
        log.debug('windows_sp=%s' % windows_sp)
        return windows_sp

    def get_windows_build(self):
        windows_build  = registry.get_value(
                'HKEY_LOCAL_MACHINE',
                'SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion',
                'CurrentBuildNumber')
        log.debug('windows_build=%s' % windows_build)
        return windows_build

    def get_processor_name(self):
        processor_name = registry.get_value(
            'HKEY_LOCAL_MACHINE',
            'HARDWARE\\DESCRIPTION\\System\\CentralProcessor\\0',
            'ProcessorNameString')
        log.debug('processor_name=%s' %processor_name)
        return processor_name

    def get_gmt(self):
        gmt = registry.get_value('HKEY_LOCAL_MACHINE', 'SYSTEM\\CurrentControlSet\\Control\\TimeZoneInformation', 'Bias')
        if gmt:
            gmt = -gmt/60
        if not gmt \
        or gmt > 12 \
        or gmt < -12:
            gmt = 0
        log.debug('gmt=%s' %gmt)
        return gmt

    def get_country(self):
        icountry = registry.get_value('HKEY_CURRENT_USER', 'Control Panel\\International', 'iCountry')
        try:
                icountry = int(icountry)
        except:
                pass
        country = mappings.icountry2country.get(icountry)
        if not country:
            scountry = registry.get_value('HKEY_CURRENT_USER', 'Control Panel\\International', 'sCountry')
            country = name2country.get(scountry)
        if not country:
           country = gmt2country.get(self.info.gmt)
        if not country:
            country = "US"
        log.debug('country=%s' %country)
        return country

    def get_timezone(self):
        timezone = country2tz.get(self.info.country)
        timezone = country_gmt2tz.get((self.info.country, self.info.gmt), timezone)
        if not timezone:
            timezone = gmt2tz.get(self.info.gmt)
        if not timezone:
            timezone = "America/New_York"
        log.debug('timezone=%s' % timezone)
        return timezone

    def eject_cd(self):
        eject_cd(self.info.cd_path)

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
        log.debug('windows version=%s' % version)
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
        log.debug('bootloader=%s' % bootloader)
        return bootloader

    def get_networking_info(self):
        return NotImplemented
        #~ win32com.client.Dispatch('WbemScripting.SWbemLocator') but it doesn't
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
                log.debug('drive=%s'% str(drive))
                drives.append(drive)
        return drives

    def get_uninstaller_path(self):
        uninstaller_path = registry.get_value('HKEY_LOCAL_MACHINE', self.info.registry_key, 'UninstallString')
        log.debug('uninstaller_path=%s' % uninstaller_path)
        return uninstaller_path

    def get_previous_target_dir(self):
        previous_target_dir = registry.get_value('HKEY_LOCAL_MACHINE', self.info.registry_key, 'InstallationDir')
        log.debug("previous_target_dir=%s" % previous_target_dir)
        return previous_target_dir

    def get_previous_distro_name(self):
        previous_distro_name = registry.get_value('HKEY_LOCAL_MACHINE', self.info.registry_key, 'DisplayName')
        log.debug("previous_distro_name=%s" % previous_distro_name)
        return previous_distro_name

    def get_registry_key(self):
        registry_key = 'Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\'  + self.info.application_name.capitalize()
        log.debug('registry_key=%s' % registry_key)
        return registry_key

    def get_windows_language_code(self):
        #~ windows_language_code = registry.get_value(
                #~ 'HKEY_CURRENT_USER',
                #~ '\\Control Panel\\International',
                #~ 'sLanguage')
        windows_language_code = mappings.language2n.get(self.info.language[:2])
        log.debug('windows_language_code=%s' % windows_language_code)
        if not windows_language_code:
            windows_language_code = 1033 #English
        return windows_language_code

    def get_windows_language(self):
        windows_language = mappings.n2fulllanguage.get(self.info.windows_language_code)
        log.debug('windows_language=%s' % windows_language)
        if not windows_language:
            windows_language = 'English'
        return windows_language

    def get_total_memory_mb(self):
        total_memory_mb = get_total_memory_mb()
        log.debug('total_memory_mb=%s' % total_memory_mb)
        return total_memory_mb

    def get_windows_username(self):
        windows_username = os.getenv('username')
        windows_username = windows_username.decode('ascii', 'ignore')
        log.debug('windows_username=%s' % windows_username)
        return windows_username

    def get_windows_user_full_name(self):
        user_full_name = os.getenv('username') #TBD
        user_full_name = user_full_name.decode('ascii', 'ignore')
        log.debug('user_full_name=%s' % user_full_name)
        return user_full_name

    def get_windows_user_dir(self):
        homedrive = os.getenv('homedrive')
        homepath = os.getenv('homepath')
        user_directory = ""
        if homedrive and homepath:
            user_directory = join_path(homedrive, homepath)
            user_directory = user_directory.decode('ascii', 'ignore')
        log.debug('user_directory=%s' % user_directory)
        return user_directory

    def get_keyboard_layout(self):
        win_keyboard_id = ctypes.windll.user32.GetKeyboardLayout(0)
        # lower word is the locale identifier (higher word is a handler to the actual layout)
        locale_id = win_keyboard_id & 0x0000FFFF
        keyboard_layout = mappings.keymaps.get(locale_id)
        if not keyboard_layout:
            keyboard_layout = self.info.country.lower()
        variant_id = win_keyboard_id & 0xFFFFFFFF
        keyboard_variant = mappings.hkl2variant.get(variant_id)
        if not keyboard_variant:
            keyboard_variant = ""
        log.debug('keyboard_id=%s' % win_keyboard_id)
        log.debug('keyboard_layout=%s' % keyboard_layout)
        log.debug('keyboard_variant=%s' % keyboard_variant)
        return keyboard_layout, keyboard_variant

    def get_system_drive(self):
        system_drive = os.getenv('SystemDrive')
        system_drive = Drive(system_drive)
        log.debug('system_drive=%s' % system_drive)
        return system_drive

    def detect_proxy(self):
        '''
        https://bugs.edge.launchpad.net/wubi/+bug/135815
        '''
        #TBD

    def extract_file_from_iso(self, iso_path, file_path, output_dir=None, overwrite=False):
        '''
        platform specific
        '''
        log.debug("  extracting %s from %s" % (file_path, iso_path))
        if not iso_path or not os.path.exists(iso_path):
            raise Exception('Invalid path %s' % iso_path)
        iso_path = abspath(iso_path)
        file_path = os.path.normpath(file_path)
        if not output_dir:
            output_dir = tempfile.gettempdir()
        output_file = join_path(output_dir, os.path.basename(file_path))
        if os.path.exists(output_file):
            if overwrite:
                os.unlink(output_file)
            else:
                raise Exception('Cannot overwrite %s' % output_file)
        command = [self.info.iso_extractor, 'e', '-i!' + file_path, '-o' + output_dir, iso_path]
        try:
            output = run_command(command)
        except Exception, err:
            log.exception(err)
            output_file = None
        if output_file and isfile(output_file):
            return output_file

    def get_usb_search_paths(self):
        '''
        Used to detect ISOs in USB keys
        '''
        return [drive.path for drive in self.info.drives] #TBD only look in USB devices

    def get_iso_search_paths(self):
        '''
        Gets default paths scanned for CD and ISOs
        '''
        paths = []
        paths += [os.path.dirname(self.info.original_exe)]
        paths += [self.info.backup_dir]
        paths += [drive.path for drive in self.info.drives]
        paths += [os.environ.get('Desktop', None)]
        paths = [abspath(p) for p in paths if p and os.path.isdir(p)]
        return paths

    def backup_iso(self, associated_task=None):
        if not self.info.backup_iso:
            return
        backup_dir = self.info.previous_target_dir + "-backup"
        install_dir = join_path(self.info.previous_target_dir, "install")
        for f in os.listdir(install_dir):
            f = join_path(install_dir, f)
            if f.endswith('.iso') \
            and os.path.isfile(f) \
            and os.path.getsize(f) > 1000000:
                log.debug("Backing up %s -> %s" % (f, backup_dir))
                if not isdir(backup_dir):
                    if isfile(backup_dir):
                        log.error("The backup directory %s is a file, skipping ISO backup" % backup_dir)
                        #TBD do something more sensible
                        return
                    os.mkdir(backup_dir)
                target_path = join_path(backup_dir, os.path.basename(f))
                shutil.move(f, target_path)

    def get_cd_search_paths(self):
        return [drive.path for drive in self.info.drives] # if drive.type == 'cd']

    def get_iso_file_names(self, iso_path):
        iso_path = abspath(iso_path)
        if iso_path in self.cache:
            return self.cache[iso_path]
        else:
            self.cache[iso_path] = None
        command = [self.info.iso_extractor,'l',iso_path]
        try:
            output = run_command(command)
        except Exception, err:
            log.exception(err)
            log.debug('command >>%s' % ' '.join(command))
            output = None
        if not output: return []
        lines = output.split(os.linesep)
        if lines < 10: return []
        lines = lines[7:-3]
        file_info = [line.split() for line in lines]
        file_names = [os.path.normpath(x[-1]) for x in file_info]
        self.cache[iso_path] = file_names
        return file_names

    def remove_registry_key(self):
        registry.delete_key(
            'HKEY_LOCAL_MACHINE',
            self.info.registry_key)

    def modify_bootloader(self, associated_task):
        for drive in self.info.drives:
            if drive.type not in ('removable', 'hd'):
                continue
            mb = None
            if self.info.bootloader == 'xp':
                mb = associated_task.add_subtask(self.modify_bootini)
            elif self.info.bootloader == '98':
                mb = associated_task.add_subtask(self.modify_configsys)
            elif self.info.bootloader == 'vista':
                mb = associated_task.add_subtask(self.modify_bcd)
            if mb:
                mb(drive)

    def undo_bootloader(self, associated_task):
        winboot_files = ['wubildr', 'wubildr.mbr', 'wubildr.exe']
        self.undo_bcd(associated_task)
        for drive in self.info.drives:
            if drive.type not in ('removable', 'hd'):
                continue
            self.undo_bootini(drive, associated_task)
            self.undo_configsys(drive, associated_task)
            for f in winboot_files:
                f = join_path(drive.path, f)
                if os.path.isfile(f):
                    os.unlink(f)

    def modify_bootini(self, drive, associated_task):
        log.debug("modify_bootini %s" % drive.path)
        bootini = join_path(drive.path, 'boot.ini')
        if not os.path.isfile(bootini):
            log.debug("Could not find boot.ini %s" % bootini)
            return
        src = join_path(self.info.root_dir, 'winboot', 'wubildr')
        dest = join_path(drive.path, 'wubildr')
        shutil.copyfile(src,  dest)
        src = join_path(self.info.root_dir, 'winboot', 'wubildr.mbr')
        dest = join_path(drive.path, 'wubildr.mbr')
        shutil.copyfile(src,  dest)
        run_command(['attrib', '-R', '-S', '-H', bootini])
        boot_line = 'C:\wubildr.mbr = "%s"' % self.info.distro.name
        old_line = boot_line[:boot_line.index("=")].strip().lower()
        # ConfigParser gets confused by the ':' and changes the options order
        content = read_file(bootini)
        if content[-1] != '\n':
            content += '\n'
        lines = content.split('\n')
        is_section = False
        for i,line in enumerate(lines):
            if line.strip().lower() == "[operating systems]":
                is_section = True
            elif line.strip().startswith("["):
                is_section = False
            if is_section and line.strip().lower().startswith(old_line):
                lines[i] = boot_line
                break
            if is_section and not line.strip():
                lines.insert(i, boot_line)
                break
        content = '\n'.join(lines)
        write_file(bootini, content)
        run_command(['attrib', '+R', '+S', '+H', bootini])

    def undo_bootini(self, drive, associated_task):
        log.debug("undo_bootini %s" % drive.path)
        bootini = join_path(drive.path, 'boot.ini')
        if not os.path.isfile(bootini):
            return
        run_command(['attrib', '-R', '-S', '-H', bootini])
        remove_line_in_file(bootini, 'c:\wubildr.mbr', ignore_case=True)
        run_command(['attrib', '+R', '+S', '+H', bootini])

    def modify_configsys(self, drive, associated_task):
        log.debug("modify_configsys %s" % drive.path)
        configsys = join_path(drive.path, 'config.sys')
        if not os.path.isfile(configsys):
            return
        src = join_path(self.info.root_dir, 'winboot', 'wubildr.exe')
        dest = join_path(drive.path, 'wubildr.exe')
        shutil.copyfile(src,  dest)
        run_command(['attrib', '-R', '-S', '-H', configsys])
        config = read_file(configsys)
        if 'REM WUBI MENU START\n' in config:
            log.debug("Configsys has already been modified")
            return

        config += '''
        REM WUBI MENU START
        [menu]
        menucolor=15,0
        menuitem=windows,Windows
        menuitem=wubildr,$distro
        menudefault=windows,10
        [wubildr]
        device=wubildr.exe
        [windows]

        REM WUBI MENU END
        '''
        write_file(configsys, config)
        run_command(['attrib', '+R', '+S', '+H', configsys])

    def undo_configsys(self, drive, associated_task):
        log.debug("undo_configsys %s" % drive)
        configsys = join_path(drive.path, 'config.sys')
        if not os.path.isfile(configsys):
            return
        run_command(['attrib', '-R', '-S', '-H', configsys])
        config = read_file(configsys)
        s = config.find('REM WUBI MENU START\n')
        e = config.find('REM WUBI MENU END\n')
        if s > 0 and e > 0:
            e += len('REM WUBI MENU END')
        config = config[:s] + config[e:]
        write_file(configsys, config)
        run_command(['attrib', '+R', '+S', '+H', configsys])

    def modify_bcd(self, drive, associated_task):
        log.debug("modify_bcd %s" % drive)
        if drive is self.info.system_drive \
        or drive.path == "C:" \
        or drive.path == os.getenv('SystemDrive').upper():
            src = join_path(self.info.root_dir, 'winboot', 'wubildr')
            dest = join_path(drive.path, 'wubildr')
            shutil.copyfile(src,  dest)
            src = join_path(self.info.root_dir, 'winboot', 'wubildr.mbr')
            dest = join_path(drive.path, 'wubildr.mbr')
            shutil.copyfile(src,  dest)
        bcdedit = join_path(os.getenv('SystemDrive'), 'bcdedit.exe')
        if not os.path.isfile(bcdedit):
            bcdedit = join_path(os.environ['systemroot'], 'sysnative', 'bcdedit.exe')
        # FIXME: Just test for bcdedit in the PATH.  What's the Windows
        # equivalent of `type`?
        if not os.path.isfile(bcdedit):
            bcdedit = join_path(os.environ['systemroot'], 'System32', 'bcdedit.exe')
        if not os.path.isfile(bcdedit):
            log.error("Cannot find bcdedit")
            return
        if registry.get_value('HKEY_LOCAL_MACHINE', self.info.registry_key, 'VistaBootDrive'):
            log.debug("BCD has already been modified")
            return

        command = [bcdedit, '/create', '/d', '%s' % self.info.distro.name, '/application', 'bootsector']
        id = run_command(command)
        id = id[id.index('{'):id.index('}')+1]
        mbr_path = join_path(self.info.target_dir, 'winboot', 'wubildr.mbr')[2:]
        run_command([bcdedit, '/set', id, 'device', 'partition=%s' % self.info.target_drive.path])
        run_command([bcdedit, '/set', id, 'path', mbr_path])
        run_command([bcdedit, '/displayorder', id, '/addlast'])
        run_command([bcdedit, '/timeout', '10'])
        registry.set_value(
            'HKEY_LOCAL_MACHINE',
            self.info.registry_key,
            'VistaBootDrive',
            id)

    def choose_disk_sizes(self, associated_task):
        total_size_mb = self.info.installation_size_mb
        home_size_mb = 0
        usr_size_mb = 0
        swap_size_mb = 256
        root_size_mb = total_size_mb - swap_size_mb
        if self.info.target_drive.is_fat():
            if root_size_mb > 8500:
                home_size_mb = root_size_mb - 8000
                usr_size_mb = 4000
                root_size_mb = 4000
            elif root_size_mb > 5500:
                usr_size_mb = 4000
                root_size_mb -= 4000
            elif root_size_mb > 4000:
                usr_size_mb = root_size_mb - 1500
                root_size_mb = 1500
            if home_size_mb > 4000:
               home_size_mb = 4000
        self.info.home_size_mb = home_size_mb
        self.info.usr_size_mb = usr_size_mb
        self.info.swap_size_mb = swap_size_mb
        self.info.root_size_mb = root_size_mb
        log.debug("total size=%s\n  root=%s\n  swap=%s\n  home=%s\n  usr=%s" % (total_size_mb, root_size_mb, swap_size_mb, home_size_mb, usr_size_mb))

    def undo_bcd(self, associated_task):
        bcdedit = join_path(os.getenv('SystemDrive'), 'bcdedit.exe')
        if not isfile(bcdedit):
            bcdedit = join_path(os.getenv('SystemRoot'), 'sysnative', 'bcdedit.exe')
        if not os.path.isfile(bcdedit):
            bcdedit = join_path(os.environ['systemroot'], 'System32', 'bcdedit.exe')
        if not os.path.isfile(bcdedit):
            log.error("Cannot find bcdedit")
            return
        id = registry.get_value(
            'HKEY_LOCAL_MACHINE',
            self.info.registry_key,
            'VistaBootDrive')
        if not id:
            log.debug("Could not find bcd id")
            return
        log.debug("Removing bcd entry %s" % id)
        command = [bcdedit, '/delete', id , '/f']
        run_command(command)
        registry.set_value(
            'HKEY_LOCAL_MACHINE',
            self.info.registry_key,
            'VistaBootDrive',
            "")

    def get_arch(self):
        cpuid = ctypes.windll.LoadLibrary(self.info.cpuid)
        if cpuid.check_64bit():
            arch = "amd64"
        else:
            arch = "i386"
        log.debug("arch=%s" % arch)
        return arch
