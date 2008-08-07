from win32ui import ui
from win32ui.wizard import Wizard
import logging
log = logging.getLogger("WindowsFrontend")


class WindowsFrontend(ui.Application):
    _main_window_class_ = ui.MainDialogWindow
    
    def __init__(self, controller, *args, **kargs):
        log.debug("__init__...")
        self.controller = controller
        self.info = controller.info
        self.current_page = None
        ui.Application.__init__(self, *args, **kargs)

    def cancel(self):
        if self.ask_confirmation("Are you sure you want to quit?", "Quitting"):
            self.quit()

    def on_init(self):
        log.debug("on_init...")
        self.main_window.resize(600,400)
        self.installation_page = InstallationPage(self.main_window)
        self.accessibility_page = AccessibilityPage(self.main_window)
        
    def on_quit(self):
        self.controller.on_quit()

    def show_page(self, page):
        if self.current_page is page:
            self.current_page.show()
            return
        if self.current_page:
            self.current_page.hide()
        self.current_page = page
        page.show()

    class Page(ui.Page):
        pass

    def run_installer(self):
        self.show_page(self.installation_page)
        self.run()

class InstallationPage(ui.Page):
    def on_init(self):
        x, y, width, height = self.parent.get_client_rect()
        self.resize(width, height)
        self.button_cancel = ui.Button(self, width - 100 , height - 34, 90, 24, text="Cancel")
        self.button_install = ui.DefaultButton(self, width - 210 , height - 34, 90, 24, text="Install")
        self.button_accessibility = ui.Button(self, width - 320 , height - 34, 90, 24, text="Accessibility")
        self.button_cancel.on_click = self.application.cancel
        self.button_accessibility.on_click = self.on_accessibility
        self.button_install.on_click = self.on_install

    def on_install(self):
        self.application.show_info_message("on_install")

    def on_accessibility(self):
        self.application.show_page(self.application.accessibility_page)

class AccessibilityPage(ui.Page):
    def on_init(self):
        x, y, width, height = self.parent.get_client_rect()
        self.resize(width, height)
        self.button_cancel = ui.Button(self, width - 100 , height - 34, 90, 24, text="Cancel")
        self.button_next = ui.DefaultButton(self, width - 210 , height - 34, 90, 24, text="Next >>")
        self.button_cancel.on_click = self.application.cancel
        self.button_next.on_click = self.on_next

    def on_next(self):
        self.application.show_page(self.application.installation_page)
