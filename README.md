# weewx-DWD
Daten vom Deutschen Wetterdienst (DWD) herunterladen und für WeeWX aufbereiten

<p align="center"><img src="Wettervorhersage-Warnungen-Fichtelberg.png" width="600px" /></p>

Diese Daten können mit den Programmen vom DWD bezogen werden:
* vorberechnete Wettervorhersagen auf Stunden-, 3-Stunden- und
  Tagesbasis
  für die nächsten 10 Tage für
  fast 6000 Orte überall auf der Welt (`dwd-mosmix`)
* Warnmeldungen für Landkreise und Orte in Deutschland
  (`dwd-warnings` und `dwd-cap-warnings`)
* Wetterkarten (`wget-dwd`)

Die Daten werden aufbereitet als:
* HTML-Dateien (`*.inc`) zum Einbinden in Skins mittels `#include`
* JSON-Dateien (`*.json`) zur maschinellen Weiterverarbeitung,
  z.B. mittels JavaScript im Browser
* `forecast.json` zur direkten Verwendung mit der Belchertown-Skin


# Melden von Fehlern

Wenn Sie Fehler melden wollen oder Hilfe benötigen, 
geben Sie bitte immer folgende Informationen mit an:
* die komplette Zeile, mit der Sie das Programm aufgerufen haben
* alles, was das Programm ausgegeben hat
* den Abschnitt `[DeutscherWetterdienst]` aus `weewx.conf`, wenn
  es den gibt
* Rufen Sie das Programm noch einmal auf und geben Sie dabei zusätzlich
  den Parameter `--verbose` an. (Nicht bei `wget-dwd`)


# Installation

Alle Dateien müssen in die jeweiligen Verzeichnisse kopiert und mit `chmod +x Dateiname` ausführbar gemacht werden.

