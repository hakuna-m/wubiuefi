# USEFUL LINKS http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/180919
# about creating files, detecting drives...

import sys
import os
import locale
import struct
import logging
import time
from metalink import Metalink
from progress import Progress
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
        progress = Progress(task_name="Gathering basic information", total_steps=4)
        progress.subtask("Detect basic info")
        self.info.exedir = os.path.abspath(os.path.dirname(sys.argv[0]))
        self.info.platform = sys.platform
        self.info.osname = os.name
        self.info.language, self.info.encoding = locale.getdefaultlocale()
        self.info.environment_variables = os.environ
        progress.subtask("Detect arch")
        self.info.arch = struct.calcsize('P') == 8 and 64 or 32  #TBD detects python/os arch not processor arch
        progress.subtask("Detect if installed")
        self.info.is_installed = self.get_is_installed()
        progress.subtask("Detect running mode")
        self.info.is_running_from_cd = self.get_is_running_from_cd()

    def fetch_installer_info(self, progress_callback=None):
        '''
        Fetch information required by the installer
        '''
        progress = Progress(task_name="Gathering information", total_steps=1)
        progress.subtask("Detecting system information")
        self.fetch_system_info()
        progress.finish_subtask()

    def fetch_system_info(self):
        pass

    def install(self, progress_callback=None):
        progress = Progress(task_name="Installing", total_steps=5, callback=progress_callback)
        progress.subtask("Subtask 1")
        time.sleep(1)
        progress.subtask("Subtask 2")
        time.sleep(1)
        progress.subtask("Subtask 3")
        time.sleep(1)
        progress.subtask("Subtask 4")
        time.sleep(1)
        progress.subtask("Subtask 5")
        time.sleep(1)
        progress.finish_subtask()

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

