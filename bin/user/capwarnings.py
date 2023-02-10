#!/usr/bin/python3
# Process warnings sent with CAP (Common Alerting Protocol)
# Copyright (C) 2023 Johanna Roedenbeck
# licensed under the terms of the General Public License (GPL) v3

from __future__ import absolute_import
from __future__ import print_function
from __future__ import with_statement

"""
    This script is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This script is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
"""

"""
    API
    ===
    
    CAPwarnings.PROVIDERS
    
        dict() of providers, where to find their configuration and
        which class to use for provider specific functions
        
    cap = CAPwarnings(config_dict, provider, verbose=False)
    
        config_dict
        
            configuration dict(), for example weewx.conf, see README.md
            for details
            
        provider
        
            name of the data provider to look up in CAPwarnings.PROVIDERS
            
        verbose
        
            extremly verbose logging (includes log_success=True and
            log_failure=True)
    
    wwarn = cap.get_warnings(lang='de', log_tags=False)
    
        receive CAP warning data from the provider and convert it to
        a Python dict()
        
        lang
        
            language code
            
        log_tags
        
            log tags while processing the XML data (for standalone
            usage only)
        
    cap.write_html(wwarn, dry_run=False)
    
        write HTML and JSON file(s) out of the dict() wwarn

        wwarn
        
            warnings dict(), received by get_warnings()
            
        dry_run
        
            if True, print result to screen instead of saving to files
            
    cap.cap.download_warncellids(target_path, dry_run)
    
        provider "DWD" only.
        
        get list of warncell IDs used by that provider and write it to
        file
        
        target_path
        
            where to write the file
            
        dry_run
        
            do not write to file but output to screen
    
    
    Standalone usage
    ================
    
    You can invoke this script standalone or by a wrapper or link called
    `cap-warnings`, `dwd-cap-warnings`, or `bbk-warnings`. Use `--help` 
    to show possible options.
    
    Invoking as `dwd-cap-warnings` includes the option `--provider=DWD`.
    
    Invoking as `bbk-warnings` includes the option `--provider=BBK`
    
            
    Common Alerting Protocol (CAP)
    ==============================
            
    Protocol description: http://docs.oasis-open.org/emergency/cap/v1.2/CAP-v1.2-os.pdf

Ein <alert>-Element DARF ein oder mehrere <info>-Elemente haben. Jedes <info>-
Element stellt eine Warnung in einer Sprache dar. Sind mehrere <info>-Elemente in
einem <alert>-Block enthalten, so MUSS jedes <info>-Element die gleiche Warnung
(die gleiche Information) in einer anderen Sprache darstellen. Jedes <info>-Element
DARF ein oder mehrere <area>-Elemente haben.

"""

import json
import time
import datetime
import configobj
import os.path
import requests
import csv
import io
import urllib.parse
from email.utils import formatdate
import html.parser
import zipfile
import sys

invoke_fn = os.path.basename(sys.argv[0])
standalone = ('cap-warnings','dwd-cap-warnings','bbk-warnings')

if __name__ == "__main__" or invoke_fn in standalone:

    import optparse
    sys.path.append('/usr/share/weewx')
    def loginf(x):
        print('INFO', x, file=sys.stderr)
    def logerr(x):
        print('ERROR', x, file=sys.stderr)
        
    def accumulateLeaves(x):
        y = dict()
        y.update({a:x.parent.parent[a] for a in x.parent.parent.scalars})
        y.update({a:x.parent[a] for a in x.parent.scalars})
        y.update({a:x[a] for a in x.scalars})
        return y

else:

    try:
        # Test for new-style weewx logging by trying to import weeutil.logger
        import weeutil.logger
        import logging
        log = logging.getLogger("user.DWD")

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
            syslog.syslog(level, 'user.DWD: %s' % msg)

        def logdbg(msg):
            logmsg(syslog.LOG_DEBUG, msg)

        def loginf(msg):
            logmsg(syslog.LOG_INFO, msg)

        def logerr(msg):
            logmsg(syslog.LOG_ERR, msg)
            
        from weeutil.weeutil import accumulateLeaves

try:
    import weewx
    from weewx.engine import StdService
    import weeutil.weeutil
    import weewx.accum
    import weewx.units
    import weewx.wxformulas
except ImportError:
    pass

def tobool(x):
    """ convert text to boolean
        Copyright (C) Tom Keffer
    """
    try:
        if x.lower() in ['true', 'yes', 'y']:
            return True
        elif x.lower() in ['false', 'no', 'n']:
            return False
    except AttributeError:
        pass
    try:
        return bool(int(x))
    except (ValueError, TypeError):
        pass
    raise ValueError("Unknown boolean specifier: '%s'." % x)


# https://www.xrepository.de/details/urn:de:bund:destatis:bevoelkerungsstatistik:schluessel:rs
# https://www.xrepository.de/api/xrepository/urn:de:bund:destatis:bevoelkerungsstatistik:schluessel:rs_2022-09-30/download/Regionalschl_ssel_2022-09-30.json

class Germany(object):

    # Amtlicher Gemeindeschluessel
    AGS_STATES = {
        '01':('SH','Schleswig-Holstein'),
        '02':('HH','Freie und Hansestadt Hamburg'),
        '03':('NS','Niedersachsen'),
        '04':('HB','Freie Hansestadt Bremen'),
        '05':('NRW','Nordrhein-Westfalen'),
        '06':('HE','Hessen'),
        '07':('RP','Rheinland-Pfalz'),
        '08':('BW','Baden-Württemberg'),
        '09':('BY','Freistaat Bayern'),
        '10':('SL','Saarland'),
        '11':('BB','Berlin'),
        '12':('BB','Brandenburg'),
        '13':('MV','Mecklenburg-Vorpommern'),
        '14':('SN','Freistaat Sachsen'),
        '15':('SA','Sachsen-Anhalt'),
        '16':('TH','Thüringen')
    }

    @staticmethod
    def compareARS(ars, pars):
        """ Is ars in pars? """
        if not pars: return True
        # remove '0' at the end of the string
        ars_str = ars.strip().rstrip('0')
        ars_len = len(ars_str)
        #print('QQQQQQQQQQ','ARS str',ars_str,'len',ars_len)
        # '000000000000' means 'whole country'
        if ars_len==0: return True
        # pars may be a list of ARS
        for ii in pars.split(','):
            # remove '0' at the end of the string
            vgl_str = ii.strip().rstrip('0')
            vgl_len = len(vgl_str)
            #print('QQQQQQQQQQ','ARS',ars_str,ars_len,'VGL',vgl_str,vgl_len,':',ars[0:min(vgl_len,ars_len)],'==',vgl_str[0:min(vgl_len,ars_len)])
            # 
            if vgl_len==0: return True
            #
            if ars[0:min(vgl_len,ars_len)]==vgl_str[0:min(vgl_len,ars_len)]: 
                return True
        return False
    


