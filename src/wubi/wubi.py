#!/usr/bin/env python
#
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

_version_ = "8.10"
_revision_ = 0
_application_name_ = "wubi"

import os
import sys
import tempfile
from optparse import OptionParser
#TBD import modules as required at runtime
from backends.win32.backend import WindowsBackend
from frontends.win32.frontend import WindowsFrontend
import logging
log = logging.getLogger("")

class WubiError(Exception):
    pass

class Blob(object):

    def __init__(self, **kargs):
        self.__dict__.update(**kargs)

    def __str__(self):
        return "Blob(%s)" % str(self.__dict__)

class Wubi(object):

    def __init__(self):
        self.info = Blob()
        self.info.version = _version_
        self.info.revision = _revision_
        self.info.application_name = _application_name_
        self.info.full_application_name = "%s-%s-rev%s" % (self.info.application_name, self.info.version, self.info.revision)
        self.info.full_version = "%s %s rev%s" % (self.info.application_name, self.info.version, self.info.revision)
        self.info.exedir = "." #os.path.abspath(os.path.dirname(__file__))
        self.info.datadir = "data" #os.path.join(os.path.dirname(self.info.exedir), "data")
        self.info.imagedir = "data/images" #os.path.join(self.info.datadir, "images")

    def run(self):
        self.parse_commandline_arguments()
        self.set_logger()
        log.info("=== " + self.info.full_version + " ===")
        log.debug("Logfile is %s" % self.info.log_file)
        self.backend = self.get_backend()
        self.backend.fetch_basic_info()
        self.select_task()

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

    def quit(self):
        '''
        Sends quit signal to frontend
        '''
        self.frontend.quit()

    def select_task(self):
        '''
        Selects the appropriate task to perform and runs it
        '''
        if self.info.run_task == "install":
            self.run_installer()
        elif self.info.run_task == "uninstall":
            self.run_uninstaller()
        elif self.info.run_task == "cdmenu":
            self.run_cd_menu()
        elif self.info.is_running_from_cd:
            self.run_cd_menu()
        else:
            self.run_installer()

    def run_installer(self):
        '''
        Runs the installer
        '''
        if self.info.is_installed or self.info.uninstall_dir:
            log.info("Already installed, running the installer...")
            self.run_uninstaller()
        log.info("Running the installer...")
        self.frontend = self.get_frontend()
        settings = self.frontend.get_installation_settings()
        log.info("Received settings %s" % settings)
        self.frontend.run_tasks(self.backend.get_installation_tasklist())
        log.info("Finished installation")

    def run_uninstaller(self):
        '''
        Runs the installer interface
        '''
        log.info("Running the uninstaller...")
        self.frontend = self.get_frontend()
        self.frontend.run_uninstaller()

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
        parser.add_option("-m", "--cdmenu", action="store_const", const="cdmenu", dest="run_task", help="run the CD menu selector")
        parser.add_option("--log-file", dest="log_file", default=None, help="use the specified log file, if omitted a log is created in your temp directory, if the value is set to 'none' no log is created")
        parser.add_option("--interface", dest="use_frontend", default=None, help="use the specified user interface, ['win32']")
        parser.add_option("--uninstall_dir", dest="uninstall_dir", default=None, help="uninstall the specified directory")
        (options, self.args) = parser.parse_args()
        self.info.__dict__.update(options.__dict__)

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
        log.setLevel(logging.DEBUG)

wubi = Wubi()
wubi.run()
