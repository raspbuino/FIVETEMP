# FIVETEMP
Es ist mein erstes kleines Projekt hier auf Github. Schau mer mal, wie das funktioniert ;-)  
Der Code (in Python3) lief aktuell in einem Test ohne Probleme.
#### Was macht das Programm grob?
Es liest fünf digitale Temperatursensoren (DS18B20) und die CPU-Temperatur an einem Raspberry-Pi aus und speichert die Daten in einer CSV-Datei.  
#### Was macht das Programm im Detail?
Es werden 5 Stück digitale Temperatursensoren (DS18B20) zyklisch ausgelesen.  
Ein Plausibilitätscheck prüft grob die ausgelesenen Werte.  
Zusätzlich wird die aktuelle CPU-Temperatur ausgelesen.  
Das wird gemacht, bis eine vorgegebene Zeit (Loopzeit) beendet ist.  
Nach Ende der Loopzeit werden die gemessenen Werte pro Sensor gemittelt.  
Die gemittelten Temperaturdaten werden in eine LOG-Datei (CSV-Format) geschrieben  
(Bei jedem Start wird eine neue LOG-Datei mit einer neuen Nummer angelegt).  
Dabei werden weitere Tabellenfelder mit Zeit- und Zählerdaten gefüllt, und zwar:
#### Spalten CSV-Datei:
Spalte 1: Unix-Zeit in    [s]  
Spalte 2: Zeitstempel     [JJJJMMTTHHMMSS]  
Spalte 3: Laufzeit        seit Start in [h]  
Spalte 4: Log-Nummer      fortlaufende Nummerierung von 1 bis n  
Spalte 5: Messungen       Anzahl der Messungen pro Sensor innerhalb Loopzeit  
Spalte 6: CPU-Temperatur  [°C]  
Spalte 7-11: T01-T05      [°C]  
