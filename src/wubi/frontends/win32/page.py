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
import os
import logging
import gettext
log = logging.getLogger("WinuiPage")


class Page(ui.Page):
    '''
    Base Page class
    Adds some handy methods
    '''

    def on_init(self):
        x, y, width, height = self.parent.get_client_rect()
        self.application = self.frontend.application
        self.info = self.application.info
        self.resize(width, height)
        self.width = width
        self.height = height
        language1 = self.info.locale and self.info.locale.split('.')[0]
        language2 = language1 and language1.split('_')[0]
        log.info("appname=%s, localedir=%s, languages=%s",self.info.application_name, self.info.translations_dir, [language1, language2])
        translation = gettext.translation(self.info.application_name, localedir=self.info.translations_dir, languages=[language1, language2, "en_US", "en"])
        translation.install(unicode=True)
    def insert_vertical_image(self, bmp_file):
        self.vertical_image = ui.Bitmap(
            self,
            0, 0, 164, 314)
        self.vertical_image.set_image(
            os.path.join(unicode(str(self.info.image_dir), 'mbcs'), unicode(str(bmp_file), 'mbcs')))
        self.vertical_image.width = 164

    def insert_header(self, title, subtitle, bmp_file):
        '''
        Inserts a header with image, title and subtitle
        '''
        hbh = 57
        hbw = 150
        self.header = ui.Panel(
            self,
            0, 0 , self.width, hbh+2)
        if bmp_file:
            self.header.image = ui.Bitmap(
                self.header,
                0, 0, hbw, hbh)
            self.header.image.set_image(
                os.path.join(unicode(str(self.info.image_dir), 'mbcs'), unicode(str(bmp_file), 'mbcs')))
        if title:
            self.header.title = ui.Label(
                self.header,
                hbw + 20, 10, self.width - 200, 16,
                text = title)
            self.header.title.set_font(bold=True)
        if subtitle:
            self.header.subtitle = ui.Label(
                self.header,
                hbw + 20, 26, self.width - 200, 26,
                text = subtitle)
        self.header.line = ui.EtchedRectangle(self.header,0, hbh,self.width, 2)
        self.header.height = hbh + 2
        self.header.set_background_color(255,255,255)

    def insert_main(self):
        '''
        Panel containing client widgets
        Inserts a control conatiner
        appropriately resized to take care of header and footer
        '''
        left=0
        top = 0
        width = self.width
        height = self.height
        if hasattr(self, "header"):
            top += self.header.height
            height -= self.header.height
        if hasattr(self, "navigation"):
            height -= self.navigation.height
        if hasattr(self, "vertical_image"):
            left = self.vertical_image.width
            width -= left
        self.main = ui.Panel(
            self,
            left, top, width, height)
        self.main.height = height
        self.main.width = width

    def insert_navigation(self, button1_text=None, button2_text=None, button3_text=None, default=None):
        '''
        Inserts navigation buttons starting from the leftmost button
        '''
        nbw = 90
        nbh = 24
        sep_top = 6
        sep_height = 2

        if hasattr(self, "vertical_image"):
            sep_top = 0

        self.navigation = ui.Panel(
            self,
            0, self.height - nbh - 20 -sep_top - sep_height, self.width, nbh + 20 + sep_top + sep_height)

        if not hasattr(self, "vertical_image"):
            self.revision_label = ui.Label(
                self.navigation,
                10, 0, 40, 20,
                "Rev %s" % self.info.revision)
            self.revision_label.disable()
            self.line = ui.EtchedRectangle(
                self.navigation,
                50, sep_top,self.width - 60, sep_height)
        else:
            self.line = ui.EtchedRectangle(
                self.navigation,
                0, sep_top, self.width, sep_height)

        for i,text in enumerate((button1_text, button2_text, button3_text)):
            if not text:
                continue
            if default and i + 1 == default:
                Button = ui.DefaultButton
            else:
                Button = ui.Button
            n = 0
            for other in (button1_text, button2_text, button3_text)[i:]:
                if other:
                    n += 1
            button = Button(
                self.navigation,
                self.width -(nbw + 10) * n, 10 + sep_top + sep_height, nbw, nbh,
                text=text)
            if default and i + 1 == default:
                button.set_focus()
            setattr(self.navigation, "button%s" % ( i + 1), button)
            self.navigation.height = nbh + 20 + sep_top + sep_height
