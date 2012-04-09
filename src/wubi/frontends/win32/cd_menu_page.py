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
log = logging.getLogger("WinuiICDMenuPage")


class CDMenuPage(Page):

    def on_init(self):
        Page.on_init(self)
        self.set_background_color(255,255,255)
        self.insert_vertical_image("%s-vertical.bmp" % self.info.cd_distro.name)
        distro_name = self.info.cd_distro.name
        self.frontend.set_title(_("%s Menu") % distro_name)
        cd_drive = self.info.drives_dict.get(self.info.cd_path[:2].lower())

        #navigation
        self.insert_navigation(_("Cancel"))
        self.navigation.button1.on_click = self.on_cancel

        #main container
        self.insert_main()
        self.main.set_background_color(255,255,255)
        x = 10
        sep = 8
        y = 10
        bw = 200
        lw = self.main.width - x*2
        bh = 30
        lh = 66

        #boot from cd
        self.main.boot_cd_button = ui.FlatButton(self.main, x, y, bw, bh, _("Demo and full installation"))
        y += bh + 2
        txt = _("Try %(distro)s without installing! Simply reboot your machine with the CD in the tray. You may perform a full installation from within the demo to install %(distro)s either alongside Windows or as the only operating system.")
        txt = txt % dict(distro=distro_name)
        self.main.boot_cd_label = ui.Label(self.main, x, y, lw, lh, txt)
        self.main.boot_cd_button.on_click = self.on_cd_boot

        #wubi
        used = ((cd_drive.total_space_mb - cd_drive.free_space_mb)*1024*1024)
        # Hide Wubi from the autorun page, per bug #975251.
        if self.info.force_wubi:
            y += lh + sep
            self.main.wubi_button = ui.FlatButton(self.main, x, y, bw, bh, _("Install inside Windows"))
            y += bh + 2
            txt = _("Install and uninstall %(distro)s like any other application, without the need for a dedicated partition. You will be able to boot into either Windows or %(distro)s. Hibernation is not enabled in this mode and disk performance is slightly reduced.")
            txt = txt % dict(distro=distro_name)
            self.main.wubi_label = ui.Label(self.main, x, y, lw, lh, txt)
            self.main.wubi_button.on_click = self.on_wubi

        #info
        y += lh + sep
        self.main.info_button = ui.FlatButton(self.main, x, y, bw, bh, _("Learn more"))
        y += bh + 2
        txt = _("%(distro)s is a free, community developed, linux-based operating system complete with a web browser, productivity software, instant messaging, and much more.")
        txt = txt % dict(distro=distro_name)
        self.main.info_label = ui.Label(self.main, x, y, lw, lh, txt)
        self.main.info_button.on_click = self.on_info

    def on_cd_boot(self):
        self.frontend.show_page(self.frontend.cd_finish_page)

    def on_wubi(self):
        self.info.run_task = "install"
        self.frontend.stop()

    def on_info(self):
        self.info.run_task = "show_info"
        self.frontend.stop()

    def on_cancel(self):
        self.frontend.cancel()
