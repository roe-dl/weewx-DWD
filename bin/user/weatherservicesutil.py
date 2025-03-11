#!/usr/bin/python3
# Copyright (C) 2022, 2023, 2024 Johanna Roedenbeck

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
from requests.auth import AuthBase
import csv
import io
import zipfile
import time
import datetime
import json
import random
import traceback

if __name__ == '__main__':
    import sys
    sys.path.append('/usr/share/weewx')

import __main__
if __name__ == '__main__' or __main__.__file__.endswith('weatherservices.py'):

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

# week day names
WEEKDAY_SHORT = {
    'de':['Mo','Di','Mi','Do','Fr','Sa','So'],
    'en':['Mon','Tue','Wed','Thu','Fri','Sat','Sun'],
    'fr':['lu','ma','me','je','ve','sa','di'],
    'it':['lun.','mar.','mer.','gio.','ven.','sab.','dom.'],
    'cs':['Po','Út','St','Čt','Pá','So','Ne'],
    'cz':['Po','Út','St','Čt','Pá','So','Ne'],
    'pl':['pon.','wt.','śr.','czw.','pt.','sob.','niedz.'],
    'nl':['Ma','Di','Wo','Do','Vr','Za','Zo'],
}

WEEKDAY_LONG = {
    'de':['Montag','Dienstag','Mittwoch','Donnerstag','Freitag','Sonnabend','Sonntag'],
    'en':['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'],
    'fr':['lundi','mardi','mercredi','jeudi','vendredi','samedi','dimanche'],
    'it':['lunedì','martedì','mercoledì','giovedì','venerdì','sabato','domenica'],
    'cs':['pondělí','úterý','středa','čtvrtek','pátek','sobota','neděle'],
    'cz':['pondělí','úterý','středa','čtvrtek','pátek','sobota','neděle'],
    'pl':['poniedziałek','wtorek','środa','czwartek','piątek','sobota','niedziela'],
    'nl':['maansdag','dinsdag','woensdag','donderdag','vrijdag','zaterdag','zondag'],
}

HTTP_MONTH = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']

# Initialize default unit for the unit groups defined in this extension
for _,ii in weewx.units.std_groups.items():
    ii.setdefault('group_wmo_ww','byte')
    ii.setdefault('group_wmo_wawa','byte')
    ii.setdefault('group_wmo_W','byte')
    ii.setdefault('group_wmo_Wa','byte')
    ii.setdefault('group_coordinate','degree_compass')

def http_timestamp_to_ts(s):
    """ convert HTTP time to Unix epoch timestamp
    
        example: Wed, 17 Jul 2024 12:13:14 GMT
        
        Args:
            s(str): timestamp string as found in HTTP headers
        
        Returns:
            int: timestamp or None in case of errors
    """
    if not s: return None
    try:
        # split day of week
        x = s.split(',')
        # split the parts of date and time
        dt = x[1].strip().split(' ')
        # get the month number from abbreviated month name
        mon = HTTP_MONTH.index(dt[1])+1
        # hours since 0:0:0 UTC
        hr = dt[3].split(':')
        # return result
        return weeutil.weeutil.utc_to_ts(
            weeutil.weeutil.to_int(dt[2]),
            mon,
            weeutil.weeutil.to_int(dt[0]),
            weeutil.weeutil.to_int(hr[0])+weeutil.weeutil.to_int(hr[1])/60.0+weeutil.weeutil.to_int(hr[2])/3600.0
        )
    except (ValueError,LookupError):
        return None

def ts_to_http_timestamp(ts):
    """ convert Unix epoch timestamp to text as used in HTTP headers
        
        Args:
            ts(int): Unix epoch timestamp
            
        Returns:
            str: formatted timestamp
    """
    x = time.gmtime(ts)
    return '%s, %02d %s %04d %02d:%02d:%02d GMT' % (
            WEEKDAY_SHORT['en'][x.tm_wday],
            x.tm_mday,HTTP_MONTH[x.tm_mon-1],x.tm_year,
            x.tm_hour,x.tm_min,x.tm_sec)

class KNMIAuth(AuthBase):
    def __init__(self, api_key):
        super(KNMIAuth,self).__init__()
        self.api_key = str(api_key)
    
    def __call__(self, r):
        r.headers['Authorization'] = self.api_key
        return r

