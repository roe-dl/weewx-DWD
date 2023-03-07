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

"""
    POI
    ===
    
    TODO: POI station lat, lon, alt from station list
    
    There are data of 47 DWD weather stations available. 
    
    DWD POI Service configuration weewx.conf:
    
    [WeatherServices]
        ...
        # optional, logging for services.
        # defaults: value from weewx.conf
        #log_success = replace_me
        #log_failure = replace_me
        ...
        [[forecast]]
            ...
            # optional, 'belchertown', 'dwd' or 'aeris'
            # default: belchertown
            #icon_set = replace_me
            ...

        [[current]]
            ...
            # Any unique identifier for this DWD POI service. Used to give the service a id for logging e.g.
            [[[any_unique_identifier_for_this_dwd_poi_service]]]
                # required, service provider: DWD
                provider = DWD

                # required, service: POI
                model = POI

                # required, DWD POI station id, see station list
                station = replace_me

                # optional, enable or disable this service.
                # default: True
                #enable = replace_me

                # optional, a prefix for each observation, e.g. "poi" results "poiObersvationname"
                # Useful if multiple services are used to be able to distinguish the data, see also weewx-DWD documentation.
                # default: ""
                #prefix = replace_me

                # optional, 'belchertown', 'dwd' or 'aeris'
                # default: value from section [[forecast]]
                #icon_set = replace_me

                # optional, debug level, e.g. 0 = no debug infos, 1 = min debug infos, 2 = more debug infos, >=3 = max debug infos.
                # default: 0
                #debug = 0 replace_me

                # optional, logging for services.
                # defaults: value from section [WeatherServices]
                #log_success = replace_me
                #log_failure = replace_me

                # optional latitude and longitude of the POI station
                # Is only used as return value
                #   latitude in decimal degrees. Negative for southern hemisphere.
                #   longitude in decimal degrees. Negative for western hemisphere.
                #latitude = replace_me
                #longitude = replace_me

                # optional altitude of the POI station with the unit. Choose 'foot' or 'meter' for unit.
                # Is only used as return value
                #altitude = replace_me
            ...
            [[[other_unique_identifier_for_a_dwd_poi_service]]]
            ...
        ...
    
    station list:
    https://github.com/roe-dl/weewx-DWD/wiki/POI-Stationen-in-Deutschland
    https://www.dwd.de/DE/leistungen/klimadatendeutschland/stationsuebersicht.html
    
    example station ids:
    10578 - Fichtelberg
    10453 - Brocken
    10961 - Zugspitze
    
    Those are all WMO station ids.
    
    current readings:
    https://www.dwd.de/DE/leistungen/beobachtung/beobachtung.html
    
    ----------------
    
    CDC
    ===
    
    CDC includes a lot more of stations than POI.
    
    https://opendata.dwd.de/climate_environment/CDC/Liesmich_intro_CDC-FTP.pdf
    https://opendata.dwd.de/climate_environment/CDC/observations_germany/climate/

    station data are in subdirectiory "meta_data"
    
    Configuration in weewx.conf:
    
    DWD CDC Service configuration weewx.conf:
    
    [WeatherServices]
        ...
        # optional, logging for services.
        # defaults: value from weewx.conf
        #log_success = replace_me
        #log_failure = replace_me
        ...
        [[forecast]]
            ...
            # optional, 'belchertown', 'dwd' or 'aeris'
            # default: belchertown
            #icon_set = replace_me
            ...

        [[current]]
            ...
            # Any unique identifier for this DWD CDC service. Used to give the service a id for logging e.g.
            [[[any_unique_identifier_for_this_dwd_cdc_service]]]
                # required, service provider: DWD
                provider = DWD

                # required, service: CDC
                model = CDC

                # required, DWD CDC station id, see station list
                station = replace_me

                # optional, enable or disable this service.
                # default: True
                #enable = replace_me

                # optional, equipment of the weather station
                # default: air,wind,gust,precipitation,solar
                #observations = replace_me

                # optional, a prefix for each observation, e.g. "cdc" results "cdcObersvationname"
                # Useful if multiple services are used to be able to distinguish the data, see also weewx-DWD documentation.
                # default: ""
                #prefix = replace_me

                # optional, 'belchertown', 'dwd' or 'aeris'
                # default: value from section [[forecast]]
                #icon_set = replace_me

                # optional, debug level, e.g. 0 = no debug infos, 1 = min debug infos, 2 = more debug infos, >=3 = max debug infos.
                # default: 0
                #debug = replace_me

                # optional, logging for services.
                # defaults: value from section [WeatherServices]
                #log_success = replace_me
                #log_failure = replace_me
            ...
            [[[other_unique_identifier_for_a_dwd_cdc_service]]]
            ...
        ...
    
    station list:
    https://opendata.dwd.de/climate_environment/CDC/help/wetter_tageswerte_Beschreibung_Stationen.txt
    https://opendata.dwd.de/climate_environment/CDC/observations_germany/climate/10_minutes/air_temperature/now/zehn_now_tu_Beschreibung_Stationen.txt
    
    example station nrs:
    01358 - Fichtelberg
    00840 - Carlsfeld
    00722 - Brocken
    05792 - Zugspitze
    
    ZAMG
    ====
    
    Austrian weather service
    
    ZAMG Service configuration weewx.conf:
    
    [WeatherServices]
        ...
        # optional, logging for services.
        # defaults: value from weewx.conf
        #log_success = replace_me
        #log_failure = replace_me
        ...
        [[forecast]]
            ...
            # optional, 'belchertown', 'dwd' or 'aeris'
            # default: belchertown
            #icon_set = replace_me
            ...

        [[current]]
            ...
            # Any unique identifier for this ZAMG service. Used to give the service a id for logging e.g.
            [[[any_unique_identifier_for_this_zamg_service]]]
                # required, service provider: ZAMG
                provider = ZAMG

                # required, ZAMG station id, see station list above
                station = replace_me

                # optional, enable or disable this service.
                # default: True
                #enable = replace_me

                # optional, equipment of the weather station
                # default: air,wind,gust,precipitation,solar
                #observations = replace_me

                # optional, a prefix for each observation, e.g. "zamg" results "zamgObersvationname"
                # Useful if multiple services are used to be able to distinguish the data, see also weewx-DWD documentation.
                # default: ""
                #prefix = replace_me

                # optional, 'belchertown', 'dwd' or 'aeris'
                # default: value from section [[forecast]]
                #icon_set = replace_me

                # optional, debug level, e.g. 0 = no debug infos, 1 = min debug infos, 2 = more debug infos, >=3 = max debug infos.
                # default: 0
                #debug = replace_me

                # optional, logging for services.
                # defaults: value from section [WeatherServices]
                #log_success = replace_me
                #log_failure = replace_me
            ...
            [[[other_unique_identifier_for_a_zamg_service]]]
            ...
        ...
    
    station list:
    https://dataset.api.hub.zamg.ac.at/v1/station/current/tawes-v1-10min/metadata
    
    ----------------
    
    API Open-Meteo
    ==============
    
    Open-Meteo is an open-source weather API with free access for non-commercial use.
    No API key is required. You can use it immediately!
    https://open-meteo.com
    
    unsing here the "DWD ICON API" to get current weather observations
    https://open-meteo.com/en/docs/dwd-api
    
    Open-Meteo Service configuration weewx.conf:
    
    [WeatherServices]
        ...
        # optional, logging for services.
        # defaults: value from weewx.conf
        #log_success = replace_me
        #log_failure = replace_me
        ...
        [[forecast]]
            ...
            # optional, 'belchertown', 'dwd' or 'aeris'
            # default: belchertown
            #icon_set = replace_me

            # optional, used for queries where a language is required, e.g. Open-Meteo geocoding API.
            # default: de
            #lang = replace_me
            ...
        [[current]]
            ...
            # Any unique identifier for this open-meteo service. Used to give the service a id for logging e.g.
            [[[any_unique_identifier_for_this_open-meteo_service]]]
                # required, service provider: open-meteo
                provider = open-meteo

                # optional, enable or disable this service.
                # default: True
                #enable = replace_me

                # optional, not case sensitiv. 'ThisStation' for local station
                # or a valid city name or postal code e.g. 'Döbeln' or '04720'.
                # default: ThisStation
                #station = replace_me

                # optional, Open-Meteo weather model, for possible values see dwd-mosmix Open-Meteo documentation or
                # DWD ICON API / Weather Forecast API documentation on Open-Meteo website https://open-meteo.com
                # default: dwd-icon
                #model = replace_me

                # optional
                #   latitude in decimal degrees. Negative for southern hemisphere.
                #   longitude in decimal degrees. Negative for western hemisphere.
                # defaults:
                #   If station is 'ThisStation': latitude and longitude from weewx.conf [station] will be use
                #   If station is a city name or postal code: latitude and longitude from Open-Weather Geocoding APIwill be use
                #latitude = replace_me
                #longitude = replace_me

                # optional, altitude of the station, with the unit. Choose 'foot' or 'meter' for unit.
                # default: 
                #   If station is 'ThisStation': altitude from weewx.conf [station] will be use
                #   If station is a city name or postal code: altitude from Open-Weather Geocoding APIwill be use
                #          otherwise: altitude from Open-Weather Geocoding API with station city or postal code
                #altitude = replace_me

                # optional, a prefix for each observation, e.g. "om" results "omObersvationname"
                # Useful if multiple services are used to be able to distinguish the data, see also weewx-DWD documentation.
                # default: ""
                #prefix = replace_me

                # optional, used for queries where a language is required, e.g. Open-Meteo geocoding API.
                # default: value from section [[forecast]]
                #lang = replace_me

                # optional, 'belchertown', 'dwd' or 'aeris'
                # default: value from section [[forecast]]
                #icon_set = replace_me

                # optional, debug level, e.g. 0 = no debug infos, 1 = min debug infos, 2 = more debug infos, >=3 = max debug infos.
                # default: 0
                #debug = replace_me

                # optional, logging for services.
                # defaults: value from section [WeatherServices]
                #log_success = replace_me
                #log_failure = replace_me
            ...
            [[[other_unique_identifier_for_a_service]]]
            ...
        ...
    
    API URL Builder "v1/dwd-icon" endpoint (Model: "dwd-icon":
    https://open-meteo.com/en/docs/dwd-api
    
    API URL Builder "v1/forecast" endpoint (Model: For models see dwd-mosmix documentation:
    https://open-meteo.com/en/docs

    API call example, Model: "dwd-icon":
    https://api.open-meteo.com/v1/dwd-icon?latitude=49.63227&longitude=12.056186&elevation=394.0&timeformat=unixtime&start_date=2023-01-29&end_date=2023-01-30&temperature_unit=celsius&windspeed_unit=kmh&precipitation_unit=mm&current_weather=true&hourly=temperature_2m,apparent_temperature,dewpoint_2m,pressure_msl,relativehumidity_2m,winddirection_10m,windspeed_10m,windgusts_10m,cloudcover,evapotranspiration,rain,showers,snowfall,freezinglevel_height,snowfall_height,weathercode,snow_depth,direct_radiation_instant
    
    Open-Meteo GitHub:
    https://github.com/open-meteo/open-meteo

    
    ----------------
    
    API Brightsky
    ==============
    
    Bright Sky is an open-source project aiming to make some of the more popular data
    — in particular weather observations from the DWD station network and weather forecasts from the MOSMIX model —
    available in a free, simple JSON API.
    https://brightsky.dev
    https://brightsky.dev/docs/
    
    unsing here the "current_weather" endpoint to get current weather observations
    https://brightsky.dev/docs/#get-/current_weather
    
    Brightsky Service configuration weewx.conf:
    
    [WeatherServices]
        ...
        # optional, logging for services.
        # defaults: value from weewx.conf
        #log_success = replace_me
        #log_failure = replace_me
        ...
        [[forecast]]
            ...
            # optional, 'belchertown', 'dwd' or 'aeris'
            # default: belchertown
            #icon_set = replace_me

            # optional, used for queries where a language is required, e.g. Open-Meteo geocoding API.
            # default: de
            #lang = replace_me
            ...
        [[current]]
            ...
            # Any unique identifier for this Brightsky service. Used to give the service a id for logging e.g.
            [[[any_unique_identifier_for_this_brightsky_service]]]
                # required, service provider: brightsky
                provider = brightsky

                # optional, enable or disable this service.
                # default: True
                #enable = replace_me

                # required if no latitude and longitude selected, otherwise optional
                # possible values:
                #   - 'ThisStation' for the local station
                #   - Valid city name or postal code e.g. 'Döbeln' or '04720'.
                #   - DWD station ID: DWD prefix 'dwd_' and typically five alphanumeric characters. e.g 'dwd_P0036'
                #   - WMO station ID: WMO prefix 'wmo_' and typically five digits. e.g 'wmo_10688'
                #   - Brightsky source ID: Brightsky API prefix 'api_' and digits. e.g 'api_6007'
                #     ==> 27.02.2023: https://github.com/jdemaeyer/brightsky/issues/126
                # If station is selected, this is primarily used for the API query.
                # default: ""
                #station = replace_me

                # required if no station is selected, otherwise optional
                # latitude in decimal degrees. Negative for southern hemisphere.
                # longitude in decimal degrees. Negative for western hemisphere.
                # defaults, if latitude or longitude empty:
                #   If station above in 'ThisStation': latitude and longitude values from weewx.conf [station] will be use
                #   If station above a city name or postal code: latitude and longitude results from open-meteo Geocoding API will be use
                # If no station is selected, latitude and longitude are primarily used for the API query.
                #latitude = replace_me
                #longitude = replace_me

                # optional, a prefix for each observation, e.g. "brightsky" results "brightskyObersvationname"
                # Useful if multiple services are used to be able to distinguish the data, see also weewx-DWD documentation.
                # default: ""
                #prefix = replace_me

                # optional, used for queries where a language is required, e.g. Open-Meteo geocoding API.
                # default: value from section [[forecast]]
                #lang = replace_me

                # optional, 'belchertown', 'dwd' or 'aeris'
                # default: value from section [[forecast]]
                #icon_set = replace_me

                # optional, debug level, e.g. 0 = no debug infos, 1 = min debug infos, 2 = more debug infos, >=3 = max debug infos.
                # default: 0
                #debug = replace_me

                # optional, logging for services.
                # defaults: value from section [WeatherServices]
                #log_success = replace_me
                #log_failure = replace_me
            ...
            [[[other_unique_identifier_for_a_service]]]
            ...
        ...
    
    Brightsky API URL Builder
    https://brightsky.dev/docs/#tag--weather
    
    Brightsky GitHub:
    https://github.com/jdemaeyer/brightsky
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
import dateutil.parser
import json
import random
import copy

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
        log = logging.getLogger("user.weatherservices")

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
            syslog.syslog(level, 'user.weatherservices: %s' % msg)

        def logdbg(msg):
            logmsg(syslog.LOG_DEBUG, msg)

        def loginf(msg):
            logmsg(syslog.LOG_INFO, msg)

        def logerr(msg):
            logmsg(syslog.LOG_ERR, msg)

import weewx
from weewx.engine import StdService
import weeutil.weeutil
import weewx.accum
import weewx.units
import weewx.wxformulas
import weewx.almanac

for group in weewx.units.std_groups:
    weewx.units.std_groups[group].setdefault('group_coordinate','degree_compass')

# DWD CDC 10 Minutes radiation unit
# https://opendata.dwd.de/climate_environment/CDC/observations_germany/climate/10_minutes/solar/now/BESCHREIBUNG_obsgermany_climate_10min_solar_now_de.pdf
# https://opendata.dwd.de/climate_environment/CDC/observations_germany/climate/10_minutes/solar/now/DESCRIPTION_obsgermany_climate_10min_solar_now_en.pdf
# TODO evaluate formula for:
# DS_10 - 10min-sum of diffuse solar radiation - unit J/cm^2
# GS_10 - 10min-sum of solar incoming radiation - unit J/cm^2
# LS_10 - 10min-sum of longwave downward radiation - unit J/cm^2
if weewx.units.conversionDict.get('joule_per_cm_squared_10minutes') is None:
    weewx.units.conversionDict.setdefault('joule_per_cm_squared_10minutes',{})
if weewx.units.conversionDict['joule_per_cm_squared_10minutes'].get('watt_per_meter_squared') is None:
    weewx.units.conversionDict['joule_per_cm_squared_10minutes']['watt_per_meter_squared'] = lambda x : (x * 10000) / 600

# Cloud cover icons

N_ICON_LIST = [
    # Belchertown day, Belchertown night, DWD icon, Aeris code, Aeris icon
    ('clear-day.png','clear-night.png','0-8.png','CL','clear'),
    ('mostly-clear-day.png','mostly-clear-night.png','2-8.png','FW','fair'),
    ('partly-cloudy-day.png','partly-cloudy-night.png','5-8.png','SC','pcloudy'),
    ('mostly-cloudy-day.png','mostly-cloudy-night.png','5-8.png','BK','mcloudy'),
    ('cloudy.png','cloudy.png','8-8.png','OV','cloudy')]
    
def get_cloudcover(n):
    """ get icon for cloud cover percentage """
    if n<7:
        icon = N_ICON_LIST[0]
    elif n<32:
        icon = N_ICON_LIST[1]
    elif n<70:
        icon = N_ICON_LIST[2]
    elif n<95:
        icon = N_ICON_LIST[3]
    else:
        icon = N_ICON_LIST[4]
    return icon


def wget(url,log_success=False,log_failure=True):
    """ download  """
    headers={'User-Agent':'weewx-DWD'}
    reply = requests.get(url,headers=headers)

    if reply.status_code==200:
        if log_success:
            loginf('Successfully downloaded %s' % reply.url)
        return reply.content
    elif reply.status_code==400:
        if log_failure:
            reason = reply.reason
            # Open-Meteo returned a JSON error object with a reason
            if 'reason' in reply.json():
                reason = str(reply.json()['reason'])
            # Brightsky returned a JSON error object with a error description
            elif 'description' in reply.json():
                reason = str(reply.json()['description'])
            # other services may return a JSON error object with an error message
            elif 'error' in reply.json():
                reason = str(reply.json()['error'])
            logerr("Download Error %s - %s URL=%s" % (reply.status_code, reason, reply.url))
        return None
    else:
        if log_failure:
            logerr('Error downloading %s: %s %s' % (reply.url,reply.status_code,reply.reason))
        return None

def is_night(record,log_success=False,log_failure=True):
    """
    Portions based on the dashboard service Copyright 2021 Gary Roderick gjroderick<at>gmail.com
    and distributed under the terms of the GNU Public License (GPLv3).

    To get the correct icon (ww Code 0..4) calculates sun rise and sun set
    and determines whether the dateTime field in the record concerned falls
    outside of the period sun rise to sun set.

    Input:
        record: Result from getRecord()
    Returns:
        False if the dateTime field is during the daytime otherwise True.
    """
    try:
        dateTime = record['dateTime'][0]
        latitude = record['latitude'][0]
        longitude = record['longitude'][0]
        altitude = record['altitude'][0]
    except LookupError as e:
        if log_failure:
            logerr("thread '%s': is_night %s - %s" % (self.name, e.__class__.__name__, e))
        return "N/A"

    # Almanac object gives more accurate results if current temp and
    # pressure are provided. Initialise some defaults.
    temperature_c = 15.0
    pressure_mbar = 1010.0
    # Record:
    # 'dateTime': (1676905200, 'unix_epoch', 'group_time')
    # 'outTemp': (10.2, 'degree_C', 'group_temperature')
    # 'barometer': (1021.0, 'hPa', 'group_pressure')
    if 'outTemp' in record:
        temperature_c = weewx.units.convert(record['outTemp'], "degree_C")[0]
    if 'barometer' in record:
        pressure_mbar = weewx.units.convert(record['barometer'], "mbar")[0]

    # get our almanac object
    almanac = weewx.almanac.Almanac(dateTime,
                                    latitude,
                                    longitude,
                                    altitude,
                                    temperature_c,
                                    pressure_mbar)
    # work out sunrise and sunset timestamp so we can determine if it is
    # night or day
    sunrise_ts = almanac.sun.rise.raw
    sunset_ts = almanac.sun.set.raw
    # if we are not between sunrise and sunset it must be night
    return not (sunrise_ts < record['dateTime'][0] < sunset_ts)

# ============================================================================
#
# Class BaseThread
#
# ============================================================================

class BaseThread(threading.Thread):

    def __init__(self, name, log_success=False, log_failure=True):
        super(BaseThread,self).__init__(name=name)
        self.log_success = log_success
        self.log_failure = log_failure
        self.evt = threading.Event()
        self.running = True
        self.query_interval = 300


    def shutDown(self):
        """ request thread shutdown """
        self.running = False
        loginf("thread '%s': shutdown requested" % self.name)
        self.evt.set()


    def get_data(self):
        raise NotImplementedError
        
        
    def getRecord(self):
        raise NotImplementedError


    def run(self):
        """ thread loop """
        loginf("thread '%s' starting" % self.name)
        try:
            while self.running:
                # download and process data
                self.getRecord()
                # time to to the next interval
                waiting = self.query_interval-time.time()%self.query_interval
                if waiting<=60: waiting += self.query_interval
                # do a little bit of load balancing
                waiting -= random.random()*60
                # wait
                logdbg ("thread '%s': wait %s s" % (self.name,waiting))
                self.evt.wait(waiting)
        except Exception as e:
            logerr("thread '%s': main loop %s - %s" % (self.name,e.__class__.__name__,e))
        finally:
            loginf("thread '%s' stopped" % self.name)


# ============================================================================
#
# Class DWDPOIthread
#
# ============================================================================

class DWDPOIthread(BaseThread):

    OBS = {
        'cloud_cover_total':'cloudcover',
        'dew_point_temperature_at_2_meter_above_ground':'dewpoint',
        'diffuse_solar_radiation_last_hour':'solarRad',
        'dry_bulb_temperature_at_2_meter_above_ground':'outTemp',
        'global_radiation_last_hour':'radiation',
        'height_of_base_of_lowest_cloud_above_station':'cloudbase',
        'horizontal_visibility':'visibility',
        'mean_wind_direction_during_last_10 min_at_10_meters_above_ground':'windDir',
        'mean_wind_speed_during last_10_min_at_10_meters_above_ground':'windSpeed',
        'precipitation_amount_last_hour':'rain',
        'present_weather':'presentWeather',
        'pressure_reduced_to_mean_sea_level':'barometer',
        'relative_humidity':'outHumidity',
        'temperature_at_5_cm_above_ground':'extraTemp1',
        'total_snow_depth':'snowDepth',
        'maximum_wind_speed_last_hour':'windGust'}
    
    UNIT = {
        'Grad C': 'degree_C'
        ,'Grad': 'degree_compass'
        ,'W/m2': 'watt_per_meter_squared'
        ,'km/h': 'km_per_hour'
        ,'h': 'hour'
        ,'min': 'minute'
        ,'%': 'percent'
        ,'km': 'km'
        ,'m': 'meter'
        ,'cm': 'cm'
        ,'mm': 'mm'
        ,'hPa': 'hPa'
        ,'CODE_TABLE': 'count'
    }
    
    WEATHER = (
        ('unbekannt','unknown.png','unknown.png'), # 0
        ('wolkenlos','clear-day.png','0-8.png'), # 1
        ('heiter','mostly-clear-day.png','2-8.png'), # 2
        ('bewölkt','mostly-cloudy-day.png','5-8.png'), # 3
        ('bedeckt','cloudy.png','8-8.png'), # 4
        ('Nebel','fog.png','40.png'), # 5
        ('gefrierender Nebel','fog.png','48.png'), # 6
        ('leichter Regen','rain.png','7.png'), # 7
        ('Regen','rain.png','8.png'), # 8
        ('kräftiger Regen','rain.png','9.png'), # 9
        ('gefrierender Regen','sleet.png','66.png'), # 10
        ('kräftiger gefrierender Regen','sleet.png','67.png'), # 11
        ('Schneeregen','sleet.png','12.png'), # 12
        ('kräftiger Schneeregen','sleet.png','13.png'), # 13
        ('leichter Schneefall','snow.png','14.png'), # 14
        ('Schneefall','snow.png','15.png'), # 15
        ('kräftiger Schneefall','snow.png','16.png'), # 16
        ('Eiskörner','snow.png','17.png'), # 17
        ('Regenschauer','rain.png','80.png'), # 18
        ('kräftiger Regenschauer','rain.png','82.png'), # 19
        ('Schneeregenschauer','sleet.png','83.png'), # 20
        ('kräftiger Schneeregenschauer','sleet.png','84.png'), # 21
        ('Schneeschauer','snow.png','85.png'), # 22
        ('kräftiger Schneeschauer','snow.png','86.png'), # 23
        ('Graupelschauer','snow.png','87.png'), # 24
        ('kräftiger Graupelschauer','snow.png','88.png'), # 25
        ('Gewitter ohne Niederschlag','thunderstorm.png','26.png'), # 26
        ('Gewitter','thunderstorm.png','27.png'), # 27
        ('kräftiges Gewitter','thunderstorm.png','28.png'), # 28
        ('Gewitter mit Hagel','thunderstorm.png','29.png'), # 29
        ('kräftiges Gewitter mit Hagel','thunderstrom.png','30.png'), # 30
        ('Böen','wind.png','18.png')) # 31
        
    
    def __init__(self, name, poi_dict, log_success=False, log_failure=True):

        super(DWDPOIthread,self).__init__(name='DWD-POI-'+name, log_success=log_success, log_failure=log_failure)

        self.lock = threading.Lock()
        self.log_success = weeutil.weeutil.to_bool(poi_dict.get('log_success', log_success))
        self.log_failure = weeutil.weeutil.to_bool(poi_dict.get('log_failure', log_failure))
        self.debug = weeutil.weeutil.to_int(poi_dict.get('debug', 0))
        self.lang = poi_dict.get('lang', 'de')

        self.station = poi_dict.get('station')
        self.iconset = weeutil.weeutil.to_int(poi_dict.get('iconset', 4))
        self.lat = weeutil.weeutil.to_float(poi_dict.get('latitude'))
        self.lon = weeutil.weeutil.to_float(poi_dict.get('longitude'))
        self.alt = weeutil.weeutil.to_float(poi_dict.get('altitude'))

        self.data = []
        self.last_get_ts = 0

        prefix = poi_dict.get('prefix', '')
        weewx.units.obs_group_dict.setdefault(prefix+'DateTime','group_time')
        for key in DWDPOIthread.OBS:
            obstype = DWDPOIthread.OBS[key]
            if obstype=='visibility':
                obsgroup = 'group_distance'
            elif obstype=='solarRad':
                obsgroup = 'group_radiation'
            elif obstype=='presentWeather':
                obsgroup = 'group_count'
            else:
                obsgroup = weewx.units.obs_group_dict.get(obstype)
            if obsgroup:
                weewx.units.obs_group_dict.setdefault(obstype, obsgroup)
                weewx.units.obs_group_dict.setdefault(prefix+obstype[0].upper()+obstype[1:],obsgroup)


    def get_data(self):
        """ get buffered data """
        try:
            self.lock.acquire()
            """
            try:
                last_ts = self.data[-1]['time']
                interval = last_ts - self.last_get_ts
                self.last_get_ts = last_ts
            except (LookupError,TypeError,ValueError,ArithmeticError):
                interval = None
            """
            interval = 1
            data = self.data
            #print('POI',data)
        finally:
            self.lock.release()
        #loginf("get_data interval %s data %s" % (interval,data))
        return data,interval


    @staticmethod
    def to_float(x):
        """ convert value out of the CSV file to float """
        try:
            if x[0:1]=='--': raise ValueError('no number')
            if ',' in x:
                return float(x.replace(',','.'))
            if '.' in x:
                return float(x)
            return int(x)
        except Exception:
            pass
        return None
        
    
    @staticmethod
    def get_ww(present_weather, night):
        """ get weather description from value of 'present_weather' 
        
            ww is not required, so it is None.
            
            returns: (ww,german_text,english_text,severity,belchertown_icon,dwd_icon,aeris_icon)
        """
        try:
            x = DWDPOIthread.WEATHER[present_weather]
        except (LookupError,TypeError):
            x = ('Wetterzustand nicht gemeldet','unknown.png','','')
        if present_weather and present_weather<5:
            # clouds only, nothing more
            night = 1 if night else 0
            idx = (0,0,1,3,4)[present_weather]
            aeris = N_ICON_LIST[idx][4] + ('n' if night==1 else '') + '.png'
            return (None,x[0],'',26,N_ICON_LIST[idx][night],N_ICON_LIST[idx][2],aeris)
        return (None,x[0],'',0,x[1],x[2],'')
        
    
    def getRecord(self):
        """ download and process POI weather data """
        url = 'https://opendata.dwd.de/weather/weather_reports/poi/'+self.station+'-BEOB.csv'
        try:
            reply = wget(url,
                     log_success=self.log_success,
                     log_failure=self.log_failure)
            reply = reply.decode('utf-8')
        except Exception as e:
            logerr("thread '%s': wget %s - %s" % (self.name,e.__class__.__name__,e))
            return
        x = []
        ii = 0;
        for ln in csv.reader(reply.splitlines(),delimiter=';'):
            if ii==0:
                # column names
                names = ln
            elif ii==1:
                # units
                units = ln
            elif ii==2:
                # german column names
                gnames = ln
            else:
                # data lines
                dt = ln[0].split('.')
                ti = ln[1].split(':')
                d = datetime.datetime(int(dt[2])+2000,int(dt[1]),int(dt[0]),int(ti[0]),int(ti[1]),0,tzinfo=datetime.timezone(datetime.timedelta(),'UTC'))
                y = dict()
                y['dateTime'] = (int(d.timestamp()),'unix_epoch','group_time')
                y['interval'] = (60,'minute','group_interval')
                for idx,val in enumerate(ln):
                    if idx==0:
                        y['date'] = (val,None,None)
                    elif idx==1:
                        y['time'] = (val,None,None)
                    else:
                        col = DWDPOIthread.OBS.get(names[idx])
                        if col is None:
                            continue
                        unit = DWDPOIthread.UNIT.get(units[idx],units[idx])
                        if unit=='degree_C':
                            grp = 'group_temperature'
                        elif unit=='percent':
                            grp = 'group_percent'
                        else:
                            grp = weewx.units.obs_group_dict.get(col)
                        if col and val is not None:
                            y[col] = (DWDPOIthread.to_float(val),
                                      unit,
                                      grp)

                if self.lat is not None:
                    y['latitude'] = (self.lat,'degree_compass','group_coordinate')
                if self.lon is not None:
                    y['longitude'] = (self.lon,'degree_compass','group_coordinate')
                if self.alt is not None:
                    y['altitude'] = (self.alt,'meter','group_altitude')

                night = is_night(y, log_success=(self.log_success or self.debug > 0),
                                    log_failure=(self.log_failure or self.debug > 0))
                if night != "N/A":
                    y['day'] = (0 if night else 1,'count','group_count')
                else:
                    y['day'] = (None,'count','group_count')
                    night = False
                    if self.log_failure or self.debug > 0:
                        logerr("thread '%s': Determining day or night was not possible." % self.name)

                wwcode = DWDPOIthread.get_ww(y['presentWeather'][0], night)
                if wwcode:
                    y['icon'] = (wwcode[self.iconset],None,None)
                    y['icontitle'] = (wwcode[1],None,None)
                x.append(y)
            ii += 1
        try:
            self.lock.acquire()
            self.data = x
        finally:
            self.lock.release()
        if self.debug > 0 and len(x) > 0:
            logdbg("thread '%s': result=%s" % (self.name, str(x[0])))


# ============================================================================
#
# Class DWDCDCthread
#
# ============================================================================

class DWDCDCthread(BaseThread):

    BASE_URL = 'https://opendata.dwd.de/climate_environment/CDC/observations_germany/climate'
    
    OBS = {
        'STATIONS_ID':('station_id',None,None),
        'MESS_DATUM_ENDE':('MESS_DATUM_ENDE',None,None),
        'QN':('quality_level',None,None),
        # wind
        'FF_10':('windSpeed','meter_per_second','group_speed'),
        'DD_10':('windDir','degree_compass','group_direction'),
        # wind gust
        'FX_10':('windGust','meter_per_second','group_speed'),
        'DX_10':('windGustDir','degree_compass','group_direction'),
        # air temperature
        'PP_10':('pressure','hPa','group_pressure'),
        'TT_10':('outTemp','degree_C','group_temperature'),
        'TM5_10':('extraTemp1','degree_C','group_temperature'),
        'RF_10':('outHumidity','percent','group_percent'),
        'TD_10':('dewpoint','degree_C','group_temperature'),
        # precipitation
        'RWS_DAU_10':('rainDur','minute','group_deltatime'),
        'RWS_10':('rain','mm','group_rain'),
        'RWS_IND_10':('rainIndex',None,None),
        # solar
        'DS_10':('solarRad','joule_per_cm_squared_10minutes','group_radiation'),
        'GS_10':('radiation','joule_per_cm_squared_10minutes','group_radiation'),
        'SD_10':('sunshineDur','hour','group_deltatime'),
        'LS_10':('LS_10','joule_per_cm_squared_10minutes','group_radiation')}
        
    DIRS = {
        'air':('air_temperature','10minutenwerte_TU_','_now.zip','Meta_Daten_zehn_min_tu_'),
        'wind':('wind','10minutenwerte_wind_','_now.zip','Meta_Daten_zehn_min_ff_'),
        'gust':('extreme_wind','10minutenwerte_extrema_wind_','_now.zip','Meta_Daten_zehn_min_fx_'),
        'precipitation':('precipitation','10minutenwerte_nieder_','_now.zip','Meta_Daten_zehn_min_rr_'),
        'solar':('solar','10minutenwerte_SOLAR_','_now.zip','Meta_Daten_zehn_min_sd_')}


    def __init__(self, name, cdc_dict, log_success=False, log_failure=True):

        super(DWDCDCthread,self).__init__(name='DWD-CDC-'+name, log_success=log_success, log_failure=log_failure)

        self.lock = threading.Lock()
        self.log_success = weeutil.weeutil.to_bool(cdc_dict.get('log_success', log_success))
        self.log_failure = weeutil.weeutil.to_bool(cdc_dict.get('log_failure', log_failure))
        self.debug = weeutil.weeutil.to_int(cdc_dict.get('debug', 0))
        self.lang = cdc_dict.get('lang', 'de')

        self.station = cdc_dict.get('station')
        self.iconset = weeutil.weeutil.to_int(cdc_dict.get('iconset', 4))
        self.lat = None
        self.lon = None
        self.alt = None

        self.data = []
        self.maxtime = None
        self.last_get_ts = 0

        observations = cdc_dict.get('observations')
        if observations is not None:
            observations = weeutil.weeutil.option_as_list(observations)
        else:
            observations = ('air','wind','gust','precipitation','solar')
        url = DWDCDCthread.BASE_URL+'/10_minutes/'
        self.urls = []
        for obs in observations:
            jj = DWDCDCthread.DIRS.get(obs)
            if jj:
                self.urls.append(url+jj[0]+'/now/'+jj[1]+self.station+jj[2])
                self.get_meta_data(url+jj[0]+'/meta_data/'+jj[3]+self.station+'.zip')
            else:
                logerr("thread '%s': unknown observation group %s" % (self.name,obs))

        prefix = cdc_dict.get('prefix', '')
        weewx.units.obs_group_dict.setdefault(prefix+'DateTime','group_time')
        for key in DWDCDCthread.OBS:
            obs = DWDCDCthread.OBS[key]
            obstype = obs[0]
            obsgroup = obs[2]
            if obsgroup:
                weewx.units.obs_group_dict.setdefault(obstype, obsgroup)
                weewx.units.obs_group_dict.setdefault(prefix+obstype[0].upper()+obstype[1:],obsgroup)
        weewx.units.obs_group_dict.setdefault(prefix+'Barometer','group_pressure')
        weewx.units.obs_group_dict.setdefault(prefix+'Altimeter','group_pressure')


    def get_data(self):
        """ get buffered data  """
        try:
            self.lock.acquire()
            """
            try:
                last_ts = self.data[-1]['time']
                interval = last_ts - self.last_get_ts
                self.last_get_ts = last_ts
            except (LookupError,TypeError,ValueError,ArithmeticError):
                interval = None
            """
            interval = 10
            data = self.data
            maxtime = self.maxtime
            #print('CDC',data)
        finally:
            self.lock.release()
        #loginf("get_data interval %s data %s" % (interval,data))
        return data,interval,maxtime
        

    def decodezip(self, zipdata):
        zz = zipfile.ZipFile(io.BytesIO(zipdata),'r')
        for ii in zz.namelist():
            return zz.read(ii).decode(encoding='utf-8')
        return None

        
    def decodecsv(self, csvdata):
        x = []
        first = True
        for ln in csv.reader(csvdata.splitlines(),delimiter=';'):
            if first:
                first = False
                names = ln
            else:
                y = dict()
                for idx,val in enumerate(ln):
                    nm = names[idx].strip()
                    if idx==0:
                        # station id
                        val = val.strip()
                    elif idx==1:
                        # date and time (UTC)
                        d = datetime.datetime(int(val[0:4]),int(val[4:6]),int(val[6:8]),int(val[8:10]),int(val[10:12]),0,tzinfo=datetime.timezone(datetime.timedelta(),'UTC'))
                        y['dateTime'] = (int(d.timestamp()),'unix_epoch','group_time')
                    elif nm=='QN':
                        val = int(val)
                    else:
                        # data columns
                        try:
                            val = float(val)
                            if val==-999.0: val=None
                        except (ValueError,TypeError,ArithmeticError):
                            pass
                    if val!='eor':
                        col = DWDCDCthread.OBS.get(nm,(nm,None,None))
                        y[col[0]] = (val,col[1],col[2])
                if 'windDir' in y:
                    y['windDir10'] = y['windDir']
                if 'windSpeed' in y:
                    y['windSpeed10'] = y['windSpeed']
                if 'pressure' in y and 'altimeter' not in y and self.alt is not None:
                    try:
                        y['altimeter'] = (weewx.wxformulas.altimeter_pressure_Metric(y['pressure'][0],self.alt),'hPa','group_pressure')
                    except Exception as e:
                        logerr("thread '%s': altimeter %s" % (self.name,e))
                if 'pressure' in y and 'outTemp' in y and 'barometer' not in y and self.alt is not None:
                    try:
                        y['barometer'] = (weewx.wxformulas.sealevel_pressure_Metric(y['pressure'][0],self.alt,y['outTemp'][0]),'hPa','group_pressure')
                    except Exception as e:
                        logerr("thread '%s': barometer %s" % (self.name,e))
                x.append(y)
        return x

    
    def get_meta_data(self, url):
        try:
            func = 'wget'
            reply = wget(url,log_success=self.log_success,log_failure=self.log_failure)
            func = 'decodezip'
            zz = zipfile.ZipFile(io.BytesIO(reply),'r')
            func = 'decodecsv'
            for ii in zz.namelist():
                if ii[0:20]=='Metadaten_Geographie':
                    txt = zz.read(ii).decode(encoding='utf-8')
                    x = []
                    for ln in csv.reader(txt.splitlines(),delimiter=';'):
                        x.append(ln)
                    if x:
                        self.alt = float(x[-1][1])
                        self.lat = float(x[-1][2])
                        self.lon = float(x[-1][3])
                        loginf("thread '%s': id %s, name '%s', lat %.4f°, lon %.4f°, alt %.1f m" % (
                                self.name,
                                x[-1][0],x[-1][6],
                                self.lat,self.lon,self.alt))

        except Exception as e:
            logerr("thread '%s': %s %s %s" % (self.name,func,e.__class__.__name__,e))
    
    
    def getRecord(self):
        x = None
        ti = None
        maxtime = None
        for url in self.urls:
            try:
                # download data in ZIP format from DWD's server
                func = 'wget'
                reply = wget(url,log_success=self.log_success,log_failure=self.log_failure)
                if not reply: raise TypeError('no data')
                # extract data file out of the downloaded ZIP file
                func = 'decodezip'
                txt = self.decodezip(reply)
                if not txt: raise FileNotFoundError('no file inside ZIP')
                # convert CSV data to Python array
                func = 'decodecsv'
                tab = self.decodecsv(txt)
                # process data
                if x:
                    func = 'other table'
                    for ii in tab:
                        if ii['dateTime'][0]>x[-1]['dateTime'][0]:
                            ti[ii['dateTime']] = len(x)
                            x.append(ii)
                        else:
                            x[ti[ii['dateTime']]].update(ii)
                    # maximum timestamp for which there are all kinds
                    # of records available
                    if tab[-1]['dateTime'][0]<maxtime[0]:
                        maxtime = tab[-1]['dateTime']
                else:
                    func = 'first table'
                    x = tab
                    ti = {vv['dateTime']:ii for ii,vv in enumerate(tab)}
                    maxtime = tab[-1]['dateTime']
            except Exception as e:
                logerr("thread '%s': %s %s %s" % (self.name,func,e.__class__.__name__,e))
        if x:
            for idx,_ in enumerate(x):
                x[idx]['interval'] = (10,'minute','group_interval')
                if self.lat is not None:
                    x[idx]['latitude'] = (self.lat,'degree_compass','group_coordinate')
                if self.lon is not None:
                    x[idx]['longitude'] = (self.lon,'degree_compass','group_coordinate')
                if self.alt:
                    x[idx]['altitude'] = (self.alt,'meter','group_altitude')
        #print(x[ti[maxtime]])
        try:
            self.lock.acquire()
            self.data = x
            self.maxtime = ti[maxtime] if ti and maxtime else None
        finally:
            self.lock.release()
        if self.debug >= 0:
            logdbg("thread '%s': result=%s" % (self.name, str(self.data[self.maxtime])))


# ============================================================================
#
# Class ZAMGthread
#
# ============================================================================

class ZAMGthread(BaseThread):

    # https://dataset.api.hub.zamg.ac.at/v1/station/historical/klima-v1-10min/metadata
    # https://dataset.api.hub.zamg.ac.at/v1/docs/quickstart.html
    # https://dataset.api.hub.zamg.ac.at/v1/docs/daten.html
    
    # Meßnetz:
    # https://www.zamg.ac.at/cms/de/dokumente/klima/dok_messnetze/Stationsliste_20230101.pdf
    
    BASE_URL = 'https://dataset.api.hub.zamg.ac.at'
    
    # /v1/{grid,timeseries,station}/{historical,current,forecast}/{resource_id}/
    #
    # Nicht alle Kombinationen funktionieren. Die Möglichkeiten können wie
    # folgt abgefragt werden:
    #
    # https://dataset.api.hub.zamg.ac.at/v1/datasets?type={grid,timeseries,station}&mode={historical,current,forecast}
    
    RESOURCE_ID = (
        "inca-v1-1h-1km", # INCA stündlich
        "klima-v1-1d",    # Meßstationen Tagesdaten
        "klima-v1-10min", # Meßstationen Zehnminutendaten
        "klima-v1-1m",    # Meßstationen Monatsdaten
        "tawes-v1-10min", # Tawes Meßstationen
        "synop-v1-1h"     # Synopdaten
    )
    
    OBS = {
        'DD':('windDir','degree_compass','group_direction'),
        'DDX':('windGustDir','degree_compass','group_direction'),
        'FFAM':('windSpeed','meter_per_second','group_speed'),
        'FFX':('windGust','meter_per_second','group_speed'),
        'GLOW':('radiation','watt_per_meter_squared','group_radiation'),
        'P':('pressure','hPa','group_pressure'),
        'PRED':('pred','hPa','group_pressure'), # altimeter or barometer?
        'RFAM':('humidity','percent','group_percent'),
        'SCHNEE':('snowDepth','cm','group_rain'),
        'S0':('sunshineDur','second','group_deltatime'),
        'TL':('outTemp','degree_C','group_temperature'),
        'TP':('dewpoint','degree_C','group_temperature'),
        'TS':('extraTemp1','degree_C','group_temperature'),
        'RR':('rain','mm','group_rain')
    }
    
    UNIT = {
        '°':'degree_compass',
        '°C':'degree_C',
        'm/s':'meter_per_second',
        'mm':'mm',
        'cm':'cm',
        'W/m²':'watt_per_meter_squared',
        'hPa':'hPa',
        'min':'minute',
        'sec':'second',
    }
    
    DIRS = {
        'air':['TL','TS','P','PRED','RFAM'],
        'wind':['DD','FFAM'],
        'gust':['DDX','FFX'],
        'precipitation':['RR'],
        'solar':['GLOW']
    }
    

    def __init__(self, name, zamg_dict, log_success=False, log_failure=True):

        super(ZAMGthread,self).__init__(name='ZAMG-'+name, log_success=log_success, log_failure=log_failure)

        self.lock = threading.Lock()
        self.log_success = weeutil.weeutil.to_bool(zamg_dict.get('log_success', log_success))
        self.log_failure = weeutil.weeutil.to_bool(zamg_dict.get('log_failure', log_failure))
        self.debug = weeutil.weeutil.to_int(zamg_dict.get('debug', 0))
        self.lang = zamg_dict.get('lang', 'de')

        self.station = zamg_dict.get('station')
        self.iconset = weeutil.weeutil.to_int(zamg_dict.get('iconset', 4))
        self.user = zamg_dict.get('user')
        self.passwd = zamg_dict.get('password')
        self.lat = None
        self.lon = None
        self.alt = None

        self.data = dict()
        
        datasets = self.get_datasets('station','current')
        if datasets:
            self.current_url = datasets[0]['url']
        else:
            self.current_url = None
        self.get_meta_data()
        
        observations = zamg_dict.get('observations')
        if observations is not None:
            observations = weeutil.weeutil.option_as_list(observations)
        else:
            observations = ('air','wind','gust','precipitation','solar')
        self.observations = []
        for observation in observations:
            if observation in ZAMGthread.OBS:
                jj = [observation]
            else:
                jj = ZAMGthread.DIRS.get(observation)
            self.observations.extend(jj)
        
        prefix = zamg_dict.get('prefix', '')
        weewx.units.obs_group_dict.setdefault(prefix+'DateTime','group_time')
        for key in ZAMGthread.OBS:
            obs = ZAMGthread.OBS[key]
            obstype = obs[0]
            obsgroup = obs[2]
            if obsgroup:
                weewx.units.obs_group_dict.setdefault(obstype, obsgroup)
                weewx.units.obs_group_dict.setdefault(prefix+obstype[0].upper()+obstype[1:],obsgroup)
        weewx.units.obs_group_dict.setdefault(prefix+'Barometer','group_pressure')
        weewx.units.obs_group_dict.setdefault(prefix+'Altimeter','group_pressure')


    def get_data(self):
        try:
            self.lock.acquire()
            x = self.data
        finally:
            self.lock.release()
        return x,1


    def get_datasets(self, type, mode):
        """ get which datasets are available
        
            type: 'grid', 'timeseries', 'station'
            mode: 'historical', 'current', 'forecast'
        """
        url = ZAMGthread.BASE_URL+'/v1/datasets?type='+type+'&mode='+mode
        reply = wget(url,log_success=self.log_success,log_failure=self.log_failure)
        x = []
        if reply:
            reply = json.loads(reply)
            # Example:
            # {
            #   "/station/current/tawes-v1-10min": {    <-- resource_id
            #     "type": "station",
            #     "mode": "current",
            #     "response_formats": [
            #       "geojson",
            #       "csv"
            #     ],
            #     "url": "https://dataset.api.hub.zamg.ac.at/v1/station/current/tawes-v1-10min"
            #   }
            # }
            for resource_id in reply:
                x.append({
                    'resource_id': resource_id,
                    'url': reply[resource_id]['url']
                })
        return x

        
    def get_meta_data(self):
        url = self.current_url+'/metadata?station_ids=%s' % self.station
        reply = wget(url)
        if reply:
            reply = json.loads(reply)
            stations = reply['stations']
            for station in stations:
                if station['id']==self.station:
                    self.lat = float(station['lat'])
                    self.lon = float(station['lon'])
                    self.alt = float(station['altitude'])
                    self.locationName = station['name']
                    self.locationState = station['state']
                    loginf("thread '%s': id %s, name '%s', lat %.4f°, lon %.4f°, alt %.1f m" % (
                                self.name,
                                station['id'],station['name'],
                                self.lat,self.lon,self.alt))
                    break
    
    
    def getRecord(self):
        url = self.current_url+'?parameters=%s&station_ids=%s&output_format=geojson' % (','.join(self.observations),self.station)
        try:
            reply = wget(url, log_success=self.log_success, log_failure=self.log_failure)
            if reply:
                reply = json.loads(reply)
                x = dict()
                ts = reply['timestamps'][-1].split('T')
                dt = ts[0].split('-')
                ts = ts[1].split('+')
                ti = ts[0].split(':')
                d = datetime.datetime(int(dt[0]),int(dt[1]),int(dt[2]),int(ti[0]),int(ti[1]),0,tzinfo=datetime.timezone(datetime.timedelta(),'UTC'))
                x['dateTime'] = (int(d.timestamp()),'unix_epoch','group_time')
                observations = reply['features'][0]['properties']['parameters']
                for observation in observations:
                    try:
                        name = observations[observation]['name']
                        unit = observations[observation]['unit']
                        unit = ZAMGthread.UNIT.get(unit,unit)
                        val = float(observations[observation]['data'][-1])
                        obs = ZAMGthread.OBS.get(observation)
                        obstype = obs[0]
                        obsgroup = obs[2]
                        x[obstype] = (val,unit,obsgroup)
                    except Exception as e:
                        if self.log_failure:
                            logerr("thread '%s': %s %s" % (self.name,observation,e))
                if 'pressure' in x and 'altimeter' not in x and self.alt is not None:
                    try:
                        x['altimeter'] = (weewx.wxformulas.altimeter_pressure_Metric(x['pressure'][0],self.alt),'hPa','group_pressure')
                    except Exception as e:
                        logerr("thread '%s': altimeter %s" % (self.name,e))
                if 'pressure' in x and 'outTemp' in x and 'barometer' not in x and self.alt is not None:
                    try:
                        x['barometer'] = (weewx.wxformulas.sealevel_pressure_Metric(x['pressure'][0],self.alt,x['outTemp'][0]),'hPa','group_pressure')
                    except Exception as e:
                        logerr("thread '%s': barometer %s" % (self.name,e))
                if x:
                    x['interval'] = (10,'minute','group_interval')
                    if self.lat is not None:
                        x['latitude'] = (self.lat,'degree_compass','group_coordinate')
                    if self.lon is not None:
                        x['longitude'] = (self.lon,'degree_compass','group_coordinate')
                    if self.alt:
                        x['altitude'] = (self.alt,'meter','group_altitude')
                    if self.debug > 0:
                        logdbg("thread '%s': result=%s" % (self.name, str(x)))
                try:
                    self.lock.acquire()
                    self.data = x
                finally:
                    self.lock.release()
        except Exception as e:
            if self.log_failure:
                logerr("thread '%s': %s" % (self.name,e))


# ============================================================================
#
# Class OPENMETEOthread
#
# ============================================================================

class OPENMETEOthread(BaseThread):

    WEATHERMODELS = {
        # option: (country, weather service, model, API endpoint, exclude list)
        'best_match':('', '', '', 'forecast',['snowfall_height'])
        ,'dwd-icon':('DE', 'DWD', 'ICON', 'dwd-icon',['visibility'])
        ,'ecmwf':('EU', 'ECMWF', 'open IFS', 'ecmwf',['apparent_temperature', 'dewpoint_2m', 'diffuse_radiation_instant', 'evapotranspiration', 'freezinglevel_height', 'rain', 'relativehumidity_2m', 'shortwave_radiation_instant', 'showers', 'snow_depth', 'snowfall_height', 'visibility', 'windgusts_10m'])
        ,'ecmwf_ifs04':('EU', 'ECMWF', 'IFS', 'forecast',['snowfall_height'])
        ,'gem':('CA', 'MSC-CMC', 'GEM+HRDPS', 'gem',['evapotranspiration', 'freezinglevel_height', 'snow_depth', 'snowfall_height', 'visibility'])
        ,'gem_global':('CA', 'MSC-CMC', 'GEM', 'forecast',['snowfall_height'])
        ,'gem_hrdps_continental':('CA', 'MSC-CMC', 'GEM-HRDPS', 'forecast',['snowfall_height'])
        ,'gem_regional':('CA', 'MSC-CMC', 'GEM', 'forecast',['snowfall_height'])
        ,'gem_seamless':('CA', 'MSC-CMC', 'GEM', 'forecast',['snowfall_height'])
        ,'gfs':('US', 'NOAA', 'GFS', 'gfs',['snowfall_height'])
        ,'gfs_global':('US', 'NOAA', 'GFS Global', 'forecast',['snowfall_height'])
        ,'gfs_hrrr':('US', 'NOAA', 'GFS HRRR', 'forecast',['snowfall_height'])
        ,'gfs_seamless':('US', 'NOAA', 'GFS Seamless', 'forecast',['snowfall_height'])
        ,'icon_d2':('DE', 'DWD', 'ICON D2', 'forecast',['snowfall_height'])
        ,'icon_eu':('DE', 'DWD', 'ICON EU', 'forecast',['snowfall_height'])
        ,'icon_global':('DE', 'DWD', 'ICON Global', 'forecast',['snowfall_height'])
        ,'icon_seamless':('DE', 'DWD', 'ICON Seamless', 'forecast',['snowfall_height'])
        ,'jma':('JP', 'JMA', 'GSM+MSM', 'jma',['evapotranspiration', 'freezinglevel_height', 'rain', 'showers', 'snow_depth', 'snowfall_height', 'visibility', 'windgusts_10m'])
        ,'meteofrance':('FR', 'MeteoFrance', 'Arpege+Arome', 'meteofrance',['evapotranspiration', 'freezinglevel_height', 'rain', 'showers', 'snow_depth', 'snowfall_height', 'visibility'])
        ,'metno':('NO', 'MET Norway', 'Nordic', 'metno',['evapotranspiration', 'freezinglevel_height', 'rain', 'showers', 'snow_depth', 'snowfall_height', 'visibility'])
        ,'metno_nordic':('NO', 'MET Norway', 'Nordic', 'forecast',['snowfall_height'])
        # TODO remove 'test' in stable release?
        ,'test':('', '', '', '',[])
    }
    
    # https://open-meteo.com/en/docs
    # Evapotranspiration/UV-Index: 
    # Attention, no capital letters for WeeWX fields. Otherwise the WeeWX field "ET"/"UV" will be formed if no prefix is used!
    # Attention, not all fields available in each model
    # Mapping API field forecast and dwd-icon endpoint -> WeeWX field
    HOURLYOBS = {
        'temperature_2m': 'outTemp'
        ,'apparent_temperature': 'appTemp'
        ,'dewpoint_2m': 'dewpoint' # not available in forecast model ecmwf
        ,'pressure_msl': 'barometer'
        ,'surface_pressure': 'pressure'
        ,'relativehumidity_2m': 'outHumidity' # not available in forecast model ecmwf
        ,'winddirection_10m': 'windDir'
        ,'windspeed_10m': 'windSpeed'
        ,'windgusts_10m': 'windGust' # not available in forecast model ecmwf
        ,'cloudcover': 'cloudcover'
        ,'evapotranspiration': 'et'
        ,'precipitation': 'precipitation'
        ,'rain': 'rain'
        ,'showers': 'shower'
        ,'snowfall':'snow'
        ,'freezinglevel_height':'freezinglevelHeight'
        ,'weathercode':'weathercode'
        ,'snow_depth':'snowDepth'
        ,'shortwave_radiation_instant':'radiation'
        ,'diffuse_radiation_instant':'solarRad'
        ,'visibility':'visibility' # only available by the American weather models.
        ,'snowfall_height':'snowfallHeight' # Europe only
    }

    # Mapping API field -> WeeWX field
    CURRENTOBS = {
        'temperature': 'outTemp'
        ,'windspeed': 'windSpeed'
        ,'winddirection': 'windDir'
        ,'weathercode': 'weathercode'
    }

    # API result contain no units for current_weather
    # Mapping API current_weather unit -> WeeWX unit
    CURRENTUNIT = {
        'temperature': u'°C'
        ,'windspeed': 'km/h'
        ,'winddirection': u'°'
        ,'weathercode': 'wmo code'
        ,'time': 'unixtime'
    }

    # Mapping API hourly unit -> WeeWX unit
    UNIT = {
        u'°': 'degree_compass'
        ,u'°C': 'degree_C'
        ,'mm': 'mm'
        ,'cm': 'cm'
        ,'m': 'meter'
        ,'hPa': 'hPa'
        ,'kPa': 'kPa'
        ,u'W/m²': 'watt_per_meter_squared'
        ,'km/h': 'km_per_hour'
        ,'%': 'percent'
        ,'wmo code': 'count'
        ,'unixtime': 'unix_epoch'
    }

    # https://open-meteo.com/en/docs/dwd-api
    # WMO Weather interpretation codes (WW)
    # Code        Description
    # 0           Clear sky
    # 1, 2, 3     Mainly clear, partly cloudy, and overcast
    # 45, 48      Fog and depositing rime fog
    # 51, 53, 55  Drizzle: Light, moderate, and dense intensity
    # 56, 57      Freezing Drizzle: Light and dense intensity
    # 61, 63, 65  Rain: Slight, moderate and heavy intensity
    # 66, 67      Freezing Rain: Light and heavy intensity
    # 71, 73, 75  Snow fall: Slight, moderate, and heavy intensity
    # 77          Snow grains
    # 80, 81, 82  Rain showers: Slight, moderate, and violent
    # 85, 86      Snow showers slight and heavy
    # 95 *        Thunderstorm: Slight or moderate
    # 96, 99 *    Thunderstorm with slight and heavy hail
    # (*) Thunderstorm forecast with hail is only available in Central Europe

    # TODO Structure?
    #              0       1      2     3          4              5          6
    # WMO Key: [german, english, None, None, Belchertown Icon, DWD Icon, Aeris Icon]
    WEATHER = {
        -1:['unbekannte Wetterbedingungen', 'unknown conditions', '', '', 'unknown.png', 'unknown.png', 'na']
        # 0-3 using N_ICON_LIST, here only Documentation
        ,0:['wolkenlos', 'clear sky', '', '', 'clear-day.png', '0-8.png', 'clear']
        ,1:['heiter', 'mainly clear', '', '','mostly-clear-day.png', '2-8.png', 'fair']
        ,2:['bewölkt', 'partly cloudy', '', '','mostly-cloudy-day.png', '5-8.png', 'pcloudy']
        ,3:['bedeckt', 'overcast', '', '','cloudy.png', '8-8.png', 'cloudy']
        # from here on we evaluate
        ,45:['Nebel', 'fog', '', '','fog.png', '40.png', 'fog']
        ,48:['gefrierender Nebel', 'depositing rime fog', '', '','fog.png', '48.png', '']
        ,51:['leichter Nieselregen', 'light drizzle', '', '','rain.png', '7.png', 'drizzle']
        ,53:['Nieselregen', 'moderate drizzle', '', '','rain.png', '8.png', 'drizzle']
        ,55:['starker Nieselregen', 'dense drizzle', '', '','rain.png', '9.png', 'drizzle']
        ,56:['gefrierender Nieselregen', 'light freezing drizzle', '', '','sleet.png', '66.png', 'freezingrain']
        ,57:['kräftiger gefrierender Nieselregen', 'dense freezing drizzle', '', '','sleet.png', '67.png', 'freezingrain']
        ,61:['leichter Regen', 'slight rain', '', '','rain.png', '7.png', 'rain']
        ,63:['Regen', 'moderate rain', '', '','rain.png', '8.png', 'rain']
        ,65:['starker Regen', 'heavy rain', '', '','rain.png', '9.png', 'rain']
        ,66:['gefrierender Regen', 'light freezing rain', '', '','sleet.png', '66.png', 'freezingrain']
        ,67:['starker gefrierender Regen', 'heavy freezing rain', '', '','sleet.png', '67.png', 'freezingrain']
        ,71:['leichter Schneefall', 'slight snow fall', '', '','snow.png', '14.png', 'snow']
        ,73:['Schneefall', 'moderate snow fall', '', '','snow.png', '15.png', 'snow']
        ,75:['starker Schneefall', 'heavy snow fall', '', '','snow.png', '16.png', 'snow']
        ,77:['Eiskörner', 'snow grains' , '', '','snow.png', '17.png', 'sleet']
        ,80:['leichter Regenschauer', 'slight rain showers', '', '','rain.png', '80.png', 'showers']
        ,81:['Regenschauer', 'moderate rain showers', '', '','rain.png', '80.png', 'showers']
        ,82:['starker Regenschauer', 'heavy rain showers', '', '','rain.png', '82.png', 'showers']
        ,85:['Schneeregen', 'slight snow showers', '', '','sleet.png', '12.png', 'rainandsnow']
        ,86:['starker Schneeregen', 'heavy snow showers', '', '', 'sleet.png', '13.png', 'rainandsnow']
        ,95:['Gewitter', 'thunderstorm', '', '', 'thunderstorm.png', '27.png', 'tstorm']
        ,96:['Gewitter mit Hagel', 'thunderstorm with slight hail', '', '', 'thunderstorm.png', '29.png', 'tstorm']
        ,99:['starkes Gewitter mit Hagel', 'thunderstorm with slight hail', '', '', 'thunderstrom.png', '30.png', 'tstorm']
    }
    
    def get_current_obs(self):
        return OPENMETEOthread.CURRENTOBS

    def get_hourly_obs(self):
        hobs = copy.deepcopy(OPENMETEOthread.HOURLYOBS)
        modelparams = OPENMETEOthread.WEATHERMODELS.get(self.model)
        if modelparams is not None:
            # remove exclude list from obs
            for x in modelparams[4]:
                hobs.pop(x)
        return hobs

    def get_geocoding(self, station):
        """ 
        Get geocoding data with Open-Meteo Geocoding API
        
        Inputs:
           station: String to search for. An empty string or only 1 character will return an empty result.
                    2 characters will only match exact matching locations. 3 and more characters will perform
                    fuzzy matching. The search string can be a location name or a postal code.
        Outputs:
           geocoding result as dict from the first API result or None if errors occurred
        """
        geodata = {}

        baseurl = 'https://geocoding-api.open-meteo.com/v1/search'
        # String to search for.
        params = '?name=%s' % station
        # The number of search results to return. Up to 100 results can be retrieved.
        # here default 1
        params += '&count=1'
        # By default, results are returned as JSON.
        params += '&format=json'
        # Return translated results, if available, otherwise return english or the native location name. Lower-cased.
        params += '&language=%s' % self.lang
        
        url = baseurl + params

        if self.debug >=2:
            logdbg("thread '%s': Geocoding URL=%s" % (self.name, url))

        try:
            reply = wget(url,
                     log_success=(self.log_success or self.debug > 0),
                     log_failure=(self.log_failure or self.debug > 0))
            if reply is not None:
                geodata = json.loads(reply.decode('utf-8'))

                if self.debug >= 3:
                    logdbg("thread '%s': Geocoding returns data=%s" % (self.name, str(geodata)))
                geodata = geodata['results'][0]
                if self.debug >= 3:
                    logdbg("thread '%s': Geocoding station=%s result=%s" % (self.name, station, str(geodata)))
            else:
                if self.log_failure or self.debug > 0:
                    logerr("thread '%s': Geocoding returns None data." % self.name)
                return None
        except (Exception, LookupError) as e:
            if self.log_failure or self.debug > 0:
                logerr("thread '%s': Geocoding %s - %s" % (self.name, e.__class__.__name__, e))
            return None

        # return results
        return geodata

    def __init__(self, name, openmeteo_dict, log_success=False, log_failure=True):
    
        super(OPENMETEOthread,self).__init__(name='OPENMETEO-'+name, log_success=log_success, log_failure=log_failure)

        self.lock = threading.Lock()
        self.log_success = weeutil.weeutil.to_bool(openmeteo_dict.get('log_success', log_success))
        self.log_failure = weeutil.weeutil.to_bool(openmeteo_dict.get('log_failure', log_failure))
        self.debug = weeutil.weeutil.to_int(openmeteo_dict.get('debug', 0))
        self.lang = openmeteo_dict.get('lang', 'de')

        self.iconset = weeutil.weeutil.to_int(openmeteo_dict.get('iconset', 4))
        self.prefix = openmeteo_dict.get('prefix', '')
        self.model = openmeteo_dict.get('model', 'dwd-icon')

        self.current_obs = self.get_current_obs()
        self.hourly_obs = self.get_hourly_obs()

        self.data = []
        self.last_get_ts = 0

        station = openmeteo_dict.get('station', 'ThisStation')
        self.lat = weeutil.weeutil.to_float(openmeteo_dict.get('latitude'))
        self.lon = weeutil.weeutil.to_float(openmeteo_dict.get('longitude'))
        self.alt = weeutil.weeutil.to_float(openmeteo_dict.get('altitude'))
        if self.lat is None or self.lon is None or self.alt is None:
            if station.lower() not in ('thisstation', 'here'):
                # station is a city name or postal code
                geo = self.get_geocoding(station)
                if geo is not None:
                    if self.lat is None:
                        self.lat = weeutil.weeutil.to_float(geo.get('latitude'))
                    if self.lon is None:
                        self.lon = weeutil.weeutil.to_float(geo.get('longitude'))
                    if self.alt is None:
                        self.alt = weeutil.weeutil.to_float(geo.get('elevation'))
                else:
                    raise weewx.ViolatedPrecondition("thread '%s': Could not get geodata for station '%s'" % (self.name, station))
            else:
                raise weewx.ViolatedPrecondition("thread '%s': Configured station is not valid." % self.name)

        for opsapi, obsweewx in self.current_obs.items():
            obsgroup = None
            if obsweewx=='weathercode':
                obsgroup = 'group_count'
            else:
                obsgroup = weewx.units.obs_group_dict.get(obsweewx)
            if obsgroup is not None:
                weewx.units.obs_group_dict.setdefault(obsweewx, obsgroup)
                weewx.units.obs_group_dict.setdefault(self.prefix+obsweewx[0].upper()+obsweewx[1:],obsgroup)

        for opsapi, obsweewx in self.hourly_obs.items():
            if obsweewx=='weathercode':
                # filled with CURRENTOBS
                continue
            obsgroup = None
            if obsweewx=='precipitation':
                obsgroup = 'group_rain'
            elif obsweewx=='shower':
                obsgroup = 'group_rain'
            elif obsweewx=='freezinglevelHeight':
                obsgroup = 'group_altitude'
            elif obsweewx=='snowfallHeight':
                obsgroup = 'group_altitude'
            elif obsweewx=='visibility':
                obsgroup = 'group_distance'
            elif obsweewx=='solarRad':
                obsgroup = 'group_radiation'
            else:
                obsgroup = weewx.units.obs_group_dict.get(obsweewx)
            if obsgroup is not None:
                weewx.units.obs_group_dict.setdefault(obsweewx, obsgroup)
                weewx.units.obs_group_dict.setdefault(self.prefix+obsweewx[0].upper()+obsweewx[1:],obsgroup)

    def get_data(self):
        """ get buffered data """
        try:
            self.lock.acquire()
            """
            try:
                last_ts = self.data[-1]['time']
                interval = last_ts - self.last_get_ts
                self.last_get_ts = last_ts
            except (LookupError,TypeError,ValueError,ArithmeticError):
                interval = None
            """
            interval = 1
            data = self.data
            #print('POI',data)
        finally:
            self.lock.release()
        #loginf("get_data interval %s data %s" % (interval,data))
        return data,interval

    @staticmethod
    def get_ww(wwcode, night):
        """ get weather description from value of 'wwcode' 
            returns: (german_text,english_text,'','',belchertown_icon,dwd_icon,aeris_icon)
        """
        try:
            x = OPENMETEOthread.WEATHER[wwcode]
        except (LookupError,TypeError):
            # fallback
            x = OPENMETEOthread.WEATHER[-1]
        if wwcode < 4:
            # clouds only, nothing more
            night = 1 if night else 0
            idx = (0,1,2,4)[wwcode]
            aeris = N_ICON_LIST[idx][4] + ('n' if night==1 else '') + '.png'
            return (x[0],x[1],'','',N_ICON_LIST[idx][night],N_ICON_LIST[idx][2],aeris)
        return x

    def getRecord(self):
        """ download and process Open-Meteo weather data """

        endpoint = OPENMETEOthread.WEATHERMODELS.get(self.model)[3]
        if endpoint == 'forecast':
            modelparams = '&models=%s' % self.model
        else:
            modelparams = ''

        baseurl = 'https://api.open-meteo.com/v1/%s' % endpoint

        # Geographical WGS84 coordinate of the location
        params = '?latitude=%s' % self.lat
        params += '&longitude=%s' % self.lon

        # The elevation used for statistical downscaling. Per default, a 90 meter digital elevation model is used.
        # You can manually set the elevation to correctly match mountain peaks. If &elevation=nan is specified,
        # downscaling will be disabled and the API uses the average grid-cell height.
        # If a valid height exists, it will be used
        if self.alt is not None:
            params += '&elevation=%s' % self.alt

        # timeformat iso8601 | unixtime
        params += '&timeformat=unixtime'

        # timezone
        # If timezone is set, all timestamps are returned as local-time and data is returned starting at 00:00 local-time.
        # Any time zone name from the time zone database is supported. If auto is set as a time zone, the coordinates will
        # be automatically resolved to the local time zone.
        # using API default
        #params += '&timezone=Europe%2FBerlin'

        # TODO config param?
        # cell_selection, land | sea | nearest
        # Set a preference how grid-cells are selected. The default land finds a suitable grid-cell on land with similar
        # elevation to the requested coordinates using a 90-meter digital elevation model. sea prefers grid-cells on sea.
        # nearest selects the nearest possible grid-cell.
        #params += '&cell_selection=land'

        # TODO use "past_days=1" instead of yesterday?
        # The time interval to get weather data. A day must be specified as an ISO8601 date (e.g. 2022-06-30).
        yesterday = datetime.datetime.now() - datetime.timedelta(1)
        yesterday = datetime.datetime.strftime(yesterday, '%Y-%m-%d')
        today = datetime.datetime.today().strftime('%Y-%m-%d')
        params += '&start_date=%s' % yesterday
        params += '&end_date=%s' % today

        # units
        # The API request is made in the metric system
        # Temperature in celsius
        params += '&temperature_unit=celsius'
        # Wind in km/h
        params += '&windspeed_unit=kmh'
        # Precipitation in mm
        params += '&precipitation_unit=mm'

        # Include current weather conditions in the JSON output.
        # currently contained values (28.01.2023): temperature, windspeed, winddirection, weathercode, time
        params += '&current_weather=true'

        # A list of weather variables which should be returned. Values can be comma separated,
        # or multiple &hourly= parameter in the URL can be used.
        # defined in HOURLYOBS
        params += '&hourly='+','.join([ii for ii in self.hourly_obs])

        # Model
        params += modelparams

        url = baseurl + params

        if self.debug >= 2:
            logdbg("thread '%s': Open-Meteo URL=%s" % (self.name, url))

        apidata = {}
        try:
            reply = wget(url,
                         log_success=(self.log_success or self.debug > 0),
                         log_failure=(self.log_failure or self.debug > 0))
            if reply is not None:
                apidata = json.loads(reply.decode('utf-8'))
            else:
                if self.log_failure or self.debug > 0:
                    logerr("thread '%s': Open-Meteo returns None data." % self.name)
                return
        except Exception as e:
            if self.log_failure or self.debug > 0:
                logerr("thread '%s': Open-Meteo %s - %s" % (self.name, e.__class__.__name__, e))
            return

        # check results
        if apidata.get('hourly') is None:
            if self.log_failure or self.debug > 0:
                logerr("thread '%s': Open-Meteo returns no hourly data." % self.name)
            return

        hourly_units = apidata.get('hourly_units')
        if hourly_units is None:
            if self.log_failure or self.debug > 0:
                logerr("thread '%s': Open-Meteo returns no hourly_units data." % self.name)
            return

        current_weather = apidata.get('current_weather')
        if current_weather is None:
            if self.log_failure or self.debug > 0:
                logerr("thread '%s': Open-Meteo returns no current_weather data." % self.name)
            return

        timelist = apidata['hourly'].get('time')
        if timelist is None:
            if self.log_failure or self.debug > 0:
                logerr("thread '%s': Open-Meteo returns no time periods data." % self.name)
            return

        if not isinstance(timelist, list):
            if self.log_failure or self.debug > 0:
                logerr("thread '%s': Open-Meteo returns time periods data not as list." % self.name)
            return

        if len(timelist) == 0:
            if self.log_failure or self.debug > 0:
                logerr("thread '%s': Open-Meteo returns time periods without data." % self.name)
            return
            

        # holds the return values
        x = []
        y = dict()

        # get the last hourly observation timestamp before the current time
        actts = weeutil.weeutil.to_int(time.time())
        obshts = None
        for ts in timelist:
            if ts > actts:
                break
            obshts = weeutil.weeutil.to_int(ts)
        if obshts is None:
            if self.log_failure or self.debug > 0:
                logerr("thread '%s': Open-Meteo returns timestamps only in the future." % self.name)
            return

        latitude = apidata.get('latitude')
        longitude = apidata.get('longitude')
        altitude = apidata.get('elevation')

        if self.debug >= 3:
            logdbg("thread '%s':    ts now=%s" % (self.name, str(actts)))
            logdbg("thread '%s':    ts now=%s" % (self.name, str( datetime.datetime.fromtimestamp(actts).strftime('%Y-%m-%d %H:%M:%S'))))
            logdbg("thread '%s': ts hourly=%s" % (self.name, str(obshts)))
            logdbg("thread '%s': ts hourly=%s" % (self.name, str( datetime.datetime.fromtimestamp(obshts).strftime('%Y-%m-%d %H:%M:%S'))))
            logdbg("thread '%s': lat %s lon %s alt %s" % (self.name,latitude,longitude,altitude))
            logdbg("thread '%s': model=%s" % (self.name,self.model))
            if self.debug >= 4:
                logdbg("thread '%s': API result: %s" % (self.name, str(apidata)))

        # timestamp current_weather
        obscts = int(current_weather.get('time', 0))

        # final timestamp
        obsts = weeutil.weeutil.to_int(max(obscts, obshts))

        y['dateTime'] = (obsts, 'unix_epoch', 'group_time')
        y['interval'] = (60, 'minute', 'group_interval')

        #get current weather data
        for obsapi, obsweewx in self.current_obs.items():
            obsname = self.prefix+obsweewx[0].upper()+obsweewx[1:]
            if self.debug >= 3:
                logdbg("thread '%s': current: weewx=%s api=%s obs=%s" % (self.name, str(obsweewx), str(obsapi), str(obsname)))
            obsval = current_weather.get(obsapi)
            if obsval is None:
                if self.debug > 2:
                    logdbg("thread '%s': current: Value 'None' for observation %s - %s on timestamp %s" % (self.name, str(obsapi), str(obsname), str(obscts)))
                continue
            # API json response contain no unit data for current_weather observations
            unitapi = OPENMETEOthread.CURRENTUNIT.get(obsapi)
            if unitapi is None:
                if self.log_failure or self.debug > 0:
                    logerr("thread '%s': current: No valid unit for observation %s - %s" % (self.name, str(obsapi), str(obsname)))
                continue
            unitweewx = OPENMETEOthread.UNIT.get(unitapi)
            if unitweewx is None:
                if self.log_failure or self.debug > 0:
                    logerr("thread '%s': current: Could not convert api unit '%s' to weewx unit" % (self.name, str(unitapi)))
                continue
            groupweewx = weewx.units.obs_group_dict.get(obsname)
            y[obsweewx] = (weeutil.weeutil.to_float(obsval), unitweewx, groupweewx)
            if self.debug >= 3:
                logdbg("thread '%s': current: weewx=%s result=%s" % (self.name, str(obsweewx), str(y[obsweewx])))

        if self.debug >= 3:
            logdbg("thread '%s': current: result=%s" % (self.name, str(y)))

        # get hourly weather data
        for obsapi, obsweewx in self.hourly_obs.items():
            obsname = self.prefix+obsweewx[0].upper()+obsweewx[1:]
            if y.get(obsweewx) is not None:
                # filled with current_weather data
                continue
            if self.debug >= 3:
                logdbg("thread '%s': hourly: weewx=%s api=%s obs=%s" % (self.name, str(obsweewx), str(obsapi), str(obsname)))
            obslist = apidata['hourly'].get(obsapi)
            if obslist is None:
                if self.debug >= 2:
                    logdbg("thread '%s': hourly: No value for observation '%s' - '%s'" % (self.name, str(obsapi), str(obsname)))
                continue
            # Build a dictionary with timestamps as key and the corresponding values
            obsvals = dict(zip(timelist, obslist))
            obsval = obsvals.get(obshts)
            if obsval is None:
                if self.debug >= 2:
                    logdbg("thread '%s': hourly: Value 'None' for observation %s - %s on timestamp %s" % (self.name, str(obsapi), str(obsname), str(obshts)))
                continue
            unitapi = hourly_units.get(obsapi)
            if unitapi is None:
                if self.log_failure or self.debug > 0:
                    logerr("thread '%s': hourly: No unit for observation %s - %s" % (self.name, str(obsapi), str(obsname)))
                continue
            unitweewx = OPENMETEOthread.UNIT.get(unitapi)
            if unitweewx is None:
                if self.log_failure or self.debug > 0:
                    logerr("thread '%s': hourly: Could not convert api unit '%s' to weewx unit" % (self.name, str(unitapi)))
                continue
            groupweewx = weewx.units.obs_group_dict.get(obsname)
            # snowDepth from meter to mm, weewx snowDepth is weewx group_rain
            # group_rain has no conversation from meter to mm
            if obsweewx == 'snowDepth':
                obsval = (weeutil.weeutil.to_float(obsval) * 1000)
                unitweewx = 'mm'
            y[obsweewx] = (weeutil.weeutil.to_float(obsval), unitweewx, groupweewx)
            if self.debug >= 3:
                logdbg("thread '%s': hourly: weewx=%s result=%s" % (self.name, str(obsweewx), str(y[obsweewx])))

        if latitude is not None and longitude is not None:
            y['latitude'] = (latitude,'degree_compass','group_coordinate')
            y['longitude'] = (longitude,'degree_compass','group_coordinate')
        if altitude is not None:
            y['altitude'] = (altitude,'meter','group_altitude')

        wwcode = y.get('weathercode')
        if wwcode is not None:
            wwcode = int(wwcode[0])
        else:
            wwcode = -1

        night = is_night(y, log_success=(self.log_success or self.debug > 0),
                         log_failure=(self.log_failure or self.debug > 0))
        if night != "N/A":
            y['day'] = (0 if night else 1,'count','group_count')
        else:
            y['day'] = (None,'count','group_count')
            night = False
            if self.log_failure or self.debug > 0:
                logerr("thread '%s': Determining day or night was not possible." % self.name)

        wwcode = OPENMETEOthread.get_ww(wwcode, night)
        if wwcode:
            y['icon'] = (wwcode[self.iconset],None,None)
            y['icontitle'] = (wwcode[0],None,None)

        y['model'] = (self.model,None,None)

        x.append(y)

        if self.debug > 0:
            logdbg("thread '%s': result=%s" % (self.name, str(x)))

        try:
            self.lock.acquire()
            self.data = x
        finally:
            self.lock.release()


# ============================================================================
#
# Class BRIGHTSKYthread
#
# ============================================================================

class BRIGHTSKYthread(BaseThread):

    # https://brightsky.dev/docs/#overview--on-stations-and-sources
    # Icons nach https://github.com/jdemaeyer/brightsky/issues/111
    # Icons nach https://github.com/jdemaeyer/brightsky/blob/master/brightsky/web.py#L146-L174
    # condition - dry┃fog┃rain┃sleet┃snow┃hail┃thunderstorm┃
    # icon - clear-day┃clear-night┃partly-cloudy-day┃partly-cloudy-night┃cloudy┃fog┃wind┃rain┃sleet┃snow┃hail┃thunderstorm┃

    # Evapotranspiration/UV-Index:
    # Attention, no capital letters for WeeWX fields. Otherwise the WeeWX field "ET"/"UV" will be formed if no prefix is used!
    # Mapping API observation fields -> WeeWX field, unit, group
    OBS = {
        'timestamp': ('dateTime', 'unix_epoch', 'group_time')
        ,'condition': ('APIcondition', None, None)
        ,'icon': ('APIicon', None, None)
        ,'temperature': ('outTemp', 'degree_C', 'group_temperature')
        ,'dew_point': ('dewpoint', 'degree_C', 'group_temperature')
        ,'pressure_msl': ('barometer', 'hPa', 'group_pressure')
        ,'relative_humidity': ('outHumidity', 'percent', 'group_percent')
        ,'wind_speed_10': ('windSpeed10', 'km_per_hour', 'group_speed')
        ,'wind_speed_30': ('windSpeed30', 'km_per_hour', 'group_speed')
        ,'wind_speed_60': ('windSpeed60', 'km_per_hour', 'group_speed')
        ,'wind_direction_10': ('windDir10', 'degree_compass', 'group_direction')
        ,'wind_direction_30': ('windDir30', 'degree_compass', 'group_direction')
        ,'wind_direction_60': ('windDir60', 'degree_compass', 'group_direction')
        ,'wind_gust_speed_10': ('windGust10', 'km_per_hour', 'group_speed')
        ,'wind_gust_speed_30': ('windGust30', 'km_per_hour', 'group_speed')
        ,'wind_gust_speed_60': ('windGust60', 'km_per_hour', 'group_speed')
        ,'wind_gust_direction_10': ('windGustDir10', 'degree_compass', 'group_direction')
        ,'wind_gust_direction_30': ('windGustDir30', 'degree_compass', 'group_direction')
        ,'wind_gust_direction_60': ('windGustDir60', 'degree_compass', 'group_direction')
        ,'cloud_cover': ('cloudcover', 'percent', 'group_percent')
        ,'precipitation_10': ('precipitation10', 'mm', 'group_rain')
        ,'precipitation_30': ('precipitation30', 'mm', 'group_rain')
        ,'precipitation_60': ('precipitation60', 'mm', 'group_rain')
        ,'sunshine_10': ('sunshineDur10', 'minute', 'group_deltatime')
        ,'sunshine_30': ('sunshineDur30', 'minute', 'group_deltatime')
        ,'sunshine_60': ('sunshineDur60', 'minute', 'group_deltatime')
        ,'visibility': ('visibility', 'meter', 'group_distance')
    }

    # Mapping API primary source fields -> WeeWX field, unit, group
    SOURCES = {
        'id': ('APIstationId', None, None)
        ,'dwd_station_id': ('DWDstationId', None, None)
        ,'wmo_station_id': ('WMOstationId', None, None)
        ,'observation_type': ('observationType', None, None)
        ,'lat': ('latitude', 'degree_compass', 'group_coordinate')
        ,'lon': ('longitude', 'degree_compass', 'group_coordinate')
        ,'height': ('altitude', 'meter', 'group_altitude')
        ,'distance': ('distance', 'meter', 'group_distance')
        ,'station_name': ('stationName', None, None)
    }

    # Mapping API icon field to internal icon fields
    CONDITIONS = {
        #                     0       1      2     3          4              5          6
        # BRIGHTSKY Icon: [german, english, None, None, Belchertown Icon, DWD Icon, Aeris Icon]
        'clear-day': ('wolkenlos', 'clear sky', '', '', 'clear-day.png', '0-8.png', 'clear')
        ,'clear-night': ('wolkenlos', 'clear sky', '', '', 'clear-night.png', '0-8.png', 'clearn')
        ,'partly-cloudy-day': ('bewölkt', 'partly cloudy', '', '', 'mostly-cloudy-day.png', '5-8.png', 'pcloudy')
        ,'partly-cloudy-night': ('bewölkt', 'partly cloudy', '', '', 'mostly-cloudy-night.png', '5-8.png', 'pcloudyn')
        ,'cloudy': ('bedeckt', 'overcast', '', '', 'cloudy.png', '8-8.png', 'cloudy')
        ,'hail': ('Hagel', 'hail', '', '', 'hail.png', '13.png', 'freezingrain')
        ,'snow': ('Schneefall', 'snow fall', '', '', 'snow.png', '15.png', 'snow')
        ,'sleet': ('Schneeregen', 'snow showers', '', '', 'sleet.png', '13.png', 'rainandsnow')
        ,'rain': ('Regen', 'rain', '', '', 'rain.png', '8.png', 'rain')
        ,'wind': ('Wind', 'wind', '', '', 'wind.png', '18.png', 'wind')
        ,'fog': ('Nebel', 'fog', '', '', 'fog.png', '40.png', 'fog')
        ,'thunderstorm': ('Gewitter', 'thunderstorm', '', '', 'thunderstorm.png', '27.png', 'tstorm')
    }

    def get_current_obs(self):
        return BRIGHTSKYthread.OBS

    def get_sources_obs(self):
        return BRIGHTSKYthread.SOURCES

    def get_condition_obs(self):
        return BRIGHTSKYthread.CONDITIONS

    def get_geocoding(self, station):
        """
        Get geocoding data with Open-Meteo Geocoding API

        Inputs:
           station: String to search for. An empty string or only 1 character will return an empty result.
                    2 characters will only match exact matching locations. 3 and more characters will perform
                    fuzzy matching. The search string can be a location name or a postal code.
        Outputs:
           geocoding result as dict from the first API result or None if errors occurred
        """
        geodata = {}

        baseurl = 'https://geocoding-api.open-meteo.com/v1/search'
        # String to search for.
        params = '?name=%s' % station
        # The number of search results to return. Up to 100 results can be retrieved.
        # here default 1
        params += '&count=1'
        # By default, results are returned as JSON.
        params += '&format=json'
        # Return translated results, if available, otherwise return english or the native location name. Lower-cased.
        params += '&language=%s' % self.lang

        url = baseurl + params

        if self.debug >= 2:
            logdbg("thread '%s': Geocoding URL=%s" % (self.name, url))

        try:
            reply = wget(url,
                         log_success=(self.log_success or self.debug > 0),
                         log_failure=(self.log_failure or self.debug > 0))
            if reply is not None:
                geodata = json.loads(reply.decode('utf-8'))

                if self.debug >= 3:
                    logdbg("thread '%s': Geocoding returns data=%s" % (self.name, str(geodata)))
                geodata = geodata['results'][0]
                if self.debug >= 3:
                    logdbg("thread '%s': Geocoding station=%s result=%s" % (self.name, station, str(geodata)))
            else:
                if self.log_failure or self.debug > 0:
                    logerr("thread '%s': Geocoding returns None data." % self.name)
                return None
        except (Exception, LookupError) as e:
            if self.log_failure or self.debug > 0:
                logerr("thread '%s': Geocoding %s - %s" % (self.name, e.__class__.__name__, e))
            return None

        # return results
        return geodata

    def __init__(self, name, brightsky_dict, log_success=False, log_failure=True):

        super(BRIGHTSKYthread, self).__init__(name='BRIGHTSKY-' + name, log_success=log_success,
                                              log_failure=log_failure)

        self.lock = threading.Lock()
        self.log_success = weeutil.weeutil.to_bool(brightsky_dict.get('log_success', log_success))
        self.log_failure = weeutil.weeutil.to_bool(brightsky_dict.get('log_failure', log_failure))
        self.debug = weeutil.weeutil.to_int(brightsky_dict.get('debug', 0))
        self.lang = brightsky_dict.get('lang', 'de')

        self.iconset = weeutil.weeutil.to_int(brightsky_dict.get('iconset', 4))
        self.prefix = brightsky_dict.get('prefix', '')

        self.current_obs = self.get_current_obs()
        self.sources_obs = self.get_sources_obs()

        self.primary_api_query = None

        self.data = []
        self.last_get_ts = 0

        station = brightsky_dict.get('station')
        if station.lower() not in ('thisstation', 'here'):
            spl = station.lower().split('_')
            if len(spl) >= 2:
                # station id is selected?
                if spl[0] == 'api':
                    self.primary_api_query = '?source_id=%s' % spl[1]
                elif spl[0] == 'dwd':
                    self.primary_api_query = '?dwd_station_id=%s' % str(spl[1])
                elif spl[0] == 'wmo':
                    self.primary_api_query = '?wmo_station_id=%s' % str(spl[1])

            if self.primary_api_query is None:
                # station is a city name or postal code?
                geo = self.get_geocoding(station)
                if geo is not None:
                    self.primary_api_query = '?lat=%s&lon=%s' % (geo.get('latitude'), geo.get('longitude'))
        else:
            self.primary_api_query = '?lat=%s&lon=%s' % (brightsky_dict.get('latitude'), brightsky_dict.get('longitude'))

        if self.primary_api_query is None:
            raise weewx.ViolatedPrecondition("thread '%s': Configured station or latitude/longitude not valid." % self.name)

        for opsapi, obsweewx in self.current_obs.items():
            obs = obsweewx[0]
            group = obsweewx[2]
            if group is not None:
                weewx.units.obs_group_dict.setdefault(obs, group)
                weewx.units.obs_group_dict.setdefault(self.prefix + obs[0].upper() + obs[1:], group)

        for opsapi, obsweewx in self.sources_obs.items():
            obs = obsweewx[0]
            group = obsweewx[2]
            if group is not None:
                weewx.units.obs_group_dict.setdefault(obs, group)
                weewx.units.obs_group_dict.setdefault(self.prefix + obs[0].upper() + obs[1:], group)

    def get_data(self):
        """ get buffered data """
        try:
            self.lock.acquire()
            """
            try:
                last_ts = self.data[-1]['time']
                interval = last_ts - self.last_get_ts
                self.last_get_ts = last_ts
            except (LookupError,TypeError,ValueError,ArithmeticError):
                interval = None
            """
            interval = 1
            data = self.data
            # print('POI',data)
        finally:
            self.lock.release()
        # loginf("get_data interval %s data %s" % (interval,data))
        return data, interval

    def get_conditions(self, icon):
        """ convert API icon to internal icons with weather description
            returns: (german_text,english_text,'','',belchertown_icon,dwd_icon,aeris_icon)
        """
        try:
            x = BRIGHTSKYthread.CONDITIONS[icon]
        except (LookupError, TypeError) as e:
            x = ('unbekannte Wetterbedingungen', 'unknown conditions', '', '', 'unknown.png', 'unknown.png', 'unknown')
            if self.log_failure or self.debug > 0:
                logerr("thread '%s': icon=%s mapping %s - %s" % (self.name, icon, e.__class__.__name__, e))
        return x

    def getRecord(self):
        """ download and process Brightsky API weather data """

        baseurl = 'https://api.brightsky.dev//current_weather'

        # primary api query
        params = self.primary_api_query

        # Timezone in which record timestamps will be presented, as tz database name, e.g. Europe/Berlin.
        # Will also be used as timezone when parsing date and last_date, unless these have explicit UTC offsets.
        # If omitted but date has an explicit UTC offset, that offset will be used as timezone.
        # Otherwise will default to UTC.
        params += '&timezone=Europe%2FBerlin'

        # Physical units in which meteorological parameters will be returned. Set to si to use SI units.
        # The default dwd option uses a set of units that is more common in meteorological applications and civil use:
        #                       DWD     SI
        # Cloud cover           %       %
        # Dew point             °C      K
        # Precipitation         mm      kg/m²
        # Pressure              hPa     Pa
        # Relative humidity     %       %
        # Sunshine              min     s
        # Temperature           °C      K
        # Visibility            m       m
        # Wind direction        °       °
        # Wind speed            km/h    m/s
        # Wind gust direction   °       °
        # Wind gust speed       km/h    m/s
        params += '&units=dwd'

        url = baseurl + params

        if self.debug >= 2:
            logdbg("thread '%s': Brightsky URL=%s" % (self.name, url))

        apidata = {}
        try:
            reply = wget(url,
                         log_success=(self.log_success or self.debug > 0),
                         log_failure=(self.log_failure or self.debug > 0))
            if reply is not None:
                apidata = json.loads(reply.decode('utf-8'))
            else:
                if self.log_failure or self.debug > 0:
                    logerr("thread '%s': Brightsky returns None data." % self.name)
                return
        except Exception as e:
            if self.log_failure or self.debug > 0:
                logerr("thread '%s': Brightsky %s - %s" % (self.name, e.__class__.__name__, e))
            return

        # get and check results
        weather = apidata.get('weather')
        if weather is None:
            if self.log_failure or self.debug > 0:
                logerr("thread '%s': Brightsky returns no weather data." % self.name)
            return

        sources = apidata.get('sources')
        if sources is None:
            if self.log_failure or self.debug > 0:
                logerr("thread '%s': Brightsky returns no sources data." % self.name)
            return

        # holds the return values
        x = []
        y = dict()

        if self.debug >= 4:
            logdbg("thread '%s': API result: %s" % (self.name, str(apidata)))

        y['interval'] = (60,'minute','group_interval')

        # get current weather data
        for obsapi, obsweewx in self.current_obs.items():
            obsname = self.prefix+obsweewx[0][0].upper()+obsweewx[0][1:]
            obsval = weather.get(obsapi)
            if obsval is None:
                if self.debug >= 2:
                    logdbg("thread '%s': No value for observation '%s' - '%s'" % (self.name, str(obsapi), str(obsweewx[0])))
                continue

            if self.debug >= 3:
                logdbg("thread '%s': weewx=%s api=%s obs=%s val=%s" % (self.name, str(obsweewx[0]), str(obsapi), str(obsname), str(obsval)))

            if obsapi == 'timestamp':
                # get a datetime object from observation timestamp ISO 8601 Format
                dt = dateutil.parser.isoparse(obsval)
                # convert dt timestamp to unix timestamp
                obsval = weeutil.weeutil.to_int(dt.timestamp())
            # WeeWX value with group?
            elif obsweewx[2] is not None:
                obsval = weeutil.weeutil.to_float(obsval)
            y[obsweewx[0]] = (obsval, obsweewx[1], obsweewx[2])

        # get primary source data
        source_id = weather.get('source_id')
        if source_id is not None:
            for source in sources:
                if source.get('id') == source_id:
                    for obsapi, obsweewx in self.sources_obs.items():
                        obsname = self.prefix+obsweewx[0][0].upper()+obsweewx[0][1:]
                        obsval = source.get(obsapi)
                        if obsval is None:
                            if self.debug >= 2:
                                logdbg("thread '%s': No value for source '%s' - '%s'" % (self.name, str(obsapi), str(obsweewx[0])))
                            continue

                        if self.debug >= 3:
                            logdbg("thread '%s': weewx=%s api=%s obs=%s val=%s" % (self.name, str(obsweewx[0]), str(obsapi), str(obsname), str(obsval)))

                        # WeeWX value with group?
                        if obsweewx[2] is not None:
                            obsval = weeutil.weeutil.to_float(obsval)
                        
                        y[obsweewx[0]] = (obsval, obsweewx[1], obsweewx[2])
                    break

        # convert Brightsky condition to weather description and icon
        apiicon = weather.get('icon')
        if apiicon is None:
            # dummy
            apiicon = 'unknown'
        condition = self.get_conditions(apiicon)

        if condition is not None:
            y['icon'] = (condition[self.iconset], None, None)
            y['icontitle'] = (condition[0], None, None)

        night = is_night(y, log_success=(self.log_success or self.debug > 0),
                         log_failure=(self.log_failure or self.debug > 0))
        if night != "N/A":
            y['day'] = (0 if night else 1,'count','group_count')
        else:
            y['day'] = (None,'count','group_count')

        x.append(y)

        if self.debug > 0:
            logdbg("thread '%s': result=%s" % (self.name, str(x)))

        try:
            self.lock.acquire()
            self.data = x
        finally:
            self.lock.release()



# ============================================================================
#
# Class CurrentService
#
# ============================================================================

class CurrentService(StdService):

    def __init__(self, engine, config_dict):
        super(CurrentService,self).__init__(engine, config_dict)
        
        site_dict = weeutil.config.accumulateLeaves(config_dict.get('WeatherServices',configobj.ConfigObj()))
        self.log_success = weeutil.weeutil.to_bool(site_dict.get('log_success', True))
        self.log_failure = weeutil.weeutil.to_bool(site_dict.get('log_failure', True))
        self.debug = weeutil.weeutil.to_int(site_dict.get('debug', 0))
        if self.debug > 0:
            self.log_success = True
            self.log_failure = True

        self.threads = dict()
        
        try:
            iconset = config_dict['WeatherServices']['forecast']['icon_set']
            self.lang = config_dict['WeatherServices']['forecast']['lang']
        except LookupError:
            iconset = config_dict.get('WeatherServices',site_dict).get('forecast',site_dict).get('icon_set','belchertown').lower()
            self.lang = 'de'
        self.iconset = 4
        if iconset=='dwd': self.iconset = 5
        if iconset=='aeris': self.iconset = 6
        
        site_dict = config_dict.get('WeatherServices',configobj.ConfigObj()).get('current',configobj.ConfigObj())
        for section in site_dict.sections:
            station_dict = weeutil.config.accumulateLeaves(site_dict[section])

            # section enabled?
            if not weeutil.weeutil.to_bool(station_dict.get('enable',True)):
                if self.log_success or self.debug > 0:
                    loginf("Section '%s' is not enabled. Skip section." % section)
                continue

            # Check required provider
            provider = station_dict.get('provider')
            if provider: provider = provider.lower()
            if provider not in ('dwd', 'zamg', 'open-meteo', 'brightsky'):
                if self.log_failure or self.debug > 0:
                    logerr("Section '%s' - weather service provider is not valid. Skip section." % section)
                continue

            # Check required model
            model = station_dict.get('model')
            if model: model = model.lower()
            if provider == 'dwd':
                if model not in ('cdc', 'poi'):
                    if self.log_failure or self.debug > 0:
                        logerr("Section '%s' weather service provider '%s' - model is not valid. Skip section." % (section, provider))
                    continue
            elif provider == 'open-meteo':
                if model not in OPENMETEOthread.WEATHERMODELS:
                    if self.log_failure or self.debug > 0:
                        logerr("Section '%s' weather service provider '%s' - model is not valid. Skip section." % (section, provider))
                    continue

            # check required station 
            station = station_dict.get('station')
            if (provider == 'dwd' or provider == 'ZAMG') and station is None:
                if self.log_failure or self.debug > 0:
                    logerr("Section '%s' weather service provider '%s' - station is not valid. Skip section." % (section, provider))
                continue

            # Icon set 
            iconset = station_dict.get('icon_set', iconset)
            if iconset is not None:
                station_dict['iconset'] = self.iconset
                if iconset=='belchertown': station_dict['iconset'] = 4
                if iconset=='dwd': station_dict['iconset'] = 5
                if iconset=='aeris': station_dict['iconset'] = 6

            # set default station if not selected
            if station is None:
                station = 'thisStation'

            # possible station coordinates
            altitude = station_dict.get('altitude')
            if altitude is not None:
                altitude_t = weeutil.weeutil.option_as_list(altitude)
                if len(altitude_t) >= 2:
                    altitude_t[1] = altitude_t[1].lower()
                    if altitude_t[1] in ('meter', 'foot'):
                        altitude_vt = weewx.units.ValueTuple(weeutil.weeutil.to_float(altitude_t[0]), altitude_t[1], "group_altitude")
                        station_dict['altitude'] = weewx.units.convert(altitude_vt, 'meter')[0]
                    else:
                        station_dict['altitude'] = None
                        if self.log_failure or self.debug > 0:
                            logerr("Configured unit '%s' for altitude in section '%s' is not valid, altitude will be ignored." % (altitude_t[1], section))
                else:
                    station_dict['altitude'] = None
                    if self.log_failure or self.debug > 0:
                        logerr("Configured altitude '%s' in section '%s' is not valid, altitude will be ignored." % (altitude, section))

            if station.lower() in ('thisstation', 'here'):
                if station_dict.get('latitude') is None or station_dict.get('longitude') is None:
                    station_dict['latitude'] = station_dict.get('latitude', engine.stn_info.latitude_f)
                    station_dict['longitude'] = station_dict.get('longitude', engine.stn_info.longitude_f)
                if station_dict.get('altitude') is None:
                    station_dict['altitude'] = weewx.units.convert(engine.stn_info.altitude_vt, 'meter')[0]

            if provider == 'dwd':
                if model == 'poi':
                    self._create_poi_thread(section, station_dict)
                elif model == 'cdc':
                    self._create_cdc_thread(section, station_dict)
            elif provider == 'zamg':
                self._create_zamg_thread(section, station_dict)
            elif provider == 'open-meteo':
                # TODO remove 'test' in stable release?
                if model == 'test':
                    prefix = station_dict.get('prefix', '')
                    for ommodel in OPENMETEOthread.WEATHERMODELS:
                        modlocation = section + "-" + ommodel.upper()
                        station_dict['model'] = ommodel
                        station_dict['prefix'] = prefix + '-' + ommodel
                        self._create_openmeteo_thread(modlocation, station_dict)
                else:
                    self._create_openmeteo_thread(section, station_dict)
            elif provider == 'brightsky':
                self._create_brightsky_thread(section, station_dict)
            elif self.log_failure or self.debug > 0:
                logerr("Unknown weather service provider '%s' in section '%s'" % (provider, section))

        if  __name__!='__main__':
            self.bind(weewx.NEW_LOOP_PACKET, self.new_loop_packet)
            self.bind(weewx.NEW_ARCHIVE_RECORD, self.new_archive_record)


    def _create_poi_thread(self, thread_name, station_dict):
        prefix = station_dict.get('prefix','id'+thread_name)
        self.threads[thread_name] = dict()
        self.threads[thread_name]['datasource'] = 'POI'
        self.threads[thread_name]['prefix'] = prefix
        self.threads[thread_name]['thread'] = DWDPOIthread(thread_name,
                    station_dict,
                    log_success=weeutil.weeutil.to_bool(station_dict.get('log_success',self.log_success)) or self.verbose,
                    log_failure=weeutil.weeutil.to_bool(station_dict.get('log_failure',self.log_failure)) or self.verbose)
        self.threads[thread_name]['thread'].start()
    
    
    def _create_cdc_thread(self, thread_name, station_dict):
        prefix = station_dict.get('prefix','id'+thread_name)
        self.threads[thread_name] = dict()
        self.threads[thread_name]['datasource'] = 'CDC'
        self.threads[thread_name]['prefix'] = prefix
        self.threads[thread_name]['thread'] = DWDCDCthread(thread_name,
                    station_dict,
                    log_success=weeutil.weeutil.to_bool(station_dict.get('log_success',self.log_success)) or self.verbose,
                    log_failure=weeutil.weeutil.to_bool(station_dict.get('log_failure',self.log_failure)) or self.verbose)
        self.threads[thread_name]['thread'].start()
    
    
    def _create_zamg_thread(self, thread_name, station_dict):
        prefix = station_dict.get('prefix','id'+thread_name)
        self.threads[thread_name] = dict()
        self.threads[thread_name]['datasource'] = 'ZAMG'
        self.threads[thread_name]['prefix'] = prefix
        self.threads[thread_name]['thread'] = ZAMGthread(thread_name,
                    station_dict,
                    log_success=weeutil.weeutil.to_bool(station_dict.get('log_success',self.log_success)) or self.verbose,
                    log_failure=weeutil.weeutil.to_bool(station_dict.get('log_failure',self.log_failure)) or self.verbose)
        self.threads[thread_name]['thread'].start()
    
    
    def _create_openmeteo_thread(self, thread_name, station_dict):
        prefix = station_dict.get('prefix','id'+thread_name)
        self.threads[thread_name] = dict()
        self.threads[thread_name]['datasource'] = 'OPENMETEO'
        self.threads[thread_name]['prefix'] = prefix
        self.threads[thread_name]['thread'] = OPENMETEOthread(thread_name,
                    station_dict,
                    log_success=weeutil.weeutil.to_bool(station_dict.get('log_success',self.log_success)) or self.verbose,
                    log_failure=weeutil.weeutil.to_bool(station_dict.get('log_failure',self.log_failure)) or self.verbose)
        self.threads[thread_name]['thread'].start()
    
    def _create_brightsky_thread(self, thread_name, station_dict):
        prefix = station_dict.get('prefix','id'+thread_name)
        self.threads[thread_name] = dict()
        self.threads[thread_name]['datasource'] = 'BRIGHTSKY'
        self.threads[thread_name]['prefix'] = prefix
        self.threads[thread_name]['thread'] = BRIGHTSKYthread(thread_name,
                    station_dict,
                    log_success=weeutil.weeutil.to_bool(station_dict.get('log_success',self.log_success)) or self.verbose,
                    log_failure=weeutil.weeutil.to_bool(station_dict.get('log_failure',self.log_failure)) or self.verbose)
        self.threads[thread_name]['thread'].start()

    def shutDown(self):
        """ shutdown threads """
        for ii in self.threads:
            try:
                self.threads[ii]['thread'].shutDown()
            except Exception:
                pass


    def new_loop_packet(self, event):
        for thread_name in self.threads:
            pass
            
    
    def new_archive_record(self, event):
        for thread_name in self.threads:
            # get collected data
            data = None
            datasource = self.threads[thread_name]['datasource']
            if datasource=='POI':
                data,interval = self.threads[thread_name]['thread'].get_data()
                if data: data = data[0]
            elif datasource=='CDC':
                data,interval,maxtime = self.threads[thread_name]['thread'].get_data()
                if data: data = data[maxtime]
            elif datasource=='ZAMG':
                data,interval = self.threads[thread_name]['thread'].get_data()
            elif datasource=='OPENMETEO':
                data,interval = self.threads[thread_name]['thread'].get_data()
                if data: data = data[0]
            elif datasource=='BRIGHTSKY':
                data,interval = self.threads[thread_name]['thread'].get_data()
                if data: data = data[0]
            if data:
                x = self._to_weewx(thread_name,data,event.record['usUnits'])
                event.record.update(x)


    def _to_weewx(self, thread_name, reply, usUnits):
        prefix = self.threads[thread_name]['prefix']
        data = dict()
        for key in reply:
            #print('*',key)
            if key in ('interval','count','sysStatus'):
                pass
            elif key in ('interval','count'):
                data[key] = reply[key]
            else:
                try:
                    val = reply[key]
                    # first convert val to standard unit in METRIC unit system
                    val = weewx.units.convertStd(val, weewx.METRIC)
                    # now convert val to archive record unit system
                    val = weewx.units.convertStd(val, usUnits)[0]
                except (TypeError,ValueError,LookupError,ArithmeticError) as e:
                    try:
                        val = reply[key][0]
                    except LookupError:
                        val = None
                data[prefix+key[0].upper()+key[1:]] = val
        return data


# ============================================================================
#
# __main__
#
# ============================================================================

if __name__ == '__main__':

    conf_dict = configobj.ConfigObj("DWD.conf")

    class Engine(object):
        class stn_info(object): 
            latitude_f = conf_dict['Station']['latitude']
            longitude_f = conf_dict['Station']['longitude']
            altitude_vt = (100.0,'meter','group_altitude') 
            location = 'Testlocation'
    engine = Engine()
    
    if False:

        t = DWDPOIthread('POI',conf_dict,log_success=True,log_failure=True)
        t.start()

        try:
            while True:
                x = t.get_data()
                print(x)
                time.sleep(10)
        except (Exception,KeyboardInterrupt):
            pass

        print('xxxxxxxxxxxxx')
        t.shutDown()
        print('+++++++++++++')

    else:
    
        sv = CurrentService(engine,conf_dict)
        
        try:
            while True:
                #event = weewx.Event(weewx.NEW_LOOP_PACKET)
                #event.packet = {'usUnits':weewx.METRIC}
                #sv.new_loop_packet(event)
                #if len(event.packet)>1:
                #    print(event.packet)
                event = weewx.Event(weewx.NEW_ARCHIVE_RECORD)
                event.record = {'usUnits':weewx.METRIC}
                sv.new_archive_record(event)
                if len(event.record)>1:
                    print(event.record)
                time.sleep(10)
        except Exception as e:
            print('**MAIN**',e)
        except KeyboardInterrupt:
            print()
            print('**MAIN** CTRL-C pressed')

        sv.shutDown()
