import streamlit as st
import pandas as pd
import numpy as np
import folium
import matplotlib.pyplot as plt

# ================== DATA LADEN ==================
@st.cache_data
def load_data():
    schedule_airport = pd.read_csv("data/schedule_airport.csv", sep=",", low_memory=False)
    airports = pd.read_csv("data/airports-extended-clean.csv", sep=";", low_memory=False)
    airlines = pd.read_csv("data/airlines.csv", sep=",", low_memory=False)

    airports['Latitude'] = airports['Latitude'].astype(str).str.replace(',', '.').astype(float)
    airports['Longitude'] = airports['Longitude'].astype(str).str.replace(',', '.').astype(float)

    return schedule_airport, airports, airlines

st.set_page_config(layout="wide")
st.logo('https://companieslogo.com/img/orig/FHZN.SW_BIG.D-79fb25dc.png?t=1720244491')
# ===== Data inladen =====
schedule_airport, airports, airlines = load_data()

# ================== DATA OPSCHONEN ==================
kolommen = ['STD', 'FLT', 'STA_STD_ltc', 'ATA_ATD_ltc', 'LSV', 'Org/Des']
schedule_airport = schedule_airport[kolommen].copy()

schedule_airport['STA_STD_ltc'] = pd.to_datetime(schedule_airport['STA_STD_ltc'], errors='coerce')
schedule_airport['ATA_ATD_ltc'] = pd.to_datetime(schedule_airport['ATA_ATD_ltc'], errors='coerce')

schedule_airport["UNQ"] = schedule_airport["FLT"].astype(str).str[:2]
schedule_airport['Vertraging (min)'] = (
    schedule_airport['ATA_ATD_ltc'] - schedule_airport['STA_STD_ltc']
).dt.total_seconds() / 60

# ❌ verwijderde (>= 0) filter zodat early vluchten ook meetellen
schedule_airport = schedule_airport[
    (schedule_airport['Vertraging (min)'].notna()) &
    (schedule_airport['LSV'] == 'S')
]

# ================== BESTEMMING KIEZEN ==================
bestemmingen = sorted(schedule_airport['Org/Des'].dropna().unique())
gekozen_bestemming = st.selectbox("✈️ Kies een bestemming", bestemmingen)

df_bestemming = schedule_airport[schedule_airport['Org/Des'] == gekozen_bestemming]

# ================== GEM. VERTAGING PER MAATSCHAPPIJ ==================
vertraging_per_maatschappij = (
    df_bestemming.groupby('UNQ')
    .agg({'Vertraging (min)': 'mean', 'FLT': 'count'})
    .reset_index()
    .rename(columns={'UNQ': 'IATA', 'Vertraging (min)': 'Gemiddelde vertraging (min)', 'FLT': 'Aantal vluchten'})
)

airlines = airlines.rename(columns={col: col.strip() for col in airlines.columns})
vertraging_per_maatschappij = vertraging_per_maatschappij.merge(
    airlines[['IATA', 'Name']], on='IATA', how='left'
)

vertraging_per_maatschappij['Gemiddelde vertraging (min)'] = vertraging_per_maatschappij['Gemiddelde vertraging (min)'].astype(int)
vertraging_per_maatschappij = vertraging_per_maatschappij.sort_values(by='Gemiddelde vertraging (min)')
vertraging_per_maatschappij = vertraging_per_maatschappij[['Name', 'IATA', 'Aantal vluchten', 'Gemiddelde vertraging (min)']].rename(
    columns={'Name': 'Luchtvaartmaatschappij'}
)

st.subheader(f"Gemiddelde vertraging en aantal vluchten per luchtvaartmaatschappij naar {gekozen_bestemming}")
st.dataframe(vertraging_per_maatschappij, use_container_width=True)

# ================== KAART ==================
def maak_kaart(bestemming_code):
    zrh_lat, zrh_lon = 47.458, 8.555  # Zurich
    kaart = folium.Map(location=[zrh_lat, zrh_lon], zoom_start=4)

    bestemming = airports[airports['ICAO'].str.upper() == bestemming_code.upper()]

    if not bestemming.empty:
        dest_lat = bestemming['Latitude'].values[0]
        dest_lon = bestemming['Longitude'].values[0]
        dest_name = bestemming['Name'].values[0]

        folium.Marker(
            location=[zrh_lat, zrh_lon],
            popup="Zurich Airport (ZRH)",
            icon=folium.Icon(color="blue", icon="plane", prefix='fa')
        ).add_to(kaart)

        folium.Marker(
            location=[dest_lat, dest_lon],
            popup=f"{dest_name} ({bestemming_code})",
            icon=folium.Icon(color="red", icon="plane", prefix='fa')
        ).add_to(kaart)

        folium.PolyLine(
            locations=[[zrh_lat, zrh_lon], [dest_lat, dest_lon]],
            color="green",
            weight=3,
            opacity=0.7
        ).add_to(kaart)

        # Legenda
        legenda_html = '''
        <div style="position: fixed; 
                    bottom: 50px; left: 50px; width: 200px; 
                    background-color: white;
                    padding: 10px; border:2px solid grey; z-index:9999; font-size:14px;">
        <b>Legenda</b><br>
        🔵 Zurich Airport<br>
        🔴 Bestemming
        </div>
        '''
        kaart.get_root().html.add_child(folium.Element(legenda_html))

    return kaart

