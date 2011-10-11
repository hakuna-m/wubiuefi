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
import logging
log = logging.getLogger("WinuiInstallationPage")

class UninstallationPage(Page):

    def on_init(self):
        Page.on_init(self)
        self.frontend.set_title(_("%s Uninstaller") % self.info.previous_distro_name)

        #header
        if self.info.uninstall_before_install:
            msg = _("Uninstallation required")
        else:
            msg = _("You are about to uninstall %s") % self.info.previous_distro_name
        self.insert_header(
            msg,
            "",
            "%s-header.bmp" % self.info.previous_distro_name)

        #navigation
        self.insert_navigation(_("Uninstall"), _("Cancel"), default=2)
        self.navigation.button2.on_click = self.on_cancel
        self.navigation.button1.on_click = self.on_uninstall

        #Main control container
        self.insert_main()
        if self.info.uninstall_before_install:
            msg = _("A previous installation was detected, it needs to be uninstalled before continuing")
        else:
            msg = _("Are you sure you want to uninstall?")

        self.uninstall_label = ui.Label(
            self.main,
            40, 40, self.main.width - 80, 30,
            msg)

    def on_uninstall(self):
        self.frontend.stop()

    def on_cancel(self):
        self.frontend.cancel()
