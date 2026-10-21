import io
import os
import fitz  # PyMuPDF
import streamlit as st

# ==========================================
# 1. STREAMLIT PAGE CONFIGURATION & STYLING
# ==========================================
st.set_page_config(
    page_title="TruMed Path Labs - Dummy Report Generator",
    page_icon="🧪",
    layout="wide",
)

# Load logo safely if available
logo_html = ""
logo_path = "logo.png"
if not os.path.exists(logo_path) and os.path.exists("logo.png.jpg"):
    logo_path = "logo.png.jpg"

if os.path.exists(logo_path):
    import base64

    with open(logo_path, "rb") as image_file:
        encoded_logo = base64.b64encode(image_file.read()).decode()
    logo_html = f'<img src="data:image/png;base64,{encoded_logo}" style="max-height: 85px; background: white; padding: 10px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">'

# Render custom UI banner
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
# 2. CORE PDF PROCESSING LOGIC
# ==========================================
def process_metadata_field(page, keyword, new_value, x_offset=2, width=150):
    """Helper function to search for a metadata keyword, redact its old value,

    and write the new dummy value cleanly in place.
    """
    matches = page.search_for(keyword)
    if matches:
        r = matches[0]
        # Define rectangle covering the old value space next to the label
        old_box = fitz.Rect(r.x1 + x_offset, r.y0 - 1, r.x1 + width, r.y1 + 1)
        page.add_redact_annot(old_box, fill=(1, 1, 1))
        page.apply_redactions()

        # Write the new dummy value
        page.insert_text(
            fitz.Point(r.x1 + x_offset + 3, r.y1 - 1),
            new_value,
            fontsize=9,
            fontname="helv",
            color=(0, 0, 0),
        )


def process_report_page(page):
    """Processes a single page:

    1. Updates Patient Name, Ref.Customer, TPL Code, and SID/PID.
    2. Erases bottom signatures, doctor sign-offs, and QR verification notes.
    """
    rect = page.rect

    # --- STEP 1: IN-PLACE SURGICAL METADATA UPDATES ---
    process_metadata_field(page, "Patient Name", ": Mr DUMMY", width=180)
    process_metadata_field(page, "Ref.Customer", ": XXX", width=100)
    process_metadata_field(page, "TPL Code", ": XXX", width=100)
    process_metadata_field(page, "SID/PID", ": XXX", width=100)

    # --- STEP 2: REMOVE BOTTOM SIGNATURES, DOCTOR DETAILS & QR CODES ---
    # Wipes everything from 110 points above the bottom margin down to the bottom
    footer_wipe_start = rect.height - 110
    footer_wipe_rect = fitz.Rect(0, footer_wipe_start, rect.width, rect.height)
    page.add_redact_annot(footer_wipe_rect, fill=(1, 1, 1))

    # Also clean up any top QR code badge ("scan to download") if present
    top_qr_rects = page.search_for("scan to download")
    if top_qr_rects:
        qr_r = top_qr_rects[0]
        qr_box = fitz.Rect(qr_r.x0 - 5, qr_r.y0 - 45, qr_r.x1 + 5, qr_r.y1 + 5)
        page.add_redact_annot(qr_box, fill=(1, 1, 1))

    page.apply_redactions()


# ==========================================
# 3. STREAMLIT FILE UPLOADER & UI DASHBOARD
# ==========================================
st.subheader("📁 Upload Lab Reports")
st.write(
    "Upload your original PDF report(s) below to automatically sanitize patient details and remove signatures/QR codes."
)

uploaded_files = st.file_uploader(
    "Drag and drop PDF files here", type=["pdf"], accept_multiple_files=True
)

if uploaded_files:
    st.info(
        f"📋 **{len(uploaded_files)} file(s)** uploaded and ready for processing."
    )

    if st.button("🚀 Process & Generate Clean Dummy PDF"):
        with st.spinner(
            "Executing surgical metadata updates and removing signatures..."
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

            # Save to memory bytes container
            output_bytes = io.BytesIO()
            combined_pdf.save(output_bytes)
            combined_pdf.close()

            st.success(
                f"✅ Done! Successfully processed all **{total_pages} page(s)**."
            )

            # Download button for the output file
            st.download_button(
                label="📥 Download Processed Dummy Report PDF",
                data=output_bytes.getvalue(),
                file_name="TruMed_Dummy_Report_Clean.pdf",
                mime="application/pdf",
            )
