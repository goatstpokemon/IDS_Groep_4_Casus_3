import streamlit as sl
import pandas as pd
import numpy as np
import folium
import plotly.express as px
# Data inladen
s = pd.read_csv("data/schedule_airport.csv")
airports = pd.read_csv("data/airports.csv")
airlines = pd.read_csv("data/airlines.csv")

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
        <span>Zurich Airport — Home</span>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

sl.header('Belangrijke statistieken')
s["UNQ"] = s["FLT"].astype(str).str[:2]
airlinesUnique = s["UNQ"].unique()
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
    sl.subheader(f"{len(airlinesUnique)}")
with col5:
    sl.text("Unieke bestemmingen")
    sl.subheader(f"{s['Org/Des'].nunique()}")

df = pd.read_csv("data/schedule_airport.csv")

# Parse datetime and filter to 2019
df['STD_dt'] = pd.to_datetime(df['STD'], dayfirst=True, errors='coerce')
#kies jaar

jaar = sl.selectbox("Kies een jaar", options=[2019, 2020], key="jaar_selectie", index=0)


def color_band(value):
    if value >= 19000:
        return "≥19000"
    if value >= 15000:
        return "≥15000"
    if value >= 10000:
        return "≥10000"
    if value >= 5000:
        return "≥5000"
    return "<5000"
#grafiek die aantal vluchten per maand laat zien
sl.header(f'Aantal vluchten per maand ({jaar})')
flights_per_month = (
  df.loc[df['STD_dt'].dt.year == jaar, 'STD_dt']
    .dt.month
    .value_counts()
    .reindex(range(1, 13), fill_value=0)
    .sort_index()
)

data = pd.DataFrame(
    {
        "month": flights_per_month.index,
        "flights": flights_per_month.values,
    }
)
data["band"] = data["flights"].apply(color_band)
band_colors = {
    "≥19000": "indianred",
    "≥15000": "red",
    "≥10000": "darkorange",
    "≥5000": "gold",
    "<5000": "yellowgreen",
}


fig = px.bar(
    data,
    x="month",
    y="flights",
    color="band",
    category_orders={"band": list(band_colors.keys())},
    color_discrete_map=band_colors,
    labels={"month": "Maand", "flights": "Vluchten", "band": "Drukte"},
)

fig.update_layout(
    bargap=0.2,
    width=800,
    height=400,
    legend_title_text="Drukte",
)
fig.update_xaxes(dtick=1)

sl.plotly_chart(fig, use_container_width=True)


#tabel die top 10 bestemmingen laat zien
departures = s[s['LSV']== 'S']
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

sl.header("Top 10 destinations Zürich Airport")
sl.write(top_10_destinations)

# Top 10 bestemmingen met de meeste vluchten
#s["UNQ"] = s["FLT"].astype(str).str[:2]
#top_10_airlines = s['FLT'].value_counts().head(10).reset_index()
#print(top_10_airlines)

# Maak een nieuwe kolom 'Airline' door de eerste twee karakters
        # van de 'FLT' kolom te nemen. Dit is de IATA-code van de maatschappij.

s["Airline"] = s["FLT"].astype(str).str[:2]


# Tel het aantal voorkomens van elke unieke airline code.
top_airlines = s['Airline'].value_counts()

# Pak de top 10 van deze airlines.
top_10_airlines = top_airlines.head(10)

# Print de resultaten naar de console.
#print("Top 10 meest voorkomende vluchtcodes (Airlines):")
print(top_10_airlines)

#print(airlines['IATA'].head())
#namen = []
#for code in s['FLT']:
    # np.where zoekt de index waar de code matcht in de IATA kolom

    #match_index = np.where(airlines['IATA'] == code)

    #if len(match_index[0]) > 0:
        #naam = airlines['Name'].iloc[match_index[0][0]]
    #else:
        #naam = None # Geen match gevonden
    #namen.append(naam)

#top_10_destinations['Airline'] = namen
sl.header("Top 10 airlines Zürich Airport")
sl.write(top_10_airlines)