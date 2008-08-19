print "test"

from BitTornado.download_bt1 import BT1Download, defaults, parse_params, get_usage, get_response
from BitTornado.RawServer import RawServer, UPnP_ERROR
from random import seed
from socket import error as socketerror
from BitTornado.bencode import bencode
from BitTornado.natpunch import UPnP_test
from threading import Event
from os.path import abspath
from signal import signal, SIGWINCH
from sha import sha
from sys import argv, exit
import sys
from time import time, strftime
from BitTornado.clock import clock
from BitTornado import createPeerID, version
from BitTornado.ConfigDir import ConfigDir

def fmttime(n):
    if n == 0:
        return 'download complete!'
    try:
        n = int(n)
        assert n >= 0 and n < 5184000  # 60 days
    except:
        return '<unknown>'
    m, s = divmod(n, 60)
    h, m = divmod(m, 60)
    return 'finishing in %d:%02d:%02d' % (h, m, s)


def status(dpflag=Event(), fractionDone=None, timeEst=None, downRate=None, upRate=None, activity=None, statistics=None, spew=None, **kws):
    if downRate is not None:
        downRate = '%.1f KB/s' % (float(downRate) / (1 << 10))
    if upRate is not None:
        upRate = '%.1f KB/s' % (float(upRate) / (1 << 10))
    print "%%: %s | down: %s | up: %s | %s | status: %s" % (fractionDone, downRate, upRate, fmttime(timeEst), activity)
    dpflag.set()

def finished(*kws):
    print "Finished"
    print kws

def error(*kws):
    print "Error"
    print kws

def failed(*kws):
    print "Failed"
    print kws

def getFileName(default, size, saveas, directory):
    if saveas == '':
        saveas = default
    return saveas

def run(params):
    doneflag = Event()
    try:
        while 1:
            configdir = ConfigDir('downloadcurses')
            defaultsToIgnore = ['responsefile', 'url', 'priority']
            configdir.setDefaults(defaults,defaultsToIgnore)
            configdefaults = configdir.loadConfig()
            defaults.append(('save_options',0,
             "whether to save the current options as the new default configuration " +
             "(only for btdownloadcurses.py)"))
            try:
                config = parse_params(params, configdefaults)
            except ValueError, e:
                error('error: ' + str(e) + '\nrun with no args for parameter explanations')
                break
            if not config:
                error(get_usage(defaults, fieldw, configdefaults))
                break
            if config['save_options']:
                configdir.saveConfig(config)
            configdir.deleteOldCacheData(config['expire_cache_data'])

            myid = createPeerID()
            seed(myid)

            rawserver = RawServer(doneflag, config['timeout_check_interval'],
                                  config['timeout'], ipv6_enable = config['ipv6_enabled'],
                                  failfunc = failed, errorfunc = error)

            upnp_type = UPnP_test(config['upnp_nat_access'])
            while True:
                try:
                    listen_port = rawserver.find_and_bind(config['minport'], config['maxport'],
                                    config['bind'], ipv6_socket_style = config['ipv6_binds_v4'],
                                    upnp = upnp_type, randomizer = config['random_port'])
                    break
                except socketerror, e:
                    if upnp_type and e == UPnP_ERROR:
                        error('WARNING: COULD NOT FORWARD VIA UPnP')
                        upnp_type = 0
                        continue
                    error("Couldn't listen - " + str(e))
                    failed()
                    return

            response = get_response(config['responsefile'], config['url'], error)
            if not response:
                break

            infohash = sha(bencode(response['info'])).digest()

            dow = BT1Download(status, finished, error, error, doneflag,
                            config, response, infohash, myid, rawserver, listen_port,
                            configdir)

            if not dow.saveAs(getFileName):
                break

            if not dow.initFiles(old_style = True):
                break
            if not dow.startEngine():
                dow.shutdown()
                break
            dow.startRerequester()
            print "lol"
            dow.autoStats(status)
            print "yeah"
            if not dow.am_I_finished():
                status(activity = 'connecting to peers')
            rawserver.listen_forever(dow.getPortHandler())
            status(activity = 'shutting down')
            dow.shutdown()
            break

    except KeyboardInterrupt:
        # ^C to exit..
        pass
    try:
        rawserver.shutdown()
    except:
        pass
    if not done:
        failed()

def run2(url):
    from BitTornado.download_bt1 import download
    download([url], getFileName, status, finished, error, Event(), failed)

url="http://releases.ubuntu.com/8.04.1/ubuntu-8.04.1-alternate-amd64.iso.torrent"
run([url])
#run2(url)
