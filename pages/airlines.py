import streamlit as sl
import pandas as pd
import numpy as np
import folium
from folium.features import DivIcon
from branca.colormap import LinearColormap
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
        flex-direction: column;
        height: 100%;
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
        <span>vliegtuigmaatschapijen bestemmingen</span>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)
sl.set_page_config(page_title="Luchtvaartmaatschappijen", layout="wide")


# === DATA INLADEN ===
schedule_airport = pd.read_csv("data/schedule_airport.csv")
airports_locaties = pd.read_csv("data/airports-extended-clean.csv", sep=";")
airlines = pd.read_csv("data/airlines.csv")

# Check of ICAO kolom bestaat
if "ICAO" not in airports_locaties.columns:
    sl.error("De kolom 'ICAO' ontbreekt in airports-extended-clean.csv")
    sl.stop()

# Maatschappijcode (eerste 2 karakters)
schedule_airport["UNQ"] = schedule_airport["FLT"].astype(str).str[:2]

# Selectie maatschappij
airlineList = sorted(schedule_airport["UNQ"].unique())
selectedAirline = sl.selectbox("Selecteer een luchtvaartmaatschappij:", airlineList)

# Functie om naam op te halen
def getAirlineName(airline_code: str):
    row = airlines[airlines["IATA"] == airline_code]
    if not row.empty:
        return row.iloc[0]["Name"]
    return f"Onbekende maatschappij ({airline_code})"

sl.header(getAirlineName(selectedAirline))

# Vluchten voor gekozen maatschappij
flight_indices = np.where(schedule_airport["UNQ"] == selectedAirline)
destinations = (
    schedule_airport.iloc[flight_indices]["Org/Des"]
    .value_counts()
    .reset_index()
)
destinations.columns = ["ICAO", "Aantal Vluchten"]

sl.subheader("Aantal vluchten per bestemming")
sl.dataframe(destinations, use_container_width=True)

# Locaties ophalen
airports_locaties_filtered = airports_locaties[
    airports_locaties["ICAO"].isin(destinations["ICAO"])
]

# Aantal vluchten toevoegen aan locaties
locations = airports_locaties_filtered.merge(destinations, on="ICAO", how="left")

# === Kleuren instellen (pastel groen -> pastel rood) ===
min_val = locations["Aantal Vluchten"].min()
max_val = locations["Aantal Vluchten"].max()

colormap = LinearColormap(
    colors=["#b6e2b6", "#f4e5af", "#f4c27f", "#f49b7a", "#e57373"],
    vmin=min_val,
    vmax=max_val
)

def kleur_schaal(count):
    return colormap(count)

# === KAART MAKEN ===
def createMap(locations_df: pd.DataFrame):
    m = folium.Map(location=[52.1326, 5.2913], zoom_start=4)

    for _, row in locations_df.iterrows():
        lat_raw = row.get("Latitude", None)
        lon_raw = row.get("Longitude", None)
        if pd.isna(lat_raw) or pd.isna(lon_raw):
            continue

        try:
            lat = float(str(lat_raw).replace(",", "."))
            lon = float(str(lon_raw).replace(",", "."))
        except (ValueError, TypeError):
            continue

        count = int(row["Aantal Vluchten"])
        kleur = kleur_schaal(count)
        popup_text = f"<b>{row.get('City', '')}</b> ({row.get('ICAO', '')})<br>Aantal vluchten: {count}"

        html = f"""
        <div style="position: relative; text-align: center; transform: translate(-50%, -100%);">
            <div style="
                background: {kleur};
                color: black;
                padding: 4px 10px;
                border-radius: 50px;
                font-size: 12px;
                font-weight: bold;
                min-width: 30px;
                display: inline-block;
                box-shadow: 0px 0px 4px rgba(0,0,0,0.3);
                ">
                {count}
            </div>
            <div style="
                width: 0;
                height: 0;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 8px solid {kleur};
                margin: 0 auto;
                ">
            </div>
        </div>
        """

        folium.Marker(
            location=[lat, lon],
            popup=popup_text,
            icon=DivIcon(
                icon_size=(30, 30),
                icon_anchor=(0, 0),
                html=html,
            )
        ).add_to(m)

    # === Legenda ===
    legenda_steps = 5
    step_values = np.linspace(min_val, max_val, legenda_steps, dtype=int)

    kleurblokken = ""
    for val in step_values:
        kleurblokken += f"""
            <div style="display:flex;align-items:center;margin-bottom:4px;">
                <div style="width:20px;height:20px;background:{kleur_schaal(val)};margin-right:8px;border:1px solid #ccc;"></div>
                <span style="font-size:12px;">{val} vluchten</span>
            </div>
        """

    legenda_html = f"""
    <div style="
     position: fixed;
     top: 30px;
     right: 30px;
     width: 200px;
     background-color: white;
     border:2px solid #eee;
     z-index:9999;
     font-size:14px;
     padding: 10px;
     border-radius: 8px;
     ">
     <b>Kleurenschaal</b><br>
     <small>Groen = weinig vluchten<br>Rood = veel vluchten</small>
     <hr>
     {kleurblokken}
    </div>
    """
    m.get_root().html.add_child(folium.Element(legenda_html))

    return m

# === Bestemmingen sectie ===
sl.subheader(f"Bestemmingen van {getAirlineName(selectedAirline)}")

sl.markdown("""
**Uitleg kaart**
- Elke pointer op de kaart geeft een luchthaven weer waar de maatschappij naartoe vliegt.
- De kleur geeft het aantal vluchten aan (groen = weinig, rood = veel).
- Klik op een pointer om de stad en ICAO-code te zien.

""")

map_ = createMap(locations)
sl.components.v1.html(map_._repr_html_(), height=750)
