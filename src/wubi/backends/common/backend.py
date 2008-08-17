# USEFUL LINKS http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/180919
# about creating files, detecting drives...

import sys
import os
import locale
import struct
import logging
import time
import mappings
from metalink import Metalink
from tasklist import ThreadedTaskList
log = logging.getLogger("CommonBackend")


class Blob(object):

    def __init__(self, **kargs):
        self.__dict__.update(**kargs)

    def __str__(self):
        return "Blob(%s)" % str(self.__dict__)


class Backend(object):
    '''
    Implements non-platform-specific functionality
    Subclasses need to implement platform-specific getters
    '''
    def __init__(self, application):
        self.application = application
        self.info = application.info

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
        self.fetch_basic_os_specific_info()

    def get_exe_dir(self):
        #does not work when frozen
        #os.path.abspath(os.path.dirname(__file__))
        exedir = os.path.abspath(os.path.dirname(sys.argv[0]))
        log.debug("exedir=%s" % exedir)
        return exedir

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

    def parse_metalink(self, metalink_file):
        metalink = Metalink(metalink_file)
        log.debug("metalin=%s" % str(metalink))
        return metalink

