import streamlit as st
import pandas as pd
import numpy as np
import folium
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(layout="wide")
st.logo('https://companieslogo.com/img/orig/FHZN.SW_BIG.D-79fb25dc.png?t=1720244491')

st.title("Analyse van vluchtvertragingen per luchtvaartmaatschappij")

st.markdown("""
Op deze pagina wordt informatie weergegeven over vertragingen per luchtvaartmaatschappij.

- Je kunt een bestemming kiezen om te zien hoe luchtvaartmaatschappijen daarop presteren.
- Er wordt getoond wat de gemiddelde vertraging per maatschappij is en hoeveel vluchten ze uitvoeren.
- Daarnaast is een interactieve kaart te zien van de route van Zürich naar de geselecteerde bestemming.
- In de grafieken zie je:
  - Bubble chart: aantal vluchten vs gemiddelde vertraging, kleur = kans op vertraging, inclusief trendlijn.
  - Punctualiteitsgrafiek: verdeling Early, On-Time en Delayed per maatschappij.

Door deze trends te analyseren, kun je beter voorspellen welke maatschappijen in de toekomst mogelijk meer vertragingen zullen hebben.
""")


@st.cache_data
def load_data():
    schedule_airport = pd.read_csv("data/schedule_airport.csv", sep=",", low_memory=False)
    airports = pd.read_csv("data/airports-extended-clean.csv", sep=";", low_memory=False)
    airlines = pd.read_csv("data/airlines.csv", sep=",", low_memory=False)

    airports['Latitude'] = airports['Latitude'].astype(str).str.replace(',', '.').astype(float)
    airports['Longitude'] = airports['Longitude'].astype(str).str.replace(',', '.').astype(float)
    return schedule_airport, airports, airlines

schedule_airport, airports, airlines = load_data()


kolommen = ['STD', 'FLT', 'STA_STD_ltc', 'ATA_ATD_ltc', 'LSV', 'Org/Des']
schedule_airport = schedule_airport[kolommen].copy()

schedule_airport['STA_STD_ltc'] = pd.to_datetime(schedule_airport['STA_STD_ltc'], errors='coerce')
schedule_airport['ATA_ATD_ltc'] = pd.to_datetime(schedule_airport['ATA_ATD_ltc'], errors='coerce')
schedule_airport["UNQ"] = schedule_airport["FLT"].astype(str).str[:2]
schedule_airport['Vertraging (min)'] = (schedule_airport['ATA_ATD_ltc'] - schedule_airport['STA_STD_ltc']).dt.total_seconds() / 60
schedule_airport = schedule_airport[(schedule_airport['Vertraging (min)'].notna()) & (schedule_airport['LSV'] == 'S')]

bestemmingen = sorted(schedule_airport['Org/Des'].dropna().unique())
gekozen_bestemming = st.selectbox("Kies een bestemming", bestemmingen)
df_bestemming = schedule_airport[schedule_airport['Org/Des'] == gekozen_bestemming]

vertraging_per_maatschappij = (
    df_bestemming.groupby('UNQ')
    .agg({'Vertraging (min)': 'mean', 'FLT': 'count'})
    .reset_index()
    .rename(columns={'UNQ': 'IATA', 'Vertraging (min)': 'Gemiddelde vertraging (min)', 'FLT': 'Aantal vluchten'})
)
airlines = airlines.rename(columns={col: col.strip() for col in airlines.columns})
vertraging_per_maatschappij = vertraging_per_maatschappij.merge(airlines[['IATA', 'Name']], on='IATA', how='left')
vertraging_per_maatschappij['Gemiddelde vertraging (min)'] = vertraging_per_maatschappij['Gemiddelde vertraging (min)'].astype(int)
vertraging_per_maatschappij = vertraging_per_maatschappij.sort_values(by='Gemiddelde vertraging (min)')
vertraging_per_maatschappij = vertraging_per_maatschappij[['Name', 'IATA', 'Aantal vluchten', 'Gemiddelde vertraging (min)']].rename(
    columns={'Name': 'Luchtvaartmaatschappij'}
)

st.subheader(f"Gemiddelde vertraging en aantal vluchten per luchtvaartmaatschappij naar {gekozen_bestemming}")
st.dataframe(vertraging_per_maatschappij, use_container_width=True)

def maak_kaart(bestemming_code):
    zrh_lat, zrh_lon = 47.458, 8.555
    kaart = folium.Map(location=[zrh_lat, zrh_lon], zoom_start=4)
    bestemming = airports[airports['ICAO'].str.upper() == bestemming_code.upper()]
    if not bestemming.empty:
        dest_lat = bestemming['Latitude'].values[0]
        dest_lon = bestemming['Longitude'].values[0]
        dest_name = bestemming['Name'].values[0]
        folium.Marker([zrh_lat, zrh_lon], popup="Zurich Airport (ZRH)",
                      icon=folium.Icon(color="blue", icon="plane", prefix='fa')).add_to(kaart)
        folium.Marker([dest_lat, dest_lon], popup=f"{dest_name} ({bestemming_code})",
                      icon=folium.Icon(color="red", icon="plane", prefix='fa')).add_to(kaart)
        folium.PolyLine([[zrh_lat, zrh_lon], [dest_lat, dest_lon]], color="green", weight=3, opacity=0.7).add_to(kaart)
    return kaart

