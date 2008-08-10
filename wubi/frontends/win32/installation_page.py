from lib.winui import ui
from page import Page
import logging
log = logging.getLogger("WinuiInstallationPage")


class InstallationPage(Page):
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

    def on_install(self):
        self.application.show_info_message("on_install")

    def on_accessibility(self):
        self.application.show_page(self.application.accessibility_page)
