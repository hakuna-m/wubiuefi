import os
import subprocess

class Blob(object):

    def __init__(self, **kargs):
        self.__dict__.update(kargs)

    def __str__(self):
        return "Blob(%s)" % str(self.__dict__)

def run_command(command):
    '''return stdout on success or raise error'''
    process = subprocess.Popen(
        command, stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
    output = process.stdout.read()
    errormsg = process.stderr.read()
    retval = process.wait()
    if retval == 0:
        return output
    else:
        raise Exception(
            "Error executing command %s\n>>retval=%s\n>>stderr=%s\n>>stdout=%s"
            % (command, retval, output, errormsg))

def read_file(file_path):
    if not os.path.isfile(file_path):
        return
    f = None
    f = open(file_path, 'r')
    content = f.read()
    f.close()
    return content

def get_dir_files(dir_path):
    files = []
    for dir in os.walk(dir_path):
        files += [dir[0] + f for f in dir[2]]
    return files

def parse_metalink(metalink_file):
    metalink = load_file(url)
    f = metalink.files[0]
    print [(u.url, u.preference, u.location) for u in sorted(f.urls,key=lambda x:x.preference)]
    return metalink

def get_dir_file_names(dir_path):
    files = []
    for dir in os.walk(dir_path):
        files += [dir[0] + f for f in dir[2]]
    return files
