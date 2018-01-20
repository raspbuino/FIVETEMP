#!/usr/bin/python3
#FIVETEMP
#Temperaturmessungen 5 Stück + CPU-Temperatur, LOG-Dateien schreiben

#Version:   FIVETEMP-v02d.py
#Datum:     20.JAN.2018
#Author:    Dr. Mirko Schelp
#alias:     raspbuino
#===========================================================================
#Sicher nicht alles im Code ist allein von mir.
#Ich weiß aber nicht mehr, woher genau die einzelnen Schnipsel stammen.
#Danke an alle, die ihr Wissen und Können veröffentlichen!
#Nachmachen - Lernen - Selber machen und eigene Ideen entwickeln.
#===========================================================================

#Was macht das Programm?
# Es werden 5 Stück digitale Temperatursensoren (DS18B20) zyklisch ausgelesen.
# Ein Plausibilitätscheck prüft grob die ausgelesenen Werte.
# Zusätzlich wird die aktuelle CPU-Temperatur ausgelesen.
# Das wird gemacht, bis eine vorgegebene Zeit (Loopzeit) beendet ist.
# Nach Ende der Loopzeit werden die gemessenen Werte pro Sensor gemittelt.
# Die gemittelten Temperaturdaten werden in eine LOG-Datei (CSV-Format) geschrieben
# (Bei jedem Start wird eine neue LOG-Datei mit einer neuen Nummer angelegt).
# Dabei werden weitere Tabellenfelder mit Zeit- und Zählerdaten gefüllt, und zwar:
# Spalte 1: Unix-Zeit in    [s]
# Spalte 2: Zeitstempel     [JJJJMMTTHHMMSS]
# Spalte 3: Laufzeit        seit Start in [h]
# Spalte 4: Log-Nummer      fortlaufende Nummerierung von 1 bis n
# Spalte 5: Messungen       Anzahl der Messungen pro Sensor innerhalb Loopzeit
# Spalte 6: CPU-Temperatur  [°C]
# Spalte 7-11: T01-T05      [°C]

import time
import csv
import os

#Header für CSV-Tabelle----------------------------------------------------
header = ["unix-Zeit[s]", "Zeitstempel", "Laufzeit[h]", "LogNr", "Messungen"]

#Tupel mit den Bezeichnungen der einzelnen Sensorwerte DS18B20
bez_DS = (
    "T01",
    "T02",
    "T03",
    "T04",
    "T05"
    )

#erweitern des Headers um die Temperaturkanalbezeichnungen
#CPU geht zunächst extra weil der Tupel mit den DS80B20 später separat benötigt wird
header.extend("CPU")
header.extend(bez_DS)

#Pfade---------------------------------------------------------------------
#INTENSO ist hier der Name meines USB-Sticks, die Pfade sind natürlich anzupassen
pfad_LOG = "/media/pi/INTENSO/FIVETEMP-LOG/"
pfad_EVE = "/media/pi/INTENSO/FIVETEMP-EVENTS/"
pfad_CPU = "/sys/class/thermal/thermal_zone0/temp"

#Logdateien----------------------------------------------------------------
datei_LOG = "FIVETEMP-LOG-"        #für Datenlogs
datei_NUM = 1                      #fortlaufende Dateinummer, Start bei 1 zur Prüfung
datei_EVE = "FIVETEMP-EVENTS.txt"  #für Eventlogs

#Variableninitiierung------------------------------------------------------
TIMEOUT_seku = 20   #[s] Loopzeit (Dauer für wiederholte Messloops)
SLEEPER_seku = 1    #[s] Schlafzeit zwischen zwei Einzelmessungen
UTIME = 0           #für unixzeit

COUNTER_mess = 0    #Anzahl Messungen (wegen Mittelwertbildung)
COUNTER_logs = 0    #Anzahl Hauptloop (egal ob Timeout oder Zyklus)
COUNTER_zykl = 0    #Anzahl detektierter Lastspielzyklen

TEMPCPU_valu = 0    #Raspi CPU Temperatur
TEMPCPU_summ = 0    #Baspi CPU Temperatursummenwert
TEMPCPU_last = 0    #Raspi CPU Temperatur letzter gueltiger Wert

TIME_init = time.time()

