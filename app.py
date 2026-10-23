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
                <div class="banner-subtitle">Professional Dummy Report Generator</div>
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
# 2. XXXXX REDACTION & ERASURE ENGINE
# ==========================================
def apply_margin_watermark(page):
    """Applies a professional banner watermark in the top margin at 25% opacity."""
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
    """Erase/strike out sensitive fields and put XXXXX for Patient Name and SID/PID."""
    
    # 1. Wipe the entire patient info zone cleanly to remove doctors, dates, and extra metadata
    metadata_box = fitz.Rect(30, 92, 575, 145)
    page.add_redact_annot(metadata_box, fill=(1, 1, 1))

    # 2. Erase/strike out any stray sensitive labels appearing across pages
    for stray_keyword in ["Ref.Doctor", "Ref.Customer", "Collected on", "Registered on", "Reported on"]:
        stray_matches = page.search_for(stray_keyword)
        for sm in stray_matches:
            stray_box = fitz.Rect(sm.x0 - 2, sm.y0 - 2, sm.x1 + 180, sm.y1 + 2)
            page.add_redact_annot(stray_box, fill=(1, 1, 1))

    # 3. Redact pathologist/doctor signatures at the bottom
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

    # Commit redactions (erasing everything targeted)
    page.apply_redactions()

    # 4. Stamp back ONLY Patient Name and SID/PID as XXXXX cleanly
    page.insert_text(fitz.Point(35, 105), "Patient Name : XXXXX", fontsize=9, fontname="Helvetica-Bold", color=(0, 0, 0))
    page.insert_text(fitz.Point(35, 120), "SID/PID      : XXXXX", fontsize=9, fontname="Helvetica-Bold", color=(0, 0, 0))
    page.insert_text(fitz.Point(320, 105), "Sample Type  : Serum", fontsize=9, fontname="Helvetica", color=(0, 0, 0))

    # 5. Apply Margin Watermark Banner
    apply_margin_watermark(page)


# ==========================================
# 3. STREAMLIT FILE PROCESSING DASHBOARD
# ==========================================
st.subheader("📁 Upload Lab Reports")
st.write("Upload original lab reports to generate clean dummy PDFs with XXXXX masking.")

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
            
            doc_list = []
            total_pages_count = 0
            for uploaded_file in uploaded_files:
                d = fitz.open(stream=uploaded_file.read(), filetype="pdf")
                doc_list.append(d)
                total_pages_count += len(d)

            current_page = 0
            for doc in doc_list:
                for page_num in range(len(doc)):
                    status_text.text(f"Processing page {current_page + 1} of {total_pages_count}...")
                    page = doc[page_num]
                    process_report_page(page)
                    combined_pdf.insert_pdf(doc, from_page=page_num, to_page=page_num)
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
            file_name="TruMed_XXXXX_Dummy_Report.pdf",
            mime="application/pdf",
        )
