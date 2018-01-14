#!/usr/bin/python3
#FIVETEMP-v01.py
#Copyright Dr. Mirko Schelp
#Temperaturmessungen 5 Stück
#Hauptprogramm
#Headerdefinition Logdatei (in der zweiten Zeile):
#A: "" leer (=> in der Zeile darüber, erste Spalte, Platz für Dateiname
#B: "" leer (Platzhalter für DatumZeitStempel)
#C: "t[h]" [TIME_lauf/3600] fortlaufende Zeit seit Programmstart in [h] mit 6 Stellen
#D: "LogNr" [COUNTER_logs] fortlaufende Lognr / Messchleifen gesamt, egal ob N(Zyklen) oder timeout(Loop)
#E: "N" [COUNTER_zykl] Lastspielzahl
#F: "Anz" [COUNTER_mess] Anzahl Messungen im geloggerten Loop oder Zyklus
#G: "TCPU" [TEMPCPU_valu] CPU-Temperatur
#H+ [gemittelte Temperaturen] in [°C], Korrekturfaktor berücksichtigt

header = ["utime", "z-stamp", "t[h]", "LogNr", "Anz"] # wird unten dann erweitert

import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM) #Bezug auf die BCM-Nummerierung der Pins (also nicht die Pin-Nummern)
import time
import csv
import os

GPIO_input = 21        #BCM 21 ist GPIO29 ist Pin40
GPIO_LED01 = 26        #BCM 26 ist GPIO25 ist Pin37 max 8mA

GPIO.setup(GPIO_LED01, GPIO.OUT)
GPIO.setup(GPIO_input, GPIO.IN)

#Pfade---------------------------------------------------------------------
pfad_LOG = "/media/pi/INTENSO/FIVETEMP-LOG/"
pfad_EVE = "/media/pi/INTENSO/FIVETEMP-EVENTS/"
pfad_CPU = "/sys/class/thermal/thermal_zone0/temp"

#Logdateien----------------------------------------------------------------
datei_LOG = "FIVETEMP-LOG-"        #für Datenlogs
datei_NUM = 1                      #fortlaufende Dateinummer, Start bei 1 zur Prüfung
datei_EVE = "FIVETEMP-EVENTS.txt"  #für Eventlogs

#Variableninitiierung------------------------------------------------------
LEDBCM1 = 4         #BCM 4 ist GPIO7 ist Pin7
TIMEOUT_seku = 20   #[s] maximal erlaubte Loopzeit (ohne Erreichen Zyklusende)
SLEEPER_seku = 1    #[s] Schlafzeit zwischen zwei Einzelmessungen
UTIME = 0          #für unixzeit

COUNTER_mess = 0    #Anzahl Messungen (wegen Mittelwertbildung)
COUNTER_logs = 0    #Anzahl Hauptloop (egal ob Timeout oder Zyklus)
COUNTER_zykl = 0    #Anzahl detektierter Lastspielzyklen

TEMPCPU_valu = 0    #Raspi CPU Temperatur
TEMPCPU_summ = 0    #Baspi CPU Temperatursummenwert
TEMPCPU_last = 0    #Raspi CPU Temperatur letzter gueltiger Wert

TIME_init = time.time()

#Tupel mit den Bezeichnungen der einzelnen Sensorwerte DS18B20
bez_DS = (
    "T01",
    "T02",
    "T03",
    "T04",
    "T05"
    )

header.extend(bez_DS) #erweitern des Headers um die Temperaturkanalbezeichnungen

#Tupel mit den Ordnern der 1W-Temperatursensoren
fol_1W = (
    "28-0415a4aa94ff",
    "28-0415a4cdf3ff",
    "28-0415a4d20bff",
    "28-0415a431fcff",
    "28-011592a60dff"
    )

AnzTsens = len(fol_1W)

#Zuordnung Adressen und Korrekturwert und Kabelbeschriftung
#28-0415a4aa94ff  Tkorr:  0 Kabel TBD
#28-0415a4cdf3ff  Tkorr:  0 Kabel TBD
#28-0415a4d20bff  Tkorr:  0 Kabel TBD
#28-0415a431fcff  Tkorr:  0 Kabel TBD
#28-011592a60dff  Tkorr:  0 Kabel TBD

#Tupel mit den Korrekturwerten der einzelnen Sensoren
TEMPDS_korr = (0.000000, 0.000000, 0.000000, 0.000000, 0.000000)
#Liste mit den Temperaturwerten
TEMPDS_valu = [0,0,0,0,0]
#Liste mit den Temperatursummenwerten
TEMPDS_summ = [0,0,0,0,0]
#Liste mit den letzten Temperaturwerten
TEMPDS_last = [0,0,0,0,0]


#CSV Datei im LOG-Pfad anlegen mit nächster freier Nummer, Header schreiben
while os.path.exists(pfad_LOG + datei_LOG + str(datei_NUM) + ".csv") == True:
    datei_NUM += 1
pfad_GES = pfad_LOG + datei_LOG + str(datei_NUM) + ".csv"
Zeile2 = "TIMEOUT " + str(TIMEOUT_seku) + "s"
with open(pfad_GES, "x") as out:
    cw = csv.writer(out)
    cw.writerow([pfad_GES])
    cw.writerow([Zeile2])
    cw.writerow(header)
header = [] #wird nicht mehr weiter gebraucht

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

#Main
funct_Event("Programmneustart")
#TIME_init = time.time()

while True:
    TIMEOUT_start = time.time() #Zuweisung der gerade aktuellen Zählerzeit
    COUNTER_mess = 0
    COUNTER_logs += 1

    while time.time() < TIMEOUT_start + TIMEOUT_seku: #Intervall rum ohne Zyklusende?
        COUNTER_mess += 1

# PAUSE_oben (Temperaturmessungen NEU) ==================================
        print("Arraymessung", COUNTER_mess, ":")
        for i in range(0, AnzTsens): #len(fol_1W)):
            try:
                #Temperatur aus Datei einlesen
                sensor = "/sys/devices/w1_bus_master1/" + fol_1W[i] + "/w1_slave"
                file = open(sensor, "r")
                lines = file.readlines()
                file.close()
                while lines[0].strip()[-3:] != "YES":
                    #time.sleep(0.8)
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
            print("Einzelmessung", bez_DS[i], "=", TEMPDS_valu[i])
        #print("Das war Temp-Arraymessung Nr", COUNTER_mess)

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
