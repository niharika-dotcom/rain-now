import requests
import pandas as pd
import streamlit as st
from datetime import datetime

st.set_page_config(page_title="Rain Now", page_icon="🌧️")

GEO_URL = "https://geocoding-api.open-meteo.com/v1/search"
WX_URL = "https://api.open-meteo.com/v1/forecast"
RAIN_CODES = {51, 53, 55, 56, 57, 61, 63, 65, 66, 67, 80, 81, 82, 95, 96, 99}

T = {
    "English": {
        "code": "en",
        "title": "🌧️ Rain Now",
        "caption": "Is it raining at this place right now? (current data, not a forecast)",
        "input": "Place name (e.g. Nellore, Gudur, Tirupati)",
        "search_fail": "Place search failed",
        "not_found": "Place not found. Try a different spelling.",
        "select": "Select place",
        "wx_fail": "Weather data failed",
        "raining": "🌧️ It is raining right now",
        "not_raining": "☀️ No rain right now",
        "rain_mm": "Rain (mm)",
        "temp": "Temp °C",
        "humidity": "Humidity %",
        "condition": "Condition",
        "unknown": "Unknown",
        "data_time": "Data time",
        "local": "local",
        "source": "Source: Open-Meteo model data.",
        "reports_title": "👥 Local users report",
        "reports_caption": "If you are at this place, tell us what you see.",
        "btn_rain": "🌧️ It is raining",
        "btn_no_rain": "☀️ No rain",
        "match": "Match between users' reports and API",
        "coord_title": "Can't find your village? Use coordinates",
        "coord_help": "Open Google Maps, long-press your village, copy the numbers shown (like 14.4426, 79.9865) and paste here.",
        "coord_input": "Coordinates (latitude, longitude)",
        "coord_bad": "Could not read coordinates. Use the format: 14.4426, 79.9865",
        "coord_name": "Your coordinates",
        "codes": {
            0: "Clear sky", 1: "Mostly clear", 2: "Partly cloudy", 3: "Overcast",
            45: "Fog", 48: "Fog",
            51: "Light drizzle", 53: "Drizzle", 55: "Heavy drizzle",
            61: "Light rain", 63: "Rain", 65: "Heavy rain",
            80: "Light showers", 81: "Showers", 82: "Heavy showers",
            95: "Thunderstorm", 96: "Thunderstorm + hail", 99: "Thunderstorm + hail",
        },
    },
    "తెలుగు": {
        "code": "te",
        "title": "🌧️ ఇప్పుడు వర్షం?",
        "caption": "ఈ ప్రదేశంలో ఇప్పుడు వర్షం పడుతోందా? (అంచనా కాదు, ప్రస్తుత డేటా)",
        "input": "ఊరి పేరు (ఉదా: Nellore, Gudur, Tirupati లేదా తెలుగులో)",
        "search_fail": "ఊరి శోధన విఫలమైంది",
        "not_found": "ఊరు దొరకలేదు. వేరే స్పెల్లింగ్ ప్రయత్నించు.",
        "select": "ఊరిని ఎంచుకో",
        "wx_fail": "వాతావరణ డేటా విఫలమైంది",
        "raining": "🌧️ ఇప్పుడు వర్షం పడుతోంది",
        "not_raining": "☀️ ఇప్పుడు వర్షం లేదు",
        "rain_mm": "వర్షం (mm)",
        "temp": "ఉష్ణోగ్రత °C",
        "humidity": "తేమ %",
        "condition": "పరిస్థితి",
        "unknown": "తెలియదు",
        "data_time": "డేటా సమయం",
        "local": "స్థానిక",
        "source": "మూలం: Open-Meteo మోడల్ డేటా.",
        "reports_title": "👥 స్థానికుల రిపోర్ట్",
        "reports_caption": "మీరు ఆ ప్రదేశంలో ఉంటే, నిజం చెప్పండి.",
        "btn_rain": "🌧️ వర్షం ఉంది",
        "btn_no_rain": "☀️ వర్షం లేదు",
        "match": "యూజర్ రిపోర్ట్స్, API సరిపోలిక",
        "coord_title": "మీ ఊరు దొరకలేదా? కోఆర్డినేట్స్ వాడండి",
        "coord_help": "Google Maps ఓపెన్ చేసి, మీ ఊరి మీద ఎక్కువసేపు నొక్కండి, కనిపించే సంఖ్యలను (14.4426, 79.9865 లాగా) కాపీ చేసి ఇక్కడ పేస్ట్ చేయండి.",
        "coord_input": "కోఆర్డినేట్స్ (latitude, longitude)",
        "coord_bad": "కోఆర్డినేట్స్ చదవలేకపోయాను. ఇలా రాయండి: 14.4426, 79.9865",
        "coord_name": "మీ కోఆర్డినేట్స్",
        "codes": {
            0: "నిర్మలమైన ఆకాశం", 1: "దాదాపు నిర్మలం", 2: "పాక్షికంగా మేఘావృతం", 3: "మేఘావృతం",
            45: "పొగమంచు", 48: "పొగమంచు",
            51: "తేలికపాటి చినుకులు", 53: "చినుకులు", 55: "ఎక్కువ చినుకులు",
            61: "తేలికపాటి వర్షం", 63: "వర్షం", 65: "భారీ వర్షం",
            80: "తేలికపాటి జల్లులు", 81: "జల్లులు", 82: "భారీ జల్లులు",
            95: "ఉరుములతో వర్షం", 96: "ఉరుములు + వడగళ్ళు", 99: "ఉరుములు + వడగళ్ళు",
        },
    },
}

