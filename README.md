# weewx-DWD

[deutsche Version](https://github.com/roe-dl/weewx-DWD/blob/master/README-de.md)

display weather icons in WeeWX as well as
download weather and warning data and use them in WeeWX and skins.

<p align="center"><img src="Wettervorhersage-Warnungen-Fichtelberg.png" width="600px" /></p>

Independent of certain weather services you can display weather
icons and symbols in skins by using the searchlist extension
`$presentweather`, provided by this WeeWX extension.

With this extension you can receive and process the following data:
* from **OGC OWS servers** of several weather services like NOAA, DWD, KNMI, etc.

  See [Query Open Geospatial Consortium (OGC) Servers](https://github.com/roe-dl/weewx-DWD/wiki/Query-Open-Geospatial-Consortium-(OGC)-Servers-(English))

  * maps, satellite pictures, etc. 
* from **OpenWeather**

  See [OpenWeather wiki article](https://github.com/roe-dl/weewx-DWD/wiki/OpenWeather-(English))

  * actual calculated weather data for every point on earth
  * forecast for every point on earth (`dwd-mosmix`)
* by using the **Open-Meteo** weather API

  See [Open-Meteo wiki page](https://github.com/roe-dl/weewx-DWD/wiki/Open%E2%80%90Meteo-(English))
  for details

  * pre-calculated weather forecasts based on different weather models for
    all over the world (`dwd-mosmix`)
* from VAISALA **Xweather** (formerly AerisWeather)

  See [VAISALA Xweather (formerly Aeris) wiki page](https://github.com/roe-dl/weewx-DWD/wiki/VAISALA-Xweather-(formerly-Aeris)-(English))
  for more details and descriptions

  * actual weather data of the nearest station
  * other data they provide
* from **Meteorological Service Canada** (MSC)
  * weather alerts for counties (`msc-warnings`)
  * forecast via Open-Meteo
* from **Koninklijk Nederlands Meteorologisch Instituut** (KNMI)

  See [KNMI wiki page](https://github.com/roe-dl/weewx-DWD/wiki/Koninklijk-Nederlands-Meteorologisch-Instituut-(KNMI))
  for more details and instructions.

  * text forecasts and warnings
  * other data they provide on their open data server
  * OGC maps
* from **Finnish Meteorological Institute** (FMI)
  * [radar maps, traffic state, etc](./wiki/Query-Open-Geospatial-Consortium-(OGC)-Servers-(English)#finnish-meteorological-institute-fmi)
* from **Deutscher Wetterdienst** (DWD)

  See [DWD wiki page](https://github.com/roe-dl/weewx-DWD/wiki/Deutscher-Wetterdienst)
  for more details and instructions

  * pre-calculated weather forecasts based on hours, three-hours, and days
    for the next 10 days for about 6000 places around the world (`dwd-mosmix`)
  * weather alerts for counties and places in Germany (`dwd-warnings` and
    `dwd-cap-warnings`)
  * weather maps of Europe (`user.weatherservices.DWDservice`)
  * actual readings of the DWD weather stations in Germany
    (`user.weatherservices.DWDservice`)
  * radar images and radar readings
    (`user.weatherservices.DWDservice`, for details see
    [Niederschlagsradar](https://github.com/roe-dl/weewx-DWD/wiki/Niederschlagsradar)
    (german))
  * health related forecast
    (`user.weatherservices.DWDservice`)
* from Zentralanstalt für Meteorologie und Geodynamik (ZAMG) / **GeoSphere
  Austria**
  
  See [ZAMG wiki page](https://github.com/roe-dl/weewx-DWD/wiki/Zentralanstalt-für-Meteorologie-und-Geodynamik-(ZAMG)---GeoSphere-Austria)

  * actual readings of the ZAMG weather stations in Austria
    (`user.weatherservices.DWDservice`)
* from Bundesanstalt für Bevölkerungsschutz und Katastrophenhilfe (**BBK**)
  * homeland security alerts for counties in Germany (`bbk-warnings`)

Data will be processed to:
* HTML files (`*.inc`) to include in skins with `#include`
* JSON files (`*.json`) to automatically process 
* `forecast.json` for direct use with Belchertown skin
* observation types in WeeWX
* maps (in case of radar data)

> [!TIP]
> If you look for a skin that supports weewx-DWD directly, you may want to
> have a look at
> [Weather Data Center weewx-wdc](https://github.com/Daveiano/weewx-wdc).
> There is a detailed instruction how to configure this extension for 
> that skin in 
> [their wiki](https://github.com/Daveiano/weewx-wdc/wiki/Support-for-weewx-DWD).

For icons and symbols in SVG vector graphic format see [images](https://github.com/roe-dl/weathericons).

For NOAA NWS forecasts see [weewx-nws](https://github.com/chaunceygardiner/weewx-nws)
by John A Kline.

## Contents

* [Trouble shooting](#trouble-shooting)
* [Prerequisites](#prerequisites)
* [Installation](#installation)
* [Programs](#programs)
  * [dwd-mosmix](#dwd-mosmix)
  * [dwd-cap-warnings](#dwd-cap-warnings)
  * [bbk-warnings](#bbk-warnings)
  * [msc-warnings](#msc-warnings)
  * [wget-dwd](#wget-dwd) (DEPRECATED)
  * [dwd-warnings](#dwd-warnings) (DEPRECATED)
  * [/etc/cron.hourly/dwd](#etccronhourlydwd)
* [WeeWX service](#weewx-service)
  * [Weather services and products/weather models](#weather-services-and-products-weather-models)
  * [Activating the service in WeeWX](#activating-the-service-in-weewx)
  * [Observation types](#observation-types)
* [Searchlist extension `$presentweather`](#searchlist-extension-presentweather)
  (for displaying weather symbols and icons in skins)
* [Configuration](#configuration)
  * [Create directory](#create-directory)
  * [Configuration in `weewx.conf`](#configuration-in-weewxconf)
* [Where can you include the following examples?](#where-can-you-include-the-following-examples)
  * [Belchertown skin](#belchertown-skin)
  * [Weather Data Center (WDC) skin](#weather-data-center-wdc-skin)
  * [other skins](#other-skins)
* [Weather forecast in HTML template](#weather-forecast-in-html-template)
* [Forecast in Belchertown skin](#forecast-in-belchertown-skin)
* [weather forecast diagram](#weather-forecast-diagram)
  * [Belchertown skin](#belchertown-skin)
  * [other skins](#other-skins)
* [Weather map in HTML template](#weather-map-in-html-template)
* [Links](#links)


## Trouble shooting

If you need help, please make sure to provide:

* the complete command line used to invoke the program
* the complete output
* the sections `[WeatherServices]` and `[DeutscherWetterdienst]` if any
* Try to use the `--verbose` option to get more information

In case of performance issues please additionally read the wiki article
[V5 Performance Troubleshooting](https://github.com/weewx/weewx/wiki/v5-performance-troubleshooting)
from Tom Keffer.

## Prerequisites

You may install `GeoPy`. It is useful, but not required. 
In case you installed WeeWX by `pip` you may have to install `requests`
as well.

If you installed WeeWX by packet installation:

```shell
sudo apt-get install python3-geopy
```

If you installed WeeWX by pip installation into a virtual environment:

```shell
source ~/weewx-venv/bin/activate
pip install geopy
pip install requests
```

## Installation

1) Download the extension from Github

   ```shell
   wget -O weewx-dwd.zip https://github.com/roe-dl/weewx-DWD/archive/master.zip
   ```

2) Installation

   Installation at WeeWX up to version 4.X:

   ```shell
   sudo wee_extension --install weewx-dwd.zip
   ```

   Installation at WeeWX from version 5.0 on after WeeWX packet installation:

   ```shell
   sudo weectl extension install weewx-dwd.zip
   ```

   Installation at WeeWX from version 5.0 on after WeeWX pip installation:

   ```shell
   source ~/weewx-venv/bin/activate
   weectl extension install weewx-dwd.zip
   ```

> [!CAUTION]
> You must not use `sudo` if you installed WeeWX by `pip`.

3) Adapt configuration

   see section [Configuration](#configuration)

4) restart weewx

   for SysVinit systems:

   ```shell
   sudo /etc/init.d/weewx stop
   sudo /etc/init.d/weewx start
   ```

   for systemd systems:

   ```shell
   sudo systemctl stop weewx
   sudo systemctl start weewx
   ```


Manual installation:

Unpack the file

Copy all files in `bin/user/` 
into the extension directory of WeeWX. For WeeWX 4 that is often
`/usr/share/weewx/user`. For WeeWX 5 `/etc/weewx/bin/user` 
is common.

Copy `usr/local/bin/dwd-mosmix`, `usr/local/bin/dwd-warnings`,
`usr/local/bin/html2ent.ansi`, and `usr/local/bin/wget-dwd` to
`/usr/local/bin` and make it executable by `chmod +x file_name`.

Create the following links:
```
sudo ln -s /usr/share/weewx/user/capwarnings.py /usr/local/bin/bbk-warnings
sudo ln -s /usr/share/weewx/user/capwarnings.py /usr/local/bin/dwd-cap-warnings
sudo ln -s /usr/share/weewx/user/capwarnings.py /usr/local/bin/msc-warnings
```

If you installed WeeWX into another directory than `/usr/share/weewx`
then you have to adapt the path in the above commands.

## Programs

### dwd-mosmix

Creates weather forecasts.

You can use `dwd-mosmix` to create weather forecasts in HTML to include
them in your website, JSON files of the forecast data for further processing
by Javascript, and the `forecast.json` file of the Belchertown skin to
replace the Aeris forecast by the forecast of another weather service
provider.

Data source are at your choice the MOSMIX forecasts from the Deutscher
Wetterdienst (DWD) or the forecasts provided by Open-Meteo and based
on the weather model you chose when invoking `dwd-mosmix`. The MOSMIX
forecasts are based on both the ICON model of the DWD and the IFS
model of the EZMW, enriched by additional information.

To use `dwd-mosmix` you need:
* weather icons of the [Belchertown Skin](https://obrienlabs.net/belchertownweather-com-website-theme-for-weewx/),
  the [DWD](https://www.dwd.de/DE/wetter/warnungen_aktuell/objekt_einbindung/piktogramm_node.html)
  or [SVG icons](https://github.com/roe-dl/weathericons)
* weather icons of [Erik Flowers](https://erikflowers.github.io/weather-icons/)
* additional CSS entries (see below)

You can invoke `dwd-mosmix` using the following options:

```
Usage: dwd-mosmix [options] [station]

Options:
  -h, --help            show this help message and exit
  --config=CONFIG_FILE  Use configuration file CONFIG_FILE.
  --weewx               Read config from weewx.conf.
  --orientation=H,V     HTML table orientation horizontal, vertial, or both
  --icon-set=SET        icon set to use, default is 'belchertown', possible
                        values are 'dwd', 'belchertown', 'aeris', and 'svg'
  --lang=ISO639         Forecast language. Default 'de'
  --aqi-source=PROVIDER Provider for Belchertown AQI section
  --hide-placemark      No placemark caption over forecast table
  --hours=COUNT         amount of hours in hourly forecast, default 11
  --open-meteo=MODEL    use Open-Meteo API instead of DWD MOSMIX
  --openweather=API_KEY use OpenWeather API instead of DWD MOSMIX

  Output and logging options:
    --dry-run           Print what would happen but do not do it. Default is
                        False.
    --log-tags          Log tags while parsing the KML file.
    -v, --verbose       Verbose output

  Commands:
    --print-icons-ww    Print which icons are connected to which ww weather
                        code
    --html              Write HTML .inc file
    --json              Write JSON file
    --belchertown       Write Belchertown style forecast file
    --database          Write database file
    --print-uba=CMD     download data from UBA

  Intervals:
    --all               Output all details in HTML
    --hourly            output hourly forecast
    --daily             output daily forecast (the default)
```

You can use several options of section "Commands" at the same time.

To specifiy the location you need a station code or a set of geographic
coordinates. Geographic coordinates are to be used together with the
options `--open-meteo` and `--openweather`, station codes otherwise. See
[Wiki](https://github.com/roe-dl/weewx-DWD/wiki) for lists of
station codes.

If you do not specify otherwise the HTML file contains two tables,
one for PC usage in horizontal orientation and one for phone
usage in vertical orientation. By the CSS class `hidden-xs` 
one of them is visible at the same time only. You can restrict
the creation to one of the tables by using the `--orientation`
option. Possible values are `h` and `v`.

The option `--icon-set` specifies the weather icon set to be used.
Make sure to install the desired set to your website.

The language option influences the weekday names only, for English
and german the tool tips, too. `de` (german), `en` (English), 
`fr` (french), `it` (italian), `cz` (czech), and `pl` (polish) are 
available.

The get data by the Open-Meteo API instead of the DWD, use the 
option `--open-meteo` and specify a weather model:

--open-meteo=   | Country | Weather service          | Model
----------------|---------|--------------------------|---------------
dwd-icon        | DE      | DWD                      | ICON
gfs             | US      | NOAA                     | GFS
meteofrance     | FR      | MeteoFrance              | Arpege+Arome
ecmwf           | EU      | ECMWF                    | open IFS
jma             | JP      | JMA                      | GSM+MSM
metno           | NO      | MET Norway               | Nordic
gem             | CA      | MSC-CMC | GEM+HRDPS
ecmwf_ifs04     | EU      | ECMWF                    | IFS
metno_nordic    | NO      | MET Norway               | Nordic
icon_seamless   | DE      | DWD                      | ICON Seamless
icon_global     | DE      | DWD                      | ICON Global
icon_eu         | DE      | DWD                      | ICON EU
icon_d2         | DE      | DWD                      | ICON D2
gfs_seamless    | US      | NOAA                     | GFS Seamless
gfs_global      | US      | NOAA                     | GFS Global
gfs_hrrr        | US      | NOAA                     | GFS HRRR
gem_seamless    | CA      | MSC-CMC | GEM
gem_global      | CA      | MSC-CMC | GEM
gem_regional    | CA      | MSC-CMC | GEM
gem_hrdps_continental | CA      | MSC-CMC | GEM-HRDPS
ukmo_seamless | GB | UK Met Office | UKMO Seamless

Don't forget to observe the terms and conditions of Open-Meteo and the respective
weather service when using their data.

### dwd-cap-warnings

Downloads CAP warning alerts and creates HTML and JSON files out of them.

```
Usage: dwd-cap-warnings [options] [zip_file_name [CAP_file_name]]

  Without an option from the commands group HTML and JSON files are
  created and saved according to the configuration.

Options:
  -h, --help            show this help message and exit
  --config=CONFIG_FILE  Use configuration file CONFIG_FILE.
  --weewx               Read config from /etc/weewx/weewx.conf.
  --diff                Use diff files instead of status files.
  --resolution=VALUE    Overwrite configuration setting for resolution.
                        Possible values are 'county' and 'city'.
  --lang=ISO639         Alert language. Default 'de'

  Output and logging options:
    --dry-run           Print what would happen but do not do it. Default is
                        False.
    --log-tags          Log tags while parsing the XML file.
    -v, --verbose       Verbose output

  Commands:
    --get-warncellids   Download warn cell ids file.
    --list-ii           List defined II event codes
    --list-zip          Download and display zip file list
    --list-cap          List CAP files within a zip file. Requires zip file
                        name as argument
    --print-cap         Convert one CAP file to JSON and print the result.
                        Requires zip file name and CAP file name as arguments
```

> [!CAUTION]
> If you installed WeeWX using `pip` you must use the option `--config`
> instead of `--weewx`.

The script creates an HTML file (`*.inc`) to include in skins and a
JSON file for further processing.

### bbk-warnings

This script is to download and process warnings of Bundesamt für
Bevölkerungsschutz und Katastrophenhilfe. Warnings are county based
here. The county is specified by its ARS code, which has the last
7 characters set to `0` to indicate that it is the whole county.

[list of ARS codes of german counties](https://github.com/roe-dl/weewx-DWD/wiki/Namen-der-Landkreise-in-der-Schreibweise-des-Deutschen-Wetterdienstes)

To get country-wide warnings you can use the following marks:
* `katwarn`: "Katwarn" warnings
* `biwapp`: "Biwapp" warnings
* `mowas`: "Mowas" warnings
* `dwd`: weather related warnings only (only together with `--include-dwd`)
* `lhp`: flood warnings
* `police`: warnings of the police authorities

The script creates an HTML file (`*.inc`) to include in skins and a
JSON file for further processing.

To invoke in case of WeeWX packet installation:

```shell
bbk-warnings --weewx
```

To invoke in case of WeeWX `pip` installation or no WeeWX present:

```shell
bbk-warnings --config=/path/to/your/config_file
```

To invoke in case you cannot make files executable:

```shell
python3 /path/to/capwarnings.py --config=/path/to/your/config_file --provider=BBK
```

### msc-warnings

This script is to download and process warnings of the Canadian MSC.

To invoke in case of WeeWX packet installation:

```shell
msc-warnings --weewx
```

To invoke in case of WeeWX `pip` installation or no WeeWX present:

```shell
msc-warnings --config=/path/to/your/config_file
```

To invoke in case you cannot make files executable:

```shell
python3 /path/to/capwarnings.py --config=/path/to/your/config_file --provider=MSC
```


### wget-dwd

*DEPRECATED*

This script downloads the weather maps "Europe-North Atlantic" and
"Western and middle Europe" as well as the files needed for the
`dwd-warnings` script.

### dwd-warnings

*DEPRECATED*

Uses the `warnings.json` file downloaded by `wget-dwd` to create
county wide warnings for counties in Germany. See german version
of this readme for more details. 

This script is deprecated.

### /etc/cron.hourly/dwd

If you only use the WeeWX service and/or the searchlist extension
out of this package, you do not need this script. 

The script takes care to invoke all the scripts hourly. It should
contain:

```
#!/bin/bash
/usr/local/bin/wget-dwd 2>/dev/null
/usr/local/bin/dwd-cap-warnings --weewx --resolution=city 2>/dev/null >/dev/null
/usr/local/bin/dwd-mosmix --weewx --daily --hourly XXXXX 2>/dev/null >/dev/null
```

Replace XXXXX by the appropriate station id or geographic coordinates
and add the required options, which may include `--open-meteo` and
`--belchertown`.

If you don't want to use the configuration out of the WeeWX configuration
file `/etc/weewx/weewx.conf` you can replace `--weewx` by 
`--config=/path/to/your/config_file`.

## WeeWX service

Alongside with the standalone programs described in the previous section,
this extension provides a WeeWX service to augment the archive record
by actual data of official or governmental weather stations.

### Weather services and products/weather models

The option `provider` selects the provider to receive data from. The
option `model` specifies a weather model or product of that provider.

to put into section `[[current]]`:

* OpenWeather

  ```
            provider = OpenWeather
  ```

  OpenWeather provides calculated data for every point on earth. You have
  to specifiy the geographic coordinates of the location, you want data
  for. See 
  [OpenWeather wiki article](https://github.com/roe-dl/weewx-DWD/wiki/OpenWeather-(English))
  for details.

* DWD POI

  ```
            provider = DWD
            model = POI
  ```

  With the product name 'POI' the DWD offers hourly actualized
  readings of selected DWD weather stations together with the
  actual weather state at that place.

  [list of stations](https://github.com/roe-dl/weewx-DWD/wiki/POI-Stationen-in-Deutschland)

* DWD CDC

  ```
            provider = DWD
            model = CDC
  ```

  As CDC the DWD provides the bare readings. Different publishing
  intervals are available. Here the 10 minutes interval can only
  be used.

  [list of stations](https://opendata.dwd.de/climate_environment/CDC/help/wetter_tageswerte_Beschreibung_Stationen.txt)

* ZAMG / GeoSphere Austria

  ```
            provider = ZAMG
  ```

  The Austrian weather service ZAMG publishs weather stations readings,
  too.

  [list of stations](https://dataset.api.hub.zamg.ac.at/v1/station/current/tawes-v1-10min/metadata)

* Open-Meteo

  ```
            provider = Open-Meteo
            model = Wettermodell_laut_Liste_im_Abschnitt_dwd_mosmix
  ```

  [Open-Meteo](https://open-meteo.com/) provides an API to get 
  weather data out of different weather models of serveral big
  weather services of the world. The desired place is to be
  specified by geographic coordindates.

to put into section `[[radar]]`:

* DWD weather radar

  This is to download ground based weather radar data. See wiki article
  [Niederschlagsradar](https://github.com/roe-dl/weewx-DWD/wiki/Niederschlagsradar)
  (german) for details.

to put in section `[[forecast]]`:

* Staatsbetrieb Sachsenforst

  ```
            provider = Sachsenforst
  ```

  You need a contract to use these data. It is for free, but
  there are requirements.

* DWD text forecast

  ```
            provider = DWD
            model = text
  ```

  For the current day and the following three days the German Weather
  Service (DWD) provides text forecasts for the german federal states. 
  They are updated serveral times a day. See the abbrevations of the
  states to use for this purpose in the wiki article
  [Abkürzungen der Bundesländer beim Deutschen Wetterdienst](https://github.com/roe-dl/weewx-DWD/wiki/Abkürzungen-der-Bundesländer-beim-Deutschen-Wetterdienst)
  (german).

  Using the option `insert_lf_after_summary = true` you can insert a
  line feed between the header and the text.

* DWD health related forecast

  ```
            provider = DWD
            model = biowetter
  ```

  [list of forecast areas](https://github.com/roe-dl/weewx-DWD/wiki/Biowettervorhersage)

* DWD pollen forecast

  ```
            provider = DWD
            model = pollen
  ```

  [list of forecast areas](https://github.com/roe-dl/weewx-DWD/wiki/Pollenflugvorhersage)

* DWD UV index forecast

  This forecast is provided for selected cities and mountains only.

  ```
            provider = DWD
            model = uvi
  ```

to put into section `[[download]]`:

* DWD ground level weather map

  ```
            provider = DWD
            model = bwk-map
  ```

  weather map including barometer pressure and weather fronts.

* DWD warning map using traffic sign like symbols

  ```
            provider = DWD
            model = warning-map-with-symbols
  ```

  The area to display is specified within the `area` key. See wiki article
  [Warnstatuskarten](https://github.com/roe-dl/weewx-DWD/wiki/Warnstatuskarten)
  (german) for more details and configuration instructions.

* DWD warning map

  ```
            provider = DWD
            model = warning-map
  ```

  The area to display is specified by the key `area`. See wiki article
  [Warnstatuskarten](https://github.com/roe-dl/weewx-DWD/wiki/Warnstatuskarten)
  (german) for more details and configuration instructions.

* general download


  ```
            url = "..."
            from_encoding = "..."
            to_encoding = "..."
  ```

  You can download all files that you can get by an URL. Just in time before
  the end of the archive interval the server is asked for an update of the
  file. If there is an update, it is downloaded and safed to disk. If
  the previously downloaded version of the file is still up to date,
  nothing happens.

  `from_encoding` specifies the encoding the file is stored on the server.
  `to_encoding` specifies the encoding the file should be safed to disk
  locally. If the keys are missing, no decoding nor encoding is performed.

### Activating the service in WeeWX

To activate this service within WeeWX you need to add its name
to `weewx.conf`:


```
[Engine]
    [[Services]]
        ...
        data_services = ..., user.weatherservices.DWDservice
        ...
```

To specify the locations to get data for see section Configuration.

If you want to compare barometer readings according to the DWD rules
with your own measurements, you can have this extension calculate 
`barometerDWD` out of `pressure`, `outTemp`, and `outHumidity` by
adding the following line to `weewx.conf`:

```
[StdWXCalculate]
    [[Calculations]]
        ...
        barometerDWD = software, loop
```

### Observation types

The observation types are named like the standard observation types of
WeeWX, prepended by a prefix specified in configuration. The first
character is changed to uppercase. So if you think about the outside
temperature `outTemp` and the prefix `xyz` the resulting observation
type name will be `xyzOutTemp`.

In case you want to output this data by MQTT consider to not use
underscores as they are used to separate observation type name
and unit there. This is especially important when using the
Belchertown skin.

* always: 
  * `dateTime`: measuring timestamp
  * `interval`: measuring interval (1h for POI, 10min. for CDC)
* Sensor group `air`: 
  * `pressure`: air pressure QFE
  * `barometer`: barometer
    (bei POI im Datensatz enthalten, bei CDC berechnet,
    wenn `pressure` und `outTemp` verfügbar)
  * `barometerDWD`: barometer according to the DWD formula
    (CDC only, `pressure`, `outTemp`, and `outHumidity` 
    required to calculate)
  * `outTemp`: air temperature at 2 m above the ground 
  * `extraTemp1`: air temperature at 5 cm above the ground
  * `outHumidity`: relative humidity
  * `dewpoint`: dewpoint
* Sensor group `wind`: 
  * `windSpeed`: wind speed
  * `windDir`: wind direction
* Sensor group `gust`: 
  * `windGust`: wind gust speed
  * `windGustDir`: wind gust direction
* Sensor group `precipitation`: 
  * `rainDur`: duration of precipitation during the measuring interval
  * `rain`: amount of precipitation during the measuring interval
  * `rainIndex`: kind of precipitation
* Sensor group `solar`: 
  * `solarRad` 
  * `radiation`
  * `sunshineDur`: sunshine duration during the measuring interval
  * `LS_10`
* POI only: 
  * `cloudcover`: cloud cover in percent
  * `cloudbase`: cloud base
  * `visibility`: visibility 
  * `presentWeather`: coded weather
  * `snowDepth`: snow depth
  * `icon`: weather icon (file name)
  * `icontitle`: description 
* CDC only: 
  * `station_id`
  * `MESS_DATUM_ENDE`
  * `quality_level`
* other than POI:
  * `latitude`: latitude of the station
  * `longitude`: longitude of the station
  * `altitude': altitude of the station

`icon`, `icontitle`, `station_id` and 'MESS_DATUM_ENDE` are string values,
that require `.raw` to use them.

## Searchlist extension `$presentweather`

The weather forecast and some measuring instruments provide a code
called `ww` or `wawa` describing the present weather condition.
These codes as well as the symbols representing them on weather maps
are standardized by the WMO. When using `dwd-mosmix` the script
includes the appropriate symbols and descriptions in the forecast.
But otherwise, if the `ww` code is provided by some other source,
you can use this searchlist extension to convert `ww` and `wawa`
codes to icons and weather condition descriptions.

To use the searchlist extension within a skin, you have to extend
`skin.conf`:

```
[CheetahGenerator]
    search_list_extensions = user.weathercodes.WeatherSearchList
    ...
```

If the line `search_list_extensions` is already present, add the
value at the end of the line, separeted by a komma.

After that you can use an additional tag:

```
$presentweather(ww=$ww, n=$n, night=$night, wawa=$wawa, ...).attr
```

The parameters are:

* `ww`: the ww weather code or a list of weather codes 
* `n`: cloud cover in precent (necessary for `ww`&lt;4 only)
* `night`: `True` if the night time symbol is to be used.
* `wawa`: the wawa weather code or a list of such weather codes
* In case of `station` as value of `attr` additional parameters
  can be used to define readings to present in the station model.

All the parameters are optional. At least one of `ww`, `n`, or `wawa`
is necessary. If both `ww` and `wawa` are present, `ww` ist used and
`wawa` ignored. `n` is used if `ww` and `wawa` are `None` or less
than 4.

`attr` can be one of the following:

* `ww`: the weather code chosen from the list
* `text`: the description of the weather event 
* `belchertown_icon`: the file name of the icon from the Belchertown set
* `dwd_icon`: the file name of the icon from the DWD set
* `aeris_icon`: the file name of the icon from the Aeris set
* `wi_icon`: icon of the icon set from Erik Flowers
* `svg_icon`: weather icon in SVG format
* `svg_icon($width=128,$x=None,$y=None,$with_tooltip=True)`: 
  weather icon in SVG format, formatted
* `svg_icon_filename`: filename of the SVG icon from
  [weathericons](https://github.com/roe-dl/weathericons)
* `wmo_symbol`: the meteorological symbol as defined by the WMO
* `wmo_symbol($width,color=$color,None_string=None)`: the meteorological symbol as defined
  by the WMO, formatted
* `n`: cloud cover in percent (if parameter `n` is given only)
* `okta`: cloud cover in Okta (if parameter `n` is given only)
* `station`: station model as used in weather maps in SVG format

The file name are for use with the `<img>` tag. 

Example:
```
<img src="$relative_url/images/$presentweather($ww,$n,$night).belchertown_icon" />
```

In contrast, `wmo_symbol` and `svg_icon` are used directly:

```
$presentweather($ww,$n,$night).wmo_symbol(30)
```

If a color is provided, the whole symbol is displayed in that color. If no
color is provided, the symbol is displayed in original color, i.e.
multicolor.

`wi_icon` is used directly as well, for example:

```
$presentweather($ww,$n,$night).wi_icon
```

[Description of the symbols](https://www.woellsdorf-wetter.de/info/presentweather.html)

Example: Belchertown icons
fog | drizzle | rain | hail | sleet | snow | thunderstorm | wind | tornado
----|---------|------|------|-------|------|--------------|------|---------
<img src="https://www.woellsdorf-wetter.de/images/fog.png" width="50px" /> | <img src="https://www.woellsdorf-wetter.de/images/drizzle.png" width="50px" /> |<img src="https://www.woellsdorf-wetter.de/images/rain.png" width="50px" /> | <img src="https://www.woellsdorf-wetter.de/images/hail.png" width="50px" /> | <img src="https://www.woellsdorf-wetter.de/images/sleet.png" width="50px" /> | <img src="https://www.woellsdorf-wetter.de/images/snow.png" width="50px" /> | <img src="https://www.woellsdorf-wetter.de/images/thunderstorm.png" width="50px" /> | <img src="https://www.woellsdorf-wetter.de/images/wind.png" width="50px" /> | <img src="https://www.woellsdorf-wetter.de/images/tornado.png" width="50px" />

WMO symbols
WMO code table  4677 ww | WMO code table 4680 w<sub>a</sub>w<sub>a</sub>
-------------------------|---------------------------
![WMO-Code-Tabelle 4677](https://raw.githubusercontent.com/roe-dl/weathericons/master/WMO-code-table-4677-colored.png) | ![WMO-Code-Tabelle 4680](https://raw.githubusercontent.com/roe-dl/weathericons/master/WMO-code-table-4680-colored.png)

With
```
python3 /usr/share/weewx/user/weathercodes.py --write-svg target_directory
```
alle the WMO symbols can be written to the target directory in SVG format.

With
```
python3 /usr/share/weewx/user/weathercodes.py --print-ww-tab >wmo4677.inc
python3 /usr/share/weewx/user/weathercodes.py --print-wawa-tab >wmo4680.inc
```
you can create a HTML table of the symbols.

## Configuration

### Create directory

You need to create a sub-directory within the directory of the skin
you are using. 

Example:
```
cd /etc/weewx/skins/Belchertown
mkdir dwd
```

The word `Belchertown` is to be replaced by the name of your skin.

All the programs and services of this extension save their files to
that directory.

### Configuration in `weewx.conf`

Example:
```
[StdWXCalculate]
    [[Calculations]]
        ...
        barometerDWD = software, loop
...
[Engine]
    [[Services]]
        ...
        data_services = ..., user.weatherservices.DWDservice
        ...
...
[WeatherServices]
    # path to the directory to save the files there
    path='/etc/weewx/skins/Belchertown/dwd'
    # configuration to get readings of official or governmental stations
    [[current]]
        # Examples follow.
        [[[station_nr]]]
            provider = ZAMG  # DWD, ZAMG or Open-Meteo
            prefix = observation_type_prefix_for_station
            # equipment of the weather station (optional)
            observations = air,wind,gust,precipitation,solar
        [[[station_code]]]
            provider = DWD
            model = POI
            prefix = observation_type_prefix_for_station
        [[[station_id]]]
            provider = DWD
            model = CDC
            prefix = observation_type_prefix_for_station
            # equipment of the weather station (optional)
            observations = air,wind,gust,precipitation,solar
        [[[ThisStation]]]
            # actual readings out of the forecast for the location of this station
            provider = Open-Meteo
            model = dwd-icon
            prefix = observation_type_prefix
        [[[OpenWeather-Example]]]
            provider = OpenWeather
            latitude = latitude_of_the_location
            longitude = longitude_of_the_location
            station = station_name # (optional)
            lang = 'en' # language
            api_key = 'api key received from the provider'
    # configuration for dwd-mosmix
    [[forecast]]
        # location of the icons on the web server
        icons = '../images'
        # which icon set to use: belchertown, dwd, aeris
        icon_set = belchertown
        # which orientation(s) shall be created in HTML?
        orientation = h,v
        # show observation type icons in HTML
        #show_obs_symbols = True # optional
        # show observation type description in HTML
        #show_obs_description = False # optional
        # show place name above the forecast table in HTML
        #show_placemark = True # optional
    # warnings
    [[warning]]
        #icons = ... # optional
        #bbk_icons = ... # optional
        #bbk_logos = ... # optional
        #bbk_include_dwd = True|False # optional
        #dwd_icons = ... # optional
        #dwd_status_url = ... # optional
        #dwd_diff_url = ... # optional
        #dwd_resolution = county|city
        #dwd_states = 'Sachsen', 'Thüringen'
        # examples
        [[[1]]]
            provider = MSC # Canada
            office = ... # Code of the issuing office (try without if unsure)
            county = county_name
            file = target_file
        [[[145220000000]]]
            provider = BBK
            # section name is county 
            file = DL
        [[[Leipzig]]]
            provider = BBK
            county = 147130000000 
            file = L
        [[[counties]]]
            provider = DWD
            'Kreis Mittelsachsen - Tiefland'='DL'
            'Stadt Leipzig'='L'
            'Stadt Jena'='J'
            'Stadt Dresden'='DD'
        [[[cities]]]
            provider = DWD
            'Stadt Döbeln'='DL'
            'Stadt Waldheim'='DL'
            'Leipzig-Mitte'='L'
            'Stadt Jena'='J'
            'Dresden-Altstadt'='DD'
     # configuration for the --belchertown option of dwd-mosmix
     [[Belchertown]]
        # name of the section of the Belchertown skin in [StdReport]
        section = Belchertown
        # warnings file from section [[warnings]]
        warnings = DL
        # forecast file from running dwd-mosmix
        forecast = P0291
        # include warnings coming into effect in future
        #include_advance_warnings = 0 # optional
        # air quality provider (optional)
        # possible values: aeris uba{station_code}
        #aqi_source = ... 
        # compass direction language (optional)
        # possible values: de, en, fr, it, cz, es, nl, no, gr
        #compass_lang = 'en' # optional
    [[download]]
        # general download interface to download maps and forecasts and
        # other files
        [[[Download1]]]
            # what to download
            url = "https://www.example.com/pfad/datei"
            # what encoding the original file is in
            # optional
            #from_encoding = iso8859-1
            # what encoding is to used to save the file
            # optional
            #to_encoding = html_entities
            # authentication (optional)
            #auth_method = basic # or digest
            #username = replace_me
            #password = replace_me
        [[[Download2]]]
            # wather map from DWD
            provider = DWD
            model = bwk-map
        [[[Download3]]]
            # warnings map 
            provider = DWD
            model = warning-map-with-symbols
            area = LZ
        [[[Download4]]]
            # another warnings map
            provider = DWD
            model = warning-map
            area = sac
```

The key `path` has to point to the directory created before.

The paths, states, and counties are to replaced by the appropriate names.

**Note:** The key `icons` refers to the web servers. The value must not
start with `/`.

## Where can you include the following examples?

### Belchertown skin

There are special files available that are intended to be used for 
additional content. Simply create the file and fill it with what
you want to display:
* `index_hook_after_station_info.inc`
* `index_hook_after_forecast.inc`
* `index_hook_after_snapshot.inc`
* `index_hook_after_charts.inc`

The name of the file indicates the place where it is included in the
web page.

### Weather Data Center (WDC) skin

See [Support for weewx DWD](https://github.com/Daveiano/weewx-wdc/wiki/Support-for-weewx-DWD).

### other skins

Determine which include files are defined for that skin or include
the example into files with the name ending in `.html.tmpl`

## Weather forecast in HTML template

Replace `dwd/forecast-P0291.inc` by the apprpriate file name

```
  <div class="col-sm-8">
    <p style="font-size:110%">Wettervorhersage</p>
    #include raw "dwd/forecast-P0291.inc"
  </div>
```

Additionally you need to add the following to the style sheet file.
For the Belchertown skin that would be in `custom.css`
```
.dwdforecasttable {
    line-height: 1.0;
}
.dwdforecasttable td {
    text-align: center;
    padding-left: 3px;
    padding-right: 3px;
    line-height: 1.2;
}
.dwdforecasttable .icons td {
    padding-top: 5px;
    padding-bottom: 0px;
}
.dwdforecasttable .topdist td {
    padding-top: 5px;
}
.light .dwdforecasttable td.weekend {
    background-color: #ffe;
}
.dark .dwdforecasttable td.weekend {
    background-color: #333;
}
/* scrollbar for 48-hour hourly forecast */
.dwdforecast-horizontal.dwdforecast-hourly48 {
    /* prevent vertical scrollbar */
    padding: 5px;
    /* switch on horizontal scrollbar */
    overflow-x: scroll;
}
```

Example for a forecast:

<img src="MOSMIX-Vorhersage.png" width="700px"/>

The following table is intended for experienced users, who want to style
the forecast using CSS:

CSS class | Usage
----------|------
`.dwdforecasttable` | all forecast tables, set for `<table>`
`.dwdforecasttable-symbol` | table header field containing the symbol of the observation type
`.dwdforecasttable-description` | table header field containing the name of the observation type
`.dwdforecasttable-unit` | table header field containing the unit
`.dwdforecasttable-horizontal` | at the surrounding `<div>` of horizontal oriented tables
`.dwdforecasttable-vertical` | at the surrounding `<div>` of vertical oriented tables
`.weekend` | for the daily forecast at fields describing data of weekend days
`.dwdforecasttable-hourlyXX` | at the surrounding `<div>` of hourly forecasts, where `XX` is the amount of hours in the forecast

## Forecast in Belchertown skin

Using the option `--belchertown` with `dwd-mosmix` you can create the
`forecast.json` file for the Belchertown skin. No changes to the
code of the Belchertown skin is required. You only need to change
some configuration option in `skin.conf` or the `[[Belchertown]]` 
section of `[StdReport]` in `weewx.conf`.

```
    forecast_enabled = 1
    forecast_stale = 86400
    forecast_alert_enabled = 1
```

There is a separate key for the unit system to be used for the forecast
of the Belchertown skin. Set `forecast_units = si` for metric units
or `forecast_units = us` for U.S. units.

Additionally you need to add a sub-section in the `[DeutscherWetterdienst]`
section of `weewx.conf`.

```
[WeatherServices]
    ...
    # configuration for the --belchertown option of dwd-mosmix
    [[Belchertown]]
        # name of the section of the Belchertown skin in [StdReport]
        section = Belchertown
        # warnings file from section [[warnings]]
        warnings = DL
        # forecast file from running dwd-mosmix
        forecast = P0291
        # include warnings coming into effect in future
        #include_advance_warnings = 0 # optional
        # air quality provider (optional)
        # possible values: aeris ubaXXXX
        #aqi_source = ... 
        # compass direction language (optional)
        # possible values: de, en, fr, it, cz, es, nl, no, gr
        #compass_lang = 'en'
```

The key `section` has to point to the section of the Belchertown skin
in the `[StdReport]` section of `weewx.conf`. 

The key `warnings` sets the file name of a warnings file defined in
section `[[warnings]]` if any. Using the optional key 
`include_advance_warnings` you can specify a timespan in seconds.
All the warnings coming in effect within that timespan in future
will be included additionally. The default is 0.

The key `forecast` sets the id of the forecast location to be used.
In case of Open-Meteo this is `openmeteo-latitude-longitude-model`,
where 'latitude' and 'longitude' is to be replaced by the geographic 
coordinates of the location and 'model' by the weather model. In
other cases this is the station id or station code of the location.

Using the key `aqi_source` you can specify a provider air quality
data can be received from. Possible values are `aeris` or `ubaXXXX`,
where XXXX is the code of the station the readings should be used.

*Please note*: The amount of downloads from Aeris is restricted.
Additionally you nead an account with them.

A list of air quality stations of the german Umweltbundesamt (UBA)
can be acquired by
```
usr/local/bin/dwd-mosmix --print-uba=meta,measure
```

If you want to use warnings, you need to call `dwd-cap-warnings` before
`dwd-mosmix`. Otherwise outdated warnings may be processed.

## Weather forecast diagram

Using the option `--database` you can create an SQLITE database file.
It is written into the path defined by `SQLITE_ROOT` and named
`dwd-forecast-station_code.sdb`.

Generally, the values are in hourly interval.

To use that file for diagrams you need to declare it in `weewx.conf`
as follows:

```
[DataBindings]
    ...
    [[dwd_binding]]
        database = dwd_sqlite
        table_name = forecast
        manager = weewx.manager.Manager
        schema = schemas.dwd.schema
[Databases]
    ...
    [[dwd_sqlite]]
        database_name = dwd-forecast-Stationscode.sdb
        database_type = SQLite
```

Then write a file named `dwd.py` into the `schemas` directory of
WeeWX, containing the following:

```
schema = [('dateTime','INTEGER NOT NULL PRIMARY KEY'),
          ('usUnits','INTEGER NOT NULL'),
          ('interval','INTEGER NOT NULL')]
```

In `extensions.py` the missing observation types are to be defined:

```
import weewx.units
weewx.units.obs_group_dict['pop'] = 'group_percent'
weewx.units.obs_group_dict['cloudcover'] = 'group_percent'
weewx.units.obs_group_dict['sunshineDur'] = 'group_deltatime'
weewx.units.obs_group_dict['rainDur'] = 'group_deltatime'
```

Observation types in forecast:
* `outTemp`: air temperature 2m above the ground
* `dewpoint`: dewpoint 2m above the ground
* `windchill`: windchill temperature (calculated out of `outTemp`
  and `windSpeed`)
* `heatindex`: heat index (calculated out of `outTemp` and `dewpoint`)
* `outHumidity`: relative humidity ( calculated out of `outTemp` and
  `dewpoint`)
* `windDir`: wind direction
* `windSpeed`: wind speed
* `windGust`: wind gust speed
* `pop`: propability of precipitation
* `cloudcover`: cloud cover
* `barometer`: barometer
* `rain`: amount of rain during the last hour
* `rainDur`: rain duration during the last hour
* `sunshineDur`: sunshine duration during the last hour

### Belchertown skin

Example configuration within `graphs.conf`:

```
    [[forecast]]
        tooltip_date_format = "dddd LLL"
        gapsize = 3600 # 1 hour in seconds
        credits = "&copy; DWD"
        data_binding = dwd_binding
        time_length = all
        [[[outTemp]]]
        [[[dewpoint]]]
```

![Belchertown skin example](./forecast-chart-belchertown.png)

### Other skins

Example configuration within `skin.conf`:

```
[ImageGenerator]
    ...
    [[day_images]]
        ...
        [[[forecast]]]
            data_binding = dwd_binding
            line_gap_fraction = 0.04
            time_length = 950400
            x_label_format = %d.%m.
            [[[[outTemp]]]]
            [[[[dewpoint]]]]
```

![Other skin example](./forecast-chart-other.png)

## Weather map in HTML template

Please, adjust the path within the following examples to the path you
configured in `[WeatherServices]` section of `weewx.conf`.

```
  <div class="col-sm-12 snapshot-records-text">
    Wetterkarte (Luftdruck am Boden)
  </div>
  
  <div class="col-sm-12">
    <img src="$relative_url/dwd/bwk_bodendruck_na_ana.png?v=<%=os.path.getmtime("/etc/weewx/skins/Belchertown-de/dwd/bwk_bodendruck_na_ana.png")%>" />
  </div>
```

In order to make the image file uploaded to the web server, you need
to add it in `weewx.conf`:

```
[CopyGenerator]
    ...
    copy_always = ...,dwd/bwk_bodendruck_na_ana.png
```

Instead of `bwk_bodendruck_na_ana.png` (Europe-Northern Atlantics) you can
also use `bwk_bodendruck_weu_ana.png` (western and middle Europe). Both
those files are downlaoded by `wget-dwd`.

## Links

* [WeeWX Homepage](http://weewx.com) - [WeeWX Wiki](https://github.com/weewx/weewx/wiki)
* [page "Homepagewetter" from Deutscher Wetterdienst](https://www.dwd.de/DE/wetter/warnungen_aktuell/objekt_einbindung/objekteinbindung_node.html)
* [warning icons](https://www.dwd.de/DE/wetter/warnungen_aktuell/objekt_einbindung/icons/warnicons_nach_stufen_50x50_zip.zip?__blob=publicationFile&v=2)
* [DWD-MOSMIX](https://www.dwd.de/EN/ourservices/met_application_mosmix/met_application_mosmix.html;jsessionid=20DEB86AFBC29A8EA7F97358302C7EB9.live31083)
* [spoken weather forecasts with Python](https://beltoforion.de/de/wetterbericht/)
* [Open-Meteo](https://open-meteo.com/)
