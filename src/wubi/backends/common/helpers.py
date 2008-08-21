import os
import glob
import subprocess

class Blob(object):

    def __init__(self, **kargs):
        self.__dict__.update(kargs)

    def __str__(self):
        return "Blob(%s)" % str(self.__dict__)

def run_command(command):
    '''return stdout on success or raise error'''
    process = subprocess.Popen(
        command, stderr=subprocess.PIPE, stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
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

def read_file(file_path):
    if not file_path or not os.path.isfile(file_path):
        return
    f = None
    f = open(file_path, 'r')
    content = f.read()
    f.close()
    return content

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

def get_dir_file_names(dir_path):
    files = []
    for dir in os.walk(dir_path):
        files += [dir[0] + f for f in dir[2]]
    return files
