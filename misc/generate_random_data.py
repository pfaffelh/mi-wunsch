import pandas as pd
import random
from openpyxl import Workbook

# Definieren der möglichen Werte für die Spalten
pruefer = ['bartels', 'criens', 'dondl', 'goette', 'grosse', 'huber', 'junker',
             'kebekus', 'kuwert', 'martin', 'mildenberger', 'pfaffelhuber',
             'rohde', 'ruzicka', 'schmidt', 'soergel', 'wang']
vornamen = ['Max', 'Anna', 'Lisa', 'Peter', 'Maria', 'Thomas', 'Julia', 'Michael']
nachnamen = ['Müller', 'Schmidt', 'Schneider', 'Fischer', 'Weber', 'Meyer', 'Wagner', 'Becker', 'Neumann', 'Hoffmann', 'Schulz', 'Koch', 'Bauer', 'Maier', 'Nowak', 'Richter', 'Klein', 'Wolf', 'Braun', 'Schulz', 'König', 'Lehmann', 'Hofmann', 'Werner', 'Kraus', 'Albrecht', 'Dietrich', 'Engel', 'Hartmann', 'Walter', 'Krüger', 'Meier', 'Schubert', 'Schulze', 'Sommer', 'Barth', 'Lang', 'Vogel', 'Schmidt', 'Müller', 'Meier', 'Schulz', 'Becker', 'Hofmann', 'Weber', 'Fischer', 'Schmidt', 'Müller', 'Meier', 'Schulz']
faecher = ['Analysis', 'Lineare Algebra']

# Funktion zum Erstellen eines zufälligen Datensatzes
def create_random_student():
    name = random.choice(nachnamen)
    # Sicherstellen, dass Wünsche nicht gleich dem Namen sind
    wünsche = random.sample(pruefer, 3)

    return {
        'Matr': random.randint(10000000, 99999999),
        'Name': random.choice(nachnamen),
        'Vorname': random.choice(vornamen),
        'Fach': random.choice(faecher),
        'wunsch1': wünsche[0],
        'wunsch2': wünsche[1],
        'wunsch3': wünsche[2]
    }

# Anzahl der zu generierenden Datensätze
anzahl_datensaetze = 50

# Erstellen einer Liste von zufälligen Datensätzen
data = [create_random_student() for _ in range(anzahl_datensaetze)]

# Erstellen eines DataFrames aus der Liste
df = pd.DataFrame(data)

with pd.ExcelWriter("studenten_data.xls", engine='openpyxl') as writer:
    df.to_excel(writer, index=False, sheet_name='Sheet1')
    worksheet = writer.sheets['Sheet1']

df = pd.read_excel('studenten_data.xls')
print(df)

