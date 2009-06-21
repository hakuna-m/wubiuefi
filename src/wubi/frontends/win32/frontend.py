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

import os
from winui import ui
from installation_finish_page import InstallationFinishPage
from installation_page import InstallationPage
from uninstallation_page import UninstallationPage
from uninstallation_finish_page import UninstallationFinishPage
from accessibility_page import AccessibilityPage
from progress_page import ProgressPage
from cd_menu_page import CDMenuPage
from cd_finish_page import CDFinishPage
from cdboot_page import CDBootPage
from wubi.errors import QuitException
import logging
log = logging.getLogger("WindowsFrontend")


class WindowsFrontend(ui.Frontend):
    _main_window_class_ = ui.MainDialogWindow

    def __init__(self, application, *args, **kargs):
        log.debug("__init__...")
        self.application = application
        self.current_page = None
        kargs["text"] = self.application.info.application_name
        kargs["icon"] = self.application.info.application_icon
        ui.Frontend.__init__(self, *args, **kargs)

    def cancel(self, confirm=False):
        log.info("Operation cancelled")
        if confirm:
            if not self.ask_confirmation(_("Are you sure you want to quit?")):
                log.info("Cancelled cancellation, resuming")
                return
        self.quit()

    def run(self):
        if self.application.info.quitting:
            raise QuitException()
        ui.Frontend.run(self)
        if self.application.info.quitting:
            raise QuitException()

    def quit(self):
        log.debug("frontend.quit")
        ui.Frontend.quit(self)

    def on_quit(self):
        log.debug("frontend.on_quit")
        if hasattr(self, "tasklist") and self.tasklist:
            if self.tasklist.isAlive():
                log.debug("stopping remaining background tasks: '%s'" % self.tasklist.name)
                self.tasklist.cancel()
                self.tasklist.join(3)
                if self.tasklist.isAlive():
                    log.debug("Task cancellation timed out, the program will exit anyway")
                    self.application.info.force_exit = True
        self.application.on_quit()

    def on_init(self):
        log.debug("on_init...")
        self.main_window.resize(504,385)

    def show_page(self, page):
        if self.current_page is page:
            self.current_page.show()
            return
        if self.current_page:
            self.current_page.hide()
        self.current_page = page
        page.show()
        self.main_window.show()
        self.run()

    def show_installer_page(self):
        self.installation_page = InstallationPage(self.main_window)
        self.accessibility_page = AccessibilityPage(self.main_window)
        self.show_page(self.installation_page)

    def show_cdboot_page(self):
        self.cdboot_page = CDBootPage(self.main_window)
        self.accessibility_page = AccessibilityPage(self.main_window)
        self.show_page(self.cdboot_page)

    def show_cd_menu_page(self):
        self.cd_menu_page = CDMenuPage(self.main_window)
        self.cd_finish_page = CDFinishPage(self.main_window)
        self.show_page(self.cd_menu_page)

    def show_installation_finish_page(self):
        self.installation_finish_page = InstallationFinishPage(self.main_window)
        self.show_page(self.installation_finish_page)

    def show_installation_settings(self):
        self.accessibility_page = AccessibilityPage(self.main_window)
        self.installation_page = InstallationPage(self.main_window)
        self.show_page(self.installation_page)

    def show_uninstallation_settings(self):
        self.uninstallation_page = UninstallationPage(self.main_window)
        self.show_page(self.uninstallation_page)

    def show_uninstallation_finish_page(self):
        self.uninstallation_finish_page = UninstallationFinishPage(self.main_window)
        self.show_page(self.uninstallation_finish_page)

    def run_tasks(self, tasklist):
        '''
        Runs the tasks in the specied tasklist, showing a progress page
        It is stopped by self.progress_page.on_progress
        '''
        self.progress_page = ProgressPage(self.main_window)
        tasklist.callback = self.progress_page.on_progress
        self.tasklist = tasklist
        tasklist.start()
        self.show_page(self.progress_page)
        if isinstance(tasklist.error, Exception):
            raise tasklist.error
        elif isinstance(tasklist.error, tuple):
            raise tasklist.error[0], tasklist.error[1], tasklist.error[2]
