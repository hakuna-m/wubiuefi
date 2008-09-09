from winui import ui
from installation_finish_page import InstallationFinishPage
from installation_page import InstallationPage
from accessibility_page import AccessibilityPage
from progress_page import ProgressPage
import logging
import threading
log = logging.getLogger("WindowsFrontend")


class WindowsFrontend(ui.Application):
    _main_window_class_ = ui.MainDialogWindow

    def __init__(self, controller, *args, **kargs):
        log.debug("__init__...")
        self.controller = controller
        self.info = controller.info
        self.current_page = None
        kargs["text"] = "Ubuntu Setup"
        ui.Application.__init__(self, *args, **kargs)

    def cancel(self):
        if self.ask_confirmation("Are you sure you want to quit?", "Quitting"):
            log.info("Installation manually cancelled")
            self.quit()

    def on_quit(self):
        log.debug("frontend on_quit...")
        if hasattr(self, "tasklist") and self.tasklist:
            log.debug("stopping background task")
            self.tasklist.stop()
        self.controller.on_quit()

    def on_init(self):
        log.debug("on_init...")
        self.main_window.resize(504,385)
        self.installation_page = InstallationPage(self.main_window)
        self.accessibility_page = AccessibilityPage(self.main_window)
        self.progress_page = ProgressPage(self.main_window)
        self.installation_finish_page = InstallationFinishPage(self.main_window)

    def show_page(self, page):
        if self.current_page is page:
            self.current_page.show()
            return
        if self.current_page:
            self.current_page.hide()
        self.current_page = page
        page.show()

    def show_installer_page(self):
        self.show_page(self.installation_page)
        self.run()

    def show_installation_finish_page(self):
        self.show_page(self.installation_finish_page)
        self.run()

    def get_installation_settings(self):
        def on_ok(settings):
            self.installation_settings = settings
            self.stop()
        self.installation_settings = None
        self.accessibility_page = AccessibilityPage(self.main_window)
        self.installation_page = InstallationPage(self.main_window)
        self.installation_page.callback = on_ok
        self.show_page(self.installation_page)
        self.run()
        return self.installation_settings

    def run_tasks(self, tasklist):
        self.progress_page = ProgressPage(self.main_window)
        self.show_page(self.progress_page)
        tasklist.on_progress_callback = self.progress_page.on_progress
        self.tasklist = tasklist
        tasklist.start()
        self.run() #will be stopped by self.progress_page.on_progress
