import pandas as pd
from datetime import datetime, timedelta
import streamlit as st
import numpy as np
import folium
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
image_url = "https://media.myswitzerland.com/image/fetch/c_lfill,g_auto,w_3200,h_1800/f_auto,q_80,fl_keep_iptc/https://www.myswitzerland.com/-/media/st/gadmin/images/partner/strapa/flughafen%20zrich/03_airport_zurich_plane_92626.jpg"

st.markdown(
    """
    <style>
      .image-overlay-container {
        position: relative;
        width: 100%;
        max-width: 100%;
        border-radius: 20px;
        line-height: 0; /* remove whitespace gap below images */
      }
      .image-overlay-container img {
        width: 100%;
        height: auto;
        max-height: 400px;
        object-fit: cover;
        border-radius: 20px;
        display: block;
      }
      .overlay-text {
        position: absolute;
        inset: 0; /* shorthand for top:0; right:0; bottom:0; left:0; */
        display: flex;
        align-items: center; /* vertical centering */
        justify-content: center; /* horizontal centering */
        padding: 1rem;
        color: white;
        font-weight: 500;
        font-family: 'Helvetica Neue', sans-serif;
        font-size: 2.5rem;
        letter-spacing: 1px;
        text-align: center;
        text-shadow: 0 2px 8px rgba(0,0,0,0.6);
        pointer-events: none; /* clicks pass through if needed */
      }
      /* Optional: add a dark gradient for contrast */
      .overlay-gradient::before {
        content: "";
        position: absolute;
        border-radius: 20px;
        inset: 0;
        background: linear-gradient(
          to bottom,
          rgba(0,0,0,0.4),
          rgba(0,0,0,0.2) 40%,
          rgba(0,0,0,0.5)
        );
        z-index: 0;
      }
      .overlay-text > span {
        position: relative;
        z-index: 1;
      }
    </style>
    <div class="image-overlay-container overlay-gradient">
      <img src='""" + image_url + """' alt="Hero" />
      <div class="overlay-text">
        <span>Zurich Airport — Hoeveel vliegtuigen zijn er op de grond?</span>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)
# === Data inladen ===
SA = pd.read_csv('data/schedule_airport.csv')
SADF = pd.DataFrame(SA)
st.logo('https://companieslogo.com/img/orig/FHZN.SW_BIG.D-79fb25dc.png?t=1720244491')
st.set_page_config(layout="wide")

SADF["date"] = pd.to_datetime(SA["STD"], format="%d/%m/%Y")
SADF["ATA_ATD_ltc"] = pd.to_datetime(SA["ATA_ATD_ltc"], format="%H:%M:%S").dt.time
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
day_SADFI = SADF[(SADF['LSV'] == 'L') & (SADF["date"] == pd.Timestamp(selected_datum))].copy()
day_SADFO = SADF[(SADF['LSV'] == 'S') & (SADF["date"] == pd.Timestamp(selected_datum))].copy()

if day_SADFI.empty and day_SADFO.empty:
    st.warning(f"Geen vluchten gevonden voor {selected_datum}.")
else:
    # Maak tijdstappen van 10 minuten
    start_tijd = pd.Timestamp(selected_datum)
    eind_tijd = start_tijd + timedelta(days=1)
    times = pd.date_range(start=start_tijd, end=eind_tijd, freq="10min")

    initial_on_ground = 40

    # Fast searchsorted approach
    day_SADFI_sorted = day_SADFI["WT"].sort_values().values
    day_SADFO_sorted = day_SADFO["WT"].sort_values().values

    arrivals_count = np.searchsorted(day_SADFI_sorted, times, side='right')
    departures_count = np.searchsorted(day_SADFO_sorted, times, side='right')
    ground_counts = initial_on_ground + arrivals_count - departures_count

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