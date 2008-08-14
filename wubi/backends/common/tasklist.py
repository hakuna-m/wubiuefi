import time
import threading
import logging

log = logging.getLogger("TaskList")


class Task(object):
    '''
    Allows (nested) tasks to be run in succession and keeps track of total progress and partial progress
    Handy for progress reporting. Subtasks can be added at runtime and the progress will reflect that
    A real task is associated to a function, the function must take as only argument the task
    The function must return True if the tasklist has to be updated and the next task has to be run (automatic step)
    If it returns False, the function must call task.finish() or task.step() within its body.
    Dummy subtasks are also allowed, those are not associated to a real function
    and are used for a more in-depth progress reporting. Manual stepping is required in this case.
    '''

    INACTIVE = 0
    ACTIVE = 1
    COMPLETED = 2
    FAILED = 3
    CANCELLED = 4

    def __init__(self, name, function=None, subtasks=None, parent=None, on_change=None, is_stopped=None, is_required=True):
        if callable(function) and 'task' not in function.func_code.co_varnames:
            function = wrap_function(function)
        self.name = name
        self.function = function
        self.is_required = True
        self.parent = parent
        self.status = Task.INACTIVE
        self.n_current_subtask = 0
        self.start_time = 0
        self.end_time = 0
        self.on_change = on_change
        self.children = []
        self._is_stopped = is_stopped
        self.subtasks = []
        self.add_subtasks(subtasks and subtasks or [])

    @property
    def run_time(self):
        if not self.status: return 0
        if not self.subtasks:
            if self.end_time: return self.end_time
            return time.time() - self.start_time
        else:
            return sum(subtask.run_time for subtask in self.subtasks if subtask.status)

    @property
    def estimated_end_time(self):
        if not self.n_current_step: return
        self.start_time + 1.0*self.run_time*self.n_current_subtask/self.n_total_subtasks

    @property
    def n_subtasks(self):
        return len(self.subtasks)

    @property
    def n_total_subtasks(self):
        if not self.subtasks: return 1 #1 = self
        return sum(subtask.n_total_subtasks for subtask in self.subtasks)

    @property
    def n_completed_subtasks(self):
        if not self.status: return 0
        if self.subtasks:
            return sum(1 for subtask in self.subtasks if subtask.status is Task.COMPLETED)
        else:
            if self.status is Task.COMPLETED:
                return 1 #1 = self
            else:
                return 0

    @property
    def n_completed_total_subtasks(self):
        if not self.status: return 0
        if self.subtasks:
            return sum(subtask.n_completed_total_subtasks for subtask in self.subtasks if subtask.status)
        else:
            if self.status is Task.COMPLETED:
                return 1 #1 = self
            else:
                return 0

    @property
    def task_progress(self):
        return 1.0*self.n_completed_subtasks/self.n_subtasks

    @property
    def total_progress(self):
        return 1.0*self.n_completed_total_subtasks/self.n_total_subtasks

    @property
    def current_subtask(self):
        if not self.subtasks: return
        if self.n_current_subtask >= len(self.subtasks): return
        return self.subtasks[self.n_current_subtask]

    @property
    def current_subtask_name(self):
        current_subtask = self.current_subtask
        if current_subtask: return current_subtask.name
        return None

    @property
    def is_finished(self):
        return self.status in (Task.COMPLETED,)

    def add_subtasks(self, subtasks):
        if self.is_stopped(): return
        if isinstance(subtasks, int):
            subtasks = [str(i) for i in range(subtasks)]
        elif isinstance(subtasks, basestring):
            subtasks = [subtasks]
        for subtask in subtasks:
            if isinstance(subtask, dict):
                self.add_subtask(**subtask)
            elif isinstance(subtask, basestring):
                self.add_subtask(subtask)
            else:
                self.add_subtask(*subtask)

    def add_subtask(self, name, function=None, subtasks=None):
        if self.is_stopped(): return
        subtask = Task(name, parent=self, subtasks=subtasks, function=function, on_change=self.on_change)
        self.subtasks.append(subtask)
        self.on_change()
        return subtask

    def setpct(self, percentage):
        '''
        Set the current task as a percentage where 1 is the last task
        '''
        self.n_current_subtask = int(round(self.n_subtasks * percentage))
        if self.n_current_subtask >= self.n_subtasks:
            self.finish()
        else:
            self.current_subtask.run()

    def step(self):
        if self.is_stopped(): return
        if self.current_subtask and self.current_subtask.status is Task.INACTIVE:
            if not self.current_subtask.function:
                self.current_subtask.finish()
            else:
                # TBD what do we do in such situation ????
                log.exception((self.name, "step > old subtask is real but inactive >", self.current_subtask.name))
        elif self.current_subtask and self.current_subtask.status is Task.ACTIVE:
            self.current_subtask.finish()
        elif self.current_subtask and self.current_subtask.status is Task.FAILED:
            # TBD what do we do in such situation ????
            log.exception((self.name, "step > old subtask is FAILED >", self.current_subtask.name))
        else:
            self.n_current_subtask += 1
            if self.n_current_subtask >= self.n_subtasks:
                self.finish()
            else:
                self.current_subtask.run()

    def run(self):
        if self.is_stopped(): return
        self.start_time = time.time()
        self.status = Task.ACTIVE
        log.debug((self.name, "> run"))
        self.on_change()
        if callable(self.function):
            log.debug((self.name, "> run > function >", self.function))
            if self.function(self):
                self.step()
        if self.current_subtask and self.current_subtask.status is Task.INACTIVE:
            self.current_subtask.run()

    def finish(self):
        if self.is_stopped(): return
        self.status = Task.COMPLETED
        self.end_time = time.time()
        log.debug((self.name, "> finish"))
        self.on_change()
        if self.parent:
            self.parent.step()

    def fail(self):
        if self.is_stopped(): return
        self.status = Task.FAILED
        self.end_time = time.time()
        log.exception((self.name, "> fail"))
        self.on_change()
        if self.parent:
            self.parent.step()

    def cancel(self):
        if self.is_stopped(): return
        self.status = Task.CANCELLED
        self.end_time = time.time()
        log.info((self.name, "> cancel"))
        self.on_change()
        if self.parent:
            self.parent.step()

    def is_stopped(self):
        if self._is_stopped is None:
            if self.parent:
                is_stopped = self.parent._is_stopped
            else:
                return
        else:
            is_stopped = self._is_stopped
        if callable(is_stopped): return is_stopped()
        return is_stopped

