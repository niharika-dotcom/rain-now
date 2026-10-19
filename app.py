import requests
import pandas as pd
import streamlit as st
from datetime import datetime

st.set_page_config(page_title="Rain Now", page_icon="🌧️")
st.title("🌧️ Rain Now")
st.caption("Ee place lo ippudu rain padutunda? (prediction kaadu, current data)")

GEO_URL = "https://geocoding-api.open-meteo.com/v1/search"
WX_URL = "https://api.open-meteo.com/v1/forecast"

RAIN_CODES = {51, 53, 55, 56, 57, 61, 63, 65, 66, 67, 80, 81, 82, 95, 96, 99}

CODE_TEXT = {
    0: "Clear sky", 1: "Mostly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Fog", 48: "Fog",
    51: "Light drizzle", 53: "Drizzle", 55: "Heavy drizzle",
    61: "Light rain", 63: "Rain", 65: "Heavy rain",
    80: "Light showers", 81: "Showers", 82: "Heavy showers",
    95: "Thunderstorm", 96: "Thunderstorm + hail", 99: "Thunderstorm + hail",
}


@st.cache_data(ttl=300)
def search_place(name):
    r = requests.get(GEO_URL, params={"name": name, "count": 5}, timeout=10)
    r.raise_for_status()
    return r.json().get("results", [])


@st.cache_data(ttl=300)
def current_weather(lat, lon):
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,precipitation,rain,showers,weather_code",
        "timezone": "auto",
    }
    r = requests.get(WX_URL, params=params, timeout=10)
    r.raise_for_status()
    return r.json()["current"]


if "reports" not in st.session_state:
    st.session_state.reports = []

query = st.text_input("Place peru (e.g. Nellore, Gudur, Tirupati)")

if query:
    try:
        places = search_place(query)
    except Exception as e:
        st.error(f"Place search fail ayindi: {e}")
        places = []

    if not places:
        st.warning("Place dorakaledu. Vere spelling try cheyyi.")
    else:
        labels = [
            f"{p['name']}, {p.get('admin1', '')}, {p.get('country', '')}" for p in places
        ]
        choice = st.selectbox("Select place", labels)
        p = places[labels.index(choice)]
        lat, lon = p["latitude"], p["longitude"]

        try:
            cur = current_weather(lat, lon)
        except Exception as e:
            st.error(f"Weather data fail ayindi: {e}")
            st.stop()

        mm = (cur.get("precipitation") or 0)
        code = cur.get("weather_code")
        raining = mm > 0 or code in RAIN_CODES

        if raining:
            st.success(f"🌧️ Ippudu rain padutundi ({mm} mm)")
        else:
            st.info("☀️ Ippudu rain ledu")

        c1, c2, c3 = st.columns(3)
        c1.metric("Rain (mm)", mm)
        c2.metric("Temp °C", cur.get("temperature_2m"))
        c3.metric("Humidity %", cur.get("relative_humidity_2m"))
        st.write(f"Condition: **{CODE_TEXT.get(code, 'Unknown')}**")
        st.caption(f"Data time: {cur.get('time')} (local). Source: Open-Meteo model data.")

        st.map(pd.DataFrame({"lat": [lat], "lon": [lon]}))

        st.divider()
        st.subheader("👥 Local users report")
        st.caption("Neeku aa place lo evaraina unte, nijam cheppandi.")
        col1, col2 = st.columns(2)
        if col1.button("🌧️ Rain undi"):
            st.session_state.reports.append(
                {"place": p["name"], "status": "rain", "time": datetime.now()}
            )
        if col2.button("☀️ Rain ledu"):
            st.session_state.reports.append(
                {"place": p["name"], "status": "no rain", "time": datetime.now()}
            )

        mine = [r for r in st.session_state.reports if r["place"] == p["name"]]
        if mine:
            df = pd.DataFrame(mine)
            st.write(df["status"].value_counts())
            agree = (df["status"] == ("rain" if raining else "no rain")).mean() * 100
            st.write(f"API tho users reports match: **{agree:.0f}%**")
