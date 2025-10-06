import streamlit as sl
import pandas as pd
import numpy as np
import folium

# Data inladen
s = pd.read_csv("data/schedule_airport.csv")

def add_logo():
    sl.markdown(
        """
        <style>


            [data-testid="stSidebarNav"]::before {
                content: "Pagina's";
                text-align: center;
                font-family: 'helvetica', sans-serif;
                color: white;
                font-weight: bold;
                font-size: 25px;
                position: relative;


            }
        </style>
        """,
        unsafe_allow_html=True,
    )
add_logo()

def main_page():
    # Hoofdpagina titel
    sl.markdown("# Homepagina ")


def page2():
    # Tweede pagina titel
    sl.markdown("# Bekijk vliegmaatschapijen")
sl.set_page_config(layout="wide")
sl.logo('https://companieslogo.com/img/orig/FHZN.SW_BIG.D-79fb25dc.png?t=1720244491')


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
        <span>Zurich Airport — Dashboard Home</span>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

sl.header('Belangrijke statistieken')
s["UNQ"] = s["FLT"].astype(str).str[:2]
airlines = s["UNQ"].unique()
col1, col2, col3, col4, col5 = sl.columns(5, border=True)

with col1:
    sl.text("Totaal aantal vluchten")
    sl.subheader(f"{len(s)}")
with col2:
    sl.text("Aantal inbound")
    sl.subheader(f"{s[s['LSV'] == 'S'].shape[0]}")
with col3:
    sl.text("Aantal outbound")
    sl.subheader(f"{s[s['LSV'] == 'L'].shape[0]}")
with col4:
    sl.text("Unieke vliegmaatschappijen")
    sl.subheader(f"{len(airlines)}")
with col5:
    sl.text("Unieke bestemmingen")
    sl.subheader(f"{s['Org/Des'].nunique()}")

df = pd.read_csv("data/schedule_airport.csv")
#grafiek die aantal vluchten per maand laat zien
sl.header('Aantal vluchten per maand')
df['fpm'] = pd.to_datetime(df['STD'], format='%d/%m/%Y', errors='coerce').dt.month
flights_per_month = df['fpm'].value_counts().sort_index() / 2

sl.bar_chart(flights_per_month.reindex(range(1, 13), fill_value=0))