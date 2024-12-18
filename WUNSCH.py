import streamlit as st
import pandas as pd
from io import BytesIO
import numpy as np
import random
from itertools import combinations
from scipy.optimize import linear_sum_assignment
from datetime import datetime
from config import *

st.set_page_config(page_title="Prüfungseinteilung", layout="wide")

# Es liegt eine xls-Datei vor mit Feldern
# Matr, Name, Vorname, Fach, wunsch1, wunsch2, wunsch3
# Fach ist "Analysis" oder "Lineare Algebra"
# Ziel ist es, eine Spalten zu Ergänzungen: Zuteilung des Prüfers

# In config.py sind die Prüfer und ihre initialen Prüfungsslots definiert. 

st.header("Einteilung der Prüfungen für Analysis und Lineare Algebra")

if "pruefer" not in st.session_state:
    st.session_state.pruefer = pruefer
if "kosten" not in st.session_state:
    st.session_state.kosten = kosten
if "fixed_seed" not in st.session_state:
    st.session_state.fixed_seed = True
if "xls_his" not in st.session_state:
    st.session_state.xls_his = None
if "xls_ilias" not in st.session_state:
    st.session_state.xls_ilias = None

def to_excel(df):
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
        worksheet = writer.sheets['Sheet1']

        # Automatische Anpassung der Spaltenbreite an die Inhalte
        for col in worksheet.columns:
            max_length = 0
            col_letter = col[0].column_letter  # Spaltenbuchstabe (z.B., 'A', 'B', 'C')
            for cell in col:
                try:
                    max_length = max(max_length, len(str(cell.value)))
                except:
                    pass
            adjusted_width = max_length + 2  # +2 für Puffer
            worksheet.column_dimensions[col_letter].width = adjusted_width
    return output.getvalue()

def update_slots(i, fach, n):
    if fach == "Analysis":
        st.session_state.pruefer[i]["SlotsAna"] = st.session_state[f"{st.session_state.pruefer[i]['Kurzname']}_Ana_size"]
    elif fach == "Lineare Algebra": 
        st.session_state.pruefer[i]["SlotsLA"] = st.session_state[f"{st.session_state.pruefer[i]['Kurzname']}_LA_size"]

# list is a list of dicts, query is a dict
def find_item(list, query):
    res = -1
    for i, x in enumerate(list):
        if query.items() <= x.items():
            res = i
            break
    return res

with st.expander("Grundeinstellungen"):
    st.session_state.kosten[1] = st.number_input("Kosten, wenn Prüfer == Wunsch2 und das Fach richtig ist", min_value = 0, value = st.session_state.kosten[1], key = f"kosten1")
    st.session_state.kosten[2] = st.number_input("Kosten, wenn Prüfer == Wunsch3 und das Fach richtig ist", min_value = 0, value = st.session_state.kosten[2], key = f"kosten2")
    st.session_state.kosten[3] = st.number_input("Kosten, wenn kein Prüferwunsch erfüllt wird aber das Fach des Prüfungsslots richtig ist", min_value = 0, value = st.session_state.kosten[3], key = f"kosten3")
    st.session_state.kosten[4] = st.number_input("Kosten, wenn das Fach des Prüfungsslots nicht richtig ist", min_value = 0, value = st.session_state.kosten[4], key = f"kosten4")
    st.session_state.fixed_seed = st.toggle("Es werden immer dieselben Zufallszahlen genommen.", st.session_state.fixed_seed)

with st.expander("Prüfungsslots"):
    col = st.columns([2,2,1,1])
    col[1].write("#### Anzahl")
    col[2].write("#### Prüft Analysis")
    col[3].write("#### Prüft LinAlg")

    pr = st.session_state.pruefer
    for i, p in enumerate(pr):
        col = st.columns([2,2,1,1])
        col[0].write(f"{p['Vorname']} {p['Nachname']}")
        p['Slots'] = col[1].number_input("Anzahl", min_value = 0, value = p['Slots'], key = f"{p['Kurzname']}_Slots_size", label_visibility="collapsed")
        p["Ana"] = col[2].toggle("Prüft Analysis", p["Ana"], key = f"{p['Kurzname']}_Ana", label_visibility = "collapsed")
        p["LA"] = col[3].toggle("Prüft Lineare Algebra", p["LA"], key = f"{p['Kurzname']}_LA", label_visibility = "collapsed")

    col = st.columns([2,2,1,1])
    col[0].write("#### Summe")
    col[1].markdown(sum([ p['Slots'] for p in st.session_state.pruefer]))
    col[2].markdown(sum([ p['Slots'] for p in st.session_state.pruefer if p["Ana"]]))
    col[3].markdown(sum([ p['Slots'] for p in st.session_state.pruefer if p["LA"]]))

    save = st.button("Speichern", type="primary")
    if save:
        st.session_state.pruefer = pr

