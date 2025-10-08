import streamlit as sl
import pandas as pd
import numpy as np
import folium
import plotly.express as px
import requests

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
        <span>Live vluchtgegevens</span>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)
sl.set_page_config(layout="wide")
sl.logo("https://companieslogo.com/img/orig/FHZN.SW_BIG.D-79fb25dc.png?t=1720244491")

# Load data
flight_1s = pd.read_excel("data/30sFlight_1.xlsx")
flight_2s = pd.read_excel("data/30sFlight_2.xlsx")
flight_3s = pd.read_excel("data/30sFlight_3.xlsx")
flight_4s = pd.read_excel("data/30sFlight_4.xlsx")
flight_5s = pd.read_excel("data/30sFlight_5.xlsx")
flight_6s = pd.read_excel("data/30sFlight_6.xlsx")
flight_7s = pd.read_excel("data/30sFlight_7.xlsx")

sl.title("Live Flight Data ")
gekozen_vlucht = sl.selectbox(
    "Selecteer vlucht",
    ["Flight 1", "Flight 2", "Flight 3", "Flight 4", "Flight 5", "Flight 6", "Flight 7"],
)
col1, col2, col3 = sl.columns(3, border=True)
col4, col5, col6, col7 = sl.columns(4, border=True)
col8, col9 = sl.columns(2, border=True)
if gekozen_vlucht == "Flight 1":
    df = flight_1s
elif gekozen_vlucht == "Flight 2":
    df = flight_2s
elif gekozen_vlucht == "Flight 3":
    df = flight_3s
elif gekozen_vlucht == "Flight 4":
    df = flight_4s
elif gekozen_vlucht == "Flight 5":
    df = flight_5s
elif gekozen_vlucht == "Flight 6":
    df = flight_6s
else:
    df = flight_7s

# Ensure numeric types (coerce strings like "123", "123.0", or "N/A" safely)
num_cols = ["[3d Altitude Ft]", "TRUE AIRSPEED (derived)", "Time (secs)"]
for c in num_cols:
    if c in df.columns:
        df[c] = pd.to_numeric(df[c], errors="coerce")

sl.subheader(f"Live data voor {gekozen_vlucht}")
sl.dataframe(df, use_container_width=True)

fig = px.line(
    df,
    x="Time (secs)",
    y="[3d Altitude Ft]",
    title=f"Altitude vs Speed for {gekozen_vlucht}",
)
fig.add_scatter(
    x=df["Time (secs)"],
    y=df["TRUE AIRSPEED (derived)"],
    mode="lines",
    name="True Airspeed",
    yaxis="y2",
)
fig.update_layout(yaxis2=dict(title="True Airspeed", overlaying="y", side="right"))
sl.plotly_chart(fig, use_container_width=True)

# Helpers to format metrics even if series is empty after coercion
def fmt_min(s):
    s = s.dropna()
    return f"{s.min():,.0f}" if not s.empty else "—"

def fmt_max(s):
    s = s.dropna()
    return f"{s.max():,.0f}" if not s.empty else "—"

def fmt_mean(s):
    s = s.dropna()
    return f"{s.mean():,.0f}" if not s.empty else "—"

col1.metric("Minimum Altitude (Ft)", fmt_min(df["[3d Altitude Ft]"]))
col2.metric("Maximum Al titude (Ft)", fmt_max(df["[3d Altitude Ft]"]))
col3.metric("Average Altitude (Ft)", fmt_mean(df["[3d Altitude Ft]"]))
col4.metric("Minimum Speed (Knots)", fmt_min(df["TRUE AIRSPEED (derived)"]))
col5.metric("Maximum Speed (Knots)", fmt_max(df["TRUE AIRSPEED (derived)"]))
col6.metric("Average Speed (Knots)", fmt_mean(df["TRUE AIRSPEED (derived)"]))
col7.metric("Total Time (min)", fmt_max(df["Time (secs)"] /60))  # Assuming time starts at 0
# Assuming the DataFrame has columns for start and end locations in long lat format
start_location = df[["[3d Latitude]", "[3d Longitude]"]].dropna().iloc[0].to_dict()
end_location = df[["[3d Latitude]", "[3d Longitude]"]].dropna().iloc[-1].to_dict()


start_location_url = (
    f"https://api.bigdatacloud.net/data/reverse-geocode-client?"
    f"latitude={start_location['[3d Latitude]']}&longitude={start_location['[3d Longitude]']}&localityLanguage=en"
)

end_location_url = (
    f"https://api.bigdatacloud.net/data/reverse-geocode-client?"
    f"latitude={end_location['[3d Latitude]']}&longitude={end_location['[3d Longitude]']}&localityLanguage=en"
)

responsestart = requests.get(start_location_url)