class CAP(object):

    NOWARNING = {
        'de': 'zur Zeit keine Warnungen',
        'en': 'no warnings at present',
        'fr': "pas d'alerte pour le moment"
    }

    # Codes from CAP

    SEVERITY = {
        'Minor':2,
        'Moderate':3,
        'Severe':4,
        'Extreme':5
    }
    
    def level_text(self, level, lang='de', isdwd=None):
        return None

    CATEGORY = {
        'Geo':{'de':'geophysikalisch','en':'geophysical'},
        'Met':{'de':'meteorologisch','en':'meteorological'},
        'Safety':{'de':'allgemeine Gefahren und öffentliche Sicherheit',
                'en':'general emergency and public safety'},
        'Security':{'de':'Gesetzesdurchsetzung, militärische, regionale und lokale/private Sicherheit',
                'en':'law enforcement, miltary, homeland and local/private security'},
        'Rescue':{'de':'Feuerbekämpfung und Sicherheit',
              'en':'fire suppression and rescue'},
        'Health':{'de':'Medizin und öffentliche Gesundheit',
              'en':'medical and public health'},
        'Env':{'de':'Umweltverschmutzung und andere Umweltgefahren',
           'en':'pollution and other environmental'},
        'Transport':{'de':'öffentlicher und privater Verkehr',
                 'en':'public and private transportation'},
        'Infra':{'de':'Infrastruktur', # z.B. Telekommunikation
             'en':'utility, telecommunication, other non-transport infrastructure'},
        'CBRNE':{'de':'chemische, biologische, radioaktive, nukleare oder explosive Bedrohung oder Attacke',
             'en':'chemical, biological, radiological, nuclear or high-yield exlosive threat or attack'},
        'Other':{'de':'andere Ereignisse','en':'other events'}
    }

    @staticmethod
    def get_category_name(category, lang='de'):
        """ long name of the alert category """
        try:
            return CAP.CATEGORY[category][lang.lower()]
        except LookupError:
            pass
        try:
            return CAP.CATEGORY[category]['en']
        except LookupError:
            pass
        if lang.lower()=='de': return 'unbekannt'
        return 'unknown'

    @staticmethod
    def mktime(timestring):
        """ convert CAP timestamp string to epoch time """
        if not timestring: return None
        ti = datetime.datetime.strptime(timestring,'%Y-%m-%dT%H:%M:%S%z')
        #print(ti)
        return int(ti.timestamp()*1000)
        
    def get_logo(self, sender):
        """ file name of the logo picture of the originator of the alert """
        return dict()
        
    def warn_icon_file(self, typ, level, eventcode):
        """ file name of the alert icon """
        return None

    def __init__(self, warn_dict, verbose=False):
        super(CAP,self).__init__()
        # logging configuration
        self.log_success = tobool(warn_dict.get('log_success',False))
        self.log_failure = tobool(warn_dict.get('log_failure',False))
        self.verbose = verbose
        if verbose:
            self.log_success = True
            self.log_failure = True
        # internal data to be initialized in the provider specific classes
        self.icon_base_url = None
        self.logo_base_url = None
        self.filter_area = None
        

    def wget(self, url, success_msg='successfully downloaded %s'):
        """ download from provider """
        headers={'User-Agent':'weewx-DWD'}
        reply = requests.get(url,headers=headers)

        if reply.status_code==200:
            if self.log_success or self.verbose:
                loginf(success_msg % reply.url)
            return reply.content
        else:
            if self.log_failure or self.verbose:
                loginf('error downloading %s: %s %s' % (reply.url,reply.status_code,reply.reason))
            return None

    def convert_xml(self, xmltext, log_tags=False):
        """ convert XML to dict """
        parser = CAPParser(log_tags)
        try:
            parser.feed(xmltext)
            cap_dict = parser.cap
        finally:
            parser.close()
        return cap_dict


    def _area_filter(self, info_dict):
        """ find out whether the given alert is valid for one of the areas 
            (cities, counties etc.) we are interested in
            
            As the providers provide that information in different ways, this
            function has to be defined in the provider specific classes.
        """
        raise NotImplementedError
        

    def process_alert(self, alert_dict, lang='de'):
        """ process alert 
        
            This includes converting the dict() to a less deeper one
            and augmenting it by icons and status texts.
        """
        lang = lang.lower()
        # <alert>
        # search the alert for area references we are interested in
        areas = []
        info_dict = dict()
        if isinstance(alert_dict, dict):
            #print('1')
            for lvl2 in alert_dict:
                #print('2',lvl2)
                if lvl2=='info':
                    # <info>
                    # There may be one or more <info> sections, one for 
                    # each language
                    #print('3')
                    try:
                        info_de = None
                        info_en = None
                        info_dict = None
                        # search the <info> section for the required language
                        for info in alert_dict[lvl2]:
                            try:
                                info_lang = info['language'][0:2].lower()
                            except LookupError:
                                info_lang = lang
                            #print('info_lang',info_lang,'lang',lang)
                            if info_lang==lang:
                                #print('4',json.dumps(info,indent=4))
                                info_dict = info
                            elif info_lang=='de':
                                info_de = info
                            elif info_lang=='en':
                                info_en = info
                        # If the required language is not available, try
                        # English and then german.
                        if not info_dict:
                            if info_en:
                                info_dict = info_en
                            elif info_de:
                                info_dict = info_de
                        if info_dict:
                            # search <info> section for <area> sections
                            ar = self._area_filter(info_dict)
                            if ar: areas.extend(ar)
                    except Exception as e:
                        logerr("%s %s" % (e.__class__.__name__,e))
                        pass
                else:
                    pass
        else:
            # items in <alert> that are not dicts
            pass
        # If the alert applies to areas we are interested in,
        # the variable areas contains the the area references. 
        # Otherwise it is an empty array.
        if areas and alert_dict.get('status','')!='Test':
            areas.sort(key=lambda x:x[0])
            altitude = (areas[0][2],areas[0][3])
            for ii in areas:
                if (ii[2],ii[3])!=altitude:
                    altitude = None
                    break
            alert = {
                        'identifier':alert_dict.get('identifier'),
                        'sender':alert_dict.get('sender'),
                        'sent':CAP.mktime(alert_dict.get('sent')),
                        'status':alert_dict.get('status'),
                        'msgType':alert_dict.get('msgtype'),
                        'source':alert_dict.get('source'),
                        'scope':alert_dict.get('scope'),
                        'regionName':[ii[0] for ii in areas],
                        'altitudeRange':altitude,
                        'areas':areas,
                        'description':info_dict.get('description',''),
                        'event':info_dict.get('event',''),
                        'headline':info_dict.get('headline',''),
                        'instruction':info_dict.get('instruction',''),
                        'category':info_dict.get('category'),
                        'categoryName':[CAP.get_category_name(ii,lang) for ii in info_dict.get('category',[])],
                        'responseType':info_dict.get('responsetype'),
                        'urgency':info_dict.get('urgency'),
                        'severity':info_dict.get('severity')
            }
            # release time
            alert['released'] = CAP.mktime(info_dict.get('effective',alert_dict.get('effective',alert_dict.get('sent'))))
            # start time
            alert['start'] = CAP.mktime(info_dict.get('onset',alert_dict.get('onset',alert_dict.get('sent'))))
            # end time
            alert['end'] = CAP.mktime(info_dict.get('expires',alert_dict.get('expires')))
            # <eventCode>
            for ii in info_dict.get('eventcode',[]):
                try:
                    alert['eventCode-'+ii['valuename']] = ii['value']
                except Exception:
                    pass
            # <parameter>
            alert['parameter'] = dict()
            for ii in info_dict.get('parameter',[]):
                try:
                    alert['parameter'][ii['valuename']] = ii['value']
                except Exception:
                    pass
            # <code>
            for ii in alert_dict.get('code',[]):
                        if ii=='SILENT_UPDATE':
                            alert['SILENT_UPDATE'] = True
                        if ii=='PARTIAL_CLEAR':
                            alert['PARTIAL_CLEAR'] = True
                        if ii[:3]=='id:':
                            alert['msgid'] = ii
            # severity level
            if info_dict.get('event','')[:16]=='VORABINFORMATION':
                alert['level'] = 1
            else:
                alert['level'] = CAP.SEVERITY.get(info_dict.get('severity'),0)
            alert["level_text"] = self.level_text(alert['level'],lang=lang)
            # event type
            alert['type'] = DWD.get_eventtype_from_cap(
                                      info_dict.get('event'),
                                      alert.get('eventCode-II'))
            # warn icon
            try:
                alert['icon'] = (
                    self.icon_base_url+'/'+
                    self.warn_icon_file(
                        alert['type'],
                        alert['level'],
                        alert_dict.get('BBK_eventcode')
                    )
                )
                if alert['icon']=='https://warnung.bund.de/api31/appdata/gsb/eventCodes/bbkicon.png':
                    if alert['sender']=='CAP@hochwasserzentralen.de':
                        alert['icon'] = 'https://warnung.bund.de/assets/icons/report_hochwasser.svg'
                    else:
                        alert['icon'] = 'https://warnung.bund.de/assets/icons/report_mowas.svg'
            except Exception:
                pass
            # sender
            if 'sender' in alert:
                logo = self.get_logo(alert['sender'])
                if logo:
                    if alert['sender']=='CAP@hochwasserzentralen.de' and self.logo_base_url=='https://warnung.bund.de/api31/appdata/gsb/logos':
                        alert['sender_logo'] = 'https://www.hochwasserzentralen.de/images/logo_lhp3.png'
                    elif 'image' in logo and self.logo_base_url:
                        alert['sender_logo'] = self.logo_base_url+'/'+logo['image']
                    if 'name' in logo:
                        alert['sender_name'] = logo['name']

            if 'capwarnings-downloaded' in alert_dict:
                alert['capwarnings_downloaded'] = alert_dict['capwarnings-downloaded']
            
            return alert
        return None


    def warnings(self, lang='de', log_tags=False):
        raise NotImplementedError
    
    
    def get_warnings(self, lang='de', log_tags=False):
        """  """
        if self.verbose:
            print('-- get_warnings -------------------------------')
        # initialize dict for all regions to collect warnings for
        wwarn = {self.filter_area[i]:dict() for i in self.filter_area}
        for cap in self.warnings(lang,log_tags):
            alert = self.process_alert(cap,lang)
            if alert:
                areas = alert['areas']
                #print('++++++++++')
                #print(areas)
                #print('++++++++++')
                _areas = dict()
                for ii in areas: _areas[ii[-1]] = True
                _region = ', '.join([ii[0] for ii in areas])
                for ii in _areas:
                    if _region not in wwarn[ii]:
                        wwarn[ii][_region] = []
                    wwarn[ii][_region].append(alert)
                    #print(json.dumps(alert,indent=4,ensure_ascii=False))
        # The sub-dictionary for regions was include for the purpose
        # of sorting, only. Now it is removed to get the the right
        # data structure.
        for __ww in wwarn:
            x = []
            for ii in wwarn[__ww]: x.extend(wwarn[__ww][ii])
            wwarn[__ww] = x

        #if self.verbose:
        #    loginf('file %s processed' % filename)
        #print(json.dumps(wwarn,indent=4,ensure_ascii=False))
        return wwarn, lang

    def write_html(self, wwarn, target_path, dryrun):
        """ prototype function """
        raise NotImplementedError
    

##############################################################################
#   DWD specific constants and functions                                     #
##############################################################################

