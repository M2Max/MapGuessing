import streamlit as st
import folium
from streamlit_folium import st_folium
from src.restaurant_list import PlaceSearcher
from src.distance_calculator import DistanceCalculator
from src.filter_values import PlaceFilter

st.set_page_config(page_title="MapGuessing Web UI", layout="wide")
st.title("MapGuessing Place Search 🌍")
st.markdown("""
<style>
    .stTextInput>div>div>input {font-size: 18px;}
    .stButton>button {font-size: 18px;}
    .stSelectbox>div>div>div {font-size: 18px;}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.header("Search Parameters")
    api_key = st.text_input("Google Maps API Key", type="password")
    lat = st.text_input("Center Latitude", "")
    lng = st.text_input("Center Longitude", "")
    diameter_km = st.number_input("Search Diameter (km)", min_value=1.0, value=10.0)
    min_km = st.number_input("Min Distance (km)", min_value=0.0, value=0.0)
    max_km = st.number_input("Max Distance (km)", min_value=0.0, value=100.0)
    min_min = st.number_input("Min Travel Time (min)", min_value=0, value=0)
    max_min = st.number_input("Max Travel Time (min)", min_value=0, value=120)
    search = st.button("Search")

if search:
    try:
        lat_f = float(lat)
        lng_f = float(lng)
        radius_m = int(diameter_km * 1000 / 2)
        st.info("Searching for places...")
        searcher = PlaceSearcher(api_key)
        places = searcher.search(lat_f, lng_f, radius_m)
        st.success(f"Found {len(places)} places. Calculating distances...")
        calculator = DistanceCalculator(api_key, lat_f, lng_f)
        places_with_dist = calculator.calculate_for_places(places)
        filterer = PlaceFilter(min_km, max_km, min_min, max_min)
        filtered = filterer.filter(places_with_dist)
        st.subheader(f"Filtered to {len(filtered)} places:")
        cols = st.columns(2)
        for idx, p in enumerate(filtered):
            lat_val = p.get('latitude')
            lng_val = p.get('longitude')
            if lat_val is None or lng_val is None:
                st.warning(f"Skipping result with missing coordinates: {p.get('name','Unknown')}")
                continue
            try:
                lat_val = float(lat_val)
                lng_val = float(lng_val)
            except Exception:
                st.warning(f"Skipping result with invalid coordinates: {p.get('name','Unknown')}")
                continue
            with cols[idx % 2]:
                st.markdown(f"### {p.get('name','Unknown')}")
                st.markdown(f"**Address:** {p.get('address','No address')}")
                st.markdown(f"**Distance:** {p.get('distance_km','?')} km")
                st.markdown(f"**Travel time:** {p.get('duration_text','?')}")
                m = folium.Map(location=[lat_val, lng_val], zoom_start=14, width='100%', height='200')
                folium.Marker([lat_val, lng_val], icon=folium.Icon(color='red')).add_to(m)
                st_folium(m, width=400, height=250, returned_objects=[])
    except Exception as e:
        st.error(f"Error: {e}")
        st.stop()
else:
    st.info("Enter parameters and click Search to begin.")
