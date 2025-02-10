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

# Es liegen zwei xls-Dateien vor. Eine mit Anmeldungen aus HisInOne und eine den abgegebenen Wünschen
# aus dem Ilias-Kurs. Ziel ist es, die erste Tabelle um die Prüferwünsche, und den eingeteilten Prüfer
# zu ergänzen. Weitere Beschreibung siehe unten.

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

def update_slots(i, prgebiet, n):
    if prgebiet == "Analysis I und II":
        st.session_state.pruefer[i]["SlotsAna"] = st.session_state[f"{st.session_state.pruefer[i]['Kurzname']}_Ana_size"]
    elif prgebiet == "Lineare Algebra I und II": 
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
    st.write("Wenn die Default-Einstellungen genändert werden sollen, muss die Datei `config.py` angepasst werden. Dies gilt auch, wenn neue Prüfer hinzukommen oder alte wegfallen.")
    st.session_state.kosten[1] = st.number_input("Kosten, wenn Prüfer == Wunsch2 und das Prüfungsgebiet richtig ist", min_value = 0, value = st.session_state.kosten[1], key = f"kosten1")
    st.session_state.kosten[2] = st.number_input("Kosten, wenn Prüfer == Wunsch3 und das Prüfungsgebiet richtig ist", min_value = 0, value = st.session_state.kosten[2], key = f"kosten2")
    st.session_state.kosten[3] = st.number_input("Kosten, wenn kein Prüferwunsch erfüllt wird aber das Prüfungsgebiet des Prüfungsslots richtig ist", min_value = 0, value = st.session_state.kosten[3], key = f"kosten3")
    st.session_state.kosten[4] = st.number_input("Kosten, wenn das Prüfungsgebiet des Prüfungsslots nicht richtig ist", min_value = 0, value = st.session_state.kosten[4], key = f"kosten4")
    st.session_state.fixed_seed = st.toggle("Es werden immer dieselben Zufallszahlen genommen.", st.session_state.fixed_seed)

