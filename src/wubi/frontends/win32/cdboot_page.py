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
        self.insert_vertical_image("Ubuntu-vertical.bmp")

        #navigation
        self.insert_navigation("Accessibility", "Install", "Cancel", default=2)
        self.navigation.button3.on_click = self.on_cancel
        self.navigation.button2.on_click = self.on_install
        self.navigation.button1.on_click = self.on_accessibility

        #main container
        self.insert_main()
        self.main.set_background_color(255,255,255)
        self.main.title = ui.Label(self.main, 40, 20, self.main.width - 80, 60, "Install CD booter")
        self.main.title.set_font(size=20, bold=True, family="Arial")
        txt = "If your machine cannot boot off the CD, this program will install a new boot menu entry to help you boot from CD. In most cases this program is not needed, and it is sufficient to reboot with the CD-Rom in the tray.\n\nDo you want to proceed and install the CD booter?"
        self.main.label = ui.Label(self.main, 40, 90, self.main.width - 80, 80, txt)

    def on_cancel(self):
        self.frontend.cancel()

    def on_accessibility(self):
        self.frontend.show_page(self.frontend.accessibility_page)

    def on_install(self):
        self.frontend.stop()
