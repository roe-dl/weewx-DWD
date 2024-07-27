#!/usr/bin/python3
# Copyright (C) 2023 Johanna Roedenbeck

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

"""
    The german forest administrations issue a wildfire danger level
    (Waldbrandgefahrenstufe), based on an index (Waldbrandgefahrenindex)
    calculated by the German Weather Service (DWD) and on the forest 
    characteristics (Waldbrandgefahrenklasse). They issue it once a day.
    
    There are 5 levels:
    1 - very low danger
    2 - low danger
    3 - moderate danger
    4 - high danger
    5 - extremly high danger
    
    Along with those levels, certain restrictions to forest access
    apply.
    
    Eastern german forest administrations use an icon showing a squirrel
    to represent information about wildfire protection. This 'wildfire 
    squirrel' is used in different colors here to display the wildfire 
    danger level in effect.
    
    Configuration keys:
    
    * `enable`       - enable or disable, optional, default True
    * `provider`     - data provider, actually `Sachsenforst` only,
                       mandatory
    * `server_url`   - URL to fetch data from, mandatory
    * `area`         - area code, mandatory
    * `api_key`      - API key, mandatory
    * `fetch_time`   - time of day, when data is issued by the provider,
                       mandatory; in UTC, if value ends with `UTC` otherwise
                       in local time (example "03:00 UTC", "06:30")
                       If data is not available at that time, retries
                       take place every 5 minutes.
    * `file`         - unique file name part to use when creating files, 
                       mandatory
    * `log_sleeping` - log remaining sleeping time before going to sleep,
                       optional, default False
    
    derived from higher levels of the configuration or set here:
    
    * `log_success`  - log successful operation, optional, default False
    * `log_failure`  - log failed operation, optional, default True
    * `path`         - path to write files to, mandatory
    
    Example configuration:
    
    ```
    log_success = True
    log_failure = True
    ...
    [WeatherServices]
        path = '/etc/weewx/skins/Belchertown/dwd'
        ...
        [[forecast]]
            ...
            [[[AREA10]]]
                provider = WBSProvider
                server_url = 'https://wbs.example.com/wbs.php'
                area = 10
                api_key = 'asdfghjkl1234567'
                fetch_time = 04:30 UTC
                file = XX
                log_sleeping = True
    ```
    
    Actually Saxony is supported only.
    
    Please note, you need a contract (free of charge) to display the 
    wildfire danger level on your website. Contact the respective
    forest administration for more information.
    
    If you want to add another provider, define a new class based on
    class WildfireThread, defining provider_name(), provider_url(),
    get_url(), and process_data() functions. Then append a reference
    to that class to providers_dict.
    
    https://www.dwd.de/DE/leistungen/waldbrandgef/waldbrandgef.html
"""

VERSION = "0.x"

import threading
import configobj
import requests
import datetime
import json
import random
import time
import os
import os.path

if __name__ == '__main__':

    import sys
    import __main__
    sys.path.append('/usr/share/weewx')
    x = os.path.dirname(os.path.abspath(os.path.dirname(__main__.__file__)))
    if x not in sys.path:
        sys.path.append(x)

    def logdbg(x):
        print('DEBUG',x)
    #def loginf(x):
    #    print('INFO',x)
    #def logerr(x):
    #    print('ERROR',x)
        
    import weeutil.logger
    weeutil.logger.setup('wildfire',dict())
    import logging
    log = logging.getLogger("user.DWD.wildfire")
    def loginf(msg):
        log.info(msg)
    def logerr(msg):
        log.error(msg)

else:

    import weeutil.logger
    import logging
    log = logging.getLogger("user.DWD.wildfire")

    def logdbg(msg):
        log.debug(msg)

    def loginf(msg):
        log.info(msg)

    def logerr(msg):
        log.error(msg)

from user.weatherservicesutil import wget, BaseThread
import weeutil.weeutil # startOfDay, archiveDaySpan
import weeutil.config # accumulateLeaves

# RAL3000: #A72920

