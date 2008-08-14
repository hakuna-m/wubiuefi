from lib.winui import ui
from page import Page
import logging
log = logging.getLogger("WinuiAccessibilityPage")


class AccessibilityPage(Page):
    def on_init(self):
        Page.on_init(self)

        #header
        self.insert_header(
            "Accessibility profile",
            "Please select the appropriate accessibility prfoile",
            "Ubuntu-header.bmp")

        #navigation
        self.insert_navigation("Next >>", "Cancel", default=1)
        self.navigation.button2.on_click = self.application.cancel
        self.navigation.button1.on_click = self.on_next

        #Main control container
        self.insert_main()

        #visibility aids
        self.main.visibility_group = ui.GroupBox(self.main, 10, 10, 130, 120, text="Visibility Aids")
        self.main.visibility1_button = ui.RadioButton(self.main, 30, 30, 108, 20, text = "Visibility1")
        self.main.visibility2_button = ui.RadioButton(self.main, 30, 50, 108, 20, text = "Visibility2")
        self.main.visibility3_button = ui.RadioButton(self.main, 30, 70, 108, 20, text = "Visibility3")
        self.main.braille_button = ui.RadioButton(self.main, 30, 90, 108, 20, text = "Braille")

        #mobility aids
        self.main.mobility_group = ui.GroupBox(self.main, 160, 10, 130, 70, text="Mobility Aids")
        self.main.mobility1_button = ui.RadioButton(self.main, 180, 30, 108, 20, text = "Mobility1")
        self.main.mobility2_button = ui.RadioButton(self.main, 180, 50, 108, 20, text = "Mobility2")

        #no aids
        self.main.no_aids_button = ui.RadioButton(self.main, 180, 90, 108, 20, text="None")


    def on_next(self):
        self.application.show_page(self.application.installation_page)
