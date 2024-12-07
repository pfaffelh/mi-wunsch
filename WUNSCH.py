import streamlit as st
import pandas as pd
from io import BytesIO
import numpy as np
import random
from itertools import combinations
from scipy.optimize import linear_sum_assignment
from config import *

st.set_page_config(page_title="Prüfungseinteilung", layout="centered")

# Es liegt eine xls-Datei vor mit Feldern
# Matr, Name, Vorname, Fach, wunsch1, wunsch2, wunsch3
# Ziel ist es, eine Spalten zu Ergänzungen: Zuteilung des Prüfers

# In config.py sind die Prüfer Workshops definiert. Der "name" gibt dabei jeweils den Workshop an

st.header("Einteilung der Prüfungen für Analysis und Lineare Algebra")

if "pruefer" not in st.session_state:
    st.session_state.pruefer = pruefer

def update_slots(i, fach, n):
    if fach == "Analysis":
        st.session_state.pruefer[i]["SlotsAna"] = st.session_state[f"{st.session_state.pruefer[i]["Kurzname"]}_Ana_size"]
    elif fach == "Lineare Algebra": 
        st.session_state.pruefer[i]["SlotsLA"] = st.session_state[f"{st.session_state.pruefer[i]["Kurzname"]}_LA_size"]

with st.expander("Es werden folgende Prüfungsslots von den Prüfern angeboten"):
    
    col = st.columns([3,1,1,1])
    col[1].write("#### Analysis")
    col[2].write("#### Lineare Algebra")
    col[3].write("#### Summe")

    max_pr = max([p["SlotsAna"]+p["SlotsLA"] for p in st.session_state.pruefer])
    st.write(max_pr)
    for i, p in enumerate(st.session_state.pruefer):
        col = st.columns([2,1,1,1])
        col[0].write(f"{p['Vorname']} {p['Nachname']}")
        p['SlotsAna'] = col[1].number_input("Anzahl", min_value = 0, value = p['SlotsAna'], on_change = update_slots, key = f"{p["Kurzname"]}_Ana_size", label_visibility="collapsed")
        p['SlotsLA'] = col[2].number_input("Anzahl", min_value = 0, value = p['SlotsLA'], args = (i, "Lineare Algebra"), key = f"{p["Kurzname"]}_LA_size", label_visibility="collapsed")
        with col[3]:
            bar_length = 100  # Länge in Pixel
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

st.expander("Es liegen Anmeldungen in einer xls-Datei in Folgendem Format vor:")
df = pd.read_excel("anmeldungen_bsp.xlsx")
wuensche_xls = st.file_uploader("Upload Wünsche")
wuensche_xls = 'misc/studenten_data.xls'
st.write(df)

if wuensche_xls:
    df = pd.read_excel(wuensche_xls)
    df = df.drop_duplicates(subset='Nachname', keep='last')
    st.write(f"**Insgesamt gibt es {df.shape[0]} Anmeldungen.**")
    st.write("Nun wird die Einteilung vorgenommen.")

    dfAna = df[df["fach"] == "Analysis"]
    dfLA = df[df["fach"] == "Lineare Angebra"]
    
    for wr in st.session_state.workshopreihe:    
        with st.expander(f"Einteilung von {wr["name"]}"):
            if df.shape[1] > wr['groesse']:
                st.write(f"**Einteilung in {wr['name']} nicht möglich, da es {df.shape[1]} Anmeldungen, aber nur {wr['groesse']} Plätze gibt.**")
            else: 
                st.write(f"Einteilung in {wr['name']} möglich, es gibt genug Plätze.")

            # Diese Liste von Listen gibt die Wünsche der Teilnehmer 
            wuensche = [list(df[df.columns[i]]) for i in wr["wunschspalten"]]
            allewuensche = [item for sublist in wuensche for item in sublist]        
            # Wünsche müssen mit den Namen der Workshops übereinstimmen!
            w_namen = [w["name_kurz"] for w in wr["data"]]
            #st.write(allewuensche)
            #st.write(w_namen)
            fehler = [w for w in allewuensche if w not in w_namen]
            if len(fehler):
                st.warning(f"Wünsche {fehler} wurden angegeben, sind aber nicht wählbar!")

            # Doppelte Wünsche werden gelöscht:
            for wunsch1, wunsch2 in combinations(wuensche,2):
                for i in range(len(wunsch1)):
                    if wunsch1[i] == wunsch2[i]:
                        wunsch2[i] = ""

            # spalten sind die workshops der einzelnen Reihen, jede Spalte ist ein Platz im Workshop
            spalten = []
            for w in wr["data"]:
                spalten.extend([w['name_kurz'] for i in range(w['groesse'])])
            random.seed(42)
            random.shuffle(spalten)
            # Zunächst gehen wir von maximalen Kosten aus
            kosten = wr["kosten"][-1] + np.zeros((df.shape[0], len(spalten)))
            for i in range(kosten.shape[0]):
                for j in range(kosten.shape[1]):
                    for w in range(len(wuensche)):
                        if wuensche[w][i] == spalten[j]:
                            kosten[i,j] = float(wr["kosten"][w])
            row_ind, col_ind = linear_sum_assignment(kosten, maximize=False)

            df[f"Einteilung {wr["name"]}"] = [workshopname_dict[spalten[j]] for j in col_ind]
            df[f"Workshopname {wr["name"]}"] = [ workshop_dict[spalten[j]] for j in col_ind ]

            # Ein wenig Statistik
            for wunsch in wuensche:
                st.write(f"{wr["name"]}: {sum(df[f"Einteilung {wr["name"]}"] == [workshopname_dict[x] for x in wunsch])} Teilnehmer haben ihren Wunsch { wuensche.index(wunsch) + 1} bekommen.")
            for w in wr["data"]:
                st.write(f"Zu {w['name']} sind {sum(df[f"Einteilung {wr["name"]}"] == w["name"])} Teilnehmer eingeteilt.")
    st.write("Hier das Ergebnis der Einteilung:")
    st.write(df)

    output = BytesIO()
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

    # Streamlit-Button für den Download
    excel_data = to_excel(df)
    st.download_button(
        label="Download Excel-Datei",
        data=excel_data,
        file_name="anmeldungen.xls",
        mime="application/vnd.ms-excel"
    )
