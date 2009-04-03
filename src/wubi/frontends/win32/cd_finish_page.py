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
log = logging.getLogger("WinuiCDFinishPage")


class CDFinishPage(Page):

    def on_init(self):
        Page.on_init(self)
        self.set_background_color(255,255,255)
        self.insert_vertical_image("%s-vertical.bmp" % self.info.cd_distro.name)

        #navigation
        self.insert_navigation(_("< Back"), _("Finish"), _("Cancel"), default=2)
        self.navigation.button1.on_click = self.on_back
        self.navigation.button2.on_click = self.on_finish
        self.navigation.button3.on_click = self.on_cancel

        #main container
        self.insert_main()
        self.main.set_background_color(255,255,255)
        self.main.title = ui.Label(self.main, 40, 20, self.main.width - 80, 60, _("Reboot required"))
        self.main.title.set_font(size=20, bold=True, family="Arial")
        txt = _("To start the Live CD you need to reboot your machine leaving the CD in the tray. If your machine cannot boot from the CD, the last option should work in most cases.")
        self.main.label = ui.Label(self.main, 40, 90, self.main.width - 80, 40, txt)
        self.main.reboot_now = ui.RadioButton(self.main, 60, 150, self.main.width - 100, 20, _("Reboot now"))
        self.main.reboot_later = ui.RadioButton(self.main, 60, 180, self.main.width - 100, 20, _("I want to manually reboot Later"))
        self.main.cd_boot = ui.RadioButton(self.main, 60, 210, self.main.width - 100, 20, _("Help me to boot from CD"))
        self.main.reboot_later.set_check(True)

    def on_finish(self):
        if self.main.reboot_later.is_checked():
            self.application.quit()
        elif self.main.reboot_now.is_checked():
            self.info.run_task = "reboot"
        elif self.main.cd_boot.is_checked():
            self.info.run_task = "cd_boot"
        self.frontend.stop()

    def on_back(self):
        self.frontend.show_page(self.frontend.cd_menu_page)

    def on_cancel(self):
        self.frontend.cancel()