class DWD(CAP):

    DEFAULT_DWD_WARNCELLID_URL = "https://www.dwd.de/DE/leistungen/opendata/help/warnungen/cap_warncellids_csv.csv?__blob=publicationFile&v=3"
    DEFAULT_DWD_CAP_URL = "https://opendata.dwd.de/weather/alerts/cap"

    # Der DWD verwendet ganz offensichtlich nicht die nach ISO genormten
    # Abkuerzungen fuer Bundeslaender.
    DWD_COPY = {
        'SN':'https://www.dwd.de/DE/wetter/warnungen_aktuell/warnlagebericht/sachsen/warnlage_sac_node.html',
        'TH':'https://www.dwd.de/DE/wetter/warnungen_aktuell/warnlagebericht/thueringen/warnlage_thu_node.html',
        'SA':'https://www.dwd.de/DE/wetter/warnungen_aktuell/warnlagebericht/sachen_anhalt/warnlage_saa_node.html',
        'BB':'https://www.dwd.de/DE/wetter/warnungen_aktuell/warnlagebericht/berlin_brandenburg/warnlage_bb_node.html',
        'MV':'https://www.dwd.de/DE/wetter/warnungen_aktuell/warnlagebericht/mecklenburg_vorpommern/warnlage_mv_node.html',
        'NS':'https://www.dwd.de/DE/wetter/warnungen_aktuell/warnlagebericht/niedersachsen_bremen/warnlage_nds_node.html',
        'HB':'https://www.dwd.de/DE/wetter/warnungen_aktuell/warnlagebericht/niedersachsen_bremen/warnlage_nds_node.html',
        'HE':'https://www.dwd.de/DE/wetter/warnungen_aktuell/warnlagebericht/hessen/warnlage_hes_node.html',
        'NRW':'https://www.dwd.de/DE/wetter/warnungen_aktuell/warnlagebericht/nordrhein_westfalen/warnlage_nrw_node.html',
        'BY':'https://www.dwd.de/DE/wetter/warnungen_aktuell/warnlagebericht/bayern/warnlage_bay_node.html',
        'SH':'https://www.dwd.de/DE/wetter/warnungen_aktuell/warnlagebericht/schleswig_holstein_hamburg/warnlage_shh_node.html',
        'HH':'https://www.dwd.de/DE/wetter/warnungen_aktuell/warnlagebericht/schleswig_holstein_hamburg/warnlage_shh_node.html',
        'RP':'https://www.dwd.de/DE/wetter/warnungen_aktuell/warnlagebericht/rheinland-pfalz_saarland/warnlage_rps_node.html',
        'SL':'https://www.dwd.de/DE/wetter/warnungen_aktuell/warnlagebericht/rheinland-pfalz_saarland/warnlage_rps_node.html',
        'BW':'https://www.dwd.de/DE/wetter/warnungen_aktuell/warnlagebericht/baden-wuerttemberg/warnlage_baw_node.html'
    }

    # Codes from warnings.json

    DWD_LEVEL = (
        'keine Warnung',     # 0 no warning
        'Vorinformation',    # 1 preliminary info
        'Wetterwarnung',     # 2 minor
        'markantes Wetter',  # 3 moderate
        'Unwetterwarnung',   # 4 severe
        'extremes Unwetter'  # 5 extreme
    )

    # Namensbestandteile der Warn-Icons
    DWD_WARNING_TYPE = (
        'gewitter',          # 0 thunderstorm
        'wind',              # 1 wind/storm
        'regen',             # 2 rain
        'schnee',            # 3 snow
        'nebel',             # 4 fog
        'frost',             # 5 frost
        'eis',               # 6 ice
        'tau',               # 7 thawing
        'hitze',             # 8 heat
        'uv'                 # 9 uv warning
    )
    
    @staticmethod
    def dwd_warn_icon_file(type, level):
        if type is None: return None
        if type==8 or type==9:
            return "warn_icons_%s.png" % DWD.DWD_WARNING_TYPE[type]
        if level==1:
            return "warn_icons_%s_pre.png" % DWD.DWD_WARNING_TYPE[type]
        if level<2 or level>5: return None
        return "warn_icons_%s_%s.png" % (DWD.DWD_WARNING_TYPE[type],level-1)

    def warn_icon_file(self, type, level, eventcode):
        return DWD.dwd_warn_icon_file(type, level)
        
    @staticmethod
    def dwd_level_text(level):
        try:
            return DWD.DWD_LEVEL[level]
        except IndexError:
            if level==10: return 'Hitzewarnung'
        return None

    def level_text(self, level, lang='de', isdwd=True):
        return DWD.dwd_level_text(level)
    
    def get_logo(self, sender):
        return {
            #'image':'...',
            'name':'DWD'
        }
    
    # Codes from CAP

    CAP_II_CAPTION = (
        'Warnungen',
        'Küsten-Warnungen',
        'Hochsee-Warnungen',
        'Medizin-Meteorologische Warnungen',
        'Vorabinformationen Unwetter'
    )
    
    CAP_II = (
        #II,type,c,name
        # Küsten-Warnungen
        (11,1,1,'Böen'),
        (12,1,1,'Wind'),
        (13,1,1,'Sturm'),
        # Hochsee-Warnungen
        (14,1,2,'Starkwind'),
        (15,1,2,'Sturm'),
        (16,1,2,'schwerer Sturm'),
        # Warnungen
        (22,5,0,'Frost'),
        (24,6,0,'Glätte'),
        (31,0,0,'Gewitter'),
        (33,0,0,'starkes Gewitter'),
        (34,0,0,'starkes Gewitter'),
        (36,0,0,'starkes Gewitter'),
        (38,0,0,'starkes Gewitter'),
        (40,0,0,'schweres Gewitter mit Orkanböen'),
        (41,0,0,'schweres Gewitter mit extremen Orkanböen'),
        (42,0,0,'schweres Gewitter mit heftigem Starkregen'),
        (44,0,0,'schweres Gewitter mit Orkanböen und heftigem Starkregen'),
        (45,0,0,'schweres Gewitter mit extremen Orkanböen und heftigem Starkregen'),
        (46,0,0,'schweres Gewitter mit heftigem Starkregen und Hagel'),
        (48,0,0,'schweres Gewitter mit Orkanböen, heftigem Starkregen und Hagel'),
        (49,0,0,'schweres Gewitter mit extremen Orkanböen, heftigem Starkregen und Hagel'),
        (51,1,0,'Windböen'),
        (52,1,0,'Sturmböen'),
        (53,1,0,'schwere Sturmböen'),
        (54,1,0,'orkanartige Böen'),
        (55,1,0,'Orkanböen'),
        (56,1,0,'extreme Orkanböen'),
        (57,1,0,'Starkwind'),
        (58,1,0,'Sturm'),
        (59,4,0,'Nebel'),
        (61,2,0,'Starkregen'),
        (62,2,0,'heftiger Starkregen'),
        (63,2,0,'Dauerregen'),
        (64,2,0,'ergiebiger Dauerregen'),
        (65,2,0,'extrem ergiebiger Dauerregen'),
        (66,2,0,'extrem heftiger Starkregen'),
        (70,3,0,'leichter Schneefall'),
        (71,3,0,'Schneefall'),
        (72,3,0,'starker Schneefall'),
        (73,3,0,'extrem starker Schneefall'),
        (74,3,0,'Schneeverwehung'),
        (75,3,0,'starke Scheeverwehung'),
        (76,3,0,'extrem starke Schneeverwehung'),
        (79,5,0,'Leiterseilschwingungen'),
        (82,5,0,'strenger Frost'),
        (84,6,0,'Glätte'),
        (85,6,0,'Glatteis'),
        (87,6,0,'Glatteis'),
        (88,7,0,'Tauwetter'),
        (89,7,0,'starkes Tauwetter'),
        (90,0,0,'Gewitter'),
        (91,0,0,'starkes Gewitter'),
        (92,0,0,'schweres Gewitter'),
        (93,0,0,'extremes Gewitter'),
        (95,0,0,'schweres Gewitter mit extremem, heftigem Starkregen und Hagel'),
        (96,0,0,'extremes Gewitter mit Orkanböen, extrem heftigem Starkregen und Hagel'),
        (98,None,0,'Test-Warnung'),
        (99,None,0,'Test-Unwetterwarnung'),
        # Medizin-Meteorologische Warnungen
        (246,9,3,'UV-Index'),
        (247,8,3,'starke Hitze'),
        (248,8,3,'extreme Hitze'),
        # Vorabinformationen Unwetter
        (40,0,4,'Vorabinformation schweres Gewitter'),
        (55,1,4,'Vorabinformation Orkanböen'),
        (65,2,4,'Vorabinformation heftiger/ergiebiger Regen'),
        (75,3,4,'Vorabinformation starker Schneefall/Schneeverwehung'),
        (85,6,4,'Vorabinformation Glatteis'),
        (89,7,4,'Vorabinformation starkes Tauwetter'),
        (99,None,4,'Test-Vorabinformation Unwetter')
    )

    CAP_II_TYPE = { ii[0]:ii[1] for ii in CAP_II if ii[2]!=4 and ii[1] is not None }

    CAP_EVENT = {
        'FROST':(5,22),
        'GLÄTTE':(6,24),
        'GLATTEIS':(6,None),
        'GEWITTER':(0,31),
        'WINDBÖEN':(1,51),
        # 'STURM':(1,58),
        'NEBEL':(4,59),
        'TEST-WARNUNG':(None,98),
        'TEST-UNWETTERWARNUNG':(None,99),
        # Vorabinformation Unwetter
        'VORABINFORMATION SCHWERES GEWITTER':(0,40),
        'VORABINFORMATION ORKANBÖEN':(1,55),
        'VORABINFORMATION HEFTIGER / ERGIEBIGER REGEN':(2,65),
        'VORABINFORMATION STARKER SCHNEEFALL / SCHNEEVERWEHUNG':(3,75),
        'VORABINFORMATION GLATTEIS':(6,85),
        'VORABINFORMATION STARKES TAUWETTER':(7,89),
        'TEST-VORABINFORMATION UNWETTER':(None,99),
        # Küsten-Warnungen
        'BÖEN':(1,11),
        'WIND':(1,12),
        'STURM':(1,13),
        # Medizin-Meteorologische-Warnungen
        'UV-INDEX':(9,246),
        'STARKE HITZE':(8,247),
        'EXTREME HITZE':(8,248)
    }

    # räumliche Auflösung
    CAP_URL_RES = {
        'county': 'DISTRICT',
        'city': 'COMMUNEUNION',
        'Landkreis': 'DISTRICT',
        'Gemeinde': 'COMMUNEUNION'}

    # Aktualisierungsstrategie und Aktualisierungsregeln
    # update strategy and update rules
    CAP_URL_UPDATE = {
        'cell': {
            'dwd': 'DWD',
            'neutral': 'CELLS'},
        'event': {
            'neutral': 'EVENT',
            None: 'EVENT'}
    }

    # Kompletter Warnstatus oder Differenzmeldungen
    # status or difference messages
    CAP_URL_STATUS_DIFFERENCE = {
        False: 'STAT',
        True: 'DIFF'
    }

    @staticmethod
    def get_eventtype_from_cap(capevent,eventtypeii):
        """ get JSON event type from CAP event and ii """
        try:
            if capevent in DWD.CAP_EVENT: return DWD.CAP_EVENT[capevent][0]
            if 'GEWITTER' in capevent: return 0
            if 'STURM' in capevent: return 1
            if 'REGEN' in capevent: return 2
            if 'SCHNEEFALL' in capevent: return 3
            if 'FROST' in capevent: return 5
            if 'TAUWETTER' in capevent: return 7
            eventtypeii = int(eventtypeii)
            if eventtypeii in DWD.CAP_II_TYPE: return DWD.CAP_II_TYPE[eventtypeii]
        except Exception:
            pass
        return None

    @staticmethod
    def get_cap_url(resolution, strategy, rule, diff):
        """ compose URL for CAP files """
        try:
            return DWD.DEFAULT_DWD_CAP_URL+'/'+DWD.CAP_URL_RES[resolution]+'_'+DWD.CAP_URL_UPDATE[strategy][rule]+'_'+DWD.CAP_URL_STATUS_DIFFERENCE[diff]
        except Exception as e:
            logerr(e)
            return None


    def __init__(self, warn_dict, verbose=False):
        super(DWD,self).__init__(warn_dict, verbose)
        # warn icons
        if 'dwd_icons' in warn_dict:
            self.icon_base_url = warn_dict['dwd_icons']
        else:
            self.icon_base_url = warn_dict['icons']
        # Bundeslaender und Landkreise, fuer die Warndaten
        # bereitgestellt werden sollen, aus weewx.conf lesen
        self.resolution = warn_dict.get('dwd_resolution','city')
        self.states = warn_dict.get('states',[])
        if not isinstance(self.states,list): self.states=[self.states]
        _area = DWD.CAP_URL_RES.get(self.resolution,'COMMUNEUNION' if 'cities' in warn_dict else 'DISTRICT')
        if _area=='DISTRICT':
            self.filter_area = warn_dict.get('counties',dict())
        elif _area=='COMMUNEUNION':
            self.filter_area = warn_dict.get('cities',dict())
        # source urls
        self.dwd_status_url = warn_dict.get('dwd_status_url',DWD.get_cap_url(self.resolution,'cell','neutral',False))
        self.dwd_diff_url = warn_dict.get('dwd_diff_url',DWD.get_cap_url(self.resolution,'cell','neutral',True))
        self.diff = False


    def dir(self, diff, lang='de'):
    
        if diff:
            url = self.dwd_diff_url
        else:
            url = self.dwd_status_url
   
        if self.verbose:
            loginf('about to download zip file list from %s' % url)
            
        reply = self.wget(url,'zip file list from %s successfully downloaded')
       
        if reply:
            reply = reply.decode(encoding='utf-8')
            parser = CapDirParser(lang)
            parser.feed(reply)
            return parser.get_files()
        else:
            return None
            

    def download_zip(self, diff, file_name):
    
        if diff:
            url = self.dwd_diff_url
        else:
            url = self.dwd_status_url

        url = url+'/'+file_name

        if self.verbose:
            loginf('about to download %s' % url)
            
        reply = self.wget(url)
        
        if reply:
            return zipfile.ZipFile(io.BytesIO(reply),'r')
        else:
            return None


    def warnings(self, lang='de',log_tags=False):
        """ DWD """
        diff = self.diff
        filename = self.dir(diff,lang)[-1]
        if self.verbose:
            loginf('processing file %s' % filename)
        # initialize dict for all regions to collect warnings for
        wwarn={self.filter_area[i]:dict() for i in self.filter_area}
        # download CAP file 
        zz = self.download_zip(diff,filename)
        ti = time.time()
        # process alerts included in the CAP file
        for name in zz.namelist():
            # read file out of zip file and convert to dict
            xmltext = zz.read(name).decode(encoding='utf-8')
            cap_dict = self.convert_xml(xmltext,log_tags)
            for warn in cap_dict:
                cap_dict[warn]['capwarnings-downloaded'] = ti
                yield cap_dict[warn]
        
        
    def _area_filter(self, info_dict):
        """ find out whether the given alert is valid for one of the areas 
            (cities, counties etc.) we are interested in
        """
        reply = []
        for tag in info_dict:
            val = info_dict[tag]
            try:
                if tag=='area':
                  for ii in val:
                    try:
                        if ii['areadesc'] in self.filter_area:
                            wcid = None
                            for jj in ii.get('geocode',[]):
                                if jj.get('valuename','')=='WARNCELLID':
                                    wcid = jj.get('value')
                            try:
                                ags = wcid[-8:]
                                state = Germany.AGS_STATES[ags[:2]]
                            except Exception:
                                state = [None,None]
                            try:
                                alt = int(float(ii['altitude'])*0.3048)
                            except Exception:
                                alt = None
                            try:
                                cie = int(float(ii['ceiling'])*0.3048)
                            except Exception:
                                cie = None
                            reply.append((ii['areadesc'],
                                          wcid,alt,cie,
                                          state[0],state[1],
                                          self.filter_area[ii['areadesc']]))
                    except Exception as e:
                        if self.verbose:
                            logerr(e)
            except Exception as e:
                if self.verbose:
                    logerr(e)
        return reply


    def write_html(self, wwarn, target_path, dryrun):
        lang = wwarn[1]
        wwarn = wwarn[0]
        # loop over all target file names
        for __ww in wwarn:
            s = ""
            stateShort = ""
            r = None
            for idx,val in enumerate(wwarn[__ww]):
                
                # get the state (Bundesland) out of the AGS code
                try:
                    _states = list({(i[4],i[5]) for i in val['areas'] if i[-1]==__ww})
                    if len(_states)!=1: raise Exception
                    stateShort = _states[0][0]
                    val['stateShort'] = stateShort
                    val['state'] = _states[0][1]
                except Exception:
                    stateShort = None

                # list of warning regions that alert applies to
                _region = ', '.join([i[0] for i in val['areas'] if i[-1]==__ww])
                _region = _region.replace('Stadt ','').replace('Gemeinde ','')
                val['regionName'] = _region
                # if a new region starts, set a caption
                if r is None or r!=_region:
                    r = _region
                    s+='<p style="margin-top:5px"><strong>%s</strong></p>\n' % r
                
                # alert message 
                s+='<table style="vertical-align:middle"><tr style="vertical-align:middle">\n'
                if val.get('icon'):
                    s+='<td style="width:60px"><img src="%s" alt="%s"/></td>\n' % (val['icon'],val['event'])
                __size=110 if int(val['level'])>2 else 100
                s+='<td><p style="font-size:%i%%;margin-bottom:0">%s</p>\n' % (__size,val['headline'])
                s='%s<p style="font-size:80%%">gültig vom %s bis %s\n' % (s,time.strftime("%d.%m. %H:%M",time.localtime(val['start']/1000)),time.strftime("%d.%m. %H:%M",time.localtime(val['end']/1000)))
                
                if val.get('altitudeRange'):
                    altitude = val['altitudeRange']
                    if altitude[0]>0 and altitude[1]>=3000:
                        s += '<br />für Höhen ab %s m\n' % altitude[0]
                    elif altitude[0]<=0 and altitude[1]<3000:
                        s += '<br />für Höhen bis %s m\n' % altitude[1]
                    elif altitude[0]>0 and altitude[1]<3000:
                        s += '<br />für Höhen von %s m bis %s m\n' % altitude

                s+='</p></td>\n</tr></table>\n'

                if val.get('description'):
                    s+="<p>%s</p>\n" % val['description']
                if val.get('instruction'):
                    s+="<p>%s</p>\n" % val['instruction']

                s += '<p style="font-size:40%%">%s &ndash; %s &emsp;&ndash;&emsp; %s &ndash; %s &emsp;&ndash;&emsp; II=%s &ndash; %s</p>' % (val['type'],val['event'],val['level'],val['level_text'],val.get('eventCode-II',''),val.get('eventCode-GROUP',''))

            ti = time.localtime(wwarn[__ww][0]['capwarnings_downloaded'] if wwarn[__ww] else time.time())
            if s:
                s += '<p style="font-size:80%%">Quelle: <a href="%s" target="_blank">DWD</a> | Abgerufen am %s</p>\n' % (DWD.DWD_COPY.get(stateShort,"https://www.wettergefahren.de"),time.strftime('%d.%m.%Y %H:%M',ti))
            else:
                s = '<p>%s</p>' % CAP.NOWARNING.get(lang,CAP.NOWARNING['en'])
                s += '<p style="font-size:80%%">Zuletzt beim <a href="%s" target="_blank">DWD</a> abgerufen am %s</p>\n' % (DWD.DWD_COPY.get(stateShort,"https://www.wettergefahren.de"),time.strftime('%d.%m.%Y %H:%M',ti))
            
            if dryrun:
                print("########################################")
                print("-- HTML -- warn-%s.inc ------------------------------"%__ww)
                print(s)
                print("-- JSON -- warn-%s.json -----------------------------"%__ww)
                print(json.dumps(wwarn[__ww],indent=4,ensure_ascii=False))
            else:
                with open("%s/warn-%s.inc" % (target_path,__ww),"w") as file:
                    file.write(s)
                with open("%s/warn-%s.json" % (target_path,__ww),"w") as file:
                    json.dump(wwarn[__ww],file,indent=4)


    def download_warncellids(self, target_path, dryrun=False):
    
        # Path to store the file
        fn = os.path.join(target_path,'warncellids.csv')

        if os.path.exists(fn):
            mtime = os.path.getmtime(fn)
            mtime_str = formatdate(mtime,False,True)
        else:
            mtime = 0
            mtime_str = None
        if self.verbose:
            loginf('warncellids.csv mtime %s %s' % (mtime,mtime_str))
        
        # Without specifying a user agent the server sends the error
        # message 403
        headers={'User-Agent':'weewx-DWD'}
        # If the file is not changed we need not download it again
        if mtime_str: headers['If-Modified-Since'] = mtime_str

        reply = requests.get(DWD.DEFAULT_DWD_WARNCELLID_URL,headers=headers)
        if self.verbose:
            loginf('warncellids URL %s' % reply.url)
        
        if reply.status_code==200:
            if self.log_success or self.verbose:
                loginf('warncellids successfully downloaded')
            if dryrun:
                print(reply.text)
            else:
                with open(fn,'w',encoding='utf-8') as f:
                    f.write(reply.text)
            
        elif reply.status_code==304:
            if self.log_success or self.verbose:
                loginf('warncellids.csv is already up to date')
        else:
            if self.log_failure or self.verbose:
                logerr('error downloading warncellids: %s %s' % (reply.status_code,reply.reason))

        if not dryrun:
            with open(fn,'r',encoding='utf-8') as f:
                f.read(3)
                wcids = csv.DictReader(f,delimiter=';')
                print(wcids)
                #for i in wcids: print(i)


