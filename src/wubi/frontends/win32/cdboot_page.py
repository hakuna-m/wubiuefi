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
log = logging.getLogger("WinuiCDBootPage")


class CDBootPage(Page):

    def on_init(self):
        Page.on_init(self)
        self.set_background_color(255,255,255)
        self.frontend.set_title(_("%s CD Boot Helper") % self.info.cd_distro.name)
        self.insert_vertical_image("%s-vertical.bmp" % self.info.cd_distro.name)

        #sanity checks
        self.info.distro = self.info.cd_distro
        self.info.target_drive = None
        for drive in [self.info.system_drive] + self.info.drives:
            if drive.free_space_mb > self.info.distro.max_iso_size/1000000:
                self.info.target_drive = drive
                break
        if not self.info.target_drive:
            self.frontend.show_error_message(_("Not enough disk space to proceed"))

        #navigation
        self.insert_navigation(_("Accessibility"), _("Install"), _("Cancel"), default=2)
        self.navigation.button3.on_click = self.on_cancel
        self.navigation.button2.on_click = self.on_install
        self.navigation.button1.on_click = self.on_accessibility

        #main container
        self.insert_main()
        self.main.set_background_color(255,255,255)
        self.main.title = ui.Label(self.main, 40, 20, self.main.width - 80, 60, _("Install CD boot helper"))
        self.main.title.set_font(size=20, bold=True, family="Arial")
        txt = _("If your machine cannot boot off the CD, this program will install a new boot menu entry to help you boot from CD. In most cases this program is not needed, and it is sufficient to reboot with the CD-Rom in the tray.\n\nDo you want to proceed and install the CD booter?")
        self.main.label = ui.Label(self.main, 40, 90, self.main.width - 80, 80, txt)

    def on_cancel(self):
        self.frontend.cancel()

    def on_accessibility(self):
        self.frontend.show_page(self.frontend.accessibility_page)

    def on_install(self):
        self.frontend.stop()
