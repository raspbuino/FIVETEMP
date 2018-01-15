# FIVETEMP
reading five temperature sensors (DS18B20) with a raspberry-pi and store the data in a csv-file.

It is my first (real) repository here on github - let's see, how it works ;-)

The code currently works in a test. There are some minor issues in the code (e.g. the header for the csv is not entirely correct but that does't matter for now).

[GERMAN]
#was macht das Programm?
# Es werden 5 Stück digitale Temperatursensoren (DS18B20) zyklisch ausgelesen.
# Ein Plausibilitätscheck prüft grob die ausgelesenen Werte. 
# Zusätzlich wird die aktuelle CPU-Temperatur ausgelesen.
# Das wird gemacht, bis eine vorgegebene Zeit (Loopzeit) beendet ist.
# Nach Ende der Loopzeit werden die gemessenen Werte pro Sensor gemittelt.
# Die gemittelten Temperaturdaten werden in eine LOG-Datei (CSV-Format) geschrieben.
# Davor werden weitere Tabellenfelder mit Zeit- und Zählerdaten gefüllt, und zwar:
# Spalte 1: Unix-Zeit in    [s]
# Spalte 2: Zeitstempel     [JJJJMMTTHHMMSS]
# Spalte 3: Laufzeit        seit Start in [h]
# Spalte 4: Log-Nummer      fortlaufende Nummerierung von 1 bis n
# Spalte 5: Messungen       Anzahl der Messungen pro Sensor innerhalb Loopzeit
# Spalte 6: CPU-Temperatur  [°C]
# Spalte 7-11: T01-T05		[°C]
