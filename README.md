# mi-wunsch
Streamlit-App zur Einteilung der Wünsche der Prüfungen in den Grundvorlesungen

## Verwendung
Default-Einstellungen sind in `config.py` einzugeben. Dies betrifft insbesondere die Namen der Prüfer und die Prüfungsnummern. 
Die Namen der Püfer müssen mit denen, die in Ilias hinterlegt sind, genau übereinstimmen. 
Aus den Prüfungsnummern werden Prüfungsgebiete (Analysis 1+2 bzw Lineare Algebra) generiert. 

### Uploads
Es müssen folgende xls-Files im Programm hochgeladen werden: 
1. Anmeldungen aus HisInOne (+Sonderfälle): Es müssen folgende Spalten vorhanden sein: Matrikelnummer, Nachname, Vorname, Nummer
2. Prüferwünsche aus Ilias: Es müssen folgende Spalten vorhanden sein: Matrikelnummer, Prüfungsgebiet, Prüfer*in Priorität 1, Prüfer*in Priorität 2, Prüfer*in Priorität 3, Letzte Änderung

Aus 2. wird von jeder Prüfung (eindeutige Matrikelnummer + Prüfungsgebiet) nur der jeweils neueste Eintrag genommen.

Es wird die erste xls-Liste um die Spalten Wiederholungsprüfung, Prüfer, Prüfer*in Priorität 1, Prüfer*in Priorität 2, Prüfer*in Priorität 3 erweitert. 

Wie werden Spezialfälle behandelt?
* Studierende, die in 1. auftauchen, aber nicht in 2., werden zufällig zugeordnet. 
* Studierende, die in 2. auftauchen, aber nicht in 1., werden zur ausgegebenen Liste ergänzt. Hier fehlt dann Name, Vorname
 

Falls Prüferwünsche angegeben sind, werden diese immer genommen. 

Falls schon ein Prüfer feststeht (zB wege Wiederholungsprüfung) und keine Wünsche angegeben sind, werden alle Wünsche auf diesen Prüfer gesetzt



Fragen: 

Bekommen Wiederholungsprüfungen denselben Prüfer wie bei der Erstprüfung?
Soll die HisInOne-Liste schon eine Spalte Prüfer haben, bei der bei den Wiederholungsprüfungen der Erstprüfer eingetragen werden kann?

