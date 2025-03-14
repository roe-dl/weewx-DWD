#!/usr/bin/python3
# Copyright (C) 2023, 2024 Johanna Roedenbeck

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
    This extension processes radar data provided by the German Weather
    Service DWD and published in binary on their opendata server.
    
    * HG format:
      precipitation kind 2m above ground according to the radar
    * WN format
      radar reflectivity factor dBZ
    * RV format
      precipitation in mm of the last 5 min.
    
    # https://opendata.dwd.de/weather/radar/composite/{hg|pg|rv|wn}/

    Format description
    ==================
    
    The format description documents are in german.
    
    * HG format:
      https://www.dwd.de/DE/leistungen/radarprodukte/formatbeschreibung_hg.pdf?__blob=publicationFile&v=6
    * WN format:
      https://www.dwd.de/DE/leistungen/radarprodukte/formatbeschreibung_wndaten.pdf?__blob=publicationFile&v=7
    * RV format:
      https://www.dwd.de/DE/leistungen/radarprodukte/formatbeschreibung_rv.pdf?__blob=publicationFile&v=3

    Coordinate conversion
    =====================
    
    Geographic coordinates have to be converted to the coordinates of the
    appropriate projection using the `proj` tool, which is available for
    free for Linux, Windows and macOS.
    
    https://proj.org/en/9.3/usage/quickstart.html
    https://proj.org/en/9.3/operations/projections/stere.html
