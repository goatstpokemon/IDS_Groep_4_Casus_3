import streamlit as sl
import pandas as pd
import numpy as np
import folium

import pandas as pd

# CSV-bestand inladen
schedule_airport = pd.read_csv("data/schedule_airport.csv")
airports = pd.read_csv("data/airports.csv")
# Kolomnamen bekijken (om te weten hoe bestemmingen en frequentie heten)
print(schedule_airport.columns)

departures = schedule_airport[schedule_airport['LSV']== 'S']
# Top 10 bestemmingen met de meeste vluchten
top_10_destinations = departures['Org/Des'].value_counts().head(10).reset_index()

#print(top_10_destinations)


namen = []
for code in top_10_destinations['Org/Des']:
    # np.where zoekt de index waar de code matcht in de ICAO kolom
    match_index = np.where(airports['ICAO'] == code)

    if len(match_index[0]) > 0:
        naam = airports['Name'].iloc[match_index[0][0]]
    else:
        naam = None # Geen match gevonden
    namen.append(naam)

top_10_destinations['Vliegveld Naam'] = namen

print(top_10_destinations)