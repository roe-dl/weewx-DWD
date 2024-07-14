#!/usr/bin/python3
# Copyright (C) 2024 Johanna Roedenbeck

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

    Note: If you start WeeWX between 11:00 and 12:00 no actual data
          will be available. 
    
"""

import json
import configobj
import time
import threading
import os
import os.path
import random
import copy

if __name__ == '__main__':
    import optparse
    import sys
    sys.path.append('/usr/share/weewx')

import __main__
if __name__ == '__main__' or __main__.__file__.endswith('weatherservices.py'):

    def logdbg(x):
        print('DEBUG health',x)
    def loginf(x):
        print('INFO health',x)
    def logerr(x):
        print('ERROR health',x)

else:

    try:
        # Test for new-style weewx logging by trying to import weeutil.logger
        import weeutil.logger
        import logging
        log = logging.getLogger("user.DWD.health")

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

import weeutil.weeutil
import weewx.units
import weewx.accum
from user.weatherservicesutil import wget, BaseThread, WEEKDAY_LONG

ACCUM_STRING = { 'accumulator':'firstlast','extractor':'last' }

NEG_NEG_SYMBOL = (2.2,"-25 -25 110 50",
"""  <circle cx="0" cy="0" r="25" fill="#e53210" stroke="none" />
  <path fill="#ffffff" stroke="none"
   d="m-19,-4 h38 v8 h-38 z" />
  <circle cx="55" cy="0" r="25" fill="#e53210" stroke="none" />
  <path fill="#ffffff" stroke="none"
   d="m36,-4 h38 v8 h-38 z" />
""")
NEG_SYMBOL = (1.0,"-25 -25 50 50",
"""  <circle cx="0" cy="0" r="25" fill="#f9e814" stroke="none" />
  <path fill="#ffffff" stroke="none"
   d="m-19,-4 h38 v8 h-38 z" />
""")
NEUTRAL_SYMBOL = (1.0,"-25 -25 50 50",
"""  <circle cx="0" cy="0" r="25" fill="#3ea72d" stroke="none" />
  <path fill="#ffffff" stroke="none" stroke-with="0.1"
   d="m0,-19 a17,19 0 0 0 0,38 a17,19 0 0 0 0,-38 v7 a10,12 0 0 1 0,24 a10,12 0 0 1 0,-24 z" />
""")
POS_SYMBOL = (1.0,"-25 -25 50 50",
"""  <circle cx="0" cy="0" r="25" fill="#006eff" stroke="none" />
  <path fill="#ffffff" stroke="none"
   d="m-19,-4 h15 v-15 h8 v15 h15 v8 h-15 v15 h-8 v-15 h-15 z" />
""")
SVG_START = """<svg
   width="%s"
   height="%s"
   viewBox="%s"
   version="1.1"
   xmlns="http://www.w3.org/2000/svg">
