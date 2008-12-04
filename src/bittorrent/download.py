# Written by Bram Cohen
# see LICENSE.txt for license information

from zurllib import urlopen
from urlparse import urljoin
from btformats import check_message
from Choker import Choker
from Storage import Storage
from StorageWrapper import StorageWrapper
from Uploader import Upload
from Downloader import Downloader
from Connecter import Connecter
from Encrypter import Encoder
from RawServer import RawServer
from Rerequester import Rerequester
from DownloaderFeedback import DownloaderFeedback
from RateMeasure import RateMeasure
from CurrentRateMeasure import Measure
from PiecePicker import PiecePicker
from bencode import bencode, bdecode
from __init__ import version
from binascii import b2a_hex
from sha import sha
from os import path, makedirs
from parseargs import parseargs, formatDefinitions
from socket import error as socketerror
from random import seed
from threading import Thread, Event
from time import time
try:
    from os import getpid
except ImportError:
    def getpid():
        return 1

defaults = [
    ('max_uploads', 7,
        "the maximum number of uploads to allow at once."),
    ('keepalive_interval', 120.0,
        'number of seconds to pause between sending keepalives'),
    ('download_slice_size', 2 ** 14,
        "How many bytes to query for per request."),
    ('request_backlog', 5,
        "how many requests to keep in a single pipe at once."),
    ('max_message_length', 2 ** 23,
        "maximum length prefix encoding you'll accept over the wire - larger values get the connection dropped."),
    ('ip', '',
        "ip to report you have to the tracker."),
    ('minport', 6881, 'minimum port to listen on, counts up if unavailable'),
    ('maxport', 6999, 'maximum port to listen on'),
    ('responsefile', '',
        'file the server response was stored in, alternative to url'),
    ('url', '',
        'url to get file from, alternative to responsefile'),
    ('saveas', '',
        'local file name to save the file as, null indicates query user'),
    ('timeout', 300.0,
        'time to wait between closing sockets which nothing has been received on'),
    ('timeout_check_interval', 60.0,
        'time to wait between checking if any connections have timed out'),
    ('max_slice_length', 2 ** 17,
        "maximum length slice to send to peers, larger requests are ignored"),
    ('max_rate_period', 20.0,
        "maximum amount of time to guess the current rate estimate represents"),
    ('bind', '', 
        'ip to bind to locally'),
    ('upload_rate_fudge', 5.0, 
        'time equivalent of writing to kernel-level TCP buffer, for rate adjustment'),
    ('display_interval', .5,
        'time between updates of displayed information'),
    ('rerequest_interval', 5 * 60,
        'time to wait between requesting more peers'),
    ('min_peers', 20, 
        'minimum number of peers to not do rerequesting'),
    ('http_timeout', 60, 
        'number of seconds to wait before assuming that an http connection has timed out'),
    ('max_initiate', 35,
        'number of peers at which to stop initiating new connections'),
    ('max_allow_in', 55,
        'maximum number of connections to allow, after this new incoming connections will be immediately closed'),
    ('check_hashes', 1,
        'whether to check hashes on disk'),
    ('max_upload_rate', 0,
        'maximum kB/s to upload at, 0 means no limit'),
    ('snub_time', 30.0,
        "seconds to wait for data to come in over a connection before assuming it's semi-permanently choked"),
    ('spew', 0,
        "whether to display diagnostic info to stdout"),
    ('rarest_first_cutoff', 4,
        "number of downloads at which to switch from random to rarest first"),
    ('min_uploads', 4,
        "the number of uploads to fill out to with extra optimistic unchokes"),
    ('report_hash_failures', 0,
        "whether to inform the user that hash failures occur. They're non-fatal."),
    ]

