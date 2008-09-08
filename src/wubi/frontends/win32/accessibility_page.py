from winui import ui
from page import Page
import logging
log = logging.getLogger("WinuiAccessibilityPage")


class AccessibilityPage(Page):
    def on_init(self):
        self.application.info.accessibility = ""
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
        h=30
        w = (self.width - h*7)/2

        self.main.visibility_group = ui.GroupBox(self.main, h, h*1, w+h*2, h*6 - 10, text="Visibility Aids")
        self.main.visibility1_button = ui.RadioButton(self.main, h*2, h*2, w, h, text = "Visibility1")
        self.main.visibility2_button = ui.RadioButton(self.main, h*2, h*3, w, h, text = "Visibility2")
        self.main.visibility3_button = ui.RadioButton(self.main, h*2, h*4, w, h, text = "Visibility3")
        self.main.braille_button = ui.RadioButton(self.main, h*2,  h*5, w, h, text = "Braille")

        #mobility aids
        self.main.mobility_group = ui.GroupBox(self.main, w+h*4, h*1, w+h*2, h*4 - 10, text="Mobility Aids")
        self.main.mobility1_button = ui.RadioButton(self.main, w+h*5, h*2, w, h, text = "Mobility1")
        self.main.mobility2_button = ui.RadioButton(self.main, w+h*5, h*3, w, h, text = "Mobility2")

        #no aids
        self.main.no_aids_button = ui.RadioButton(self.main, w+h*5, h*5 + 6, w, 20, text="None")
        self.main.no_aids_button.set_check(True)

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
        self.application.info.accessibility = accessibility
        self.application.show_page(self.application.installation_page)