"""
SVG_END = """</svg>
"""
VAL_SYMBOLS = {
    'geringe Gefährdung': NEG_SYMBOL,
    'hohe Gefährdung': NEG_NEG_SYMBOL,
    'kein Einfluss': NEUTRAL_SYMBOL,
    'positiver Einfluss': POS_SYMBOL,
}

def symbol(val, height):
    if val not in VAL_SYMBOLS: return val
    sym = VAL_SYMBOLS[val]
    width = height*sym[0]
    return '%s<title>%s</title>%s%s' % (SVG_START % (width,height,sym[1]),val,sym[2],SVG_END)

class DwdHealthThread(BaseThread):

    BASE_URL = 'https://opendata.dwd.de/climate_environment/health'
    
    ALERTS_URL = {
        'biowetter':'alerts/biowetter.json',
        'thermal':'alerts/gt.json',
        'pollen':'alerts/s31fg.json',
        'uvi':'alerts/uvi.json'
    }
    
    TIMESPANS1 = [
        'today',
        'tomorrow',
        'dayafter_to'
    ]

    TIMESPANS2 = [
        'today_morning',
        'today_afternoon',
        'tomorrow_morning',
        'tomorrow_afternoon',
        'dayafter_to_morning',
        'dayafter_to_afternoon',
    ]
    
    BIOWETTER_OBS = {
        'biowetterValidFrom':('unix_epoch','group_time'),
        'biowetterValidTo':('unix_epoch','group_time'),
        'biowetterIssued':('unix_epoch','group_time'),
        'biowetterNextUpdate':('unix_epoch','group_time'),
        'biowetterValue':(None,None),
    }
    
    POLLEN_OBS = {
        'pollenValidFrom':('unix_epoch','group_time'),
        'pollenValidTo':('unix_epoch','group_time'),
        'pollenIssued':('unix_epoch','group_time'),
        'pollenNextUpdate':('unix_epoch','group_time'),
    }
    
    POLLEN_TYPES = [
        'Hasel',
        'Erle',
        'Esche',
        'Birke',
        'Graeser',
        'Roggen',
        'Beifuss',
        'Ambrosia',
    ]

    POLLEN_COLORS = [
        '#3ea72d',   # 0
        '#dafac7',   # 0.5
        '#fee391',   # 1
        '#fec44e',   # 1.5
        '#fe9929',   # 2
        '#f03b20',   # 2.5
        '#bd0026',   # 3
    ]

    @property
    def provider_name(self):
        return 'DWD'
        
    @property
    def provider_url(self):
        return 'https://www.dwd.de'
    
    @classmethod
    def is_provided(cls, model):
        return model in cls.ALERTS_URL

    def __init__(self, name, conf_dict, archive_interval):
        # get logging configuration
        log_success = weeutil.weeutil.to_bool(conf_dict.get('log_success',False))
        log_failure = weeutil.weeutil.to_bool(conf_dict.get('log_failure',True))
        # initialize thread
        super(DwdHealthThread,self).__init__(name='DWD-Health-'+name,log_success=log_success,log_failure=log_failure)
        # archive interval
        self.query_interval = weeutil.weeutil.to_int(archive_interval)
        # log sleeping time or not
        self.log_sleeping = weeutil.weeutil.to_bool(conf_dict.get('log_sleeping',False))
        # config
        self.model = conf_dict.get('model')
        if self.model: self.model = self.model.lower()
        self.url = '%s/%s' % (DwdHealthThread.BASE_URL,DwdHealthThread.ALERTS_URL[self.model])
        self.area = conf_dict.get('area')
        self.target_path = conf_dict.get('path','.')
        self.filename = '%s-%s' % (self.model,conf_dict.get('file',self.area))
        self.data = dict()
        self.tab = (dict(),dict())
        loginf("thread '%s': area '%s', URL '%s'" % (self.name,self.area,self.url))
        self.last_update = 0
        self.next_update = 0
        self.area_name = ''
        self.lock = threading.Lock()
        # register observation types and accumulators
        prefix = conf_dict.get('prefix','')
        _accum = dict()
        if self.model=='biowetter':
            obs_dict = DwdHealthThread.BIOWETTER_OBS
        elif self.model=='pollen':
            obs_dict = DwdHealthThread.POLLEN_OBS
            for plant in DwdHealthThread.POLLEN_TYPES:
                obs_dict['pollen%sValue' % plant] = ('count','group_count')
                obs_dict['pollen%sText' % plant] = (None,None)
        else:
            obs_dict = None
        if obs_dict:
            for key, obs in obs_dict.items():
                obstype = key
                obsgroup = obs[1]
                #print(prefix,obstype,obsgroup)
                if obsgroup:
                    # number variable
                    if prefix:
                        weewx.units.obs_group_dict.setdefault(prefix+obstype[0].upper()+obstype[1:],obsgroup)
                    else:
                        weewx.units.obs_group_dict.setdefault(obstype,obsgroup)
                else:
                    # string variable
                    if prefix:
                        _accum[prefix+obstype[0].upper()+obstype[1:]] = ACCUM_STRING
                    else:
                        _accum[obstype] = ACCUM_STRING
        if _accum:
            weewx.accum.accum_dict.maps.append(_accum)
        # classes to include in <table> and surronding <div> tag
        self.horizontal_table_classes = 'table-striped'
        self.horizontal_main_effect_td_classes = 'records-header'
        # test output
        if __name__ == "__main__":
            print('obs_group_dict')
            print('')
            print(weewx.units.obs_group_dict)
            print('accum_dict')
            print(weewx.accum.accum_dict)
            print('')
            print('log_success',self.log_success)
            print('log_failure',self.log_failure)
            print('log_sleeping',self.log_sleeping)
            print('model',self.model)
            print('filename',self.filename)

    def get_data(self, ts):
        """ get actual biometeorologic forecast data for the given 
            timestamp
            
            Note: This method is called by another thread. So lock
                  internal data from changing.
        """
        data = dict()
        try:
            self.lock.acquire()
            # If data is already received, timestamps of actual and next
            # release are always available, independent of the time data
            # is requested for.
            data['%sLastUpdate' % self.model] = (
                self.last_update if self.last_update else None,
                'unix_epoch',
                'group_time'
            )
            data['%sNextUpdate' % self.model] = (
                self.next_update if self.next_update else None,
                'unix_epoch',
                'group_time'
            )
            # Look for data for the requested timestamp
            for ii in self.data:
                if ts<=ii[1] and ts>ii[0]:
                    data.update(ii[2])
        finally:
            self.lock.release()
        return data,5
    
    def convert_timestamp(self, val):
        """ convert timestamp to unix_epoch """
        if val is None: return None
        val = str(val)
        if 'T' in val:
            val = val.split('T')
        else:
            val = val.split(' ')
        if len(val)<1: return None
        dt = val[0].split('-')
        if len(val)<2:
            ti = [0,0,0]
        else:
            ti = val[1].split(':')
        try:
            return time.mktime((
                int(dt[0]), # year
                int(dt[1]), # month
                int(dt[2]), # day
                int(ti[0]), # hour
                int(ti[1]), # minute
                int(ti[2]) if len(ti)>2 else 0, # second
                -1,
                -1,
                -1
            ))
        except (TypeError,OverflowError,ValueError) as e:
            logerr("thread '%s': convert timestamp %s - %s" % (self.name,e.__class__.__name__,e))
            return None

    def process_pollen(self, zone, name, author, last_update, next_update, now, legend):
        """ pollen forecast """
        lang = 'de'
        data = []
        tab = dict()
        timespans = dict()
        # name of the area data is valid for
        if zone.get('partregion_id',-1)==-1:
            area_name = zone.get('region_name',zone['region_id'])
        else:
            area_name = zone.get('partregion_name',zone['partregion_id'])
        # process legend
        legend_dict = dict()
        a = dict()
        b = dict()
        for ii in legend:
            if ii.startswith('id'):
                no = ii.split('_')[0]
                if ii.endswith('desc'):
                    b[no] = legend[ii]
                else:
                    a[no] = legend[ii]
        for ii in a:
            legend_dict[a[ii]] = b.get(ii)
        del a
        del b
        # test output
        if __name__ == "__main__":
            print('Legende:')
            print(legend_dict)
        # initialize timespans (today, tomorrow, day after tomorrow)
        dt = last_update
        for ii in range(3):
            start, end = weeutil.weeutil.archiveDaySpan(dt)
            wday = WEEKDAY_LONG[lang][time.localtime(start).tm_wday]
            dd = time.strftime('%d.%m.',time.localtime(start))
            ti = None
            data.append((start,end,{
                'pollenIssued':(last_update,'unix_epoch','group_time'),
                'pollenValidFrom':(start,'unix_epoch','group_time'),
                'pollenValidTo':(end,'unix_epoch','group_time'),
            }))
            if end>=now:
                timespans[(wday,dd,ti)] = None
            dt = end+3600
        # process data
        for plant in zone.get('Pollen',[]):
            for idx,timespan in enumerate(DwdHealthThread.TIMESPANS1):
                if timespan in zone['Pollen'][plant]:
                    val = zone['Pollen'][plant][timespan]
                    if val.isdigit():
                        val_f = float(val)
                    else:
                        val_f = val.split('-')
                        try:
                            val_f = float(val_f[0])+0.5
                        except (ValueError,OverflowError):
                            val_f = None
                    data[idx][2]['pollen'+plant+'Value'] = (val_f,None,None)
                    data[idx][2]['pollen'+plant+'Text'] = (legend_dict.get(val),None,None)
                    wday = WEEKDAY_LONG[lang][time.localtime(data[idx][0]).tm_wday]
                    dt = time.strftime('%d.%m.',time.localtime(data[idx][0]))
                    ti = None
                    if end>=now:
                        if plant not in tab:
                            tab[plant] = dict()
                        if (wday,dt,ti) not in tab[plant]:
                            tab[plant][(wday,dt,ti)] = dict()
                        tab[plant][(wday,dt,ti)] = {'value':val_f,'effect':legend_dict.get(val)}
        return data, (tab, timespans), area_name

    def process_bio(self, zone, name, author, last_update, next_update, now):
        """ process bioweather data """
        lang = 'de'
        data = []
        tab = dict()
        timespans = dict()
        # name of the area data is valid for
        area_name = zone.get('name',zone['id'])
        # process data
        for timespan in DwdHealthThread.TIMESPANS2:
            if timespan in zone:
                #loginf(zone[timespan])
                forecast = zone[timespan]
                dt = forecast['date']
                ti = forecast['name']
                val = forecast['value']
                #print(name,dt,ti,val)
                if ti.startswith('1'):
                    start = self.convert_timestamp('%sT0:0:0' % dt)
                    end = self.convert_timestamp('%sT12:0:0' % dt)
                    wday = WEEKDAY_LONG[lang][time.localtime(end).tm_wday]
                    dt = time.strftime('%d.%m.',time.localtime(end))
                else:
                    start = self.convert_timestamp('%sT12:0:0' % dt)
                    end = self.convert_timestamp('%sT24:0:0' % dt)
                    wday = WEEKDAY_LONG[lang][time.localtime(start).tm_wday]
                    dt = time.strftime('%d.%m.',time.localtime(start))
                if end>=now:
                    timespans[(wday,dt,ti)] = val
                _data = {
                    'biowetterIssued':(last_update,'unix_epoch','group_time'),
                    'biowetterValidTo':(end,'unix_epoch','group_time'),
                    'biowetterValidFrom':(start,'unix_epoch','group_time'),
                    'biowetterValue':(val,None,None),
                }
                for effect in forecast['effect']:
                    #print(effect['name'],effect['value'])
                    if end>=now:
                        if effect['name'] not in tab:
                            tab[effect['name']] = dict()
                        if (wday,dt,ti) not in tab[effect['name']]:
                            tab[effect['name']][(wday,dt,ti)] = dict()
                        tab[effect['name']][(wday,dt,ti)]['effect'] = effect['value']
                    for subeffect in effect.get('subeffect',[]):
                        nm = subeffect['name']
                        vl = subeffect['value']
                        #print('%-40s: %s' % (nm,vl))
                        if end>=now:
                            nmm = '* %s' % nm
                            if nmm not in tab:
                                tab[nmm] = dict()
                            if (wday,dt,ti) not in tab[nmm]:
                                tab[nmm][(wday,dt,ti)] = dict()
                            tab[nmm][(wday,dt,ti)]['effect'] = vl
                for recomm in forecast['recomms']:
                    #print(recomm['name'],recomm['value'])
                    if end>=now:
                        if recomm['name'] not in tab:
                            tab[recomm['name']] = dict()
                        if (wday,dt,ti) not in tab[recomm['name']]:
                            tab[recomm['name']][(wday,dt,ti)] = dict()
                        tab[recomm['name']][(wday,dt,ti)]['recomm'] = recomm['value']
                #print('')
                data.append((start,end,_data))
        return data, (tab, timespans), area_name
    
    def process_uvi(self, zone, name, author, last_update, next_update, now, forecast_day):
        """ process bioweather data """
        lang = 'de'
        data = []
        tab = dict()
        timespans = dict()
        # name of the area data is valid for
        area_name = zone.get('city','')
        # forecast start timestamp
        start_timestamp = self.convert_timestamp('%sT12:0:0' % forecast_day)
        # process data
        for idx, timespan in enumerate(DwdHealthThread.TIMESPANS1):
            if timespan in zone.get('forecast',dict()):
                val = zone['forecast'][timespan]
                dt = start_timestamp+idx*86400
                start, end = weeutil.weeutil.archiveDaySpan(dt)
                dt = time.localtime(dt)
                wday = WEEKDAY_LONG[lang][dt.tm_wday]
                dt = time.strftime('%d.%m.',dt)
                ti = None
                timespans[(wday,dt,ti)] = val
                data.append((start,end,{
                    'uviforecastIssued':(last_update,'unix_epoch','group_time'),
                    'uviforecastValidTo':(end,'unix_epoch','group_time'),
                    'uviforecastValidFrom':(start,'unix_epoch','group_time'),
                    'uviforecastValue':(val,'uv_index','group_uv')
                }))
        return data, (tab, timespans), area_name
    
    def write_html(self, tabtimespans, area_name, last_update, now):
        if tabtimespans:
            tab = tabtimespans[0]
            timespans = tabtimespans[1]
            colwidth = 100/(len(timespans)+1)
            s = '<p><strong>%s</strong></p>\n' % area_name
            s += '<table class="%s">' % self.horizontal_table_classes
            s += '<thead style="position:sticky;top:0">'
            s += '<tr><th width="%d%%"></th>' % colwidth
            timespansvalue = False
            for ii,val in timespans.items():
                s += '<th width="%d%%" scope="col">%s<br />%s<br />%s</th>' % (colwidth,ii[0],ii[1],ii[2])
                if val is not None: timespansvalue = True
            s += '</tr>'
            s += '</thead><tbody>'
            if timespansvalue:
                s += '<tr><td scope="row">Wert</td>'
                for _,ii in timespans.items():
                    s += '<td>%s</td>' % ii
                s += '</tr>'
            for ii in tab:
                vertical_align = 'middle'
                for jj in timespans:
                    if jj in tab[ii] and 'recomm' in tab[ii][jj] and tab[ii][jj]['recomm']!='keine':
                        vertical_align = 'top'
                        break
                if ii.startswith('*') or self.model!='biowetter':
                    s += '<tr><td style="vertical-align:%s" scope="row">%s</td>' % (
                        vertical_align,
                        ii
                    )
                else:
                    s += '<tr><td class="%s" colspan="%d">%s</td></tr>' % (
                        self.horizontal_main_effect_td_classes,
                        len(timespans)+1,
                        ii
                    )
                    s += '<tr><td style="vertical-align:%s" scope="row">%s</td>' % (
                        vertical_align,
                        'Insgesamt'
                    )
                for jj in timespans:
                    s += '<td style="vertical-align:%s">' % vertical_align
                    if jj in tab[ii]:
                        if self.model=='pollen':
                            col = tab[ii][jj].get('value')
                            if col is not None:
                                if col>3: col = 3
                                if col<0: col = 0
                                tcl = '#ffffff' if col<0.25 or col>1.75 else '#000000'
                                col = DwdHealthThread.POLLEN_COLORS[int(round(col*2.0,0))]
                                s += ('<span style="color:%s;background-color:%s">&nbsp;%s&nbsp;</span> ' % (tcl,col,tab[ii][jj]['value'])).replace('.',',')
                        effect = tab[ii][jj].get('effect','')
                        if effect=='geringe Gefährdung':
                            col = '#ffd879'
                        elif effect=='hohe Gefährdung':
                            col = '#e53210'
                        elif effect=='positiver Einfluss':
                            col = '#7cb5ec'
                        else:
                            col = ''
                        if self.model=='biowetter':
                            effect = symbol(effect,20)
                        if self.model=='pollen':
                            s += '<span class="hidden-xs">'
                        if col:
                            s += '<span style="color:%s">%s</span>' % (col,effect)
                        else:
                            s += effect
                        if 'recomm' in tab[ii][jj] and tab[ii][jj]['recomm']!='keine':
                            s += '<br /><strong>%s:</strong><br />%s' % ('Empfehlung',tab[ii][jj]['recomm'])
                        if self.model=='pollen':
                            s += '</span>'
                    s += '</td>'
                s += '</tr>'
            s += '</tbody>'
            s += '</table>\n'
            if self.model=='biowetter':
                s += '<ul style="list-style:none;width:100%;padding:0;margin-left:-1em;margin-bottom:auto">'
                for ii in ('Legende:','hohe Gefährdung','geringe Gefährdung','kein Einfluss','positiver Einfluss'):
                    sym = symbol(ii,20)
                    txt = ii if sym==ii else '%s&nbsp;%s' % (sym,ii)
                    s += '<li style="display:inline-block;padding-left:1em;padding-right:1em">%s</li>' % txt
                s += '</ul>'
            s += '<p style="font-size:65%%">herausgegeben vom <a href="%s" target="_blank">%s</a> am %s | Vorhersage erstellt am %s</p>' % (
                self.provider_url,self.provider_name,
                time.strftime('%d.%m.%Y %H:%M',time.localtime(last_update)),
                time.strftime('%d.%m.%Y %H:%M',time.localtime(now))
            )
            try:
                fn = os.path.join(self.target_path,'health-%s.inc' % self.filename)
                fn_tmp = '%s.tmp' % fn
                with open(fn_tmp,'wt') as f:
                    f.write(s)
                os.rename(fn_tmp,fn)
            except OSError as e:
                if self.log_failure:
                    logerr("thread '%s': cannot write .inc file %s - %s" % (self.name,e.__class__.__name__,e))
            """
            try:
                fn = os.path.join(self.target_path,'health-%s.json' % self.filename
                fn_tmp = '%s.tmp' % fn
                with open(fn_tmp,'wt') as f:
                    json.dump(tab,f,indent=4,ensure_ascii=False)
                os.rename(fn_tmp,fn)
            except (OSError,TypeError,RecursionError,ValueError) as e:
                if self.log_failure:
                    logerr("thread '%s': cannot write .json file %s - %s" % (self.name,e.__class__.__name__,e))
            """
    
    def getRecord(self):
        """ download and process data """
        if __name__ == "__main__":
            print('getRecord() start')
        try:
            reply = wget(self.url,
                     log_success=self.log_success,
                     log_failure=self.log_failure)
            now = time.time()
            reply = json.loads(reply)
        except Exception as e:
            if self.log_failure:
                logerr("thread '%s': wget %s - %s" % (self.name,e.__class__.__name__,e))
            return
        data = None
        try:
            last_update = self.convert_timestamp(reply.get('last_update'))
            next_update = self.convert_timestamp(reply.get('next_update'))
            if self.model=='biowetter':
                for zone in reply['zone']:
                    if zone['id']==self.area:
                        data, tabtimespans, area_name = self.process_bio(zone,reply.get('name'),reply.get('author'),last_update,next_update,now)
                        break
            elif self.model=='pollen':
                area1 = int(self.area)
                if (area1%10)!=0:
                    # subregion
                    area2 = area1
                    area1 -= area1%10
                else:
                    # main region
                    area2 = -1
                print('area',area1,area2)
                for zone in reply['content']:
                    if (zone['region_id']==area1 and 
                        zone['partregion_id']==area2):
                        data, tabtimespans, area_name = self.process_pollen(zone,reply.get('name'),reply.get('sender'),last_update,next_update,now,reply.get('legend'))
                        break
            elif self.model=='uvi':
                for zone in reply['content']:
                    if zone['city']==self.area:
                        data, tabtimespans, area_name = self.process_uvi(zone,reply.get('name'),reply.get('sender'),last_update,next_update,now,reply.get('forecast_day'))
                        break
        except Exception as e:
            if self.log_failure:
                logerr("thread '%s': process %s - %s" % (self.name,e.__class__.__name__,e))
        # If new data could be obtained, update the cache.
        if data:
            try:
                self.write_html(tabtimespans, area_name, last_update, now)
            except Exception as e:
                if self.log_failure:
                    logerr("thread '%s': write HTML %s - %s" % (self.name,e.__class__.__name__,e))
            try:
                self.lock.acquire()
                self.last_update = last_update
                self.next_update = next_update
                self.area_name = area_name
                if self.data:
                    self.data = [self.data[-1]] + data
                else:
                    self.data = data
                self.tab = tabtimespans
            finally:
                self.lock.release()

    def waiting_time(self):
        now = time.time()
        # If it is after the time the next update is scheduled for,
        # fetch data at the end of the current archive interval.
        if now>=self.next_update:
            return super(DwdHealthThread,self).waiting_time()
        # At the beginning of the next day there is no new data, but
        # the HTML table has to be rewritten.
        eod = weeutil.weeutil.archiveDaySpan(now)[1]+self.query_interval
        # noon of the day in case it is in future
        mid = eod-43200
        if mid<now or self.model!='biowetter': mid = eod
        # when to fetch new data or write the new HTML table
        next_update = min(self.next_update,eod,mid)
        # adjust to archive interval border
        if next_update%self.query_interval!=0:
            next_update += self.query_interval-next_update%self.query_interval
        # time to wait
        waiting = next_update-now
        if __name__ == '__main__':
            print('waiting_time()',waiting)
        return waiting

    def random_time(self, waiting):
        """ do a little bit of load balancing 
        
            let at least 60 seconds to ultimo to download and process
            data
        """
        if waiting<=60: return 0.1-waiting
        w = waiting-60
        return -random.random()*(60 if w>60 else w)-60


def is_provided(provided, model):
    if provided.lower()=='dwd':
        return DwdHealthThread.is_provided(model.lower())
    return False

def create_thread(thread_name,config_dict,archive_interval):
    """ create radar thread """
    prefix = config_dict.get('prefix','')
    provider = config_dict.get('provider')
    model = config_dict.get('model')
    if provider=='DWD' and DwdHealthThread.is_provided(model):
        conf_dict = weeutil.config.accumulateLeaves(config_dict)
        conf_dict['prefix'] = prefix
        conf_dict['model'] = model
        if weeutil.weeutil.to_bool(conf_dict.get('enable',True)):
            #loginf(conf_dict)
            thread = dict()
            thread['datasource'] = 'Health'+model
            thread['prefix'] = prefix
            thread['thread'] = DwdHealthThread(thread_name,conf_dict,archive_interval)
            thread['thread'].start()
            return thread
    return None


if __name__ == "__main__":

        print('Weatherservices Health start')
        conf = configobj.ConfigObj("health.conf")
        dwd = create_thread(conf['model'],conf,300)
        if not dwd:
            print('could not create thread')
        try:
            while True:
                time.sleep(300-time.time()%300+15)
                data, interval = dwd['thread'].get_data(time.time()-15)
                print(json.dumps(data,indent=4,ensure_ascii=False))
        except Exception as e:
            print('**MAIN**',e)
        except KeyboardInterrupt:
            print()
            print('**MAIN** CTRL-C pressed')
        dwd['thread'].shutDown()
        exit(0)