##############################################################################
#   BBK specific constants and functions                                     #
##############################################################################

# Source: https://nina.api.bund.dev
# Protocol description: http://docs.oasis-open.org/emergency/cap/v1.2/CAP-v1.2-os.pdf

class BBK(CAP):

    DEFAULT_BBK_URL = "https://warnung.bund.de/api31"

    WARNING_SOURCES = (
        'katwarn',
        'biwapp',
        'mowas',
        'dwd',
        'lhp',
        'police'
    )
    
    BBK_LEVEL = {
        'de': (
            'keine Warnung',     # 0 no warning
            'Vorinformation',    # 1 preliminary info
            'leicht',            # 2 minor
            'mittel',            # 3 moderate
            'schwer',            # 4 severe
            'extrem'             # 5 extreme
        ),
        'en': (
            'no warning',        # 0 no warning
            'preliminary info',  # 1 preliminary info
            'minor',             # 2 minor
            'moderate',          # 3 moderate
            'severe',            # 4 severe
            'extreme'            # 5 extreme
        )
    }

    
    def level_text(self, level, lang='de', isdwd=False):
        try:
            if lang not in BBK.BBK_LEVEL: lang='en'
            if isdwd: return DWD.dwd_level_text(level)
            return BBK.BBK_LEVEL[lang][level]
        except LookupError:
            if level==10: return 'Hitzewarnung'
        return None

    def get_eventtype(self, evt, ii):
        return '*'
        
    def get_logo(self, sender):
        return self.logos.get(sender)
    
    def warn_icon_file(self, type, level, eventcode):
        if eventcode:
            return self.eventicons.get(eventcode,'unknown.png')
        else:
            return 'bbkicon.png'
    
    def __init__(self, warn_dict, verbose=False):
        super(BBK,self).__init__(warn_dict,verbose)
        self.bbk_url = BBK.DEFAULT_BBK_URL
        # warn icons
        if 'bbk_icons' in warn_dict:
            self.icon_base_url = warn_dict['bbk_icons']
        else:
            self.icon_base_url = warn_dict.get('icons',self.bbk_url+'/appdata/gsb/eventCodes')
        if 'bbk_logos' in warn_dict:
            self.logo_base_url = warn_dict['bbk_logos']
        else:
            self.logo_base_url = warn_dict.get('logos',self.bbk_url+'/appdata/gsb/logos')
        self.eventicons = self.get_eventcodes()
        self.logos = self.get_logos()
        # list of counties to get warnings for
        self.filter_area = warn_dict.get('counties',configobj.ConfigObj())
        for section in warn_dict.sections:
            if section not in ('counties','cities'):
                sec_dict = warn_dict[section]
                if sec_dict.get('provider','------').upper()=='BBK':
                    self.filter_area[sec_dict.get('county',section)] = sec_dict.get('file',section)
        # include DWD warnings (default: no)
        self.include_dwd = tobool(warn_dict.get('bbk_include_dwd',False))


    def wget(self, url, success_msg='successfully downloaded %s'):
        """ get JSON data from provider and convert to dict() """
        reply = super(BBK,self).wget(url)
        if reply is None: return None
        return json.loads(reply)
        
        
    def get_logos(self):
        """ get the list of sender logos """
        url = self.bbk_url + '/appdata/gsb/logos/logos.json'
        logos = self.wget(url)
        return {logo['senderId']:logo for logo in logos['logos']}
    
    
    def get_eventcodes(self):
        """ get the list of event codes """
        url = self.bbk_url + '/appdata/gsb/eventCodes/eventCodes.json'
        evcs = self.wget(url)
        return {evc['eventCode']:evc['imageUrl'] for evc in evcs['eventCodes']}
    

    def get_list(self, ars):
        """ get list of active warnings for county ars """
        if ars in BBK.WARNING_SOURCES:
            url = self.bbk_url + '/' + ars + '/mapData.json'
        else:
            url = self.bbk_url + '/dashboard/' + str(ars)[0:5] + '0000000.json'
        return self.wget(url)


    def get_warning(self, id):
        """ get warning data of warning id """    
        url = self.bbk_url + '/warnings/' + id +'.json'
        return self.wget(url)
        
        
    def warnings(self, lang='de', log_tags=False):
        """ alerts of BBK """
        # list of the counties we are interested in
        arss = self.filter_area
        # dict() of alert IDs with a list of counties that alert is valid for
        areas = dict()
        # go through all counties (or dashboard regions)
        for ars in arss:
            if self.verbose and __name__ == "__main__":
                print("++ dashboard data ++++++++++++++++++++++++++++++++++++++")
                
            # get the list of actual alerts for the county specified by the
            # Regionalschlüssel ars
            warns = self.get_list(ars)
            
            if self.verbose:
                loginf("Regionalschlüssel ARS %s, %s Einträge" % (ars,len(warns)))
                
            if warns:
                # if there are actual alerts remember them in areas
                for warn in warns:

                    if self.verbose:
                        loginf("Warn ID: %s" % warn.get('id'))
                        loginf(warn)
                        
                    warn['BBK_ARS'] = ars
                    warn['output_region'] = arss[ars]
                    warn['BBK_eventcode'] = warn.get('payload',dict()).get('data',dict()).get('transKeys',dict()).get('event')
                    # structure of warn:
                    # {
                    #   'id': message ID
                    #   'payload': {
                    #     ...
                    #     'data': {
                    #       ...
                    #       'transKeys': {
                    #         'event': BBK event code
                    #       }
                    #     }
                    #   }
                    #   'i18nTitle': {
                    #     language code: message title
                    #   }
                    #   'sent': ISO timestamp
                    #   'onset': ISO timestamp (optional)
                    #   'expires': ISO timestamp (optional)
                    #   'effective': ISO timestamp (optional)
                    #   'BBK_ARS': Regionalschlüssel
                    #   'output_region': target file mark
                    # }
                    if warn['id'] not in areas:
                        areas[warn['id']] = []
                    areas[warn['id']].append(warn)
        if self.verbose:
            print('BBK.warnings() areas',[ id for id in areas])
            for id in areas:
                print('BBK.warnings() areas[]',id,[ii['id'] for ii in areas[id]])
        # go through messages
        for id in areas:
            # download warning
            alert = self.get_warning(id)
            ti = time.time()
            if self.verbose:
                print('BBK.warnings() get_warning(',id,')')
            # 'info' is an array of different language versions of the alert
            # add the list of areas to each of them
            for ii,__ in enumerate(alert['info']):
                alert['info'][ii]['BBK_areas'] = areas[id]
            # The eventcode is the same for all elements of areas[id]
            alert['BBK_eventcode'] = areas[id][0].get('payload',dict()).get('data',dict()).get('transKeys',dict()).get('event')
            
            # "opendata@dwd.de"
            if alert.get('sender','')!="opendata@dwd.de" or self.include_dwd:
                alert['capwarnings-downloaded'] = ti
                yield alert
                    
                        
                
    def _area_filter(self, info_dict):
        """ find out whether the given alert is valid for one of the areas 
            (cities, counties etc.) we are interested in
        
            BBK 
        """
        x = []
        areaDesc = ''
        warnverwaltungsbereiche = None
        for tag in info_dict:
            val = info_dict[tag]
            # The only parameter we are interested in is 
            # 'warnVerwaltungsbereiche'. Remember the value.
            if tag=='parameter':
                for ii in val:
                    vn = None
                    vl = None
                    for jj in ii:
                        if jj.lower()=='valuename':
                            vn = ii[jj]
                        elif jj.lower()=='value':
                            vl = ii[jj]
                    if vn and vn.lower()=='warnverwaltungsbereiche':
                        warnverwaltungsbereiche = vl
                        break
            # While in DWD warnings 'area' contains detailed information,
            # this is not the case for BBK alerts. There is a general
            # description of the region available only, and it is in
            # human readable form. There is at most one element in 'area' only.
            if tag=='area':
                for jj in val:
                    areaDesc = jj.get('areaDesc',areaDesc)
            # 'BBK_areas' is a list of all dashboard regions (counties)
            # that refer to this alert.
            if tag=='BBK_areas':
                for ii in val:
                  # 'ii' is one of the regions with one Regionalschlüssel
                  ars = ii['BBK_ARS']
                  if Germany.compareARS(ars,warnverwaltungsbereiche):
                      try:
                          bundesland = Germany.AGS_STATES[ars[0:2]]
                      except (LookupError,TypeError):
                          bundesland = ('','')
                      # There are no altitudes available from BBK, so use
                      # defaults.
                      x.append((areaDesc,ars,0,3000,bundesland[0],bundesland[1],ii['output_region']))
        return x


    def write_html(self, wwarn, target_path, dryrun):
        """ BBK """
        lang = wwarn[1]
        wwarn = wwarn[0]
        for __ww in wwarn:
            s = ""
            r = None
            for idx,val in enumerate(wwarn[__ww]):
                _region = ', '.join([i[0] for i in val['areas'] if i[-1]==__ww])
                _region = _region.replace('Stadt ','').replace('Gemeinde ','')
                val['regionName'] = _region
                if r is None or r!=_region:
                    r = _region
                    s+='<p style="margin-top:5px"><strong>%s</strong></p>\n' % r
                
                # alert message 
                s+='<table style="vertical-align:middle"><tr style="vertical-align:middle">\n'
                if val.get('icon'):
                    s+='<td style="width:60px"><img src="%s" alt="%s"/></td>\n' % (val['icon'],val['event'])
                __size=110 if int(val['level'])>2 else 100
                s+='<td><p style="font-size:%i%%;margin-bottom:0">%s</p>\n' % (__size,val['headline'])
                if val['start'] and val['end']:
                    s='%s<p style="font-size:80%%">gültig vom %s bis %s</p></td>\n' % (s,time.strftime("%d.%m. %H:%M",time.localtime(val['start']/1000)),time.strftime("%d.%m. %H:%M",time.localtime(val['end']/1000)))
                elif val['start']:
                    s='%s<p style="font-size:80%%">gültig seit %s</p></td>\n' % (s,time.strftime("%d.%m. %H:%M",time.localtime(val['start']/1000)))
                elif val['end']:
                    s='%s<p style="font-size:80%%">gültig bis %s</p></td>\n' % (s,time.strftime("%d.%m. %H:%M",time.localtime(val['end']/1000)))
                s+='</tr></table>\n'

                if val.get('description'):
                    s+="<p>%s</p>\n" % val['description']
                if val.get('instruction'):
                    s+="<p>%s</p>\n" % val['instruction']
                if val.get('sender'):
                    if 'sender_name' in val:
                        sn = val['sender_name']+' ('+val['sender']+')'
                    else:
                        sn = val['sender']
                    if val.get('sender_logo',''):
                        lg = '<img src="%s" style="max-height:16px" alt="%s" /> ' % (val['sender_logo'],val['sender'])
                    else:
                        lg = ""
                    s+='<p style="font-size:80%%">Quelle: %s%s</p>' % (lg,sn)

                s+='<p style="font-size:40%%">%s &ndash; %s &emsp;&ndash;&emsp;  %s &ndash; %s &emsp;&ndash;&emsp; %s &ndash; %s &emsp;&ndash;&emsp; %s</p>' % (val.get('type',''),val.get('event',''),val.get('level',''),val.get('level_text',''),val.get('category',''),val.get('categoryName',''),val.get('identifier',''))
                
            if s:
                s += '<p style="font-size:65%%">Herausgegeben vom BBK | Abgerufen am %s</p>\n' % time.strftime('%d.%m.%Y %H:%M')
            else:
                s = '<p>%s</p>' % CAP.NOWARNING.get(lang,CAP.NOWARNING['en'])
                s += '<p style="font-size:65%%">Zuletzt beim BBK abgerufen am %s</p>\n' % time.strftime('%d.%m.%Y %H:%M')
 
            if dryrun:
                print("########################################")
                print("-- HTML -- bbk-%s.inc ------------------------------"%__ww)
                print(s)
                print("-- JSON -- bbk-%s.json -----------------------------"%__ww)
                print(json.dumps(wwarn[__ww],indent=4,ensure_ascii=False))
            else:
                with open("%s/bbk-%s.inc" % (target_path,__ww),"w") as file:
                    file.write(s)
                with open("%s/bbk-%s.json" % (target_path,__ww),"w") as file:
                    json.dump(wwarn[__ww],file,indent=4)

        

