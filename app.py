import io
import os
import fitz  # PyMuPDF
from PIL import Image, ImageDraw, ImageFont
import streamlit as st

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="TruMed Path Labs - Dummy Report Generator",
    page_icon="🧪",
    layout="wide",
)

# --- HEADER SECTION WITH EXACT REFERENCE BRANDING ---
logo_html = ""
logo_path = "logo.png"
if not os.path.exists(logo_path) and os.path.exists("logo.png.jpg"):
    logo_path = "logo.png.jpg"

if os.path.exists(logo_path):
    import base64

    with open(logo_path, "rb") as image_file:
        encoded_logo = base64.b64encode(image_file.read()).decode()
    logo_html = f'<img src="data:image/png;base64,{encoded_logo}" style="max-height: 85px; background: white; padding: 10px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">'

st.markdown(
    f"""
    <style>
    .trumed-banner {{
        background: linear-gradient(135deg, #1D52D8 0%, #153EB1 100%);
        color: white;
        padding: 24px 30px;
        border-radius: 12px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 25px;
        box-shadow: 0 6px 15px rgba(29, 82, 216, 0.25);
    }}
    .banner-left {{
        display: flex;
        align-items: center;
        gap: 24px;
    }}
    .banner-title {{
        font-size: 28px;
        font-weight: 800;
        margin: 0;
        color: #FFFFFF;
        letter-spacing: 0.5px;
    }}
    .banner-subtitle {{
        font-size: 15px;
        color: #E2E8F0;
        margin: 4px 0 2px 0;
        font-weight: 600;
    }}
    .banner-contact {{
        font-size: 13px;
        color: #93C5FD;
        margin: 0;
        font-weight: 600;
    }}
    .banner-address {{
        font-size: 12px;
        color: #CBD5E1;
        margin: 3px 0 0 0;
    }}
    .nabl-pill {{
        background: linear-gradient(135deg, #FFB800 0%, #FF9F00 100%);
        color: #0F172A;
        font-weight: 900;
        padding: 12px 22px;
        border-radius: 30px;
        font-size: 13px;
        letter-spacing: 0.8px;
        box-shadow: 0 4px 12px rgba(255, 159, 0, 0.4);
        white-space: nowrap;
        display: flex;
        align-items: center;
        gap: 6px;
    }}
    </style>

    <div class="trumed-banner">
        <div class="banner-left">
            {logo_html}
            <div>
                <h1 class="banner-title">TruMed Path Labs India Pvt Ltd.</h1>
                <div class="banner-subtitle">Dummy Report Generator</div>
                <div class="banner-contact">📞 Helpline: +91 703636 63689</div>
                <div class="banner-address">📍 Central Lab, Plot No. 32, Umakanth Arcade, Vasavi Nagar Colony, Karkhana, Secunderabad, Telangana - 500015</div>
            </div>
        </div>
        <div class="nabl-pill">
            🏅 NABL ACCREDITED LAB
        </div>
    </div>
""",
    unsafe_allow_html=True,
)


def process_report_page(page):
    """Processes an individual PDF page:

    1. Masks patient details (Name -> DUMMY, IDs -> XXX).
    2. Strips signatures and QR codes.
    3. Preserves charts/graphs.
    4. Stamps 'TruMed's Dummy Report' diagonal watermark.
    5. Flattens into a non-editable image-based PDF page.
    """
    rect = page.rect

    # --- STEP 1: MASK PATIENT DETAILS & REMOVE SIGNATURES/QR ---
    page.draw_rect(
        fitz.Rect(110, 85, 330, 115), color=(1, 1, 1), fill=(1, 1, 1)
    )
    page.draw_rect(
        fitz.Rect(110, 135, 270, 155), color=(1, 1, 1), fill=(1, 1, 1)
    )
    page.draw_rect(
        fitz.Rect(110, 155, 270, 175), color=(1, 1, 1), fill=(1, 1, 1)
    )
    page.draw_rect(
        fitz.Rect(410, 100, 570, 125), color=(1, 1, 1), fill=(1, 1, 1)
    )

    page.draw_rect(
        fitz.Rect(
            rect.width - 250, rect.height - 130, rect.width - 20, rect.height - 40
        ),
        color=(1, 1, 1),
        fill=(1, 1, 1),
    )
    page.draw_rect(
        fitz.Rect(20, rect.height -
