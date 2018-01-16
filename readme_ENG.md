# FIVETEMP
It is my first (real) repository here on github - let's see, how it works ;-)  
The code currently works in a test without any problems. There are some minor issues in the code itself (e.g. the header for the csv is not entirely correct because I forgot to insert the column name for CPU) but that does't matter for now. Furthermore, there are still some fragments of older code which I haven't removed yet. Update will follow.
#### What does FIVETEMP roughly?
Reading five temperature sensors (DS18B20) and the CPU-temperature on a Raspberry-Pi and store the data in a csv-file.  
#### What does FIVETEMP in detail?  
still to be translated (I am tired now...)

Es werden 5 Stück digitale Temperatursensoren (DS18B20) zyklisch ausgelesen.  
Ein Plausibilitätscheck prüft grob die ausgelesenen Werte.   
Zusätzlich wird die aktuelle CPU-Temperatur ausgelesen.  
Das wird gemacht, bis eine vorgegebene Zeit (Loopzeit) beendet ist.  
Nach Ende der Loopzeit werden die gemessenen Werte pro Sensor gemittelt.  
Die gemittelten Temperaturdaten werden in eine LOG-Datei (CSV-Format) geschrieben.  
Davor werden weitere Tabellenfelder mit Zeit- und Zählerdaten gefüllt, und zwar:  
#### Spalten CSV-Datei:
Spalte 1: Unix-Zeit in [s]  
Spalte 2: Zeitstempel [JJJJMMTTHHMMSS]  
Spalte 3: Laufzeit seit Start in [h]  
Spalte 4: fortlaufende Nummerierung von 1 bis n  
Spalte 5: Anzahl der Messungen pro Sensor innerhalb Loopzeit  
Spalte 6: CPU-Temperatur in [°C]  
Spalte 7-11: T01-T05 in [°C]  