"""

import time
import datetime
import gzip
import bz2
import tarfile
import io
import configobj
import os
import os.path
import threading
import random
import math
import struct
from PIL import Image, ImageColor, ImageDraw, ImageFont, PngImagePlugin

# deal with differences between python 2 and python 3
try:
    # Python 3
    import queue
except ImportError:
    # Python 2
    # noinspection PyUnresolvedReferences
    import Queue as queue

import __main__

if __name__ == '__main__':
    import optparse
    import json
    import sys
    sys.path.append('/usr/share/weewx')
    x = os.path.dirname(os.path.abspath(os.path.dirname(__main__.__file__)))
    if x not in sys.path:
        sys.path.append(x)

if __name__ == '__main__' or __main__.__file__.endswith('weatherservices.py'):

    def logdbg(x):
        print('DEBUG radar',x)
    def loginf(x):
        print('INFO radar',x)
    def logerr(x):
        print('ERROR radar',x)

else:

    try:
        # Test for new-style weewx logging by trying to import weeutil.logger
        import weeutil.logger
        import logging
        log = logging.getLogger("user.DWD.radar")

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

from user.weatherservicesutil import wget, BaseThread
import weeutil.weeutil # startOfDay, archiveDaySpan
import weeutil.config # accumulateLeaves
import weewx.units
import weewx.xtypes

MAP_LOCATIONS_DE1200_WGS84 = {
    'Wöllsdorf': {'xy': (766379.87, -579859.86), 'lat': '51.123', 'lon': '13.040', 'scale':1.0},
    'Leipzig': {'xy': (716516.82, -556809.38), 'lat': '51.3406', 'lon': '12.3747', 'scale':1.0},
    'Dresden': {'xy': (817762.02, -585484.68), 'lat': '51.0489', 'lon': '13.7331', 'scale':1.0},
    'Chemnitz': {'xy': (759302.32, -614127.12), 'lat': '50.8332', 'lon': '12.92', 'scale':1.0},
    'Berlin': {'xy': (783746.86, -416406.23), 'lat': '52.518611', 'lon': '13.408333', 'scale':1.0},
    'Brandenburg':{'xy':(724015.12,-431647.86),'lat':52.41399,'lon':12.55369,'scale':2.0},
    'Görlitz': {'xy': (909705.9, -566628.93), 'lat': '51.15', 'lon': '15.0', 'scale':1.0},
    'Hamburg': {'xy': (542739.88, -304450.27), 'lat': '53.550556', 'lon': '9.993333', 'scale':1.0},
    'Emden': {'xy': (350748.08, -320916.7), 'lat': '53.3668', 'lon': '7.2061', 'scale':1.0},
    'Bremen':{'xy':(460307.48,-358300.18),'lat':53.0758,'lon':8.80717,'scale':2.0},
    'Bremerhaven':{'xy':(445790.99,-303943.91),'lat':53.54446,'lon':8.57895,'scale':6.0},
    'Greifswald': {'xy': (771145.8, -235040.31), 'lat': '54.0960', 'lon': '13.3817', 'scale':1.0},
    'Wolfenbüttel': {'xy': (581351.05, -464637.09), 'lat': '52.16263', 'lon': '10.53484', 'scale':1.0},
    'Brocken': {'xy': (587565.63, -506791.63), 'lat': '51.7991', 'lon': '10.6156', 'scale':1.0, 'peak':True},
    'Fichtelberg': {'xy': (764264.57, -661198.14), 'lat': '50.429444', 'lon': '12.954167', 'scale':1.0, 'peak':True},
    'Carlsfeld':{'xy':(738623.48,-662226.69),'lat':50.4314,'lon':12.6114,'scale':20.0},
    'Rittersgrün':{'xy':(752720.72,-656540.09),'lat':50.47409,'lon':12.8032,'scale':20.0},
    'Aue':{'xy':(744558.02,-643498.63),'lat':50.58865,'lon':12.70238,'scale':20.0},
    'Schwarzenberg':{'xy':(750902.22,-649178.70),'lat':50.53761,'lon':12.78369,'scale':10.0},
    'Cranzahl':{'xy':(766566.35,-650829.15),'lat':50.5168,'lon':12.9921,'scale':20.0},
    'Eibenstock':{'xy':(737396.96,-654935.98),'lat':50.49393,'lon':12.59945,'scale':20.0},
    'Jáchymov':{'xy':(761972.06,-668527.96),'lat':50.368,'lon':12.9186,'scale':20.0},
    'Weimar': {'xy': (641248.04, -601415.0), 'lat': '50.97937', 'lon': '11.32976', 'scale':1.0},
    'Aachen': {'xy': (253005.58, -616350.99), 'lat': '50.77644', 'lon': '6.08373', 'scale':1.0},
    'Augsburg': {'xy': (614212.32, -909407.49), 'lat': '48.36879', 'lon': '10.89774', 'scale':1.0},
    'Nürnberg': {'xy': (626001.01, -780799.9), 'lat': '49.45390', 'lon': '11.07730', 'scale':1.0},
    'Praha': {'xy': (876957.35, -694134.76), 'lat': '50.08749', 'lon': '14.42120', 'scale':1.0},
    'Salzburg': {'xy': (787704.56, -971297.07), 'lat': '47.79848', 'lon': '13.04667', 'scale':1.0},
    'Plzeň': {'xy': (800628.43, -739437.07), 'lat': '49.7472', 'lon': '13.37748', 'scale':1.0},
    'Offenbach': {'xy': (449889.2, -703981.79), 'lat': '50.10478', 'lon': '8.76454', 'scale':1.0},
    'Luxembourg': {'xy': (247137.74, -753023.96), 'lat': '49.6113', 'lon': '6.1292', 'scale':1.0},
    'Zürich': {'xy': (424864.45, -1027214.44), 'lat': '47.37177', 'lon': '8.54220', 'scale':1.0},
    'Karlsruhe': {'xy': (419118.5, -831795.91), 'lat': '49.01396', 'lon': '8.40442', 'scale':1.0},
    'Münster': {'xy': (372911.26, -484503.91), 'lat': '51.9626', 'lon': '7.6258', 'scale':1.0},
    'Kiel': {'xy': (552568.9, -215715.36), 'lat': '54.3231', 'lon': '10.1399', 'scale':1.0},
    'Flensburg': {'xy': (505833.67, -162879.18), 'lat': '54.7832', 'lon': '9.4345', 'scale':1.0},
    'Husum':{'xy':(479962.35,-197575.74),'lat':54.47698,'lon':9.05168,'scale':2.0},
    'Brunsbüttel':{'xy':(482414.53,-264324.56),'lat':53.8954,'lon':9.1041,'scale':2.0},
    'Szczecin': {'xy': (856569.86, -306401.86), 'lat': '53.42523', 'lon':'14.56021', 'scale':1.0},
    'Cottbus/Chóśebuz': {'xy': (855632.43, -499673.59), 'lat': '51.76068', 'lon':'14.33429', 'scale':1.0},
    'Göttingen': {'xy': (538491.31, -538008.38), 'lat': '51.5328', 'lon': '9.9352', 'scale':2.0},
    'Kassel':{'xy':(506522.38,-563143.59), 'lat': '51.3157', 'lon': '9.498', 'scale':1.0},
    'Zugspitze':{'xy':(623159.66,-1022123.31),'lat':47.42122,'lon':10.9863, 'scale':1.0, 'peak':True},
    'Schwerin':{'xy':(639938.73,-294247.94),'lat':53.62884,'lon': 11.41486, 'scale':2.0},
    'Leeuwarden':{'xy':(252164.35,-334194.25),'lat':53.19959,'lon':5.79331, 'scale':2.0},
    'Apeldoorn':{'xy':(255942.84,-448573.20),'lat':52.2154,'lon':5.9640, 'scale':1.0},
    'Ústí nad Labem':{'xy':(843631.75,-629392.32),'lat':50.659167,'lon':14.041667,'scale':2.0},
    'Karlovy Vary':{'xy':(759537.85,-684494.50),'lat':50.2331,'lon':12.8755,'scale':4.0},
    'Louny':{'xy':(827797.23,-665920.36),'lat':50.35732,'lon':13.79678,'scale':4.0},
    'Riesa':{'xy':(784545.47,-557952.21),'lat':51.3019,'lon':13.3041,'scale':2.0},
    'Rostock':{'xy':(687534.54,-239909.82),'lat':54.08871,'lon':12.14009,'scale':2.0},
    'Neubrandenburg':{'xy':(766490.78,-297304.44),'lat':53.55743,'lon':13.26029,'scale':2.0},
    'Lübeck':{'xy':(589701.46,-267829.25),'lat':53.86661,'lon':10.68486,'scale':2.0},
    'Stralsund':{'xy':(750175.49,-210958.17),'lat':54.31599,'lon':13.09048,'scale':3.0},
    'Wismar':{'xy':(642670.59,-263984.20),'lat':53.89142,'lon':11.46612,'scale':3.0},
    'Magdeburg':{'xy':(659925.02,-467441.19),'lat':52.12564,'lon':11.63476,'scale':2.0},
    'Wernigerode':{'xy':(599678.61,-502655.27),'lat':51.83341,'lon':10.78443,'scale':10.0},
    'Goslar':{'xy':(574026.86,-494503.16),'lat':51.9059,'lon':10.42904,'scale':10.0},
    'Nordhausen':{'xy':(600850.17,-541186.64),'lat':51.5021,'lon':10.79329,'scale':4.0},
    'Sangerhausen':{'xy':(637582.21,-543917.50),'lat':51.4729,'lon':11.29772,'scale':10.0},
    'Herzberg am Harz':{'xy':(568003.36,-523537.35),'lat':51.65652,'lon':10.3428,'scale':10.0},
    'Quedlinburg':{'xy':(625518.77,-507290.73),'lat':51.7898,'lon':11.14194,'scale':4.0},
    'Halle':{'xy':(686408.52,-541383.04),'lat':51.4827,'lon':11.9698,'scale':2.0},
    'Dessau':{'xy':(704934.34,-499645.91),'lat':51.83534,'lon':12.24687,'scale':4.0},
    'Eisenach':{'xy':(566769.42,-603040.83),'lat':50.97463,'lon':10.31962,'scale':2.0},
    'Zwickau':{'xy':(728629.46,-629097.17),'lat':50.71774,'lon':12.49731,'scale':4.0},
    'Plauen':{'xy':(702782.89,-656383.59),'lat':50.49379,'lon':12.13588,'scale':4.0},
    'Gera':{'xy':(697226.91,-611763.29),'lat':50.87658,'lon':12.08329,'scale':4.0},
    'Bautzen/Budyšin':{'xy':(867292.32,-566448.65),'lat':51.1814,'lon':14.42402,'scale':4.0},
    'Stendal':{'xy':(674153.10,-411427.04),'lat':52.60511,'lon':11.85934,'scale':2.0},
    'Herzberg (Elster)':{'xy':(776949.55,-512837.59),'lat':51.69239,'lon':13.23517,'scale':2.0},
    'Bad Düben':{'xy':(730557.66,-527005.97),'lat':51.59102,'lon':12.58524,'scale':4.0},
    'Innsbruck':{'xy':(656587.54,-1039686.29),'lat':47.2685,'lon':11.39321,'scale':4.0},
    'Döbeln':{'xy':(772401.33,-579683.03),'lat':51.12174,'lon':13.12199,'scale':10.0},
    'Waldheim':{'xy':(765529.88,-585740.27),'lat':51.07308,'lon':13.02422,'scale':10.0},
    'Hartha':{'xy':(761938.15,-583039.95),'lat':51.09779,'lon':12.97736,'scale':10.0},
    'Roßwein':{'xy':(777357.60,-586031.84),'lat':51.06510,'lon':13.18456,'scale':10.0},
    'Leisnig':{'xy':(757848.47,-576002.90),'lat':51.15981,'lon': 12.92668,'scale':10.0},
    'Gärtitz':{'xy':(771940.21,-577226.79),'lat':51.14297,'lon':13.11754,'scale':20.0},
    'Großweitzschen':{'xy':(766550.99,-575748.76),'lat':51.1581,'lon':13.0453,'scale':10.0},
    'Ziegra':{'xy':(767778.60,-581947.75),'lat':51.1045,'lon':13.0575,'scale':20.0},
    'Geringswalde':{'xy':(756649.66,-585769.85),'lat':51.07676,'lon':12.90362,'scale':10.0},
    'Ostrau':{'xy':(775027.72,-570451.50),'lat':51.19950,'lon':13.16463,'scale':20.0},
    'Mügeln':{'xy':(766227.92,-566575.17),'lat':51.23677,'lon':13.04755,'scale':10.0},
    'Bockelwitz':{'xy':(759657.51,-571308.11),'lat':51.1992,'lon':12.9546,'scale':20.0},
    'Würzburg':{'xy':(537819.43,-741466.75),'lat':49.79442,'lon':9.9294,'scale':2.0},
    'Stuttgart':{'xy':(478924.35,-861337.35),'lat':48.77501,'lon':9.17878,'scale':2.0},
    'Ulm':{'xy':(542686.17,-906655.24),'lat':48.39666,'lon':9.99354,'scale':3.0},
    'Freiburg im Breisgau':{'xy':(371457.19,-951050.08),'lat':47.99603,'lon':7.84956,'scale':2.0},
    'Strasbourg':{'xy':(365930.12,-881015.56),'lat':48.58339,'lon':7.74594,'scale':3.0},
    'Großglockner':{'xy':(763478.42,-1059093.91),'lat':47.0745464,'lon':12.6938826,'scale':1.0,'peak':True},
    'Śnieżka/Sněžka':{'xy':(968601.87,-609683.31),'lat':50.7359438,'lon':15.7397826,'scale':1.0,'peak':True},
}

# often used map dimensions
AREAS = {
    'DE':(120,100,860,1000),    # Deutschland gesamt
    'DE-MV':(578,839,275,200),  # Mecklenburg-Vorpommern
    'DE-BB':(631,624,240,290),  # Land Brandenburg
    'DE-BE':(756,754,54,54),    # Berlin
    'DE-ST':(580,588,196,254),  # Sachsen-Anhalt
    'DE-SN':(677,489,240,202),  # Sachsen
    'DE-TH':(520,494,219,192),  # Thüringen
    'Harz':(550,646,100,70),    # Harz (Gebirge)
    'DE-Ost':(520,489,400,550), # Deutschland Ost
    'DE-SH':(390,869,240,190),  # Schleswig-Hollstein
    'DE-HH':(515,877,42,46),    # Hansestadt Hamburg
    'DE-HB':(424,832,57,70),    # Hansestadt Bremen
    'DE-NI':(287,630,332,306),  # Niedersachsen
    'DE-NW':(235,490,276,294),  # Nordrhein-Westfalen
    'DE-RP':(240,356,200,246),  # Rheinland-Pfalz
    'DE-SL':(256,383,88,68),    # Saarland
    'DE-HE':(370,408,190,270),  # Hessen
    'DE-BW':(330,160,266,310),  # Baden-Württemberg
    'DE-BY':(465,155,390,400),  # Bayern
    'AT-8':(493,102,74,96),     # Vorarlberg
    'AT-7':(543,78,240,150),    # Tirol
    'LU':  (215,417,66,100),    # Lëtzebuerg
    'Döbeln':(755,608,30,24),   # Döbelner Land
    'Fichtelberg':(727,526,44,26) # Fichtelberggebiet
}

# Initialize default unit for the unit groups defined in this extension

for _,ii in weewx.units.std_groups.items():
    ii.setdefault('group_wmo_wawa','byte')

def load_places(fn,projection):
    try:
        line = ''
        places = dict()
        with open(fn,'rt') as f:
            for line in f:
                x = line.split()
                if x[2] and x[2][0]=='^':
                    loc = x[2][1:]
                    peak = True
                else:
                    loc = x[2]
                    peak = False
                places[loc.replace('_',' ')] = {
                    'xy':(float(x[0]),float(x[1])),
                    'lat':x[3],
                    'lon':x[4],
                    'scale':float(x[5]),
                    'peak':peak
                }
        if projection=='DE1200':
            MAP_LOCATIONS_DE1200_WGS84.update(places)
    except OSError as e:
        logerr("%s: cannot open file %s %s" % (fn,e.__class__.__name__,e))
    except LookupError as e:
        logerr("%s: invalid line '%s' %s %s" % (fn,line,e.__class__.__name__,e))
        logerr("%s: expected 'easting northing name latitude longitude scale'" % fn)
    except (ValueError,OverflowError) as e:
        logerr("%s: file encoding error %s %s" % (fn,e.__class__.__name,e))

def merge_wawa(wawa, intensity):
    """ merge precipitation intensity into wawa
    
        Args:
            wawa(int): wawa
            intensity(float): precipitation intensity in mm/h
        
        Returns:
            int: wawa
    """
    try:
        if wawa==50:
            if intensity<0.1: return 51
            if intensity>=0.5: return 53
            return 52
        if wawa==54:
            if intensity<0.1: return 54
            if intensity>=0.5: return 56
            return 55
        if wawa==60:
            if intensity<2.5: return 61
            if intensity>=10.0: return 63
            return 62
        if wawa==64:
            if intensity<2.5: return 64
            if intensity>=10: return 66
            return 65
        if wawa==67:
            if intensity<2.5: return 67
            return 68
        if wawa==70:
            if intensity<1.0: return 71
            if intensity>=4: return 73
            return 72
        if wawa==74:
            if intensity<1.0: return 74
            if intensity>=4.0: return 76
            return 75
    except (TypeError,ValueError,ArithmeticError):
        pass
    return wawa

def hyperbel_color(y0, yn, xs):
    ys = 0.5*yn+0.5*y0
    a = yn-ys
    c = a/(yn-y0)
    b = (1-c)/xs
    return a,b,c

class DwdRadar(object):

    COMPOSITE_URL = 'https://opendata.dwd.de/weather/radar/composite'
    RADOLAN_URL = 'https://opendata.dwd.de/weather/radar/radolan'
    RADVOR_URL = 'https://opendata.dwd.de/weather/radar/radvor'

    # valid for 1200x1100 DE1200 WGS84 HG, WN, RV
    BORDER_DE1200_WGS84 = {
        'NW': {'xy': (-500.0, 500.0), 'lat': '55.86208711', 'lon': '1.463301510'}, 
        'NO': {'xy': (1099500.0, 500.0), 'lat': '55.84543856', 'lon': '18.73161645'}, 
        'SO': {'xy': (1099500.0, -1199500.0), 'lat': '45.68460578', 'lon': '16.58086935'}, 
        'SW': {'xy': (-500.0, -1199500.0), 'lat': '45.69642538', 'lon': '3.566994635'}
    }
    
    PROJ_STR_DE1200_WGS84 = "+proj=stere +lat_0=90 +lat_ts=60 +lon_0=10 +a=6378137 +b=6356752.3142451802 +no_defs +x_0=543196.83521776402 +y_0=3622588.8619310018"

    BORDER_DE900_WGS84 = {
        'NW': { 'lat':'54.58546706','lon':'2.095883211' },
        'NO': { 'lat':'54.73806893','lon':'15.69697166' },
        'SO': { 'lat':'47.07156997','lon':'14.60482286' },
        'SW': { 'lat':'46.95361533','lon':'3.604382997' }
    }
    
    BORDER_DE900_KUGEL = {
        'NW': { 'xy':(-523462.2,-3758645.0), 'lat':54.5877, 'lon':2.0715 },
        'NO': { 'xy':(376537.8,-3758645.0), 'lat':54.7405, 'lon':15.7208 },
        'SO': { 'xy':(376537.8,-4658645.0), 'lat':47.0705, 'lon':15.7208 },
        'SW': { 'xy':(-523462.2,-4658645.0), 'lat':46.9526, 'lon':3.5889 }
    }
    
    COLORS_HG = {
        0:          '#FFFFFFD0', # no echo
        2147483648: '#FFFFFFD0', # no data
        1:          '#787878D0', # nicht klassifiziert
        16777216:   '#d3d3d3D0', # kein Niederschlag
        8192:       '#84009bD0', # Hagel
        4096:       '#ff9900D0', # Graupel
        64:         '#ffa7ffD0', # Schnee Bit 7
        80:         '#feff00D0', # Schneeregen Bits 5+7
        20:         '#ff0000D0', # Gefrierender Regen Bits 5+3
        16:         '#009901D0', # Regen Bit 5
        12:         '#f77676D0', # Gefrierender Sprühregen Bits 4+3
        8:          '#32ff00D0', # Sprühregen
    }
    
    HUE_HG = {
        8192:       291,         # Hagel
        4096:        36,         # Graupel
        64:         300,         # Schnee
        80:          60,         # Schneeregen
        20:           0,         # Gefrierender Regen
        16:         120,         # Regen
        12:           0,         # Gefrierender Sprühregen
        8:          108,         # Sprühregen
    }
    
    WAWA = {
        0:          None, # no echo
        2147483648: None, # no data
        1:          40,   # nicht klassifiziert
        16777216:   0,    # kein Niederschlag
        8192:       89,   # Hagel
        4096:       74,   # Graupel
        64:         70,   # Schnee Bit 7
        80:         67,   # Schneeregen Bits 5+7
        20:         64,   # Gefrierender Regen Bits 5+3
        16:         60,   # Regen Bit 5
        12:         54,   # Gefrierender Sprühregen Bits 4+3
        8:          50,   # Sprühregen
    }
    
    TEXT = {
        'de': {
            8192:       'Hagel',
            4096:       'Graupel',
            64:         'Schnee',
            80:         'Schneeregen',
            20:         'gefrierender Regen',
            16:         'Regen',
            12:         'gefrierender Sprühregen',
            8:          'Sprühregen',
            1:          'nicht klassifizierter Niederschlag',
            16777216:   'kein Niederschlag',
            0:          'kein Echo',
            2147483648: 'keine Daten'
        },
        'en': {
            8192:       'hail',
            4096:       'graupel',
            64:         'snow',
            80:         'sleet',
            20:         'freezing rain',
            16:         'rain',
            12:         'freezing drizzle',
            8:          'drizzle',
            1:          'precipitation of unknown kind',
            16777216:   'no precipitation',
            0:          'no echo',
            2147483648: 'no data'
        }
    }
    
    colors = dict()
    class_lock = threading.Lock()
    
    HEADER_FMT = {
        'BY':('I',10), # Produktlänge in Bytes
        'VS':('I',2),  # Formatversion
        'SW':('A',9),  # Software-Version
        'PR':('A',5),  # Genauigkeit der Daten
        'INT':('I',4), # Intervalldauer in Minuten
        'GP':('A',9),  # Anzahl der Pixel
        'VV':('I',4),  # Vorhersagezeitpunkt in Minuten nach der Messung
        'MF':('I',9),  # Modulflags
        'MS':('A',3),  # 
    }
    
    DATA_SIZE = {
        'HG':16777216, # 4 Bytes
        'WN':256,      # 2 Bytes
        'RV':256,      # 2 Bytes
        'WX':1,        # 1 Byte
        'RX':1,        # 1 Byte
        'EX':1,        # 1 Byte
        'WW':16777216, # 4 Bytes
    }

    def __init__(self, log_success=False, log_failure=True, verbose=0):
        self.created = time.time()
        # logging settings
        self.log_success = log_success
        self.log_failure = log_failure
        self.verbose = verbose
        # configuration data
        self.colors = DwdRadar.COLORS_HG
        self.data_width = 1100
        self.data_height = 1200
        #self.font_file = '/etc/weewx/skins/Belchertown1_3/lib/fonts/roboto/KFOlCnqEu92Fr1MmSU5fBBc9.ttf'
        self.font_file = '/etc/weewx/skins/Seasons/font/OpenSans-Regular.ttf'
        self.background = 'light'
        # data
        self.data = []
        self.header = dict()
        self.clutter_flag = list()
        self.station_flag = list()
        self.product = None
        self.version = None
        # initialize coordinate data
        self.init_coords()
    
    @classmethod
    def open(cls, fn, log_success=False, log_failure=True, verbose=0):
        """ create a DwdRadar instance from a file
        """
        if verbose: start_ts = time.time()
        if tarfile.is_tarfile(fn):
            # a set of records embedded in one tar file
            dwd = []
            with tarfile.open(fn) as tarf:
                dwd = cls._read_tarfile(tarf,log_success,log_failure,verbose)
        else:
            # one record in one file only, no forecast
            dwd = cls(log_success,log_failure,verbose)
            dwd.read_data(DwdRadar._decompress_file(fn))
        if verbose: print('elapsed time for loading from file: %.2f s' % (time.time()-start_ts))
        return dwd
    
    @classmethod
    def wget(cls, product, log_success=False, log_failure=True, verbose=0):
        """ create a DwdRadar instance from internet data
        """
        if verbose: start_ts = time.time()
        # 'PG' is in BUFR format, not in the format handled here.
        fn = {
            'HG':'HG_LATEST_000.bz2',
            'RV':'DE1200_RV_LATEST.tar.bz2',
            'WN':'WN_LATEST.tar.bz2',
            'RW':'raa01-rw_10000-latest-dwd---bin.bz2',
            'RY':'raa01-ry_10000-latest-dwd---bin.bz2',
            'SF':'raa01-sf_10000-latest-dwd---bin.bz2',
            'YW':'raa01-yw_10000-latest-dwd---bin.bz2',
            'RE':'%s',
            'RQ':'%s',
        }[product.upper()]
        # The base URL depends on the product.
        if product in {'HG','RV','WN'}:
            # HG actual precipitation type
            # RV actual precipitation amount and forecast
            # WN actual radar reflectivity factor dBZ and forecast
            url = DwdRadar.COMPOSITE_URL
        elif product in {'RE','RQ'}:
            # RQ calibrated precipitation analysis and forecast
            # RE analysis and forecast of the proportion of solid precipitation
            url = DwdRadar.RADVOR_URL
            reply = wget('%s/%s' % (url,product.lower()))
            if reply is None: return None
            fns = DwdRadar._list_directory(reply.decode(encoding='utf-8'))
        else:
            # RW, RY, SF, YW
            url = DwdRadar.RADOLAN_URL
        # The complete URL contains of the base URL, the product name in
        # lowercase and the filename
        url = '/'.join((url,product.lower(),fn))
        # Depending on the structure of the files on the DWD opendata server
        # different downloading methods apply.
        if product in {'RE','RQ'}:
            # Several files to download
            dwd = []
            for fn in fns:
                reply = wget(url % fn,log_success,log_failure)
                newdwd = cls(log_success,log_failure,verbose)
                if fn.endswith('.gz') or fn.endswith('.GZ'):
                    newdwd.read_data([gzip.decompress(reply)])
                else:
                    newdwd.read_data([bz2.decompress(reply)])
                dwd.append(newdwd)
        else:
            # One file to download only
            reply = wget(url,log_success,log_failure)
            if reply is None: return None
            if 'tar' not in fn:
                # one record in one file only
                dwd = cls(log_success,log_failure,verbose)
                dwd.read_data([bz2.decompress(reply)])
            else:
                # actual record and forecast included in one tar.bz2 file
                dwd = []
                with io.BytesIO(reply) as f:
                    with tarfile.open(fileobj=f) as tarf:
                        dwd = cls._read_tarfile(tarf,
                                                log_success,
                                                log_failure,
                                                verbose)
        if verbose: print('elapsed time for download: %.2f s' % (time.time()-start_ts))
        return dwd
    
    @classmethod
    def from_hg_rv(cls, hg, rv, log_success=False, log_failure=True, verbose=0):
        if verbose:
            print('timestamp hg',hg.timestamp,'rv',rv.timestamp)
        if hg.timestamp==rv.timestamp and hg.version==rv.version:
            dwd = cls(log_success,log_failure,verbose)
            dwd.product = 'HGRV'
            dwd.timestamp = hg.timestamp
            dwd.wmo_nr = hg.wmo_nr
            dwd.header = hg.header
            dwd.version = hg.version
            dwd.data = list(zip(hg.data,rv.data))
            dwd.no_data_value = rv.no_data_value
            dwd.out_of_range_value = rv.out_of_range_value
            dwd.created_hg = hg.created
            dwd.created_rv = rv.created
            dwd.init_coords()
            factor = pow(10,int(rv.header['PR'].strip()[1:]))
            yn = 100
            y0 = 10
            dwd.colors = dict()
            for hgval,hgcol in DwdRadar.COLORS_HG.items():
                hue = DwdRadar.HUE_HG.get(hgval,256)
                if hgval&8:
                    xs = 0.3/12
                elif hgval&64:
                    xs = 2.5/12
                else:
                    xs = 6.25/12
                a, b, c = hyperbel_color(y0,yn,xs)
                for i in range(4096):
                    idx = (hgval,i*factor)
                    sat = yn-a/(b*i*factor+c)
                    if hue<256:
                        #col = ImageColor.getrgb('hsv(%s,%s%%,100%%)' % (hue,math.log(i)/7.6*256 if i>0 else 0))
                        col = ImageColor.getrgb('hsv(%s,%s%%,100%%)' % (hue,sat))
                        dwd.colors[idx] = col+(0xD0,)
                    elif hgval==1:
                        sat = int(255-sat*255/100)
                        dwd.colors[idx] = (sat,sat,sat,0xD0)
                    else:
                        dwd.colors[idx] = ImageColor.getrgb(hgcol)
            return dwd
        return None
    
    @staticmethod
    def _decompress_file(fn):
        """ iterator to decompress a radar data file
        
            used internally only
        """
        with bz2.open(fn,'rb') as f:
            while True:
                reply = f.read1(4096)
                if reply==b'': break
                yield reply

    @classmethod
    def _read_tarfile(cls, tarf, log_success, log_failure, verbose):
        """ read a set of records, embedded in one tar file """
        added_data = []
        dwd = list()
        for member in tarf:
            ff = tarf.extractfile(member)
            newdwd = cls(log_success,log_failure,verbose)
            newdwd.read_data(ff)
            ff.close()
            if newdwd.product=='RV':
                added_data.append(newdwd.data)
            dwd.append(newdwd)
        if dwd and dwd[0].product=='RV':
            if verbose: start_ts = time.thread_time_ns()
            dwd[0].sum_data = list(map(newdwd._add_none,*added_data))
            if verbose: print('RV added data: elapsed CPU time %.3fs' % ((time.thread_time_ns()-start_ts)*1e-9))
        return dwd
    
    def _add_none(self, *x):
        try:
            if self.no_data_value in x:
                raise TypeError('no data value')
            result = sum(x)
        except TypeError:
            result = None
        return result
    
    @staticmethod
    def _list_directory(reply):
        """ read directory and get the names of the most recent records """
        fns = list()
        reply_len = len(reply)
        i = 0
        while True:
            i = reply.find('href="',i)
            if i<0: break
            i += 6
            fn = ''
            while i<reply_len and reply[i]!='"':
                fn += reply[i]
                i += 1
            fns.append(fn)
        fns.sort()
        if fns:
            x = fns[-1].split('_')
            fns = [fn for fn in fns if fn.startswith(x[0])]
        return fns

    def read_data(self, in_data):
        """ read radar data and convert to internal data structure
        
            Args:
                in_data (iterator or list of bytes): raw data
            
            Returns:
                nothing
            
            The result is saved to the internal structure.
        """
        if self.verbose: start_ts = time.thread_time()
        header = ""
        out_data = []
        self.clutter_flag = []
        self.station_flag = []
        isheader = True
        by = 0
        by = b''
        ct = 1
        length = 0
        data_size = 1
        for reply in in_data:
            length += len(reply)
            if isheader:
                i = reply.split(b'\x03',maxsplit=1)
                if self.verbose:
                    print('header',len(i[0]))
                header += i[0].decode('ascii',errors='replace')
                if len(i)<2:
                    # header is not complete --> look for more data
                    continue
                # the whole header is read --> decode it
                data_size, factor = self._decode_header(header)
                isheader = False
                reply = i[1]
            if by:
                reply = by+reply
                by = b''
            if data_size==1:
                format = '<%sB' % len(reply)
            elif data_size==16777216:
                i = len(reply)%4
                if i:
                    by = reply[-i:]
                    reply = reply[:-i]
                format = '<%sL' % int(len(reply)/4)
            else: # data_size==256
                if len(reply)%2:
                    by = reply[-1:]
                    reply = reply[:-1]
                format = '<%sH' % int(len(reply)/2)
            if reply:
                out_data.extend(struct.unpack(format,reply))
        if self.verbose:
            print('file length:',length)
            #print(header)
            time1_ts = time.thread_time()
        if data_size==256:
            # Bit 15     0x8000: clutter mark
            # Bit 14     0x4000: negative sign
            # Bit 13     0x2000: error mark
            # Bit 12     0x1000: station data instead of radar data, hail flag, 
            # Bit 11...0 0x0FFF: value
            # speed issues:
            #     About 90% of the run time is consumed by the calculation.
            #     An empty loop is short. Referencing values by `self.`
            #     takes more time then by local variables.
            if self.header.get('VV',0)==0:
                self.clutter_flag = [(x&0x8000)!=0 for x in out_data]
                self.station_flag = [(x&0x1000)!=0 for x in out_data]
            no_data_value = self.no_data_value
            out_data = [no_data_value if (i&0x2000) else (-(i&0x0FFF) if (i&0x4000) else (i&0x0FFF))*factor for i in out_data]
        if self.verbose: time2_ts = time.thread_time()
        # radar reflectivity factor
        if self.product in {'WN','WX','RX'}:
            no_data_value = self.no_data_value
            out_data = [0.5*i-32.5 if i<no_data_value else i for i in out_data]
        if self.verbose: time3_ts = time.thread_time()
        self.data = out_data
        # initialize coordinate data
        self.init_coords()
        if self.verbose:
            print(self.header)
            print('data',len(self.data),min(self.data),max(self.data))
            print('time elapsed %.3fs - flags %.3fs - convert %.3fs - %.3fs' % (time1_ts-start_ts,time2_ts-time1_ts,time3_ts-time2_ts,time.thread_time()-time3_ts))
    
    def _decode_header(self, header):
        """ decode the file header """
        if self.verbose: start_ts = time.thread_time()
        # product code
        self.product = header[0:2]
        # data size
        try:
            data_size = DwdRadar.DATA_SIZE[self.product]
        except LookupError:
            data_size = 256
        # issued
        self.timestamp_dt = datetime.datetime(
            int('20'+header[15:17]), # YY
            int(header[13:15]),      # MM
            int(header[2:4]),        # DD
            hour=int(header[4:6]),   # hh
            minute=int(header[6:8]), # mm
            tzinfo=datetime.timezone.utc
        )
        self.timestamp = self.timestamp_dt.timestamp()
        # WMO station code, for composite products 10000
        self.wmo_nr = header[8:13]
        # variable header
        header = header[17:]
        if self.verbose:
            print('Produktkennung:',self.product)
            print('Zeitpunkt der Messung:',self.timestamp_dt)
            print('Zeitpunkt der Messung:',time.strftime("%Y-%m-%d %H:%M:%S %z",time.localtime(self.timestamp)))
            print('Zeitpunkt der Messung:',self.timestamp)
            print('WMO-Nummer:',self.wmo_nr)
            #print(header)
        header_vals = dict()
        
        idx = ""
        val = ""
        ct = 0
        for ii in header:
            if idx=='BY' and not ii.isdigit() and ii!=' ':
                header_vals[idx] = val
                idx = ""
                val = ""
                ct = 0
            if ct:
                val += ii
                ct -= 1
                if ct==0:
                    if idx=='MS' and val.isdigit():
                        ct = int(val)
                        val = ""
                        continue
                    elif tp=='I':
                        header_vals[idx] = int(val)
                    else:
                        header_vals[idx] = val
                    idx = ""
                    val = ""
            else:
                idx += ii
                if idx in DwdRadar.HEADER_FMT:
                    ct = DwdRadar.HEADER_FMT[idx][1]
                    tp = DwdRadar.HEADER_FMT[idx][0]
        self.header = header_vals
        # no data value
        if self.product=='HG':
            self.no_data_value = 2147483648
            self.out_of_range_value = 2147483648
        elif self.product in {'WX','RX','EX'}:
            self.no_data_value = 250
            self.out_of_range_value = 249
        else:
            self.no_data_value = 0x29C4
            self.out_of_range_value = 4096
        # format version
        if 'VS' in header_vals:
            try:
                self.version = int(header_vals['VS'])
            except ValueError:
                self.version = None
        # data size
        if 'GP' in header_vals:
            # example 1200x1100
            x = header_vals['GP'].split('x')
            self.data_height = int(x[0])
            self.data_width = int(x[1])
            #print('GP','height',self.data_height,'width',self.data_width)
        # data accuracy
        if 'PR' in header_vals:
            x = header_vals['PR'].strip()
            if x[0]=='E' and x[1]=='-' and data_size==256:
                factor = pow(10,int(x[1:]))
                if self.verbose:
                    print('Genauigkeitsfaktor:',factor)
                #self.data = [(i&0x0FFF)*(-1 if (i&0x4000) else 1)*factor if (i&0xAFFF)<self.out_of_range_value else self.no_data_value for i in self.data]
            else:
                factor = 1.0
        else:
            factor = 1.0
        if self.verbose: time3_ts = time.thread_time()
        # colors
        if self.product=='HG':
            self.colors = {i[0]:ImageColor.getrgb(i[1]) for i in DwdRadar.COLORS_HG.items()}
        elif self.product in {'WX','RX','EX'}:
            self.colors = dict()
            for i in range(249):
                idx = i*factor
                if i==0:
                    col = (255,255,255)
                else:
                    col = ImageColor.getrgb('hsv(%s,100%%,100%%)' % (256-i))
                self.colors[idx] = col+(0xD0,)
            self.colors[self.no_data_value] = (255,255,255,0xD0) # no data 0x29C4
        else:
            try:
                DwdRadar.class_lock.acquire()
                self.colors = DwdRadar.colors.get(self.product,{}).get(factor,None)
            finally:
                DwdRadar.class_lock.release()
            if self.colors is None:
                self.colors = DwdRadar.init_colors_2byte(self.product,factor)
                try:
                    DwdRadar.class_lock.acquire()
                    if self.product not in DwdRadar.colors:
                        DwdRadar.colors[self.product] = dict()
                    DwdRadar.colors[self.product][factor] = self.colors
                finally:
                    DwdRadar.class_lock.release()
        if self.verbose: print('time elapsed in _decode_header: %.2fs' % (time.thread_time()-start_ts))
        return data_size, factor
    
    def init_coords(self):
        """ initialize coordinate data
        """
        if (self.version is None or 
            (self.product in {'HG','WN','RV','HGRV'} and self.version>=5)):
            self.coords = DwdRadar.BORDER_DE1200_WGS84
            self.coords.update(MAP_LOCATIONS_DE1200_WGS84)
            self.lines = []
            if self.verbose and self.version is not None:
                print('Grid initialized to DE1200 WGS84')
        elif self.data_height==900 and self.data_width==900 and self.version>=5:
            self.coords = DwdRadar.BORDER_DE900_WGS84
            self.lines = []
            if self.verbose:
                print('Grid initialized to DE900 WGS84')
        elif self.data_height==900 and self.data_width==900 and self.version<5:
            self.coords = DwdRadar.BORDER_DE900_KUGEL
            self.lines = []
            if self.verbose:
                print('Grid initialized to DE900 Kugel')

    @staticmethod
    def init_colors_2byte(product, factor):
        colors = dict() # DwdRadar.COLORS_WN # 1...0x0FFF 1...4095
        for i in range(4096):
            if product=='WN':
                idx = i*factor/2-32.5
            else:
                idx = i*factor
            if i==0:
                col = (255,255,255)
            else:
                if product=='RW':
                    # RW factor 0.1 precipitation
                    col = 240-math.log(i)/8.3*240
                elif product=='WN':
                    # WN factor 0.1 dBZ
                    col = 240-(idx if idx>0 else 0)/85*240
                elif product=='RV':
                    # RV factor 0.01 precipitation
                    #col = 256-math.log(i)/7.6*256
                    col = 240-math.log(0.02425*i+0.03)*26.632997406928514-93.39014738656778
                    if col<0 and col>-30:
                        col += 360
                if col<0: col=330
                # The defined range for hue is 0 to 360 here.
                # 240 blue - 180 cyan - 120 green - 60 yellow - 0 red
                col = ImageColor.getrgb('hsv(%s,100%%,100%%)' % col)
            colors[idx] = col+(0xD0,)
        colors[0x29C4] = (255,255,255,0xD0) # no data 0x29C4
        return colors

    def get_index(self, xy):
        """ get the index in self.data for a certain location
            
            Args:
                xy (tuple): coordinate pair in meters
            
            Returns:
                int: index
        """
        cx = (xy[0]-self.coords['SW']['xy'][0])/1000
        cy = (xy[1]-self.coords['SW']['xy'][1])/1000
        if cx>self.data_width or cx<0.0:
            raise LookupError('x %s out of range' % xy[0])
        if cy>self.data_height or cy<0.0:
            raise LookupError('y %s out of range' % xy[1])
        if cx==self.data_width: cx -= 0.1
        if cy==self.data_height: cy -= 0.1
        return int(cy)*self.data_width+int(cx)
    
    def get_value(self, xy):
        """ get the radar reading for a certain location 
            
            Args:
                xy (tuple): coordinate pair in meters
            
            Returns:
                int: reading of the location described by xy
        """
        return self.data[self.get_index(xy)]
    
    def get_float(self, xy):
        val = self.get_value(xy)
        return val if val!=self.no_data_value else None
    
    def get_clutter_flag(self, xy):
        if self.clutter_flag:
            return self.clutter_flag[self.get_index(xy)]
        else:
            return None
    
    def get_station_flag(self, xy):
        if self.station_flag:
            return self.station_flag[self.get_index(xy)]
        else:
            return None
    
    def get_wawa(self, xy):
        """ get the wawa value out of the radar reading for a certain location
            
            Args:
                xy (tuple): coordinate pair in meters
            
            Returns:
                int: wawa code of the location described by xy
        """
        if self.product=='HGRV':
            try:
                x = self.get_value(xy)
                return merge_wawa(DwdRadar.WAWA[x[0]],x[1])
            except LookupError:
                return None
        if self.product!='HG': 
            raise ValueError('product '+self.product+' does not provide precipitation type')
        try:
            return DwdRadar.WAWA[self.get_value(xy)]
        except LookupError:
            return None
    
    def get_rainrate(self, xy):
        """ get the precipitation rate for products that provide it 
        
            Args:
                xy (tuple): tuple of easting and northing of the location
                            to get the value for, in meters
            
            Returns:
                float: precipitation rate in mm/h
        
        """
        if self.product=='RV':
            y = self.get_value(xy)
        elif self.product=='HGRV':
            y = self.get_value(xy)[1]
        else:
            raise ValueError('product %s does not provide precipitation' % self.product)
        try:
            if y==self.no_data_value: raise ValueError('no data')
            return y*12
        except (LookupError,TypeError,ValueError,ArithmeticError):
            return None
    
    def get_2h_rain_forecast(self, xy):
        if self.product!='RV': return
        try:
            return self.sum_data[self.get_index(xy)]
        except (LookupError,AttributeError):
            return None

    def map(self,x,y,width,height, filter=[], background_img=None, svg=False, credits=None):
        """ draw a map
        
            Args:
                x (int, float): left image border in pixels 0...1100
                y (int, float): lower (!) image border in pixels 0...1200
                width (int, float): image width in pixels 0...1100
                height (int, float): image height in pixels 0...1200
        """
        start_ts = time.time()
        time0_ts = time.thread_time_ns()
        x = int(x)
        y = int(y)
        if (x+width)>self.data_width:
            width = self.data_width-x
        if (y+height)>self.data_height:
            height = self.data_height-y
        if width>512:
            scale = 1.0
        elif width>300:
            scale = 2.0
        elif width>256:
            scale = 3.0
        elif width>200:
            scale = 4.0
        elif width>166:
            scale = 5.0
        elif width>128:
            scale = 6.0
        elif width>100:
            scale = 8.0
        elif width>50:
            scale = 10.0
        else:
            scale = 20.0
        if self.verbose:
            print('scale: %s' % scale)
        ww = width*scale
        hh = ww*height/width
        if self.background and self.background[0]=='#':
            if len(self.background)==4:
                background_color = ImageColor.getrgb('#'+
                    self.background[1]+self.background[1]+
                    self.background[2]+self.background[2]+
                    self.background[3]+self.background[3]+
                    'FF')
            else:
                background_color = ImageColor.getrgb(self.background[:7]+'FF')
            dark_background = self.background[1]<='4'
        else:
            dark_background = self.background=='dark'
            background_color = ImageColor.getrgb('#000000FF' if dark_background else '#FFFFFFFF')
        if svg:
            baseimg = None
            img = '<svg xmlns="http://www.w3.org/2000/svg" version="1.1" width="%s" height="%s" viewBox="%s %s %s %s">\n' % (ww,hh,x,1200-y-height,width,height)
            font_size = 16
        else:
            if scale==1.0:
                img_bytes = list()
            else:
                img = Image.new('RGBA',(int(width*scale),int(height*scale)),color=(0,0,0,0))
                draw = ImageDraw.Draw(img)
                if self.verbose:
                    print('Abmessung der Bilddatei',img.size)
            if background_img:
                baseimg = background_img
            elif scale==1.0:
                baseimg_bytes = list()
            else:
                baseimg = Image.new('RGBA',(int(width*scale),int(height*scale)),color=(0,0,0,0))
                basedraw = ImageDraw.Draw(baseimg)
            if (width*scale)>=640:
                font_size = 16
            elif (width*scale)<320:
                font_size = 8
            else:
                font_size = int(width*scale*0.025)
            if self.verbose:
                print('font size: %s' % font_size)
            fnt=ImageFont.truetype(self.font_file,font_size)
        # set points according to radar reading
        time1_ts = time.thread_time_ns()
        # Separate loops for xx and yy are much faster than one loop over
        # self.data with calculating xx and yy from the list index.
        # 68% of the time is consumed by ImageColor.getrgb(). So this 
        # statement is moved to read_data(). Color is expressed by a
        # tuple of (R,G,B,A).
        data = self.data
        colors = self.colors
        # This index points to the left-most pixel in the line obove the
        # top line of the image.
        idx0 = (y+height)*self.data_width+x
        for yy in range(height):
            # go from top to bottom
            # Move the index one line down the image
            idx0 -= self.data_width
            # Get the line in the image, measured from top
            if scale==1.0:
                yyy = yy
            else:
                yyy = yy*scale
            for xx in range(width):
                # go from left to right
                val = data[idx0+xx]
                col = colors.get(val,(1,2,3,128))
                if dark_background and col[:3]==(255,255,255):
                    col = (0,0,0,col[3])
                if self.product=='HGRV': val = val[1]
                if svg:
                    img += '<rect x="%s" y="%s" width="1" height="1" fill="#%02X%02X%02X" fill-opacity="%.2f" />\n' % (x+xx,1200-yy-y-1,col[0],col[1],col[2],col[3]/255)
                else:
                    try:
                        if scale==1.0:
                            #draw.point((xx,yyy),fill=col)
                            img_bytes.extend(col)
                            if not background_img:
                                baseimg_bytes.extend((0,0,0,0) if val==self.no_data_value else background_color)
                            #if val!=self.no_data_value and not background_img:
                            #    basedraw.point((xx,yyy),fill=background_color)
                        else:
                            xxx = xx*scale
                            draw.rectangle([xxx,yyy,xxx+(scale-1.0),yyy+(scale-1.0)],fill=col)
                            if val!=self.no_data_value and not background_img:
                                basedraw.rectangle([xxx,yyy,xxx+(scale-1.0),yyy+(scale-1.0)],fill=background_color)
                    except IndexError as e:
                        print(e,xx,height-yy,col)
        if scale==1.0:
            img = Image.frombytes('RGBA',(width,height),bytes(img_bytes))
            draw = ImageDraw.Draw(img)
            if not background_img:
                baseimg = Image.frombytes('RGBA',(width,height),bytes(baseimg_bytes))
                basedraw = ImageDraw.Draw(baseimg)
        time2_ts = time.thread_time_ns()
        # mark locations
        for location,coord in self.coords.items():
            if location not in {'NW','NO','SW','SO'} and location not in filter and scale>=coord['scale']:
                cx = (coord['xy'][0]-self.coords['SW']['xy'][0])/1000
                cy = (coord['xy'][1]-self.coords['SW']['xy'][1])/1000
                peak = coord.get('peak',False)
                if location in {'Dresden','Chemnitz','Aschberg'}:
                    # label besides the dot
                    y_off = 4+font_size/4
                    x_off = 6
                elif location in {'Fichtelberg','Zugspitze','Jelení','Weimar'}:
                    # label right below the dot
                    y_off = 4-font_size/4
                    x_off = 4
                else: 
                    # label right above the dot
                    y_off = 4+font_size
                    x_off = 4
                if svg:
                    img += '<circle cx="%s" cy="%s" r="%.2f" fill="%s" />\n' % (cx,1200-cy,width/150,'#FFF' if dark_background else '#000')
                else:
                    cx -= x
                    cy -= y
                    if cx>=0 and cy>=0:
                        if peak:
                            draw.polygon([cx*scale-2.30940108,(height-cy)*scale+1.333333,cx*scale+2.30940108,(height-cy)*scale+1.333333,cx*scale,(height-cy)*scale-2.666667],fill=ImageColor.getrgb('#FFF' if dark_background else '#000'))
                        else:
                            draw.ellipse([cx*scale-2,(height-cy)*scale-2,cx*scale+2,(height-cy)*scale+2],fill=ImageColor.getrgb('#FFF' if dark_background else '#000'))
                        draw.text((cx*scale+x_off,(height-cy)*scale-y_off),location,fill=ImageColor.getrgb('#FFF' if dark_background else '#000'),font=fnt)
        time3_ts = time.thread_time_ns()
        try:
            vv = int(self.header['VV'])*60
        except (LookupError,ValueError,TypeError,ArithmeticError):
            vv = 0
        ts_str = time.strftime("%d.%m.%Y %H:%M %z",time.localtime(self.timestamp+vv))
        if self.product=='HG':
            product_str = 'Niederschlagsart 2m über Grund\n'
        elif self.product=='WN':
            product_str = 'Radarreflektivität dBZ\n'
        elif self.product=='RV':
            product_str = 'Regenintensität\n'
        else:
            product_str = ''
        # copyright notice
        if self.lines or background_img is not None:
            bcptxt = 'Geographie © %s\n' % (self.lines_copyright if self.lines_copyright else 'Kartendatenlieferant')
        else:
            bcptxt = ''
        txt = '%sHerausgegeben %s\nDatenbasis Deutscher Wetterdienst\n%s%s' % (product_str,ts_str,bcptxt,credits if credits else '© Wetterstation Wöllsdorf')
        if svg:
            pass
        else:
            txtfnt=ImageFont.truetype(self.font_file,int(font_size*0.9))
            # fade the background a little bit
            txtimg = Image.new("RGBA",img.size,(0,0,0,0))
            txtdraw = ImageDraw.Draw(txtimg)
            bbox = txtdraw.multiline_textbbox(
                    (7,height*scale-5),
                    txt,
                    font=txtfnt,
                    anchor="ld")
            txtdraw.rectangle((0,bbox[1]-5,bbox[2]+5,height*scale),fill=(0,0,0,128) if dark_background else (255,255,255,128))
            # draw the copyright notice
            txtdraw.multiline_text(
                (7,height*scale-5),
                txt,
                fill=ImageColor.getrgb('#FFF' if dark_background else '#000'),
                font=txtfnt,
                anchor="ld")
            # mix it into the image
            newimg = Image.alpha_composite(img,txtimg)
            txtimg.close()
            img.close()
            img = newimg
        time4_ts = time.thread_time_ns()
        if not background_img:
            col0 = ImageColor.getrgb('#FFF' if dark_background else '#000')
            for line in self.lines:
                if line['color']:
                    col = line['color']
                else:
                    col = col0
                polygon = line['type']=='Polygon'
                xy = []
                for coord in line['coordinates']:
                    xx = (coord['xy'][0]-self.coords['SW']['xy'][0])/1000-x
                    yy = (coord['xy'][1]-self.coords['SW']['xy'][1])/1000-y
                    xy.append((xx*scale,(height-yy)*scale))
                if svg:
                    pass
                else:
                    if polygon:
                        basedraw.polygon(xy,fill=col)
                    else:
                        basedraw.line(xy,fill=col,width=1)
        time5_ts = time.thread_time_ns()
        if svg:
            img += '</svg>\n'
        else:
            newimg = Image.alpha_composite(baseimg,img)
            img.close()
            img = newimg
        if self.verbose:
            print('elapsed time for creating the image: %.2fs' % (time.time()-start_ts))
        logdbg('elapsed CPU time for creating the image: init %.3fs, readings %.3fs, cities %.3fs, copyright %.3fs, lines %.3fs, all %.3fs' % (
        (time1_ts-time0_ts)/1000000000,
        (time2_ts-time1_ts)/1000000000,
        (time3_ts-time2_ts)/1000000000,
        (time4_ts-time3_ts)/1000000000,
        (time5_ts-time4_ts)/1000000000,
        (time.thread_time_ns()-time0_ts)/1000000000))
        baseimg.close()
        return img, None, product_str, txt, scale
        return img, baseimg, product_str, txt, scale
    
    def save_map(self, fn, img, title=None, desc=None, credits=None):
        """ Save a previously created map to a file
            
            Args:
                fn (str): file path
                img (Image): image to save
            
            Returns:
                nothing
        """
        if self.verbose: start_ts = time.time()
        copyright = [
            credits if credits else 'Wetterstation Wöllsdorf',
            'Deutscher Wetterdienst'
        ]
        if self.lines and self.lines_copyright:
            copyright.append(str(self.lines_copyright))
        if fn.endswith('.png'):
            try:
                pnginfo = PngImagePlugin.PngInfo()
                if title:
                    pnginfo.add_text('Title',str(title))
                if desc:
                    pnginfo.add_text('Description',str(desc),zip=True)
                pnginfo.add_text('Copyright','; '.join(copyright))
                pnginfo.add_text('Software','weewx-DWD')
                pnginfo.add_text('Source','Wetterradarverbund des Deutschen Wetterdienstes (DWD)')
                ti = time.gmtime(self.timestamp)
                mon = ('','JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC')[ti.tm_mon]
                pnginfo.add_text('Creation Time','%02d %s %04d %02d:%02d:%02d +0000' % (ti.tm_mday,mon,ti.tm_year,ti.tm_hour,ti.tm_min,ti.tm_sec))
            except (ValueError,TypeError,LookupError):
                pnginfo = None
        try:
            fn_tmp = '%s.tmp%s' % (fn[:-4],fn[-4:])
            if fn.endswith('.png') and pnginfo is not None:
                img.save(fn_tmp,pnginfo=pnginfo)
            else:
                img.save(fn_tmp)
            os.rename(fn_tmp,fn)
        except (ValueError,OSError) as e:
            if self.log_failure:
                logerr("could not create '%s': %s %s" % (fn,e.__class__.__name__,e))
            raise
        else:
            if self.log_success:
                loginf("map '%s' saved" % fn)
        if self.verbose:
            print('elapsed time for saving the image: %.2f s' % (time.time()-start_ts))

    def load_coordinates(self, fn):
        """ read a file of locations and their coordinates 
        
            Data is used when creating maps.
        
            Args:
                fn (str): path of a file containing a whitespace separated 
                          table
            
            Returns:
                nothing
        """
        coords = dict()
        with open(fn,'rt') as f:
            for line in f:
                x = line.split()
                coords[x[2]] = {'xy':(float(x[0]),float(x[1])),'lat':x[3],'lon':x[4]}
        coords.update(DwdRadar.BORDER_DE1200_WGS84)
        self.coords = coords
        if self.verbose:
            print('NO-NW x',coords['NO']['xy'][0]-coords['NW']['xy'][0])
            print('SO-SW x',coords['SO']['xy'][0]-coords['SW']['xy'][0])
            print('NW-SW y',coords['NW']['xy'][1]-coords['SW']['xy'][1])
            print('NO-SO y',coords['NO']['xy'][1]-coords['SO']['xy'][1])
    
    def print_coordinates(self):
        """ print the list of locations and their actual readings """
        print('%-20s %8s %8s %12s %12s %s' % ('location','easting','northing','latitude','longitude','reading'))
        print('%-20s %8s %8s %12s %12s %s' % ('-'*20,'-'*8,'-'*8,'-'*12,'-'*12,'-'*10))
        for location,coord in self.coords.items():
            print('%-20s %8.0f %8.0f %12s %12s %s' % (
                location,
                coord['xy'][0]-self.coords['SW']['xy'][0],
                coord['xy'][1]-self.coords['SW']['xy'][1],
                coord['lat'],
                coord['lon'],
                self.get_value(coord['xy'])
            ))
    
    def load_lines(self, fn, copyright):
        """ read a file containing line data to draw on maps """
        lines = []
        start = True
        col = None
        polygon = False
        with open(fn, "rt") as f:
            for line in f:
                x = line.split()
                if x[0]=='*':
                    start = True
                    if len(x)>=3 and x[2].startswith('COLOR='):
                        try:
                            if '"' in x[2]:
                                col = x[2].split('"')[1]
                            elif "'" in x[2]:
                                col = x[2].split("'")[1]
                            else:
                                raise ValueError('invalid COLOR specification')
                            if col.startswith('auto'):
                                col = None
                            else:
                                col = ImageColor.getrgb(col)
                        except (LookupError,ValueError):
                            # string is not a valid color specification
                            pass
                    elif len(x)>=3 and x[2].upper().startswith('POLYGON'):
                        polygon = True
                else:
                    if start:
                        lines.append({
                            'coordinates':[],
                            'color':col,
                            'type':'Polygon' if polygon else 'LineString'
                        })
                    lines[-1]['coordinates'].append({'xy':(float(x[0]),float(x[1]))})
                    start = False
                    polygon = False
        self.lines = lines
        self.lines_copyright = str(copyright)
    
    def set_background_color(self, color):
        """ set the background color """
        if isinstance(color,tuple):
            col = color
        else:
            col = ImageColor.getrgb(str(color))
        if len(col)==3:
            col = col+(0xD0,)
        self.colors[self.no_data_value] = col

class DwdRadarThread(BaseThread):

    @property
    def provider_name(self):
        return 'DWD'
        
    @property
    def provider_url(self):
        return 'https://www.dwd.de'

    def __init__(self, name, conf_dict, archive_interval):
        # get logging configuration
        log_success = weeutil.weeutil.to_bool(conf_dict.get('log_success',False))
        log_failure = weeutil.weeutil.to_bool(conf_dict.get('log_failure',True))
        # initialize thread
        super(DwdRadarThread,self).__init__(name='DWD-Radar-'+name,log_success=log_success,log_failure=log_failure)
        # archive interval
        self.query_interval = weeutil.weeutil.to_int(archive_interval)
        # Note: The German Weather Service DWD releases radar data every
        #       5 minutes. So it is no use to query them more often.
        if self.query_interval<300:
            self.query_interval = 300
            logdbg("thread '%s': The German Weather Service DWD releases radar data every 5 minutes. So it is no use to query them more often." % self.name)
        # locations to report
        self.locations = conf_dict['locations']
        self.maps = conf_dict['maps']
        # target path
        self.target_path = conf_dict['path']
        # product
        self.product = conf_dict['model']
        self.filter = conf_dict.get('filter',[])
        # data
        self.data = []
        self.lock = threading.Lock()
        for map in self.maps:
            if 'background_img' in self.maps[map]:
                self.maps[map]['background_img'] = Image.open(self.maps[map]['background_img'])
            else:
                self.maps[map]['background_img'] = None
        self.hgrv_queue = None
        self.forecast = dict()
    
    def getRecord(self):
        # Get the last 5 minutes border
        last5m = time.time()
        last5m -= last5m%300
        # Download the radar data
        try:
            dwd = DwdRadar.wget(self.product,self.log_success,self.log_failure)
            if dwd is None: 
                if self.log_failure:
                    logerr("thread '%s': error downloading data" % self.name)
                return
        except (ConnectionError,OSError) as e:
            if self.log_failure:
                logerr("thread '%s': download error %s %s" % (self.name,e.__class__.__name__,e))
            return
        # If the file includes forecasts, find the record of the actual data
        if isinstance(dwd,list):
            # data include actual data and forecast
            logdbg("radar file contains %s records" % len(dwd))
            for ii in dwd:
                # test shutdown request
                if not self.running: return
                # forecast indicator
                try:
                    vv = int(ii.header['VV'])
                except (LookupError,TypeError):
                    vv = 0
                # remember actual data record
                if vv==0: 
                    self.cache_readings(ii,last5m)
                    self.queue_for_hgrv(ii)
                    break
            if dwd[0].product=='RV':
                self.cache_forecast(dwd)
            try:
                for map in self.maps:
                    # test shutdown request
                    if not self.running: return
                    # include forecast?
                    with_forecast = self.maps[map].get('forecast','none').lower()
                    imgs = []
                    descs = []
                    scale = 1.0
                    for ii in dwd:
                        # test shutdown request
                        if not self.running: break
                        # forecast indicator
                        vv = int(ii.header['VV'])
                        # remember actual data record
                        if vv==0: dwd0 = ii
                        # create map image
                        if vv==0 or with_forecast in {'png','gif'}:
                            img, desc, scale = self.write_map(map,ii,vv,save_forecast=with_forecast=='png')
                            if img:
                                # add the time at the bottom right corner
                                try:
                                    if ii.background and ii.background[0]=='#':
                                        dark_background = ii.background[1]<='4'
                                    else:
                                        dark_background = ii.background=='dark'
                                    txtdraw = ImageDraw.Draw(img)
                                    txtdraw.text(
                                        img.size,
                                        time.strftime('%H:%M ',time.localtime(ii.timestamp+vv*60)),
                                        fill=ImageColor.getrgb('#FFF' if dark_background else '#000'),
                                        font=ImageFont.truetype(ii.font_file,int((img.height/1000.0)**0.25*32)),
                                        anchor='rd')
                                except (TypeError,ValueError,ArithmeticError,LookupError):
                                    pass
                                # add to the list of images and descriptions
                                imgs.append(img)
                                descs.append(desc)
                    # animated GIF file
                    if with_forecast=='gif' and imgs and self.running:
                        if self.maps[map].get('prefix'):
                            fn = self.maps[map]['prefix']+'Radar-'+dwd0.product+'.gif'
                        else:
                            fn = 'radar-'+dwd0.product+'.gif'
                        fn = os.path.join(self.target_path,fn)
                        try:
                            # how long one image is shown
                            wt = weeutil.weeutil.to_float(
                                self.maps[map].get('animation_interval')
                            )
                            if wt is None or wt<=1:
                                wt = int(scale*100) if scale<3.0 else 300
                            st = wt+400
                            # save as animated GIF
                            imgs[0].save(fn,
                                     save_all=True,
                                     append_images=imgs[1:],
                                     duration=[st]+[wt]*(len(imgs)-2)+[1000],
                                     loop=0,
                                     comment=descs[0])
                        except (ValueError,OSError) as e:
                            if self.log_failure:
                                logerr("thread '%s': error saving '%s' %s %s" % (self.name,fn,e.__class__.__name__,e)) 
                        else:
                            if self.log_success:
                                loginf("thread '%s': animated GIF %s saved" % (self.name,fn))
                    # close images and free memory
                    while imgs:
                        img = imgs.pop()
                        if img: img.close()
            except (LookupError,TypeError) as e:
                if self.log_failure:
                    logerr("thread '%s': invalid forecast indicator %s %s" % (self.name,e.__class__.__name__,e))
                return
        else:
            # actual data only
            # data
            self.cache_readings(dwd,last5m)
            # create map image
            for map in self.maps:
                # test shutdown request
                if not self.running: return
                img, _, _ = self.write_map(map,dwd,0,False)
                if img: img.close()
            self.queue_for_hgrv(dwd)

    def cache_forecast(self, dwds):
        #start_ts = time.time()
        start = list()
        stop = list()
        try:
            for dwd in dwds:
                vv = int(dwd.header['VV'])
                ts = dwd.timestamp+vv*60
                start.append(ts-300)
                stop.append(ts)
        except (LookupError,AttributeError,ValueError,TypeError):
            return
        vals = {
            'start': (start,'unix_epoch','group_time'),
            'stop': (stop,'unix_epoch','group_time')
        }
        for location in self.locations:
            if not self.running: return
            try:
                xy = self.locations[location]['xy']
                if 'prefix' in self.locations[location] and self.locations[location]['prefix']:
                    prefix = self.locations[location]['prefix']+'Radar'+dwds[0].product
                else:
                    prefix = 'radar'+dwds[0].product
                val = list()
                for dwd in dwds:
                    if dwd.product=='RV':
                        val.append(dwd.get_rainrate(xy))
                val = (val,'mm_per_hour','group_rainrate')
                vals['%sRainRateForecast' % prefix] = val
            except (LookupError,ValueError,TypeError,ArithmeticError,NameError) as e:
                if self.log_failure:
                    logerr("thread '%s': could not assign forecast %s %s" % (self.name,e.__class__.__name__,e))
        #loginf("thread '%s': cache_forecast %.2fs" % (self.name,time.time()-start_ts))
        try:
            self.lock.acquire()
            self.forecast = vals
        finally:
            self.lock.release()
    
    def queue_for_hgrv(self, dwd):
        """ queue data for HGRV thread """
        if self.hgrv_queue:
            try:
                self.hgrv_queue.put(dwd, block=False)
            except queue.Full as e:
                if self.log_failure:
                    logerr("thread '%s': HGRV queue error %s %s" % (self.name,e.__class__.__name__,e))
    
    def cache_readings(self, dwd, last5m):
        """ get readings and cache them
        
            process all the locations defined in configuration and get the
            readings for those locations and cache them
            
        """
        logdbg("cache_readings %s" % dwd.timestamp)
        # Is this record released after the last 5 minutes border?
        if dwd.timestamp<last5m:
            loginf("thread '%s': got data from previous interval. radar timestamp %s, last5m %s" % (
                self.name,
                time.strftime("%H:%M",time.localtime(dwd.timestamp)),
                time.strftime("%H:%M",time.localtime(last5m))
            ))
            if dwd.product=='HGRV':
                loginf("thread '%s': got data from previous interval. created HGRV %s, HG %s, RV %s" % (
                    self.name,
                    time.strftime("%H:%M:%S",time.localtime(dwd.created)),
                    time.strftime("%H:%M:%S",time.localtime(dwd.created_hg)),
                    time.strftime("%H:%M:%S",time.localtime(dwd.created_rv))
                ))
        #start_ts = time.time()
        # Note: prefix is added in _to_weewx() in weatherservices.py, not here
        data = dict()
        try:
            data['dateTime'] = (int(dwd.timestamp),'unix_epoch','group_time')
            data['interval'] = (5,'minute','group_interval')
        except (LookupError,ValueError,TypeError,ArithmeticError,NameError) as e:
            if self.log_failure:
                logerr("thread '%s': could not assign timestamp %s %s" % (self.name,e.__class__.__name__,e))
        for location in self.locations:
            # test shutdown request
            if not self.running: return
            try:
                xy = self.locations[location]['xy']
                if 'prefix' in self.locations[location] and self.locations[location]['prefix']:
                    prefix = self.locations[location]['prefix']+'Radar'+dwd.product
                else:
                    prefix = 'radar'+dwd.product
                if dwd.product=='HG':
                    # precipitation type
                    data[prefix+'Value'] = (dwd.get_value(xy),None,None)
                    data[prefix+'Wawa'] = (dwd.get_wawa(xy),'byte','group_wmo_wawa')
                elif dwd.product=='WN':
                    # radar reflectivity factor
                    data[prefix+'DBZ'] = (dwd.get_float(xy),'dB','group_db')
                elif dwd.product=='RV':
                    # 5 minute precipitation
                    data[prefix+'Rain'] = (dwd.get_float(xy),'mm','group_rain')
                    data[prefix+'RainRate'] = (dwd.get_rainrate(xy),'mm_per_hour','group_rainrate')
                    data[prefix+'Rain2hForecast'] = (dwd.get_2h_rain_forecast(xy),'mm','group_rain')
                elif dwd.product=='HGRV':
                    # combined precipitation type (HG) and amount (RV)
                    data[prefix[:-4]+'Wawa'] = (dwd.get_wawa(xy),'byte','group_wmo_wawa')
                    data[prefix[:-4]+'Rainrate'] = (dwd.get_rainrate(xy),'mm_per_hour','group_rainrate')
                data[prefix+'DateTime'] = (int(dwd.timestamp),'unix_epoch','group_time')
            except (LookupError,ValueError,TypeError,ArithmeticError,NameError) as e:
                if self.log_failure:
                    logerr("thread '%s': could not assign reading %s %s" % (self.name,e.__class__.__name__,e))
        #loginf("thread '%s': cache_readings %.2fs" % (self.name,time.time()-start_ts))
        try:
            self.lock.acquire()
            self.data.append((dwd.timestamp,data))
            while len(self.data)>0 and self.data[0][0]<(time.time()-3600):
                del self.data[0]
        finally:
            self.lock.release()
    
    def write_map(self, map, dwd, vv, save_forecast):
        """ write map
        """
        try:
            fn = '' if vv==0 else '-%03d' % vv
            if self.maps[map].get('prefix'):
                fn = '%sRadar-%s%s.png' % (self.maps[map]['prefix'],dwd.product,fn)
            else:
                fn = 'radar-%s%s.png' % (dwd.product,fn)
            fn = os.path.join(self.target_path,fn)
            size = self.maps[map]['map']
            dwd.background = self.maps[map].get('background','light')
            if 'place_label_font_path' in self.maps[map]:
                dwd.font_file = self.maps[map]['place_label_font_path']
            if 'borders' in self.maps[map] and self.maps[map]['background_img'] is None:
                dwd.load_lines(os.path.join(self.target_path,self.maps[map]['borders']),self.maps[map].get('borders_copyright','Kartendatenlieferant'))
            else:
                dwd.lines_copyright = self.maps[map].get('borders_copyright','Kartendatenlieferant')
            img, self.maps[map]['background_img'], title, desc, scale = dwd.map(
                    size[0], # x
                    size[1], # y
                    size[2], # width
                    size[3], # height
                    filter=self.maps[map].get('filter',[]),
                    background_img=self.maps[map]['background_img'],
                    credits=self.maps[map].get('credits'))
            if vv==0 or save_forecast:
                if self.maps[map].get('name'):
                    title = '%s %s' % (title,self.maps[map]['name'])
                dwd.save_map(fn, img, title=title, desc=desc, credits=self.maps[map].get('credits'))
            return img, desc, scale
        except (LookupError,ValueError,TypeError,ArithmeticError,NameError) as e:
            if self.log_failure:
                logerr("thread '%s': error writing map %s %s" % (self.name,e.__class__.__name__,e))
            return None, None, 1.0

    def get_data(self, ts):
        data = dict()
        if self.is_alive():
            try:
                self.lock.acquire()
                for dd in self.data:
                    if dd[0]>=ts: break
                    data = dd[1]
            finally:
                self.lock.release()
        try:
            interval = data['interval'][0]
        except LookupError:
            interval = 5 # minutes
        logdbg('get_data(%s) %s' % (ts,data))
        return data,interval
    
    def get_forecast(self):
        if not self.is_alive(): return None
        try:
            if not self.lock.acquire(timeout=5):
                raise RuntimeError("thread '%s': could not acquire lock for reading data" % self.name)
            forecast = self.forecast
        finally:
            if self.lock.locked():
                self.lock.release()
        return forecast
    
    def random_time(self, waiting):
        """ do a little bit of load balancing """
        ti = super(DwdRadarThread,self).random_time(waiting)
        # RV needs a lot of time to process. So try to start loading
        # earlier.
        if self.product=='RV' and ti>-30:
            ti -= 30
            if (waiting+ti)<0.1: ti = 0.1-waiting
        return ti


class HgRvThread(DwdRadarThread):

    def __init__(self, name, conf_dict, archive_interval):
        super(HgRvThread,self).__init__(name, conf_dict, archive_interval)
        self.hg = None
        self.rv = None
        self.data_processed = False

    def waiting_time(self):
        """ How long to wait before the next getRecord() call 
        
            New data do not arrive earlier than 60 seconds before the next
            5 minutes boundary. So we can easily waiting until then before
            checking for new data in getRecord()
        """
        process_time = 31
        waiting = self.query_interval-time.time()%self.query_interval
        if self.data_processed:
            # Data is processed. We are about to wait for the next interval. 
            self.data_processed = False
            # Discard data received within the last interval if any.
            self.hg = None
            self.rv = None
            # If data is processed before the end of the interval, we do
            # not wait to the end of this interval, but the next one.
            if waiting<=process_time:
                waiting += self.query_interval
        else:
            # Time is reached, but data did not arrive so far.
            if waiting>process_time:
                # No data to process within this interval
                self.data_processed = True
        if waiting>process_time: return waiting-process_time
        if waiting>10 or waiting<=0.3: return 0.1
        return waiting-0.2

    def random_time(self, waiting):
        """ add a (random) additional amount of time to the waiting time 
        
            As we do not access the Internet in this thread, we need not
            do any load balancing here.
            
            Beware! A return value below 0 results in waiting after
            the getRecord() call. 
        """
        return 0
    
    def getRecord(self):
        """ get data - in this case from the queue - and process it """
        # get the last 5 minutes border
        last5m = time.time()
        last5m -= last5m%300
        # get a record of radar data from the queue
        ct = 0
        while self.running:
            try:
                reply = self.hgrv_queue.get(timeout=10)
            except queue.Empty:
                if ct: break
                return
            # determine the kind of radar data
            try:
                product = reply.product
            except AttributeError:
                if self.log_failure:
                    logerr("thread '%s': got data out of the queue that is not radar data" % self.name)
                product = None
            # Form the queue we get one radar data record at a time only. So
            # save them for further reference. 
            if product=='HG':
                self.hg = reply
                ct += 1
            elif product=='RV':
                self.rv = reply
                ct += 1
        # If one of self.hg or self.rv is None, we cannot do anything except
        # waiting for more data to arrive.
        if self.hg is None or self.rv is None:
            return
        # process data
        try:
            # Try to get a combined record of both the HG und RV data.
            dwd = DwdRadar.from_hg_rv(self.hg,
                                      self.rv,
                                      log_success=self.log_success,
                                      log_failure=self.log_failure)
            if dwd:
                # Data received by the queue are processed. So we do not
                # need them any more.
                self.hg = None
                self.rv = None
                self.data_processed = True
                # get observation types
                self.cache_readings(dwd, last5m)
                # create map image
                for map in self.maps:
                    # test shutdown request
                    if not self.running: return
                    self.write_map(map,dwd,0,False)
        except (LookupError,TypeError,ValueError,ArithmeticError,NameError) as e:
            if self.log_failure:
                logerr("thread '%s': getRecord() %s %s" % (self.name,e.__class__.__name__,e))


def create_thread(thread_name,config_dict,archive_interval):
    """ create radar thread """
    prefix = config_dict.get('prefix','')
    provider = config_dict.get('provider')
    model = config_dict.get('model')
    if provider=='DWD':
        conf_dict = weeutil.config.accumulateLeaves(config_dict)
        conf_dict['prefix'] = prefix
        conf_dict['model'] = model
        conf_dict['locations'] = configobj.ConfigObj()
        conf_dict['maps'] = configobj.ConfigObj()
        for section in config_dict.sections:
            if ('easting' in config_dict[section] and
                'northing' in config_dict[section]):
                prefix2 = config_dict[section].get('prefix','')
                conf_dict['locations'][section] = {
                    'xy': (weeutil.weeutil.to_float(config_dict[section]['easting']),
                           weeutil.weeutil.to_float(config_dict[section]['northing'])),
                    'prefix': prefix2,
                    'latitude':weeutil.weeutil.to_float(config_dict[section].get('latitude')),
                    'longitude':weeutil.weeutil.to_float(config_dict[section].get('longitude'))
                }
                if prefix:
                    p = prefix+prefix2.capitalize()
                else:
                    p = prefix2
                if p:
                    p = p+'Radar'+model
                else:
                    p = 'radar'+model
                weewx.units.obs_group_dict.setdefault(p+'DateTime','group_time')
                if model=='HG':
                    weewx.units.obs_group_dict.setdefault(p+'Wawa','group_wmo_wawa')
                elif model=='WN':
                    weewx.units.obs_group_dict.setdefault(p+'DBZ','group_db')
                elif model=='RV':
                    weewx.units.obs_group_dict.setdefault(p+'Rain','group_rain')
                    weewx.units.obs_group_dict.setdefault(p+'RainRate','group_rainrate')
                    weewx.units.obs_group_dict.setdefault(p+'RainRateForecast','group_rainrate')
                    weewx.units.obs_group_dict.setdefault(p+'Rain2hForecast','group_rain')
                elif model=='HGRV':
                    weewx.units.obs_group_dict.setdefault(p[:-4]+'Wawa','group_wmo_wawa')
                    weewx.units.obs_group_dict.setdefault(p[:-4]+'RainRate','group_rainrate')
            if 'map' in config_dict[section]:
                conf_dict['maps'][section] = weeutil.config.deep_copy(config_dict[section])
                if isinstance(config_dict[section]['map'],list):
                    map = [weeutil.weeutil.to_int(x) for x in config_dict[section]['map']]
                else:
                    map = AREAS[config_dict[section]['map']]
                conf_dict['maps'][section].update({
                    'map': map,
                    'prefix':config_dict[section].get('prefix',''),
                })
        if weeutil.weeutil.to_bool(conf_dict.get('enable',True)):
            #loginf(conf_dict)
            thread = dict()
            thread['datasource'] = 'Radolan'+model
            thread['prefix'] = prefix
            if model=='HGRV':
                thread['thread'] = HgRvThread(thread_name,conf_dict,archive_interval)
            else:
                thread['thread'] = DwdRadarThread(thread_name,conf_dict,archive_interval)
            thread['thread'].start()
            return thread
    return None


def convert_geojson(fni, fno, include_comment, color):
    """ convert geojson file to list of coordinates for proj
    
        Args:
            fni (str): geojson file to read
            fno (str): file to write
        
        Returns:
            nothing
    """
    min_lon = min(float(DwdRadar.BORDER_DE1200_WGS84['NW']['lon']),float(DwdRadar.BORDER_DE1200_WGS84['SW']['lon']))
    max_lon = max(float(DwdRadar.BORDER_DE1200_WGS84['NO']['lon']),float(DwdRadar.BORDER_DE1200_WGS84['SO']['lon']))
    min_lat = min(float(DwdRadar.BORDER_DE1200_WGS84['SW']['lat']),float(DwdRadar.BORDER_DE1200_WGS84['SO']['lat']))
    max_lat = max(float(DwdRadar.BORDER_DE1200_WGS84['NW']['lat']),float(DwdRadar.BORDER_DE1200_WGS84['NO']['lat']))
    coords = []
    with open(fni,"rb") as f:
        geojson = json.load(f)
    if not geojson:
        print('error reading file')
        return
    ct_features = 0
    ct_coordinates = 0
    ct_new = 0
    for x in geojson['features']:
        ct_features += 1
        name = x['properties'].get('name','unknown')
        if name is None: name = 'unknown'
        typ = x['geometry']['type']
        if typ=='LineString':
            if len(coords)==0 or len(coords[-1])!=0:
                coords.append({'name':name,'geometry':[]})
            for z in x['geometry']['coordinates']:
                if z[0]>=min_lon and z[0]<max_lon and z[1]>=min_lat and z[1]<max_lat:
                    coords[-1]['geometry'].append(z)
                    ct_new += 1
                else:
                    if len(coords[-1])!=0:
                        coords.append({'name':name,'geometry':[]})
        elif typ=='Point':
            pass
        else:
            for y in x['geometry']['coordinates']:
                if len(coords)==0 or len(coords[-1])!=0:
                    coords.append({'name':name,'geometry':[]})
                for z in y:
                    ct_coordinates += 1
                    if z[0]>=min_lon and z[0]<max_lon and z[1]>=min_lat and z[1]<max_lat:
                        coords[-1]['geometry'].append(z)
                        ct_new += 1
                    else:
                        if len(coords[-1])!=0:
                            coords.append({'name':name,'geometry':[]})
    with open(fno,'wt') as f:
        if color:
            f.write('366 366 COLOR="%s"\n' % color)
        for x in coords:
            if include_comment:
                f.write('366 366 %s - -\n' % x['name'].replace(' ','_'))
            else:
                f.write('366 366 %s\n' % x['name'].replace(' ','_'))
            for y in x['geometry']:
                if include_comment:
                    f.write('%s %s %s %s %s\n' % (y[0],y[1],x['name'].replace(' ','_'),y[1],y[0]))
                else:
                    f.write('%s %s\n' % (y[0],y[1]))
    print('features',ct_features)
    print('coordinates',ct_coordinates)
    print('new',ct_new)


if __name__ == "__main__":

    usage = """Usage: %prog [options] [file.bz2]
       %prog --convert-geojson [options] sourcefile targetfile

