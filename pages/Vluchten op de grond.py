import pandas as pd
from datetime import datetime, timedelta
import streamlit as st
import numpy as np
import folium
import matplotlib.pyplot as plt
import matplotlib.dates as mdates  # ⬅️ toegevoegd

# === Data inladen ===
SA = pd.read_csv('data/schedule_airport.csv')
SADF = pd.DataFrame(SA)

SADF["date"] = pd.to_datetime(SA["STD"], format="%d/%m/%Y")
# SADF["STA_STD_ltc"] = pd.to_datetime(SA["STA_STD_ltc"], format="%H:%M:%S").dt.time
SADF["ATA_ATD_ltc"] = pd.to_datetime(SA["ATA_ATD_ltc"], format="%H:%M:%S").dt.time

# SADF["STA_STD_ltc"] = SADF.apply(lambda x: datetime.combine(x["date"], x["STA_STD_ltc"]), axis=1)
SADF["WT"] = SADF.apply(lambda x: datetime.combine(x["date"], x["ATA_ATD_ltc"]), axis=1)

# === Datum selectie ===
min_date, max_date = SADF["date"].min().date(), SADF["date"].max().date()
selected_datum = st.date_input(
    "Selecteer een datum",
    min_value=min_date,
    max_value=max_date,
    value=min_date
)

# Data filteren
# SADFI = np.where(SADF['LSV'] == 'L') 
# SADFO = np.where(SADF['LSV'] == 'S') 
SADFI = SADF[SADF['LSV'] == 'L'].copy()
SADFO = SADF[SADF['LSV'] == 'S'].copy()

# Filter data op geselecteerde datum
day_SADF = SADF[SADF["date"] == pd.Timestamp(selected_datum)]

if day_SADF.empty:
    st.warning(f"Geen vluchten gevonden voor {selected_datum}.")
else:
    # Maak tijdstappen van 15 minuten
    start_tijd = SADF["WT"].min()
    eind_tijd = SADF["WT"].max()
    
    times = pd.date_range(start=start_tijd, end=eind_tijd, freq="10min")

    ground_counts = []
    on_ground = 40      #zoals in voorbeeld

    for time in times:
        on_ground += (SADFI["WT"] <= time).sum()
        SADFI = SADFI[SADFI["WT"] > time]

        on_ground -= (SADFO["WT"] <= time).sum()
        SADFO = SADFO[SADFO["WT"] > time]

        ground_counts.append(on_ground)

    ground_counts = []

    # # Tel vliegtuigen op de grond per tijdstap
    # for t in times:
    #     on_ground = 40              #zoals in voorbeeld
    #     for _, row in day_SADF.iterrows():
    #         if row["LSV"] == "L":
    #             if row["ATA_ATD_ltc"] <= t < row["STA_STD_ltc"]:
    #                 on_ground += 1
    #         elif row["LSV"] == "S":
    #             if row["ATA_ATD_ltc"] > t:
    #                 on_ground += 1
    #     ground_counts.append(on_ground)

