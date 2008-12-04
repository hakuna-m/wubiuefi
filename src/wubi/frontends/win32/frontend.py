# Copyright (c) 2008 Agostino Russo
#
# Written by Agostino Russo <agostino.russo@gmail.com>
#
# This file is part of Wubi the Win32 Ubuntu Installer.
#
# Wubi is free software; you can redistribute it and/or modify
# it under 5the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation; either version 2.1 of
# the License, or (at your option) any later version.
#
# Wubi is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

from winui import ui
from installation_finish_page import InstallationFinishPage
from installation_page import InstallationPage
from uninstallation_page import UninstallationPage
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

    def cancel(self, confirm=False):
        if confirm:
            if self.ask_confirmation("Are you sure you want to quit?", "Quitting"):
                log.info("Installation manually cancelled")
                self.quit()
        else:
            self.quit()

    def on_quit(self):
        log.debug("frontend on_quit...")
        if hasattr(self, "tasklist") and self.tasklist:
            log.debug("stopping background task %s" % self.tasklist.name)
            self.tasklist.cancel()
            self.tasklist.join(1)
            if self.tasklist.isAlive():
                log.debug("Task cancellation timed out, the program will exit anyway")
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
        tasklist.progress_callback = self.progress_page.on_progress
        self.tasklist = tasklist
        tasklist.start()
        self.run() #will be stopped by self.progress_page.on_progress

    def get_uninstallation_settings(self):
        def on_ok(settings):
            self.stop()
        self.uninstallation_page = UninstallationPage(self.main_window)
        self.uninstallation_page.callback = on_ok
        self.show_page(self.uninstallation_page)
        self.run()
        return True

    def show_uninstallation_finish_page(self):
        self.progress_page.hide()