lang = st.radio("Language / భాష", list(T.keys()), horizontal=True)
t = T[lang]

st.title(t["title"])
st.caption(t["caption"])


@st.cache_data(ttl=300)
def search_place(name, lang_code):
    r = requests.get(
        GEO_URL, params={"name": name, "count": 5, "language": lang_code}, timeout=10
    )
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

query = st.text_input(t["input"])

with st.expander(t["coord_title"]):
    st.caption(t["coord_help"])
    coord_text = st.text_input(t["coord_input"])

sel = None  # (name, lat, lon)

if coord_text.strip():
    try:
        a, b = coord_text.replace("°", "").split(",")
        la, lo = float(a), float(b)
        if not (-90 <= la <= 90 and -180 <= lo <= 180):
            raise ValueError
        sel = (t["coord_name"], la, lo)
    except Exception:
        st.warning(t["coord_bad"])
elif query:
    try:
        places = search_place(query, t["code"])
    except Exception as e:
        st.error(f"{t['search_fail']}: {e}")
        places = []

    if not places:
        st.warning(t["not_found"])
        st.info(t["coord_title"] + " ⬆️")
    else:
        labels = [
            f"{p['name']}, {p.get('admin1', '')}, {p.get('country', '')}" for p in places
        ]
        choice = st.selectbox(t["select"], labels)
        p = places[labels.index(choice)]
        sel = (p["name"], p["latitude"], p["longitude"])

if sel:
    place_name, lat, lon = sel

    try:
        cur = current_weather(lat, lon)
    except Exception as e:
        st.error(f"{t['wx_fail']}: {e}")
        st.stop()

    mm = cur.get("precipitation") or 0
    code = cur.get("weather_code")
    raining = mm > 0 or code in RAIN_CODES

    if raining:
        st.success(f"{t['raining']} ({mm} mm)")
    else:
        st.info(t["not_raining"])

    c1, c2, c3 = st.columns(3)
    c1.metric(t["rain_mm"], mm)
    c2.metric(t["temp"], cur.get("temperature_2m"))
    c3.metric(t["humidity"], cur.get("relative_humidity_2m"))
    st.write(f"{t['condition']}: **{t['codes'].get(code, t['unknown'])}**")
    st.caption(f"{t['data_time']}: {cur.get('time')} ({t['local']}). {t['source']}")

    st.map(pd.DataFrame({"lat": [lat], "lon": [lon]}))

    st.divider()
    st.subheader(t["reports_title"])
    st.caption(t["reports_caption"])
    col1, col2 = st.columns(2)
    if col1.button(t["btn_rain"]):
        st.session_state.reports.append(
            {"place": place_name, "status": "rain", "time": datetime.now()}
        )
    if col2.button(t["btn_no_rain"]):
        st.session_state.reports.append(
            {"place": place_name, "status": "no rain", "time": datetime.now()}
        )

    mine = [r for r in st.session_state.reports if r["place"] == place_name]
    if mine:
        df = pd.DataFrame(mine)
        st.write(df["status"].value_counts())
        agree = (df["status"] == ("rain" if raining else "no rain")).mean() * 100
        st.write(f"{t['match']}: **{agree:.0f}%**")