with st.expander("Upload Daten von Studierenden", expanded = False if st.session_state.xls_his is not None and st.session_state.xls_ilias is not None else True):
    col0, col1, col2 = st.columns([2,1,1])
    with col0:
        st.session_state.xls_his = st.file_uploader("Anmeldungen aus HisInOne (xls)", key = "data_His")
        if st.session_state.xls_his:
            df_his = pd.read_excel(st.session_state.xls_his)
            pr_nummer_dict = { x["Nummer"] : x["Fach"] for x in pruefungsnummern}
            df_his["Fach"] = [ pr_nummer_dict.get(x, "") for x in df_his["Nummer"]]
            df_his["Name"] = df_his.apply(lambda row: f"{row['Nachname']}, {row['Vorname']}", axis = 1)
            nummer_unbekannt = [x for x in df_his["Nummer"] if x not in pr_nummer_dict.keys()]
            st.write(df_his)
            if nummer_unbekannt != []:
                st.warning(f"Folgende Prüfungsnummern sind unbekannt und können nicht zugeordnet werden: {', '.join(nummer_unbekannt)}")

            dict_his = df_his.to_dict(orient="records")

            st.write("Anmeldungen")
            anm = {"Name": "Anmeldungen", 
                "Analysis" : df_his[df_his["Fach"] == "Analysis"].shape[0], 
                "Lineare Algebra" : df_his[df_his["Fach"] == "Lineare Algebra"].shape[0],
                "Summe" : df_his.shape[0]
                }
            anm2 = {"Name": "Slots", 
                "Analysis" : sum([ p['Slots'] for p in st.session_state.pruefer if p["Ana"]]), 
                "Lineare Algebra" : sum([ p['Slots'] for p in st.session_state.pruefer if p["LA"]]),
                "Summe" : ""
                }
            st.write(pd.DataFrame([anm, anm2]))

    with col1:
        st.session_state.xls_ilias_ana = st.file_uploader("Analysis-Prüferwünsche aus Ilias (xls)", key = "data_Ilias_ana")
        if st.session_state.xls_ilias_ana:
            df_ilias_ana = pd.read_excel(st.session_state.xls_ilias_ana)
            df_ilias_ana.sort_values(by='Letzte Änderung', ascending=True, inplace=True)
            st.write(f"{df_ilias_ana.shape[0]} Datensätze geladen.")
            df_ilias_ana.drop_duplicates(subset=['Matrikelnummer'], keep="last", inplace=True)
            st.write(f"{df_ilias_ana.shape[0]} Datensätze nach Löschen von Duplikaten.")
            st.write(df_ilias_ana)

            dict_ilias_ana = df_ilias_ana.to_dict(orient="records")
            for item in dict_ilias_ana:
                i = find_item(dict_his, { "MatrikelNr." : item["Matrikelnummer"], "Name" : item["Im Besitz von (Name)"], "Fach" : "Analysis"})
                if i >= 0:
                    dict_his[i]["wunsch1"] = item["Prüfer*in Priorität 1"]
                    dict_his[i]["wunsch2"] = item["Prüfer*in Priorität 2"]
                    dict_his[i]["wunsch3"] = item["Prüfer*in Priorität 2"]
                elif find_item(dict_his, { "MatrikelNr." : item["Matrikelnummer"], "Fach" : "Analysis"}) != -1:
                    st.warning(f"Matrikelnummer {item['Matrikelnummer']} trägt den falschen Namen.")
                elif find_item(dict_his, { "Name" : item["Im Besitz von (Name)"], "Fach" : "Analysis"}) != -1:
                    st.warning(f"{['Im Besitz von (Name)']} trägt die falsche Matrikelnummer.")
                else:
                    st.warning(f"Matrikelnummer {item['Matrikelnummer']} nicht in der HisInOne-Liste gefunden.")

    with col2:
        st.session_state.xls_ilias_la = st.file_uploader("Lineare Algebra Prüferwünsche aus Ilias (xls)", key = "data_Ilias_la")
        if st.session_state.xls_ilias_la:
            df_ilias_la = pd.read_excel(st.session_state.xls_ilias_la)
            df_ilias_ana.sort_values(by='Letzte Änderung', ascending=True, inplace=True)
            st.write(f"{df_ilias_la.shape[0]} Datensätze geladen.")
            df_ilias_la.drop_duplicates(subset=['Matrikelnummer'], keep="last", inplace=True)
            st.write(f"{df_ilias_la.shape[0]} Datensätze nach Löschen von Duplikaten.")
            st.write(df_ilias_la)

            dict_ilias_la = df_ilias_ana.to_dict(orient="records")
            for item in dict_ilias_la:
                i = find_item(dict_his, { "MatrikelNr." : item["Matrikelnummer"], "Name" : item["Im Besitz von (Name)"], "Fach" : "Lineare Algebra"})
                if i >= 0:
                    dict_his[i]["wunsch1"] = item["Prüfer*in Priorität 1"]
                    dict_his[i]["wunsch2"] = item["Prüfer*in Priorität 2"]
                    dict_his[i]["wunsch3"] = item["Prüfer*in Priorität 2"]
                elif find_item(dict_his, { "MatrikelNr." : item["Matrikelnummer"], "Fach" : "Lineare Algebra"}) != -1:
                    st.warning(f"Matrikelnummer {item['Matrikelnummer']} trägt den falschen Namen.")
                elif find_item(dict_his, { "Name" : item["im Besitz von (Name)"], "Fach" : "Lineare Algebra"}) != -1:
                    st.warning(f"{['im Besitz von (Name)']} trägt die falsche Matrikelnummer.")
                else:
                    st.warning(f"Matrikelnummer {item['Matrikelnummer']} nicht in der HisInOne-Liste gefunden.")

    if st.session_state.xls_his and st.session_state.xls_ilias_ana and st.session_state.xls_ilias_la:
        for item in dict_his:
            if "wunsch1" not in item.keys():
                item["wunsch1"] = item["wunsch2"] = item["wunsch3"] = ""
                st.write(f"{item['MatrikelNr.']} ({item['Nachname']}, {item['Vorname']}) hat keinen Prüferwunsch angegeben")

        df = pd.DataFrame.from_dict(dict_his)
        st.write(df)

        anzahl_slots = sum([ p['Slots'] for p in st.session_state.pruefer])
        if df.shape[1] > anzahl_slots:
            st.error(f"**Einteilung nicht möglich, da es {df.shape[1]} Anmeldungen, aber nur {anzahl_slots} Prüfungsslots gibt.**")
        else: 
            st.success(f"Einteilung möglich, es gibt genug Prüfungsslots.")

        for w1, w2 in combinations(["wunsch1", "wunsch2", "wunsch3"],2):
            for i in range(df.shape[0]):
                if df[w1][i] == df[w2][i]:
                    st.warning(f"{df['Nachname'][i]}, {df['Vorname'][i]} ({df['MatrikelNr.'][i]}) hat Prüfer {df[w1][i]} als {w1} und {w2} angegeben. Es wird {w2} ='' gesetzt.")
                    df[w2][i] = ""

