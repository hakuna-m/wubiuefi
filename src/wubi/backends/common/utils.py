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

import sys
import os
import md5
import subprocess

def run_command(command):
    '''
    return stdout on success or raise error
    '''
    process = subprocess.Popen(
        command, stderr=subprocess.PIPE, stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=False)
    process.stdin.close()
    output = process.stdout.read()
    errormsg = process.stderr.read()
    retval = process.wait()
    if retval == 0:
        return output
    else:
        raise Exception(
            "Error executing command\n>>command=%s\n>>retval=%s\n>>stderr=%s\n>>stdout=%s"
            % (" ".join(command), retval, output, errormsg))

def run_async_command(command):
    '''
    run command and return immediately
    '''
    process = subprocess.Popen(
        command, stderr=subprocess.PIPE, stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=False)
    process.communicate()

def get_file_md5(file_path, progress_callback=None):
    file_size = os.path.getsize(file_path)
    file = open(file_path, "rb")
    md5hash = md5.new()
    data_read = 0
    for i in range(100):
        data = file.read(1024**2)
        data_read += 1024.0**2
        if data == "": break
        if callable(progress_callback):
            if progress_callback(data_read/float(file_size+1)):
                file.close()
                return
        md5hash.update(data)
    file.close()
    md5hash = md5hash.hexdigest()
    if callable(progress_callback):
        progress_callback(1)
    return md5hash

def reversed(list):
    list.reverse()
    return list

def read_file(file_path, binary=False):
    if not file_path or not os.path.isfile(file_path):
        return
    f = None
    if binary:
        f = open(file_path, 'rb')
    else:
        f = open(file_path, 'r')
    content = f.read()
    f.close()
    return content

def write_file(file_path, str):
    if not file_path:
        return
    f = None
    f = open(file_path, 'w')
    f.write(str)
    f.close()

def replace_line_in_file(file_path, old_line, new_line):
    if new_line[-1] != "\n":
        new_line += "\n"
    f = open(file_path, 'r')
    lines = f.readlines()
    f.close()
    f = open(file_path, 'w')
    for i,line in enumerate(lines):
        if line.startswith(old_line):
            lines[i] = new_line
    f.writelines(lines)
    f.close()

def find_line_in_file(file_path, line, endswith=False):
    if not file_path or not os.path.isfile(file_path):
        return
    if line[-1] != "\n":
        line += "\n"
    f = None
    f = open(file_path, 'r')
    lines = f.readlines()
    f.close()
    for line in lines:
        if (endswith and line.endswith(line)) \
        or (not endswith and line.startswith(line)):
            return line[:-1]

def unixpath(path):
    path = path.replace(r'\\', '/')
    if path[1] == ':':
        path = path[2:]
    return path
