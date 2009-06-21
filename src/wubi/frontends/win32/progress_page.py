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
import gettext
log = logging.getLogger("WinuiProgressPage")


class ProgressPage(Page):

    def on_init(self):
        Page.on_init(self)

        #header
        if self.info.distro:
            distro_name = self.info.distro.name
        elif self.info.previous_distro_name:
            distro_name = self.info.previous_distro_name
        self.insert_header(
            _("Installing %(distro)s-%(version)s") % dict(distro=distro_name, version=self.info.version),
            _("Please wait"),
            "%s-header.bmp" % distro_name)

        #navigation
        self.insert_navigation(_("Cancel"))
        self.navigation.button1.on_click = self.on_cancel

        #main container
        self.insert_main()
        self.main.task_label = ui.Label(self.main, 20, 20, self.width - 40, 20)
        self.main.progressbar = ui.ProgressBar(self.main, 20, 50, self.width - 40, 20)
        self.main.subtask_label = ui.Label(self.main, 20, 80, self.width - 40, 20)
        self.main.subprogressbar = ui.ProgressBar(self.main, 20, 110, self.width - 40, 20)
        self.main.localiso_button = ui.Button(self.main, 20, 150, 200, 20, _("Do not download, use a local file"))

        self.main.localiso_button.hide()
        self.main.subtask_label.hide()
        self.main.subprogressbar.hide()

    def on_progress(self, task, message=None):
        tasklist = task.get_root()
        self.header.title.set_text(tasklist.description)
        self.main.progressbar.set_position(int(100*tasklist.get_percent_of_tasks_completed()))
        self.main.task_label.set_text(task.description)
        if task.get_percent_completed() > 0:
            self.main.subprogressbar.set_position(int(100*task.get_percent_completed()))
            self.main.subtask_label.set_text(gettext.ngettext("Remaining time approximately %s","Remaining time approximately %s",task.estimate_remaining_time()) % task.estimate_remaining_time())
            self.main.subtask_label.show()
            self.main.subprogressbar.show()
        else:
            self.main.subtask_label.hide()
            self.main.subprogressbar.hide()
        if tasklist.status is not tasklist.ACTIVE:
            self.main.progressbar.set_position(100)
            self.frontend.stop()

    def on_cancel(self):
        self.frontend.cancel(confirm=True)
