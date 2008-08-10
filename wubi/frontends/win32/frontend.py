from lib.winui import ui
from installation_page import InstallationPage
from accessibility_page import AccessibilityPage
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
        self.main_window.resize(506,386)
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

    def run_installer(self):
        self.show_page(self.installation_page)
        self.run()
