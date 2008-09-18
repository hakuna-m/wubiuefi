import os
import glob
import subprocess
import md5
cache = {}

class Blob(object):

    def __init__(self, **kargs):
        self.__dict__.update(kargs)

    def __str__(self):
        return "Blob(%s)" % str(self.__dict__)

def run_command(command):
    '''return stdout on success or raise error'''
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
    '''run command and return immediately'''
    process = subprocess.Popen(
        command, stderr=subprocess.PIPE, stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=False)
    process.communicate()

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

def get_dir_files(dir_path, depth=2):
    files = []
    if not depth:
        for dir in os.walk(dir_path):
            files += [dir[0] + f for f in dir[2]]
    else:
        dir_path = os.path.abspath(dir_path)
        for level in range(depth -1):
            dir_path = os.path.join(dir_path,'*')
            files += [f for f in glob.glob(dir_path) if os.path.isfile(f)]
    return files

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

def get_md5(str):
    m = md5.new(str)
    hash = m.hexdigest()
    return hash

def reversed(list):
    list.reverse()
    return list

if __name__ == "__main__":
    print "sleeping3"
    run_async_command(['sleep', '3'])
    f = open("/tmp/7za460.zip", 'r')
    c = f.read()
    f.close()
    print 1, run_command(['md5sum', "/tmp/7za460.zip"])
    print 2, get_md5(c)