class MSC(CAP):

    # Canada
    # https://eccc-msc.github.io/open-data/msc-data/alerts/readme_alerts-datamart_en/
    # https://dd.weather.gc.ca/alerts/cap/

    MSC_URL = 'https://dd.weather.gc.ca/alerts/cap'
    
    OFFICES = {
        'CWUL':(
            'Quebec Storm Prediction Centre',
            'centre de prévision des intempéries du Québec',
            'QSPC','CPIQ','Montréal'),
        'CWEG':(
            'Prairie and Arctic Storm Prediction Centre',
            "centre de prévision des intempéries des Prairies et de l'Arctique",
            'PASPC','CPIPA','Edmonton'),
        'CWNT':(
            'Prairie and Arctic Storm Prediction Centre',
            "centre de prévision des intempéries des Prairies et de l'Arctique",
            'PASPC','CPIPA','Edmonton'),
        'CWWG':(
            'Prairie and Arctic Storm Prediction Centre',
            "centre de prévision des intempéries des Prairies et de l'Arctique",
            'PASPC','CPIPA','Winnipeg'),
        'CWVR':(
            'Pacific and Yukon Storm Prediction Centre',
            "centre de prévision des intempéries de la région du Pacfique et du Yukon",
            'PSPC','CPIP','Vancouver'),
        'CWTO':(
            'Ontario Storm Prediction Centre',
            "centre de prévision des intempéries de l'Ontario",
            'OSPC','CPIO','Toronto'),
        'CYQX':(
            'Newfoundland and Labrador Weather Office',
            "centre de prévision des intempéries de Terre-Neuve-et-Labrador",
            'NLWO','CPITNL','Gander'),
        'CWAO':(
            'Canadian Meteorological Centre',
            "Centre météorologique canadien",
            'CMC','CMC','Montréal'),
        'CWIS':(
            'Canadian Ice Service',
            "Service canadien des glaces",
            'CIS','SCG','Ottawa'),
        'CWHX':(
            'Atlantic Storm Prediction Centre',
            "centre de prévision des intempéries de la région de l'Atlantique",
            'ASPC','CPIRA','Dartmouth')
    }

    MSC_LEVEL = (
        'no warning',     # 0 no warning
        'preliminary info',    # 1 preliminary info
        'minor',     # 2 minor
        'moderate',  # 3 moderate
        'servere',   # 4 severe
        'extreme'  # 5 extreme
    )

    def level_text(self, level, lang='en', isdwd=True):
        try:
            return MSC.MSC_LEVEL[level]
        except LookupError:
            return 'unknown'

    def __init__(self, warn_dict, verbose=False):
        super(MSC,self).__init__(warn_dict)
        self.filter_area = dict()
        self.offices = []
        for loc in warn_dict.sections:
            if warn_dict[loc].get('provider','')=='MSC':
                location = warn_dict[loc]
                if 'office' in location:
                    if isinstance(location['office'],list):
                        self.offices.extend(location['office'])
                    else:
                        self.offices.append(location['office'])
                if 'county' in location:
                    self.filter_area[location['county']] = location['file']
        if not self.offices:
            self.offices = [ii for ii in MSC.OFFICES]
                
        
    def dir(self, url, dirtype):
        if self.verbose:
            loginf('about to download zip file list from %s' % url)
        reply = self.wget(url,'subdirectory list from %s successfully downloaded')
        if reply:
            reply = reply.decode(encoding='utf-8')
            parser = MSCsubdirParser(dirtype)
            parser.feed(reply)
            return parser.get_files()
        else:
            return None
            

    def warnings(self, lang='en',log_tags=False):
        now = time.time()
        dt = time.strftime("%Y%m%d",time.localtime())
        url = MSC.MSC_URL+'/'+dt
        dirs = self.dir(url,'office')
        for dir in dirs:
          if dir[0:4] in self.offices:
            #loginf(dir)
            subdirs = self.dir(url+'/'+dir,'hour')
            for subdir in subdirs:
                x = url+'/'+dir+subdir
                #loginf(x)
                files = self.dir(x,'cap')
                for file in files:
                    reply = self.wget(x+file)
                    ti = time.time()
                    if reply:
                        xmltext = reply.decode(encoding='utf-8')
                        cap_dict = self.convert_xml(xmltext,log_tags)
                        cap_dict['alert']['MSC_office'] = dir[0:4]
                        cap_dict['alert']['MSC_hour'] = subdir[0:2]
                        cap_dict['alert']['capwarnings_downloaded'] = ti
                        yield cap_dict['alert']


    def _area_filter(self, info_dict):
        """ find out whether the given alert is valid for one of the areas 
            (cities, counties etc.) we are interested in
            
            As the providers provide that information in different ways, this
            function has to be defined in the provider specific classes.
        """
        #print('++++++++++++++++++++++++++++++++++++')
        #print(json.dumps(info_dict,indent=4))
        #print('------------------------------------')
        reply = []
        for tag,val in info_dict.items():
            try:
                if tag=='area':
                    for ii in val:
                        try:
                            if ii['areadesc'] in self.filter_area:
                                reply.append((ii['areadesc'],'id',0,3000,'state','state',self.filter_area[ii['areadesc']]))
                                
                        except Exception as e:
                            if self.verbose:
                                logerr("inner %s %s" % (e.__class__.__name__,e))
            except Exception as e:
                if self.verbose:
                    logerr("outer %s %s" % (e.__class__.__name__,e))
        return reply


    def write_html(self, wwarn, target_path, dryrun):
        """ Canada """
        lang = wwarn[1]
        wwarn = wwarn[0]
        for __ww in wwarn:
            s = ""
            stateShort = ""
            r = None
            for idx,val in enumerate(wwarn[__ww]):
                # alert message 
                s+='<table style="vertical-align:middle"><tr style="vertical-align:middle">\n'
                if val.get('icon'):
                    s+='<td style="width:60px"><img src="%s" alt="%s"/></td>\n' % (val['icon'],val['event'])
                __size=110 if int(val['level'])>2 else 100
                s+='<td><p style="font-size:%i%%;margin-bottom:0">%s</p>\n' % (__size,val['headline'])
                s='%s<p style="font-size:80%%">valid from %s to %s\n' % (s,time.strftime("%d.%m. %H:%M",time.localtime(val['start']/1000)),time.strftime("%d.%m. %H:%M",time.localtime(val['end']/1000)))
                s+='</p></td>\n</tr></table>\n'

                if val.get('description'):
                    s+="<p>%s</p>\n" % val['description']
                if val.get('instruction'):
                    s+="<p>%s</p>\n" % val['instruction']

                s+='<p style="font-size:40%%">%s &ndash; %s &emsp;&ndash;&emsp; %s &ndash; %s &emsp;&ndash;&emsp; II=%s &ndash; %s</p>' % (val['type'],val['event'],val['level'],val['level_text'],val.get('eventCode-II',''),val.get('eventCode-profile:CAP-CP:Event:0.4',''))

            if s:
                s+='<p style="font-size:80%%">Source: %s | Downloaded at %s</p>\n' % (val['source'],time.strftime('%Y-%m-%d %H:%M'))
            else:
                s='<p>%s</p>' % CAP.NOWARNING.get(lang,CAP.NOWARNING['en'])
            
            if dryrun:
                print("########################################")
                print("-- HTML -- warn-%s.inc ------------------------------"%__ww)
                print(s)
                print("-- JSON -- warn-%s.json -----------------------------"%__ww)
                print(json.dumps(wwarn[__ww],indent=4,ensure_ascii=False))
            else:
                with open("%s/warn-%s.inc" % (target_path,__ww),"w") as file:
                    file.write(s)
                with open("%s/warn-%s.json" % (target_path,__ww),"w") as file:
                    json.dump(wwarn[__ww],file,indent=4)


