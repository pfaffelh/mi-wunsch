import pandas as pd

pruefer = [
    {"Kurzname":"bartels","Vorname":"Sören","Nachname":"Bartels", "SlotsAna" : 5, "SlotsLA": 5},
    {"Kurzname":"criens","Vorname":"David","Nachname":"Criens", "SlotsAna" : 5, "SlotsLA": 5},
    {"Kurzname":"dondl","Vorname":"Patrick","Nachname":"Dondl", "SlotsAna" : 5, "SlotsLA": 5},
    {"Kurzname":"goette","Vorname":"Sebastian","Nachname":"Goette", "SlotsAna" : 5, "SlotsLA": 5},
    {"Kurzname":"grosse","Vorname":"Nadine","Nachname":"Große", "SlotsAna" : 5, "SlotsLA": 5},
    {"Kurzname":"huber","Vorname":"Annette","Nachname":"Huber-Klawitter", "SlotsAna" : 5, "SlotsLA": 5},
    {"Kurzname":"junker","Vorname":"Markus","Nachname":"Junker", "SlotsAna" : 5, "SlotsLA": 5},
    {"Kurzname":"kebekus","Vorname":"Stefan","Nachname":"Kebekus", "SlotsAna" : 5, "SlotsLA": 5},
    {"Kurzname":"kuwert","Vorname":"Ernst","Nachname":"Kuwert", "SlotsAna" : 5, "SlotsLA": 5},
    {"Kurzname":"martin","Vorname":"Amador","Nachname":"Martin Pizarro", "SlotsAna" : 5, "SlotsLA": 5},
    {"Kurzname":"mildenberger","Vorname":"Heike","Nachname":"Mildenberger", "SlotsAna" : 5, "SlotsLA": 5},
    {"Kurzname":"pfaffelhuber","Vorname":"Peter","Nachname":"Pfaffelhuber", "SlotsAna" : 5, "SlotsLA": 5},
    {"Kurzname":"rohde","Vorname":"Angelika","Nachname":"Rohde", "SlotsAna" : 5, "SlotsLA": 5},
    {"Kurzname":"ruzicka","Vorname":"Michael","Nachname":"Ruzicka", "SlotsAna" : 5, "SlotsLA": 5},
    {"Kurzname":"schmidt","Vorname":"Thorsten","Nachname":"Schmidt", "SlotsAna" : 5, "SlotsLA": 5},
    {"Kurzname":"soergel","Vorname":"Wolfgang","Nachname":"Soergel", "SlotsAna" : 5, "SlotsLA": 5},
    {"Kurzname":"wang","Vorname":"Guofang","Nachname":"Wang", "SlotsAna" : 5, "SlotsLA": 5}
    ]

# Sortiere Prüfer
pruefer = sorted(pruefer, key=lambda x: (x['Nachname'], x['Vorname']))
# pruefer = { p["Kurzname"] : {key: value for key, value in p.items() if key != 'Kurzname'} for p in pruefer }
# pruefer = pd.DataFrame.from_dict(pruefer).transpose()

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

