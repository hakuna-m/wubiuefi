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
import shutil

def join_path(*args):
    if args and args[0][-1] == ":":
        args = list(args)
        args[0] = args[0] + os.path.sep
    return os.path.abspath(os.path.join(*args))

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

def get_file_md5(file_path, associated_task=None):
    file_size = os.path.getsize(file_path)/(1024**2)
    if associated_task:
        associated_task.unit = "MB"
        associated_task.size = file_size
    file = open(file_path, "rb")
    md5hash = md5.new()
    data_read = 0
    for i in range(file_size + 1):
        data = file.read(1024**2)
        data_read += 1
        if data == "":
            break
        if associated_task:
            if associated_task.set_progress(data_read):
                file.close()
                return
        md5hash.update(data)
    file.close()
    md5hash = md5hash.hexdigest()
    if associated_task:
        associated_task.finish()
    return md5hash

def copy_file(source, target, associated_task=None):
    '''
    Copy file with progress report
    '''
    file_size = os.path.getsize(source)
    if associated_task:
        associated_task.size = file_size/1024**2
        associated_task.unit = "MB"
    source_file = open(source, "rb")
    target_file = open(target, "wb")
    data_read = 0
    while True:
        data = source_file.read(1024**2)
        data_read += 1
        if not data:
            break
        if associated_task:
            if associated_task.set_progress(data_read):
                source_file.close()
                target_file.close()
                return
        target_file.write(data)
        if data_read >= file_size:
            break
    source_file.close()
    target_file.close()
    if associated_task:
        associated_task.finish()

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

def remove_line_in_file(file_path, rm_line):
    f = open(file_path, 'r')
    lines = f.readlines()
    f.close()
    f = open(file_path, 'w')
    for i,line in enumerate(lines):
        if line.startswith(rm_line):
            lines[i] = ""
    f.writelines(lines)
    f.close()

def find_line_in_file(file_path, text, endswith=False):
    if not file_path or not os.path.isfile(file_path):
        return
    if endswith and text[-1] != "\n":
        text += "\n"
    f = open(file_path, 'r')
    lines = f.readlines()
    f.close()
    for line in lines:
        if (endswith and line.endswith(text)) \
        or (not endswith and line.startswith(text)):
            return line[:-1]

def unixpath(path):
    path = path.replace(r'\\', '/')
    if path[1] == ':':
        path = path[2:]
    return path

def copytree(source, dest):
    '''
    Copies a tree, replacing any pre-existing destination file/directory
    '''
    if os.path.exists(dest):
        if os.path.isfile(dest):
            os.unlink(dest)
        elif os.path.isdir(dest):
            shutil.rmtree(dest)
    shutil.copytree(source, dest)