WILDFIRESQUIRREL = """<svg xmlns="http://www.w3.org/2000/svg" version="1.1" width="2.508em" height="3.3em" viewBox="0 0 38 50" style="vertical-align:middle">
  <desc>wildfire squirrel, symbol for wildfire protection information</desc>
  <g fill="currentColor" stroke="#808080" stroke-width="0.2">
  <path
    d="M6.935295,44.711580 a6.482001,6.482001 0 0 0 3.596696,-4.620631 a13.644133,13.644133 0 0 0 -0.068403,-5.557274 a0.228929,0.228929 0 0 0 -0.431365,-0.046626 a27.268676,27.268676 0 0 1 -0.736688,1.752761 a6.001329,6.001329 0 0 1 -1.434802,2.179622
    a1.630918,1.630918 0 0 1 -2.269422,0.0 a6.001329,6.001329 0 0 1 -1.434802,-2.179622 a27.268676,27.268676 0 0 1 -0.736688,-1.752761
    a0.228929,0.228929 0 0 0 -0.431365,0.046626 a13.644133,13.644133 0 0 0 -0.068403,5.557274 a6.482001,6.482001 0 0 0 3.596696,4.620631 a0.490562,0.490562 0 0 0 0.418547,0.0 z
    m0.823528,-1.439428 a0.858473,0.858473 0 0 1 0.0,-1.716946 a0.858473,0.858473 0 0 1 0.0,1.716946 z
    m-2.065603,0.0 a0.858473,0.858473 0 0 1 0.0,-1.716946 a0.858473,0.858473 0 0 1 0.0,1.716946 z" />
  <path
    d="M24.055036,43.055735 a60.782331,60.782331 0 0 0 4.481236,-2.812037 a19.228682,19.228682 0 0 0 5.300621,-5.50048 a9.561191,9.561191 0 0 0 1.470733,-5.827300 a12.440101,12.440101 0 0 0 -3.571742,-7.856123
    a45.895191,45.895191 0 0 0 -4.440116,-3.935195 a17.208693,17.208693 0 0 1 -3.911794,-4.274347 a5.768483,5.768483 0 0 1 -0.383815,-5.547223 a13.360628,13.360628 0 0 1 3.27377,-4.393855
    a0.228929,0.228929 0 0 0 -0.147581,-0.400409 a56.106619,56.106619 0 0 0 -5.095566,0.141507 a18.616484,18.616484 0 0 0 -9.558791,3.489555 a11.907618,11.907618 0 0 0 -1.384843,18.113483
    a33.210675,33.210675 0 0 0 8.683288,6.177239 a15.74156,15.74156 0 0 1 5.410498,4.375847 a5.641644,5.641644 0 0 1 0.982336,5.087692 a11.642344,11.642344 0 0 1 -1.327258,2.932109
    a0.163521,0.163521 0 0 0 0.219024,0.229537 z" />
  <path
    d="M16.898712,47.468716 a14.955168,14.955168 0 0 0 5.296982,-4.184626 a3.465218,3.465218 0 0 0 -0.061093,-4.402527 a5.835861,5.835861 0 0 0 -4.178532,-2.059574
    a7.603164,7.603164 0 0 0 -7.225739,4.327981 a0.327042,0.327042 0 0 0 0.276185,0.466993 a7.478184,7.478184 0 0 0 1.382153,-0.047094 a7.921646,7.921646 0 0 1 2.354687,0.053122
    a2.365996,2.365996 0 0 1 1.899268,1.791745 a6.553674,6.553674 0 0 1 -0.192326,3.650614 a0.327042,0.327042 0 0 0 0.448415,0.403367 z" />
  <path
    d="M8.635952,44.829714 
    a3.885224,3.885224 0 0 0 0.706730,0.043170
    a8.990396,8.990396 0 0 0 1.187499,-0.115119
    a7.292493,7.292493 0 0 0 1.249999,-0.321374
    a2.324046,2.324046 0 0 0 1.000963,-0.692471
    a0.841804,0.841804 0 0 0 -0.134683,-1.213347
    a1.417503,1.417503 0 0 0 -0.769819,-0.285571
    a2.774292,2.774292 0 0 0 -0.976268,0.114453
    a2.330031,2.330031 0 0 0 -0.331815,0.129188
    a5.321219,5.321219 0 0 0 -1.971899,1.629073
    a1.381100,1.381100 0 0 0 -0.181861,0.333066
    a0.282251,0.282251 0 0 0 0.221154,0.378933 z" />
  </g>
</svg>
"""

#              N/A       1         2         3         4         5
LEVELCOLOR = ['#808080','#ffffcd','#ffd879','#ff8c39','#e9161d','#7f0126']

