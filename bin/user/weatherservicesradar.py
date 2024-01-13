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
    This extension processes radar data provided by the German Weather
    Service DWD and published in binary on their opendata server.
    
    * HG format:
      precipitation kind 2m above ground according to the radar
    
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
import bz2
import tarfile
import io
from PIL import Image, ImageColor, ImageDraw, ImageFont
import configobj
import os.path
import threading
import random

if __name__ == '__main__':

    import optparse
    import json
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

MAP_LOCATIONS_DE1200_WGS84 = {
    'Wöllsdorf': {'xy': (766379.87, -579859.86), 'lat': '51.123', 'lon': '13.040'},
    'Leipzig': {'xy': (716516.82, -556809.38), 'lat': '51.3406', 'lon': '12.3747'},
    'Dresden': {'xy': (817762.02, -585484.68), 'lat': '51.0489', 'lon': '13.7331'},
    'Chemnitz': {'xy': (759302.32, -614127.12), 'lat': '50.8332', 'lon': '12.92'},
    'Berlin': {'xy': (783746.86, -416406.23), 'lat': '52.518611', 'lon': '13.408333'},
    'Görlitz': {'xy': (909705.9, -566628.93), 'lat': '51.15', 'lon': '15.0'},
    'Hamburg': {'xy': (542739.88, -304450.27), 'lat': '53.550556', 'lon': '9.993333'},
    'Emden': {'xy': (350748.08, -320916.7), 'lat': '53.3668', 'lon': '7.2061'},
    'Greifswald': {'xy': (771145.8, -235040.31), 'lat': '54.0960', 'lon': '13.3817'},
    'Wolfenbüttel': {'xy': (581351.05, -464637.09), 'lat': '52.16263', 'lon': '10.53484'},
    'Brocken': {'xy': (587565.63, -506791.63), 'lat': '51.7991', 'lon': '10.6156'},
    'Fichtelberg': {'xy': (764264.57, -661198.14), 'lat': '50.429444', 'lon': '12.954167'},
    'Weimar': {'xy': (641248.04, -601415.0), 'lat': '50.97937', 'lon': '11.32976'},
    'Aachen': {'xy': (253005.58, -616350.99), 'lat': '50.77644', 'lon': '6.08373'},
    'Augsburg': {'xy': (614212.32, -909407.49), 'lat': '48.36879', 'lon': '10.89774'},
    'Nürnberg': {'xy': (626001.01, -780799.9), 'lat': '49.45390', 'lon': '11.07730'},
    'Praha': {'xy': (876957.35, -694134.76), 'lat': '50.08749', 'lon': '14.42120'},
    'Salzburg': {'xy': (787704.56, -971297.07), 'lat': '47.79848', 'lon': '13.04667'},
    'Plzeň': {'xy': (800628.43, -739437.07), 'lat': '49.7472', 'lon': '13.37748'},
    'Offenbach': {'xy': (449889.2, -703981.79), 'lat': '50.10478', 'lon': '8.76454'},
    'Luxembourg': {'xy': (247137.74, -753023.96), 'lat': '49.6113', 'lon': '6.1292'},
    'Zürich': {'xy': (424864.45, -1027214.44), 'lat': '47.37177', 'lon': '8.54220'},
    'Karlsruhe': {'xy': (419118.5, -831795.91), 'lat': '49.01396', 'lon': '8.40442'},
    'Münster': {'xy': (372911.26, -484503.91), 'lat': '51.9626', 'lon': '7.6258'},
    'Kiel': {'xy': (552568.9, -215715.36), 'lat': '54.3231', 'lon': '10.1399'},
    'Flensburg': {'xy': (505833.67, -162879.18), 'lat': '54.7832', 'lon': '9.4345'},
    'Szczecin': {'xy': (856569.86, -306401.86), 'lat': '53.42523', 'lon':'14.56021'},
    'Cottbus': {'xy': (855632.43, -499673.59), 'lat': '51.76068', 'lon':'14.33429'},
    #'Göttingen': {'xy': (538491.31, -538008.38), 'lat': '51.5328', 'lon': '9.9352'},
    'Kassel':{'xy':(506522.38,-563143.59), 'lat': '51.3157', 'lon': '9.498'},
    'Zugspitze':{'xy':(623159.66,-1022123.31),'lat':47.42122,'lon':10.9863},
    #'Schwerin':{'xy':(639938.73,-294247.94),'lat':53.62884,'lon': 11.41486},
}