with st.expander("Prüfungsslots"):
    st.write("Wenn die Default-Einstellungen genändert werden sollen, muss die Datei `config.py` angepasst werden. Dies gilt auch, wenn neue Prüfer hinzukommen oder alte wegfallen.")
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
    col0, col1 = st.columns([2,2])
    with col0:
        st.session_state.xls_his = st.file_uploader("Anmeldungen aus HisInOne (xls)", key = "data_His")
        st.write("Die Datei wird aus HisInOne generiert werden. Sie muss Spalten 'Mtknr', 'Nachname', 'Vorname', 'Elementnr', 'Prüfer' enthalten. Die Spalte 'Prüfer' enthält dabei -- falls zutreffend -- den Namen des Prüfers der Erstprüfung. Weitere Spalten dürfen enthalten sein und werden nicht verändert.")
        st.write("Zulässige Einträge in der Spalte 'Prüfer' sind:")
        st.write(", ".join(x['Kurzname'] for x in pruefer))
        if st.session_state.xls_his:
            df_his = pd.read_excel(st.session_state.xls_his).fillna("")
            df_his.rename(columns={'Prüfer': 'Erstprüfer'}, inplace=True)
            pr_nummer_dict = { x["Nummer"] : x["Prüfungsgebiet"] for x in pruefungsnummern}
            df_his["Prüfungsgebiet"] = [ pr_nummer_dict.get(x, "") for x in df_his["Elementnr"]]
            df_his["Name"] = df_his.apply(lambda row: f"{row['Nachname']}, {row['Vorname']}", axis = 1)
            nummer_unbekannt = [x for x in df_his["Elementnr"] if x not in pr_nummer_dict.keys()]
            # st.write(df_his)
            if nummer_unbekannt != []:
                st.warning(f"Folgende Prüfungsnummern sind unbekannt und können nicht zugeordnet werden: {', '.join(nummer_unbekannt)}")

            df_his.fillna("", inplace=True)
            dict_his = df_his.to_dict(orient="records")

            st.write("Anmeldungen")
            anm = {"Name": "Anmeldungen", 
                "Analysis" : df_his[df_his["Prüfungsgebiet"] == "Analysis I und II"].shape[0], 
                "Lineare Algebra" : df_his[df_his["Prüfungsgebiet"] == "Lineare Algebra I und II"].shape[0],
                "Summe" : df_his.shape[0]
                }
            anm2 = {"Name": "Slots", 
                "Analysis" : sum([ p['Slots'] for p in st.session_state.pruefer if p["Ana"]]), 
                "Lineare Algebra" : sum([ p['Slots'] for p in st.session_state.pruefer if p["LA"]]),
                "Summe" : ""
                }
            st.write(pd.DataFrame([anm, anm2]))

    with col1:
        st.session_state.xls_ilias = st.file_uploader("Prüferwünsche aus Ilias (xls)", key = "data_Ilias")
        st.write("Die Datei wird aus dem Ilias-Kurs generiert. Genauer müssen die dortigen Dateien aus den beiden Prüfungsgebieten 'Analysis I und II' sowie 'Lineare Algebra I unfd II' in eine Datei zusammengeführt werden. Sie muss Spalten 'Matrikelnummer', 'Prüfungsgebiet', 'Prüfer*in Priorität 1', 'Prüfer*in Priorität 2', 'Prüfer*in Priorität 3', 'Bemerkung', 'Letzte Änderung', 'Im Besitz von (Name)' enthalten. Weitere Spalten dürfen enthalten sein und werden nicht verändert.")
        st.write("Zulässige Einträge in Spalte 'Prüfungsgebiet' sind: 'Analysis I und II' und 'Lineare Algera I und II'.")
        if st.session_state.xls_ilias and st.session_state.xls_his:
            df_ilias = pd.read_excel(st.session_state.xls_ilias)
            df_ilias.fillna("", inplace=True)
            df_ilias.sort_values(by='Letzte Änderung', ascending=True, inplace=True)
            st.write(f"{df_ilias.shape[0]} Datensätze geladen.")
            df_ilias.drop_duplicates(subset=['Matrikelnummer', 'Im Besitz von (Name)', 'Prüfungsgebiet'], keep="last", inplace=True)
            st.write(f"{df_ilias.shape[0]} Datensätze nach Löschen von Duplikaten.")
            st.write(df_ilias)

            dict_ilias = df_ilias.to_dict(orient="records")
            for item in dict_ilias:
                i = find_item(dict_his, { "Mtknr" : item["Matrikelnummer"], "Name" : item["Im Besitz von (Name)"], "Prüfungsgebiet" : item["Prüfungsgebiet"]})
                # Falls Prüferwünsche angegeben sind, werden diese immer genommen. 
                if i >= 0:
                    dict_his[i]["wunsch1"] = pruefer_kurzname[item["Prüfer*in Priorität 1"]]
                    dict_his[i]["wunsch2"] = pruefer_kurzname[item["Prüfer*in Priorität 2"]]
                    dict_his[i]["wunsch3"] = pruefer_kurzname[item["Prüfer*in Priorität 3"]]
                    dict_his[i]["Bemerkung"] = item["Bemerkung"]
                    
                elif find_item(dict_his, { "Mtknr" : item["Matrikelnummer"], "Prüfungsgebiet" : item["Prüfungsgebiet"]}) != -1:
                    st.warning(f"Matrikelnummer {item['Matrikelnummer']} trägt den falschen Namen.")
                elif find_item(dict_his, { "Name" : item["Im Besitz von (Name)"], "Prüfungsgebiet" : item["Prüfungsgebiet"]}) != -1:
                    st.warning(f"{item['Im Besitz von (Name)']} trägt die falsche Matrikelnummer.")
                else:
                    st.warning(f"Matrikelnummer {item['Matrikelnummer']} ({item['Im Besitz von (Name)']}; {item['Prüfungsgebiet']}) nicht in der HisInOne-Liste gefunden. Der Eintrag wird dort ergänzt.")
                    dict_his.append(
                        {
                            "Mtknr" : item['Matrikelnummer'],
                            "Name" : item['Im Besitz von (Name)'],
                            "Nachname" : item['Im Besitz von (Name)'].split(",", 1)[0],
                            "Vorname" : item['Im Besitz von (Name)'].split(",", 1)[1] if "," in item['Im Besitz von (Name)'] else "",
                            "Prüfungsgebiet" : item["Prüfungsgebiet"],
                            "wunsch1" : pruefer_kurzname[item["Prüfer*in Priorität 1"]],
                            "wunsch2" : pruefer_kurzname[item["Prüfer*in Priorität 2"]],
                            "wunsch3" : pruefer_kurzname[item["Prüfer*in Priorität 3"]],
                            "Bemerkung" : item["Bemerkung"]
                        }
                    )
    if st.session_state.xls_his and st.session_state.xls_ilias:
        dict_his = sorted(dict_his, key=lambda x: (x["Prüfungsgebiet"], x["Name"]))
        for item in dict_his:
            # st.write(item)
            if "wunsch1" not in item.keys() and "Erstprüfer" != "":
                item["wunsch1"] = item["wunsch2"] = item["wunsch3"] = item["Prüfer"] = ""
                st.write(f"{item['Mtknr']} ({item['Nachname']}, {item['Vorname']}; {item['Prüfungsgebiet']}) ist noch kein Prüfer zugeordnet, und hat keinen Prüferwunsch angegeben")

        df = pd.DataFrame.from_dict(dict_his)

        anzahl_slots = sum([ p['Slots'] for p in st.session_state.pruefer])
        if df.shape[1] > anzahl_slots:
            st.error(f"**Einteilung nicht möglich, da es {df.shape[1]} Anmeldungen, aber nur {anzahl_slots} Prüfungsslots gibt.**")
        else: 
            st.success(f"Einteilung möglich, es gibt genug Prüfungsslots.")

        # Aussortieren von doppelten Wünschen
        for w1, w2 in combinations(["wunsch1", "wunsch2", "wunsch3"],2):
            for i in range(df.shape[0]):
                if df[w1][i] == df[w2][i] and df[w1][i] != "":
                    st.warning(f"{df['Nachname'][i]}, {df['Vorname'][i]} ({df['Mtknr'][i]}) hat Prüfer {df[w1][i]} als {w1} und {w2} angegeben. Es wird {w2} ='' gesetzt.")
                    df[w2][i] = ""

        # Falls Prüfer schon feststeht und keine Wünsche angegeben sind, werden alle Wünsche auf diesen Prüfer gesetzt
        for i in range(df.shape[0]):
            if df["Erstprüfer"][i] != "" and df["wunsch1"][i] == "":
                df["wunsch1"][i] = df["Erstprüfer"][i]
                df["wunsch2"][i] = ""
                df["wunsch3"][i] = ""
                st.warning(f"{df['Nachname'][i]}, {df['Vorname'][i]} ({df['Mtknr'][i]}) hat Wiederholungsprüfung in {df['Prüfungsgebiet'][i]} und hat keine Wünsche angegeben. Es wird wunsch1 = {df['Erstprüfer'][i]} und wunsch2, wunsch3 leer gesetzt.")

