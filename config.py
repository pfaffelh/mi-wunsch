import pandas as pd

pruefer = [
    {"Kurzname":"Bartels","Vorname":"Sören","Nachname":"Bartels", "Slots" : 5, "Ana" : True, "LA": False},
    {"Kurzname":"Criens","Vorname":"David","Nachname":"Criens", "Slots" : 5, "Ana" : True, "LA": False},
    {"Kurzname":"Dondl","Vorname":"Patrick","Nachname":"Dondl", "Slots" : 5, "Ana" : True, "LA": True},
    {"Kurzname":"Goette","Vorname":"Sebastian","Nachname":"Goette", "Slots" : 5, "Ana" : True, "LA": True},
    {"Kurzname":"Grosse","Vorname":"Nadine","Nachname":"Große", "Slots" : 5, "Ana" : True, "LA": True},
    {"Kurzname":"Huber-Klawitter","Vorname":"Annette","Nachname":"Huber-Klawitter", "Slots" : 5, "Ana" : True, "LA": True},
    {"Kurzname":"Junker","Vorname":"Markus","Nachname":"Junker", "Slots" : 5, "Ana" : True, "LA": True},
    {"Kurzname":"Kebekus","Vorname":"Stefan","Nachname":"Kebekus", "Slots" : 5, "Ana" : True, "LA": True},
    {"Kurzname":"Kuwert","Vorname":"Ernst","Nachname":"Kuwert", "Slots" : 5, "Ana" : True, "LA": True},
    {"Kurzname":"Martin-Pizarro","Vorname":"Amador","Nachname":"Martin Pizarro", "Slots" : 5, "Ana" : False, "LA": True},
    {"Kurzname":"Mildenberger", "Vorname":"Heike","Nachname":"Mildenberger", "Slots" : 5, "Ana" : False, "LA": True},
    {"Kurzname":"Oswal", "Vorname": "Abhishek","Nachname":"Oswal", "Slots" : 0, "Ana" : True, "LA": True},
    {"Kurzname":"Pfaffelhuber","Vorname":"Peter","Nachname":"Pfaffelhuber", "Slots" : 5, "Ana" : True, "LA": False},
    {"Kurzname":"Rohde","Vorname":"Angelika","Nachname":"Rohde", "Slots" : 5, "Ana" : True, "LA": True},
    {"Kurzname":"Ruzicka","Vorname":"Michael","Nachname":"Ruzicka", "Slots" : 5, "Ana" : True, "LA": False},
    {"Kurzname":"Salimova","Vorname":"Diyora","Nachname":"Salimova", "Slots" : 0, "Ana" : False, "LA": True},
    {"Kurzname":"Schmidt","Vorname":"Thorsten","Nachname":"Schmidt", "Slots" : 5, "Ana" : True, "LA": True},
    {"Kurzname":"Soergel","Vorname":"Wolfgang","Nachname":"Soergel", "Slots" : 5, "Ana" : True, "LA": True},
    {"Kurzname":"Wang","Vorname":"Guofang","Nachname":"Wang", "Slots" : 5, "Ana" : True, "LA": False}
    ]

# Sortiere Prüfer
pruefer = sorted(pruefer, key=lambda x: (x['Nachname'], x['Vorname']))
# pruefer = { p["Kurzname"] : {key: value for key, value in p.items() if key != 'Kurzname'} for p in pruefer }
# pruefer = pd.DataFrame.from_dict(pruefer).transpose()

pruefer_kurzname = { f"{p['Vorname']} {p['Nachname']}" : p['Kurzname'] for p in pruefer}

pruefungsnummern = [
    {"Nummer":"07LE23PL-BSc21-P-Ana-müP","Studiengang":"BSc","Prüfungsgebiet":"Analysis I und II"},
    {"Nummer":"07LE23PL-2HfB21-P-Ana-müP","Studiengang":"2HfB","Prüfungsgebiet":"Analysis I und II"},
    {"Nummer":"07LE23PL-MEH21-P-Ana-müP","Studiengang":"MEd ErwHF","Prüfungsgebiet":"Analysis I und II"},
    {"Nummer":"07LE23PL-MEB21-P-Ana-müP","Studiengang":"MEd ErwBF","Prüfungsgebiet":"Analysis I und II"},
    {"Nummer":"07LE23PL-BSc12-P-LA-müP","Studiengang":"BSc","Prüfungsgebiet":"Lineare Algebra I und II"},
    {"Nummer":"07LE23PL-BSc21-P-LA-müP","Studiengang":"BSc","Prüfungsgebiet":"Lineare Algebra I und II"},
    {"Nummer":"07LE23PL-2HfB21-P-LA-müP","Studiengang":"2HfB","Prüfungsgebiet":"Lineare Algebra I und II"},
    {"Nummer":"07LE23PL-MEH21-P-LA-müP","Studiengang":"MEd ErwHF","Prüfungsgebiet":"Lineare Algebra I und II"}
    ]

#wunschspalten = [12, 13, 14]

# Kosten, falls die optimale Zuordnung nicht möglich ist:
kosten = [0, # 0: Falls pruefer == wunsch1 bekommt und das Prüfungsgebiet richtig ist
          1, # 1: Falls pruefer == wunsch2 bekommt und das Prüfungsgebiet richtig ist
          2, # 2: Falls pruefer == wunsch3 bekommt und das Prüfungsgebiet richtig ist
          5, # 3: Falls pruefer not in [wunsch1, wunsch2, wunsch3] und das Prüfungsgebiet richtig ist
          1000 # 4: Falls das Prüfungsgebiet nicht richtig ist
          ]

