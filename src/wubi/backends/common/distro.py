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

import os
from utils import read_file
import logging
import re

log = logging.getLogger('Distro')
disk_info_re = '''(?P<name>[\w\s-]+) (?P<version>[\d.]+)(?: LTS)? \"(?P<codename>[\D]+)\" - (?P<subversion>[\D]+) (?P<arch>i386|amd64) \((?P<build>[\d.]+)\)'''
disk_info_re = re.compile(disk_info_re)

class Distro(object):

    cache = {}

    def __init__(
            self, name, version, kernel, initrd,
            info_file, arch, metalink, metalink2,
            packages, size, md5sums, files_to_check,
            metalink_md5sums, metalink_md5sums_signature,
            backend, ordering, website, support, min_disk_space_mb,
            min_memory_mb, installation_dir, diskimage=None, diskimage2=None,
            min_iso_size=0, max_iso_size=0):
        self.name = name
        self.version = version
        self.arch = arch
        self.kernel = os.path.normpath(kernel)
        self.initrd = os.path.normpath(initrd)
        self.md5sums = os.path.normpath(md5sums)
        self.info_file = os.path.normpath(info_file)
        self.size = size and int(size) or 0
        self.min_iso_size = min_iso_size and int(min_iso_size) or 0
        self.max_iso_size = max_iso_size and int(max_iso_size) or 0
        self.min_disk_space_mb = int(min_disk_space_mb)
        self.min_memory_mb = int(min_memory_mb)
        self.metalink_md5sums = metalink_md5sums
        self.metalink_md5sums_signature = metalink_md5sums_signature
        self.metalink_url = metalink
        self.metalink_url2 = metalink2
        self.metalink = None
        self.packages = packages
        self.backend = backend
        self.ordering = ordering
        self.website = website
        self.support = support
        self.installation_dir = installation_dir
        self.diskimage = diskimage
        self.diskimage2 = diskimage2

        if isinstance(files_to_check, basestring):
            files_to_check = [
                os.path.normpath(f.strip().lower())
                for f in files_to_check.split(',')]
        self.files_to_check = files_to_check

    def is_valid_cd(self, cd_path, check_arch):
        cd_path = os.path.abspath(cd_path)
        log.debug('  checking whether %s is a valid %s CD' % (cd_path, self.name))
        if not os.path.isdir(cd_path):
            log.debug('    dir does not exist')
            return False
        required_files = self.get_required_files()
        for file in required_files:
            file = os.path.join(cd_path, file)
            if not os.path.isfile(file):
                log.debug('    does not contain %s' % file)
                return False
        info = self.get_info(cd_path)
        if self.check_info(info, check_arch):
            log.info('Found a valid CD for %s: %s' % (self.name, cd_path))
            return True
        else:
            return False

    def is_valid_dimage(self, dimage_path, check_arch):
        '''
        Validate a disk image

        TBD: Add more checks
        '''
        dimage_path = os.path.abspath(dimage_path)
        log.debug('  checking %s diskimage %s' % (self.name, dimage_path))
        if not os.path.isfile(dimage_path):
            log.debug('    file does not exist')
            return False
        return True

    def is_valid_iso(self, iso_path, check_arch):
        iso_path = os.path.abspath(iso_path)
        log.debug('  checking %s ISO %s' % (self.name, iso_path))
        if not os.path.isfile(iso_path):
            log.debug('    file does not exist')
            return False
        files = self.backend.get_iso_file_names(iso_path)
        files = [f.strip().lower() for f in files]
        required_files = self.get_required_files()
        for file in required_files:
            if file.strip().lower() not in files:
                log.debug('    does not contain %s' % file)
                return False
        info = self.get_info(iso_path)
        if self.check_info(info, check_arch):
            log.info('Found a valid iso for %s: %s' % (self.name, iso_path))
            return True
        else:
            return False

    def get_info(self, cd_or_iso_path):
        if (cd_or_iso_path, self.info_file) in Distro.cache:
            return Distro.cache[(cd_or_iso_path, self.info_file)]
        else:
            Distro.cache[(cd_or_iso_path, self.info_file)] = None
            if os.path.isfile(cd_or_iso_path):
                info_file = self.backend.extract_file_from_iso(
                    cd_or_iso_path,
                    self.info_file,
                    output_dir=self.backend.info.temp_dir,
                    overwrite=True)
            elif os.path.isdir(cd_or_iso_path):
                info_file = os.path.join(cd_or_iso_path, self.info_file)
            else:
                return
            if not info_file or not os.path.isfile(info_file):
                return
            try:
                info = read_file(info_file)
                info = self.parse_isoinfo(info)
            except Exception, err:
                log.error(err)
                return
            Distro.cache[(cd_or_iso_path, self.info_file)] = info
            return info

    def get_required_files(self):
        required_files = self.files_to_check[:]
        required_files += [
            self.kernel,
            self.initrd,
            self.info_file,
            self.md5sums,]
        return required_files

    def check_info(self, info, check_arch):
        if not info:
            log.debug('could not get info %s' % info)
            return False
        name, version, subversion, arch = info # used in backend as well
        if self.name and name != self.name:
            log.debug('wrong name: %s != %s' % (name, self.name))
            return False
        if self.version and not (version == self.version or version.startswith(self.version + '.')):
            log.debug('wrong version: %s != %s' % (version, self.version))
            return False
        if check_arch and self.arch and arch != self.arch:
            log.debug('wrong arch: %s != %s' % (arch, self.arch))
            return False
        return True

    def parse_isoinfo(self, info):
        '''
        Parses the file within the ISO
        that contains metadata on the iso
        e.g. .disk/info in Ubuntu
        Ubuntu 9.04 "Jaunty Jackalope" - Alpha i386 (20090106)
        Ubuntu 9.04 "Jaunty Jackalope" - Alpha i386 (20090106.1)
        Ubuntu Split Name 9.04.1 "Jaunty Jackalope" - Final Release i386 (20090106.2)
        '''
        log.debug("  parsing info from str=%s" % info)
        if not info:
            return
        info = disk_info_re.match(info)
        name = info.group('name').replace('-', ' ')
        version = info.group('version')
        subversion = info.group('subversion')
        arch = info.group('arch')
        log.debug("  parsed info=%s" % info.groupdict())
        return name, version, subversion, arch