class DwdRadar(object):

    COMPOSITE_URL = 'https://opendata.dwd.de/weather/radar/composite'

    # valid for 1200x1100 DE1200 WGS84 HG, WN, RV
    BORDER_DE1200_WGS84 = {
        'NW': {'xy': (-500.0, 500.0), 'lat': '55.86208711', 'lon': '1.463301510'}, 
        'NO': {'xy': (1099500.0, 500.0), 'lat': '55.84543856', 'lon': '18.73161645'}, 
        'SO': {'xy': (1099500.0, -1199500.0), 'lat': '45.68460578', 'lon': '16.58086935'}, 
        'SW': {'xy': (-500.0, -1199500.0), 'lat': '45.69642538', 'lon': '3.566994635'}
    }
    
    PROJ_STR_DE1200_WGS84 = "+proj=stere +lat_0=90 +lat_ts=60 +lon_0=10 +a=6378137 +b=6356752.3142451802 +no_defs +x_0=543196.83521776402 +y_0=3622588.8619310018"
    
    COLORS = {
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
    }

    def __init__(self, log_success=False, log_failure=True, verbose=0):
        # logging settings
        self.log_success = log_success
        self.log_failure = log_failure
        self.verbose = verbose
        # configuration data
        self.colors = DwdRadar.COLORS
        self.data_width = 1100
        self.data_height = 1200
        self.font_file = '/etc/weewx/skins/Belchertown1_3/lib/fonts/roboto/KFOlCnqEu92Fr1MmSU5fBBc9.ttf'
        self.background = 'light'
        # data
        self.data = []
        self.header = dict()
        self.product = None
        self.version = None
        # initialize coordinate data
        self.init_coords()
    
    @staticmethod
    def open(fn, log_success=False, log_failure=True, verbose=0):
        """ create a DwdRadar instance from a file
        """
        dwd = DwdRadar(log_success,log_failure,verbose)
        dwd.read_data(DwdRadar._decompress_file(fn))
        return dwd
    
    @staticmethod
    def wget(product, log_success=False, log_failure=True, verbose=0):
        """ create a DwdRadar instance from internet data
        """
        # 'PG' is in BUFR format, not in the format handled here.
        fn = {
            'HG':'HG_LATEST_000.bz2',
            'RV':'DE1200_RV_LATEST.tar.bz2',
            'WN':'WN_LATEST.tar.bz2'
        }[product.upper()]
        url = DwdRadar.COMPOSITE_URL+'/'+product.lower()+'/'+fn
        reply = wget(url,log_success,log_failure)
        if reply is None: return None
        if 'tar' not in fn:
            dwd = DwdRadar(log_success,log_failure,verbose)
            dwd.read_data([bz2.decompress(reply)])
            return dwd
        dwd = []
        f = io.BytesIO(reply)
        tarf = tarfile.open(fileobj=f)
        for member in tarf:
            ff = tarf.extractfile(member)
            newdwd = DwdRadar(log_success,log_failure,verbose)
            newdwd.read_data(ff)
            ff.close()
            dwd.append(newdwd)
        tarf.close()
        f.close()
        return dwd
    
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

    def read_data(self, in_data):
        """ read radar data and convert to internal data structure
        """
        header = ""
        self.data = []
        isheader = True
        by = 0
        ct = 1
        length = 0
        data_size = 1
        for reply in in_data:
            length += len(reply)
            if isheader:
                i = reply.find(b'\x03')
                if i==-1:
                    i = len(reply)
                else:
                    isheader = False
                if self.verbose:
                    print('header',i)
                header += reply[0:i].decode('ascii',errors='replace')
                if self.verbose:
                    print('---> %i' % reply[i])
                reply = reply[i+1:]
            if not isheader:
                try:
                    data_size = DwdRadar.DATA_SIZE[header[0:2]]
                except LookupError:
                    data_size = 256
                for ii in reply:
                    by += ii*ct
                    if ct==data_size:
                        self.data.append(by)
                        by = 0
                        ct = 1
                    else:
                        ct *= 256
        if self.verbose:
            print('file length:',length)
            print(header)
        # product code
        self.product = header[0:2]
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
            if x[0]=='E' and x[1]=='-' and x!='E-00':
                factor = pow(10,int(x[1:]))
                if self.verbose:
                    print('Genauigkeitsfaktor:',factor)
                self.data = [i*factor for i in self.data]
        # initialize coordinate data
        self.init_coords()
        if self.verbose:
            print(header_vals)
            print('data',len(self.data),min(self.data),max(self.data))
    
    def init_coords(self):
        """ initialize coordinate data
        """
        if (self.version is None or 
            (self.product in ('HG','WN','RV') and self.version>=5)):
            self.coords = DwdRadar.BORDER_DE1200_WGS84
            self.coords.update(MAP_LOCATIONS_DE1200_WGS84)
            self.lines = []
            if self.verbose and self.version is not None:
                print('Grid initialized to DE1200 WGS84')

    def get_value(self, xy):
        """ get the radar reading for a certain location 
            
            Args:
                xy (tuple): coordinate pair in meters
            
            Returns:
                int: reading of the location described by xy
        """
        try:
            cx = (xy[0]-self.coords['SW']['xy'][0])/1000
            cy = (xy[1]-self.coords['SW']['xy'][1])/1000
            if cx>self.data_width or cx<0.0: raise LookupError('x out of range')
            if cy>self.data_height or cy<0.0: raise LookupError('y out of range')
            if cx==self.data_width: cx -= 0.1
            if cy==self.data_height: cy -= 0.1
            return self.data[int(cy)*self.data_width+int(cx)]
        except LookupError:
            return None
    
    def get_wawa(self, xy):
        """ get the wawa value out of the radar reading for a certain location
            
            Args:
                xy (tuple): coordinate pair in meters
            
            Returns:
                int: wawa code of the location described by xy
        """
        try:
            return DwdRadar.WAWA[self.get_value(xy)]
        except LookupError:
            return None

    def map(self,fn,x,y,width,height, filter=[]):
        """ draw a map
        
            Args:
                x (int, float): left image border in pixels 0...1100
                y (int, float): lower (!) image border in pixels 0...1200
                width (int, float): image width in pixels 0...1100
                height (int, float): image height in pixels 0...1200
        """
        x = int(x)
        y = int(y)
        if (x+width)>self.data_width:
            width = self.data_width-x
        if (y+height)>self.data_height:
            height = self.data_height-y
        ww = width
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
        baseimg = Image.new('RGBA',(width,height),color=ImageColor.getrgb('#00000000'))
        img = Image.new('RGBA',(width,height),color=ImageColor.getrgb('#00000000'))
        if width>=640:
            font_size = 16
        elif width<320:
            font_size = 8
        else:
            font_size = int(width*0.025)
        fnt=ImageFont.truetype(self.font_file,font_size)
        draw = ImageDraw.Draw(img)
        basedraw = ImageDraw.Draw(baseimg)
        # set points according to radar reading
        #s = '<svg xmlns="http://www.w3.org/2000/svg" version="1.1" width="%s" height="%s" viewBox="%s %s %s %s">\n' % (ww,hh,x,1200-y-height,width,height)
        for yy in range(height):
            for xx in range(width):
                val = self.data[(y+yy)*self.data_width+x+xx]
                col = self.colors.get(val,'#12345640')
                if dark_background and col[:7]=='#FFFFFF':
                    col = '#000000'+col[7:]
                #s += '<rect x="%s" y="%s" width="1" height="1" fill="%s" />\n' % (x+xx,1200-yy-y-1,col)
                c = ImageColor.getrgb(col)
                try:
                    draw.point((xx,height-yy-1),fill=c)
                    if val!=2147483648:
                        basedraw.point((xx,height-yy-1),fill=background_color)
                except IndexError as e:
                    print(e,xx,height-yy,c)
        # mark locations
        for location,coord in self.coords.items():
            if location not in ('NW','NO','SW','SO') and location not in filter:
                cx = (coord['xy'][0]-self.coords['SW']['xy'][0])/1000
                cy = (coord['xy'][1]-self.coords['SW']['xy'][1])/1000
                #s += '<circle cx="%s" cy="%s" r="5" fill="#123456" />\n' % (cx,1200-cy)
                cx -= x
                cy -= y
                if location in ('Dresden','Chemnitz'):
                    # label besides the dot
                    y_off = 4+font_size/4
                    x_off = 6
                elif location in ('Fichtelberg','Zugspitze'):
                    # label right below the dot
                    y_off = -font_size/4
                    x_off = 4
                else: 
                    # label right above the dot
                    y_off = 4+font_size
                    x_off = 4
                if cx>=0 and cy>=0:
                    draw.ellipse([cx-2,height-cy-2,cx+2,height-cy+2],fill=ImageColor.getrgb('#FFF' if dark_background else '#000'))
                    draw.text((cx+x_off,height-cy-y_off),location,fill=ImageColor.getrgb('#FFF' if dark_background else '#000'),font=fnt)
        #s += '</svg>\n'
        ts_str = time.strftime("%d.%m.%Y %H:%M %z",time.localtime(self.timestamp))
        product_str = 'Niederschlagsart 2m über Grund\n' if self.product=='HG' else ''
        draw.multiline_text((10,height-10),'%sHerausgegeben %s\nDatenbasis Deutscher Wetterdienst\nGrenzen © EuroGeographics\n© Wetterstation Wöllsdorf' % (product_str,ts_str),fill=ImageColor.getrgb('#FFF' if dark_background else '#000'),font=fnt,anchor="ld")
        #with open('test.svg','wt') as f:
        #    f.write(s)
        for line in self.lines:
            xy = []
            for coord in line['coordinates']:
                xx = (coord['xy'][0]-self.coords['SW']['xy'][0])/1000-x
                yy = (coord['xy'][1]-self.coords['SW']['xy'][1])/1000-y
                xy.append((xx,height-yy))
                #basedraw.point((xx,height-yy),fill="#000")
            basedraw.line(xy,fill=ImageColor.getrgb('#FFF' if dark_background else '#000'),width=1)
        img = Image.alpha_composite(baseimg,img)
        try:
            img.save(fn)
        except (ValueError,OSError) as e:
            if self.log_failure:
                logerr("could not create '%s': %s %s" % (fn,e.__class__.__name__,e))
            raise
        else:
            if self.log_success:
                loginf("map '%s' created" % fn)

    def load_coordinates(self, fn):
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
    
    def load_lines(self, fn):
        lines = []
        start = True
        with open(fn, "rt") as f:
            for line in f:
                x = line.split()
                if x[0]=='*':
                    start = True
                else:
                    if start:
                        lines.append({'coordinates':[]})
                    lines[-1]['coordinates'].append({'xy':(float(x[0]),float(x[1]))})
                    start = False
        self.lines = lines
    
    def set_background_color(self, color):
        self.colors[2147483648] = str(color)

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
    
    def getRecord(self):
        dwd = DwdRadar.wget(self.product,self.log_success,self.log_failure)
        if dwd is None: 
            if log.failure:
                logerr("thread '%s': error downloading data" % self.name)
            return
        # create map image
        for map in self.maps:
            try:
                if self.maps[map].get('prefix'):
                    fn = self.maps[map]['prefix']+'Radar-'+dwd.product+'.png'
                else:
                    fn = 'radar-'+dwd.product+'.png'
                fn = os.path.join(self.target_path,fn)
                size = self.maps[map]['map']
                dwd.background = self.maps[map].get('background','light')
                if 'borders' in self.maps[map]:
                    dwd.load_lines(os.path.join(self.target_path,self.maps[map]['borders']))
                dwd.map(fn,
                    size[0], # x
                    size[1], # y
                    size[2], # width
                    size[3], # height
                    self.maps[map].get('filter',[]))
            except (LookupError,ValueError,TypeError,ArithmeticError) as e:
                if self.log_failure:
                    logerr("thread '%s': %s %s" % (self.name,e.__class__.__name__,e))
        # data
        # Note: prefix is added in _to_weewx() in weatherservices.py, not here
        data = dict()
        for location in self.locations:
            try:
                xy = self.locations[location]['xy']
                if 'prefix' in self.locations[location] and self.locations[location]['prefix']:
                    prefix = self.locations[location]['prefix']+'Radar'+dwd.product
                else:
                    prefix = 'radar'+dwd.product
                data[prefix+'Value'] = (dwd.get_value(xy),None,None)
                data[prefix+'Wawa'] = (dwd.get_wawa(xy),'byte','group_wmo_wawa')
                data[prefix+'DateTime'] = (int(dwd.timestamp),'unix_epoch','group_time')
            except (LookupError,ValueError,TypeError,ArithmeticError) as e:
                if self.log_failure:
                    logerr("thread '%s': %s %s" % (self.name,e.__class__.__name__,e))
        try:
            self.lock.acquire()
            self.data.append((dwd.timestamp,data))
            while len(self.data)>0 and self.data[0][0]<(time.time()-3600):
                del self.data[0]
        finally:
            self.lock.release()

    def get_data(self, ts):
        data = dict()
        try:
            self.lock.acquire()
            for dd in self.data:
                if dd[0]>=ts: break
                data = dd[1]
        finally:
            self.lock.release()
        interval = 1
        logdbg('get_data %s' % data)
        return data,interval
        
    def random_time(self):
        """ do a little bit of load balancing """
        return random.random()*15

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
                weewx.units.obs_group_dict.setdefault(p+'Wawa','group_wmo_wawa')
            if 'map' in config_dict[section]:
                conf_dict['maps'][section] = config_dict[section]
                map = [weeutil.weeutil.to_int(x) for x in config_dict[section]['map']]
                conf_dict['maps'][section].update({
                    'map': map,
                    'prefix':config_dict[section].get('prefix',''),
                })
        if weeutil.weeutil.to_bool(conf_dict.get('enable',True)):
            loginf(conf_dict)
            thread = dict()
            thread['datasource'] = 'Radolan'
            thread['prefix'] = prefix
            thread['thread'] = DwdRadarThread(thread_name,conf_dict,archive_interval)
            thread['thread'].start()
            return thread
    return None


