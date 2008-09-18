'''
Wrapper around urlgrabber adding support for backend progress callbacks
http://linux.duke.edu/projects/urlgrabber/help/urlgrabber.grabber.html
'''

import os
import sys
import logging
log = logging.getLogger('downloader')

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
        log.debug("Download start filename=%s, url=%s, basename=%s, length=%s, text=%s" %
            (filename, url, basename, length, text))
        self.task.name = "Downloading %s from %s" % (basename, url)
        self.task.add_subtasks(int(length/(1024**2*10))) #lets normalize it a bit 10MB = 1 subtask

    def update(self, amount_read):
        log.debug("download read =%s" % amount_read)
        self.task.setpct(1.0*amount_read/self.length)

    def end(self, amount_read):
        log.debug("download read =%s" % amount_read)
        self.task.finish()

def download(url, filename=None, task=None):
    log.debug("download(%s, %s)" % (url, filename))
    progress_obj = DownloadProgress(task)
    urlgrabber = URLGrabber(
        reget = 'simple',
        progress_obj = progress_obj)
    if os.path.isdir(filename):
        basename = os.path.basename(url)
        filename = os.path.join(filename, basename)
    filename = urlgrabber.urlgrab(url, filename=filename)
    return filename

