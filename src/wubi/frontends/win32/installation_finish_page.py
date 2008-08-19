from winui import ui
from page import Page
import logging
log = logging.getLogger("WinuiInstallationFinishPage")


class InstallationFinishPage(Page):

    def on_init(self):
        Page.on_init(self)
        self.set_background_color(255,255,255)
        self.insert_vertical_image("Ubuntu-vertical.bmp")

        #navigation
        self.insert_navigation("Finish", default=1)
        self.navigation.button1.on_click = self.on_finish

        #main container
        self.insert_main()
        self.main.set_background_color(255,255,255)
        self.main.title = ui.Label(self.main, 40, 20, self.main.width - 80, 60, "Completing the Ubuntu Setup Wizard")
        self.main.title.set_font(size=20, bold=True, family="Arial")
        self.main.label = ui.Label(self.main, 40, 90, self.main.width - 80, 40, "You need to reboot to complete the installation")
        self.main.reboot_now = ui.RadioButton(self.main, 60, 150, self.main.width - 100, 20, "Reboot now")
        self.main.reboot_later = ui.RadioButton(self.main, 60, 180, self.main.width - 100, 20, "I want to manually reboot later")
        self.main.reboot_later.set_check(True)

    def on_finish(self):
        if self.main.reboot_now.is_checked():
            self.application.show_info_message("Rebooting")
        self.application.quit()