LEVELTEXT = [
    'unbekannt',           # N/A
    'sehr geringe Gefahr', # 1
    'geringe Gefahr',      # 2
    'mittlere Gefahr',     # 3
    'hohe Gefahr',         # 4
    'sehr hohe Gefahr'     # 5
]

INSTRUCTIONTEXT = [
    # 1 Sehr geringe Gefahr
    '',
    # 2 Geringe Gefahr
    """<p>Erh&ouml;hte Umsicht und Vorsicht, um Z&uuml;ndquellen zu vermeiden</p>
<ul>
  <li>Rauchverbot beachten.</li>
  <li>Vorsicht beim Parken.</li>
</ul>
""",
    # 3 Mittlere Gefahr
    """<p>Die Situation wird kritisch und bedarf bewu&szlig;ter Einschr&auml;nkungen.</p>
<ul>
  <li>Rauchverbot strikt einhalten.</li>
  <li>&Ouml;ffentliche Feuerstellen und Grillpl&auml;tze im und am Wald sollten nicht genutzt werden.</li>
  <li>Erh&ouml;hte Vorsicht beim Parken. Nicht auf vegetationsbedeckten Fl&auml;chen parken.</li>
</ul>
""",
    # 4 Hohe Gefahr
    """<p>Aktiver Brandschutz des Waldes durch &auml;u&szlig;erste Vorsicht und weitere Einschr&auml;nkungen</p>
<ul>
  <li>Parkpl&auml;tze und touristische Einrichtungen k&ouml;nnen beh&ouml;rdlich gesperrt sein. Sperrungen beachten.</li>
  <li>Rauchverbot strikt einhalten.</li>
  <li>&Ouml;ffentliche Feuerstellen und Grillpl&auml;tze im und am Wald d&uuml;rfen nicht genutzt werden.</li>
  <li>Wege nicht verlassen.</li>
  <li>Hohe Vorsicht beim Parken. Nicht auf vegetationsbedeckten Fl&auml;chen parken.</li>
</ul>
""",
    # Sehr hohe Gefahr
    """<p>Maximaler Schutz des Waldes vor Br&auml;nden</p>
<ul>
  <li>Beh&ouml;rden und Waldbesitzer k&ouml;nnen den Wald aus Brandschutzgr&uuml;nden sperren. Sperrungen beachten.</li>
  <li>Rauchverbot strikt einhalten.</li>
  <li>Wald meiden.</li>
  <li>Bei unvermeidlichem Aufenthalt im oder am Wald Wege nicht verlassen.</li>
  <li>&Ouml;ffentliche Feuerstellen und Grillpl&auml;tze im und am Wald d&uuml;rfen nicht genutzt werden.</li>
  <li>Nur auf &ouml;ffentlichen, freigegebenen und vegetationslosen Parkpl&auml;tzen parken.</li>
</ul>
"""
]

##############################################################################
#    General wildfire danger level fetching thread                           #
##############################################################################

