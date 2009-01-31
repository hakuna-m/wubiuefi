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
            os.path.join(self.info.image_dir, bmp))
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

    def check_disk_free_space(self):
        if self.info.skip_size_check:
            return
        distro = self.get_distro()
        min_space_mb = distro.min_disk_space_mb + distro.max_iso_size/(1024**2)+ 100
        max_space_mb = 0
        max_space_mb2 = 0
        for drive in self.info.drives:
            if drive.type not in ['removable', 'hd']:
                continue
            max_space_mb = max(max_space_mb, drive.free_space_mb)
            if int(drive.free_space_mb/1024) * 1000 > min_space_mb:
                max_space_mb2 = max(max_space_mb2, drive.free_space_mb)
        if max_space_mb < 1024:
            message = "Only %sMB of disk space are available.\nAt least 1024MB are required as a bare minimum. Quitting"
            message = message % int(max_space_mb)
            self.frontend.quit()
        if max_space_mb2 < min_space_mb:
            message = "%sMB of disk size are required for installation.\nOnly %sMB are available.\nThe installation may fail in such circumstances.\nDo you wish to continue anyway?"
            min_space_mb = round(min_space_mb/1000+0.5)*1024
            message = message % (int(min_space_mb), int(max_space_mb))
            if not self.frontend.ask_confirmation(message):
                self.frontend.quit()
            else:
                self.info.skip_size_check = True

    def populate_drive_list(self):
        self.check_disk_free_space()
        distro = self.get_distro()
        min_space_mb = distro.min_disk_space_mb + distro.max_iso_size/(1024**2)+ 100
        self.drives_gb = []
        for drive in self.info.drives:
            if drive.type not in ['removable', 'hd']:
                continue
            drive_space_mb = int(drive.free_space_mb/1024) * 1000
            if self.info.skip_size_check \
            or drive_space_mb > min_space_mb:
                text = "%s (%sGB free)" % (drive.path, drive_space_mb/1000)
                self.drives_gb.append(text)
                self.target_drive_list.add_item(text)
        self.select_default_drive()

    def select_default_drive(self):
        drive = self.info.target_drive
        if drive:
            Drive = self.info.drives[0].__class__
            if isinstance(drive, Drive):
                pass
            else:
                drive = self.info.drives_dict.get(drive[:2].lower())
        if drive:
            drive = "%s (%sGB free)" % (drive.path, int(drive.free_space_mb/1024))
        else:
            drive = self.drives_gb[0]
        self.target_drive_list.set_value(drive)
        self.on_drive_change()

    def populate_size_list(self):
        target_drive = self.get_drive()
        distro = self.get_distro()
        min_space_mb = distro.min_disk_space_mb
        #this will be 1-2GB less than the disk free space, to have space for the ISO
        self.size_list_gb = []
        for i in range(1, 31):
            #~ log.debug("%s < %s and %s > %s" % (i * 1000 + distro.max_iso_size/1024**2 + 100 , target_drive.free_space_mb, i * 1000 , distro.min_disk_space_mb))
            if self.info.skip_size_check \
            or i * 1000 >= distro.min_disk_space_mb: #use 1000 as it is more conservative
                if i * 1000 + distro.max_iso_size/1024**2 + 100 <= target_drive.free_space_mb:
                    self.size_list_gb.append(i)
                    self.size_list.add_item("%sGB" % i)
        self.select_default_size()

    def select_default_size(self):
        if self.info.installation_size_mb:
            installation_size_gb = int(self.info.installation_size_mb/1000)
            for i in self.size_list_gb:
                if i >= installation_size_gb:
                    self.size_list.set_value("%sGB" % i)
                    return
        i = int(len(self.size_list_gb)/2)
        installation_size_gb = self.size_list_gb[i]
        self.size_list.set_value("%sGB" % installation_size_gb)
        self.on_size_change()

    def populate_distro_list(self):
        if self.info.cd_distro:
            distros = [self.info.cd_distro.name]
        elif self.info.iso_distro:
            distros = [self.info.iso_distro.name]
        else:
            distros = []
            for distro in self.info.distros:
                if distro.name not in distros:
                    distros.append(distro.name)
        for distro in distros:
            self.distro_list.add_item(distro)
        self.distro_list.set_value(distros[0])
        self.on_distro_change()

    def populate_language_list(self):
        languages = self.info.languages
        for language in languages:
            self.language_list.add_item(language)
        language = self.info.windows_language
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
        self.navigation.button3.on_click = self.on_cancel
        self.navigation.button2.on_click = self.on_install
        self.navigation.button1.on_click = self.on_accessibility

        #Main control container
        self.insert_main()
        h=24
        w=150

        picture, label, self.target_drive_list = self.add_controls_block(
            self.main, h, h,
            "install.bmp", "Installation drive:", True)
        # populated by on_distro_change
        self.target_drive_list.on_change = self.on_drive_change

        picture, label, self.size_list = self.add_controls_block(
                self.main, h, h*4,
                "systemsize.bmp", "Installation size:", True)
        # populated by on_drive_change
        self.size_list.on_change = self.on_size_change

        picture, label, self.distro_list = self.add_controls_block(
            self.main, h, h*7,
            "desktop.bmp", "Desktop environment:", True)
        self.populate_distro_list()
        self.distro_list.on_change = self.on_distro_change

        picture, label, self.language_list = self.add_controls_block(
            self.main, h*4 + w, h,
            "language.bmp", "Language:", True)
        self.populate_language_list()

        username = self.info.host_username.lower()
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
        password = ""
        if self.info.test:
            password = "test"
        self.password1 = ui.PasswordEdit(
            self.main,
            h*4 + w + 42, h*7-4, 150, 20,
            password, False)
        self.password2 = ui.PasswordEdit(
            self.main,
            h*4 + w + 42, h*7+20, 150, 20,
            password, False)
        self.error_label = ui.Label(
            self.main,
            40, self.main.height - 20, self.main.width - 80, 12,
            "")
        self.error_label.set_text_color(255, 0, 0)

    def get_drive(self):
        target_drive = self.target_drive_list.get_text()[:2].lower()
        drive = self.info.drives_dict.get(target_drive)
        return drive

    def get_distro(self):
        distro_name = str(self.distro_list.get_text()).lower()
        distro = self.info.distros_dict.get((distro_name, self.info.arch))
        return distro

    def get_installation_size_mb(self):
        installation_size = self.size_list.get_text()
        #using 1000 as opposed to 1024
        installation_size = int(installation_size[:-2])*1000
        return installation_size

    def on_distro_change(self):
        distro = self.get_distro()
        if not self.info.skip_memory_check:
            if self.info.total_memory_mb < distro.min_memory_mb:
                message = "%sMB of memory are required for installation.\nOnly %sMB are available.\nThe installation may fail in such circumstances.\nDo you wish to continue anyway?"
                message = message % (int(distro.min_memory_mb), int(self.info.total_memory_mb))
                if not self.frontend.ask_confirmation(message):
                    self.frontend.quit()
                else:
                    self.info.skip_memory_check = True
        self.populate_drive_list()

    def on_drive_change(self):
        self.info.target_drive = self.get_drive()
        self.populate_size_list()

    def on_size_change(self):
        self.info.installation_size_mb = self.get_installation_size_mb()

    def on_cancel(self):
        self.frontend.cancel()

    def on_accessibility(self):
        self.frontend.show_page(self.frontend.accessibility_page)

    def on_install(self):
        info = self.info
        drive = self.get_drive()
        installation_size_mb = self.get_installation_size_mb()
        distro = self.get_distro()
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
            "target_drive=%s\ninstallation_size=%sMB\ndistro_name=%s\nlanguage=%s\nusername=%s" \
            % (drive.path, installation_size_mb, distro.name, language, username))
        info.target_drive = drive
        info.distro = distro
        info.installation_size_mb = installation_size_mb
        info.language = language
        info.username = username
        info.password = get_md5(password1)
        self.frontend.stop()

def get_md5(str):
    m = md5.new(str)
    hash = m.hexdigest()
    return hash
