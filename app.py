import base64
import io
import os
import fitz  # PyMuPDF
import streamlit as st

# ==========================================
# 1. STREAMLIT PAGE CONFIGURATION & UI
# ==========================================
st.set_page_config(
    page_title="TruMed Path Labs - Dummy Report Generator",
    page_icon="🧪",
    layout="wide",
)

# Load logo safely if present
logo_html = ""
logo_path = "logo.png"
if not os.path.exists(logo_path) and os.path.exists("logo.png.jpg"):
    logo_path = "logo.png.jpg"

if os.path.exists(logo_path):
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


# ==========================================
# 2. ROBUST REDACTION & WATERMARK ENGINE
# ==========================================
def apply_dummy_watermark(page):
    """Applies centered 35-degree angled watermark 'TruMed's DUMMY REPORT'."""
    rect = page.rect
    watermark_text = "TruMed's DUMMY REPORT"
    center_point = fitz.Point(rect.width * 0.5, rect.height * 0.5)

    fontsize = int(rect.width / 13)
    morph = (center_point, fitz.Matrix(35))

    page.insert_text(
        center_point,
        watermark_text,
        fontsize=fontsize,
        fontname="hebo",
        color=(0.11, 0.32, 0.84),
        morph=morph,
        fill_opacity=0.15,
    )


def process_report_page(page):
    """Safely collects redactions, applies them in batch, inserts text, and watermarks."""
    # List of metadata mappings to replace: (Keyword, New Value, Is Bold)
    replacements = [
        ("Patient Name", ": Mr DUMMY", True),
        ("Ref.Doctor", ": XXX", False),
        ("Ref.Customer", ": XXX", False),
        ("TPL Code", ": XXX", False),
        ("SID/PID", ": XXX", False),
    ]

    # 1. Add redaction annotations for metadata fields
    for keyword, _, _ in replacements:
        matches = page.search_for(keyword)
        if matches:
            r = matches[0]
            val_box = fitz.Rect(r.x1 + 2, r.y0 - 2, r.x1 + 220, r.y1 + 2)
            page.add_redact_annot(val_box, fill=(1, 1, 1))

    # 2. Add redaction for top QR code block ("scan to download")
    top_qr = page.search_for("scan to download")
    if top_qr:
        qr_r = top_qr[0]
        qr_box = fitz.Rect(qr_r.x0 - 10, qr_r.y0 - 50, qr_r.x1 + 10, qr_r.y1 + 10)
        page.add_redact_annot(qr_box, fill=(1, 1, 1))

    # 3. Add redaction for bottom doctor signatures & designations
    doc_signs = page.search_for("PATHOLOGIST") + page.search_for("BIOCHEMIST")
    for sign_rect in doc_signs:
        sig_box = fitz.Rect(
            sign_rect.x0 - 120,
            sign_rect.y0 - 45,
            sign_rect.x1 + 120,
            sign_rect.y1 + 10,
        )
        page.add_redact_annot(sig_box, fill=(1, 1, 1))

    # 4. Apply all collected redactions simultaneously
    page.apply_redactions()

    # 5. Insert replacement text cleanly after redaction layer is committed
    for keyword, new_text, is_bold in replacements:
        matches = page.search_for(keyword)
        if matches:
            r = matches[0]
            font_name = "helv-bold" if is_bold else "helv"
            page.insert_text(
                fitz.Point(r.x1 + 4, r.y1 - 1),
                new_text,
                fontsize=9,
                fontname=font_name,
                color=(0, 0, 0),
            )

    # 6. Apply Watermark
    apply_dummy_watermark(page)


# ==========================================
# 3. STREAMLIT FILE PROCESSING DASHBOARD
# ==========================================
st.subheader("📁 Upload Lab Reports")
st.write(
    "Upload original lab reports to generate standardized dummy PDFs with clear headers, watermarks, and wiped signatures."
)

uploaded_files = st.file_uploader(
    "Drag and drop PDF files here", type=["pdf"], accept_multiple_files=True
)

if uploaded_files:
    st.info(
        f"📋 **{len(uploaded_files)} file(s)** uploaded and ready for processing."
    )

    if st.button("🚀 Process & Generate Dummy PDF"):
        with st.spinner(
            "Updating metadata, generating watermarks, and clearing signatures..."
        ):
            combined_pdf = fitz.open()
            total_pages = 0

            for uploaded_file in uploaded_files:
                doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")

                for page_num in range(len(doc)):
                    page = doc[page_num]
                    process_report_page(page)
                    combined_pdf.insert_pdf(
                        doc, from_page=page_num, to_page=page_num
                    )
                    total_pages += 1

            output_bytes = io.BytesIO()
            combined_pdf.save(output_bytes)
            combined_pdf.close()

            st.success(
                f"✅ Done! Successfully processed all **{total_pages} page(s)**."
            )

            st.download_button(
                label="📥 Download Processed Dummy Report PDF",
                data=output_bytes.getvalue(),
                file_name="TruMed_Dummy_Report_Final.pdf",
                mime="application/pdf",
            )
