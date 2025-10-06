import streamlit as sl
import pandas as pd
import numpy as np
import folium

# Data inladen
elke_s_flight_1 = pd.read_excel("data/30sFlight_1.xlsx")
elke_s_flight_2 = pd.read_excel("data/30sFlight_2.xlsx")
elke_s_flight_3 = pd.read_excel("data/30sFlight_3.xlsx")
elke_s_flight_4 = pd.read_excel("data/30sFlight_4.xlsx")
elke_s_flight_5 = pd.read_excel("data/30sFlight_5.xlsx")
elke_s_flight_6 = pd.read_excel("data/30sFlight_6.xlsx")


def main_page():
    # Hoofdpagina titel
    sl.markdown("# Homepagina ")


def page2():
    # Tweede pagina titel
    sl.markdown("# Bekijk vliegmaatschapijen")