if responsestart.status_code == 200:
    data = responsestart.json()
    city = data.get("city")
    col8.metric("Start Location", city)
else:
    print(f"Error: {responsestart.status_code} - {responsestart.text}")

responseend = requests.get(end_location_url)
if responseend.status_code == 200:
    data = responseend.json()
    city = data.get("city")
    col9.metric("End Location", city)
else:
    print(f"Error: {responseend.status_code} - {responseend.text}")

# kaart maken
def createMap(df):
    if df[["[3d Latitude]", "[3d Longitude]"]].dropna().empty:
        sl.warning("No valid latitude and longitude data available to create a map.")
        return

    # Dropdown for line color metric
    color_metric = sl.selectbox(
        "Color line by:",
        ["Height (Altitude)", "Speed"],
        key="map_color_metric"
    )

    mid_lat = df["[3d Latitude]"].mean()
    mid_lon = df["[3d Longitude]"].mean()
    m = folium.Map(location=[mid_lat, mid_lon], zoom_start=6)

    # Get clean data for the flight path
    clean_df = df[["[3d Latitude]", "[3d Longitude]", "[3d Altitude Ft]", "TRUE AIRSPEED (derived)", "Time (secs)"]].dropna()

    if len(clean_df) < 2:
        sl.warning("Not enough valid data points to create a flight path.")
        return

    # Add start and end markers
    start_row = clean_df.iloc[0]
    end_row = clean_df.iloc[-1]

    folium.Marker(
        location=[start_row["[3d Latitude]"], start_row["[3d Longitude]"]],
        popup="Start Location",
        icon=folium.Icon(color="green", icon="plane")
    ).add_to(m)

    folium.Marker(
        location=[end_row["[3d Latitude]"], end_row["[3d Longitude]"]],
        popup="End Location",
        icon=folium.Icon(color="red", icon="plane")
    ).add_to(m)

    # Create colored line segments based on selected metric
    metric_col = "[3d Altitude Ft]" if color_metric == "Height (Altitude)" else "TRUE AIRSPEED (derived)"

    # Normalize the metric values to 0-1 for color mapping
    metric_values = clean_df[metric_col]
    min_val = metric_values.min()
    max_val = metric_values.max()

    if max_val > min_val:
        normalized_values = (metric_values - min_val) / (max_val - min_val)
    else:
        normalized_values = pd.Series([0.5] * len(metric_values))

    # Create line segments with colors
    for i in range(len(clean_df) - 1):
        start_point = [clean_df.iloc[i]["[3d Latitude]"], clean_df.iloc[i]["[3d Longitude]"]]
        end_point = [clean_df.iloc[i+1]["[3d Latitude]"], clean_df.iloc[i+1]["[3d Longitude]"]]

        # Color based on normalized value (blue for low, red for high)
        color_intensity = normalized_values.iloc[i]
        color = f"#{int(255 * color_intensity):02x}{int(255 * (1 - color_intensity)):02x}00"

        folium.PolyLine(
            locations=[start_point, end_point],
            color=color,
            weight=3,
            opacity=0.8
        ).add_to(m)

    # Slider for time
    sl.subheader("Flight Path Map")
    min_time = clean_df["Time (secs)"].min()
    max_time = clean_df["Time (secs)"].max()

    current_time = sl.slider(
        "Flight time (seconds):",
        min_value=float(min_time),
        max_value=float(max_time),
        step=(max_time - min_time) / df.shape[0],  # Adjust step based on the length of the file
        value=float(min_time),
        key="plane_time"
    )

    # Find the closest data point to the selected time
    time_diff = (clean_df["Time (secs)"] - current_time).abs()
    closest_idx = time_diff.idxmin()
    current_row = clean_df.loc[closest_idx]

    current_lat = current_row["[3d Latitude]"]
    current_lon = current_row["[3d Longitude]"]
    current_alt = current_row["[3d Altitude Ft]"]
    current_speed = current_row["TRUE AIRSPEED (derived)"] * 1.852
    actual_time = current_row["Time (secs)"] / 60  # Convert to minutes

    folium.Marker(
        location=[current_lat, current_lon],
        popup=f"Time: {actual_time:.1f} min<br>Altitude: {current_alt:.0f} ft<br>Speed: {current_speed:.1f} kts",
        icon=folium.Icon(color="blue", icon="plane", prefix='fa')
    ).add_to(m)

    # Display current position info
    col1, col2, col3 = sl.columns(3)
    with col1:
        sl.metric("Time", f"{actual_time:.1f} min")
    with col2:
        sl.metric("Altitude", f"{current_alt:.0f} ft")
    with col3:
        sl.metric("Speed", f"{current_speed:.1f} km/h")

    sl.components.v1.html(m._repr_html_(), height=500)
    return m

createMap(df)