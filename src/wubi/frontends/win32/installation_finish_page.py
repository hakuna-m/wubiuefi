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
log = logging.getLogger("WinuiInstallationFinishPage")


class InstallationFinishPage(Page):

    def on_init(self):
        Page.on_init(self)
        self.set_background_color(255,255,255)
        self.insert_vertical_image("%s-vertical.bmp" % self.info.distro.name)

        #navigation
        self.insert_navigation(_("Finish"), default=1)
        self.navigation.button1.on_click = self.on_finish

        #main container
        self.insert_main()
        self.main.set_background_color(255,255,255)
        self.main.title = ui.Label(self.main, 40, 20, self.main.width - 80, 60, _("Completing the %s Setup Wizard") % self.info.distro.name)
        self.main.title.set_font(size=20, bold=True, family="Arial")
        self.main.label = ui.Label(self.main, 40, 90, self.main.width - 80, 40, _("You need to reboot to complete the installation"))
        self.main.reboot_now = ui.RadioButton(self.main, 60, 150, self.main.width - 100, 20, _("Reboot now"))
        self.main.reboot_later = ui.RadioButton(self.main, 60, 180, self.main.width - 100, 20, _("I want to manually reboot later"))
        self.main.reboot_later.set_check(True)

    def on_finish(self):
        if self.main.reboot_now.is_checked():
            self.info.run_task = "reboot"
        self.frontend.stop()

