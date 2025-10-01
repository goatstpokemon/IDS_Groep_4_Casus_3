import streamlit as sl
import pandas as pd

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

# Explore data
print(schedule_airport.info())

#Verschillende maatschappijen
schedule_airport['UNQ'] = schedule_airport['FLT'].astype(str).str[:2]
print(schedule_airport['UNQ'].value_counts().reset_index())


# Top 5 van Netwerkkaart maken
top5 = schedule_airport['UNQ'].unique()
sl.selectbox("Select a Airline:", top5)
