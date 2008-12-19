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


import time
import threading
import logging

log = logging.getLogger("TaskList")


class Task(object):
    '''
    Each task is associated to a function and/or a list of subtasks
    The task runs the associated function and subtasks, and keeps track of progress
    New subtasks can be added at runtime, and nested configurations are possible
    The task can be run in a separate thread using ThreadedTaskList

    An observer needs to provide a callback to the Task constructor
    The callback will be triggered any time there is a change in progress or status
    The callback will receive as argument the task object itself and a message.

    The function associated to a Task can optionally support an argument called
    'associated_task', if such argument is in the function argument list,
    it will be bounded at runtime to the associated task, so that the function can
    call the associated task methods (set_progress in particular).

    If set_progress returns True then the function has to terminate immediately.

    Use the "weight" argument to set the relative time an associated function takes
    compared to the other tasks (without including subtasks).
    You can use estimated number of seconds for that.
    '''

    INACTIVE = 0
    ACTIVE = 1
    COMPLETED = 2
    FAILED = 3
    CANCELLED = 4

    def __init__(self, name, associated_function=None, is_required=True, weight=0):
        self.name = name
        self._percent_completed = 0
        self._current_speed = None
        self._last_message = None
        self._last_error = None
        self.start_time = 0
        self.end_time = 0
        self.status = Task.INACTIVE
        self.current_subtask = None
        self.parent = None
        self.associated_function = associated_function
        self.associated_function_args = []
        self.associated_function_kargs = {}
        self.associated_function_weight = weight
        self.associated_function_result = None
        self.callback = None
        self.is_required = is_required
        self.subtasks = []

    def add_subtask(self, name, associated_function=None, is_required=True, weight=1):
        subtask = Task(name)
        subtask.parent = self
        subtask.is_required = is_required
        self.subtasks.append(subtask)
        if callable(associated_function):
            subtask.associated_function = associated_function
            subtask.associated_function_weight = weight
        return subtask

    def add_subtasks(self, subtasks):
        for subtask in subtasks:
            if isinstance(subtask, Task):
                subtask.parent = self
                self.subtasks.append(subtask)
            elif isinstance(subtask, (list, tuple)):
                self.add_subtask(*subtask)
            elif isinstance(subtask, dict):
                self.add_subtask(*subtask)

    def set_progress(self, percent_completed=None, message=None, current_speed=None):
        '''
        The associated function will call this method on progress.
        Then the message is propagated to the tasklist on_progress listener
        This method will return True if the function has to cancel operation
        When called without arguments, it returns True if the task was cancelled or finished.
        '''
        if self.is_cancelled():
            return True
        self._percent_completed = percent_completed
        self._current_speed = current_speed
        if percent_completed >= 1:
            self.run_subtasks()
            self.finish()
            if message is None:
                message = self.get_indent() + "Finished %s" % self.name
        if message is None:
            message = self.get_indent() + self.name
        self.notify_listeners(message)

    def finish(self):
        self.percent_completed = 1
        self.end_time = time.time()
        self.status = Task.COMPLETED

    def notify_listeners(self, message):
        if callable(self.callback):
            self.callback(self, message=message)
        if self.parent:
            self.parent.notify_listeners(message=message)

    def cancel(self):
        self.status = Task.CANCELLED
        self.notify_listeners("Cancelling %s" % self.name)

    def is_cancelled(self):
        return self.status is Task.CANCELLED or \
            (self.parent and self.parent.is_cancelled())

    def is_active(self):
        return self.status is Task.ACTIVE and \
            (self.parent is None or self.parent.is_active())

    def run(self, *args, **kargs):
        if self.status is not Task.INACTIVE \
        or self.parent and not self.parent.is_active():
            return
        self.status = Task.ACTIVE
        self.start_time = time.time()
        message = self.get_indent() + "%s ..." % self.name
        log.debug(message)
        self.set_progress(0, message)
        if callable(self.associated_function):
            if args:
                self.associated_function_args = args
            if kargs:
                self.associated_function_kargs = kargs
            if 'associated_task' in self.associated_function.func_code.co_varnames:
                self.associated_function_kargs['associated_task'] = self
            try:
                result = self.associated_function(*self.associated_function_args, **self.associated_function_kargs)
                self.associated_function_result = result
            except Exception, err:
                self.status = Task.FAILED
                if self.is_required:
                    log.exception(err)
                    raise err
                else:
                    log.error("Non fatal error %s in task %s" % (err.description, self.name))
                    self.notify_listeners(self.get_indent() + "Error: %s" % err.description)
        self.run_subtasks()
        self.set_progress(1)
        log.debug(self.get_indent() + "Finished %s" % self.name)
        return self.associated_function_result

    def run_subtasks(self):
        for subtask in self.subtasks:
            self.current_subtask = subtask
            subtask.run()

    def get_root(self):
        if self.parent:
            return self.parent.get_root()
        return self

    def get_progress(self):
        '''
        progress for current task and its subtasks
        use get_root().get_progress() for the total progress
        '''
        return 1.0*self._get_completed()/self._get_weight()

    def _get_completed(self):
        completed_subtasks = [s._get_completed() for s in self.subtasks]
        return self._percent_completed*self.associated_function_weight + sum(completed_subtasks)

    def _get_weight(self):
        subtasks_weight = [s._get_weight() for s in self.subtasks]
        return self.associated_function_weight + sum(subtasks_weight)

    def estimate_end_time(self):
        '''
        estimates end time for current tasks
        use get_root().estimate_end_time() for the total end time
        '''
        progress = self.get_progress()
        if progress:
            return self.start_time + (time.time() - self.start_time)/self.get_progress()
        else:
            return time.time() + self._get_weight()

    def get_level(self):
        level = 1
        if self.parent:
            level += self.parent.get_level()
        return level

    def get_indent(self):
        return "  " * (self.get_level()-1)

    def get_speed(self):
        if self.current_subtask:
            speed = self.current_subtask.get_speed()
            if speed is not None:
                return speed
        return self._current_speed


