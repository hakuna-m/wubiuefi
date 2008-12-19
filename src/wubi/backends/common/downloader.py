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
Wrapper around urlgrabber adding support for backend progress callbacks
http://linux.duke.edu/projects/urlgrabber/help/urlgrabber.grabber.html
'''

import os
import sys
import logging
log = logging.getLogger('downloader')

from urlgrabber.grabber import URLGrabber
import encodings.idna #required by urlgrabber
import encodings.ascii #required by urlgrabber
import encodings.utf_8 #required by urlgrabber

class DownloadProgress(object):
    def __init__(self, associated_task):
        self.associated_task = associated_task

    def start(self, filename, url, basename, length, text):
        self.filename = filename
        self.url = url
        self.basename = basename
        self.length = length
        self.text = text
        log.debug("Download start filename=%s, url=%s, basename=%s, length=%s, text=%s" %
            (filename, url, basename, length, text))
        if callable(self.associated_task):
            self.associated_task.set_progress(0, "Downloading %s from %s" % (basename, url))

    def update(self, amount_read):
        progress = 1.0*amount_read/float(self.length+1)
        if callable(self.associated_task):
            if self.associated_task.set_progress(progress):
                return True #TBD cancel download

    def end(self, amount_read):
        log.debug("download finished (read %s bytes)" % amount_read)
        if callable(self.associated_task):
            self.associated_task.set_progress(1)

def download(url, filename=None, associated_task=None, web_proxy = None):
    log.debug("downloading %s > %s" % (url, filename))
    progress_obj = DownloadProgress(associated_task)
    if web_proxy:
        web_proxy={'http':web_proxy}
    urlgrabber = URLGrabber(
        reget = 'simple',
        proxies = web_proxy,
        progress_obj = progress_obj)
    if os.path.isdir(filename):
        basename = os.path.basename(url)
        filename = os.path.join(filename, basename)
    filename = urlgrabber.urlgrab(url, filename=filename)
    return filename

