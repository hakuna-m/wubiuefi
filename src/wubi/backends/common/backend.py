# USEFUL LINKS http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/180919
# about creating files, detecting drives...

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
import ConfigParser
from helpers import *
from metalink import parse_metalink
from tasklist import ThreadedTaskList
from distro import Distro
from backends.common.mappings import lang_country2linux_locale
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
        self.info.keyboard_layout = self.get_keyboard_layout()
        self.info.total_memory_mb = self.get_total_memory_mb()
        self.info.locale = self.get_locale(self.info.language)
        self.info.cd_path, self.info.cd_distro = self.find_any_cd()
        #~ self.info.iso_path,  self.info.iso_distro = self.find_any_iso()

    def get_distros(self):
        isolist_path = os.path.join(self.info.datadir, 'isolist.ini')
        distros = self.parse_isolist(isolist_path)
        return distros

    def get_original_exe(self):
        #TBD
        #__file__ does not work when frozen
        #os.path.abspath(os.path.dirname(__file__))
        #os.path.abspath(sys.executable)
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
        arch = struct.calcsize('P') == 8 and 64 or 32
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

    def check_cd(self, cd_path):
        pass

    def check_iso(self, iso_path):
        pass

    def download_metalink(self):
        pass

    def download_iso(self):
        pass

    def get_iso(self):
        # Use CD if possible
        cd_path = None
        if self.info.distro == self.info.cd_distro \
        and os.path.isdir(self.info.cd_path):
            cd_path = self.info.cd_path
        else:
            cd_path = self.find_cd()
        if cd_path:
            if self.check_cd(cd_path):
                cd_path = self.extract_cd_content(cd_path)
                self.info.cd_path = cd_path
                self.info.iso_path = None
                return

        #Use local ISO if possible
        iso_path = None
        if self.info.distro == self.info.iso_distro \
        and os.path.isfile(self.info.iso_path):
            iso_path = self.info.iso_path
        else:
            iso_path = self.find_iso()
        if iso_path:
            iso_name = os.path.basename(iso_path)
            dest = os.path.join(self.info.installdir, iso_name)
            if self.check_iso(iso_path):
                if os.path.dirname(iso_path) == self.info.backupdir:
                    shutil.move(iso_path, dest)
                else:
                    shutil.copyfile(iso_path, dest)
                self.info.cd_path = None
                self.info.iso_path = dest
                return

        # Download the ISO
        self.info.cd_path = None
        self.info.iso_path = self.download_iso()
        if not self.info.iso_path:
            raise Exception("Could not retrieve the installation ISO")

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

    def check_file(self, file_path, relpath, md5sums):
        md5line = find_line_in_file(md5sums, "./%s" % relpath, endswith=True)
        if not md5line:
            raise Exception("Cannot find md5 for %s" % relpath)
        reference_md5 = md5line.split()[0]
        #TBD break in 100 chunks
        f = open(file_path, 'r')
        content = f.read()
        f.close()
        hash = md5(content)
        md5 = hash.digest()
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
            ("Selecting target directory", self.select_target_dir),
            ("Creating the installation directories", self.create_dir_structure),
            ("Creating the uninstaller", self.create_uninstaller),
            ("Copying files", self.copy_installation_files),
            ("Retrieving the ISO", self.get_iso),
            ("Extracting the kernel", self.extract_kernel),
            ("Uncompressing files", self.uncompress_files),
            ("Choosing disk sizes", self.choose_disk_sizes),
            ("Creating a preseed file", self.create_preseed),
            ("Adding a new bootlader entry", self.modify_bootloader),
            ("Creating the virtual disks", self.create_virtual_disks),
            ("Uncompressing files", self.uncompress_files),
            ("Ejecting the CD", self.eject_cd),
            ("Rebooting", self.reboot),
        ]
        tasklist = ThreadedTaskList("Installing", tasks=tasks)
        return tasklist

    def find_any_iso(self):
        log.debug('searching for local ISOs')
        for path in self.get_iso_search_paths():
            path = os.path.abspath(path)
            path = os.path.join(path, '*.iso')
            isos = glob.glob(path)
            for iso in isos:
                for distro in self.info.distros.values():
                    if distro.is_valid_iso(iso):
                        return iso, distro
        return None, None

    def find_iso(self):
        log.debug('searching for local ISOs')
        for path in self.get_iso_search_paths():
            path = os.path.abspath(path)
            path = os.path.join(path, '*.iso')
            isos = glob.glob(path)
            for iso in isos:
                if self.info.distro.is_valid_iso(iso):
                    return iso

    def find_any_cd(self):
        log.debug('searching for local CDs')
        for path in self.get_cd_search_paths():
            path = os.path.abspath(path)
            for distro in self.info.distros.values():
                if distro.is_valid_cd(path):
                    return path, distro
        return None, None

    def find_cd(self):
        log.debug('searching for local CDs')
        for path in self.get_cd_search_paths():
            path = os.path.abspath(path)
            if self.distro.is_valid_cd(path):
                return path

    def get_previous_targetdir(self):
        if not self.info.uninstaller_path: return
        if not os.path.exists(self.info.uninstaller_path): return
        previous_targetdir = os.path.dirname(self.info.uninstaller_path)
        return previous_targetdir

    def parse_isolist(self, isolist_path):
        isolist = ConfigParser.ConfigParser()
        isolist.read(isolist_path)
        distros = {}
        for distro in isolist.sections():
            kargs = dict(isolist.items(distro))
            kargs['backend'] = self
            distros[distro] = Distro(**kargs)
        return distros
