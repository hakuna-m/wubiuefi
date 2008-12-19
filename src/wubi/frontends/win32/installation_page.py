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
from wubi.backends.common.mappings import reserved_usernames
import os
import logging
import sys
import re
import md5

log = logging.getLogger("WinuiInstallationPage")
if sys.version.startswith('2.3'):
    from sets import Set as set

reserved_usernames = [unicode(n) for n in reserved_usernames]
re_first_char_is_letter = re.compile("^[a-zA-Z_]")
re_only_alphanum = re.compile("^[\w]+$")

class InstallationPage(Page):

    def add_controls_block(self, parent, left, top, bmp, label, is_listbox):
        picture = ui.Bitmap(
            parent,
            left, top + 6, 32, 32)
        picture.set_image(
            os.path.join(self.application.info.imagedir, bmp))
        label = ui.Label(
            parent,
            left + 32 + 10, top, 150, 12,
            label)
        if is_listbox:
            combo = ui.ComboBox(
                parent,
                left + 32 + 10, top + 20, 150, 200,
                "")
        else:
            combo = None
        return picture, label, combo

    def populate_drive_list(self):
        #Check disk space
        if self.application.info.skipsizecheck:
            drives = [
                d for d in self.application.info.drives
                if d.type in ['removable', 'hd']
                and d.free_space_mb > 3000]
            if not drives:
                self.application.show_error_message("Not enough disk space, 2.5GB minimum are required")
                self.application.cancel()
        else:
            drives = [
                d for d in self.application.info.drives
                if d.type in ['removable', 'hd']
                and d.free_space_mb > 4000]
            if not drives:
                self.application.show_error_message("Not enough disk space, 4GB minimum are required")
                self.application.cancel()
        #Populate dialog
        drives = [
            "%s (%sGB free)" % (drive.path, int(drive.free_space_mb/1024))
            for drive in drives]
        for drive in drives:
            self.targetdrive_list.add_item(drive)
        self.targetdrive_list.set_value(drives[0])

    def populate_size_list(self):
        targetdrive = self.targetdrive_list.get_text()[:2]
        targetdrive = [d for d in self.application.info.drives if d.path == targetdrive]
        freespace = min(30, int(targetdrive[0].free_space_mb / 1024))
        listitems =  ["%sGB" % x for x in range(4, freespace)]
        for item in listitems:
            self.size_list.add_item(item)
        if listitems:
            self.size_list.set_value(listitems[max(0,len(listitems)-2)])

    def populate_distro_list(self):
        if self.application.info.cd_distro:
            distros = [self.application.info.cd_distro.name]
        elif self.application.info.iso_distro:
            distros = [self.application.info.iso_distro.name]
        else:
            distros = []
            for distro in self.application.info.distros:
                if distro.name not in distros:
                    distros.append(distro.name)
        for distro in distros:
            self.distro_list.add_item(distro)
        self.distro_list.set_value(distros[0])

    def populate_language_list(self):
        languages = self.application.info.languages
        for language in languages:
            self.language_list.add_item(language)
        language = self.application.info.windows_language
        self.language_list.set_value(language)

    def on_init(self):
        Page.on_init(self)

        #header
        self.insert_header(
            #TBD change it to something more dynamic
            "You are about to install Ubuntu",
            "Please select username and password for the new account",
            "Ubuntu-header.bmp")

        #navigation
        self.insert_navigation("Accessibility", "Install", "Cancel", default=2)
        self.navigation.button3.on_click = self.application.cancel
        self.navigation.button2.on_click = self.on_install
        self.navigation.button1.on_click = self.on_accessibility

        #Main control container
        self.insert_main()
        h=24
        w=150

        picture, label, self.targetdrive_list = self.add_controls_block(
            self.main, h, h,
            "install.bmp", "Installation drive:", True)
        self.populate_drive_list()

        picture, label, self.size_list = self.add_controls_block(
                self.main, h, h*4,
                "systemsize.bmp", "Installation size:", True)
        self.populate_size_list()

        picture, label, self.distro_list = self.add_controls_block(
            self.main, h, h*7,
            "desktop.bmp", "Desktop environment:", True)
        self.populate_distro_list()

        picture, label, self.language_list = self.add_controls_block(
            self.main, h*4 + w, h,
            "language.bmp", "Language:", True)
        self.populate_language_list()

        username = self.application.info.windows_username.lower()
        username = username.replace(' ', '_')
        username = username.replace('_', '__')
        picture, label, combo = self.add_controls_block(
            self.main, h*4 + w, h*4,
            "user.bmp", "Username:", None)
        self.username = ui.Edit(
            self.main,
            h*4 + w + 42, h*4+20, 150, 20,
            username, False)

        picture, label, combo = self.add_controls_block(
            self.main, h*4 + w, h*7,
            "lock.bmp", "Password:", None)
        label.move(h*4 + w + 42, h*7 - 24)
        self.password1 = ui.PasswordEdit(
            self.main,
            h*4 + w + 42, h*7-4, 150, 20,
            "", False)
        self.password2 = ui.PasswordEdit(
            self.main,
            h*4 + w + 42, h*7+20, 150, 20,
            "", False)

        self.error_label = ui.Label(
            self.main,
            40, self.main.height - 20, self.main.width - 80, 12,
            "")

    def on_accessibility(self):
        self.application.show_page(self.application.accessibility_page)

    def on_install(self):
        info = self.application.info
        targetdrive = self.targetdrive_list.get_text()[:2]
        installation_size = self.size_list.get_text()
        distro_name = str(self.distro_list.get_text())
        language = self.language_list.get_text()
        username = self.username.get_text()
        password1 = self.password1.get_text()
        password2 = self.password2.get_text()

        error_message = ""
        if not username:
            error_message = _("Please enter a valid username")
        elif username != username.lower():
            error_message = "Please use all lower cases in the username."
        elif " " in username:
            error_message =  "Please do not use spaces in the username."
        elif not re_first_char_is_letter.match(username):
            error_message =  "Your username must start with a letter."
        elif not re_only_alphanum.match(username):
            error_message =  "Your username must contain only standard letters and numbers."
        elif username in reserved_usernames:
            error_message = "The selected username is reserved, please selected a different one."
        elif not password1:
            error_message = "Please enter a valid password."
        elif " " in password1:
            error_message = "Please do not use spaces in the password."
        elif password1 != password2:
            error_message = "Passwords do not match."
        self.error_label.set_text(error_message)
        if error_message:
            return

        log.debug(
            "targetdrive=%s\ninstallation_size=%s\ndistro_name=%s\nlanguage=%s\nusername=%s" \
            % (targetdrive, installation_size, distro_name, language, username))

        info.targetdrive = targetdrive
        info.installation_size = installation_size
        info.installation_size_mb = int(installation_size[:-2])*1024*1024
        for distro in info.distros:
            if distro.name == distro_name \
            and distro.arch == info.arch:
                info.distro = distro
                break
        info.language = language
        info.username = username
        info.password = get_md5(password1)
        self.callback("ok")

def get_md5(str):
    m = md5.new(str)
    hash = m.hexdigest()
    return hash
