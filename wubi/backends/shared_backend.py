# USEFUL LINKS http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/180919
# about creating files, detecting drives...

import sys
import os
import locale
import struct
import datetime, time
import logging
log = logging.getLogger("SharedBackend")

class Progress(object):
    '''
    Helps tracking task progress
    '''
    def __init__(self, task_name="" , total_steps=None, subtask_name="", total_substeps=None, callback=None):
        log.debug("Task: %s" % task_name)
        self.callback = callback
        self.current_step = 0
        self.run_time = 0
        self.total_steps = total_steps
        self.start_time=time.time()
        self.total_time=None
        self.task_name = task_name
        self.subtask(subtask_name, total_substeps)

    def subtask(self, subtask_name="", total_substeps=1, step=1):
        if hasattr(self, "subtask_name"):
            log.debug("    Subtask: %s" % subtask_name)
            if step:
                self.finish_subtask(step=step) #finish previous subtask
        self.current_substep = 0
        self.run_subtime = 0
        self.total_substeps = total_substeps
        self.start_subtime=time.time()
        self.total_subtime=None
        self.subtask_name = subtask_name
        self.notify()

    def step(self, n=1, current_speed=None):
        self.current_step += n
        self.current_speed = current_speed
        self.run_time = time.time() - self.start_time
        if self.total_steps:
            if self.current_step > self.total_steps:
                raise Exception("step > total_steps task=%s" % self.task_name)
            self.total_time = self.start_time + float(self.run_time)*self.current_step/self.total_steps
        if self.total_steps and self.current_step == self.total_steps:
            self.finish_task()
        self.notify()

    def substep(self, n=1, current_subspeed=None):
        self.current_substep += n
        self.current_subspeed = current_subspeed
        self.run_subtime = time.time() - self.start_subtime
        if self.total_substeps:
            if self.current_substep > self.total_substeps:
                raise Exception("substep > total_substeps subtask=%s" % self.subtask_name)
            self.total_subtime = self.start_subtime + float(self.run_subtime)*self.current_substep/self.total_substeps
        if self.total_substeps and self.current_substep == self.total_substeps:
            self.finish_subtask()
        self.notify()

    def finish_task(self):
        if self.total_steps and self.total_steps > self.current_step:
            self.step(self.total_steps - self.current_step )
        else:
            log.debug("Finished task: %s" % self.task_name)

    def finish_subtask(self, step=1):
        if self.total_substeps and self.total_substeps > self.current_substep:
            self.substep(self.total_substeps - self.current_substep)
        else:
            log.debug("    Finished subtask: %s" % self.subtask_name)
            if step:
                self.step(step) #step up main task

    def notify(self):
        if callable(self.callback):
            self.callback(self)

    def __str__(self):
        return "Progress task=%s %s/%s, subtask=%s %s/%s" % (
            self.task_name, self.current_step, self.total_steps,
            self.subtask_name, self.current_substep, self.total_substeps,
        )

class Backend(object):
    '''
    Implements non-platform-specific functionality
    Subclasses need to implement platform-specific getters
    '''
    def __init__(self, application):
        self.application = application
        self.info = application.info

    def fetch_basic_info(self):
        '''
        Basic information required by the application dispatcher select_task()
        '''
        progress = Progress(task_name="Gathering basic information", total_steps=4)
        progress.subtask("Detect basic info")
        self.info.exedir = os.path.abspath(os.path.dirname(sys.argv[0]))
        self.info.platform = sys.platform
        self.info.osname = os.name
        self.info.language, self.info.encoding = locale.getdefaultlocale()
        self.info.environment_variables = os.environ
        progress.subtask("Detect arch")
        self.info.arch = struct.calcsize('P') == 8 and 64 or 32  #TBD detects python/os arch not processor arch
        progress.subtask("Detect if installed")
        self.info.is_installed = self.get_is_installed()
        progress.subtask("Detect running mode")
        self.info.is_running_from_cd = self.get_is_running_from_cd()

    def fetch_installer_info(self, progress_callback=None):
        '''
        Fetch information required by the installer
        '''
        progress = Progress(task_name="Gathering information", total_steps=1)
        progress.subtask("Detecting system information")
        self.fetch_system_info()
        progress.finish_subtask()

    def fetch_system_info(self):
        pass

    def install(self, progress_callback=None):
        progress = Progress(task_name="Installing", total_steps=5)
        progress.subtask("Subtask 1")
        progress.subtask("Subtask 2")
        progress.subtask("Subtask 3")
        progress.subtask("Subtask 4")
        progress.subtask("Subtask 5")
        progress.finish_subtask()

    def get_is_installed(self):
        '''
        Implemented in derived classes
        '''

    def get_is_running_from_cd(self):
        '''
        Implemented in derived classes
        '''

