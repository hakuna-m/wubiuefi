from winui import ui
from page import Page
from backends.common.helpers import get_md5
from backends.common.mappings import reserved_usernames
import os
import logging
import sys
import re
log = logging.getLogger("WinuiInstallationPage")
if sys.version.startswith('2.3'):
    from sets import Set as set

reserved_usernames = [unicode(n) for n in reserved_usernames]
re_first_char_is_letter = re.compile("^[a-zA-Z_]")
re_only_alphanum = re.compile("^[\w]+$")

class InstallationPage(Page):

    def add_controls_block(self, parent, left, top, bmp, label, listitems=None):
        picture = ui.Bitmap(
            parent,
            left, top + 6, 32, 32)
        picture.set_image(
            os.path.join(self.application.info.imagedir, bmp))
        label = ui.Label(
            parent,
            left + 32 + 10, top, 150, 12,
            label)
        if listitems:
            combo = ui.ComboBox(
                parent,
                left + 32 + 10, top + 20, 150, 200,
                "")
            for item in listitems:
                combo.add_item(item)
            combo.set_value(listitems[0])
        else:
            combo = None
        return picture, label, combo


    def on_init(self):
        Page.on_init(self)

        #header
        self.insert_header(
            "You are about to install Ubuntu 8.10",
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

        #Check disk space
        if self.application.info.skipsizecheck:
            drives = [
                d for d in self.application.info.drives
                if d.type in ['removable', 'hd']
                and d.free_space_mb > 2500]
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
        listitems = [
            "%s (%sGB free)" % (drive.path, int(drive.free_space_mb/1024))
            for drive in drives]
        picture, label, self.targetdrive_list = self.add_controls_block(
            self.main, h, h,
            "install.bmp", "Installation drive:", listitems)

        targetdrive = self.targetdrive_list.get_text()[:2]
        targetdrive = [d for d in self.application.info.drives if d.path == targetdrive]
        freespace = min(30, int(targetdrive[0].free_space_mb / 1024))
        listitems =  ["%sGB" % x for x in range(4, freespace)]
        picture, label, self.size_list = self.add_controls_block(
                self.main, h, h*4,
                "systemsize.bmp", "Installation size:",
                listitems)
        self.size_list.set_value(listitems[max(0,len(listitems)-2)])

        if self.application.info.cd_distro:
            distros = [self.application.info.cd_distro.name]
        else:
            distros = set([d.name for d in self.application.info.distros])
            distros = list(distros)
            distros.sort()
            #TBD set a default distro and/or distro ordering
        picture, label, self.distro_list = self.add_controls_block(
            self.main, h, h*7,
            "desktop.bmp", "Desktop environment:", distros)

        listitems = self.application.info.languages
        picture, label, self.language_list = self.add_controls_block(
            self.main, h*4 + w, h,
            "language.bmp", "Language:", listitems)
        self.language_list.set_value(self.application.info.windows_language)

        username = self.application.info.windows_username.lower()
        username = username.replace(' ', '_')
        username = username.replace('_', '__')
        picture, label, combo = self.add_controls_block(
            self.main, h*4 + w, h*4,
            "user.bmp", "Username:", None)
        self.username = ui.Edit(
            self.main,
            h*4 + w + 42, h*4+20, 150, 20,
            username)

        picture, label, combo = self.add_controls_block(
            self.main, h*4 + w, h*7,
            "lock.bmp", "Password:", None)
        label.move(h*4 + w + 42, h*7 - 24)
        self.password1 = ui.PasswordEdit(
            self.main,
            h*4 + w + 42, h*7-4, 150, 20,
            "")
        self.password2 = ui.PasswordEdit(
            self.main,
            h*4 + w + 42, h*7+20, 150, 20,
            "")

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
        for distro in info.distros:
            if distro.name == distro_name \
            and distro.arch == info.arch:
                info.distro = distro
                break
        info.language = language
        info.username = username
        info.password = get_md5(password1)
        self.callback("ok")