##############################################################################
#   extract file names from directory listing                                #
##############################################################################

class CapDirParser(html.parser.HTMLParser):

    def __init__(self, lang):
        super(CapDirParser,self).__init__()
        if lang in ('de','en','es','fr'):
            self.lang = lang.lower()
        else:
            self.lang = 'ul'
        self.files = []
        
    def handle_starttag(self, tag, attrs):
        """ process HTML start tags """
        if tag=='a':
            for i in attrs:
                if i[0]=='href':
                    file_lang = (i[1][-6:-4]).lower()
                    if file_lang==self.lang and i[1][-4:].lower()=='.zip':
                        self.files.append(i[1])
    
    def get_files(self):
        """ get the list of file names found and close parser """
        self.close()
        return self.files


class MSCsubdirParser(html.parser.HTMLParser):

    def __init__(self, dirtype):
        super(MSCsubdirParser,self).__init__()
        if dirtype=='office':
            self.dirtype = ('C',)
        elif dirtype=='hour':
            self.dirtype = ('0','1','2')
        elif dirtype=='cap':
            self.dirtype = ('.cap',)
        self.files = []
    
    def isvalid(self, href):
        if self.dirtype[0]=='.cap':
            return href[-4:]=='.cap'
        return href[0] in self.dirtype
        
    def handle_starttag(self, tag, attrs):
        """ process HTML start tags """
        if tag=='a':
            for i in attrs:
                if i[0]=='href' and self.isvalid(i[1]):
                    self.files.append(i[1])
    
    def get_files(self):
        """ get the list of file names found and close parser """
        self.close()
        return self.files


