import streamlit as st
import pandas as pd
from io import BytesIO
import numpy as np
import random
from itertools import combinations
from scipy.optimize import linear_sum_assignment
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
        st.session_state.pruefer[i]["SlotsAna"] = st.session_state[f"{st.session_state.pruefer[i]["Kurzname"]}_Ana_size"]
    elif fach == "Lineare Algebra": 
        st.session_state.pruefer[i]["SlotsLA"] = st.session_state[f"{st.session_state.pruefer[i]["Kurzname"]}_LA_size"]

with st.expander("Grundeinstellungen"):
    st.session_state.kosten[1] = st.number_input("Kosten, wenn Prüfer == Wunsch2 und das Fach richtig ist", min_value = 0, value = st.session_state.kosten[1], key = f"kosten1")
    st.session_state.kosten[2] = st.number_input("Kosten, wenn Prüfer == Wunsch3 und das Fach richtig ist", min_value = 0, value = st.session_state.kosten[2], key = f"kosten2")
    st.session_state.kosten[3] = st.number_input("Kosten, wenn kein Prüferwunsch erfüllt wird aber das Fach des Prüfungsslots richtig ist", min_value = 0, value = st.session_state.kosten[3], key = f"kosten3")
    st.session_state.kosten[4] = st.number_input("Kosten, wenn Prüfer == Wunsch1, aber das Fach des Prüfungsslots nicht richtig ist", min_value = 0, value = st.session_state.kosten[4], key = f"kosten4")
    st.session_state.kosten[5] = st.number_input("Kosten, wenn Prüfer == Wunsch2, aber das Fach des Prüfungsslots nicht richtig ist", min_value = 0, value = st.session_state.kosten[5], key = f"kosten5")
    st.session_state.kosten[6] = st.number_input("Kosten, wenn Prüfer == Wunsch3, aber das Fach des Prüfungsslots nicht richtig ist", min_value = 0, value = st.session_state.kosten[6], key = f"kosten6")
    st.session_state.kosten[7] = st.number_input("Kosten, wenn kein Prüferwunsch erfüllt wird und das Fach des Prüfungsslots nicht richtig ist", min_value = 0, value = st.session_state.kosten[7], key = f"kosten7")
    st.session_state.fixed_seed = st.toggle("Es werden immer dieselben Zufallszahlen genommen.", st.session_state.fixed_seed)

with st.expander("Prüfungsslots"):
    col = st.columns([3,1,1,1])
    col[1].write("#### Analysis")
    col[2].write("#### Lineare Algebra")
    col[3].write("#### Summe")

    max_pr = max([p["SlotsAna"]+p["SlotsLA"] for p in st.session_state.pruefer])
    for i, p in enumerate(st.session_state.pruefer):
        col = st.columns([2,1,1,1])
        col[0].write(f"{p['Vorname']} {p['Nachname']}")
        p['SlotsAna'] = col[1].number_input("Anzahl", min_value = 0, value = p['SlotsAna'], on_change = update_slots, key = f"{p["Kurzname"]}_Ana_size", label_visibility="collapsed")
        p['SlotsLA'] = col[2].number_input("Anzahl", min_value = 0, value = p['SlotsLA'], args = (i, "Lineare Algebra"), key = f"{p["Kurzname"]}_LA_size", label_visibility="collapsed")
        with col[3]:
            fill_percentage = (p["SlotsAna"] + p["SlotsLA"])/max_pr * 100  # Füllstand in Prozent
            # HTML und CSS für den Balken
            st.markdown(f"""
            <div style="width: {bar_length}px; background-color: #ddd; border-radius: 5px; overflow: hidden;">
                <div style="width: {fill_percentage}%; background-color: #4caf50; height: 20px;"></div>
            </div>
            """, unsafe_allow_html=True)

    col = st.columns([2,1,1,1])
    col[0].write("#### Summe")
    col[1].markdown(sum([ p['SlotsAna'] for p in st.session_state.pruefer]))
    col[2].markdown(sum([ p['SlotsLA'] for p in st.session_state.pruefer]))
    col[3].markdown(sum([ p['SlotsAna'] for p in st.session_state.pruefer]) + sum([ p['SlotsLA'] for p in st.session_state.pruefer]))

with st.expander("Prüferwünsche"):
    st.write("Es wird davon ausgegangen, dass Prüferwünsche in folgendem Format vorliegen:")
    df = pd.read_excel("anmeldungen_bsp.xlsx")
    st.write(df)
    wuensche_xls = st.file_uploader("Upload Wünsche")
    wuensche_xls = 'misc/studenten_data.xls'

    if wuensche_xls:
        df = pd.read_excel(wuensche_xls)
        st.write("Anmeldungen")
        anm = {"Name": "Rohdaten", 
               "Analysis" : df[df["Fach"] == "Analysis"].shape[0], 
               "Lineare Algebra" : df[df["Fach"] == "Lineare Algebra"].shape[0],
               "Summe" : df.shape[0]
               }
        df = df.drop_duplicates(subset=['Matr', 'Fach'], keep='last')
        anm2 = {"Name" : "Nach Bereinigung von Duplikaten", 
                "Analysis" : df[df["Fach"] == "Analysis"].shape[0], 
               "Lineare Algebra" : df[df["Fach"] == "Lineare Algebra"].shape[0],
               "Summe" : df.shape[0]
               }
        st.write(pd.DataFrame([anm, anm2]))

        anzahl_slots = sum([ p['SlotsAna'] for p in st.session_state.pruefer]) + sum([ p['SlotsLA'] for p in st.session_state.pruefer])
        if df.shape[1] > anzahl_slots:
            st.write(f"**Einteilung nicht möglich, da es {df.shape[1]} Anmeldungen, aber nur {anzahl_slots} Prüfungsslots gibt.**")
        else: 
            st.write(f"Einteilung möglich, es gibt genug Prüfungsslots.")

