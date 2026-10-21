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

# --- HEADER SECTION ---
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

    # --- STEP 1: DYNAMIC PATIENT HEADER REDACTION ---
    p_name_instances = page.search_for("Patient Name")
    y0 = 75
    if p_name_instances:
        y0 = p_name_instances[0].y0 - 5
        patient_redact_rect = fitz.Rect(18, y0, rect.width - 18, y0 + 82)
        page.add_redact_annot(patient_redact_rect, fill=(1, 1, 1))

    # --- STEP 2: DYNAMIC SIGNATURE SCRIBBLE REDACTION ---
    # Target only the line where handwritten signatures overlap, leaving titles intact
    biochem_instances = page.search_for("BIOCHEMIST")
    path_instances = page.search_for("PATHOLOGIST")

    if biochem_instances:
        b_rect = biochem_instances[0]
        sig_left_rect = fitz.Rect(20, b_rect.y0 - 35, 230, b_rect.y0 - 12)
        page.add_redact_annot(sig_left_rect, fill=(1, 1, 1))

    if path_instances:
        p_rect = path_instances[0]
        sig_right_rect = fitz.Rect(
            rect.width - 240, p_rect.y0 - 35, rect.width - 20, p_rect.y0 - 12
        )
        page.add_redact_annot(sig_right_rect, fill=(1, 1, 1))

    # Apply redactions
    page.apply_redactions()

    # --- STEP 3: INSERT CLEAN DUMMY PATIENT METADATA ---
    base_y = y0

    page.insert_text(
        fitz.Point(22, base_y + 12),
        "Patient Name : Mr. DUMMY PATIENT",
        fontsize=9.5,
        color=(0, 0, 0),
    )
    page.insert_text(
        fitz.Point(22, base_y + 28),
        "Age/Sex           : 30 Year(s) / Male",
        fontsize=9.5,
        color=(0, 0, 0),
    )
    page.insert_text(
        fitz.Point(22, base_y + 44),
        "Ref.Doctor      : XXX",
        fontsize=9.5,
        color=(0, 0, 0),
    )
    page.insert_text(
        fitz.Point(22, base_y + 60),
        "Ref.Customer   : XXX",
        fontsize=9.5,
        color=(0, 0, 0),
    )
    page.insert_text(
        fitz.Point(22, base_y + 76),
        "TPL Code         : XXX",
        fontsize=9.5,
        color=(0, 0, 0),
    )

    page.insert_text(
        fitz.Point(340, base_y + 12),
        "Sample Type : Serum",
        fontsize=9.5,
        color=(0, 0, 0),
    )
    page.insert_text(
        fitz.Point(340, base_y + 28),
        "SID/PID        : XXX",
        fontsize=9.5,
        color=(0, 0, 0),
    )
    page.insert_text(
        fitz.Point(340, base_y + 44),
        "Collected on : 2026-10-21 10:00:00",
        fontsize=9.5,
        color=(0, 0, 0),
    )
    page.insert_text(
        fitz.Point(340, base_y + 60),
        "Registered on : 2026-10-21 11:00:00",
        fontsize=9.5,
        color=(0, 0, 0),
    )
    page.insert_text(
        fitz.Point(340, base_y + 76),
        "Reported on   : 2026-10-21 12:00:00",
        fontsize=9.5,
        color=(0, 0, 0),
    )

    # --- STEP 4: RENDER TO IMAGE & APPLY VISIBLE DIAGONAL WATERMARK ---
    pix = page.get_pixmap(dpi=200)
    img = Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGBA")
    w, h = img.size

    text_img = Image.new("RGBA", (w, h), (255, 255, 255, 0))
    text_draw = ImageDraw.Draw(text_img)

    watermark_text = "TRUMED DUMMY REPORT - FOR TRAINING ONLY"
    try:
        font = ImageFont.truetype("arial.ttf", 55)
    except IOError:
        font = ImageFont.load_default()

    # Draw centered watermark text with clear visibility (Alpha = 65)
    text_draw.text(
        (w // 12, h // 2.2),
        watermark_text,
        fill=(29, 82, 216, 65),
        font=font,
    )

    rotated_watermark = text_img.rotate(30, expand=True)
    px = (rotated_watermark.width - w) // 2
    py = (rotated_watermark.height - h) // 2
    cropped_watermark = rotated_watermark.crop((px, py, px + w, py + h))

    final_img = Image.alpha_composite(img, cropped_watermark).convert("RGB")

    pdf_bytes = io.BytesIO()
    final_img.save(pdf_bytes, format="PDF", resolution=200)
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
            "Sanitizing patient data, stripping signature lines, watermarking, and merging all pages..."
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
