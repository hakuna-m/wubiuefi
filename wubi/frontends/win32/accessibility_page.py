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

        #visibility aids
        top = self.header.height
        self.visibility_group = ui.GroupBox(self, 10, top + 10, 130, 120, text="Visibility Aids")
        self.visibility1_button = ui.RadioButton(self, 30, top + 30, 108, 20, text = "Visibility1")
        self.visibility2_button = ui.RadioButton(self, 30, top + 50, 108, 20, text = "Visibility2")
        self.visibility3_button = ui.RadioButton(self, 30, top + 70, 108, 20, text = "Visibility3")
        self.braille_button = ui.RadioButton(self, 30, top + 90, 108, 20, text = "Braille")

        #mobility aids
        self.mobility_group = ui.GroupBox(self, 160, top + 10, 130, 70, text="Mobility Aids")
        self.mobility1_button = ui.RadioButton(self, 180, top + 30, 108, 20, text = "Mobility1")
        self.mobility2_button = ui.RadioButton(self, 180, top + 50, 108, 20, text = "Mobility2")

        #no aids
        self.no_aids_button = ui.RadioButton(self, 180, top + 90, 108, 20, text="None")


    def on_next(self):
        self.application.show_page(self.application.installation_page)
