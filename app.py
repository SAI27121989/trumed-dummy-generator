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

# --- CUSTOM BRANDING CSS (Royal Blue #1D52D8 & Gold #FF9F00) ---
st.markdown(
    """
    <style>
    /* Global Page Background */
    .main {
        background-color: #F4F6FB;
    }
    
    /* Header Banner Styling */
    .trumed-header {
        background-color: #1D52D8;
        color: white;
        padding: 20px 30px;
        border-radius: 10px 10px 0px 0px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .header-left {
        display: flex;
        align-items: center;
        gap: 20px;
    }
    
    .logo-img {
        background-color: white;
        padding: 8px;
        border-radius: 8px;
        max-height: 65px;
    }
    
    .trumed-header h1 {
        color: white;
        font-size: 26px;
        font-weight: 700;
        margin: 0;
    }
    
    .trumed-header p {
        color: #E2E8F0;
        font-size: 13px;
        margin: 4px 0 0 0;
    }
    
    .nabl-badge {
        background-color: #FF9F00;
        color: #0F172A;
        font-weight: 800;
        padding: 8px 16px;
        border-radius: 20px;
        font-size: 13px;
        letter-spacing: 0.5px;
        white-space: nowrap;
    }

    /* Card Container */
    .card-container {
        background-color: #FFFFFF;
        padding: 30px;
        border-radius: 0px 0px 10px 10px;
        box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.05);
        margin-bottom: 25px;
    }
    
    /* Primary Processing Button */
    .stButton>button {
        background-color: #1D52D8;
        color: white;
        font-weight: 600;
        font-size: 16px;
        border-radius: 6px;
        border: none;
        padding: 12px 28px;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #153EB1;
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- HEADER SECTION ---
logo_html = ""
if os.path.exists("logo.png"):
    import base64

    with open("logo.png", "rb") as image_file:
        encoded_logo = base64.b64encode(image_file.read()).decode()
    logo_html = f'<img src="data:image/png;base64,{encoded_logo}" class="logo-img">'

st.markdown(
    f"""
    <div class="trumed-header">
        <div class="header-left">
            {logo_html}
            <div>
                <h1>TruMed Path Labs India Pvt Ltd.</h1>
                <p>📍 Central Lab: Plot No. 32, Umakanth Arcade, Vasavi Nagar Colony, Secunderabad - 500015 | 📞 Helpline: +91 7036363689</p>
            </div>
        </div>
        <div class="nabl-badge">
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
        fitz.Rect(20, rect.height - 130, 220, rect.height - 50),
        color=(1, 1, 1),
        fill=(1, 1, 1),
    )

    # --- STEP 2: INSERT DUMMY PLACEHOLDER TEXT ---
    page.insert_text(
        fitz.Point(115, 105), "DUMMY", fontsize=10, color=(0, 0, 0)
    )
    page.insert_text(fitz.Point(115, 148), "XXX", fontsize=10, color=(0, 0, 0))
    page.insert_text(fitz.Point(115, 168), "XXX", fontsize=10, color=(0, 0, 0))
    page.insert_text(fitz.Point(415, 118), "XXX", fontsize=10, color=(0, 0, 0))

    # --- STEP 3: RENDER TO HIGH-RES IMAGE & WATERMARK ---
    pix = page.get_pixmap(dpi=250)
    img = Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGBA")
    w, h = img.size

    text_img = Image.new("RGBA", (w, h), (255, 255, 255, 0))
    text_draw = ImageDraw.Draw(text_img)

    watermark_text = "TruMed's Dummy Report"
    try:
        font = ImageFont.truetype("arial.ttf", int(w * 0.05))
    except IOError:
        font = ImageFont.load_default()

    text_draw.text(
        (w // 4, h // 2), watermark_text, fill=(160, 160, 160, 80), font=font
    )

    rotated_watermark = text_img.rotate(32, expand=True)
    px = (rotated_watermark.width - w) // 2
    py = (rotated_watermark.height - h) // 2
    cropped_watermark = rotated_watermark.crop((px, py, px + w, py + h))

    final_img = Image.alpha_composite(img, cropped_watermark).convert("RGB")

    # --- STEP 4: FLATTEN INTO SECURE NON-EDITABLE PDF PAGE ---
    pdf_bytes = io.BytesIO()
    final_img.save(pdf_bytes, format="PDF", resolution=250)
    return pdf_bytes.getvalue()


# --- DASHBOARD CARD CONTAINER ---
st.markdown('<div class="card-container">', unsafe_allow_html=True)

st.subheader("📁 Upload Lab Reports")
st.write(
    "Select individual reports, attachments, or multi-page PDF profiles to generate a merged, locked dummy PDF."
)

uploaded_files = st.file_uploader(
    "Drag and drop PDF files here", type=["pdf"], accept_multiple_files=True
)

if uploaded_files:
    st.info(
        f"📋 **{len(uploaded_files)} file(s)** uploaded and ready for processing."
    )

    if st.button("🚀 Process & Generate Unified Dummy PDF"):
        with st.spinner(
            "Sanitizing patient data, stripping signatures/QRs, watermarking, and merging..."
        ):
            combined_pdf = fitz.open()
            total_pages = 0

            for uploaded_file in uploaded_files:
                doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")

                for page_num in range(len(doc)):
                    page = doc[page_num]
                    processed_bytes = process_report_page(page)
                    processed_doc = fitz.open(
                        stream=processed_bytes, filetype="pdf"
                    )
                    combined_pdf.insert_pdf(processed_doc)
                    total_pages += 1

            output_bytes = io.BytesIO()
            combined_pdf.save(output_bytes)
            combined_pdf.close()

            st.success(
                f"✅ Done! Processed **{total_pages} page(s)** across **{len(uploaded_files)} report file(s)**."
            )

            st.download_button(
                label="📥 Download Merged Dummy Report PDF",
                data=output_bytes.getvalue(),
                file_name="TruMed_Dummy_Report_Merged.pdf",
                mime="application/pdf",
            )

st.markdown("</div>", unsafe_allow_html=True)
