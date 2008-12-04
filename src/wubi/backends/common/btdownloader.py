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

import bittorrent.download
from threading import Event
import logging
log = logging.getLogger('btdownloader')

stop_signal = Event()

class DownloadError(Exception):
    pass

def download(url, filename, progress_callback=None):
    params = ['--url', url, '--saveas', filename]
    cols = 80
    stop_signal = Event()

    def set_saveas(default, size, filename, dir):
        '''set final saveas'''
        return filename

    def stop_downlad():
        return stop_signal.isSet()

    def on_progress(kargs):
        percent_completed = float(kargs.get("fractionDone", 0))
        percent_completed = min(0.99, percent_completed)
        current_speed = "%sKBps" % int(kargs.get("downRate", 0)/1024.0)
        if callable(progress_callback):
            if progress_callback(percent_completed, current_speed=current_speed):
                stop_signal.set()

    def finish_callback():
        if callable(progress_callback):
            progress_callback(1)
        stop_signal.set()

    def error_callback(message):
        raise DownloadError(message)

    BitTorrent.download.download(
        params,
        set_saveas,
        on_progress,
        finish_callback,
        error_callback,
        stop_signal,
        cols=80,
        #~ pathFunc = None,
        #~ paramfunc = None,
        #~ spewflag = Event(),
        )

if __name__ == "__main__":
    url = 'http://releases.ubuntu.com/8.10/ubuntu-8.10-desktop-i386.iso.torrent'
    saveas = '/tmp/x/myfile'
    def progress_callback(percent_completed, current_speed=None):
        print "pc",percent_completed, current_speed
    download(url, saveas, progress_callback)