class WildfireThread(BaseThread):

    @property
    def provider_name(self):
        raise NotImplementedError
        
    @property
    def provider_url(self):
        raise NotImplementedError

    def __init__(self, name, conf_dict, archive_interval):
        # get logging configuration
        log_success = weeutil.weeutil.to_bool(conf_dict.get('log_success',False))
        log_failure = weeutil.weeutil.to_bool(conf_dict.get('log_failure',True))
        # initialize thread
        super(WildfireThread,self).__init__(name='DWD-WBS-'+name,log_success=log_success,log_failure=log_failure)
        # archive interval
        self.query_interval = weeutil.weeutil.to_int(archive_interval)
        # fetch time (example: "03:00 UTC", "06:30")
        fetch_time = conf_dict.get('fetch_time','').upper().strip()
        self.fetch_time_utc = fetch_time.endswith('UTC')
        fetch_time = ''.join([i for i in fetch_time if i in '0123456789:'])
        self.fetch_time = 0
        j = 3600
        for i in fetch_time.split(':'):
            self.fetch_time += int(i)*j
            j /= 60
        # log sleeping time or not
        self.log_sleeping = weeutil.weeutil.to_bool(conf_dict.get('log_sleeping',False))
        # server data
        self.server_url = conf_dict.get('server_url')
        self.wildfire_area = conf_dict.get('area')
        self.api_key = conf_dict.get('api_key')
        # path and file name for HTML and JSON files
        self.target_path = conf_dict.get('path','.')
        self.filename = conf_dict.get('file','')
        self.bootstrapmodal = weeutil.weeutil.to_bool(conf_dict.get('Bootstrap_modal',True))
        # log config at start
        loginf("thread '%s': provider '%s', fetch time %s %s, area %s" % (self.name,self.provider_name,self.fetch_time,'UTC' if self.fetch_time_utc else 'local time',self.wildfire_area))

        self.lock = threading.Lock()

        self.init_data()
        self.last_newday_ts = 0
        self.wildfire_area_name = ''


    def init_data(self):
        self.last_data_ts = 0
        self.data = dict()


    def get_data(self, ts):
        """ get buffered data """
        today_ts = weeutil.weeutil.startOfArchiveDay(ts)
        try:
            self.lock.acquire()
            if today_ts>self.last_data_ts:
                # data is outdated
                self.init_data()
            interval = 1
            data = self.data
        finally:
            self.lock.release()
        if __name__ == '__main__':
            print('get_data()',data)
        data = {
                'wildfireDangerLevel':(data.get('wbs'),'byte','group_data'),
                'wildfireDangerLevelIssued':(data.get('released'),'unix_epoch','group_datetime'),
                'wildfireDangerLevelText':(data.get('text'),None,None),
                'wildfireDangerLevelArea':(data.get('name'),None,None),
                'wildfireDangerLevelColor':(data.get('color'),None,None)
        }
        return data,interval
    
    
    def is_fetch_time_reached(self):
        """ check if fetch time is reached """
        now = time.time()
        today = weeutil.weeutil.archiveDaySpan(now)
        if self.fetch_time_utc:
            # UTC
            reference_time = today[0]-today[0]%86400+self.fetch_time
            if reference_time<=today[0]:
                reference_time += 86400
            countdown = reference_time-now
        else:
            # local time
            now_tuple = time.localtime(now)
            now_time_of_day = now_tuple.tm_hour*3600+now_tuple.tm_min*60+now_sec
            countdown = self.fetch_time-now_time_of_day
        return now, today, countdown
    

    def get_url(self):
        """ get URL to fetch data """
        raise NotImplementedError
    
    
    def getRecord(self):
        """ download and process data 
        
            called at the beginning of the new day and from the scheduled
            time on until success
            
            Please note, that additional calls are possible due to
            interruptions of the sleeping function within the base thread.
        """
        if __name__ == '__main__':
            print('WildfireThread.getRecord()')
        now, today, countdown = self.is_fetch_time_reached()
        # Check if all is done for today
        if self.last_data_ts>today[0]:
            # Data for today already received. Nothing to do.
            return
        # Check if fetch time is reached
        fetch_time_reached = countdown<=60
        # 
        if fetch_time_reached:
            # fetch data
            try:
                reply = wget(self.get_url(),
                         log_success=self.log_success,
                         log_failure=self.log_failure)
                if reply is None: return
                reply = json.loads(reply)
                if self.log_success:
                    loginf("thread '%s': got %s" % (self.name,reply))
            except Exception as e:
                if self.log_failure:
                    logerr("thread '%s': wget %s - %s" % (self.name,e.__class__.__name__,e))
                return
            # process data
            try:
                data, issued = self.process_data(reply, now)
            except Exception as e:
                if self.log_failure:
                    logerr("thread '%s': process data %s - %s" % (self.name,e.__class__.__name__,e))
                return
            if not data or not issued:
                # no valid data received
                return
            self.last_data_ts = issued
            if issued and 'name' in data:
                self.wildfire_area_name = data['name']
        else:
            # Check if day change is already processed
            if self.last_newday_ts>today[0]:
                # Day change is already processed and fetch time is not
                # reached. Nothing to do.
                return
            self.last_newday_ts = now
            data = {
                'Issuer':self.provider_name,
                'id':self.wildfire_area,
                'name': self.wildfire_area_name, # region
                'sent': now,
                'wbs': None,
                'released': None,
                'text': 'noch nicht veröffentlicht',
                'description':'',
                'instruction':'',
                'color': LEVELCOLOR[0],
                'day': time.strftime('%d.%m.',time.localtime(now))
            }
        data['fetch_time_reached'] = fetch_time_reached
        data['processed'] = now
        data['start'] = today[0]
        data['end'] = today[1]
        try:
            self.lock.acquire()
            self.data = data
        finally:
            self.lock.release()
        self.write_html(({self.filename:[data]},'de'),self.target_path,False)
        if self.bootstrapmodal:
            self.write_html_bootstrap_modal(({self.filename:[data]},'de'),self.target_path,False)


    def waiting_time(self):
        """ time to wait until the next fetch """
        if self.last_data_ts==0: return 0
        now, today, countdown = self.is_fetch_time_reached()
        if today[0]>self.last_data_ts:
            # new day
            if countdown<=0:
                # If data is outdated, wait to the end of the current archive
                # interval.
                waiting = self.query_interval-now%self.query_interval
            else:
                # in the morning wait to the next schedule
                waiting = countdown
        else:
            # Otherwise wait to the beginning of the new day
            waiting = today[1]-now+self.query_interval
        if __name__ == '__main__':
            print('waiting_time()',time.strftime('%H:%M:%S'),'countdown',countdown,'waiting',waiting)
        return waiting


    def random_time(self, waiting):
        """ do a little bit of load balancing 
        
            let at least 10 seconds to ultimo to download an process
            data
        """
        return -random.random()*60

    def process_data(self, reply, now):
        """ convert reply to internal structure """
        raise NotImplementedError

    
    def write_html(self, wwarn, target_path, dryrun):
        """ create HTML and JSON file """
        lang = wwarn[1]
        wwarn = wwarn[0]
        for __ww,data_list in wwarn.items():
            s = ''
            r = None
            for data in data_list:
                _region = data['name']
                # if a new region starts, set a caption
                if r is None or r!=_region:
                    r = _region
                    s+='<p style="margin-top:5px"><strong>%s</strong></p>\n' % r

                valid_on = time.strftime('%d.%m.%Y',time.localtime((data['start']+data['end'])/2))
                wbs = data.get('wbs')
                color = data.get('color',LEVELCOLOR[wbs]) if wbs in (1,2,3,4,5) else LEVELCOLOR[0]
                s += '<table><tr>\n'
                s += '<td style="vertical-align:middle;padding:0.2em">\n'
                s += '<span style="color:%s">\n%s</span>\n' % (color,WILDFIRESQUIRREL)
                s += '<span style="font-size:200%%;vertical-align:middle">%s</span>\n' % (wbs if wbs else '?',)
                s += '</td><td style="padding:0.2em">\n'
                s += '<span style="font-size:80%%">Waldbrandgefahrenstufe %s</span><br /><span style="font-size:%d%%">%s</span>\n' % (data.get('wbs',''),110 if wbs else 100,data.get('text','nicht verf&uuml;gbar'))
                s += '<br /><span style="font-size:80%%">g&uuml;ltig am %s</span>' % valid_on
                s += '</td>\n'
                s += '</tr></table>\n'
                s += data.get('instruction','')
            if not s:
                s += '<p>keine Angaben verf&uuml;gbar</p>'
            s += '<p style="font-size:80%%">Waldbrandgefahrenstufe ausgegeben vom <a href="%s" target="_blank" rel="noopener">%s</a></p>\n' % (self.provider_url,self.provider_name)
            if dryrun:
                print("########################################")
                print("-- HTML -- wbs-%s.inc -------------------------------"%__ww)
                print(s)
                print("-- JSON -- wbs-%s.json ------------------------------"%__ww)
                print(json.dumps(data,indent=4,ensure_ascii=False))
            else:
                fn = os.path.join(target_path,"wbs-%s.inc" % __ww)
                fn_tmp = '%s.tmp' % fn
                with open(fn_tmp,"w") as file:
                    file.write(s)
                os.rename(fn_tmp,fn)
                fn = os.path.join(target_path,"wbs-%s.json" % __ww)
                fn_tmp = '%s.tmp' % fn
                with open(fn_tmp,"w") as file:
                    json.dump(data_list,file,indent=4,ensure_ascii=False)
                os.rename(fn_tmp,fn)

    def write_html_bootstrap_modal(self, wwarn, target_path, dryrun):
        """ create link and modal window for Bootstrap framework """
        lang = wwarn[1]
        wwarn = wwarn[0]
        for __ww,data_list in wwarn.items():
            s_link = ''
            s_modal = ''
            for data in data_list:
                valid_on = time.strftime('%d.%m.%Y',time.localtime((data['start']+data['end'])/2))
                wbs = data.get('wbs')
                color = data.get('color',LEVELCOLOR[wbs]) if wbs in (1,2,3,4,5) else LEVELCOLOR[0]
                linkname = 'wbs%s' % int(data.get('start',0)*1000)
                s_link += '<div class="wildfire-link" style="line-height:1;vertical-align:middle">'
                #if wbs and wbs!=1:
                #    s_link += '<a href="#%s" data-toggle="modal" data-target="#%s">' % (linkname,linkname)
                s_link += '<span style="float:left;padding-right:0.7em">'
                s_link += '<span style="color:%s">%s</span>\n' % (color,WILDFIRESQUIRREL)
                s_link += '<span style="font-size:200%%;vertical-align:middle">%s</span>' % (wbs if wbs else '?',)
                s_link += '</span>\n'
                if wbs and wbs!=1:
                    s_link += '<a href="#%s" data-toggle="modal" data-target="#%s">' % (linkname,linkname)
                s_link += '<span style="font-size:80%%">Waldbrandgefahrenstufe %s<br /></span><span style="font-size:%d%%">%s<br /></span>\n' % (data.get('wbs',''),110 if wbs else 100,data.get('text','nicht verf&uuml;gbar'))
                s_link += '<span style="font-size:80%%">g&uuml;ltig am %s</span>' % valid_on
                if wbs and wbs!=1:
                    s_link += '</a>'
                s_link += '</div>\n'
                # modal dialog
                if wbs and wbs!=1:
                    s_modal += '<!== Wildfire Danger Level %s -->\n' % linkname
                    s_modal += '<div class="modal fade" id="%s" tabindex="-1" role="dialog">\n' % linkname
                    s_modal += '<div class="modal-dialog" role="document">\n'
                    s_modal += '<div class="modal-content">\n'
                    s_modal += '<div class="modal-header">\n'
                    s_modal += '<button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>\n'
                    s_modal += '<h4 class="modal-title" id="wbs">%s</h4>\n' % data.get('name','')
                    s_modal += '</div>\n'
                    s_modal += '<div class="modal-body wildfire-modal" style="min-height:80px">\n'
                    s_modal += '<p style="line-height:1"><span style="float:left;padding-right:0.7em">'
                    s_modal += '<span style="color:%s">%s</span>\n' % (color,WILDFIRESQUIRREL)
                    s_modal += '<span style="font-size:200%%;vertical-align:middle">%s</span>' % (wbs if wbs else '?',)
                    s_modal += '</span>\n'
                    s_modal += '<span style="font-size:80%%">Waldbrandgefahrenstufe %s</span><br /><span style="font-size:%d%%">%s</span>\n' % (data.get('wbs',''),110 if wbs else 100,data.get('text','nicht verf&uuml;gbar'))
                    s_modal += '<br /><span style="font-size:80%%">g&uuml;ltig am %s</span>' % valid_on
                    s_modal += '</p>'
                    s_modal += data.get('description','')
                    s_modal += data.get('instruction','')
                    s_modal += '<p style="font-size:80%%">Waldbrandgefahrenstufe ausgegeben vom <a href="%s" target="_blank" rel="noopener">%s</a></p>\n' % (self.provider_url,self.provider_name)
                    s_modal += '</div>\n'
                    s_modal += '<div class="modal-footer">\n'
                    s_modal += '<button type="button" class="btn btn-primary" data-dismiss="modal">Schlie&szlig;en</button>\n'
                    s_modal += '</div>\n'
                    s_modal += '</div>\n'
                    s_modal += '</div>\n'
                    s_modal += '</div>\n'
                    s_modal += '<!== End of Wildfire Danger Level %s -->\n' % linkname
            if dryrun:
                print("########################################")
                print("-- HTML -- wbs-%s-link.inc --------------------------"%__ww)
                print(s_link)
                print("-- HTML -- wbs-%s-modal.inc -------------------------"%__ww)
                print(s_modal)
            else:
                with open(os.path.join(target_path,"wbs-%s-link.inc" % __ww),"w") as file:
                    file.write(s_link)
                with open(os.path.join(target_path,"wbs-%s-modal.inc" % __ww),"w") as file:
                    file.write(s_modal)

