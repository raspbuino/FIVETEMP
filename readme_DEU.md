# FIVETEMP
Es ist mein erstes kleines Projekt hier auf Github. Schau mer mal, wie das funktioniert ;-)  
Der Code läuft aktuell in einem Test ohne Probleme. Es gibt noch ein paar Kleinigkeiten aber diese sind nicht weiter tragisch  
(z.B. sind die Spaltenbeschriftungen nicht ganz korrekt, weil ich die Beschriftung für CPU vergessen habe)  
Ausserdem sind noch ein paar Codefragmente aus einem anderen Programm drin, die ich noch entfernen muss. Update folgt.
#### was macht das Programm grob?
liest fünf digitale Temperatursensoren (DS18B20) und die CPU-Temperatur an einem Raspberry-Pi aus und speichert die Daten in einer CSV-Datei  
#### Was macht das Programm im Detail?  
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