#Tupel mit den Ordnern der 1W-Temperatursensoren---------------------------
#muss individuell an die vorhandenen Sensoren angepasst werden
#jeder DS18B20 hat eine global eindeutige Hex-Adresse
#meine Sensoren haben folgende Adressen
fol_1W = (
    "28-0415a4aa94ff",
    "28-0415a4cdf3ff",
    "28-0415a4d20bff",
    "28-0415a431fcff",
    "28-011592a60dff"
    )

#Anzahl Sensoren ermitteln:
AnzTsens = len(fol_1W)

#Zuordnung Adressen und Korrekturwert und ggf Kabelbeschriftung:
#28-0415a4aa94ff  Tkorr:  0 Kabel Nr. TBD
#28-0415a4cdf3ff  Tkorr:  0 Kabel Nr. TBD
#28-0415a4d20bff  Tkorr:  0 Kabel Nr. TBD
#28-0415a431fcff  Tkorr:  0 Kabel Nr. TBD
#28-011592a60dff  Tkorr:  0 Kabel Nr. TBD

#Tupel mit den Korrekturwerten der einzelnen Sensoren:
TEMPDS_korr = (0.000000, 0.000000, 0.000000, 0.000000, 0.000000)
#Liste mit den Temperaturwerten:
TEMPDS_valu = [0,0,0,0,0]
#Liste mit den Temperatursummenwerten:
TEMPDS_summ = [0,0,0,0,0]
#Liste mit den letzten (gültigen) Temperaturwerten:
TEMPDS_last = [0,0,0,0,0]

#CSV Datei im LOG-Pfad anlegen mit nächster freier Nummer----------------
#Zunächst den Namen der Datei ermitteln:
while os.path.exists(pfad_LOG + datei_LOG + str(datei_NUM) + ".csv") == True:
    datei_NUM += 1

#Gesamtpfad zusammenbauen:
pfad_GES = pfad_LOG + datei_LOG + str(datei_NUM) + ".csv"

#Zeile2 ermitteln (die Loopzeit soll in dieser Zeile mit in die CSV geschrieben werden)
Zeile2 = "Loopzeit: " + str(TIMEOUT_seku) + "s"

#drei Zeilen in die CSV schreiben (1: Pfad, 2: Zeile2, 3: Header für Wertetabelle)
with open(pfad_GES, "x") as out:
    cw = csv.writer(out)
    cw.writerow([pfad_GES])       #Zeile1
    cw.writerow([Zeile2])         #Zeile2
    cw.writerow(header)           #Zeile3

#Leerputzen der header-Liste, da nicht mehr benötigt:
header = []

#Funktionen-------------------------------------------------------------
#neuerLogeintrag => nur bei besonderen Events ein Eintrag mit Zeitstempel
def funct_Event(logtext):
    try:
        TIME_lauf = round((time.time() - TIME_init)/3600, 2)   #bisherige Laufzeit seit Start in [h]
        timestr = time.strftime("%Y%m%d%H%M%S")
        with open(pfad_EVE + datei_EVE, "a") as out:
            logstr=timestr+" [T"+str(TIME_lauf)+"][L"+str(COUNTER_logs)+"]: "+logtext
            out.write(logstr + "\n")
            print("[EVENTLOG]: ", logstr)
    except(IOError):
        print("Event-Logfile nicht gefunden...")
#-----------------------------------------------------------------------

#HAUPTPROGRAMM:

funct_Event("Programmneustart")

while True:
    TIMEOUT_start = time.time() #Zuweisung der gerade aktuellen Zählerzeit
    COUNTER_mess = 0
    COUNTER_logs += 1

    while time.time() < TIMEOUT_start + TIMEOUT_seku: #Intervall rum ohne Zyklusende?
        COUNTER_mess += 1

