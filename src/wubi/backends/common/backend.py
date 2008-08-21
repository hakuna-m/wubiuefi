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
            self.info.rootdir = os.path.dirname(os.path.abspath(sys.executable))
            self.info.tempdir = tempfile.mkdtemp(dir=self.info.rootdir)
        else:
            self.info.rootdir = ''
            self.info.tempdir = tempfile.mkdtemp()
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
        self.info.exedir = self.get_exe_dir()
        self.info.platform = self.get_platform()
        self.info.osname = self.get_osname
        self.info.language, self.info.encoding = self.get_language_encoding()
        self.info.environment_variables = os.environ
        self.info.arch = self.get_arch()
        self.info.languages = self.get_languages()
        self.info.distros = self.get_distros()
        self.fetch_basic_os_specific_info()
        self.info.cd_path, self.info.cd_distro = self.find_cd()
        self.info.iso_path,  self.info.iso_distro = self.find_iso()
        self.info.is_running_from_cd = self.get_is_running_from_cd()

    def get_distros(self):
        isolist_path = os.path.join(self.info.datadir, 'isolist.ini')
        distros = self.parse_isolist(isolist_path)
        return distros

    def get_exe_dir(self):
        #__file__ does not work when frozen
        #os.path.abspath(os.path.dirname(__file__))
        #os.path.abspath(sys.executable)
        exedir = os.path.abspath(os.path.dirname(sys.argv[0]))
        log.debug("exedir=%s" % exedir)
        return exedir

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

    def fetch_installer_info(self):
        '''
        Fetch information required by the installer
        '''

    def dummy_function(self):
        time.sleep(1)

    def get_installation_tasklist(self):
        f = self.dummy_function
        tasks = [
            ("task 1", f),
            ("task 2", f),
            ("task 3", f),
            ("task 4", f),
            ("task 5", f),
        ]
        tasklist = ThreadedTaskList("Installing", tasks=tasks)
        return tasklist

    #~ def extract_data_dir(self, data_pkg='data.pkg'):
        #~ '''
        #~ Hack around pyinstaller limitations
        #~ The data dir is packaged with the exe and must be extracted
        #~ '''
        #~ self.info.datadir = "data" #os.path.join(os.path.dirname(self.info.exedir), "data")

            #~ import carchive
            #~ this = carchive.CArchive(sys.executable)
            #~ pkg = this.openEmbedded(data_pkg)
            #~ targetdir = os.environ['_MEIPASS2']
            #~ targetdir = os.path.join(targetdir,'data')
            #~ os.mkdir(targetdir)
            #~ log.debug("Extracting data")
            #~ log.debug("Data dir=%s" % targetdir)
            #~ for fnm in pkg.contents():
                #~ try:
                    #~ stuff = pkg.extract(fnm)[1]
                    #~ outnm = os.path.join(targetdir, fnm)
                    #~ dirnm = os.path.dirname(outnm)
                    #~ if not os.path.exists(dirnm):
                        #~ os.makedirs(dirnm)
                    #~ open(outnm, 'wb').write(stuff)
                #~ except Exception,mex:
                    #~ print mex
            #~ pkg = None
            #~ self.info.datadir = targetdir
            #~ self.info.imagedir = os.path.join(targetdir, 'images')

    def find_iso(self):
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

    def find_cd(self):
        log.debug('searching for local CDs')
        for path in self.get_cd_search_paths():
            path = os.path.abspath(path)
            for distro in self.info.distros.values():
                if distro.is_valid_cd(path):
                    return path, distro
        return None, None

    def get_is_running_from_cd(self):
        #TBD
        is_running_from_cd = self.info.cd_path is not None
        log.debug("is_running_from_cd=%s" % is_running_from_cd)
        return is_running_from_cd

    def parse_isolist(self, isolist_path):
        isolist = ConfigParser.ConfigParser()
        isolist.read(isolist_path)
        distros = {}
        for distro in isolist.sections():
            kargs = dict(isolist.items(distro))
            kargs['backend'] = self
            distros[distro] = Distro(**kargs)
        return distros