kaart = maak_kaart(gekozen_bestemming)
kaart.save("kaart.html")
st.subheader(f"Route van Zurich naar {gekozen_bestemming}")
st.components.v1.html(open("kaart.html", "r", encoding="utf-8").read(), height=500)

# ================== TRENDPLOT ==================
vertraging_frequentie = (
    df_bestemming.groupby('UNQ')
    .agg({'Vertraging (min)': 'mean', 'FLT': 'count'})
    .reset_index()
    .rename(columns={'UNQ': 'IATA', 'FLT': 'Aantal vluchten', 'Vertraging (min)': 'Gemiddelde vertraging (min)'})
)

vertraging_frequentie = vertraging_frequentie.merge(airlines[['IATA', 'Name']], on='IATA', how='left')
vertraging_frequentie['Aantal vluchten'] = pd.to_numeric(vertraging_frequentie['Aantal vluchten'], errors='coerce')
vertraging_frequentie['Gemiddelde vertraging (min)'] = pd.to_numeric(vertraging_frequentie['Gemiddelde vertraging (min)'], errors='coerce')
vertraging_frequentie = vertraging_frequentie.dropna()

# ================== PUNCTUALITEIT ==================
maatschappijen = vertraging_frequentie['IATA'].unique()
gekozen_maatschappij = st.selectbox("📌 Kies een luchtvaartmaatschappij voor punctualiteit", maatschappijen)

df_maatschappij = df_bestemming[df_bestemming['UNQ'] == gekozen_maatschappij]
bins = [-1000, -5, 5, float('inf')]
labels = ['Early', 'On-time', 'Delayed']
df_maatschappij['Categorie'] = pd.cut(df_maatschappij['Vertraging (min)'], bins=bins, labels=labels)

punctualiteit = df_maatschappij['Categorie'].value_counts(normalize=True).reindex(labels).fillna(0) * 100

# ================== LAYOUT GRAFIEKEN ==================
col1, col2 = st.columns(2)

with col1:
    st.subheader(f"Trend: Aantal vluchten vs. gemiddelde vertraging")
    fig1, ax1 = plt.subplots()
    ax1.scatter(vertraging_frequentie['Aantal vluchten'], vertraging_frequentie['Gemiddelde vertraging (min)'], alpha=0.7)
    if len(vertraging_frequentie) > 1:
        x = vertraging_frequentie['Aantal vluchten']
        y = vertraging_frequentie['Gemiddelde vertraging (min)']
        m, b = np.polyfit(x, y, 1)
        ax1.plot(x, m*x + b, color='red', linewidth=2, label='Trendlijn')
        corr = np.corrcoef(x, y)[0, 1]
    else:
        corr = 0
    ax1.set_xlabel("Aantal vluchten")
    ax1.set_ylabel("Gemiddelde vertraging (min)")
    ax1.legend()
    for i, row in vertraging_frequentie.iterrows():
        ax1.text(row['Aantal vluchten'], row['Gemiddelde vertraging (min)'], row['IATA'], fontsize=8)
    st.pyplot(fig1)
    st.write(f"**Correlatie:** {corr:.2f}")
    if corr < -0.2:
        st.success("Duidelijke dalende trend: meer vluchten = minder vertraging.")
    elif corr > 0.2:
        st.warning("Stijgende trend: meer vluchten = meer vertraging.")
    else:
        st.info(" Geen duidelijke trend tussen aantal vluchten en vertraging.")

with col2:
    st.subheader(f"Punctualiteit van {gekozen_maatschappij}")
    fig2, ax2 = plt.subplots()
    punctualiteit.plot(kind='bar', ax=ax2, color=['green', 'gold', 'red'])
    ax2.set_ylabel('Percentage (%)')
    ax2.set_xlabel('Categorie')
    ax2.set_ylim(0, 100)
    for i, v in enumerate(punctualiteit):
        ax2.text(i, v + 1, f"{v:.1f}%", ha='center')
    st.pyplot(fig2)
