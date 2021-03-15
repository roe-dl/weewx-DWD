# weewx-DWD
Daten vom Deutschen Wetterdienst (DWD) herunterladen und für WeeWX aufbereiten

# Text-Vorhersage im HTML-Template

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

# Wetterwarnungen im HTML-Template

"DL" durch den jeweiligen Gebietscode ersetzen wie in `/usr/local/bin/dwd-warnings` definiert.

```
  <div class="col-sm-6">
    <p style="font-size:110%">Wetterwarnungen</p>
    #include raw "dwd/warn-DL.inc"
  </div>

```
