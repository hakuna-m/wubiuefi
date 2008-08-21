#http://linux.duke.edu/projects/urlgrabber/help/urlgrabber.grabber.html

import sys
import logging
log = logging.getLogger('downloader')

sys.path.append('/home/src/wubi/intrepid/src')
from urlgrabber.grabber import URLGrabber
from tasklist import Task

class DownloadProgress(object):
    def __init__(self, task):
        if task is None: task = Task()
        self.task = task

    def start(self, filename, url, basename, length, text):
        self.filename = filename
        self.url = url
        self.basename = basename
        self.length = length
        self.text = text
        log.debug("Download start filename=%s, url=%s, basename=%s, length=%s, text=%s")
        self.task.name = "Downloading %s from %s" % (basename, url)
        self.task.add_subtasks(length/(1024**2*10)) #lets normalize it a bit 10MB = 1 subtask

    def update(self, read):
        log.debug("download read =%s" % read)
        self.task.setpct(1.0*read/self.length)

    def end(self):
        self.task.finish()

def download(url, filename=None, task=None):
    progress_obj = DownloadProgress(task)
    urlgrabber = URLGrabber(
        reget = 'simple',
        progress_obj = progress_obj,
        )
    filename = urlgrabber.urlgrab(url, filename=filename)
    return filename
