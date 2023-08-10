#!/usr/bin/python3
# Copyright (C) 2022, 2023 Johanna Roedenbeck

"""

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""

VERSION = "0.x"

import threading
import configobj
import requests
import csv
import io
import zipfile
import time
import datetime
import json
import random

if __name__ == '__main__':

    import sys
    sys.path.append('/usr/share/weewx')

    def logdbg(x):
        print('DEBUG',x)
    def loginf(x):
        print('INFO',x)
    def logerr(x):
        print('ERROR',x)

else:

    try:
        # Test for new-style weewx logging by trying to import weeutil.logger
        import weeutil.logger
        import logging
        log = logging.getLogger("user.DWD.base")

        def logdbg(msg):
            log.debug(msg)

        def loginf(msg):
            log.info(msg)

        def logerr(msg):
            log.error(msg)

    except ImportError:
        # Old-style weewx logging
        import syslog

        def logmsg(level, msg):
            syslog.syslog(level, 'user.DWD.base: %s' % msg)

        def logdbg(msg):
            logmsg(syslog.LOG_DEBUG, msg)

        def loginf(msg):
            logmsg(syslog.LOG_INFO, msg)

        def logerr(msg):
            logmsg(syslog.LOG_ERR, msg)

import weewx
from weewx.engine import StdService
import weeutil.weeutil
import weewx.units

for group in weewx.units.std_groups:
    weewx.units.std_groups[group].setdefault('group_coordinate','degree_compass')

def wget(url,log_success=False,log_failure=True):
    """ download  """
    headers={'User-Agent':'weewx-DWD'}
    reply = requests.get(url,headers=headers)

    reply_url = reply.url.split('?')[0]

    if reply.status_code==200:
        if log_success:
            loginf('successfully downloaded %s' % reply_url)
        return reply.content
    else:
        if log_failure:
            loginf('error downloading %s: %s %s' % (reply_url,reply.status_code,reply.reason))
        return None


class BaseThread(threading.Thread):

    def __init__(self, name, log_success=False, log_failure=True):
        super(BaseThread,self).__init__(name=name)
        self.log_success = log_success
        self.log_failure = log_failure
        self.log_sleeping = False
        self.evt = threading.Event()
        self.running = True
        self.query_interval = 300


    def shutDown(self):
        """ request thread shutdown """
        self.running = False
        loginf("thread '%s': shutdown requested" % self.name)
        self.evt.set()


    def get_data(self, ts):
        raise NotImplementedError
        
        
    def getRecord(self):
        """ download and process data """
        raise NotImplementedError


    def waiting_time(self):
        """ time to wait until the next data fetch """
        return self.query_interval-time.time()%self.query_interval
    
    
    def run(self):
        """ thread loop """
        loginf("thread '%s' starting" % self.name)
        try:
            while self.running:
                # download and process data
                self.getRecord()
                # time to to the next interval
                waiting = self.waiting_time()
                if waiting<=60: waiting += self.query_interval
                # do a little bit of load balancing
                waiting -= random.random()*60
                # wait
                if self.log_sleeping:
                    loginf ("thread '%s': sleeping for %s seconds" % (self.name,waiting))
                self.evt.wait(waiting)
        except Exception as e:
            logerr("thread '%s': main loop %s - %s" % (self.name,e.__class__.__name__,e))
        finally:
            loginf("thread '%s' stopped" % self.name)
