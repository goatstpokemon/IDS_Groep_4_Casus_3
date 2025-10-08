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
day_SADFI = SADF[(SADF['LSV'] == 'L') & (SADF["date"] == pd.Timestamp(selected_datum))].copy()
day_SADFO = SADF[(SADF['LSV'] == 'S') & (SADF["date"] == pd.Timestamp(selected_datum))].copy()

if day_SADFI.empty and day_SADFO.empty:
    st.warning(f"Geen vluchten gevonden voor {selected_datum}.")
else:
    # Maak tijdstappen van 10 minuten for the selected day only
    start_tijd = pd.Timestamp(selected_datum)
    eind_tijd = start_tijd + timedelta(days=1)

    times = pd.date_range(start=start_tijd, end=eind_tijd, freq="10min")

    ground_counts = []
    initial_on_ground = 40  # Starting count

    for time in times:
        # Count arrivals (landed by this time)
        arrivals = (day_SADFI["WT"] <= time).sum()
        # Count departures (departed by this time)
        departures = (day_SADFO["WT"] <= time).sum()

        on_ground = initial_on_ground + arrivals - departures
        ground_counts.append(on_ground)

    # Plot
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(times, ground_counts, linewidth=2)
    ax.set_xlabel("Tijd")
    ax.set_ylabel("Vliegtuigen op de grond")
    ax.set_title(f"Aantal vliegtuigen op de grond - {selected_datum}")
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    ax.xaxis.set_major_locator(mdates.HourLocator(interval=2))
    plt.xticks(rotation=45)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    st.pyplot(fig)