##############################################################################
#   parse CAP file                                                           #
##############################################################################

# Note: Strictly speaking CAP files are XML, not HTML. But for our 
#       purpose a simple HTML parser is sufficient.

# Note: There is one and only one alert per file.

class CAPParser(html.parser.HTMLParser):

    # tags that require special handling
    TAGTYPE = {
        # tag       sub      multiple
        #           section  times
        'alert':    (True,   False),
        'info':     (True,   True),
        'eventcode':(True,   True),
        'area':     (True,   True),
        'geocode':  (True,   True),
        'parameter':(True,   True),
        'code':     (False,  True)}
        # default:   False   False
        
    def __init__(self, log_tags=False):
        super(CAPParser,self).__init__()
        self.log_tags = log_tags
        self.lvl = 0
        self.tags = []
        self.cap = dict()
        self.ar = [self.cap]
        
    def _is_dict(self, tag):
        """ Is this tag a sub-section? """
        return self.TAGTYPE.get(tag,(False,False))[0]
        
    def _is_array(self, tag):
        """ Is this tag allowed multiple times? """
        return self.TAGTYPE.get(tag,(False,False))[1]
        
    def handle_starttag(self, tag, attrs):
        """ handle start tag """
        if self.log_tags:
            print(self.lvl,self.tags,'start',tag,attrs)
        self.tags.append(tag)
        self.lvl+=1
        if self._is_array(tag):
            if tag not in self.ar[-1]:
                self.ar[-1][tag] = []
            if self._is_dict(tag):
                self.ar[-1][tag].append(dict())
                self.ar.append(self.ar[-1][tag][-1])
        elif self._is_dict(tag):
            self.ar[-1][tag] = dict()
            self.ar.append(self.ar[-1][tag])
        
    def handle_endtag(self, tag):
        """ handle end tag """
        del self.tags[-1]
        self.lvl-=1
        if self._is_dict(tag):
            del self.ar[-1]
        if self.log_tags:
            print(self.lvl,self.tags,'end',tag)

    def handle_data(self, data):
        """ handle data between tags """
        if len(self.tags)>0:
            tag = self.tags[-1]
            if self._is_array(tag):
                if self._is_dict(tag):
                    pass
                else:
                    self.ar[-1][tag].append(data)
                    pass
            elif self._is_dict(tag):
                if not data.isspace():
                    self.ar[-1]['@'] = data
            else:
                self.ar[-1][tag] = data
        if self.log_tags:
            print(self.lvl,self.tags,'data',data)


##############################################################################

