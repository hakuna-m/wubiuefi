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
import sys
import random
import ctypes
import logging

log = logging.getLogger("CommonBackendUtils")

def join_path(*args):
    if args and args[0] and args[0][-1] == ":":
        args = list(args)
        args[0] = args[0] + os.path.sep
    return os.path.abspath(os.path.join(*args))

def run_command(command, show_window=False):
    '''
    return stdout on success or raise error
    '''
    STARTF_USESHOWWINDOW = 1
    SW_HIDE = 0
    if show_window:
        startupinfo = None
    else:
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = SW_HIDE
    process = subprocess.Popen(
        command,
        stderr=subprocess.PIPE, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
        startupinfo=startupinfo,
        shell=False)
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

def run_nonblocking_command(command, show_window=False):
    '''
    run command and return immediately
    '''
    STARTF_USESHOWWINDOW = 1
    SW_HIDE = 0
    if show_window:
        startupinfo = None
    else:
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = SW_HIDE
    process = subprocess.Popen(
        command,
        startupinfo=startupinfo)
    return process.pid

def md5_password(password):
    # From http://mail.python.org/pipermail/python-list/2003-March/195202.html
    salt_chars = './abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    salt = ''.join([random.choice(salt_chars) for i in range(5)])

    hash = md5.new()
    hash.update(password)
    hash.update('$1$')
    hash.update(salt)

    second_hash = md5.new()
    second_hash.update(password)
    second_hash.update(salt)
    second_hash.update(password)
    second_hash = second_hash.digest()
    q, r = divmod(len(password), len(second_hash))
    second_hash = second_hash*q + second_hash[:r]
    assert len(second_hash) == len(password)
    hash.update(second_hash)
    del second_hash, q, r

    i = len(password)
    while i > 0:
        if i & 1:
            hash.update('\0')
        else:
            hash.update(password[0])
        i >>= 1

    hash = hash.digest()

    for i in xrange(1000):
        nth_hash = md5.new()
        if i % 2:
            nth_hash.update(password)
        else:
            nth_hash.update(hash)
        if i % 3:
            nth_hash.update(salt)
        if i % 7:
            nth_hash.update(password)
        if i % 2:
            nth_hash.update(hash)
        else:
            nth_hash.update(password)
        hash = nth_hash.digest()

    # a different base64 than the MIME one
    base64 = './0123456789' \
        'ABCDEFGHIJKLMNOPQRSTUVWXYZ' \
        'abcdefghijklmnopqrstuvwxyz'
    def b64_three_char(char2, char1, char0, n):
        byte2, byte1, byte0 = map(ord, [char2, char1, char0])
        w = (byte2 << 16) | (byte1 << 8) | byte0
        s = []
        for _ in range(n):
            s.append(base64[w & 0x3f])
            w >>= 6
        return s

    result = ['$1$', salt, '$']
    result.extend(b64_three_char(hash[0], hash[6], hash[12], 4))
    result.extend(b64_three_char(hash[1], hash[7], hash[13], 4))
    result.extend(b64_three_char(hash[2], hash[8], hash[14], 4))
    result.extend(b64_three_char(hash[3], hash[9], hash[15], 4))
    result.extend(b64_three_char(hash[4], hash[10], hash[5], 4))
    result.extend(b64_three_char('\0', '\0', hash[11], 2))

    return ''.join(result)

def get_file_md5(file_path, associated_task=None):
    if not file_path or not os.path.isfile(file_path):
        return
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

def get_drive_space(drive_path):
    #Windows only
    freeuser = ctypes.c_int64()
    total = ctypes.c_int64()
    free = ctypes.c_int64()
    ctypes.windll.kernel32.GetDiskFreeSpaceExW(
            unicode(drive_path),
            ctypes.byref(freeuser),
            ctypes.byref(total),
            ctypes.byref(free))
    return total.value

def copy_file(source, target, associated_task=None):
    '''
    Copy file with progress report
    '''
    if os.path.isfile(source):
        file_size = os.path.getsize(source)
    elif os.path.ismount(source):
        if sys.platform.startswith("win"):
            file_size = get_drive_space(source)
            source = "\\\\.\\%s" % source[:2]
    if associated_task:
        associated_task.size = file_size/1024**2
        associated_task.unit = "MB"
    source_file = open(source, "rb")
    target_file = open(target, "wb")
    data_read = 0
    while True:
        data = source_file.read(1024**2)
        data_read += 1
        if data == "":
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
    try:
        f.writelines(lines)
    except Exception, err:
        log.exception(err)
    f.close()

def remove_line_in_file(file_path, rm_line, ignore_case=False):
    f = open(file_path, 'r')
    lines = f.readlines()
    f.close()
    f = open(file_path, 'w')
    if ignore_case:
        rm_line = rm_line.lower()
    for i,line in enumerate(lines):
        if ignore_case:
            line = line.lower()
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

def unix_path(path):
    #TBD not a proper conversion but will do for now
    path = path.replace('\\', '/')
    if len(path)>1 and path[1] == ':':
        path = path[2:]
    if len(path)>1 and path[-1] == '/':
        path = path[:-1]
    return path

def rm_tree(target):
    if not os.path.exists(target):
        return
    if os.path.isfile(target):
            os.unlink(target)
    elif not os.path.isdir(target):
        return
    if sys.platform.startswith("win"):
        for dir, subdirs, files in os.walk(target):
            if not files:
                continue
            for file in files:
                file = join_path(dir, file)
                run_command(['attrib', '-R', '-S', '-H', file])
    shutil.rmtree(target)
