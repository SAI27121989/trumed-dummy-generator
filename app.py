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
    rect = page.rect

    # --- STEP 1: PRECISELY MASK PATIENT DETAILS ---
    page.draw_rect(
        fitz.Rect(18, 105, rect.width - 18, 185), color=(1, 1, 1), fill=(1, 1, 1)
    )
    # Mask top right QR code area
    page.draw_rect(
        fitz.Rect(rect.width - 95, 75, rect.width - 15, 175),
        color=(1, 1, 1),
        fill=(1, 1, 1),
    )

    # --- STEP 2: PRECISELY MASK HANDWRITTEN SIGNATURES ABOVE NAMES ---
    page.draw_rect(
        fitz.Rect(20, rect.height - 185, 250, rect.height - 125),
        color=(1, 1, 1),
        fill=(1, 1, 1),
    )
    page.draw_rect(
        fitz.Rect(
            rect.width - 270, rect.height - 185, rect.width - 20, rect.height - 125
        ),
        color=(1, 1, 1),
        fill=(1, 1, 1),
    )

    # --- STEP 3: INSERT CLEAN DUMMY PLACEHOLDER TEXT ---
    page.insert_text(
        fitz.Point(22, 120),
        "Patient Name : DUMMY PATIENT",
        fontsize=9.5,
        color=(0, 0, 0),
    )
    page.insert_text(
        fitz.Point(22, 137),
        "Age/Sex           : 30 Year(s) / General",
        fontsize=9.5,
        color=(0, 0, 0),
    )
    page.insert_text(
        fitz.Point(22, 154), "Ref.Doctor      : XXX", fontsize=9.5, color=(0, 0, 0)
    )
    page.insert_text(
        fitz.Point(22, 171),
        "Ref.Customer   : XXX",
        fontsize=9.5,
        color=(0, 0, 0),
    )

    page.insert_text(
        fitz.Point(340, 120), "SID/PID    : XXX", fontsize=9.5, color=(0, 0, 0)
    )
    page.insert_text(
        fitz.Point(340, 137),
        "Collected  : 2026-10-21 10:00:00",
        fontsize=9.5,
        color=(0, 0, 0),
    )
    page.insert_text(
        fitz.Point(340, 154),
        "Registered : 2026-10-21 11:00:00",
        fontsize=9.5,
        color=(0, 0, 0),
    )
    page.insert_text(
        fitz.Point(340, 171),
        "Reported   : 2026-10-21 12:00:00",
        fontsize=9.5,
        color=(0, 0, 0),
    )

    # --- STEP 4: RENDER TO HIGH-RES IMAGE & ADD CLEAR WATERMARK ---
    pix = page.get_pixmap(dpi=250)
    img = Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGBA")
    w, h = img.size

    text_img = Image.new("RGBA", (w, h), (255, 255, 255, 0))
    text_draw = ImageDraw.Draw(text_img)

    watermark_text = "TRUMED DUMMY REPORT - FOR TRAINING ONLY"
    try:
        font = ImageFont.truetype("arial.ttf", int(w * 0.045))
    except IOError:
        font = ImageFont.load_default()

    # Draw a prominent, clearly visible gray watermark across the center
    text_draw.text(
        (w // 8, h // 2.3),
        watermark_text,
        fill=(110, 110, 110, 130),
        font=font,
    )

    rotated_watermark = text_img.rotate(30, expand=True)
    px = (rotated_watermark.width - w) // 2
    py = (rotated_watermark.height - h) // 2
    cropped_watermark = rotated_watermark.crop((px, py, px + w, py + h))

    final_img = Image.alpha_composite(img, cropped_watermark).convert("RGB")

    # --- STEP 5: FLATTEN INTO SECURE NON-EDITABLE PDF PAGE ---
    pdf_bytes = io.BytesIO()
    final_img.save(pdf_bytes, format="PDF", resolution=250)
    return pdf_bytes.getvalue()


# --- DASHBOARD CARD CONTAINER ---
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
            "Sanitizing patient data, stripping signatures, watermarking, and merging all pages..."
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
                f"✅ Done! Successfully processed all **{total_pages} page(s)** across **{len(uploaded_files)} report file(s)**."
            )

            st.download_button(
                label="📥 Download Merged Dummy Report PDF",
                data=output_bytes.getvalue(),
                file_name="TruMed_Dummy_Report_Merged.pdf",
                mime="application/pdf",
            )