##############################################################################
#    Provider Sachsenforst                                                   #
##############################################################################

class SachsenforstThread(WildfireThread):

    @property
    def provider_name(self):
        return 'Staatsbetrieb Sachsenforst'
        
    @property
    def provider_url(self):
        return 'https://www.mais.de/php/sachsenforst.php'
        
    def get_url(self):
        """ get URL to fetch data """
        return str(self.server_url)+'?id='+str(self.wildfire_area)+'&key='+str(self.api_key)
    
    
    def process_data(self, reply, now):
        """ convert received data to dict """
        data = {
            'Issuer':self.provider_name,
            'ProductID':'WBS',
            'id':self.wildfire_area
        }
        if reply:
            data['name'] = reply.get('region','')
            if time.strftime('%d.%m.%Y')==reply['date']:
                try:
                    wbs = int(reply['wbs'])
                except (LookupError,TypeError,ValueError):
                    wbs = None
                try:
                    issued = time.strptime(reply['generated'],'%d.%m.%Y %H:%M')
                    #issued = time.mktime(issued[0:8]+(0,))
                    issued = time.mktime(issued)
                    if reply['wbs']==0: issued = None
                except (LookupError,ValueError,TypeError,ArithmeticError):
                    issued = None
                data['sent'] = issued
                data['released'] = issued # effective
                data['description'] = ''
                try:
                    data['instruction'] = INSTRUCTIONTEXT[wbs-1]
                except (LookupError,ValueError,TypeError,ArithmeticError):
                    data['instruction'] = ''
                data['wbs'] = wbs
                data['color'] = reply.get('color',LEVELCOLOR[wbs if wbs in (1,2,3,4,5) else 0])
                data['text'] = reply.get('text','')
                data['day'] = reply.get('date','')[0:6]
            else:
                # got out of day data
                issued = None
        else:
            issued = None
        return data, issued

