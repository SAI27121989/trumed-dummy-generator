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

# --- HEADER SECTION (Using Native Streamlit for zero errors) ---
col_logo, col_text, col_badge = st.columns([1, 4, 1.5])

with col_logo:
    # Checks for either logo.png or logo.png.jpg
    logo_path = "logo.png"
    if not os.path.exists(logo_path) and os.path.exists("logo.png.jpg"):
        logo_path = "logo.png.jpg"

    if os.path.exists(logo_path):
        st.image(logo_path, width=90)

with col_text:
    st.markdown(
        "### **TruMed Path Labs India Pvt Ltd.**\n"
        "📍 Central Lab: Plot No. 32, Umakanth Arcade, Vasavi Nagar Colony, Secunderabad - 500015  \n"
        "📞 Helpline: +91 7036363689"
    )

with col_badge:
    st.markdown(
        "<div style='background-color: #FF9F00; color: #0F172A; text-align: center; font-weight: 800; padding: 10px 15px; border-radius: 20px; font-size: 13px; margin-top: 10px;'>🏅 NABL ACCREDITED LAB</div>",
        unsafe_allow_html=True,
    )

st.divider()


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
