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

    def set_backend_task(self, backend_task):
        self.backend_task = backend_task

    def on_progress(self, progress):
        self.main.task_label.set_text(progress.task_name)
        self.main.progressbar.set_position(progress.total_steps and int(100.0*progress.current_step/progress.total_steps) or 0)
        self.main.subtask_label.set_text(progress.subtask_name)
        self.main.subprogressbar.set_position(progress.total_substeps and int(100.0*progress.current_substep/progress.total_substeps) or 0)
        if progress.task_is_complete:
            self.main.progressbar.set_position(100)
            self.application.stop()