class TaskList(Task):
    '''
    Root Task object which contains other tasks
    '''
    def __init__(self, name, tasks=None, callback=None):
        Task.__init__(self, name)
        self.callback = callback
        if tasks:
            self.add_subtasks(tasks)


class ThreadedTaskList(threading.Thread, TaskList):
    '''
    A TaskList that runs in a separate thread
    Can be started and stopped.
    Should be used as root Task object which contains other tasks.
    '''
    def __init__ (self, name, tasks=None, callback=None):
        threading.Thread.__init__(self)
        TaskList.__init__(self, name, tasks=tasks, callback = callback)
        self._stopped_event = threading.Event()
        self.setDaemon(True) #do not prevent the main application from closing

    def cancel(self):
        self._stopped_event.set()
        TaskList.cancel(self)

    def run(self):
        TaskList.run(self)

    def is_cancelled(self):
        return self._stopped_event.isSet() or TaskList.is_cancelled(self)


if __name__ == "__main__":

    def fsleep():
        time.sleep(1)

    def fcallback(associated_task=None):
        time.sleep(1)
        if associated_task.set_progress(.3): return
        time.sleep(1)
        if associated_task.set_progress(.6): return
        time.sleep(1)
        associated_task.add_subtask("fsleepsub", fsleep)

    def callback(task, message):
        tasklist = task.get_root()
        progress = tasklist.get_progress()*100
        secs = int(tasklist.estimate_end_time()- time.time())
        print "%s (%s%% completed, %s secs remaining)" % (message, progress, secs)
    tasks = [
        ("fsleep1", fsleep),
        ("fsleep2", fsleep),
        ("fcallback1", fcallback, True),
        ("fcallback2", fcallback, True)]
    tasklist = ThreadedTaskList("test 1", tasks=tasks, callback=callback)
    tasklist.run()
