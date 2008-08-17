# USEFUL LINKS http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/180919
# about creating files, detecting drives...

import sys
import os
import locale
import struct
import logging
import time
from metalink import Metalink
from tasklist import ThreadedTaskList
log = logging.getLogger("CommonBackend")

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
        self.info.exedir = os.path.abspath(os.path.dirname(sys.argv[0]))
        self.info.platform = sys.platform
        self.info.osname = os.name
        self.info.language, self.info.encoding = locale.getdefaultlocale()
        self.info.environment_variables = os.environ
        self.info.arch = struct.calcsize('P') == 8 and 64 or 32  #TBD detects python/os arch not processor arch
        self.info.is_installed = self.get_is_installed()
        self.info.is_running_from_cd = self.get_is_running_from_cd()

    def fetch_installer_info(self):
        '''
        Fetch information required by the installer
        '''
        self.fetch_system_info()

    def fetch_system_info(self):
        pass

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

    def get_is_installed(self):
        '''
        Implemented in derived classes
        '''

    def get_is_running_from_cd(self):
        '''
        Implemented in derived classes
        '''

    def parse_metalink(self, metalink_file):
        self.info.metalink = Metalink(metalink_file)

