import os
import ConfigParser
import shutil
import logging
from helpers import *
log = logging.getLogger('Distro')

class Distro(object):
    def __init__(
            self, name, version, kernel, initrd,
            info_file, arch, metalink, metalink2,
            packages, size, md5sums, files_to_check,
            metalink_md5sums, metalink_md5sums_signature,
            backend, minsize=0, maxsize=0):
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
        if isinstance(files_to_check, basestring):
            files_to_check = [f.strip().lower() for f in files_to_check.split(',')]
        self.files_to_check = files_to_check

    def set_cd(cd_path):
        self.cd_path = cd_path

    def set_iso(iso_path):
        self.iso_path

    def is_valid_cd(self, cd_path):
        cd_path = os.path.normpath(cd_path)
        log.debug('Checking cd %s' % cd_path)
        if not os.path.isdir(cd_path):
            log.debug('  dir does not exist')
            return False
        files = get_dir_file_names(cd_path)
        if not self.check_required_files:
            log.debug('  does not contain %s' % file)
            return False
        info_file = os.path.join(cd_path, self.info_file)
        info = read_file(info_file)
        return self.check_info(info)

    def is_valid_iso(self, iso_path):
        iso_path = os.path.normpath(iso_path)
        log.debug('Checking iso %s' % iso_path)
        if not os.path.isfile(iso_path):
            log.debug('  file does not exist')
            return False
        file_size = os.path.getsize(cd_or_iso_path)
        if self.size and self.size != file_size:
            log.debug('  wrong size: %s != %s' % (file_size, self.size))
            return False
        elif self.minsize and file_size < self.minsize:
            log.debug('  wrong size: %s < %s' % (file_size, self.size))
            return False
        elif self.minsize and file_size < self.minsize:
            log.debug('  wrong size: %s > %s' % (file_size, self.size))
            return False
        files = self.backend.get_iso_file_names(iso_path)
        if not self.check_required_files:
            log.debug('  does not contain %s' % file)
            return False
        info_file = backend.extract_file_from_iso(self,
            iso_path,
            self.info_file,
            output_dir=self.backend.info.tempdir,
            overwrite=True)
        info = read_file(info_file)
        os.unlink(info_file)
        return self.check_info(info)

    def check_required_files(self, files):
        files = [f.strip().lower() for f in files]
        required_files = self.files_to_check[:]
        required_files += [
            self.kernel,
            self.initrd,
            self.info_file,
            self.md5sums,]
        for file in self.required_files:
            if file.strip.lower() not in files:
                return False
        return True

    def check_info(self, info):
        if not info:
            log.debug('  null info')
            return False
        info = parse_isoinfo(info)
        if not info:
            log.debug('  could not parse info %s' % info)
            return False
        name, version, arch = info
        if self.name and name != self.name:
            log.debug('  wrong name: %s != %s' % (name, self.name))
            return False
        if self.version and version != self.version:
            log.debug('  wrong version: %s != %s' % (version, self.version))
            return False
        if self.arch and arch != self.arch:
            log.debug('  wrong arch: %s != %s' % (arch, self.arch))
            return False
        log.info('Found a valid cd/iso: %s' % cd_or_iso_path)
        return True

def parse_isolist(isolist_path, backend):
    isolist = ConfigParser.ConfigParser()
    isolist.read(isolist_path)
    distros = {}
    for distro in isolist.sections():
        kargs = dict(isolist.items(distro))
        kargs['backend'] = backend
        distros[distro] = Distro(**kargs)
    return distros

def parse_isoinfo(info):
    '''
    Parses the file within the ISO
    that contains metadata on the iso
    e.g. .disk/info in Ubuntu
    '''
    #TBD use re
    log.debug("  info=%s" % info)
    name = info.split(' ')[0]
    version = info.split(' ')[1]
    codename = info.split('"')[1]
    build = info.split('(')[1][:-1]
    arch = info.split('(')[0].split(" ")[-2]
    subversion = info.split('(')[0].split(" ")[-3]
    log.debug((name, version, codename, build, arch, subversion))
    return name, version, arch