if __name__ == "__main__":

    usage = """Usage: %prog [options] [file.bz2]

Direct call is for testing only."""
    epilog = """The maximum image size for HG is 1100px wide and 1200px high,
referring to 1100 km west-east and 1200 km south-north.
Coordinates go from west to east and south to north, respectively.
"""

    parser = optparse.OptionParser(usage=usage, epilog=epilog)
    
    parser.add_option("--write-map", dest="writemap", action="store_true",
                      help="write map image")
    parser.add_option("--image-size", dest="imagesize", metavar="X,Y,W,H",
                      type="string",
                      help="optional x y width height")
    parser.add_option("--filter", dest="filter", metavar="LIST",
                      type="string",
                      help="optional list of locations to filter")
    parser.add_option("--background",dest="background", metavar="TYPE",
                      type="string",
                      help="optional background type light or dark")

    parser.add_option("--print-locations", dest="printlocations", action="store_true",
                      help="print locations list")
    parser.add_option("--test-thread",dest="test",action="store_true",
                      help="test thread")
    
    parser.add_option("-v","--verbose", dest="verbose",action="store_true",
                      help="Verbose output")

    (options, args) = parser.parse_args()

    """
    vals = dict()
    for ii in data:
        if ii not in vals:
            vals[ii] = 0
        vals[ii] += 1
    print('vals',vals)
    """
    
    verbose = 1 if options.verbose else 0

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

    # 'HG_LATEST_000.bz2'

    if len(args)>0:
        dwd = DwdRadar.open(args[0],log_success=True,verbose=verbose)
    else:
        dwd = DwdRadar.wget('HG',log_success=True,verbose=verbose)

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
            x = options.imagesize.split(',')
            image_size = tuple([int(i) for i in x])
        else:
            image_size = (100,100,900,1000)
        if options.filter:
            filter = options.filter.split(',')
        else:
            filter = []
        #dwd.load_lines('coastcoords.txt')
        dwd.load_lines('countrycoords.txt')
        """
        for line in dwd.lines:
            xxx = [str(coord['xy']) for coord in line['coordinates']]
            print('    [%s],' % ','.join(xxx))
        """
        dwd.map('radar-'+dwd.product+'.png',image_size[0],image_size[1],image_size[2],image_size[3],filter=filter)

