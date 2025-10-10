import streamlit as sl
import pandas as pd
import numpy as np
import folium
import plotly.express as px
import requests

image_url = "https://media.myswitzerland.com/image/fetch/c_lfill,g_auto,w_3200,h_1800/f_auto,q_80,fl_keep_iptc/https://www.myswitzerland.com/-/media/st/gadmin/images/partner/strapa/flughafen%20zrich/03_airport_zurich_plane_92626.jpg"

sl.markdown(
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
        <span>Live vluchtgegevens</span>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)
sl.set_page_config(layout="wide")
sl.logo("https://companieslogo.com/img/orig/FHZN.SW_BIG.D-79fb25dc.png?t=1720244491")

# Load data
flight_1s = pd.read_excel("data/30sFlight_1.xlsx")
flight_2s = pd.read_excel("data/30sFlight_2.xlsx")
flight_3s = pd.read_excel("data/30sFlight_3.xlsx")
flight_4s = pd.read_excel("data/30sFlight_4.xlsx")
flight_5s = pd.read_excel("data/30sFlight_5.xlsx")
flight_6s = pd.read_excel("data/30sFlight_6.xlsx")
flight_7s = pd.read_excel("data/30sFlight_7.xlsx")

sl.title("Live Flight Data ")

sl.text("""
Hieronder is de live vluchtdata te zien van een vlucht tussen Schiphol en Barcelona.
""")

df_flight_1s = pd.DataFrame(flight_1s)
df_flight_2s = pd.DataFrame(flight_2s)
df_flight_3s = pd.DataFrame(flight_3s)
df_flight_4s = pd.DataFrame(flight_4s)
df_flight_5s = pd.DataFrame(flight_5s)
df_flight_6s = pd.DataFrame(flight_6s)
df_flight_7s = pd.DataFrame(flight_7s)
dfs = [
    ("flight_1", df_flight_1s),
    ("flight_2", df_flight_2s),
    ("flight_3", df_flight_3s),
    ("flight_4", df_flight_4s),
    ("flight_5", df_flight_5s),
    ("flight_6", df_flight_6s),
    ("flight_7", df_flight_7s),
]
df_flights = pd.concat(
    [d.assign(flight_id=label) for label, d in dfs], ignore_index=True
)


colors = px.colors.qualitative.Dark24
# vergelijk duur van de vlucht
# get flight of all flights on the y axis and duration on the x axis
fig = px.line(
    df_flights,
    x="Time (secs)",
    y="[3d Altitude Ft]",
    color="flight_id",  # <-- key part
    color_discrete_sequence=None,  # let Plotly pick, or provide your own
    title="Hoogte van de vlucht over tijd",
)
sl.plotly_chart(fig, use_container_width=True)

# vergelijk snelheid van de vlucht
fig2 = px.line(
    df_flights,
    x="Time (secs)",
    y="TRUE AIRSPEED (derived)",
    color="flight_id",  # <-- key part
    color_discrete_sequence=None,  # let Plotly pick, or provide your own
    title="Snelheid van de vlucht over tijd",
)
sl.plotly_chart(fig2, use_container_width=True)
