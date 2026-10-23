import base64
import io
import os
import fitz  # PyMuPDF
import streamlit as st

# ==========================================
# 1. STREAMLIT PAGE CONFIGURATION & UI
# ==========================================
st.set_page_config(
    page_title="TruMed Path Labs - Clean Dummy Generator",
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
                <div class="banner-subtitle">Clean Dummy Report Generator</div>
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
# 2. CLEAN SLATE REDACTION & WATERMARK ENGINE
# ==========================================
def apply_margin_watermark(page):
    """Applies a clean, non-intrusive watermark banner in the top margin at 25% opacity."""
    rect = page.rect
    watermark_text = "--- DUMMY REPORT FOR CLIENT REVIEW ---"
    point = fitz.Point(rect.width * 0.32, 88)

    page.insert_text(
        point,
        watermark_text,
        fontsize=10,
        fontname="Helvetica-Bold",
        color=(0.11, 0.32, 0.84),  # TruMed Blue
        fill_opacity=0.25,
    )


def process_report_page(page):
    """Wipes the messy metadata area cleanly and prints structured dummy details."""
    
    # 1. Dynamically find where the test table starts ("TEST DESCRIPTION")
    table_matches = page.search_for("TEST DESCRIPTION")
    header_bottom = 175
    if table_matches:
        header_bottom = table_matches[0].y0 - 2

    # 2. Clean slate wipe of the entire metadata block zone between header and test table
    metadata_box = fitz.Rect(35, 95, 575, header_bottom)
    page.add_redact_annot(metadata_box, fill=(1, 1, 1))

    # 3. Redact top QR code block if present
    top_qr = page.search_for("scan to download")
    if top_qr:
        for qr_r in top_qr:
            qr_box = fitz.Rect(qr_r.x0 - 10, qr_r.y0 - 50, qr_r.x1 + 10, qr_r.y1 + 10)
            page.add_redact_annot(qr_box, fill=(1, 1, 1))

    # 4. Redact doctor signatures and designations at the bottom
    for sign_keyword in ["PATHOLOGIST", "BIOCHEMIST", "MD", "DNB", "CONSULTANT"]:
        sign_matches = page.search_for(sign_keyword)
        for sign_rect in sign_matches:
            sig_box = fitz.Rect(
                sign_rect.x0 - 120,
                sign_rect.y0 - 45,
                sign_rect.x1 + 120,
                sign_rect.y1 + 10,
            )
            page.add_redact_annot(sig_box, fill=(1, 1, 1))

    # Commit all redactions
    page.apply_redactions()

    # 5. Stamp clean, perfectly aligned professional dummy metadata
    page.insert_text(fitz.Point(40, 112), "Patient Name : Mr DUMMY", fontsize=9, fontname="Helvetica-Bold", color=(0, 0, 0))
    page.insert_text(fitz.Point(40, 127), "Ref.Doctor   : XXX", fontsize=9, fontname="Helvetica", color=(0, 0, 0))
    page.insert_text(fitz.Point(40, 142), "Ref.Customer : XXX", fontsize=9, fontname="Helvetica", color=(0, 0, 0))
    page.insert_text(fitz.Point(40, 157), "TPL Code     : XXX", fontsize=9, fontname="Helvetica", color=(0, 0, 0))
    page.insert_text(fitz.Point(320, 112), "SID/PID      : XXX", fontsize=9, fontname="Helvetica", color=(0, 0, 0))
    page.insert_text(fitz.Point(320, 127), "Sample Type  : Serum", fontsize=9, fontname="Helvetica", color=(0, 0, 0))

    # 6. Apply Margin Watermark Banner
    apply_margin_watermark(page)


# ==========================================
# 3. STREAMLIT FILE PROCESSING DASHBOARD
# ==========================================
st.subheader("📁 Upload Lab Reports")
st.write("Upload original lab reports to generate clean, standardized dummy PDFs.")

uploaded_files = st.file_uploader(
    "Drag and drop PDF files here", type=["pdf"], accept_multiple_files=True
)

if uploaded_files:
    st.info(f"📋 **{len(uploaded_files)} file(s)** uploaded and ready for processing.")

    if st.button("🚀 Process & Generate Dummy PDF"):
        progress_bar = st.progress(0)
        status_text = st.empty()

        try:
            combined_pdf = fitz.open()
            total_pages_count = sum(
                len(fitz.open(stream=f.read(), filetype="pdf"))
                for f in uploaded_files
            )
            for f in uploaded_files:
                f.seek(0)

            current_page = 0
            for uploaded_file in uploaded_files:
                doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")

                for page_num in range(len(doc)):
                    status_text.text(f"Processing page {current_page + 1} of {total_pages_count}...")
                    page = doc[page_num]
                    process_report_page(page)
                    combined_pdf.insert_pdf(
                        doc, from_page=page_num, to_page=page_num
                    )
                    current_page += 1
                    progress_bar.progress(current_page / total_pages_count)

            output_bytes = io.BytesIO()
            combined_pdf.save(output_bytes, garbage=4, deflate=True)
            combined_pdf.close()

            st.session_state["output_pdf"] = output_bytes.getvalue()
            status_text.empty()
            progress_bar.empty()
            st.success(f"✅ Success! Processed all **{total_pages_count} page(s)** cleanly.")

        except Exception as e:
            st.error(f"An error occurred during processing: {str(e)}")

    if "output_pdf" in st.session_state:
        st.download_button(
            label="📥 Download Clean Dummy Report PDF",
            data=st.session_state["output_pdf"],
            file_name="TruMed_Clean_Dummy_Report.pdf",
            mime="application/pdf",
        )
