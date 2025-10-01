
import streamlit as sl
import pandas as pd


def main_page():
    sl.markdown("# Homepagina ")


def page2():
    sl.markdown("# Pagina 2 ")


page_names_to_funcs = {
    "Homepagina": main_page,
    "Alle Locaties": page2

}
selected_page = sl.sidebar.selectbox("Select a page", page_names_to_funcs.keys())
page_names_to_funcs[selected_page]()











