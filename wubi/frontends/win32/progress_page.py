from lib.winui import ui
from page import Page
import logging
log = logging.getLogger("WinuiIProgressPage")


class ProgressPage(Page):

    def on_init(self):
        Page.on_init(self)

        #header
        self.insert_header(
            "Installing Ubuntu 8.10",
            "Please wait",
            "Ubuntu-header.bmp")

        #navigation
        self.insert_navigation("Cancel")
        self.navigation.button1.on_click = self.application.cancel

        #main container
        self.insert_main()
        self.main.task_label = ui.Label(self.main, 20, 20, self.width - 200, 20)
        self.main.progressbar = ui.ProgressBar(self.main, 20, 40, self.width - 200, 20)
        self.main.subtask_label = ui.Label(self.main, 20, 60, self.width - 200, 20)
        self.main.subprogressbar = ui.ProgressBar(self.main, 20, 80, self.width - 200, 20)

    def on_progress(self, task):
        self.main.task_label.set_text(task.name)
        self.main.progressbar.set_position(int(100.0*task.task_progress))
        self.main.subtask_label.set_text(task.current_subtask_name)
        self.main.subprogressbar.set_position(int(100.0*task.total_progress))
        if task.is_finished:
            self.main.progressbar.set_position(100)
            self.application.stop()
