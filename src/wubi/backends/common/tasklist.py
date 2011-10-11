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
import sys

log = logging.getLogger("TaskList")

class Task(object):
    '''
    Each task is associated to a function and optionally a list of subtasks
    The task runs the associated function and then the subtasks, and keeps track of progress
    New subtasks can be added at runtime, and nested configurations are possible
    The task can be run in a separate thread using ThreadedTaskList

    An observer needs to provide a callback by the setting the callback property
    of the Task instance
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

    def __init__(self, associated_function, name=None, description=None, size=None, unit=None, weight=None, is_required=None):
        self.associated_function = associated_function
        if name:
            self.name = name
        elif hasattr(associated_function, "name"):
            self.name = associated_function.name
        else:
            self.name = associated_function.__name__
        if description:
            self._description = description
        elif hasattr(associated_function, "description"):
            self._description = associated_function.description
        else:
            self._description = None
        if unit:
            self.unit = unit
        elif hasattr(associated_function, "unit"):
            self.unit = associated_function.unit
        else:
            self.unit = None
        if weight:
            self.weight = weight
        elif hasattr(associated_function, "weight"):
            self.weight = associated_function.weight
        else:
            self.weight = 1
        if size:
            self.size = size
        elif hasattr(associated_function, "size"):
            self.size = associated_function.size
        else:
            self.size = 1
        if is_required is not None:
            self.is_required = is_required
        elif hasattr(associated_function, "is_required"):
            self.is_required  = associated_function.is_required
        else:
            self.is_required  = True
        self.completed = 0
        self.last_completed = 0
        self.start_time = 0
        self.end_time = 0
        self.status = Task.INACTIVE
        self._speed = None
        self.progress_timestamp = None
        self.last_progress_timestamp = None
        self.current_subtask = None
        self.parent = None
        self.associated_function_args = []
        self.associated_function_kargs = {}
        self.associated_function_result = None
        self.error = None
        self.callback = None
        self.subtasks = []

    def add_subtask(self, task_or_function, name=None, description=None, size=None, unit=None, weight=None, is_required=None):
        if isinstance(task_or_function, Task):
            task = task_or_function
        else:
            task = Task(task_or_function, name, description, size, unit, weight, is_required)
        task.parent = self
        self.subtasks.append(task)
        message = "New task %s" % task.name
        log.debug(message)
        self._notify_listeners(message)
        return task

    def set_progress(self, completed=0, size=None, unit="", speed=None, message=None):
        '''
        The associated function will call this method on progress.
        Then the message is propagated to the parent and any listener
        This method will return True if the function has to cancel operation
        '''
        if self.is_cancelled():
            return True
        self._speed = speed
        self.last_progress_timestamp = self.progress_timestamp
        self.progress_timestamp = time.time()
        self.last_completed = self.completed
        self.completed = completed
        if size:
            self.size = size
        if completed >= self.size:
            self._run_subtasks()
            self.finish()
        else:
            if not message:
                message = "Progress"
            self._notify_listeners(message)

    def finish(self):
        if self.status == Task.COMPLETED:
            return
        message = "Finished %s" % self.name
        self.log(message)
        self.completed = self.size
        self.end_time = time.time()
        self.status = Task.COMPLETED
        self._notify_listeners(message)

    def log(self, message, indent=True, log_level=logging.DEBUG):
        if indent:
            message = "#" * self.get_level()  + " " + message
        log.log(log_level, message)

    def cancel(self):
        self.status = Task.CANCELLED
        message = "Cancelling %s" % self.name
        self.log(message)
        self._notify_listeners(message)

    def is_cancelled(self):
        return self.status is Task.CANCELLED or \
            (self.parent and self.parent.is_cancelled())

    def is_active(self):
        return self.status is Task.ACTIVE and \
            (self.parent is None or self.parent.is_active())

    def __call__(self, *args, **kargs):
        if self.status is not Task.INACTIVE \
        or self.parent and not self.parent.is_active():
            return
        message = "Running %s..." % self.name
        self.log(message)
        self.error = None
        self.status = Task.ACTIVE
        self.start_time = time.time()
        self._notify_listeners(message)
        if callable(self.associated_function):
            if args:
                self.associated_function_args = args
            if kargs:
                self.associated_function_kargs = kargs
            if 'associated_task' in self.associated_function.func_code.co_varnames:
                self.associated_function_kargs['associated_task'] = self
            result = None
            try:
                result = self.associated_function(*self.associated_function_args, **self.associated_function_kargs)
            except Exception, err:
                self.error = sys.exc_info()
                self.status = Task.FAILED
                log.exception(err)
                if self.is_required:
                    root = self.get_root()
                    root.error = self.error
                    root.cancel()
                    return
                else:
                    message = "Non fatal error %s in task %s" % (err, self.name)
                    log.error(message)
                    self._notify_listeners(message)
            self.associated_function_result = result
        self._run_subtasks()
        self.finish()
        return self.associated_function_result

    def get_root(self):
        if self.parent:
            return self.parent.get_root()
        return self

    def get_speed(self):
        if self._speed:
            return self._speed
        if not self.last_completed or not self.completed:
            return ""
        task_time = self.progress_timestamp - self.last_progress_timestamp
        if not task_time:
            return ""
        speed = (self.completed - self.last_completed)/task_time
        if int(speed) <= 0:
            return ""
        unit = "ps"
        if self.unit:
            unit = self.unit + unit
        speed = "%i%s" % (int(speed), unit)
        return speed

    def estimate_end_time(self):
        '''
        estimates end time for current tasks and associated subtasks
        use get_root().estimate_end_time() for the total end time
        '''
        progress = self.get_percent_completed()
        if self.end_time:
            return self.end_time
        if progress:
            return self.start_time + (time.time() - self.start_time)/progress
        else:
            return time.time() + self._get_weight()

    def estimate_remaining_time(self):
        '''
        Remaining time in human readable format
        '''
        if self.end_time:
            return _("0s")
        end_time = self.estimate_end_time()
        secs = end_time - time.time()
        if secs <= 0:
            return _("0s")
        hours = int(secs/3600)
        secs = secs - hours*3600
        mins = int(secs/60)
        secs = secs - mins*60
        secs = int(secs/10)*10 + 10
        secs = min(secs, 59)
        message = []
        if hours:
            message.append(_("%ih") % hours)
        if mins:
            message.append(_("%imin") % mins)
        if not hours:
            if not mins or secs:
                message.append(_("%is") % secs)
        message = " ".join(message)
        return message

    def get_level(self):
        '''
        Nesting level of current task
        '''
        level = 1
        if self.parent:
            level += self.parent.get_level()
        return level

    def get_progress_info(self):
        '''
        human readable progress message
        '''
        message = ""
        message += "%i%% " % (self.get_percent_completed()*100)
        if self.get_speed():
            message += self.get_speed() + " "
        message += self.estimate_remaining_time()
        message = message.strip()
        return message

    def get_percent_of_tasks_completed(self):
        n_subtasks = self.count_subtasks()
        if n_subtasks:
            return self.count_completed_subtasks()/n_subtasks
        else:
            return 0.0

    def count_subtasks(self):
        subtasks = [s.count_subtasks() for s in self.subtasks]
        return 1.0 + sum(subtasks)

    def count_completed_subtasks(self):
        subtasks = [s.count_completed_subtasks() for s in self.subtasks]
        if self.size:
            return float(self.completed/self.size) + sum(subtasks)
        else:
            return float(self.completed) + sum(subtasks)

    def get_percent_completed(self):
        weight = self._get_weight()
        if weight:
            return self._get_completed()/weight
        else:
            return 0.0

    def _notify_listeners(self, message, task=None):
        if not task:
            task = self
        if callable(self.callback):
            self.callback(task, message=message)
        if self.parent:
            self.parent._notify_listeners(message, task)

    def _run_subtasks(self):
        for subtask in self.subtasks:
            self.current_subtask = subtask
            subtask()

    def _get_completed(self):
        '''
        get weighted sum of percent completed for this task and all the subtasks
        '''
        completed_subtasks = [s._get_completed() for s in self.subtasks]
        return float(self.completed*self.weight) + sum(completed_subtasks)

    def _get_weight(self):
        '''
        get total weight for this task and all the subtasks
        '''
        subtasks_weight = [s._get_weight() for s in self.subtasks]
        return float(self.size*self.weight) + sum(subtasks_weight)

    def _get_decription(self):
        if self._description:
            return self._description
        else:
            return self.name

    def _set_description(self, description):
        self._description = description

    description = property(_get_decription, _set_description)

class TaskList(Task):
    '''
    Root Task object which contains other tasks
    '''
    def __init__(self, name=None, description=None, tasks=None, callback=None):
        def tasklist():
            return
        Task.__init__(self, tasklist, name=name, description=description, weight=0.01)
        self.callback = callback
        if tasks:
            for task in tasks:
                task.parent = self
                self.subtasks.append(task)

class ThreadedTaskList(threading.Thread, TaskList):
    '''
    A TaskList that runs in a separate thread
    Can be started and stopped.
    Should be used as root Task object which contains other tasks.
    '''
    def __init__ (self, name=None, description=None, tasks=None, callback=None):
        threading.Thread.__init__(self)
        TaskList.__init__(self, name=name, description=description, tasks=tasks, callback = callback)
        self._stopped_event = threading.Event()
        self.setDaemon(True) #do not prevent the main application from closing

    def cancel(self):
        self._stopped_event.set()
        TaskList.cancel(self)

    def run(self):
        TaskList.__call__(self)

    def is_cancelled(self):
        return self._stopped_event.isSet() or TaskList.is_cancelled(self)

def test():
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(message)s', datefmt='%m-%d %H:%M')
    handler.setFormatter(formatter)
    handler.setLevel(logging.DEBUG)
    log.addHandler(handler)

    def fsleep():
        time.sleep(1)

    def fnested(associated_task):
        time.sleep(1)
        associated_task.add_subtask(fsleep, "fsleepsub1")
        for i in range(10):
            if associated_task.set_progress(i/10.0):
                return
            time.sleep(0.3)
        associated_task.add_subtask(fsleep, "fsleepsub2")

    def callback(task, message):
        print message, task._get_weight(), task._get_completed(), task.weight, task.size, task.completed

    tasks = [
        Task(fsleep, "fsleep1"),
        Task(fsleep, "fsleep2"),
        Task(fnested, "fcallback1"),
        Task(fnested, "fcallback2")
        ]
    tasklist = ThreadedTaskList(name="test 1", tasks=tasks, callback=callback)
    tasklist.run()

if __name__ == "__main__":
    test()