# Temperaturmessungen
        for i in range(0, AnzTsens): #len(fol_1W)):
            try:
                #Temperatur aus Datei einlesen
                sensor = "/sys/devices/w1_bus_master1/" + fol_1W[i] + "/w1_slave"
                file = open(sensor, "r")
                lines = file.readlines()
                file.close()
                while lines[0].strip()[-3:] != "YES":
                    print("reading T one more time...")
                    file = open(sensor, "r")
                    lines = file.readlines()
                tempdata = lines[1].find("t=")
                if tempdata != -1:
                    tempstring = lines[1].strip()[tempdata:] #+2:]
                    TEMPDS_valu[i] = float(tempstring[2:]) #noch Faktor 1000 drin
                    TEMPDS_last[i] = TEMPDS_valu[i]
                else:
                    TEMPDS_valu[i] = TEMPDS_last[i]
                    Meldung = bez_DS[i] + " außer Range..."
                    funct_Event(Meldung)
            except (IOError, ValueError):
                TEMPDS_valu[i] = TEMPDS_last[i] #nochmal den bisherigen Wert verwenden
                Meldung = "Exception (A): IOError oder ValueError"
                funct_Event(Meldung)
            TEMPDS_summ[i] = TEMPDS_summ[i] + TEMPDS_valu[i] #Messsumme bilden, so oder so

        #Printausgabe der einzel ausgelesenen Werte (noch mit Faktor 1000) auf Bildschirm
        strMessungen = "Messung" + str(COUNTER_mess) + ": "
        for i in range(0, AnzTsens):
            strMessungen = strMessungen + "  " + str(bez_DS[i]) + "=" + str(TEMPDS_valu[i])
        print(strMessungen)

#[TIMEOUT]-----------------------------------------------------------------------------------
    #CPU-Temperatur aus Datei einlesen
    file = open(pfad_CPU)
    TEMPCPU_valu = file.readline()
    file.close()
    TEMPCPU_valu = round(float(TEMPCPU_valu)/1000, 2) #zuvor war noch Faktor 1000 drin

    #Timeout (s. Whileschleife Hauptloop) fürs Datensammeln fertig
    #summierte Daten mitteln und Korrekturfaktoren berücksichtigen
    UTIME = time.time()
    timestr = time.strftime("%Y%m%d%H%M%S")
    TIME_lauf = round((UTIME - TIME_init)/3600, 6) #bisherige Laufzeit seit Start in [h]
    #DS-Einzeltemperaturen mitteln, runden und dann Korrekturfaktoren berücksichtigen
    #Ergebnis ist die Liste TEMPS_valu mit den zu loggenden Temperaturwerten
    for i in range(0, len(TEMPDS_valu)):
        TEMPDS_valu[i] = round(TEMPDS_summ[i]/COUNTER_mess/1000 + TEMPDS_korr[i], 2)

#[Log-Daten]----------------------------------------------------------------------------------------
    #zusammenstellen in eine Liste [logrow]
    #Reihenfolhe gemäß Headerdefinition
    logrow = [int(UTIME), timestr, TIME_lauf, COUNTER_logs, COUNTER_mess, TEMPCPU_valu]+TEMPDS_valu

#[LOG] CSV schreiben und ggf Bildschirmausgabe------------------------------------------------------
    try:
    #timestralles = time.strftime("%Y%m%d-%H%M%S")
    #timestrmonat = time.strftime("%Y%m")
        with open(pfad_GES, "a") as out:
            cw = csv.writer(out) #, delimiter=";", lineterminator="\n")
            cw.writerow(logrow)
            print("[LOG]: Daten ins CSV-File schreiben..........[OK]")
            #Printausgabe Bildschirm----------------------------------------------------------------
            print("Logfile     =", pfad_GES)
            print("UTIME       =", UTIME)
            print("Zeitstempel =", timestr)
            print("Laufzeit    =", TIME_lauf, "[h]")
            print("Log-Nr      =", COUNTER_logs)
            print("Messungen   =", COUNTER_mess)
            print("CPU         =", TEMPCPU_valu)
            for i in range(0, len(TEMPDS_valu)):
                #print(bez_DS[i], "=", TEMPDS_valu[i], "[°C]", " (ADDR=", fol_1W[i], ")")
                print("(ADDR=", fol_1W[i], ")", bez_DS[i], "=", TEMPDS_valu[i], "[°C]", )
            print("--------------------------------------")
    except(IOError):
        print("[LOG]: Exception...Logfile nicht gefunden.. .[NOK]")
#Die Summenwerte jetzt wieder auf Null setzen
    for i in range(0, len(TEMPDS_valu)):
        TEMPDS_summ[i] = 0
#---------------------------------------------------------------------------------------------------