kaart = maak_kaart(gekozen_bestemming)
kaart.save("kaart.html")
st.subheader(f"Route van Zurich naar {gekozen_bestemming}")
st.components.v1.html(open("kaart.html", "r", encoding="utf-8").read(), height=500)

vertraging_plot = (
    df_bestemming.groupby('UNQ')
    .agg(
        totaal_vluchten=('FLT', 'count'),
        gemiddelde_vertraging=('Vertraging (min)', 'mean'),
        vertraagde_vluchten=('Vertraging (min)', lambda x: (x > 5).sum())
    )
    .reset_index()
)
vertraging_plot['kans_op_vertraging'] = (vertraging_plot['vertraagde_vluchten'] / vertraging_plot['totaal_vluchten']) * 100
vertraging_plot = vertraging_plot.merge(airlines[['IATA', 'Name']], left_on='UNQ', right_on='IATA', how='left')

fig3 = px.scatter(
    vertraging_plot,
    x="totaal_vluchten",
    y="gemiddelde_vertraging",
    size="totaal_vluchten",
    color="kans_op_vertraging",
    hover_name="Name",
    text="IATA",
    color_continuous_scale="RdYlGn_r",
)

# Trendlijn toevoegen
if len(vertraging_plot) > 1:
    X = vertraging_plot['totaal_vluchten']
    Y = vertraging_plot['gemiddelde_vertraging']
    m, b = np.polyfit(X, Y, 1)
    x_line = np.linspace(X.min(), X.max(), 100)
    y_line = m * x_line + b
    fig3.add_trace(go.Scatter(x=x_line, y=y_line, mode='lines', line=dict(color='black', width=2), name='Trendlijn'))
    corr = np.corrcoef(X, Y)[0, 1]
else:
    corr = 0

fig3.update_traces(textposition='top center')
fig3.update_layout(
    xaxis_title="Aantal vluchten",
    yaxis_title="Gemiddelde vertraging (min)",
    plot_bgcolor='white',
    xaxis=dict(showgrid=True, gridcolor='lightgrey'),
    yaxis=dict(showgrid=True, gridcolor='lightgrey'),
    font=dict(size=12),
    coloraxis_colorbar=dict(title="Kans op vertraging (%)")
)


st.subheader(f"Kans op vertraging per luchtvaartmaatschappij naar {gekozen_bestemming}")
st.plotly_chart(fig3, use_container_width=True)


st.markdown("### Conclusie trendlijn")
if corr < -0.2:
    st.success(f"Er is een duidelijke **dalende trend** (correlatie: {corr:.2f}). Meer vluchten gaan gepaard met minder vertraging.")
elif corr > 0.2:
    st.warning(f"Er is een duidelijke **stijgende trend** (correlatie: {corr:.2f}). Meer vluchten gaan gepaard met meer vertraging.")
else:
    st.info(f"Er is **geen duidelijke trend** zichtbaar tussen het aantal vluchten en de gemiddelde vertraging (correlatie: {corr:.2f}).")


vertraging_frequentie = (
    df_bestemming.groupby('UNQ')
    .agg({'Vertraging (min)': 'mean', 'FLT': 'count'})
    .reset_index()
    .rename(columns={'UNQ': 'IATA', 'FLT': 'Aantal vluchten', 'Vertraging (min)': 'Gemiddelde vertraging (min)'})
)
vertraging_frequentie = vertraging_frequentie.merge(airlines[['IATA', 'Name']], on='IATA', how='left').dropna()

maatschappijen = vertraging_frequentie['IATA'].unique()


gekozen_maatschappij = st.selectbox("Kies een luchtvaartmaatschappij voor punctualiteit", maatschappijen)

df_maatschappij = df_bestemming[df_bestemming['UNQ'] == gekozen_maatschappij]
bins = [-1000, -5, 5, float('inf')]
labels = ['Early', 'On-time', 'Delayed']
df_maatschappij['Categorie'] = pd.cut(df_maatschappij['Vertraging (min)'], bins=bins, labels=labels)
punctualiteit = df_maatschappij['Categorie'].value_counts(normalize=True).reindex(labels).fillna(0) * 100


st.subheader(f"Punctualiteit van {gekozen_maatschappij}")
fig2, ax2 = plt.subplots()
punctualiteit.plot(kind='bar', ax=ax2, color=['green', 'gold', 'red'])
ax2.set_ylabel('Percentage (%)')
ax2.set_xlabel('Categorie')
ax2.set_ylim(0, 100)
for i, v in enumerate(punctualiteit):
    ax2.text(i, v + 1, f"{v:.1f}%", ha='center')
st.pyplot(fig2)