class CAPwarnings(object):

    PROVIDERS = {
        'DWD':('DeutscherWetterdienst','warning',DWD),
        'BBK':('DeutscherWetterdienst','BBK',BBK),
        'MSC':('WeatherServices','warning',MSC)
    }
    
    def __init__(self, config_dict, provider, verbose=False):
        
        super(CAPwarnings,self).__init__()
        self.provider = provider
        section = CAPwarnings.PROVIDERS[provider]
        ws_dict = configobj.ConfigObj()
        if 'WeatherServices' in config_dict and 'warning' in config_dict['WeatherServices']:
            base_dict = accumulateLeaves(config_dict['WeatherServices'])
            ws_dict.update(accumulateLeaves(config_dict['WeatherServices']['warning']))
            for sec in config_dict['WeatherServices']['warning']:
                sec_dict = accumulateLeaves(config_dict['WeatherServices']['warning'][sec])
                ws_dict[sec] = sec_dict
        if 'DeutscherWetterdienst' in config_dict:
            if provider=='BBK' and 'BBK' in config_dict['DeutscherWetterdienst']:
                for county,file in config_dict['DeutscherWetterdienst']['BBK']['counties'].items():
                    ws_dict[county] = {'provider':'BBK','file':file}
                if 'icons' in config_dict['DeutscherWetterdienst']['BBK']:
                    ws_dict['bbk_icons'] = config_dict['DeutscherWetterdienst']['BBK']['icons']
                if 'logos' in config_dict['DeutscherWetterdienst']['BBK']:
                    ws_dict['bbk_logos'] = config_dict['DeutscherWetterdienst']['BBK']['logos']
                base_dict = accumulateLeaves(config_dict['DeutscherWetterdienst'])
            if provider=='DWD' and 'warning' in config_dict['DeutscherWetterdienst']:
                ws_dict['counties'] = config_dict['DeutscherWetterdienst']['warning']['counties']
                ws_dict['cities'] = config_dict['DeutscherWetterdienst']['warning']['cities']
                if 'icons' in config_dict['DeutscherWetterdienst']['warning']:
                    ws_dict['dwd_icons'] = config_dict['DeutscherWetterdienst']['warning']['icons']
                if 'resolution' in config_dict['DeutscherWetterdienst']['warning']:
                    ws_dict['dwd_resolution'] = config_dict['DeutscherWetterdienst']['warning']['resolution']
                base_dict = accumulateLeaves(config_dict['DeutscherWetterdienst'])
        # target path
        try:
            self.target_path = config_dict['WeatherServices']['path']
        except LookupError:
            self.target_path = base_dict['path']
        # logging
        self.verbose = verbose
        self.log_success = tobool(ws_dict.get('log_success',base_dict.get('log_success',config_dict.get('log_success',False))))
        self.log_failure = tobool(ws_dict.get('log_failure',base_dict.get('log_failure',config_dict.get('log_failure',False))))
        if int(config_dict.get('debug',0))>0 or verbose:
            self.log_success = True
            self.log_failure = True
            self.verbose = True
        ws_dict['log_success'] = self.log_success
        ws_dict['log_failure'] = self.log_failure
        # 
        self.cap = section[2](ws_dict,verbose=self.verbose)
        
        if __name__ == "__main__" and verbose:
            print('-- configuration data ----------------------------------')
            print('log success:  ',self.cap.log_success)
            print('log failure:  ',self.cap.log_failure)
            #print('status url:   ',self.dwd_status_url)
            #print('diff msgs url:',self.dwd_diff_url)
            print('filter area:  ',self.cap.filter_area)
            print('target path:  ',self.target_path)
            print('icon URL:     ',self.cap.icon_base_url)
            print('logo URL:     ',self.cap.logo_base_url)
            print('-- configuration dict ----------------------------------')
            print(json.dumps(ws_dict,indent=4,ensure_ascii=False))
            print('--------------------------------------------------------')


    def get_warnings(self, lang='de', log_tags=False):
        return self.cap.get_warnings(lang,log_tags)
    
    
    def write_html(self, wwarn, dryrun):
        self.cap.write_html(wwarn, self.target_path, dryrun)
        

if __name__ == "__main__" or invoke_fn in standalone:

    usage = "Usage: %prog [options] [warning_region]"
    epilog = None    

    # Create a command line parser:
    parser = optparse.OptionParser(usage=usage, epilog=epilog)

    # options
    parser.add_option("--config", dest="config_path", type=str,
                      metavar="CONFIG_FILE",
                      default=None,
                      help="Use configuration file CONFIG_FILE.")
    parser.add_option("--weewx", action="store_true",
                      help="Read config from weewx.conf.")
    parser.add_option("--lang", dest="lang", type=str,
                      metavar="ISO639",
                      default='de',
                      help="Alert language. Default 'de'")
    parser.add_option("--provider", dest="provider", type=str,
                      metavar="PROVIDER",
                      help="warnings provider 'DWD' or 'BBK'")

    group = optparse.OptionGroup(parser,"DWD")
    group.add_option("--diff", action="store_true",
                      help="Use diff files instead of status files.")
    group.add_option("--resolution", dest="resolution", type=str,
                      metavar="VALUE",
                      default=None,
                      help="Overwrite configuration setting for resolution. Possible values are 'county' and 'city'.")
    group.add_option("--get-warncellids", dest="warncellids", action="store_true",
                      help="Download warn cell ids file.")
    group.add_option("--list-ii", dest="lsii", action="store_true",
                     help="List defined II event codes")
    group.add_option("--list-zip", dest="lszip", action="store_true",
                     help="Download and display zip file list (for debugging purposes)")
    parser.add_option_group(group)

    group = optparse.OptionGroup(parser,"BBK")
    group.add_option("--list-logos", action="store_true",
                      help="list logos")
    group.add_option("--list-eventcodes", action="store_true",
                      help="list event codes")
    group.add_option("--include-dwd", action="store_true",
                     help="Include messages originating from DWD. Default is to exclude those messages.")
    parser.add_option_group(group)

    group = optparse.OptionGroup(parser,"Output and logging options")
    group.add_option("--target-path", dest="target_path",
                     metavar="PATH",
                     default=None,
                     help="Overwrite configuration setting for target path")
    group.add_option("--dry-run", action="store_true",
                      help="Print what would happen but do not do it. Default is False.")
    group.add_option("--log-tags", action="store_true",
                      help="Log tags while parsing the XML file. Default is not to log the XML tags.")
    group.add_option("-v","--verbose", action="store_true",
                      help="Verbose output")
    parser.add_option_group(group)
    
    (options, args) = parser.parse_args()

    if options.weewx:
        config_path = "/etc/weewx/weewx.conf"
    else:
        config_path = options.config_path

    if config_path:
        print("Using configuration file %s" % config_path)
        config = configobj.ConfigObj(config_path)
    else:
        # test only
        print("Using test configuration")
        # vom Benutzer anzupassen
        states=['Sachsen','Thüringen']
        counties={
            'Kreis Mittelsachsen - Tiefland':'DL',
            'Stadt Leipzig':'L',
            'Stadt Jena':'J',
            'Stadt Dresden':'DD'}
        cities={
            'Stadt Döbeln':'DL',
            'Stadt Leipzig':'L',
            'Stadt Jena':'J',
            'Stadt Dresden':'DD'}
        ICON_PTH="../dwd/warn_icons_50x50"
        target_path='.'
    
        config = configobj.ConfigObj({
            'log_success':True,
            'log_failure':True,
            'WeatherServices': {
                'path':target_path,
                'warning':{
                    '1': {
                        'provider':'MSC',
                        'office':'CWHX',
                        'county':'Upper Lake Melville',
                        'file':'XX'
                    }
                }
            },
            'DeutscherWetterdienst': {
                'warning': {
                    #'dwd_status_url': get_cap_url('city','cell','neutral',False),
                    #'dwd_diff_url': get_cap_url('city','cell','neutral',True),
                    'icons': ICON_PTH,
                    'states' : states,
                    'counties': counties,
                    'cities': cities },
                'BBK': {
                    'counties': {
                         '145220080080':'DL',
                         #'145220250250':'DL',
                         '147130000000':'L',
                         '145210440440':'Oberwiesenthal'}}}})

    if options.resolution:
        config['DeutscherWetterdienst']['warning']['resolution'] = options.resolution
    if options.target_path is not None:
        config['WeatherServices']['path'] = options.target_path
    
    # warnings provider
    if invoke_fn=='dwd-cap-warnings':
        # Deutscher Wetterdienst
        provider = 'DWD'
    elif invoke_fn=='bbk-warnings':
        # Bundesamt für Bevoelkerungsschutz und Katastrophenhilfe
        provider = 'BBK'
    elif invoke_fn=='msc-warnings':
        # Canada
        provider = 'MSC'
    else:
        provider = options.provider
        if not provider:
            if options.warncellids:
                provider = 'DWD'

    # areas (cities, counties) to get alerts for
    if len(args)>0:
        if provider=='DWD':
            arg_dict = {arg:arg for arg in args}
            res = config['DeutscherWetterdienst']['warning']['resolution']
            if res in ('county','counties'):
                res = 'counties'
            elif res in ('city','cities'):
                res = 'cities'
            config['DeutscherWetterdienst']['warning'][res] = arg_dict
        else:
            arg_dict = {arg:{'provider':provider} for arg in args}
            config['WeatherServices']['warning'] = arg_dict
            if 'warning' in config['DeutscherWetterdienst']:
                del config['DeutscherWetterdienst']['warning']
    
    if options.include_dwd is not None:
        if 'WeatherServices' in config and 'warning' in config['WeatherServices']:
            config['WeatherServices']['warning']['bbk_include_dwd'] = options.include_dwd
        else:
            config['DeutscherWetterdienst']['BBK']['include_dwd'] = options.include_dwd

    if options.lsii:
        # list II weather codes
        c = -1
        for ii in DWD.CAP_II:
            if c!=ii[2]:
                if c>=0: print("")
                c = ii[2]
                print(DWD.CAP_II_CAPTION[c])
                print(" II | type | c | event")
                print("---:|-----:|--:|--------------------------------------------------------------")
            print("%3s | %4s | %1s | %s" % (ii[0],ii[1],ii[2],ii[3]))
    else:
        cap = CAPwarnings(config,provider,options.verbose)

        if options.warncellids:
            # DWD warncellids
            cap.cap.download_warncellids(cap.target_path,options.dry_run)
        elif options.lszip:
            # DWD ZIP files list
            ff = cap.cap.dir(options.diff,options.lang)
            print('\n'.join(ff))
        elif options.list_logos:
            # alert originator logos list
            print(json.dumps(cap.cap.logos,indent=4,ensure_ascii=False))
        elif options.list_eventcodes:
            # alert icons list
            print(json.dumps(cap.cap.eventicons,indent=4,ensure_ascii=False))
        else:
            # output alerts to files in HTML and JSON
            wwarn = cap.get_warnings(options.lang,options.log_tags)
            cap.write_html(wwarn,options.dry_run)
    