def wget_extended(url, log_success=False, log_failure=True, session=requests, if_modified_since=None, auth=None):
    """ download  
    
        Args:
            url(str): URL to retrieve
            log_success(boolean): log in case of success or not
            log_failure(boolean): log in case of failure or not
            session(Session): http session
            if_modified_since(int): download only if newer than this timestamp
        
        Returns:
            tuple: Etag, Last-Modified, data received, status code
    """
    elapsed = time.time()
    headers = {'User-Agent':'weewx-DWD'}
    if if_modified_since is not None:
        # add a If-Modified-Since header
        headers['If-Modified-Since'] = ts_to_http_timestamp(if_modified_since)
    try:
        reply = session.get(url, headers=headers, auth=auth, timeout=5)
    except requests.exceptions.Timeout:
        if log_failure:
            logerr('timeout downloading %s' % url)
        return (None,None,None,None)
    elapsed = time.time()-elapsed

    reply_url = reply.url.split('?')[0]

    if reply.status_code==200:
        # success
        if log_success:
            loginf('successfully downloaded %s in %.2f seconds' % (reply_url,elapsed))
        return (
                reply.headers.get('Etag'),
                http_timestamp_to_ts(reply.headers.get('Last-Modified')),
                reply.content,
                reply.status_code
        )
    elif reply.status_code==304 and if_modified_since is not None:
        # not changed
        if log_success or log_failure:
            logdbg('skipped, %s was not changed since %s' % (reply_url,headers['If-Modified-Since']))
        return (
            reply.headers.get('Etag'),
            http_timestamp_to_ts(reply.headers.get('Last-Modified')),
            None,
            reply.status_code
        )
    else:
        # failure
        if log_failure:
            logerr('error downloading %s: %s %s' % (reply_url,reply.status_code,reply.reason))
        return (None,None,None,reply.status_code)

def wget(url, log_success=False, log_failure=True, session=requests):
    """ download  
    
        Args:
            url(str): URL to retrieve
            log_success(boolean): log in case of success or not
            log_failure(boolean): log in case of failure or not
            session(Session): http session
        
        Returns:
            bytes: data received or None in case of failure
    """
    return wget_extended(url, log_success, log_failure, session)[2]

class BaseThread(threading.Thread):

    def __init__(self, name, log_success=False, log_failure=True):
        super(BaseThread,self).__init__(name=name)
        self.log_success = log_success
        self.log_failure = log_failure
        self.log_sleeping = False
        self.evt = threading.Event()
        self.running = True
        self.query_interval = 300
        self.last_run_duration = 0

    def shutDown(self):
        """ request thread shutdown """
        self.running = False
        loginf("thread '%s': shutdown requested" % self.name)
        self.evt.set()

    def get_data(self, ts):
        raise NotImplementedError
    
    def set_current_location(self, latitude, longitude):
        """ remember current location for mobile stations """
        pass
    
    def getRecord(self):
        """ download and process data """
        raise NotImplementedError

    def waiting_time(self):
        """ time to wait until the next data fetch """
        return self.query_interval-time.time()%self.query_interval
    
    def random_time(self, waiting):
        """ do a little bit of load balancing 
        
            let at least 10 seconds to ultimo to download and process
            data
        """
        if waiting<=10: return 0.1-waiting
        w = waiting-10
        return -random.random()*(60 if w>60 else w)-10

    def run(self):
        """ thread loop """
        loginf("thread '%s' starting" % self.name)
        try:
            while self.running:
                # time to to the next interval
                waiting = self.waiting_time()
                # do a little bit of load balancing
                waiting_r = self.random_time(waiting)
                waiting += waiting_r
                # wait
                if self.log_sleeping:
                    loginf ("thread '%s': sleeping for %s seconds" % (self.name,waiting))
                if waiting>0: 
                    if self.evt.wait(waiting): break
                # download and process data
                start_ts = time.thread_time_ns()
                self.getRecord()
                self.last_run_duration = (time.thread_time_ns()-start_ts)*1e-9
                if waiting_r<=0:
                    if self.evt.wait(1-waiting_r): break
        except Exception as e:
            logerr("thread '%s': main loop %s - %s" % (self.name,e.__class__.__name__,e))
            for ii in traceback.format_tb(e.__traceback__):
                for jj in ii.splitlines():
                    logerr("thread '%s': *** %s" % (self.name,jj.replace('\n',' ').strip()))
        finally:
            loginf("thread '%s' stopped" % self.name)
    
    def get_parameters(self, section_dict, replace_dict=dict()):
        parameters = dict()
        for i,j in section_dict.get('parameters',dict()).items():
            if isinstance(j,list):
                k = ','.join([str(jj).replace(',','_') for jj in j])
            else:
                k = j
            for to_replace, replace_by in replace_dict.items():
                k = k.replace(to_replace, replace_by)
            k = k.replace('%','%25').replace("'",'%27').replace('/','%2F').replace(' ','%20').replace('<','%3C').replace('=','%3D').replace('>','%3E')
            parameters[i] = k
        return parameters


if __name__ == '__main__':
    ts = http_timestamp_to_ts('Mon, 17 Jul 2024 12:13:14 GMT')
    print(ts)
    print(time.strftime('%Y-%m-%d %H:%M:%S %z',time.gmtime(ts)))
    url = 'https://opendata.dwd.de/weather/text_forecasts/html/VHDL50_DWLG_LATEST_html'
    reply = wget(url,True,True,if_modified_since=1721229741-10)
    print(reply[0],reply[1],time.strftime('%Y-%m-%d %H:%M:%S',time.gmtime(reply[1])))
    print(reply[2].decode('iso8859-1'))