def download(params, filefunc, statusfunc, finfunc, errorfunc, doneflag, cols, pathFunc = None, paramfunc = None, spewflag = Event()):
    if len(params) == 0:
        errorfunc('arguments are -\n' + formatDefinitions(defaults, cols))
        return
    try:
        config, args = parseargs(params, defaults, 0, 1)
        if args:
            if config.get('responsefile', None) == None:
                raise ValueError, 'must have responsefile as arg or parameter, not both'
            if path.isfile(args[0]):
                config['responsefile'] = args[0]
            else: 
                config['url'] = args[0]
        if (config['responsefile'] == '') == (config['url'] == ''):
            raise ValueError, 'need responsefile or url'
    except ValueError, e:
        errorfunc('error: ' + str(e) + '\nrun with no args for parameter explanations')
        return
    
    try:
        if config['responsefile'] != '':
            h = open(config['responsefile'], 'rb')
        else:
            h = urlopen(config['url'])
        response = h.read()
        h.close()
    except IOError, e:
        if config['responsefile'] != '' and config['responsefile'].find('Temporary Internet Files') != -1:
            errorfunc('BitTorrent was passed a filename that doesn\'t exist.  ' +
                'Either clear your Temporary Internet Files or right-click the link ' + 
                'and save the .torrent to disk first.')
        else:
            errorfunc('problem getting response info - ' + str(e))
        return

    try:
        response = bdecode(response)
        check_message(response)
    except ValueError, e:
        errorfunc("got bad file info - " + str(e))
        return
    
    try:
        def make(f, forcedir = False):
            if not forcedir:
                f = path.split(f)[0]
            if f != '' and not path.exists(f):
                makedirs(f)
                
        info = response['info']
        if info.has_key('length'):
            file_length = info['length']
            file = filefunc(info['name'], file_length, config['saveas'], False)
            if file is None:
                return
            make(file)
            files = [(file, file_length)]
        else:
            file_length = 0
            for x in info['files']:
                file_length += x['length']
            file = filefunc(info['name'], file_length, config['saveas'], True)
            if file is None:
                return
  
            # if this path exists, and no files from the info dict exist, we assume it's a new download and 
            # the user wants to create a new directory with the default name
            existing = 0
            if path.exists(file):
                for x in info['files']:
                    if path.exists(path.join(file, x['path'][0])):
                        existing = 1
                if not existing:
                    file = path.join(file, info['name'])
                    
            make(file, True)
            
            # alert the UI to any possible change in path
            if pathFunc != None:
                pathFunc(file)
                
            files = []
            for x in info['files']:
                n = file
                for i in x['path']:
                    n = path.join(n, i)
                files.append((n, x['length']))
                make(n)
    except OSError, e:
        errorfunc("Couldn't allocate dir - " + str(e))
        return
    
    finflag = Event()
    ann = [None]
    myid = 'M' + version.replace('.', '-')
    myid = myid + ('-' * (8 - len(myid))) + b2a_hex(sha(repr(time()) + ' ' + str(getpid())).digest()[-6:])
    seed(myid)
    pieces = [info['pieces'][x:x+20] for x in xrange(0, 
        len(info['pieces']), 20)]
    def failed(reason, errorfunc = errorfunc, doneflag = doneflag):
        doneflag.set()
        if reason is not None:
            errorfunc(reason)
    rawserver = RawServer(doneflag, config['timeout_check_interval'], config['timeout'], errorfunc = errorfunc, maxconnects = config['max_allow_in'])
    try:
        try:
            storage = Storage(files, open, path.exists, path.getsize)
        except IOError, e:
            errorfunc('trouble accessing files - ' + str(e))
            return
        def finished(finfunc = finfunc, finflag = finflag, 
                ann = ann, storage = storage, errorfunc = errorfunc):
            finflag.set()
            try:
                storage.set_readonly()
            except (IOError, OSError), e:
                errorfunc('trouble setting readonly at end - ' + str(e))
            if ann[0] is not None:
                ann[0](1)
            finfunc()
        rm = [None]
        def data_flunked(amount, rm = rm, errorfunc = errorfunc, report_hash_failures = config['report_hash_failures']):
            if rm[0] is not None:
                rm[0](amount)
            if report_hash_failures:
                errorfunc('a piece failed hash check, re-downloading it')
        storagewrapper = StorageWrapper(storage, 
            config['download_slice_size'], pieces, 
            info['piece length'], finished, failed, 
            statusfunc, doneflag, config['check_hashes'], data_flunked)
    except ValueError, e:
        failed('bad data - ' + str(e))
    except IOError, e:
        failed('IOError - ' + str(e))
    if doneflag.isSet():
        return

    e = 'maxport less than minport - no ports to check'
    for listen_port in xrange(config['minport'], config['maxport'] + 1):
        try:
            rawserver.bind(listen_port, config['bind'])
            break
        except socketerror, e:
            pass
    else:
        errorfunc("Couldn't listen - " + str(e))
        return

    choker = Choker(config['max_uploads'], rawserver.add_task, finflag.isSet, 
        config['min_uploads'])
    upmeasure = Measure(config['max_rate_period'], 
        config['upload_rate_fudge'])
    downmeasure = Measure(config['max_rate_period'])
    def make_upload(connection, choker = choker, 
            storagewrapper = storagewrapper, 
            max_slice_length = config['max_slice_length'],
            max_rate_period = config['max_rate_period'],
            fudge = config['upload_rate_fudge']):
        return Upload(connection, choker, storagewrapper, 
            max_slice_length, max_rate_period, fudge)
    ratemeasure = RateMeasure(storagewrapper.get_amount_left())
    rm[0] = ratemeasure.data_rejected
    picker = PiecePicker(len(pieces), config['rarest_first_cutoff'])
    for i in xrange(len(pieces)):
        if storagewrapper.do_I_have(i):
            picker.complete(i)
    downloader = Downloader(storagewrapper, picker,
        config['request_backlog'], config['max_rate_period'],
        len(pieces), downmeasure, config['snub_time'], 
        ratemeasure.data_came_in)
    connecter = Connecter(make_upload, downloader, choker,
        len(pieces), upmeasure, config['max_upload_rate'] * 1024, rawserver.add_task)
    infohash = sha(bencode(info)).digest()
    encoder = Encoder(connecter, rawserver, 
        myid, config['max_message_length'], rawserver.add_task, 
        config['keepalive_interval'], infohash, config['max_initiate'])
    rerequest = Rerequester(response['announce'], config['rerequest_interval'], 
        rawserver.add_task, connecter.how_many_connections, 
        config['min_peers'], encoder.start_connection, 
        rawserver.add_task, storagewrapper.get_amount_left, 
        upmeasure.get_total, downmeasure.get_total, listen_port, 
        config['ip'], myid, infohash, config['http_timeout'], errorfunc, 
        config['max_initiate'], doneflag, upmeasure.get_rate, downmeasure.get_rate,
        encoder.ever_got_incoming)
    if config['spew']:
        spewflag.set()
    DownloaderFeedback(choker, rawserver.add_task, statusfunc, 
        upmeasure.get_rate, downmeasure.get_rate, 
        upmeasure.get_total, downmeasure.get_total, ratemeasure.get_time_left, 
        ratemeasure.get_size_left, file_length, finflag,
        config['display_interval'], spewflag)


    # useful info and functions for the UI
    if paramfunc:
        paramfunc({ 'max_upload_rate' : connecter.change_max_upload_rate,  # change_max_upload_rate(<int bytes/sec>)
                    'max_uploads': choker.change_max_uploads, # change_max_uploads(<int max uploads>)
                    'listen_port' : listen_port, # int
                    'peer_id' : myid, # string
                    'info_hash' : infohash, # string
                    'start_connection' : encoder._start_connection # start_connection((<string ip>, <int port>), <peer id>)
                    })
    
    statusfunc({"activity" : 'connecting to peers'})
    ann[0] = rerequest.announce
    rerequest.begin()
    rawserver.listen_forever(encoder)
    storage.close()
    rerequest.announce(2)
