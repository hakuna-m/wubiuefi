import datetime, time
import logging
log = logging.getLogger('Progress')

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
        self.task_is_complete = False
        self.subtask_is_complete = False
        self.subtask(subtask_name, total_substeps)

    def subtask(self, subtask_name="", total_substeps=1, step=1):
        if hasattr(self, "subtask_name"):
            log.debug("    Subtask: %s" % subtask_name)
            if step and self.subtask_name:
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
                log.exception("step > total_steps task=%s" % self.task_name)
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
                log.exception("substep > total_substeps subtask=%s" % self.subtask_name)
            self.total_subtime = self.start_subtime + float(self.run_subtime)*self.current_substep/self.total_substeps
        if self.total_substeps and self.current_substep == self.total_substeps:
            self.finish_subtask()
        self.notify()

    def finish_task(self):
        if self.total_steps and self.total_steps > self.current_step:
            self.step(self.total_steps - self.current_step )
        else:
            log.debug("Finished task: %s" % self.task_name)
            self.task_is_complete = True

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
