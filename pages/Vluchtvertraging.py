import streamlit as st
import pandas as pd
import numpy as np
import folium
import matplotlib.pyplot as plt

@st.cache_data
def load_data():
    schedule_airport = pd.read_csv("data/schedule_airport.csv", sep=",", low_memory=False)
    airports = pd.read_csv("data/airports-extended-clean.csv", sep=";", low_memory=False)
    airlines = pd.read_csv("data/airlines.csv", sep=",", low_memory=False)

    # Komma’s in coördinaten vervangen door punten
    airports['Latitude'] = airports['Latitude'].astype(str).str.replace(',', '.').astype(float)
    airports['Longitude'] = airports['Longitude'].astype(str).str.replace(',', '.').astype(float)

    return schedule_airport, airports, airlines


# ===== Data inladen =====
schedule_airport, airports, airlines = load_data()

# Relevante kolommen
kolommen = ['STD', 'FLT', 'STA_STD_ltc', 'ATA_ATD_ltc', 'LSV', 'Org/Des']
schedule_airport = schedule_airport[kolommen].copy()

# Tijden converteren
schedule_airport['STA_STD_ltc'] = pd.to_datetime(schedule_airport['STA_STD_ltc'], errors='coerce')
schedule_airport['ATA_ATD_ltc'] = pd.to_datetime(schedule_airport['ATA_ATD_ltc'], errors='coerce')

# Luchtvaartmaatschappijcode (eerste 2 tekens)
schedule_airport["UNQ"] = schedule_airport["FLT"].astype(str).str[:2]

# Vertraging berekenen in minuten
schedule_airport['Vertraging (min)'] = (
    schedule_airport['ATA_ATD_ltc'] - schedule_airport['STA_STD_ltc']
).dt.total_seconds() / 60

# Filter geldige data
schedule_airport = schedule_airport[
    (schedule_airport['Vertraging (min)'].notna()) &
    (schedule_airport['LSV'] == 'S') &
    (schedule_airport['Vertraging (min)'] >= 0)
]

# Bestemmingenlijst
bestemmingen = sorted(schedule_airport['Org/Des'].dropna().unique())
gekozen_bestemming = st.selectbox("Kies een bestemming", bestemmingen)

# Filter op gekozen bestemming
df_bestemming = schedule_airport[schedule_airport['Org/Des'] == gekozen_bestemming]

# === Gemiddelde vertraging + aantal vluchten per maatschappij ===
vertraging_per_maatschappij = (
    df_bestemming.groupby('UNQ')
    .agg({
        'Vertraging (min)': 'mean',
        'FLT': 'count'  # aantal vluchten
    })
    .reset_index()
    .rename(columns={
        'UNQ': 'IATA',
        'Vertraging (min)': 'Gemiddelde vertraging (min)',
        'FLT': 'Aantal vluchten'
    })
)

# Koppelen aan airlines.csv
airlines = airlines.rename(columns={col: col.strip() for col in airlines.columns})  # spaties verwijderen
vertraging_per_maatschappij = vertraging_per_maatschappij.merge(
    airlines[['IATA', 'Name']], on='IATA', how='left'
)

# Kolommen netjes ordenen
vertraging_per_maatschappij['Gemiddelde vertraging (min)'] = vertraging_per_maatschappij['Gemiddelde vertraging (min)'].astype(int)
vertraging_per_maatschappij = vertraging_per_maatschappij.sort_values(by='Gemiddelde vertraging (min)')
vertraging_per_maatschappij = vertraging_per_maatschappij[['Name', 'IATA', 'Aantal vluchten', 'Gemiddelde vertraging (min)']].rename(
    columns={'Name': 'Luchtvaartmaatschappij'}
)

# Tabel tonen
st.subheader(f"Gemiddelde vertraging en aantal vluchten per luchtvaartmaatschappij naar {gekozen_bestemming}")
st.dataframe(vertraging_per_maatschappij, use_container_width=True)

# ===== Kaart genereren =====
def maak_kaart(bestemming_code):
    zrh_lat, zrh_lon = 47.458, 8.555  # Zurich Airport
    kaart = folium.Map(location=[zrh_lat, zrh_lon], zoom_start=4)

    bestemming = airports[airports['ICAO'].str.upper() == bestemming_code.upper()]

    if not bestemming.empty:
        dest_lat = bestemming['Latitude'].values[0]
        dest_lon = bestemming['Longitude'].values[0]
        dest_name = bestemming['Name'].values[0]

        folium.Marker(
            location=[zrh_lat, zrh_lon],
            popup="Zurich Airport (ZRH)",
            icon=folium.Icon(color="blue")
        ).add_to(kaart)

        folium.Marker(
            location=[dest_lat, dest_lon],
            popup=f"{dest_name} ({bestemming_code})",
            icon=folium.Icon(color="red")
        ).add_to(kaart)

        folium.PolyLine(
            locations=[[zrh_lat, zrh_lon], [dest_lat, dest_lon]],
            color="green",
            weight=3,
            opacity=0.7
        ).add_to(kaart)

    return kaart


# ===== Kaart tonen =====
kaart = maak_kaart(gekozen_bestemming)
kaart.save("kaart.html")

st.subheader(f"Route van Zurich naar {gekozen_bestemming}")
st.components.v1.html(open("kaart.html", "r", encoding="utf-8").read(), height=500)
