# USEFUL LINKS http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/180919
# about creating files, detecting drives...

import sys
import os
import tempfile
#~ import carchive
import locale
import struct
import logging
import tempfile
import time
import StringIO
import mappings
import gettext
import glob
from helpers import *
from metalink import parse_metalink
from distro import parse_isolist
from tasklist import ThreadedTaskList
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
        self.extract_data_dir()
        self.info.tempdir = tempfile.mkdtemp() #os.path.join(self.info.datadir, "temp")

    def change_language(self, codeset):
        domain = self.info.application_name #not sure what it is
        localedir = self.info.datadir + '/locale'
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

    def get_distros(self):
        isolist_path = os.path.join(self.info.datadir, 'isolist.ini')
        distros = parse_isolist(isolist_path, self)
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

    def extract_data_dir(self, data_pkg='data.pkg'):
        '''
        Hack around pyinstaller limitations
        The data dir is packaged with the exe and must be extracted
        '''
        self.info.datadir = "data" #os.path.join(os.path.dirname(self.info.exedir), "data")
        self.info.imagedir = "data/images" #os.path.join(self.info.datadir, "images")
        #~ if hasattr(sys,'frozen') and sys.frozen:
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

    def find_isos(self):
        for path in self.info.iso_search_paths:
            isos = glob.glob('*.iso')
        for iso in isos:
            for distro in self.info.distros:
                if distro.is_valid_iso(iso):
                    return iso, distro

    def find_cds(self):
        for cd in self.info.cd_search_paths:
            for distro in self.info.distros:
                if distro.is_valid_iso(cd):
                    return cd, distro

    def get_is_running_from_cd(self):
        #TBD
        is_running_from_cd = False
        log.debug("is_running_from_cd=%s" % is_running_from_cd)
        return is_running_from_cd

