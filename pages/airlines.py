import streamlit as sl
import pandas as pd
import numpy as np
import folium

sl.title('Bekijk vliegtuigmaatschapijen')
sl.set_page_config(layout="wide")
sl.logo('https://companieslogo.com/img/orig/FHZN.SW_BIG.D-79fb25dc.png?t=1720244491')
schedule_airport = pd.read_csv("data/schedule_airport.csv")
airports_locaties = pd.read_csv("data/airports-extended-clean.csv", sep=";")
airlines = pd.read_csv("data/airlines.csv")

# Filter op ICAO-codes die in beide datasets voorkomen
airports_locaties_filtered = airports_locaties[
    airports_locaties["ICAO"].isin(schedule_airport["Org/Des"])
]

# Bepaal maatschappijcode (eerste 2 karakters van vluchtcode)
schedule_airport["UNQ"] = schedule_airport["FLT"].astype(str).str[:2]

# Selecteer maatschappij via Streamlit
airlineList = schedule_airport["UNQ"].unique()
selectedAirline = sl.selectbox("Selecteer een Vliegtuigmaatschapij:", airlineList)


# Haal alle vluchten op voor gekozen maatschappij (geeft indices terug)
def getAllFlightAirline(airline: str):
    # Retourneert een tuple met indexen waar UNQ gelijk is aan airline
    return np.where(schedule_airport["UNQ"] == airline)


flights = getAllFlightAirline(selectedAirline)


def getAirlineName(airline_code: str):
    # Haal naam op uit airlines.csv, anders 'Unknown Airline'
    return np.where(
        airlines[airlines["IATA"] == airline_code]["Name"],
        airlines[airlines["IATA"] == airline_code]["Name"],
        "Unknown Airline",
    )[0]


sl.header(getAirlineName(selectedAirline))


# Tel bestemmingen (ICAO) voor de gekozen vluchten
def getDestinationAirport(flightIndices):
    # flightIndices is een tuple van numpy.where; gebruik deze direct in iloc
    return (
        schedule_airport.iloc[flightIndices]["Org/Des"]
        .value_counts()
        .reset_index()
    )


destinations = getDestinationAirport(flights)

sl.header("Aantal vluchten per bestemming")
sl.write(destinations)


# Vind locaties (lat/lon) van bestemmingsluchthavens
def getLocationDestinationAirport(destinations_input):
    # Ondersteunt zowel DataFrame (van value_counts()   reset_index()) als lijst/Series
    if isinstance(destinations_input, pd.DataFrame):
        # Standaardkolom van value_counts().reset_index() is 'index'
        if "index" in destinations_input.columns:
            codes = destinations_input["index"]
        else:
            # Valt terug op de eerste kolom indien anders benoemd
            codes = destinations_input.iloc[:, 0]
    else:
        codes = destinations_input

    return airports_locaties_filtered[
        airports_locaties_filtered["ICAO"].isin(codes)
    ]


locations = getLocationDestinationAirport(destinations)
sl.write(locations)


# Maak een Folium-kaart met markers voor elke bestemming
def createMap(locations_df: pd.DataFrame):
    # Start kaart, gecentreerd op Nederland
    m = folium.Map(location=[52.1326, 5.2913], zoom_start=4)

    # Voeg markers toe; sta komma-decimalen en missende waarden toe
    for _, row in locations_df.iterrows():
        lat_raw = row.get("Latitude", None)
        lon_raw = row.get("Longitude", None)

        if pd.isna(lat_raw) or pd.isna(lon_raw):
            continue

        try:
            lat = float(str(lat_raw).replace(",", "."))
            lon = float(str(lon_raw).replace(",", "."))
        except (ValueError, TypeError):
            # Sla rijen met ongeldige coördinaten over
            continue

        popup_text = f"{row.get('City', '')} ({row.get('ICAO', '')})"
        folium.Marker(
            location=[lat, lon],
            popup=popup_text,
            icon=folium.Icon(color="blue", icon="plane", prefix="fa"),
        ).add_to(m)

    return m


map_ = createMap(locations)

# Render Folium-kaart in Streamlit
sl.components.v1.html(map_._repr_html_(), height=600)