##############################################################################
    
providers_dict = {
  'Sachsenforst': SachsenforstThread
}



def create_thread(thread_name,config_dict,archive_interval):
    """ create wildfire thread """
    prefix = config_dict.get('prefix','id'+thread_name)
    provider = config_dict.get('provider')
    wildfire_area = config_dict.get('area')
    if provider and provider in providers_dict:
        conf_dict = weeutil.config.accumulateLeaves(config_dict)
        conf_dict['prefix'] = prefix
        conf_dict['area'] = wildfire_area
        if weeutil.weeutil.to_bool(conf_dict.get('enable',True)):
            thread = dict()
            thread['datasource'] = 'WBS'
            thread['prefix'] = prefix
            thread['thread'] = providers_dict[provider](thread_name,conf_dict,archive_interval)
            thread['thread'].start()
            return thread
    return None
    

    
if __name__ == '__main__':

    conf_dict = configobj.ConfigObj("wildfire.conf")
    print('create wildfire thread')
    wildfire = SachsenforstThread('wildfiretest',conf_dict,300)
    print('about to start thread')
    wildfire.start()
    print('started')
    try:
        while True:
            time.sleep(300-time.time()%300+15)
            data, interval = wildfire.get_data(time.time()-15)
            print(json.dumps(data,indent=4,ensure_ascii=False))
    except Exception as e:
        print('**MAIN**',e)
    except KeyboardInterrupt:
        print()
        print('**MAIN** CTRL-C pressed')
    wwarn = ({'Test':[]},'de')
    now = time.time()
    for i in range(5):
        x = {
            'name':'Testregion',
            'wbs':i+1,
            'start':now+i*86400,
            'end':now+i*86400,
            'instruction':INSTRUCTIONTEXT[i],
            'text':LEVELTEXT[i+1],
            'color':LEVELCOLOR[i+1],
        }
        wwarn[0]['Test'].append(x)
    wildfire.write_html(wwarn,'.',False)
    if wildfire.bootstrapmodal:
        wildfire.write_html_bootstrap_modal(wwarn,'.',False)
    for i in wwarn[0]['Test']:
        wildfire.write_html(({'Test-%s' % i['wbs']:[i]},'de'),'.',False)
        if wildfire.bootstrapmodal:
            wildfire.write_html_bootstrap_modal(({'Test-%s' % i['wbs']:[i]},'de'),'.',False)
    wildfire.shutDown()
