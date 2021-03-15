# weewx-DWD
Daten vom Deutschen Wetterdienst (DWD) herunterladen und für WeeWX aufbereiten

Achtung! Diese Dateien sind noch sehr beta!

# Installation

Alle Dateien müssen in die jeweiligen Verzeichnisse kopiert und mit `chmod +x Dateiname` ausführbar gemacht werden.

Die Icons (Symbole) können beim DWD unter [Warnicons](https://www.dwd.de/DE/wetter/warnungen_aktuell/objekt_einbindung/icons/warnicons_nach_stufen_50x50_zip.zip?__blob=publicationFile&v=2) heruntergeladen werden.

# Programme

## wget-dwd

Dieses Script lädt die nötigen Dateien vom Webserver des DWD herunter und speichert sie. Dabei wird eine Log-Datei unter /var/log/ abgelegt, aus der man ersehen kann, ob es geklappt hat.

## dwd-warnings

Dieses Python-Script bereitet die JSONP-Datei des DWD mit den Wetterwarnungen auf und erzeugt daraus HTML-Texte. Am Beginn der Datei müssen die gewünschten Landkreise in der vom DWD benutzten Schreibweise eingetragen werden. Um herauszufinden, wie der Landkreis korrekt geschrieben werden muß, öffnet man die Datei `warnings.json`, die von `wget-dwd` heruntergeladen wurde, mit einem Browser, der JSON-Dateien anzeigen kann (z.B. Firefox). Dort kann man dann den gewünschten Landkreis suchen und sehen, wie er geschrieben wurde. Beachte: Wenn der Landkreis keine Warnungen hat, kommt er in der Datei gar nicht vor. Dann muß man warten, bis es wieder Warnungen gibt.

## /etc/cron.hourly/dwd

Dieses Script sorgt dafür, daß die beiden Scripte `wget-dwd` und `dwd-warnings` regelmäßig aufgerufen werden.

# Bundesländer

Der Deutsche Wetterdienst (DWD) hält sich nicht an die genormten Abkürzungen der Bundesländer, sondern kocht sein eigenes Süppchen, und das noch nicht einmal einheitlich.

ISO3166-2 | Bundesland             | DWD-JSONP | Warnlage | VHDL |
----------|------------------------|-----------|----------|------|
SN        | Sachsen                | SN        | sac      | DWLG |
ST        | Sachsen-Anhalt         | SA        | saa      |      |
TH        | Thüringen              | TH        | thu      |      |
BB        | Brandenburg            | BB        | bb       |      |
BE        | Berlin                 |           | bb       |      |
MV        | Mecklenburg-Vorpommern | MV        | mv       |      |
NI        | Niedersachsen          | NS        | nds      |      |

# Konfiguration

## Text-Vorhersage im HTML-Template

```
  <div class="col-sm-12" style="margin-bottom:1em">
    #if os.path.exists("dwd/VHDL50_DWLG_LATEST.html")
    #include raw "dwd/VHDL50_DWLG_LATEST.html"
    #end if
    [Quelle:
    <a
    href="https://www.dwd.de/DE/wetter/wetterundklima_vorort/sachsen/sac_node.html"
    target="_blank">DWD</a>]
  </div>
```

## Wetterwarnungen im HTML-Template

"DL" durch den jeweiligen Gebietscode ersetzen wie in `/usr/local/bin/dwd-warnings` definiert.

```
  <div class="col-sm-6">
    <p style="font-size:110%">Wetterwarnungen</p>
    #include raw "dwd/warn-DL.inc"
  </div>

```