if st.session_state.xls_his and st.session_state.xls_ilias:
    with st.expander("Einteilung"):
        st.write("Nun wird die Einteilung vorgenommen.")
        # Diese Liste von Listen gibt die Wünsche der Studierenden 
        wunschspalten = [df.columns.get_loc(name) for name in ["wunsch1", "wunsch2", "wunsch3"]]
        wuensche = [list(df[df.columns[i]]) for i in wunschspalten]
        allewuensche = [item for sublist in wuensche for item in sublist] 
        pruefer_kurznamen = [p["Kurzname"] for p in st.session_state.pruefer]

        fehler = [w for w in allewuensche if w not in pruefer_kurznamen + ["", None, np.nan]]
        if len(fehler):
            st.warning(f"Wünsche {', '.join(fehler)} wurden angegeben, sind aber nicht wählbar!")

        if st.session_state.fixed_seed:
            random.seed(42)

        spalten = []

        for i in range(max([p["Slots"] for p in st.session_state.pruefer])):
            for p in st.session_state.pruefer:
                if i < p["Slots"]:
                    spalten.extend([(p["Kurzname"], p["Ana"], p["LA"])])

        kostenMatrix = np.zeros((df.shape[0], len(spalten)))
        prgebiet = df["Prüfungsgebiet"]
        for i in range(kostenMatrix.shape[0]):
            for j in range(kostenMatrix.shape[1]):
                if (prgebiet[i] == "Analysis I und II" and not spalten[j][1]) or (prgebiet[i] == "Lineare Algebra I und II" and not spalten[j][2]):
                    kostenMatrix[i,j] = float(kosten[4])
                else:
                    kostenMatrix[i,j] = float(kosten[3])
                for w in range(len(wuensche)):
                    if wuensche[w][i] == spalten[j][0]:
                        kostenMatrix[i,j] = float(kosten[w])

        row_ind, col_ind = linear_sum_assignment(kostenMatrix, maximize=False)
        df["Name"] = [spalten[j][0] for j in col_ind]
        df["Prüfer"] = df["Name"]
        del df["Name"]
        #df.rename(columns={'Name': 'Prüfer'}, inplace=True)
        #df = df[["Mtknr", "Nachname", "Vorname", "Prüfungsgebiet", "Prüfer", "wunsch1", "wunsch2", "wunsch3"]]

        st.write("Hier das Ergebnis der Einteilung:")
        st.write("### Studierende mit zwei Prüfungen:")
        for i in range(len(df)):
            for j in range(i + 1, len(df)):
                if df.iloc[i]["Mtknr"] == df.iloc[j]["Mtknr"]:
                    st.write(f"{df.iloc[i]['Nachname']}, {df.iloc[i]['Vorname']} ({df.iloc[i]['Mtknr']}) hat sich zu Prüfungen in {df.iloc[i]['Prüfungsgebiet']} und {df.iloc[j]['Prüfungsgebiet']} angemeldet. Prüfer sind **{df.iloc[i]['Prüfer']}** und **{df.iloc[j]['Prüfer']}**.")    
        st.write("### Ergänzung der HisInOne-Liste  :")
        st.write(df)
        
        output = BytesIO()

        # Streamlit-Button für den Download
        excel_data = to_excel(df)
        st.download_button(
            label="Download Excel-Datei",
            data=excel_data,
            file_name="anmeldungen.xls",
            mime="application/vnd.ms-excel"
        )

        w1 = {"Prüfungsgebiet": "Analysis I und II", 
               "Wunsch 1" : df[(df["Prüfungsgebiet"] == "Analysis I und II") & (df["Prüfer"] == df["wunsch1"])].shape[0], 
               "Wunsch 2" : df[(df["Prüfungsgebiet"] == "Analysis I und II") & (df["Prüfer"] == df["wunsch2"])].shape[0], 
               "Wunsch 3" : df[(df["Prüfungsgebiet"] == "Analysis I und II") & (df["Prüfer"] == df["wunsch3"])].shape[0], 
               }
        w1["kein Wunsch erfüllt"] = df[(df["Prüfungsgebiet"] == "Analysis I und II") & (df["wunsch1"] != "")].shape[0] - w1["Wunsch 1"] - w1["Wunsch 2"] - w1["Wunsch 3"]
        w1["kein Wunsch angegeben"] = df[(df["Prüfungsgebiet"] == "Analysis I und II") & (df["wunsch1"] == "")].shape[0]
        w1["Summe"] = df[df["Prüfungsgebiet"] == "Analysis I und II"].shape[0]     
        
        w2 = {"Prüfungsgebiet": "Lineare Algebra I und II", 
               "Wunsch 1" : df[(df["Prüfungsgebiet"] == "Lineare Algebra I und II") & (df["Prüfer"] == df["wunsch1"])].shape[0], 
               "Wunsch 2" : df[(df["Prüfungsgebiet"] == "Lineare Algebra I und II") & (df["Prüfer"] == df["wunsch2"])].shape[0], 
               "Wunsch 3" : df[(df["Prüfungsgebiet"] == "Lineare Algebra I und II") & (df["Prüfer"] == df["wunsch3"])].shape[0], 
               }
        w2["kein Wunsch erfüllt"] = df[(df["Prüfungsgebiet"] == "Lineare Algebra I und II") & (df["wunsch1"] != "")].shape[0] - w2["Wunsch 1"] - w2["Wunsch 2"] - w2["Wunsch 3"]
        w2["kein Wunsch angegeben"] = df[(df["Prüfungsgebiet"] == "Lineare Algebra I und II") & (df["wunsch1"] == "")].shape[0]
        w2["Summe"] = df[df["Prüfungsgebiet"] == "Lineare Algebra I und II"].shape[0]


        w3 = {"Prüfungsgebiet": "Summe", 
               "Wunsch 1" : df[df["Prüfer"] == df["wunsch1"]].shape[0], 
               "Wunsch 2" : df[df["Prüfer"] == df["wunsch2"]].shape[0], 
               "Wunsch 3" : df[df["Prüfer"] == df["wunsch3"]].shape[0], 
               }
        w3["kein Wunsch erfüllt"] = df[df["wunsch1"] != ""].shape[0] - w3["Wunsch 1"] - w3["Wunsch 2"] - w3["Wunsch 3"]
        w3["kein Wunsch angegeben"] = df[df["wunsch1"] == ""].shape[0]
        w3["Summe"] = df.shape[0]     

        st.write(pd.DataFrame([w1, w2, w3]))

        bel = []
        for p in st.session_state.pruefer:
            b = {"Name" : f"{p['Nachname']}, {p['Vorname']}",
                 "Slots" : p["Slots"],
                 "Ana Prüfungen" : df[(df["Prüfungsgebiet"] == "Analysis I und II") & (df["Prüfer"] == p["Kurzname"])].shape[0],
                 "LA Prüfungen" : df[(df["Prüfungsgebiet"] == "Lineare Algebra I und II") & (df["Prüfer"] == p["Kurzname"])].shape[0],                 
            }
            bel.append(b)

        st.write(pd.DataFrame(bel))

