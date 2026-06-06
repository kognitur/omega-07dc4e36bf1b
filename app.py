import streamlit as st
from PIL import Image
import numpy as np
from sklearn.cluster import KMeans
import pandas as pd
import io
import base64

st.set_page_config(page_title="Color Palette Extractor", layout="centered")

st.title("🎨 Color Palette Extractor")
st.markdown("Upload a website screenshot and get a CSS-ready color palette instantly!")

uploaded_file = st.file_uploader("Choose a screenshot...", type=["png", "jpg", "jpeg", "webp"])

def extract_colors(image, n_colors=6):
    img = image.resize((150, 150))
    img_array = np.array(img)
    pixels = img_array.reshape(-1, 3)
    
    kmeans = KMeans(n_clusters=n_colors, random_state=42, n_init=10)
    kmeans.fit(pixels)
    
    colors = kmeans.cluster_centers_.astype(int)
    return colors

def rgb_to_hex(rgb):
    return '#{:02x}{:02x}{:02x}'.format(rgb[0], rgb[1], rgb[2])

def get_css_palette(colors):
    css = ""
    for i, color in enumerate(colors):
        hex_color = rgb_to_hex(color)
        css += f".color-{i+1} {{ background-color: {hex_color}; }}\n"
    return css

if uploaded_file is not None:
    try:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Screenshot", use_column_width=True)
        
        with st.spinner("Extracting colors..."):
            colors = extract_colors(image)
        
        st.subheader("🎯 Extracted Color Palette")
        
        # Display colors as swatches
        cols = st.columns(len(colors))
        for i, (col, color) in enumerate(zip(cols, colors)):
            hex_color = rgb_to_hex(color)
            with col:
                st.markdown(
                    f'<div style="background-color: {hex_color}; height: 60px; border-radius: 5px; margin-bottom: 5px;"></div>',
                    unsafe_allow_html=True
                )
                st.markdown(f"**{hex_color}**")
                st.caption(f"RGB: {color[0]}, {color[1]}, {color[2]}")
        
        # CSS output
        st.subheader("📝 CSS Ready Palette")
        css_palette = get_css_palette(colors)
        st.code(css_palette, language="css")
        
        # Hex codes list
        hex_list = [rgb_to_hex(c) for c in colors]
        hex_text = "\n".join(hex_list)
        
        # Download buttons
        col1, col2 = st.columns(2)
        
        with col1:
            csv_buffer = io.StringIO()
            df = pd.DataFrame({
                "Color": [f"Color {i+1}" for i in range(len(colors))],
                "Hex": hex_list,
                "R": [c[0] for c in colors],
                "G": [c[1] for c in colors],
                "B": [c[2] for c in colors]
            })
            df.to_csv(csv_buffer, index=False)
            st.download_button(
                label="📥 Download CSV",
                data=csv_buffer.getvalue(),
                file_name="color_palette.csv",
                mime="text/csv"
            )
        
        with col2:
            st.download_button(
                label="📥 Download Hex Codes",
                data=hex_text,
                file_name="hex_codes.txt",
                mime="text/plain"
            )
        
        # Copy to clipboard button
        hex_json = str(hex_list)
        b64 = base64.b64encode(hex_json.encode()).decode()
        st.markdown(
            f"""
            <button onclick="navigator.clipboard.writeText({hex_list})" 
                    style="padding: 10px 20px; background-color: #4CAF50; color: white; border: none; border-radius: 5px; cursor: pointer;">
                📋 Copy Hex Codes to Clipboard
            </button>
            """,
            unsafe_allow_html=True
        )
        
    except Exception as e:
        st.error(f"❌ Error processing image: {str(e)}")
        st.info("Please try uploading a different image file.")
else:
    st.info("👆 Drag and drop or click to upload a website screenshot")
    
    # Example usage instructions
    with st.expander("ℹ️ How to use"):
        st.markdown("""
        1. Take a screenshot of any website
        2. Upload it using the button above
        3. Get instant color palette with hex codes
        4. Download results as CSV or text file
        
        **Tip:** Works best with clean, well-lit screenshots
        """)

st.markdown("---")
st.markdown("Made with ❤️ for designers")