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
import tempfile
import locale
import struct
import logging
import tempfile
import time
import mappings
import gettext
import glob
import shutil
import ConfigParser
import btdownloader
import downloader

from metalink import parse_metalink
from tasklist import ThreadedTaskList, Task
from distro import Distro
from mappings import lang_country2linux_locale
from utils import join_path, run_command, copy_file, replace_line_in_file, read_file, write_file, get_file_md5, reversed, find_line_in_file, unixpath
from os.path import abspath, dirname, isfile, isdir, exists

log = logging.getLogger("CommonBackend")

class Backend(object):
    '''
    Implements non-platform-specific functionality
    Subclasses need to implement platform-specific getters
    '''
    def __init__(self, application):
        self.application = application
        self.info = application.info
        if hasattr(sys,'frozen') and sys.frozen:
            rootdir = dirname(abspath(sys.executable))
            tempdir = tempfile.mkdtemp(dir=rootdir)
        else:
            rootdir = ''
            tempdir = tempfile.mkdtemp()
        self.info.rootdir = abspath(rootdir)
        self.info.tempdir = abspath(tempdir)
        self.info.datadir = join_path(self.info.rootdir, 'data')
        self.info.bindir = join_path(self.info.rootdir, 'bin')
        self.info.imagedir = join_path(self.info.datadir, "images")
        log.debug('datadir=%s' % self.info.datadir)

    def get_installation_tasklist(self):
        tasks = [
            Task(self.select_target_dir, description="Selecting target directory"),
            Task(self.create_dir_structure, description="Creating the installation directories"),
            Task(self.create_uninstaller, description="Creating the uninstaller"),
            Task(self.copy_installation_files, description="Copying files", weight=5),
            Task(self.get_metalink, description="Retrieving the Metalink", weight=10),
            Task(self.get_iso, description="Retrieving the ISO", weight=10),
            Task(self.extract_kernel, description="Extracting the kernel", weight=5),
            Task(self.uncompress_files, description="Uncompressing files"),
            Task(self.choose_disk_sizes, description="Choosing disk sizes"),
            Task(self.create_preseed, description="Creating a preseed file"),
            Task(self.modify_bootloader, description="Adding a new bootlader entry"),
            Task(self.create_virtual_disks, description="Creating the virtual disks"),
            Task(self.uncompress_files, description="Uncompressing files"),
            Task(self.eject_cd, description="Ejecting the CD"),
            ]
        tasklist = ThreadedTaskList(name="installer", description="Installing", tasks=tasks)
        return tasklist

    def get_reboot_tasklist(self):
        tasks = [
            Task(self.reboot, description="Rebooting"),
            ]
        tasklist = ThreadedTaskList(name="Reboot", description="Rebooting", tasks=tasks)
        return tasklist

    def get_uninstallation_tasklist(self):
        tasks = [
            Task(self.backup_iso, "Backup ISO"),
            Task(self.undo_bootloader, "Remove bootloader entry"),
            Task(self.remove_target_dir, "Remove target dir"),
            Task(self.remove_registry_key, "Remove registry key"),]
        tasklist = ThreadedTaskList(name="Uninstaller", description="Uninstalling", tasks=tasks)
        return tasklist

    def show_info(self):
        log.debug("Showing info")
        os.startfile(self.info.distro.website)

    def change_language(self, codeset):
        domain = self.info.application_name #not sure what it is
        localedir = join_path(self.info.datadir, 'locale')
        self.info.codeset = codeset # set the language
        gettext.install(domain, codeset=codeset)

    def fetch_basic_info(self):
        '''
        Basic information required by the application dispatcher select_task()
        '''
        log.debug("Fetching basic info...")
        self.info.backup_dir = "%s.backup" % self.info.application_name
        self.info.original_exe = self.get_original_exe()
        self.info.platform = self.get_platform()
        self.info.osname = self.get_osname
        self.info.language, self.info.encoding = self.get_language_encoding()
        self.info.environment_variables = os.environ
        self.info.arch = self.get_arch()
        self.info.languages = self.get_languages()
        self.info.distro = None
        self.info.distros = self.get_distros()
        self.fetch_host_info()
        self.info.uninstaller_path = self.get_uninstaller_path()
        self.info.previous_target_dir = self.get_previous_target_dir()
        self.info.previous_backup_dir = self.get_previous_backup_dir()
        self.info.keyboard_layout = self.get_keyboard_layout()
        self.info.total_memory_mb = self.get_total_memory_mb()
        self.info.locale = self.get_locale(self.info.language)
        self.info.iso_path, self.info.iso_distro = self.find_any_iso()
        if self.info.iso_path:
            self.info.cd_path, self.info.cd_distro = None, None
        else:
            self.info.cd_path, self.info.cd_distro = self.find_any_cd()

    def get_distros(self):
        isolist_path = join_path(self.info.datadir, 'isolist.ini')
        distros = self.parse_isolist(isolist_path)
        return distros

    def get_original_exe(self):
        #TBD
        #__file__ does not work when frozen
        #os.path.abspath(os.path.dirname(__file__))
        #os.path.abspath(sys.executable)
        if self.info.original_exe:
            original_exe = self.info.original_exe
        else:
            original_exe = abspath(sys.argv[0])
        log.debug("original_exe=%s" % original_exe)
        return original_exe

    def get_locale(self, language_country):
        locale = lang_country2linux_locale.get(language_country, None)
        if not locale:
            locale = lang_country2linux_locale.get("en_US")
        log.debug("locale=%s" % locale)
        return locale

    def get_languages(self):
        return mappings.languages

    def get_platform(self):
        platform = sys.platform
        log.debug("platform=%s" % platform)
        return platform

    def get_osname(self):
        osname = os.name
        log.debug("osname=%s" % osname)
        return osname

    def get_language_encoding(self):
        language, encoding = locale.getdefaultlocale()
        log.debug("language=%s" % language)
        log.debug("encoding=%s" % encoding)
        return language, encoding

    def get_arch(self):
        #TBD detects python/os arch not processor arch
        arch = struct.calcsize('P') == 8 and "amd64" or "i386"
        log.debug("arch=%s" % arch)
        return arch

    def create_dir_structure(self, associated_task=None):
        self.info.disksdir = join_path(self.info.target_dir, "disks")
        self.info.installdir = join_path(self.info.target_dir, "install")
        self.info.installbootdir = join_path(self.info.installdir, "boot")
        self.info.disksbootdir = join_path(self.info.disksdir, "boot")
        dirs = [
            self.info.target_dir,
            self.info.disksdir,
            self.info.installdir,
            self.info.installbootdir,
            self.info.disksbootdir,
            join_path(self.info.disksbootdir, "grub"),
            join_path(self.info.installbootdir, "grub"),]
        for d in dirs:
            if not os.path.isdir(d):
                log.debug("Creating dir %s" % d)
                os.mkdir(d)

    def fetch_installer_info(self):
        '''
        Fetch information required by the installer
        '''

    def dummy_function(self):
        time.sleep(1)

    def extract_cd_content(self, cd_path):
        if os.path.isdir(cd_path):
            return
        self.info.cddir = join_path(self.info.installdir, "cd")
        shutil.copytree(self.info.cd_path, self.info.cddir)
        return dest

    def check_metalink(self, metalink, base_url, associated_task=None):
        if self.info.skip_md5_check:
            return True
        url = base_url +"/" + self.info.distro.metalink_md5sums
        metalink_md5sums = downloader.download(url, self.info.installdir, web_proxy=self.info.web_proxy)
        url = base_url +"/" + self.info.distro.metalink_md5sums_signature
        metalink_md5sums_signature = downloader.download(url, self.info.installdir, web_proxy=self.info.web_proxy)
        if not self.verify_signature(metalink_md5sums, metalink_md5sums_signature):
            return False
        md5sums = read_file(metalink_md5sums)
        log.debug("metalink md5sums:\n%s" % md5sums)
        md5sums = dict([reversed(line.split()) for line in md5sums.split('\n') if line])
        md5sum = md5sums.get(os.path.basename(metalink))
        md5sum2 = get_file_md5(metalink)
        return md5sum == md5sum2

    def check_cd(self, cd_path, associated_task=None):
        associated_task.description = "Checking CD %s" % cd_path
        if self.info.skip_md5_check:
            return True
        md5sums_file = join_path(cd_path, self.info.distro.md5sums)
        subtasks = [
            associated_task.add_subtask(self.check_file)
            for f in self.info.distro.get_required_files()]
        for subtask in subtasks:
            if not subtask(file_path, file_path, md5sums_file):
                return False
        return True

    def check_iso(self, iso_path, associated_task=None):
        if self.info.skip_md5_check:
            return True
        md5sum = None
        if not self.info.metalink:
            log.error("ERROR: the metalink file is not available, cannot check the md5 for %s, ignoring" % iso_path)
            return True
        for hash in self.info.metalink.files[0].hashes:
            if hash.type == 'md5':
                md5sum = hash.hash
        if not md5sum:
            log.error("ERROR: Could not find any md5 hash in the metalink for the ISO %s, ignoring" % iso_path)
            return True
        get_file_md5 = associated_task.add_subtask(
            get_file_md5,
            description = "Calculating md5 for %s" % iso_path)
        md5sum2 = get_file_md5(iso_path)
        if md5sum != md5sum2:
            log.error("Invalid md5 for ISO %s" % iso_path)
            return False
        return True

    def download_iso(self, associated_task=None):
        file = self.info.metalink.files[0]
        url = file.urls[0].url
        save_as = join_path(self.info.installdir, file.name)
        iso =None
        if not self.info.no_bittorrent:
            btdownloader = associated_task.add_subtask(
                btdownlaoder.download,
                is_required = False)
            iso = btdownloader(url, save_as) #TBD get the torrent url from metalink
        if iso is None:
            download = associated_task.add_subtask(
                downlaoder.download,
                is_required = True)
            iso = downloader(url, save_as, web_proxy=self.info.web_proxy)
        return iso

    def get_metalink(self, associated_task=None):
        associated_task.description = "Retrieving metalink file..."
        self.info.metalink = None
        try:
            metalink = downloader.download(self.info.distro.metalink, self.info.installdir, web_proxy=self.info.web_proxy)
            base_url = os.path.dirname(self.info.distro.metalink)
        except:
            log.error("Cannot download metalink file %s" % self.info.distro.metalink)
            try:
                metalink = downloader.download(self.info.distro.metalink2, self.info.installdir, web_proxy=self.info.web_proxy)
                base_url = os.path.dirname(self.info.distro.metalink2)
            except:
                log.error("Cannot download metalink file2 %s" % self.info.distro.metalink2)
                return
        if not self.check_metalink(metalink, base_url):
            log.exception("Cannot authenticate the metalink file, it might be corrupt")
        self.info.metalink = parse_metalink(metalink)

    def get_iso(self, associated_task=None):
        #Use pre-specified ISO
        if self.info.iso_path \
        and os.path.exists(self.info.iso_path):
            #TBD shall we do md5 check? Doesn't work well with daylies
            #TBD if a specified ISO cannot be used notify the user
            is_valid_iso = associated_task.add_subtask(
                self.info.distro.is_valid_iso,
                description = "Validating %s" % self.info.iso_path)
            if is_valid_iso(self.info.iso_path):
                self.info.cd_path = None
                return associated_task.finish()

        # Use CD if possible
        cd_path = None
        if self.info.cd_distro \
        and self.info.distro == self.info.cd_distro \
        and os.path.isdir(self.info.cd_path):
            cd_path = self.info.cd_path
        else:
            cd_path = self.find_cd()
        if cd_path:
            check_cd = associated_task.add_subtask(
                self.check_cd,
                description = "Checking %s" % cd_path, )
            extract_cd_content = associated_task.add_subtask(
                self.extract_cd_content,
                description = "Extracting files from %s" % cd_path)
            if check_cd(cd_path):
                cd_path = extract_cd_content(cd_path)
                self.info.cd_path = cd_path
                self.info.iso_path = None
                return associated_task.finish()

        #Use local ISO if possible
        iso_path = None
        if self.info.iso_distro \
        and self.info.distro == self.info.iso_distro \
        and os.path.isfile(self.info.iso_path):
            iso_path = self.info.iso_path
        else:
            iso_path = self.find_iso()
        if iso_path:
            iso_name = os.path.basename(iso_path)
            dest = join_path(self.info.installdir, iso_name)
            check_iso = associated_task.add_subtask(
                self.check_iso,
                description = "Checking %s" % iso_path)
            if check_iso(iso_path):
                if os.path.dirname(iso_path) == self.info.previous_backup_dir:
                    move_iso = associated_task.add_subtask(
                        shutil.move,
                        description = "Moving %s > %s" % (iso_path, dest))
                    move_iso(iso_path, dest)
                else:
                    copy_iso = associated_task.add_subtask(
                        copy_file,
                        description = "Copying %s > %s" % (iso_path, dest),)
                    copy_iso(iso_path, dest)
                self.info.cd_path = None
                self.info.iso_path = dest
                return associated_task.finish()

        # Download the ISO
        log.debug("Could not find any ISO or CD, downloading one now")
        self.info.cd_path = None
        download_iso = associated_task.add_subtask(
            self.download_iso,
            description = "Downloading ISO")
        check_iso = associated_task.add_subtask(
            self.check_iso,
            description = "Checking ISO")
        self.info.iso_path = download_iso()
        if not self.info.iso_path:
            raise Exception("Could not retrieve the installation ISO")
        elif not check_iso(self.info.iso_path):
            raise Exception("ISO file is corrupted")

    def extract_kernel(self):
        bootdir = self.info.installbootdir
        # Extract kernel, initrd, md5sums
        if self.info.cd_path:
            log.debug("Copying files from mounted CD %s" % self.info.cd_path)
            for src in [
            join_path(self.info.cddir, self.info.distro.md5sums),
            join_path(self.info.cddir, self.info.distro.kenel),
            join_path(self.info.cddir, self.info.distro.initrd),]:
                shutil.copyfile(src, bootdir)
        else:
            log.debug("Extracting files from ISO %s" % self.info.iso_path)
            self.extract_file_from_iso(self.info.iso_path, self.info.distro.md5sums, output_dir=bootdir)
            self.extract_file_from_iso(self.info.iso_path, self.info.distro.kernel, output_dir=bootdir)
            self.extract_file_from_iso(self.info.iso_path, self.info.distro.initrd, output_dir=bootdir)

        # Check the files
        log.debug("Checking files")
        self.info.kernel = join_path(bootdir, os.path.basename(self.info.distro.kernel))
        self.info.initrd = join_path(bootdir, os.path.basename(self.info.distro.initrd))
        md5sums = join_path(bootdir, os.path.basename(self.info.distro.md5sums))
        paths = [
            (self.info.kernel, self.info.distro.kernel),
            (self.info.initrd, self.info.distro.initrd),]
        for file_path, rel_path in paths:
                if not self.check_file(file_path, rel_path, md5sums):
                    raise Exception("File %s is corrupted" % file_path)

    def check_file(self, file_path, relpath, md5sums, associated_task=None):
        log.debug("  checking %s" % file_path)
        if associated_task:
            associated_task.description = "Checking %s" % file_path
        relpath = relpath.replace("\\", "/")
        md5line = find_line_in_file(md5sums, "./%s" % relpath, endswith=True)
        if not md5line:
            raise Exception("Cannot find md5 for %s" % relpath)
        reference_md5 = md5line.split()[0]
        md5  = get_file_md5(file_path, associated_task)
        return md5 == reference_md5

    def create_preseed(self):
        template_file = join_path(self.info.datadir, 'preseed.lupin')
        template = read_file(template_file)
        partitioning = '''
        d-i partman-auto/disk string LIDISK
        d-i partman-auto/method string loop
        d-i partman-auto-loop/partition string LIPARTITION
        d-i partman-auto-loop/recipe string   \
        '''
        if self.info.root_size_mb:
            partitioning += '%s 3000 %s %s ext3 method{ format } format{ } use_filesystem{ } filesystem{ ext3 } mountpoint{ / } .' \
            %(join_path(self.info.disksdir, 'root.disk'), self.info.root_size_mb, self.info.root_size_mb)
        if self.info.swap_size_mb:
            partitioning += '%s 100 %s %s linux-swap method{ swap } format{ } .' \
            %(join_path(self.info.disksdir, 'swap.disk'), self.info.swap_size_mb, self.info.swap_size_mb)
        if self.info.home_size_mb:
            partitioning += '%s 100 %s %s ext3 method{ format } format{ } use_filesystem{ } filesystem{ ext3 } mountpoint{ /home } .' \
            %(join_path(self.info.disksdir, 'home.disk'), self.info.home_size_mb, self.info.home_size_mb)
        if self.info.usr_size_mb:
            partitioning += '%s 100 %s %s ext3 method{ format } format{ } use_filesystem{ } filesystem{ ext3 } mountpoint{ /usr } .' \
            %(join_path(self.info.disksdir, 'usr.disk'), self.info.usr_size_mb, self.info.usr_size_mb)
        safe_host_username = self.info.host_username.replace(" ", "+")
        user_directory = self.info.user_directory.replace("\\", "/")[2:]
        host_os_name = "Windows XP Professional"
        dic = dict(
            timezone = self.info.timezone,
            password = self.info.password,
            user_full_name = self.info.user_full_name,
            distro_packages = self.info.distro.packages,
            host_username = self.info.host_username,
            user_name = self.info.username,
            partitioning = partitioning,
            user_directory = user_directory,
            safe_host_username = safe_host_username,
            host_os_name = host_os_name,)
        content = template % dic
        preseed_file = join_path(self.info.custominstall, "preseed.conf")
        write_file(preseed_file, content)

    def modify_bootloader(self):
        #platform specific
        pass

    def modify_grub_configuration(self):
        template_file = join_path(self.info.datadir, 'menu.install')
        if self.info.cd_path:
            isopath = unixpath(self.info.cd_path)
        elif self.info.iso_path:
            isopath = unixpath(self.info.iso_path)
        dic = dict(
            custominstallationdir = unixpath(self.info.custominstall),
            isopath = isopath,
            keyboardvariant = self.info.keyboardvariant,
            locale = self.info.locale,
            layoutcode = self.info.layoutcode,
            accessibility = self.info.accessibility,
            kernel = unixpath(self.info.kernel),
            initrd = unixpath(self.info.initrd),
            normal_mode_title = "Normal mode",
            safe_graphic_mode_title = "Safe graphic mode",
            acpi_workarounds_title = "ACPI workarounds",
            verbose_mode_title = "Verbose mode",
            demo_mode_title =  "Demo mode",
            )
        content = template_file % dic
        grub_config_file = join_path(self.info.installbootdir, "grub", "menu.lst")
        write_file(grub_config_file, content)

    def remove_target_dir(self, associated_task=None):
        if not os.path.isdir(self.info.previous_target_dir):
            log.debug("Cannot find %s" % self.info.previous_target_dir)
            return
        log.debug("Deleting %s" % self.info.previous_target_dir)
        shutil.rmtree(self.info.previous_target_dir)

    def find_iso(self, associated_task=None):
        log.debug("Searching for local ISO")
        for path in self.get_iso_search_paths():
            path = join_path(path, '*.iso')
            isos = glob.glob(path)
            for iso in isos:
                if self.info.distro.is_valid_iso(iso):
                    return iso

    def find_any_iso(self):
        '''
        look for USB keys with ISO or pre specified ISO
        '''
        #Use pre-specified ISO
        if self.info.iso_path \
        and os.path.exists(self.info.iso_path):
            log.debug("Checking pre-specified ISO %s" % self.info.iso_path)
            for distro in self.info.distros:
                if distro.is_valid_iso(self.info.iso_path):
                    self.info.cd_path = None
                    return self.info.iso_path, distro
        #Search USB devices
        log.debug("Searching ISOs on USB devices")
        for path in self.get_usb_search_paths():
            path = join_path(path, '*.iso')
            isos = glob.glob(path)
            for iso in isos:
                for distro in self.info.distros:
                    if distro.is_valid_iso(iso):
                        return iso, distro
        return None, None

    def find_any_cd(self):
        log.debug("Searching for local CDs")
        for path in self.get_cd_search_paths():
            path = abspath(path)
            for distro in self.info.distros:
                if distro.is_valid_cd(path):
                    return path, distro
        return None, None

    def find_cd(self):
        log.debug("Searching for local CD")
        for path in self.get_cd_search_paths():
            path = abspath(path)
            if self.info.distro.is_valid_cd(path):
                return path

    def get_previous_target_dir(self):
        if not self.info.uninstaller_path: return
        if not os.path.exists(self.info.uninstaller_path): return
        previous_target_dir = os.path.dirname(self.info.uninstaller_path)
        log.debug("Previous_target_dir=%s" % previous_target_dir)
        return previous_target_dir

    def parse_isolist(self, isolist_path):
        log.debug('Parsing isolist=%s' % isolist_path)
        isolist = ConfigParser.ConfigParser()
        isolist.read(isolist_path)
        distros = []
        for distro in isolist.sections():
            log.debug('  Adding distro %s' % distro)
            kargs = dict(isolist.items(distro))
            kargs['backend'] = self
            distros.append(Distro(**kargs))
            #order is lost in configparser, use the ordering attribute
        def compfunc(x, y):
            if x.ordering == y.ordering:
                return 0
            elif x.ordering > y.ordering:
                return 1
            else:
                return -1
        distros.sort(compfunc)
        return distros