if st.session_state.xls_his and st.session_state.xls_ilias_ana and st.session_state.xls_ilias_la:
    with st.expander("Einteilung"):
        st.write("Nun wird die Einteilung vorgenommen.")
        # Diese Liste von Listen gibt die Wünsche der Studierenden 
        wuensche = [list(df[df.columns[i]]) for i in wunschspalten]
        allewuensche = [item for sublist in wuensche for item in sublist] 
        pruefer_kurznamen = [p["Kurzname"] for p in st.session_state.pruefer]

        fehler = [w for w in allewuensche if w not in pruefer_kurznamen + [""]]
        if len(fehler):
            st.warning(f"Wünsche {fehler} wurden angegeben, sind aber nicht wählbar!")

        if st.session_state.fixed_seed:
            random.seed(42)

        spalten = []

        for i in range(max([p["Slots"] for p in st.session_state.pruefer])):
            for p in st.session_state.pruefer:
                if i < p["Slots"]:
                    spalten.extend([(p["Kurzname"], p["Ana"], p["LA"])])

        kostenMatrix = np.zeros((df.shape[0], len(spalten)))
        fach = df["Fach"]
        for i in range(kostenMatrix.shape[0]):
            for j in range(kostenMatrix.shape[1]):
                if (fach[i] == "Analysis" and not spalten[j][1]) or (fach[i] == "Lineare Algebra" and not spalten[j][2]):
                    kostenMatrix[i,j] = float(kosten[4])
                else:
                    kostenMatrix[i,j] = float(kosten[3])
                for w in range(len(wuensche)):
                    if wuensche[w][i] == spalten[j][0]:
                        kostenMatrix[i,j] = float(kosten[w])

        row_ind, col_ind = linear_sum_assignment(kostenMatrix, maximize=False)
        df["Name"] = [spalten[j][0] for j in col_ind]
        df.rename(columns={'Name': 'Prüfer'}, inplace=True)
        #df = df[["MatrikelNr.", "Nachname", "Vorname", "Fach", "Prüfer", "wunsch1", "wunsch2", "wunsch3"]]

        st.write("Hier das Ergebnis der Einteilung:")

        for stu1, stu2 in combinations(df.iterrows(), 2):
            if stu1[1]["MatrikelNr."] == stu2[1]["MatrikelNr."]:
                st.write(f"{stu1[1]['Nachname']}, {stu1[1]['Vorname']} ({stu1[1]['MatrikelNr.']}) hat sich zu Prüfungen in {stu1[1]['Fach']} und {stu2[1]['Fach']} angemeldet. Prüfer sind {stu1[1]['Prüfer']} und {stu2[1]['Prüfer']}.")    
        
        output = BytesIO()

        # Streamlit-Button für den Download
        excel_data = to_excel(df)
        st.download_button(
            label="Download Excel-Datei",
            data=excel_data,
            file_name="anmeldungen.xls",
            mime="application/vnd.ms-excel"
        )
        st.write(df)

        w1 = {"Fach": "Analysis", 
               "Wunsch 1" : df[(df["Fach"] == "Analysis") & (df["Prüfer"] == df["wunsch1"])].shape[0], 
               "Wunsch 2" : df[(df["Fach"] == "Analysis") & (df["Prüfer"] == df["wunsch2"])].shape[0], 
               "Wunsch 3" : df[(df["Fach"] == "Analysis") & (df["Prüfer"] == df["wunsch3"])].shape[0], 
               "Summe" : df[df["Fach"] == "Analysis"].shape[0]
               }
        w2 = {"Fach": "Lineare Algebra", 
               "Wunsch 1" : df[(df["Fach"] == "Lineare Algebra") & (df["Prüfer"] == df["wunsch1"])].shape[0], 
               "Wunsch 2" : df[(df["Fach"] == "Lineare Algebra") & (df["Prüfer"] == df["wunsch2"])].shape[0], 
               "Wunsch 3" : df[(df["Fach"] == "Lineare Algebra") & (df["Prüfer"] == df["wunsch3"])].shape[0], 
               "Summe" : df[df["Fach"] == "Lineare Algebra"].shape[0]
               }
        w3 = {"Fach": "Summe", 
               "Wunsch 1" : df[df["Prüfer"] == df["wunsch1"]].shape[0], 
               "Wunsch 2" : df[df["Prüfer"] == df["wunsch2"]].shape[0], 
               "Wunsch 3" : df[df["Prüfer"] == df["wunsch3"]].shape[0], 
               "Summe" : df.shape[0]
               }
        st.write(pd.DataFrame([w1, w2, w3]))

        bel = []
        for p in st.session_state.pruefer:
            b = {"Name" : f"{p['Nachname']}, {p['Vorname']}",
                 "Slots" : p["Slots"],
                 "Ana Prüfungen" : df[(df["Fach"] == "Analysis") & (df["Prüfer"] == p["Kurzname"])].shape[0],
                 "LA Prüfungen" : df[(df["Fach"] == "Lineare Algebra") & (df["Prüfer"] == p["Kurzname"])].shape[0],                 
            }
            bel.append(b)

        st.write(pd.DataFrame(bel))

