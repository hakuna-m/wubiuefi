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
from utils import run_command, copy_file, replace_line_in_file, read_file, write_file, get_file_md5, reversed, find_line_in_file, unixpath

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
            rootdir = os.path.dirname(os.path.abspath(sys.executable))
            tempdir = tempfile.mkdtemp(dir=rootdir)
        else:
            rootdir = ''
            tempdir = tempfile.mkdtemp()
        self.info.rootdir = os.path.abspath(rootdir)
        self.info.tempdir = os.path.abspath(tempdir)
        self.info.datadir = os.path.join(self.info.rootdir, 'data')
        self.info.bindir = os.path.join(self.info.rootdir, 'bin')
        self.info.imagedir = os.path.join(self.info.datadir, "images") #os.path.join(self.info.datadir, "images")
        log.debug('datadir=%s' % self.info.datadir)

    def change_language(self, codeset):
        domain = self.info.application_name #not sure what it is
        localedir = os.path.join(self.info.datadir, 'locale')
        self.info.codeset = codeset # set the language
        gettext.install(domain, codeset=codeset)

    def fetch_basic_info(self):
        '''
        Basic information required by the application dispatcher select_task()
        '''
        self.info.original_exe = self.get_original_exe()
        self.info.platform = self.get_platform()
        self.info.osname = self.get_osname
        self.info.language, self.info.encoding = self.get_language_encoding()
        self.info.environment_variables = os.environ
        self.info.arch = self.get_arch()
        self.info.languages = self.get_languages()
        self.info.distros = self.get_distros()
        self.fetch_basic_os_specific_info()
        self.info.uninstaller_path = self.get_uninstaller_path()
        self.info.previous_targetdir = self.get_previous_targetdir()
        self.info.previous_backupdir = self.get_previous_backupdir()
        self.info.keyboard_layout = self.get_keyboard_layout()
        self.info.total_memory_mb = self.get_total_memory_mb()
        self.info.locale = self.get_locale(self.info.language)
        self.info.iso_path, self.info.iso_distro = self.find_any_iso()
        if self.info.iso_path:
            self.info.cd_path, self.info.cd_distro = None, None
        else:
            self.info.cd_path, self.info.cd_distro = self.find_any_cd()

    def get_distros(self):
        isolist_path = os.path.join(self.info.datadir, 'isolist.ini')
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
            original_exe = os.path.abspath(sys.argv[0])
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

    def create_dir_structure(self):
        self.info.disksdir = os.path.join(self.info.targetdir, "disks")
        self.info.installdir = os.path.join(self.info.targetdir, "install")
        self.info.installbootdir = os.path.join(self.info.installdir, "boot")
        self.info.disksbootdir = os.path.join(self.info.disksdir, "boot")
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

    def fetch_installer_info(self):
        '''
        Fetch information required by the installer
        '''

    def dummy_function(self):
        time.sleep(1)

    def extract_cd_content(self, cd_path):
        if os.path.isdir(cd_path):
            return
        self.info.cddir = os.path.join(self.info.installdir, "cd")
        shutil.copytree(self.info.cd_path, self.info.cddir)
        return dest

    def check_metalink(self, metalink, base_url):
        if self.info.skipmd5check:
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

    def check_cd(self, cd_path, associated_task):
        if self.info.skipmd5check:
            return True
        md5sums_file = os.path.join(cd_path, self.info.distro.md5sums)
        subtasks = [
            associated_task.add_subtask("Checking %s" % f, self.check_file)
            for f in self.info.distro.get_required_files()]
        for subtask in subtasks:
            if not subtask.run(file_path, file_path, md5sums_file):
                return False
        return True

    def check_iso(self, iso_path, associated_task=None):
        if self.info.skipmd5check:
            return True
        md5sum = None
        if not self.info.metalink:
            log.error("The metalink file is not available, cannot check the md5 for %s, hoping for the better..." % iso_path)
            return True
        for hash in self.info.metalink.files[0].hashes:
            if hash.type == 'md5':
                md5sum = hash.hash
        if not md5sum:
            log.error("Could not find any md5 hash in the metalink for the ISO %s, ignoring" % iso_path)
            return True
        log.debug("Calculating md5 for %s" % iso_path)
        md5sum2 = get_file_md5(iso_path, associated_task)
        if md5sum != md5sum2:
            log.error("Invalid md5 for ISO %s" % iso_path)
            return False
        return True

    def download_iso(self, associated_task):
        log.debug("download_iso")
        file = self.info.metalink.files[0]
        url = file.urls[0].url
        save_as = os.path.join(self.info.installdir, file.name)
        iso =None
        if not self.info.nobittorrent:
            btdownloader = self.associated_task.add_subtask(
                "Downloading %s" % url, #TBD get the torrent url from metalink
                btdownlaoder.download,
                is_required = False)
            iso = btdownloader.run(url, save_as)
        if iso is None:
            download = self.associated_task.add_subtask(
                "Downloading %s" % url,
                downlaoder.download,
                is_required = True)
            iso = downloader.run(url, save_as, web_proxy=self.info.web_proxy)
        return iso

    def get_metalink(self):
        log.debug("get_metalink")
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
                log.error("Cannot download metalink file2 %s" % self.info.distro.metalink)
                return
        if not self.check_metalink(metalink, base_url):
            log.exception("Cannot authenticate the metalink file, it might be corrupt")
        self.info.metalink = parse_metalink(metalink)

    def get_iso(self, associated_task):
        #Use pre-specified ISO
        if self.info.iso_path \
        and os.path.exists(self.info.iso_path):
            #TBD shall we do md5 check? Doesn't work well with daylies
            #TBD if a specified ISO cannot be used notify the user
            is_valid_iso = associated_task.add_subtask(
                "Validating %s" % self.info.iso_path, self.info.distro.is_valid_iso)
            if is_valid_iso.run(self.info.iso_path):
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
                "Checking %s" % cd_path, self.check_cd)
            extract_cd_content = associated_task.add_subtask(
                "Extracting files from %s" % cd_path, self.extract_cd_content)
            if check_cd.run(cd_path):
                cd_path = extract_cd_content.run(cd_path)
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
            dest = os.path.join(self.info.installdir, iso_name)
            check_iso = associated_task.add_subtask(
                "Checking %s" % iso_path, self.check_iso)
            move_iso = associated_task.add_subtask(
                "Moving %s > %s" % (iso_path, dest), shutil.move)
            copy_iso = associated_task.add_subtask(
                "Copying %s > %s" % (iso_path, dest), copy_file)
            if check_iso.run(iso_path):
                if os.path.dirname(iso_path) == self.info.previous_backupdir:
                    move_iso.run(iso_path, dest)
                else:
                    copy_file.run(iso_path, dest)
                self.info.cd_path = None
                self.info.iso_path = dest
                return associated_task.finish()

        # Download the ISO
        log.debug("Could not find any ISO or CD, downloading one now")
        self.info.cd_path = None
        download_iso = associated_task.add_subtask(
            "Downloading ISO", self.check_iso)
        check_iso = associated_task.add_subtask(
            "Checking %s" % iso_path, self.check_iso)
        self.info.iso_path = download_iso.run()
        if not self.info.iso_path:
            raise Exception("Could not retrieve the installation ISO")
        elif not check_iso.run(iso_path):
            raise Exception("ISO file is corrupted")
        return associated_task.finish()

    def extract_kernel(self):
        bootdir = self.info.installbootdir
        # Extract kernel, initrd, md5sums
        if self.info.cd_path:
            for src in [
            os.path.join(self.info.cddir, self.info.distro.md5sums),
            os.path.join(self.info.cddir, self.info.distro.kenel),
            os.path.join(self.info.cddir, self.info.distro.initrd),]:
                shutil.copyfile(src, bootdir)
        else:
            self.extract_file_from_iso(self.info.iso_path, self.info.distro.md5sums, output_dir=bootdir)
            self.extract_file_from_iso(self.info.iso_path, self.info.distro.kernel, output_dir=bootdir)
            self.extract_file_from_iso(self.info.iso_path, self.info.distro.initrd, output_dir=bootdir)

        # Check the files
        self.info.kernel = os.path.join(bootdir, os.path.basename(self.info.distro.kernel))
        self.info.initrd = os.path.join(bootdir, os.path.basename(self.info.distro.initrd))
        md5sums = os.path.join(bootdir, os.path.basename(self.info.distro.md5sums))
        paths = [
            (self.info.kernel, self.info.distro.kernel),
            (self.info.initrd, self.info.distro.initrd),]
        for file_path, rel_path in paths:
                if not self.check_file(file_path, rel_path, md5sums):
                    raise Exception("File %s is corrupted" % file_path)

    def check_file(self, file_path, relpath, md5sums, associated_task=None):
        relpath = relpath.replace("\\", "/")
        log.debug("find_line_in_file(%s, %s)" % (md5sums, "./%s" % relpath))
        md5line = find_line_in_file(md5sums, "./%s" % relpath, endswith=True)
        if not md5line:
            raise Exception("Cannot find md5 for %s" % relpath)
        reference_md5 = md5line.split()[0]
        md5  = get_file_md5(file_path, associated_task)
        log.debug("Checking %s ref_md5=%s calculated_md5=%s" % (file_path, reference_md5, md5))
        return md5 == reference_md5

    def choose_disk_sizes(self):
        total_size_mb = self.info.installation_size_mb
        home_size_mb = 0
        usr_size_mb = 0
        swap_size_mb = 256
        root_size_mb = total_size_mb - swap_size_mb
        if self.info.installation_drive.filesystem == "vfat":
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
        self.info.swap.size_mb = swap_size_mb
        self.info.root_size_mb = root_size_mb
        log.debug("total size: %s\nroot size: %s\nswap size: %s\nhome size: %s\n usr size: %s" % (total_size_mb, root_size_mb, swap_size_mb, home_size_mb, usr_size_mb))

    def create_preseed(self):
        template_file = os.path.join(self.info.datadir, 'preseed.lupin')
        template = read_file(template_file)
        partitioning = '''
        d-i partman-auto/disk string LIDISK
        d-i partman-auto/method string loop
        d-i partman-auto-loop/partition string LIPARTITION
        d-i partman-auto-loop/recipe string   \
        '''
        if self.info.root_size_mb:
            partitioning += '  %s 3000 %s %s ext3 method{ format } format{ } use_filesystem{ } filesystem{ ext3 } mountpoint{ / } .' \
            %(os.path.join(self.info.disksdir, 'root.disk'), self.info.root_size_mb, self.info.root_size_mb)
        if self.info.swap_size_mb:
            partitioning += '  %s 100 %s %s linux-swap method{ swap } format{ } .' \
            %(os.path.join(self.info.disksdir, 'swap.disk'), self.info.swap_size_mb, self.info.swap_size_mb)
        if self.info.home_size_mb:
            partitioning += '  %s 100 %s %s ext3 method{ format } format{ } use_filesystem{ } filesystem{ ext3 } mountpoint{ /home } .' \
            %(os.path.join(self.info.disksdir, 'home.disk'), self.info.home_size_mb, self.info.home_size_mb)
        if self.info.usr_size_mb:
            partitioning += '  %s 100 %s %s ext3 method{ format } format{ } use_filesystem{ } filesystem{ ext3 } mountpoint{ /usr } .' \
            %(os.path.join(self.info.disksdir, 'usr.disk'), self.info.usr_size_mb, self.info.usr_size_mb)
        safe_host_user_name = self.info.host_user_name.replace(" ", "+")
        user_directory = self.info.user_directory.replace("\\", "/")[2:]
        host_os_name = "Windows XP Professional"
        dic = dict(
            timezone = self.info.timezone,
            partitioning = partitioning,
            password = self.info.user_password,
            user_name = self.info.user_name,
            user_full_name = self.info.user_full_name,
            user_directory = self.info.user_directory,
            distro_packages = self.info.distro_packages,
            host_user_name = self.info.host_user_name,
            safe_host_user_name = safe_host_user_name,
            host_os_name = host_os_name,)
        content = template % dic
        preseed_file = os.path.join(self.info.custominstall, "preseed.conf")
        write_file(preseed_file, content)

    def modify_bootloader(self):
        #platform specific
        pass

    def modify_grub_configuration(self):
        template_file = os.path.join(self.info.datadir, 'menu.install')
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
        grub_config_file = os.path.join(self.info.installbootdir, "grub", "menu.lst")
        write_file(grub_config_file, content)

    def get_installation_tasklist(self):
        tasks = [
            Task("Selecting target directory", self.select_target_dir),
            Task("Creating the installation directories", self.create_dir_structure),
            Task("Creating the uninstaller", self.create_uninstaller),
            Task("Copying files", self.copy_installation_files, True, weight=5),
            Task("Retrieving the Metalink", self.get_metalink, True, weight=10),
            Task("Retrieving the ISO", self.get_iso, True, weight=1000),
            Task("Extracting the kernel", self.extract_kernel, True, weight=5),
            Task("Uncompressing files", self.uncompress_files),
            Task("Choosing disk sizes", self.choose_disk_sizes),
            Task("Creating a preseed file", self.create_preseed),
            Task("Adding a new bootlader entry", self.modify_bootloader),
            Task("Creating the virtual disks", self.create_virtual_disks),
            Task("Uncompressing files", self.uncompress_files),
            Task("Ejecting the CD", self.eject_cd),
            Task("Rebooting", self.reboot),
        ]
        tasklist = ThreadedTaskList("Installing", tasks=tasks)
        return tasklist

    def get_uninstallation_tasklist(self):
        tasks = [
            ("Backup ISO", self.backup_iso),
            ("Remove bootloader entry", self.undo_bootloader),
            ("Remove target dir", self.remove_targetdir),
            ("Remove registry key", self.remove_registry_key),
            ]
        tasklist = ThreadedTaskList("Uninstalling", tasks=tasks)
        return tasklist

    def backup_iso(self):
        log.debug("Backing up ISOs")
        backupdir = os.path.join(self.info.previous_targetdir[:2], '/', "%s.backup" % self.info.application_name)
        installdir = os.path.join(self.info.previous_targetdir, "install")
        if not os.path.isdir(installdir):
            return
        for f in os.listdir(self.info.previous_targetdir):
            f = os.path.join(self.info.previous_targetdir, f)
            if not f.endswith('.iso') \
            or not os.path.isfile(f) \
            or os.path.getsize(f) < 1000000:
                continue
            log.debug("Backing up %s -> %s" % (f, backupdir))
            shutil.copy(f, backupdir)

    def remove_targetdir(self):
        if not os.path.isdir(self.info.previous_targetdir):
            log.debu("Cannot find %s" % self.info.previous_targetdir)
            return
        log.debug("Deleting %s" % self.info.previous_targetdir)
        shutil.rmtree(self.info.previous_targetdir)

    def find_iso(self):
        log.debug('searching for local ISOs')
        for path in self.get_iso_search_paths():
            path = os.path.abspath(path)
            path = os.path.join(path, '*.iso')
            isos = glob.glob(path)
            for iso in isos:
                if self.info.distro.is_valid_iso(iso):
                    return iso

    def find_any_iso(self):
        '''
        look for usb keys with ISO or pre specified ISO
        '''
        log.debug('searching for local ISOs')
        #Use pre-specified ISO
        if self.info.iso_path \
        and os.path.exists(self.info.iso_path):
            for distro in self.info.distros:
                if distro.is_valid_iso(self.info.iso_path):
                    self.info.cd_path = None
                    return self.info.iso_path, distro
        #Search USB devices
        for path in self.get_usb_search_paths():
            path = os.path.abspath(path)
            path = os.path.join(path, '*.iso')
            isos = glob.glob(path)
            for iso in isos:
                for distro in self.info.distros:
                    if distro.is_valid_iso(iso):
                        return iso, distro
        return None, None

    def find_any_cd(self):
        log.debug('searching for local CDs')
        for path in self.get_cd_search_paths():
            path = os.path.abspath(path)
            for distro in self.info.distros:
                if distro.is_valid_cd(path):
                    return path, distro
        return None, None

    def find_cd(self):
        log.debug('searching for local CDs')
        for path in self.get_cd_search_paths():
            path = os.path.abspath(path)
            if self.info.distro.is_valid_cd(path):
                return path

    def get_previous_backupdir(self):
        if self.info.previous_targetdir:
            drives = [self.info.previous_targetdir[:2] + "\\"]
        else:
            drives = []
        drives += [d.path + "\\" for d in self.info.drives]
        for drive in drives:
            backupdir = os.path.join(drive, '/', "%s.backup" % self.info.application_name)
            if os.path.isdir(backupdir):
                log.debug("Previous_backupdir=%s"%backupdir)
                return backupdir

    def get_previous_targetdir(self):
        if not self.info.uninstaller_path: return
        if not os.path.exists(self.info.uninstaller_path): return
        previous_targetdir = os.path.dirname(self.info.uninstaller_path)
        return previous_targetdir

    def parse_isolist(self, isolist_path):
        log.debug('Parsing isolist=%s' % isolist_path)
        isolist = ConfigParser.ConfigParser()
        isolist.read(isolist_path)
        distros = []
        for distro in isolist.sections():
            log.debug('Adding distro %s' % distro)
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
