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


class UninstallationFinishPage(Page):

    def on_init(self):
        Page.on_init(self)
        self.set_background_color(255,255,255)
        self.insert_vertical_image("%s-vertical.bmp" % self.info.previous_distro_name)

        #navigation
        self.insert_navigation(_("Finish"), default=1)
        self.navigation.button1.on_click = self.on_finish

        #main container
        self.insert_main()
        self.main.set_background_color(255,255,255)
        self.main.title = ui.Label(self.main, 40, 20, self.main.width - 80, 60, _("Uninstallation completed"))
        self.main.title.set_font(size=20, bold=True, family="Arial")
        self.main.label = ui.Label(self.main, 40, 90, self.main.width - 80, 40, _("%s has been successfully uninstalled") % self.info.previous_distro_name)

    def on_finish(self):
        self.frontend.stop()

