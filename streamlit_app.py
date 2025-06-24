import streamlit as st
import requests
import requests
from io import BytesIO

API_URL = "http://localhost:8000/clothes/"
SAVE_URL = "http://localhost:8000/save-outfit"

st.set_page_config(page_title="Virtual Closet", layout="wide")
st.title("🧥 Your Virtual Closet - Outfit Builder")

# Load clothes
res = requests.get(API_URL)
if res.status_code != 200:
    st.error("Failed to load clothes.")
    st.stop()
clothes = res.json()
if not clothes:
    st.warning("Add some clothes first!")
    st.stop()

# Filters
types = sorted(set([c['garment_type'] for c in clothes]))
colors = sorted(set([c['color'] for c in clothes]))
col1, col2 = st.columns(2)
with col1:
    selected_type = st.selectbox("Garment Type", ["All"] + types)
with col2:
    selected_color = st.selectbox("Color", ["All"] + colors)

filtered = clothes
if selected_type != "All":
    filtered = [c for c in filtered if c['garment_type'] == selected_type]
if selected_color != "All":
    filtered = [c for c in filtered if c['color'] == selected_color]

# Outfit Builder
st.subheader("Select items to include in your outfit:")
selected_ids = []
cols = st.columns(3)
for idx, item in enumerate(filtered):
    with cols[idx % 3]:
        st.image(item["image_url"], use_container_width=True)
        st.caption(f"{item['name']} ({item['color']} {item['garment_type']})")
        if st.checkbox("Add to outfit", key=f"check_{item['id']}"):
            selected_ids.append(item["id"])
# Upload Section
st.markdown("### 📸 Upload New Clothing")
uploaded_image = st.file_uploader("Choose an image", type=["jpg", "jpeg", "png"])

name = st.text_input("Name")
color = st.text_input("Color")
garment_type = st.text_input("Garment Type")

if st.button("Upload"):
    if uploaded_image and name and color and garment_type:
        try:
            files = {
                "image": (uploaded_image.name, uploaded_image, uploaded_image.type)
            }
            data = {
                "name": name,
                "color": color,
                "garment_type": garment_type
            }

            res = requests.post("http://localhost:8000/upload-clothing/", files=files, data=data)

            if res.status_code == 200:
                st.success(f"Uploaded '{name}' successfully!")
            else:
                st.error(f"Error: {res.text}")
        except Exception as e:
            st.error(f"Exception occurred: {e}")
    else:
        st.warning("Please fill out all fields and select an image.")

# Save Outfit
st.divider()
outfit_name = st.text_input("📝 Outfit Name")
if st.button("💾 Save Outfit") and outfit_name and selected_ids:
    payload = {"name": outfit_name, "item_ids": selected_ids}
    save_res = requests.post(SAVE_URL, json=payload)
    if save_res.status_code == 200:
        st.success(f"Outfit '{outfit_name}' saved!")
    else:
        st.error("Failed to save outfit. Try again.")
