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

_version_ = 8.10
_revision_ = 0
_application_name_ = "Wubi"

import os
import sys
from optparse import OptionParser
#TBD import modules as required at runtime
from backends.win32.backend import WindowsBackend
from frontends.win32.frontend import WindowsFrontend
thisdir = os.path.abspath(os.path.dirname(__file__))
#~ sys.path.insert(1, os.path.join(thisdir, 'lib'))

class WubiError(Exception):
	pass

class Blob(object):
	pass

class Wubi(object):
	
	def __init__(self):
		self.info = Blob()
		self.info.version = _version_
		self.info.revision = _revision_
		self.info.application_name = _application_name_
		
	def run(self):
		self.parse_commandline_arguments()
		self.backend = self.get_backend()
		self.backend.fetch_basic_info()
		self.select_task()
		
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
		if self.info.use_cli:
			Frontend = CLIFrontend
		else:
			Frontend = WindowsFrontend
		return Frontend(self)
	
	def quit(self):
		pass
	
	def select_task(self):
		'''
		Select the appropriate task to perform and run it
		'''
		if self.info.show_version:
			print "%s version=%s revision=%s" % (self.info.application_name, self.info.version, self.info.revision)
		elif self.info.is_running_from_cd:
			self.run_cd_menu()
		elif self.info.is_installed or self.info.uninstall_dir:
			self.run_uninstaller()
		else:
			self.run_installer()
		
	def run_installer(self):
		'''
		Runs the installer 
		'''
		self.frontend = self.get_frontend()
		self.frontend.run_installer()

	def run_uninstaller(self):
		'''
		Runs the installer interface
		'''
		self.frontend = self.get_frontend()
		self.frontend.run_uninstaller()
		
	def run_cd_menu(self):
		'''
		If Wubi is run off a CD, run the CD menu (old umenu)
		'''
		self.frontend = self.get_frontend()
		self.frontend.run_cd_menu()
	
	def parse_commandline_arguments(self):
		'''
		Parses commandline arguments
		'''
		parser = OptionParser()
		parser.add_option("-c", "--cli", action="store_true", dest="use_cli", default=False, help="Use the command line interface")
		parser.add_option("-v", "--verbose", action="store_true", dest="verbose", default=False, help="Run in verbose mode")
		parser.add_option("-V", "--version", action="store_true", dest="show_version", default=False, help="Show the version and exit")
		parser.add_option("--frontend", dest="frontend", help="Select a specific frontend")
		parser.add_option("--uninstall", dest="uninstall_dir", help="Uninstall the specified directory")
		(options, self.args) = parser.parse_args()
		self.info.__dict__.update(options.__dict__)
		
wubi = Wubi()
wubi.run()