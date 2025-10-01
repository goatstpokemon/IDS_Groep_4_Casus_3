import streamlit as sl
import pandas as pd
import numpy as np
elke_s_flight_1 = pd.read_excel('data/30sFlight_1.xlsx')
elke_s_flight_2 = pd.read_excel('data/30sFlight_2.xlsx')
elke_s_flight_3 = pd.read_excel('data/30sFlight_3.xlsx')
elke_s_flight_4 = pd.read_excel('data/30sFlight_4.xlsx')
elke_s_flight_5 = pd.read_excel('data/30sFlight_5.xlsx')
elke_s_flight_6 = pd.read_excel('data/30sFlight_6.xlsx')
schedule_airport = pd.read_csv('data/schedule_airport.csv')


def main_page():
    sl.markdown("# Homepagina ")


def page2():
    sl.markdown("# Pagina 2")

# Dropping nutteloze data
# schedule_airport.drop('DL1', inplace=True, axis=1)
# schedule_airport.drop('DL2', inplace=True, axis=1)
# schedule_airport.drop('IX1', inplace=True, axis=1)
# schedule_airport.drop('IX2', inplace=True, axis=1)
# print(schedule_airport.head())

# Filteren op ICAO codes die voorkomen in beide
airports_locaties_filtered = airports_locaties[
    airports_locaties['ICAO'].isin(schedule_airport['Org/Des'])
]

# Explore data
# print(schedule_airport.info())

#Verschillende maatschappijen
schedule_airport['UNQ'] = schedule_airport['FLT'].astype(str).str[:2]
print(schedule_airport['UNQ'].value_counts().reset_index())


# Top 5 van Netwerkkaart maken
airlineList = schedule_airport['UNQ'].unique()
selectedAirline = sl.selectbox("Select a Airline:", airlineList)

# Functie voor het ophalen van alle vluchten
def getAllFlightAirline(airline):
    return np.where(schedule_airport['UNQ'] == airline)

flights = getAllFlightAirline(selectedAirline)

# Vliegveld bestemming vinden op basis van flucht
def getDestinationAirport(flightIndices):
    return schedule_airport.iloc[flightIndices]['Org/Des'].value_counts().reset_index()

destinations = getDestinationAirport(flights)
sl.write(destinations)

# pulmizukil