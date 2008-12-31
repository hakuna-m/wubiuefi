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
import shutil
from utils import read_file
import logging

log = logging.getLogger('Distro')


class Distro(object):

    cache = {}

    def __init__(
            self, name, version, kernel, initrd,
            info_file, arch, metalink, metalink2,
            packages, size, md5sums, files_to_check,
            metalink_md5sums, metalink_md5sums_signature,
            backend, ordering, minsize=0, maxsize=0):
        self.name = name
        self.version = version
        self.arch = arch
        self.kernel = os.path.normpath(kernel)
        self.initrd = os.path.normpath(initrd)
        self.md5sums = os.path.normpath(md5sums)
        self.info_file = os.path.normpath(info_file)
        self.size = size and int(size) or 0
        self.minsize = minsize and int(minsize) or 0
        self.maxsize = maxsize and int(maxsize) or 0
        self.metalink_md5sums = metalink_md5sums
        self.metalink_md5sums_signature = metalink_md5sums_signature
        self.metalink = metalink
        self.metalink2 = metalink2
        self.packages = packages
        self.backend = backend
        self.ordering = ordering
        if isinstance(files_to_check, basestring):
            files_to_check = [
                os.path.normpath(f.strip().lower())
                for f in files_to_check.split(',')]
        self.files_to_check = files_to_check

    def is_valid_cd(self, cd_path):
        cd_path = os.path.abspath(cd_path)
        log.debug('checking cd %s' % cd_path)
        if not os.path.isdir(cd_path):
            log.debug('dir does not exist')
            return False
        required_files = self.get_required_files()
        for file in required_files:
            file = os.path.join(cd_path, file)
            if not os.path.isfile(file):
                log.debug('does not contain %s' % file)
                return False
        info = self.get_info(cd_path)
        if self.check_info(info):
            log.info('Found a valid cd for %s: %s' % (self.name, cd_path))
            return True
        else:
            return False

    def is_valid_iso(self, iso_path):
        iso_path = os.path.abspath(iso_path)
        log.debug('checking iso %s' % iso_path)
        if not os.path.isfile(iso_path):
            log.debug('file does not exist')
            return False
        file_size = os.path.getsize(iso_path)
        if self.size and self.size != file_size:
            log.debug('wrong size: %s != %s' % (file_size, self.size))
            return False
        elif self.minsize and file_size < self.minsize:
            log.debug('wrong size: %s < %s' % (file_size, self.minsize))
            return False
        elif self.maxsize and file_size > self.maxsize:
            log.debug('wrong size: %s > %s' % (file_size, self.maxsize))
            return False
        files = self.backend.get_iso_file_names(iso_path)
        files = [f.strip().lower() for f in files]
        required_files = self.get_required_files()
        for file in required_files:
            if file.strip().lower() not in files:
                log.debug('does not contain %s' % file)
                return False
        info = self.get_info(iso_path)
        if self.check_info(info):
            log.info('Found a valid iso for %s: %s' % (self.name, iso_path))
            return True
        else:
            return False

    def get_info(self, cd_or_iso_path):
        if (cd_or_iso_path, self.info_file) in Distro.cache:
            return Distro.cache[(cd_or_iso_path, self.info_file)]
        else:
            Distro.cache[(cd_or_iso_path, self.info_file)] = None
            log.debug("getting %s from %s" % (self.info_file,cd_or_iso_path))
            if os.path.isfile(cd_or_iso_path):
                info_file = self.backend.extract_file_from_iso(
                    cd_or_iso_path,
                    self.info_file,
                    output_dir=self.backend.info.tempdir,
                    overwrite=True)
            elif os.path.isdir(cd_or_iso_path):
                info_file = os.path.join(cd_or_iso_path, self.info_file)
            else:
                return
            if not os.path.isfile(info_file):
                return
            info = read_file(info_file)
            if info_file and os.path.isfile(info_file) and os.path.isfile(cd_or_iso_path):
                os.unlink(info_file)
            info = self.parse_isoinfo(info)
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

    def check_info(self, info):
        if not info:
            log.debug('could not get info %s' % info)
            return False
        name, version, arch = info
        if self.name and name != self.name:
            log.debug('wrong name: %s != %s' % (name, self.name))
            return False
        if self.version and version != self.version:
            log.debug('wrong version: %s != %s' % (version, self.version))
            return False
        if self.arch and arch != self.arch:
            log.debug('wrong arch: %s != %s' % (arch, self.arch))
            return False
        return True

    def parse_isoinfo(self, info):
        '''
        Parses the file within the ISO
        that contains metadata on the iso
        e.g. .disk/info in Ubuntu
        '''
        #TBD use re
        log.debug("info=%s" % info)
        name = info.split(' ')[0]
        version = info.split(' ')[1]
        codename = info.split('"')[1]
        build = info.split('(')[1][:-1]
        arch = info.split('(')[0].split(" ")[-2]
        subversion = info.split('(')[0].split(" ")[-3]
        log.debug("parsed info=" + ", ".join((name, version, codename, build, arch, subversion)))
        return name, version, arch