class TaskList(Task):
    '''
    Root object
    Takes care of reporting progress to the registered callback
    '''
    def __init__(self, name, tasks=None,  on_progress_callback=None):
        self.on_progress_callback = on_progress_callback
        Task.__init__(self, name, parent=None, subtasks=tasks, function=None, on_change = self.on_change)

    def on_change(self):
        if self.is_stopped(): return
        if callable(self.on_progress_callback):
            return self.on_progress_callback(self)

class ThreadedTaskList(threading.Thread, TaskList):
    '''
    A tasklist that runs in a separate thread
    Can be started and stopped
    '''
    def __init__ (self, name, tasks=None,  on_progress_callback=None):
        TaskList.__init__(self, name, tasks, on_progress_callback)
        threading.Thread.__init__(self)
        self._is_stopped_event = threading.Event()
        self._is_stopped = self._is_stopped_event.isSet

    def stop (self):
        self._is_stopped_event.set()
        self.join()

    def run(self):
        TaskList.run(self)

def wrap_function(function):
    def wrapped_function(task):
        result = function()
        return True
    return wrapped_function

if __name__ == "__main__":
    logging.basicConfig()
    log.setLevel(logging.DEBUG)

    def on_progress_callback(task):
        pstr = ":: task=%s subtask=%s %s%% (%s/%s) finished=%s" % (
            task.name,
            task.current_subtask_name,
            100*task.total_progress,
            task.n_completed_total_subtasks ,
            task.n_total_subtasks,
            task.is_finished,)
        print pstr

    def task_auto_step(task):
        '''
        This function returns True
        which is equivalent to call finish at the end,
        '''
        time.sleep(1)
        return True #this will trigger auto step

    def task_manual_finish(task):
        '''
        This function calls finish at the end,
        '''
        time.sleep(1)
        task.finish() #explicit finish

    def task_manual_step(task):
        '''
        This function calls step at the end,
        since the task only has 1 subtask
        step is equivalent to finish
        '''
        time.sleep(1)
        task.step() #explicit step

    def task_dynamic_subtasks(task):
        '''
        test adding real subtasks dynamically
        '''
        subtasks = [
            ("st1", task_auto_step),
            ("st2", task_manual_finish),
            ("st3", task_manual_step),
        ]
        task.add_subtasks(subtasks)

    def task_dynamic_dummy_subtasks(task):
        '''
        test adding dummy subtasks dynamically
        dummy subtasks have no function attached
        and are used for a more in depth progress reporting
        manual stepping is required
        '''
        subtasks = ("s1","s2","s3")
        task.add_subtasks(subtasks)
        for st in subtasks:
            time.sleep(1)
            print "task_dynamic_dummy_subtasks > step > ", st
            task.step()

    def task_simple_function():
        '''
        This function will be wrapped automatically
        since it does not take 'task' as argument
        '''
        time.sleep(1)


    def build_task_list():
        tasks = [
            ("t0", task_simple_function),
            ("t1", task_dynamic_subtasks),
            ("t2", task_auto_step),
            ("t3", task_manual_finish),
            ("t4", task_manual_step),
            ("t5", task_dynamic_dummy_subtasks),
        ]
        tasklist = ThreadedTaskList('tasklist', tasks, on_progress_callback)
        return tasklist

    tasklist = build_task_list()
    tasklist.start()
    print "******* starting tasklist ******"
    ## uncomment the following to test stopping the tasklist thread
    # time.sleep(5)
    # print "******* stopping tasklist *******"
    # tasklist.stop()

