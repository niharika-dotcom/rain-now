import requests
import pandas as pd
import streamlit as st
from datetime import datetime

st.set_page_config(page_title="Rain Now", page_icon="🌧️")

GEO_URL = "https://geocoding-api.open-meteo.com/v1/search"
WX_URL = "https://api.open-meteo.com/v1/forecast"
# Approximate (Sydapuram centre). Replace with exact coordinates later.
MY_PLACE = ("Kammavaripalli (near Sydapuram)", 14.17714, 79.74183)
RAIN_CODES = {51, 53, 55, 56, 57, 61, 63, 65, 66, 67, 80, 81, 82, 95, 96, 99}

T = {
    "English": {
        "code": "en", "title": "Rain Now",
        "caption": "Is it raining there right now? Live data, not a forecast.",
        "input": "Search a place (e.g. Nellore, Gudur, Tirupati)",
        "search_fail": "Place search failed", "not_found": "Place not found. Try another spelling.",
        "select": "Select place", "wx_fail": "Weather data failed",
        "raining": "It is raining", "dry": "No rain right now",
        "rain_mm": "Rain", "temp": "Temp", "humidity": "Humidity",
        "condition": "Condition", "unknown": "Unknown",
        "data_time": "Data time", "source": "Source: Open-Meteo model data",
        "tip_rain": "☔ Carry an umbrella. Postpone spraying and field work.",
        "tip_dry": "✅ Good time to travel and do field work.",
        "hours": "Rain in the last 12 hours (mm)",
        "reports_title": "👥 What do you see there?",
        "reports_caption": "If you are at this place, tell us the truth.",
        "btn_rain": "🌧️ It is raining", "btn_no_rain": "☀️ No rain",
        "match": "Users agree with the data",
        "coord_title": "Can't find your village? Use coordinates",
        "coord_help": "Open Google Maps, right-click (or long-press) your village, copy the numbers (like 14.4426, 79.9865) and paste here.",
        "coord_input": "Coordinates (latitude, longitude)",
        "coord_bad": "Could not read coordinates. Use the format: 14.4426, 79.9865",
        "coord_name": "Your coordinates",
        "my_place": "Use my village: Kammavaripalli (near Sydapuram)",
        "my_place_note": "Approximate location. Untick to search another place.",
        "codes": {0: "Clear sky", 1: "Mostly clear", 2: "Partly cloudy", 3: "Overcast", 45: "Fog", 48: "Fog",
                  51: "Light drizzle", 53: "Drizzle", 55: "Heavy drizzle", 61: "Light rain", 63: "Rain",
                  65: "Heavy rain", 80: "Light showers", 81: "Showers", 82: "Heavy showers",
                  95: "Thunderstorm", 96: "Thunderstorm + hail", 99: "Thunderstorm + hail"},
    },
    "తెలుగు": {
        "code": "te", "title": "ఇప్పుడు వర్షం?",
        "caption": "అక్కడ ఇప్పుడు వర్షం పడుతోందా? ప్రస్తుత డేటా, అంచనా కాదు.",
        "input": "ఊరి పేరు వెతుకు (ఉదా: Nellore, Gudur లేదా తెలుగులో)",
        "search_fail": "ఊరి శోధన విఫలమైంది", "not_found": "ఊరు దొరకలేదు. వేరే స్పెల్లింగ్ ప్రయత్నించు.",
        "select": "ఊరిని ఎంచుకో", "wx_fail": "వాతావరణ డేటా విఫలమైంది",
        "raining": "వర్షం పడుతోంది", "dry": "ఇప్పుడు వర్షం లేదు",
        "rain_mm": "వర్షం", "temp": "ఉష్ణోగ్రత", "humidity": "తేమ",
        "condition": "పరిస్థితి", "unknown": "తెలియదు",
        "data_time": "డేటా సమయం", "source": "మూలం: Open-Meteo మోడల్ డేటా",
        "tip_rain": "☔ గొడుగు తీసుకెళ్ళు. మందు పిచికారీ, పొలం పనులు వాయిదా వేయి.",
        "tip_dry": "✅ ప్రయాణానికి, పొలం పనులకు మంచి సమయం.",
        "hours": "గత 12 గంటల వర్షం (mm)",
        "reports_title": "👥 అక్కడ నువ్వు ఏం చూస్తున్నావు?",
        "reports_caption": "మీరు ఆ ప్రదేశంలో ఉంటే, నిజం చెప్పండి.",
        "btn_rain": "🌧️ వర్షం ఉంది", "btn_no_rain": "☀️ వర్షం లేదు",
        "match": "డేటాతో యూజర్లు ఏకీభవించారు",
        "coord_title": "మీ ఊరు దొరకలేదా? కోఆర్డినేట్స్ వాడండి",
        "coord_help": "Google Maps లో మీ ఊరి మీద రైట్ క్లిక్ (లేదా ఎక్కువసేపు నొక్కండి) చేసి, కనిపించే సంఖ్యలను (14.4426, 79.9865 లాగా) ఇక్కడ పేస్ట్ చేయండి.",
        "coord_input": "కోఆర్డినేట్స్ (latitude, longitude)",
        "coord_bad": "కోఆర్డినేట్స్ చదవలేకపోయాను. ఇలా రాయండి: 14.4426, 79.9865",
        "coord_name": "మీ కోఆర్డినేట్స్",
        "my_place": "నా ఊరు వాడు: Kammavaripalli (Sydapuram దగ్గర)",
        "my_place_note": "ఇది సుమారు స్థానం. వేరే ఊరు వెతకాలంటే టిక్ తీసేయి.",
        "codes": {0: "నిర్మలమైన ఆకాశం", 1: "దాదాపు నిర్మలం", 2: "పాక్షికంగా మేఘావృతం", 3: "మేఘావృతం",
                  45: "పొగమంచు", 48: "పొగమంచు", 51: "తేలికపాటి చినుకులు", 53: "చినుకులు",
                  55: "ఎక్కువ చినుకులు", 61: "తేలికపాటి వర్షం", 63: "వర్షం", 65: "భారీ వర్షం",
                  80: "తేలికపాటి జల్లులు", 81: "జల్లులు", 82: "భారీ జల్లులు",
                  95: "ఉరుములతో వర్షం", 96: "ఉరుములు + వడగళ్ళు", 99: "ఉరుములు + వడగళ్ళు"},
    },
}