Direct call is for testing only."""
    epilog = """The maximum image size for HG, WN, and RV is 1100px wide and 1200px high,
referring to 1100 km west-east and 1200 km south-north.
Coordinates go from west to east and south to north, respectively.
"""

    parser = optparse.OptionParser(usage=usage, epilog=epilog)
    
    parser.add_option("-v","--verbose", dest="verbose",action="store_true",
                      help="verbose output")
    parser.add_option("--places", dest="places", metavar="FILE",
                     type="string",
                     help="optional list of places to show on the map")

    group = optparse.OptionGroup(parser,'Commands')
    group.add_option("--write-map", dest="writemap", action="store_true",
                      help="write map image")
    group.add_option("--get", dest="location", metavar="LOCATION",
                     type="string",
                     help="print reading for the specified location")
    group.add_option("--print-locations", dest="printlocations", action="store_true",
                      help="print locations list")
    group.add_option("--test-thread",dest="test",action="store_true",
                      help="test thread")
    group.add_option("--convert-geojson", dest="convert", action="store_true",
                     help="convert geojson file to list for proj")
    parser.add_option_group(group)

    group = optparse.OptionGroup(parser,'Map creation options')
    group.add_option("--image-size", dest="imagesize", metavar="X,Y,W,H",
                      type="string",
                      help="optional x y width height")
    group.add_option("--filter", dest="filter", metavar="LIST",
                      type="string",
                      help="optional list of locations to filter")
    group.add_option("--borders",dest="borders",metavar="FILE",
                     type="string",
                     help="file of border coordinates")
    group.add_option("--background",dest="background", metavar="TYPE",
                      type="string",
                      help="optional background type light or dark")
    group.add_option("--svg", dest="svg", action="store_true",
                      help="output in SVG format")
    parser.add_option_group(group)
    
    group = optparse.OptionGroup(parser,'GEOJSON options')
    group.add_option("--include-comment", dest="geojsoncomment",
                     action="store_true",
                     help = "include comments in list")
    group.add_option("--color", dest="geojsoncolor", metavar="COLOR",
                     type="string", default=None,
                     help="line color")
    parser.add_option_group(group)

    (options, args) = parser.parse_args()

    # verbose output
    verbose = 1 if options.verbose else 0

    # load file containing additional places data
    if options.places:
        load_places(options.places,'DE1200')
    
    # convert a geojson file to a file appropriate for proj
    if options.convert:
        if not args[0] or not args[1]:
            print('--convert-geojson geojson_file output_file')
            exit(1)
        convert_geojson(args[0],args[1],options.geojsoncomment,options.geojsoncolor)
        exit(0)

    # test thread class
    if options.test:
        conf = configobj.ConfigObj("radar.conf")
        dwd = create_thread('radar',conf,300)
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

    # load data
    if len(args)>0 and args[0][0]!='=':
        # load from file
        dwd = DwdRadar.open(args[0],log_success=True,verbose=verbose)
    else:
        # download from DWD server
        model = args[0][1:] if len(args)>0 else 'HG'
        if model=='HGRV':
            dwd1 = DwdRadar.wget('HG',log_success=True,verbose=verbose)
            dwd2 = DwdRadar.wget('RV',log_success=True,verbose=verbose)
            for ii in dwd2:
                if int(ii.header['VV'])==0:
                    dwd2 = ii
                    break
            dwd = DwdRadar.from_hg_rv(dwd1,dwd2,log_success=True,verbose=verbose)
        else:
            dwd = DwdRadar.wget(model,log_success=True,verbose=verbose)

    # If the file contains actual data as well as forecasts, look for
    # the actual data to process and discard the forecasts
    if isinstance(dwd,list):
        print('list of %s records' % len(dwd))
        for ii in dwd:
            #print(ii.header['VV'])
            if int(ii.header['VV'])==0:
                dwd = ii
                break
    
    # which value how often?
    if verbose:
        j = 0
        x = dict()
        for i in dwd.data:
            if i not in x: x[i] = 0
            x[i] += 1
            if dwd.product=='HGRV': continue
            if i>=0x29C4 and dwd.product!='HG': continue
            j = max(j,i)
        print('maximum',j)
        for i in sorted(x.items()):
            print(i)
        if dwd.product=='RV':
            x = dict()
            for i in dwd.sum_data:
                j = None if i is None else round(i,1)
                if j not in x: x[j] = 0
                x[j] += 1
            print('sum of rain in forecast:')
            for i in sorted(x.items(),key=lambda x:-1 if x[0] is None else x[0]):
                if i[0] is None:
                    print('sum %6s %8s' % i)
                else:
                    print('sum %6.2f %8s' % i)

    # set light or dark background
    # (The default is light, if this option is missing.)
    if options.background:
        dwd.background = options.background
    
    #dwd.load_coordinates('coords.txt')
    if options.printlocations:
        dwd.print_coordinates()

    #wx = (coords['Wöllsdorf']['xy'][0]-coords['SW']['xy'][0])/1000
    #wy = (coords['Wöllsdorf']['xy'][1]-coords['SW']['xy'][1])/1000
    #map(wx-100,wy-100,200,200,coords)

    #dwd.set_background_color('#000000')
    if options.writemap:
        if options.imagesize:
            if options.imagesize in AREAS:
                image_size = AREAS[options.imagesize]
            else:
                x = options.imagesize.split(',')
                image_size = tuple([int(i) for i in x])
        else:
            image_size = (100,100,900,1000)
        if options.filter:
            filter = options.filter.split(',')
        else:
            filter = []
        #dwd.load_lines('coastcoords.txt')
        if options.borders:
            dwd.load_lines(options.borders,'Kartendatenlieferant')
        else:
            #dwd.load_lines('countrycoords.txt','EuroGeographics')
            pass
        """
        for line in dwd.lines:
            xxx = [str(coord['xy']) for coord in line['coordinates']]
            print('    [%s],' % ','.join(xxx))
        """
        img,_,title,desc,scale = dwd.map(image_size[0],image_size[1],image_size[2],image_size[3],filter=filter,svg=options.svg)
        if options.svg:
            with open('radar-'+dwd.product+'.svg','wt') as f:
                f.write(img)
        else:
            dwd.save_map('radar-'+dwd.product+'.png',img,title=title,desc=desc)

    if options.location:
        if options.location in dwd.coords:
            xy = dwd.coords[options.location]['xy']
        else:
            x = options.location.split(',')
            xy = (float(x[0]),float(x[1]))
        idx = dwd.get_index(xy)
        print('parameter: %s' % options.location)
        print('easting:   %10.3f   northing:   %10.3f   km' % (xy[0]/1000.0,xy[1]/1000.0))
        print('datawidth: %6s       dataheight: %6s       km' % (dwd.data_width,dwd.data_height))
        print('index: %10s' % idx)
        print('index x:   %6s       index y:    %6s       km' % (idx%dwd.data_width,int(idx/dwd.data_width)))
        cx = (xy[0]-dwd.coords['SW']['xy'][0])/1000
        cy = (xy[1]-dwd.coords['SW']['xy'][1])/1000
        print('map x:     %10.3f   map y:      %10.3f   km' % (cx,cy))
        print('value: %s' % dwd.get_value(xy))
