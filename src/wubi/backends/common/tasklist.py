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

'''
The tasklist object keeps track of a list of tasks and reports progress
The tasklist can be run in a separate thread using ThreadedTaskList

The object observing the TaskList needs to provide a callback to its constructor
The callback will receive as an argument the tasklist object itself.

Each function registered in a TaskList can optionally support an argument called
'progress_callback', if such argument is in the function argument list,
a callback is attached to it, so that the underlying function can
use progress_callback to interact with the tasklist, usually to send notifications
about progress. If progress_callback returns True then the function
has to terminate immediately.
'''

import time
import threading
import logging

log = logging.getLogger("TaskList")

class Task(object):
    INACTIVE = 0
    ACTIVE = 1
    COMPLETED = 2
    FAILED = 3
    CANCELLED = 4

    def __init__(self, name, function, is_required, *fargs, **fkargs):
        self.name = name
        self.function = function
        self.percent_completed = 0
        self.start_time = 0
        self.end_time = 0
        self.status = Task.INACTIVE
        self.current_subtask_name = None
        self.current_speed = None
        self.tasklist = None
        self.last_error = None
        self.fargs = fargs
        self.fkargs = fkargs
        if 'progress_callback' in function.func_code.co_varnames:
            self.fkargs['progress_callback'] = self.on_progress
        self.is_required = is_required

    def on_progress(self, percent_completed, msg=None, current_speed=None, current_subtask_name=None):
        '''
        The underlying function will call this method on progress.
        Then the message is propagated to the tasklist on_progress listener
        This method will return True if the function has to cancel operation
        '''

        self.percent_completed = percent_completed
        self.current_subtask_name = current_subtask_name
        self.current_speed = current_speed
        if percent_completed >= 1:
            if msg is None:
                msg = "Finished task %s" % self.name
            self.percent_completed = 1
            self.end_time = time.time()
            self.status = Task.COMPLETED
        self.last_msg = msg
        self.tasklist.on_progress()
        return self.is_cancelled()

    def cancel(self):
        self.status = Task.CANCELLED
        return

    def is_cancelled(self):
        return self.status is Task.CANCELLED or self.tasklist.is_cancelled()

    def run(self):
        if self.is_cancelled(): return
        self.status = Task.ACTIVE
        self.start_time = time.time()
        self.on_progress(0, "Starting task %s" % self.name)
        try:
            self.function(*self.fargs, **self.fkargs)
        except Exception, err:
            self.status = Task.FAILED
            self.last_error = err
            if self.is_required:
                log.exception(err)
                raise err
            return
        self.on_progress(1)

class TaskList(Task):
    '''
    Takes care of reporting progress to the registered callback
    '''
    def __init__(self, name, tasks=None, progress_callback=None):
        self.name = name
        self.current_task = None
        self.start_time = 0
        self.end_time = 0
        self.tasks = []
        self._is_cancelled = False
        self.progress_callback = progress_callback
        if not tasks:
            tasks = []
        for task in tasks:
            if isinstance(task, Task):
                task.tasklist = self
                self.tasks.append(task)
            elif len(task) == 2:
                self.add_task(task[0], task[1], is_required=True, *task[2:])
            else:
                self.add_task(*task)

    def add_task(self, name, function, is_required, *fargs, **fkargs):
        task = Task(name, function, is_required, *fargs, **fkargs)
        task.tasklist = self
        self.tasks.append(task)

    def run(self):
        self.start_time = time.time()
        for task in self.tasks:
            if self.is_cancelled(): return
            self.current_task = task
            task.run()
        self.end_time = time.time()

    def on_progress(self):
        if self.is_cancelled():
            return
        if callable(self.progress_callback):
            return self.progress_callback(self)

    def cancel(self):
        self._is_cancelled = True

    def is_cancelled(self):
        return self._is_cancelled

    def tasks_completed(self):
        ntasks = len(self.tasks)
        current_task_n = self.tasks.index(self.current_task)
        return float(current_task_n + self.current_task.percent_completed)/ntasks

    def estimated_end_time(self):
        if self.tasks_completed():
            ntasks = float(len(self.tasks))
            ncompleted = self.tasks_completed()*ntasks
            return time.time()+(time.time() - self.start_time)/ncompleted*(ntasks-ncompleted)
        else:
            return time.time() + len(self.tasks)

class ThreadedTaskList(threading.Thread, TaskList):
    '''
    A tasklist that runs in a separate thread
    Can be started and stopped
    '''
    def __init__ (self, name, tasks=None, progress_callback=None):
        threading.Thread.__init__(self)
        TaskList.__init__(self, name, tasks, progress_callback = progress_callback)
        self._stopped_event = threading.Event()
        self.setDaemon(True) #do not prevent the main application from closing

    def cancel(self):
        self._stopped_event.set()

    def run(self):
        return TaskList.run(self)

    def is_cancelled(self):
        return self._is_cancelled or self._stopped_event.isSet()

if __name__ == "__main__":

    def fsleep():
        time.sleep(1)

    def fcallback(progress_callback=None):
        time.sleep(1)
        if progress_callback(.3): return
        time.sleep(1)
        if progress_callback(.6): return
        time.sleep(1)

    def progress_callback(tasklist):
        print "===prog==="
        print tasklist.current_task.last_msg
        print "%s%% finished" % (tasklist.tasks_completed()*100)
        print "remaining secs:", int(tasklist.estimated_end_time()- time.time())
        print "current task completed: %s%%" % (tasklist.current_task.percent_completed*100)

    tasklist = ThreadedTaskList("test 1", progress_callback=progress_callback)
    tasklist.add_task("fsleep1", fsleep, True)
    tasklist.add_task("fsleep2", fsleep, True)
    tasklist.add_task("fcallback1", fcallback, True)
    tasklist.add_task("fcallback2", fcallback, True)
    tasklist.run()
