from winui import ui
from page import Page
import os
import logging
log = logging.getLogger("WinuiInstallationPage")


class InstallationPage(Page):

    def add_controls_block(self, parent, left, top, bmp, label, listitems=None):
        picture = ui.Bitmap(
            parent,
            left, top, 32, 32)
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
            combo.set_text(listitems[0])
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

        listitems = [
            "%s (%sGB free)" % (drive.path, int(drive.free_space_mb/1024))
            for drive in self.application.info.drives]
        picture, label, combo = self.add_controls_block(
            self.main, h, h,
            "install.bmp", "Installation drive:", listitems)

        listitems = ["4GB", "6GB", "8GB"]
        picture, label, combo = self.add_controls_block(
            self.main, h, h*4,
            "systemsize.bmp", "Installation size:", listitems)


        listitems = ["Ubuntu", "Kubuntu", "Xubuntu"]
        picture, label, combo = self.add_controls_block(
            self.main, h, h*7,
            "desktop.bmp", "Desktop environment:", listitems)

        listitems = self.application.info.languages
        picture, label, combo = self.add_controls_block(
            self.main, h*4 + w, h,
            "language.bmp", "Language:", listitems)

        picture, label, combo = self.add_controls_block(
            self.main, h*4 + w, h*4,
            "user.bmp", "Username:", None)
        self.username = ui.Edit(
            self.main,
            h*4 + w + 42, h*4+20, 150, 20,
            self.application.info.windows_username)

        picture, label, combo = self.add_controls_block(
            self.main, h*4 + w, h*7,
            "lock.bmp", "Password:", None)
        self.password1 = ui.Edit(
            self.main,
            h*4 + w + 42, h*7+20, 150, 20,
            "enter password")
        self.passowrd2 = ui.Edit(
            self.main,
            h*4 + w + 42, h*7+44, 150, 20,
            "repeat password")


        #~ self.pic3 = ui.Bitmap(
            #~ self.main,
            #~ left1, top5, 32, 32,
            #~ os.path.join(self.application.info.imagedir, "desktop.bmp"))

        #~ self.pic4 = ui.Bitmap(
            #~ self.main,
            #~ left3, top1, 32, 32,
            #~ os.path.join(self.application.info.imagedir, "language.bmp"))

        #~ self.pic5 = ui.Bitmap(
            #~ self.main,
            #~ left3, top3, 32, 32,
            #~ os.path.join(self.application.info.imagedir, "user.bmp"))

        #~ self.pic6 = ui.Bitmap(
            #~ self.main,
            #~ left3, top5, 32, 32,
            #~ os.path.join(self.application.info.imagedir, "lock.bmp"))

    def on_accessibility(self):
        self.application.show_page(self.application.accessibility_page)

    def on_install(self):
        self.callback("ok")
