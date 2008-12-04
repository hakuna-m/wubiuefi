import commands
from wubi.backends.common import Backend

class LinuxBackend(Backend):
    '''
    Linux-specific backend, TBD
    '''

    def get_stuff(self):
        self.info.timezone = commands.getoutput('date +%Z')
        self.info.arch = commands.getoutput('uname -m')
        self.info.username = commands.getoutput('whoami')

    def download_file(url):
        #TBD
        successful_download=subprocess.call('wget -c ' + url)
        return successful_download