def inject_css(raining):
    if raining:
        bg = "linear-gradient(160deg,#0f2027,#203a43,#2c5364)"
        drops = """
        .rain{position:fixed;inset:0;pointer-events:none;z-index:0;opacity:.35;
          background-image:linear-gradient(105deg,transparent 48%,#9fd3ff 50%,transparent 52%);
          background-size:26px 70px;animation:fall .6s linear infinite;}
        .rain.two{background-size:41px 110px;animation-duration:.9s;opacity:.25;}
        @keyframes fall{from{background-position:0 0}to{background-position:-12px 70px}}"""
        layers = '<div class="rain"></div><div class="rain two"></div>'
    else:
        bg = "linear-gradient(160deg,#1c92d2,#6dd5fa,#f2fcfe)"
        drops = ".sun{position:fixed;top:-60px;right:-60px;width:220px;height:220px;border-radius:50%;background:radial-gradient(circle,#fff6a8,#ffd54a 60%,transparent 70%);opacity:.8;pointer-events:none;animation:pulse 4s ease-in-out infinite;}@keyframes pulse{50%{transform:scale(1.08)}}"
        layers = '<div class="sun"></div>'
    st.markdown(f"""<style>
    .stApp{{background:{bg};}}
    h1,h2,h3,[data-testid="stCaptionContainer"],.stApp label p,.stRadio p,.stCheckbox p{{color:#fff !important;}}
    .hero{{position:relative;z-index:1;text-align:center;padding:28px 16px;margin:12px 0;border-radius:24px;
      background:rgba(255,255,255,.14);backdrop-filter:blur(8px);border:1px solid rgba(255,255,255,.3);color:#fff;}}
    .hero .big{{font-size:64px;line-height:1.1}}
    .hero .st{{font-size:28px;font-weight:700;margin-top:6px}}
    .hero .sub{{opacity:.9;margin-top:4px}}
    .cards{{display:flex;gap:10px;position:relative;z-index:1;margin-bottom:8px}}
    .card{{flex:1;text-align:center;padding:14px 6px;border-radius:18px;color:#fff;
      background:rgba(255,255,255,.16);border:1px solid rgba(255,255,255,.28)}}
    .card .v{{font-size:24px;font-weight:700}} .card .k{{font-size:13px;opacity:.9}}
    .tip{{position:relative;z-index:1;padding:12px 14px;border-radius:14px;color:#fff;
      background:rgba(0,0,0,.22);margin:8px 0}}
    {drops}
    </style>{layers}""", unsafe_allow_html=True)


