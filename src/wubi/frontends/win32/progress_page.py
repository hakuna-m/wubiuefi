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
from page import Page
import logging
log = logging.getLogger("WinuiProgressPage")


class ProgressPage(Page):

    def on_init(self):
        Page.on_init(self)

        #header
        self.insert_header(
            #TBD change it to something more dynamic
            "Installing Ubuntu",
            "Please wait",
            "Ubuntu-header.bmp")

        #navigation
        self.insert_navigation("Cancel")
        self.navigation.button1.on_click = self.application.cancel

        #main container
        self.insert_main()
        self.main.task_label = ui.Label(self.main, 20, 20, self.width - 40, 20)
        self.main.progressbar = ui.ProgressBar(self.main, 20, 50, self.width - 40, 20)
        self.main.subtask_label = ui.Label(self.main, 20, 80, self.width - 40, 20)
        self.main.subprogressbar = ui.ProgressBar(self.main, 20, 110, self.width - 40, 20)

    def on_progress(self, tasklist):
        self.header.title.set_text(tasklist.name)
        self.main.progressbar.set_position(int(100.0*tasklist.tasks_completed()))
        self.main.task_label.set_text(tasklist.current_task.name)
        subtask = ""
        if tasklist.current_task.current_subtask_name:
            subtask += tasklist.current_task.current_subtask_name + " "
        if tasklist.current_task.percent_completed and tasklist.current_task.percent_completed<1:
            subtask +=  "Downloading (%.1f%%)" % (100.0*tasklist.current_task.percent_completed)
            self.main.subprogressbar.set_position(int(100.0*tasklist.current_task.percent_completed))
        self.main.subtask_label.set_text(subtask)
        if tasklist.tasks_completed() >= 1:
            self.main.progressbar.set_position(100)
            self.application.stop()