Die Icons (Symbole) können beim DWD heruntergeladen werden:
* [Warnicons](https://www.dwd.de/DE/wetter/warnungen_aktuell/objekt_einbindung/icons/warnicons_nach_stufen_50x50_zip.zip?__blob=publicationFile&v=2) 
* [Wettericons](https://www.dwd.de/DE/wetter/warnungen_aktuell/objekt_einbindung/icons/wettericons_zip.zip?__blob=publicationFile&v=3)

# Programme

## wget-dwd

Dieses Script lädt die Wetterkarten sowie die nötigen Dateien für `dwd-warnings` vom Webserver des DWD herunter und speichert sie. Dabei wird eine Log-Datei unter /var/log/ abgelegt, aus der man ersehen kann, ob es geklappt hat.

## dwd-warnings

Dieses Python-Script bereitet die JSONP-Datei des DWD mit den Wetterwarnungen auf und erzeugt daraus HTML-Texte.
Dazu müssen die gewünschten Landkreise in der vom DWD benutzten Schreibweise
in `weewx.conf` eingetragen werden. Um herauszufinden, wie der Landkreis korrekt geschrieben werden muß, öffnet man die Datei `warnings.json`, die von `wget-dwd` heruntergeladen wurde, mit einem Browser, der JSON-Dateien anzeigen kann (z.B. Firefox). Dort kann man dann den gewünschten Landkreis suchen und sehen, wie er geschrieben wurde. Beachte: Wenn der Landkreis keine Warnungen hat, kommt er in der Datei gar nicht vor. Dann muß man warten, bis es wieder Warnungen gibt.

[Namen der Landkreise in der Schreibweise des Deutschen Wetterdienstes](https://github.com/roe-dl/weewx-DWD/wiki/Namen-der-Landkreise-in-der-Schreibweise-des-Deutschen-Wetterdienstes)

## dwd-cap-warnings

Dieses Python-Script ist eine Alternative zu `dwd-warnings`. Im Gegensatz
zu diesem wertet es die CAP-Dateien des DWD aus, die nicht nur in einer
Auflösung auf Landkreisbasis sondern auch auf Gemeindebasis verfügbar
sind. `dwd-cap-warnings` ist nicht auf einen vorherigen Aufruf von
`wget-dwd` angewiesen. Es erzeugt dieselben Dateien wie `dwd-warnings`.
Um es zu nutzen, muß der Aufruf von `dwd-warnings` in `/etc/cron.hourly/dwd`
durch `dwd-cap-warnings --weewx --resolution=city Z_CAP_C_EDZW_LATEST_PVW_STATUS_PREMIUMCELLS_COMMUNEUNION_DE.zip` ersetzt werden.

`dwd-cap-warnings` kennt die folgenden Optionen:
```
Usage: dwd-cap-warnings [options] [zip_file_name [CAP_file_name]]

  Without an option from the commands group HTML and JSON files are
  created and saved according to the configuration.

Options:
  -h, --help            show this help message and exit
  --config=CONFIG_FILE  Use configuration file CONFIG_FILE.
  --weewx               Read config from weewx.conf.
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

## dwd-mosmix

Dieses Python-Script erzeugt eine Wettervorhersage in Tabellenform und
eine JSON-Datei mit den Inhalten der Wettervorhersage.

Zur Darstellung sind folgende Ressourcen nötig:
* Wetter-Icons der [Belchertown Skin](https://obrienlabs.net/belchertownweather-com-website-theme-for-weewx/)
  oder des [DWD](https://www.dwd.de/DE/wetter/warnungen_aktuell/objekt_einbindung/piktogramm_node.html)
* Wetter-Icons von [Erik Flowers](https://erikflowers.github.io/weather-icons/)
* zusätzliche CSS-Eintragungen

`dwd-mosmix` kennt die folgenden Optionen:
```
Usage: dwd-mosmix [options] [station]

Options:
  -h, --help            show this help message and exit
  --config=CONFIG_FILE  Use configuration file CONFIG_FILE.
  --weewx               Read config from weewx.conf.
  --orientation=H,V     HTML table orientation horizontal, vertial, or both
  --icon-set=SET        icon set to use, default is 'belchertown', possible
                        values are 'dwd', 'belchertown', and 'aeris'
  --lang=ISO639         Forecast language. Default 'de'
  --aqi-source=PROVIDER Provider for Belchertown AQI section
  --hide-placemark      No placemark caption over forecast table

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

  Intervals:
    --all               Output all details in HTML
    --hourly            output hourly forecast
    --daily             output daily forecast (the default)
```

Es können mehrere der unter "Commands" aufgeführten Optionen gleichzeitig
benutzt werden. 

Der DWD bietet eine Liste der 
[Stationscodes](https://www.dwd.de/DE/leistungen/met_verfahren_mosmix/mosmix_stationskatalog.cfg?view=nasPublication&nn=16102)
zum Herunterladen an.
Nur für die dort aufgeführten Orte sind Vorhersagen beim DWD
verfügbar. Als Code ist der Wert aus der Spalte "id" zu
verwenden. 

Die HTML-Datei enthält, wenn nicht anders konfiguriert, zwei Tabellen,
eine mit waagerechter Ausrichtung für PC-Bildschirme und eine in 
senkrechter Ausrichtung für Telefone. Durch die HTML-Klassenzuordnung
`hidden-xs` und `visible-xs-block` ist immer nur eine davon sichtbar.
Mit der Option `--orientation` kann aber auch eine von beiden fest
ausgewählt werden. Die möglichen Werte sind `h` oder `v` (kann auch
ausgeschrieben werden).

Die Option `--icon-set` gibt an, für welchen Wettersymbolsatz die
Dateien erzeugt werden sollen, den der Belchertown-Skin oder den
des Deutschen Wetterdienstes.

Die Spracheinstellung betrifft nur die Wochentage, bei Englisch auch
die Tooltips der Wettersymbole. Verfügbar ist `de`, `en`, `fr`, `it`
und `cz`.

## /etc/cron.hourly/dwd

Dieses Script sorgt dafür, daß die beiden Scripte `wget-dwd` und `dwd-warnings` regelmäßig aufgerufen werden.

Der Aufruf von `dwd-warnings` kann auch durch 
```
/usr/local/bin/dwd-cap-warnings --weewx --resolution=city
``` 
bzw.
```
/usr/local/bin/dwd-cap-warnings --weewx --resolution=county
```
ersetzt werden.

Soll `dwd-mosmix` benutzt werden, muß dafür in der Datei die Zeile
```
/usr/local/bin/dwd-mosmix --weewx Station
```
hinzugefügt werden. Wenn die Vorhersage für mehrere Stationen benötigt wird, ist für jede Station ein Aufruf einzutragen.


# Warnregionen

Die Warnungen in der JSONP-Datei `warnings.json` ist nach Landkreisen gegliedert. Manche Landkreise sind dann noch weiter nach Landschaftsmerkmalen wie etwa Bergland und Tiefland unterteilt. Andere Dateien sind nach Bundesländern gegliedert. Im Wiki sind die vom Deutschen Wetterdienst verwendeten Bezeichnungen und Abkürzungen beschrieben:

* [Abkürzungen der Bundesländer](https://github.com/roe-dl/weewx-DWD/wiki/Abkürzungen-der-Bundesländer-beim-Deutschen-Wetterdienst)
* [Bezeichnungen der Warnregionen](https://github.com/roe-dl/weewx-DWD/wiki/Namen-der-Landkreise-in-der-Schreibweise-des-Deutschen-Wetterdienstes)

# Konfiguration

## Verzeichnis anlegen

Im Verzeichnis der Visualisierung (skin), wo die Meldungen des DWD 
angezeigt werden sollen, muß ein Unterverzeichnis (Ordner) `dwd` angelegt 
werden. (Es sind auch andere Namen möglich.) In das Skript `wget-dwd` 
sowie die Konfigurationsdatei `weewx.conf` (siehe unten) muß der 
komplette Pfad dieses Verzeichnisses eingetragen werden.

Beispiel:
```
cd /etc/weewx/skins/Belchertown
mkdir dwd
```

`Belchertown` im Beispiel ist durch den zutreffenden Namen zu ersetzen.

In dieses Verzeichnis speichern die Scripte die erzeugten Warn- und
Vorhersage-Dateien.

## Konfiguration in weewx.conf

Die Eintragungen in weewx.conf müssen mit der Hand vorgenommen werden. Es
gibt gegenwärtig kein Installationsprogramm dafür.

Beispiel:
```
[DeutscherWetterdienst]
    path='/etc/weewx/skins/Belchertown/dwd'
    [[warning]]
        icons='../dwd/warn_icons_50x50'
        states='Sachsen','Thüringen'
        [[[counties]]]
              'Kreis Mittelsachsen - Tiefland'='DL'
              'Stadt Leipzig'='L'
              'Stadt Jena'='J'
              'Stadt Dresden'='DD'
        [[[cities]]]
              'Stadt Döbeln'='DL'
              'Stadt Waldheim'='DL'
              'Leipzig-Mitte'='L'
              'Stadt Jena'='J'
              'Dresden-Altstadt'='DD'
    [[forecast]]
        icons='../images'
        orientation=h,v
        #show_obs_symbols = True # optional
        #show_obs_description = False # optional
        #show_placemark = True # optional
```

Der Eintrag `path` muß auf das im ersten Schritt angelegte Verzeichnis
zeigen.

Die Pfade, Bundesländer und Landkreise sind den Erfordernissen bzw.
tatsächlichen Verhältnissen entsprechend einzutragen. Die Bezeichnungen
sind der Datei warncellids.csv zu entnehmen, die beim DWD heruntergeladen
werden kann.

**Beachte**: Der Pfad bei `icons` bezieht sich auf den Web-Server. 
Er darf nicht mit `/` beginnen.

Für jeden Landkreis, für den Warnungen angezeigt werden sollen, muß
ein Eintrag unter "counties" vorhanden sein. Das Kürzel hinter dem
Gleichheitszeichen fasst die Meldungen in Dateien zusammen, für jedes
Kürzel eine. Ansonsten kann das Kürzel frei gewählt werden.

Bei Nutzung von `dwd-cap-warnings` können statt Landkreisen auch
Gemeinden ausgewählt werden, die unter "cities" einzutragen sind.
Ob die Warnungen auf Landkreis- oder Gemeindebasis angezeigt werden,
wird mit der Option `--resolution` beim Aufruf von `dwd-cap-warnings`
eingestellt. Alternativ kann die Option auch in die Konfigurationsdatei
eingetragen werden.

## Wo können die nachfolgenden Beispiele eingefügt werden?

### Belchertown-Skin

Hier ist schon vorgesehen, daß zusätzliche Abschnitte eingefügt werden.
Dazu muß einfach eine Datei unter einem der folgenden Namen erstellt
werden. Sie wird automatisch eingebunden, wenn sie existiert:
* `index_hook_after_station_info.inc`
* `index_hook_after_forecast.inc`
* `index_hook_after_snapshot.inc`
* `index_hook_after_charts.inc`

Der Name bezeichnet schon die Einfügestelle auf der Startseite.

### andere Skins

Wenn es keine solchen vorbereiteten Einfügestellen gibt, müssen die
Beispiele in eine der Dateien mit der Endung `.html.tmpl`
eingefügt werden.

## Text-Vorhersage im HTML-Template

Bitte "DWLG" im folgenden Beispiel durch die Abkürzung des gewünschten Bundeslandes aus Spalte "VHDL" ersetzen.

```
  <div class="col-sm-12" style="margin-bottom:1em">
    #if os.path.exists("dwd/VHDL50_DWLG_LATEST.html")
    #include raw "dwd/VHDL50_DWLG_LATEST.html"
    [Quelle:
    <a
    href="https://www.dwd.de/DE/wetter/wetterundklima_vorort/sachsen/sac_node.html"
    target="_blank">DWD</a>]
    #end if
  </div>
```

## Wetterwarnungen im HTML-Template

Bitte "DL" durch den jeweiligen Gebietscode ersetzen wie in `/usr/local/bin/dwd-warnings` definiert.

```
  <div class="col-sm-6">
    <p style="font-size:110%">Wetterwarnungen</p>
    #include raw "dwd/warn-DL.inc"
  </div>

```

Beispiel für eine Wetterwarnung:

<img src="Wetterwarnung-JSON.png" width="500px" />

## Wettervorhersage im HTML-Template

Bitte "P0291" durch den gewünschten Stationscode ersetzen.

```
  <div class="col-sm-8">
    <p style="font-size:110%">Wettervorhersage</p>
    #include raw "dwd/forecast-P0291.inc"
  </div>
```

Dazu muß die Stylesheet-Datei ergänzt werden, bei der Belchertown-Skin
wäre das `custom.css`:
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
```

Beispiel für eine Wettervorhersage:

<img src="MOSMIX-Vorhersage.png" width="700px"/>

## DWD-Wettervorhersage in der Belchertown-Skin

Mit der speziellen Option `--belchertown` erzeugt `dwd-mosmix` die
`forecast.json`-Datei für die Belchertown-Skin. Damit kann die
Wettervorhersage des DWD in die Belchertown-Skin integriert werden,
ohne daß Eingriffe in den Code nötig sind. Nur eine Konfigurationsoption
muß geändert werden, entweder in `skin.conf` oder im Abschnitt der
Skin in `weewx.conf`:

```
forecast_stale = 86400
```

Außerdem muß der Abschnitt des Deutschen Wetterdienstes in `weewx.conf`
ergänzt werden:

```
[DeutscherWetterdienst]
    ...
    [[Belchertown]]
        section = "Belchertown"
        warnings = DL
        forecast = P0291
        #include_advance_warnings = 0 # optional
        #aqi_source = None # optional
        #compass_lang = 'en' # optional, alternative 'de','fr','cz'
```

Der Schlüssel `section` muß den Namen des Abschnittes der Belchertown-Skin 
unter `[StdReport]` angeben. Der Schlüssel `warnings` gibt das Kürzel der 
zu verwendenden Warn-Datei aus dem Abschnitt `[[warning]]` an. 
Der Schlüssel `forecast` gibt das Kürzel der Station an, deren Vorhersage 
verwendet werden soll. 
Mit dem optionalen Schlüssel `include_advance_warnings` kann man eine Zeitspanne
in Sekunden vorgeben. Es werden dann neben den aktiven Warnungen auch
Warnungen angezeigt, die bis zu der angegebenen Zahl Sekunden in der
Zukunft aktiv werden.

Mit `aqi_source` kann man einen Provider angeben, von dem AQI-Daten
bezogen werden sollen. Momentan mögliche Werte sind `aeris` und `ubaXXXX`,
wobei XXXX durch die Nummer der Station zu ersetzen ist, deren
Werte abgerufen werden sollen.

*Beachte*: Bei Aeris ist die Anzahl der Anfragen pro Tag limitiert.
Es ist darüber hinaus ein Account nötig.

Eine Liste der Luftqualitätsmeßstationen des Umweltbundesamtes (UBA) 
erhält man mit
```
usr/local/bin/dwd-mosmix --print-uba=meta,measure
```

Beim Aufruf der Programme muß `dwd-cap-warnings` ungedingt vor `dwd-mosmix`
aufgerufen werden, sonst werden unter Umständen veraltete Warnungen 
verarbeitet.

In `/etc/cron.hourly/dwd` ist dann die folgende Zeile hinzufügen:
```
/usr/local/bin/dwd-mosmix --weewx --belchertown Stationsname
```

Soll das Programm zu Testzwecken von der Kommandozeile aufgerufen werden,
ist `sudo` nötig:
```
sudo /usr/local/bin/dwd-mosmix --weewx --belchertown Stationsname
```

## Wetterkarte im HTML-Template

Der Pfad, hier `dwd`, ist entsprechend der eigenen Konfiguration anzupassen. Das Anhängsel mit `getmtime` ist notwendig, damit der Browser keine veralteten Karten anzeigt. Damit wird der Cache beim Nutzer überlistet.

```
  <div class="col-sm-12 snapshot-records-text">
    Wetterkarte (Luftdruck am Boden)
  </div>
  
  <div class="col-sm-12">
    <img src="$relative_url/dwd/bwk_bodendruck_na_ana.png?v=<%=os.path.getmtime("/etc/weewx/skins/Belchertown-de/dwd/bwk_bodendruck_na_ana.png")%>" />
  </div>
```

Damit die Wetterkarte auch mit auf den Server hochgeladen wird, muß sie in `skin.conf` ergänzt werden:

```
[CopyGenerator]
    ...
    copy_always = ...,dwd/bwk_bodendruck_na_ana.png
```

Anstelle von `bwk_bodendruck_na_ana.png` (Europa-Nordatlantik) kann in den obigen Beispielen 
auch `bwk_bodendruck_weu_ana.png` (West-Mittel-Europa) verwendet werden. Beide Karten werden
von `wget-dwd` heruntergeladen.

# Verweise

* [WeeWX Homepage](http://weewx.com) - [WeeWX Wiki](https://github.com/weewx/weewx/wiki)
* [Seite "Homepagewetter" des Deutschen Wetterdienstes](https://www.dwd.de/DE/wetter/warnungen_aktuell/objekt_einbindung/objekteinbindung_node.html)
* [Warnicons](https://www.dwd.de/DE/wetter/warnungen_aktuell/objekt_einbindung/icons/warnicons_nach_stufen_50x50_zip.zip?__blob=publicationFile&v=2)
* [Seite "Wetter und Klima vor Ort" des Deutschen Wetterdienstes mit Unterseiten für die Bundesländer](https://www.dwd.de/DE/wetter/wetterundklima_vorort/_node.html)
* [Seite "Warnlagebericht" des Deutschen Wetterdienstes mit Unterseiten für die Bundesländer](https://www.dwd.de/DE/wetter/warnungen_aktuell/warnlagebericht/warnlagebericht_node.html)
* [gesprochene Wetterberichte mit Python](https://beltoforion.de/de/wetterbericht/)
