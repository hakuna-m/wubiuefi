# Written by Bram Cohen
# see LICENSE.txt for license information

from time import time

class DownloaderFeedback:
    def __init__(self, choker, add_task, statusfunc, upfunc, downfunc, uptotal, downtotal,
            remainingfunc, leftfunc, file_length, finflag, interval, spewflag):
        self.choker = choker
        self.add_task = add_task
        self.statusfunc = statusfunc
        self.upfunc = upfunc
        self.downfunc = downfunc
        self.uptotal = uptotal
        self.downtotal = downtotal
        self.remainingfunc = remainingfunc
        self.leftfunc = leftfunc
        self.file_length = file_length
        self.finflag = finflag
        self.interval = interval
        self.spewflag = spewflag
        self.lastids = []
        self.display()

    def _rotate(self):
        cs = self.choker.connections
        for id in self.lastids:
            for i in xrange(len(cs)):
                if cs[i].get_id() == id:
                    return cs[i:] + cs[:i]
        return cs

    def collect_spew(self):
        l = [ ]
        cs = self._rotate()
        self.lastids = [c.get_id() for c in cs]
        for c in cs:
            rec = {}
            rec["ip"] = c.get_ip()
            if c is self.choker.connections[0]:
                rec["is_optimistic_unchoke"] = 1
            else:
                rec["is_optimistic_unchoke"] = 0
            if c.is_locally_initiated():
                rec["initiation"] = "local"
            else:
                rec["initiation"] = "remote"
            u = c.get_upload()
            rec["upload"] = (int(u.measure.get_rate()), u.is_interested(), u.is_choked())

            d = c.get_download()
            rec["download"] = (int(d.measure.get_rate()), d.is_interested(), d.is_choked(), d.is_snubbed())
            
            l.append(rec)
        return l

    def display(self):
        self.add_task(self.display, self.interval)
        spew = []
        if self.finflag.isSet():
            status = {"upRate" : self.upfunc(), "upTotal" : self.uptotal() / 1048576.0}
            if self.spewflag.isSet():
                status['spew'] = self.collect_spew()
            self.statusfunc(status)
            return
        timeEst = self.remainingfunc()

        if self.file_length > 0:
            fractionDone = (self.file_length - self.leftfunc()) / float(self.file_length)
        else:
            fractionDone = 1
        status = {
            "fractionDone" : fractionDone, 
            "downRate" : self.downfunc(), 
            "upRate" : self.upfunc(),
            "upTotal" : self.uptotal() / 1048576.0,
            "downTotal" : self.downtotal() / 1048576.0
            }
        if timeEst is not None:
            status['timeEst'] = timeEst
        if self.spewflag.isSet():
            status['spew'] = self.collect_spew()
        self.statusfunc(status)