if wuensche_xls:
    with st.expander("Einteilung"):
        st.write("Nun wird die Einteilung vorgenommen.")
        # Diese Liste von Listen gibt die Wünsche der Studierenden 
        wuensche = [list(df[df.columns[i]]) for i in wunschspalten]
        allewuensche = [item for sublist in wuensche for item in sublist] 
        pruefer_kurznamen = [p["Kurzname"] for p in st.session_state.pruefer]

        fehler = [w for w in allewuensche if w not in pruefer_kurznamen + [""]]
        if len(fehler):
            st.warning(f"Wünsche {fehler} wurden angegeben, sind aber nicht wählbar!")

        st.write("Doppelte Wünsche werden gelöscht, d.h. wenn wunsch1 == wunsch3, wird wunsch3='' gesetzt.")
        for wunsch1, wunsch2 in combinations(wuensche,2):
            for i in range(len(wunsch1)):
                if wunsch1[i] == wunsch2[i]:
                    wunsch2[i] = ""

                # spalten sind die workshops der einzelnen Reihen, jede Spalte ist ein Platz im Workshop
        if st.session_state.fixed_seed:
            random.seed(42)
        spalten = []
        for p in st.session_state.pruefer:
            spalten.extend([(p["Kurzname"], "Analysis") for i in range(p['SlotsAna'])])
            spalten.extend([(p["Kurzname"], "Lineare Algebra") for i in range(p['SlotsLA'])])
            random.shuffle(spalten)

        kostenMatrix = np.zeros((df.shape[0], len(spalten)))
        for i in range(kostenMatrix.shape[0]):
            for j in range(kostenMatrix.shape[1]):
                offset = 4*(df["Fach"][i] != spalten[j][1]) 
                kostenMatrix[i,j] = float(kosten[offset + 3])
                for w in range(len(wuensche)):
                    if wuensche[w][i] == spalten[j][0]:
                        kostenMatrix[i,j] = float(kosten[offset + w])

        row_ind, col_ind = linear_sum_assignment(kostenMatrix, maximize=False)
        df["Prüfer"] = [spalten[j][0] for j in col_ind]


        st.write("Hier das Ergebnis der Einteilung:")

        for stu1, stu2 in combinations(df.iterrows(), 2):
            if stu1[1]["Matr"] == stu2[1]["Matr"]:
                st.write(f"{stu1[1]['Name']}, {stu1[1]['Vorname']} ({stu1[1]['Matr']}) hat sich zu Prüfungen in {stu1[1]['Fach']} und {stu2[1]['Fach']} angemeldet. Prüfer sind {stu1[1]['Prüfer']} und {stu2[1]['Prüfer']}.")    
        
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


if wuensche_xls:
    with st.expander("Prüferbelastung"):
        anzahl_pruefungen = [sum(df["Prüfer"] == p["Kurzname"]) for p in st.session_state.pruefer]
#        st.write(anzahl_pruefungen)
        max_anzahl = max(anzahl_pruefungen)
        for i, p in enumerate(st.session_state.pruefer):
            col = st.columns([2,1,2])
            col[0].write(f"{p['Vorname']} {p['Nachname']}")
            with col[1]:
                fill_percentage = (anzahl_pruefungen[i])/max_anzahl * 100  # Füllstand in Prozent
                # HTML und CSS für den Balken
                st.markdown(f"""
                <div style="width: {bar_length}px; background-color: #ddd; border-radius: 5px; overflow: hidden;">
                    <div style="width: {fill_percentage}%; background-color: #4caf50; height: 20px;"></div>
                </div>
                """, unsafe_allow_html=True)
                st.markdown(anzahl_pruefungen[i])
            with col[2]:
                df_loc = df[df["Prüfer"] == p["Kurzname"]]
                if sum(df_loc["Fach"] == "Analysis") > p["SlotsAna"]:
                    st.write(f"{sum(df_loc["Fach"] == "Analysis")} Prüfungen in Analysis eingeteilt, wollte aber nur {p["SlotsAna"]}.")

                if sum(df_loc["Fach"] == "Lineare Algebra") > p["SlotsLA"]:
                    st.write(f"{sum(df_loc["Fach"] == "Lineare Algebra")} Prüfungen in Analysis eingeteilt, wollte aber nur {p["SlotsLA"]}.")

