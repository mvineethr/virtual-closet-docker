import streamlit as st
import requests

API_URL = "http://localhost:8000/clothes"

st.set_page_config(page_title="Virtual Closet", layout="wide")
st.title("👗 Your Virtual Closet")

# Fetch clothes from backend
response = requests.get(API_URL)
if response.status_code != 200:
    st.error("Failed to load clothes")
    st.stop()

clothes = response.json()
if not clothes:
    st.warning("No clothes in your closet yet!")
    st.stop()

# 🧠 Extract filter options
types = sorted(set([c['garment_type'] for c in clothes]))
colors = sorted(set([c['color'] for c in clothes]))

# 🔘 Filter selection
col1, col2 = st.columns(2)
with col1:
    selected_type = st.selectbox("Filter by Garment Type", ["All"] + types)
with col2:
    selected_color = st.selectbox("Filter by Color", ["All"] + colors)

# 🧼 Apply filters
filtered = clothes
if selected_type != "All":
    filtered = [c for c in filtered if c['garment_type'] == selected_type]
if selected_color != "All":
    filtered = [c for c in filtered if c['color'] == selected_color]

# 🖼 Display filtered results
st.subheader(f"Showing {len(filtered)} Items")
cols = st.columns(3)
for idx, item in enumerate(filtered):
    with cols[idx % 3]:
        st.image(item['image_url'], use_container_width=True)
        st.caption(f"👕 {item['name']} ({item['color']} {item['garment_type']})")
