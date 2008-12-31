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

_version_ = "9.04"
_revision_ = 0
_application_name_ = "wubi"

import os
import sys
import tempfile
from optparse import OptionParser
#TBD import modules as required at runtime
from wubi.backends.win32 import WindowsBackend
from wubi.frontends.win32 import WindowsFrontend
import logging
log = logging.getLogger("")

class Wubi(object):

    def __init__(self):
        self.info = Info()
        self.info.version = _version_
        self.info.revision = _revision_
        self.info.application_name = _application_name_
        self.info.full_application_name = "%s-%s-rev%s" % (self.info.application_name, self.info.version, self.info.revision)
        self.info.full_version = "%s %s rev%s" % (self.info.application_name, self.info.version, self.info.revision)

    def run(self):
        self.parse_commandline_arguments()
        self.set_logger()
        log.info("=== " + self.info.full_version + " ===")
        log.debug("Logfile is %s" % self.info.log_file)
        self.backend = self.get_backend()
        self.backend.fetch_basic_info()
        self.select_task()

    def quit(self):
        '''
        Sends quit signal to frontend, since quit signals are originated by the frontend anyway
        '''
        self.frontend.quit()

    def on_quit(self):
        '''
        Receives quit notification from frontend
        '''
        log.info("sys.exit")
        sys.exit(0)

    def get_backend(self):
        '''
        Gets the appropriate backend for the system
        The backend contains system-specific libraries for tasks such as
        Information fetching, installation, and disinstallation
        '''
        #TBD do proper detection of backend
        return WindowsBackend(self)

    def get_frontend(self):
        '''
        Gets the appropriate frontend for the system
        '''
        #TBD do proper detection of frontend
        if self.info.use_frontend:
            raise NotImplemented
        else:
            Frontend = WindowsFrontend
        return Frontend(self)

    def select_task(self):
        '''
        Selects the appropriate task to perform and runs it
        '''
        if self.info.run_task == "install":
            self.run_installer()
        elif self.info.run_task == "uninstall":
            self.run_uninstaller()
        elif self.info.cd_path or self.info.run_task == "cd_menu":
            self.run_cd_menu()
        else:
            self.run_installer()
        self.quit()

    def run_installer(self):
        '''
        Runs the installer
        '''
        #TBD add non_interactive mode
        if self.info.previous_target_dir or self.info.uninstall_dir:
            log.info("Already installed, running the installer...")
            self.run_uninstaller()
            self.backend.fetch_basic_info()
            if self.info.previous_target_dir or self.info.uninstall_dir:
                self.quit()
        else:
            self.frontend = self.get_frontend()
        log.info("Running the installer...")
        settings = self.frontend.get_installation_settings()
        log.info("Received settings %s" % settings)
        self.frontend.run_tasks(self.backend.get_installation_tasklist())
        log.info("Almost finished installing")
        self.frontend.show_installation_finish_page()
        log.info("Finished installation")

    def run_uninstaller(self):
        '''
        Runs the uninstaller interface
        '''
        log.info("Running the uninstaller...")
        self.frontend = self.get_frontend()
        if not self.info.test:
            settings = self.frontend.get_uninstallation_settings()
            log.info("Received settings %s" % settings)
        self.frontend.run_tasks(self.backend.get_uninstallation_tasklist())
        log.info("Almost finished uninstalling")
        self.frontend.show_uninstallation_finish_page()
        log.info("Finished uninstallation")

    def run_cd_menu(self):
        '''
        If Wubi is run off a CD, run the CD menu (old umenu)
        '''
        log.info("Running the CD menu...")
        self.frontend = self.get_frontend()
        self.frontend.run_cd_menu()

    def parse_commandline_arguments(self):
        '''
        Parses commandline arguments
        '''
        usage = "%s [options]" % self.info.application_name
        parser = OptionParser(usage=usage, version=self.info.full_version)
        parser.add_option("-q", "--quiet", action="store_const", const="quiet", dest="verbosity", help="run in quiet mode, only critical error messages are displayed")
        parser.add_option("-v", "--verbose", action="store_const", const="verbose", dest="verbosity", help="run in verbose mode, all messages are displayed")
        parser.add_option("-i", "--install", action="store_const", const="install", dest="run_task", help="run the uninstaller, it will first look for an existing uninstaller, otherwise it will run itself in uninstaller mode")
        parser.add_option("-u", "--uninstall", action="store_const", const="uninstall", dest="run_task", help="run the installer, if an existing installation is detected it will be uninstalled first")
        parser.add_option("-m", "--cd_menu", action="store_const", const="cd_menu", dest="run_task", help="run the CD menu selector")
        parser.add_option("-b", "--cdboot", action="store_const", const="cd_boot", dest="run_task", help="install a CD boot helper program")
        parser.add_option("--nobittorrent", action="store_true", dest="no_bittorrent", help="Do not use the bittorrent downloader")
        parser.add_option("--skipmd5check", action="store_true", dest="skip_md5_check", help="Skip md5 checks")
        parser.add_option("--skipsizecheck", action="store_true", dest="skip_size_check", help="Skip disk size checks")
        parser.add_option("--skipmemorycheck", action="store_true", dest="skip_memory_check", help="Skip memory size checks")
        parser.add_option("--noninteractive", action="store_true", dest="non_interactive", help="Non interactive mode")
        parser.add_option("--test", action="store_true", dest="test", help="Test mode")
        parser.add_option("--debug", action="store_true", dest="debug", help="Debug mode")
        parser.add_option("--drive", dest="target_drive", help="Target drive")
        parser.add_option("--size", dest="installation_size_mb", help="Installation size in MB")
        parser.add_option("--locale", dest="locale", help="Linux locale")
        parser.add_option("--language", dest="language", help="Language")
        parser.add_option("--username", dest="username", help="Username")
        parser.add_option("--password", dest="password", help="Password (md5)")
        parser.add_option("--distro", dest="distro_name", help="Distro")
        parser.add_option("--accessibility", dest="accessibility", help="Accessibility")
        parser.add_option("--webproxy", dest="web_proxy", help="Web proxy")
        parser.add_option("--isopath", dest="iso_path", help="Use specified ISO")
        parser.add_option("--exefile", dest="original_exe", default=None, help="Used to indicate the original location of the executable in case of self-extracting files")
        parser.add_option("--log-file", dest="log_file", default=None, help="use the specified log file, if omitted a log is created in your temp directory, if the value is set to 'none' no log is created")
        parser.add_option("--interface", dest="use_frontend", default=None, help="use the specified user interface, ['win32']")
        parser.add_option("--uninstall_dir", dest="uninstall_dir", default=None, help="uninstall the specified directory")
        (options, self.args) = parser.parse_args()
        self.info.__dict__.update(options.__dict__)
        if self.info.test:
            self.info.debug = True
        if self.info.debug:
            self.info.verbose = True

    def set_logger(self):
        '''
        Adjust the application root logger settings
        '''
        # file logging
        if not self.info.log_file or self.info.log_file.lower() != "none":
            if not self.info.log_file:
                fname = self.info.full_application_name + ".log"
                dname = tempfile.gettempdir()
                self.info.log_file = os.path.join(dname, fname)
            handler = logging.FileHandler(self.info.log_file)
            formatter = logging.Formatter('%(asctime)s %(levelname)-6s %(name)s: %(message)s', datefmt='%m-%d %H:%M')
            handler.setFormatter(formatter)
            handler.setLevel(logging.DEBUG)
            log.addHandler(handler)
        # console logging
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(message)s', datefmt='%m-%d %H:%M')
        handler.setFormatter(formatter)
        if self.info.verbosity == "verbose":
            handler.setLevel(logging.DEBUG)
        elif self.info.verbosity == "quiet":
            handler.setLevel(logging.ERROR)
        else:
            handler.setLevel(logging.INFO)
        log.addHandler(handler)
        log.setLevel(handler.level)

class Info(object):

    def __str__(self):
        return "Info(%s)" % str(self.__dict__)


if __name__ == "__main__":
    app = Wubi()
    app.run()
