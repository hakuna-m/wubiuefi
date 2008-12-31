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

from winui import ui
from page import Page
import os
import logging
import sys
log = logging.getLogger("WinuiInstallationPage")

class UninstallationPage(Page):

    def on_init(self):
        Page.on_init(self)

        #header
        self.insert_header(
            #TBD change it to something more dynamic
            "You are about to uninstall Ubuntu",
            "",
            "Ubuntu-header.bmp")

        #navigation
        self.insert_navigation("Uninstall", "Cancel", default=2)
        self.navigation.button2.on_click = self.application.cancel
        self.navigation.button1.on_click = self.on_uninstall

        #Main control container
        self.insert_main()

        self.uninstall_label = ui.Label(
            self.main,
            40, 40, self.main.width - 80, 12,
            "Are you sure you want to uninstall?")
        self.backup_iso = ui.CheckButton(
            self.main, 60, 60, self.main.width - 120, 12,
            "Backup the downloaded files (ISO)")
        self.backup_iso.set_check(False)
        self.backup_iso.hide()
        installdir = os.path.join(self.application.info.previous_target_dir, 'install')
        if os.path.isdir(installdir):
            for f in os.listdir(installdir):
                if f.endswith('.iso'):
                    self.backup_iso.set_check(True)
                    self.backup_iso.show()
                    break

    def on_uninstall(self):
        info = self.application.info
        self.application.backup_iso = self.backup_iso.is_checked()
        self.callback("ok")
