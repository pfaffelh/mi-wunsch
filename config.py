import pandas as pd

pruefer = [
    {"Kurzname":"bartels","Vorname":"Sören","Nachname":"Bartels", "Slots" : 10, "Ana" : True, "LA": True},
    {"Kurzname":"criens","Vorname":"David","Nachname":"Criens", "Slots" : 10, "Ana" : True, "LA": True},
    {"Kurzname":"dondl","Vorname":"Patrick","Nachname":"Dondl", "Slots" : 10, "Ana" : True, "LA": True},
    {"Kurzname":"goette","Vorname":"Sebastian","Nachname":"Goette", "Slots" : 10, "Ana" : True, "LA": True},
    {"Kurzname":"grosse","Vorname":"Nadine","Nachname":"Große", "Slots" : 10, "Ana" : True, "LA": True},
    {"Kurzname":"huber","Vorname":"Annette","Nachname":"Huber-Klawitter", "Slots" : 10, "Ana" : True, "LA": True},
    {"Kurzname":"junker","Vorname":"Markus","Nachname":"Junker", "Slots" : 10, "Ana" : True, "LA": True},
    {"Kurzname":"kebekus","Vorname":"Stefan","Nachname":"Kebekus", "Slots" : 10, "Ana" : True, "LA": True},
    {"Kurzname":"kuwert","Vorname":"Ernst","Nachname":"Kuwert", "Slots" : 10, "Ana" : True, "LA": True},
    {"Kurzname":"martin","Vorname":"Amador","Nachname":"Martin Pizarro", "Slots" : 10, "Ana" : True, "LA": True},
    {"Kurzname":"mildenberger","Vorname":"Heike","Nachname":"Mildenberger", "Slots" : 10, "Ana" : True, "LA": True},
    {"Kurzname":"pfaffelhuber","Vorname":"Peter","Nachname":"Pfaffelhuber", "Slots" : 10, "Ana" : True, "LA": True},
    {"Kurzname":"rohde","Vorname":"Angelika","Nachname":"Rohde", "Slots" : 10, "Ana" : True, "LA": True},
    {"Kurzname":"ruzicka","Vorname":"Michael","Nachname":"Ruzicka", "Slots" : 10, "Ana" : True, "LA": True},
    {"Kurzname":"schmidt","Vorname":"Thorsten","Nachname":"Schmidt", "Slots" : 10, "Ana" : True, "LA": True},
    {"Kurzname":"soergel","Vorname":"Wolfgang","Nachname":"Soergel", "Slots" : 10, "Ana" : True, "LA": True},
    {"Kurzname":"wang","Vorname":"Guofang","Nachname":"Wang", "Slots" : 10, "Ana" : True, "LA": True}
    ]

# Sortiere Prüfer
pruefer = sorted(pruefer, key=lambda x: (x['Nachname'], x['Vorname']))
# pruefer = { p["Kurzname"] : {key: value for key, value in p.items() if key != 'Kurzname'} for p in pruefer }
# pruefer = pd.DataFrame.from_dict(pruefer).transpose()

pruefer_kurzname = { f"{p['Vorname']} {p['Nachname']}" : p['Kurzname'] for p in pruefer}

pruefungsnummern = [
    {"Nummer":"07LE23PL-BSc21-P-Ana","Studiengang":"BSc","Fach":"Analysis"},
    {"Nummer":"07LE23PL-2HfB21-P-Ana","Studiengang":"2HfB","Fach":"Analysis"},
    {"Nummer":"07LE23PL-MEH21-P-Ana","Studiengang":"MEd ErwHF","Fach":"Analysis"},
    {"Nummer":"07LE23PL-MEB21-P-Ana","Studiengang":"MEd ErwBF","Fach":"Analysis"},
    {"Nummer":"07LE23PL-BSc12-P-LA","Studiengang":"BSc","Fach":"Lineare Algebra"},
    {"Nummer":"07LE23PL-BSc21-P-LA","Studiengang":"BSc","Fach":"Lineare Algebra"},
    {"Nummer":"07LE23PL-2HfB21-P-LA","Studiengang":"2HfB","Fach":"Lineare Algebra"},
    {"Nummer":"07LE23PL-MEH21-P-LA","Studiengang":"MEd ErwHF","Fach":"Lineare Algebra"}
    ]

wunschspalten = [12, 13, 14]

# Kosten, falls die optimale Zuordnung nicht möglich ist:
kosten = [0, # 0: Falls pruefer == wunsch1 bekommt und das Fach richtig ist
          1, # 1: Falls pruefer == wunsch2 bekommt und das Fach richtig ist
          2, # 2: Falls pruefer == wunsch3 bekommt und das Fach richtig ist
          5, # 3: Falls pruefer not in [wunsch1, wunsch2, wunsch3] und das Fach richtig ist
          1000 # 4: Falls das Fach nicht richtig ist
          ]
bar_length = 100 # Länge in Pixel