@st.cache_data(ttl=300)
def search_place(name, lang_code):
    r = requests.get(GEO_URL, params={"name": name, "count": 5, "language": lang_code}, timeout=10)
    r.raise_for_status()
    return r.json().get("results", [])


@st.cache_data(ttl=300)
def get_weather(lat, lon):
    params = {
        "latitude": lat, "longitude": lon, "timezone": "auto",
        "current": "temperature_2m,relative_humidity_2m,precipitation,weather_code",
        "hourly": "precipitation", "past_hours": 12, "forecast_hours": 1,
    }
    r = requests.get(WX_URL, params=params, timeout=10)
    r.raise_for_status()
    return r.json()


lang = st.radio("Language / భాష", list(T.keys()), horizontal=True)
t = T[lang]

if "reports" not in st.session_state:
    st.session_state.reports = []

use_mine = st.checkbox(t["my_place"], value=True)
if use_mine:
    st.caption(t["my_place_note"])
query = st.text_input(t["input"])
with st.expander(t["coord_title"]):
    st.caption(t["coord_help"])
    coord_text = st.text_input(t["coord_input"])

sel = None
if use_mine and not coord_text.strip():
    sel = MY_PLACE
elif coord_text.strip():
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
        labels = [f"{p['name']}, {p.get('admin1', '')}, {p.get('country', '')}" for p in places]
        choice = st.selectbox(t["select"], labels)
        p = places[labels.index(choice)]
        sel = (p["name"], p["latitude"], p["longitude"])

if not sel:
    inject_css(False)
    st.title("🌧️ " + t["title"])
    st.caption(t["caption"])
else:
    place_name, lat, lon = sel
    try:
        data = get_weather(lat, lon)
    except Exception as e:
        inject_css(False)
        st.error(f"{t['wx_fail']}: {e}")
        st.stop()

    cur = data["current"]
    mm = cur.get("precipitation") or 0
    code = cur.get("weather_code")
    raining = mm > 0 or code in RAIN_CODES
    inject_css(raining)

    st.title("🌧️ " + t["title"])
    st.caption(t["caption"])

    emoji = "🌧️" if raining else ("⛅" if code in (2, 3) else "☀️")
    status = t["raining"] if raining else t["dry"]
    st.markdown(
        f"""<div class="hero"><div class="big">{emoji}</div>
        <div class="st">{status}</div>
        <div class="sub">📍 {place_name} · {t['codes'].get(code, t['unknown'])}</div></div>
        <div class="cards">
        <div class="card"><div class="v">{mm} mm</div><div class="k">{t['rain_mm']}</div></div>
        <div class="card"><div class="v">{cur.get('temperature_2m')}°C</div><div class="k">{t['temp']}</div></div>
        <div class="card"><div class="v">{cur.get('relative_humidity_2m')}%</div><div class="k">{t['humidity']}</div></div>
        </div>
        <div class="tip">{t['tip_rain'] if raining else t['tip_dry']}</div>""",
        unsafe_allow_html=True,
    )

    try:
        h = data["hourly"]
        df_h = pd.DataFrame({"mm": h["precipitation"]}, index=[x[-5:] for x in h["time"]])
        st.subheader(t["hours"])
        st.bar_chart(df_h)
    except Exception:
        pass

    st.caption(f"{t['data_time']}: {cur.get('time')} · {t['source']}")
    st.map(pd.DataFrame({"lat": [lat], "lon": [lon]}))

    st.divider()
    st.subheader(t["reports_title"])
    st.caption(t["reports_caption"])
    c1, c2 = st.columns(2)
    if c1.button(t["btn_rain"], use_container_width=True):
        st.session_state.reports.append({"place": place_name, "status": "rain", "time": datetime.now()})
    if c2.button(t["btn_no_rain"], use_container_width=True):
        st.session_state.reports.append({"place": place_name, "status": "no rain", "time": datetime.now()})

    mine = [r for r in st.session_state.reports if r["place"] == place_name]
    if mine:
        df = pd.DataFrame(mine)
        agree = (df["status"] == ("rain" if raining else "no rain")).mean()
        st.write(f"{t['match']}: **{agree * 100:.0f}%** ({len(df)})")
        st.progress(float(agree))
