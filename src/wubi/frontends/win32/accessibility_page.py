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
log = logging.getLogger("WinuiAccessibilityPage")


class AccessibilityPage(Page):
    def on_init(self):
        Page.on_init(self)
        self.info.accessibility = ""

        #header
        self.insert_header(
            _("Accessibility profile"),
            _("Please select the appropriate accessibility profile"),
            "%s-header.bmp" % self.info.distro)

        #navigation
        self.insert_navigation(_("Next >>"), _("Cancel"), default=1)
        self.navigation.button2.on_click = self.on_cancel
        self.navigation.button1.on_click = self.on_next

        #Main control container
        self.insert_main()

        #visibility aids
        h=30
        w = (self.width - h*7)/2

        self.main.visibility_group = ui.GroupBox(self.main, h, h*1, w+h*2, h*6 - 10, text=_("Visibility Aids"))
        self.main.visibility1_button = ui.RadioButton(self.main, h*2, h*2, w, h, text = _("Visibility1"))
        self.main.visibility2_button = ui.RadioButton(self.main, h*2, h*3, w, h, text = _("Visibility2"))
        self.main.visibility3_button = ui.RadioButton(self.main, h*2, h*4, w, h, text = _("Visibility3"))
        self.main.braille_button = ui.RadioButton(self.main, h*2,  h*5, w, h, text = _("Braille"))

        #mobility aids
        self.main.mobility_group = ui.GroupBox(self.main, w+h*4, h*1, w+h*2, h*4 - 10, text=_("Mobility Aids"))
        self.main.mobility1_button = ui.RadioButton(self.main, w+h*5, h*2, w, h, text = _("Mobility1"))
        self.main.mobility2_button = ui.RadioButton(self.main, w+h*5, h*3, w, h, text = _("Mobility2"))

        #no aids
        self.main.no_aids_button = ui.RadioButton(self.main, w+h*5, h*5 + 6, w, 20, text=_("None"))
        self.main.no_aids_button.set_check(True)

    def on_cancel(self):
        self.frontend.cancel()

    def on_next(self):
        accessibility = ""
        if self.main.braille_button.is_checked():
            accessibility = "braille=ask"
        elif self.main.visibility1_button.is_checked():
            accessibility = "access=visibility1"
        elif self.main.visibility2_button.is_checked():
            accessibility = "access=visibility2"
        elif self.main.visibility3_button.is_checked():
            accessibility = "access=visibility3"
        elif self.main.mobility1_button.is_checked():
            accessibility = "access=mobility1"
        elif self.main.mobility2_button.is_checked():
            accessibility = "access=mobility2"
        self.info.accessibility = accessibility
        self.frontend.show_page(self.frontend.installation_page)
