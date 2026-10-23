import base64
import io
import os
import fitz  # PyMuPDF
import streamlit as st
import openai  # Requires: pip install openai

# ==========================================
# 1. STREAMLIT CONFIG & API SETUP
# ==========================================
st.set_page_config(
    page_title="TruMed Path Labs - Vision AI Dummy Generator",
    page_icon="🤖",
    layout="wide",
)

st.title("🧪 TruMed Path Labs - Vision AI Report Scrubber")
st.write("Upload your lab reports to let AI visually inspect, redact PII, and apply professional branding.")

# Secure API Key input in sidebar
with st.sidebar:
    st.header("🔑 AI Configuration")
    api_key = st.text_input("Enter OpenAI API Key", type="password")
    if api_key:
        openai.api_key = api_key
    st.markdown("---")
    st.info("This tool renders pages as images and uses Vision AI to intelligently locate PII and signature blocks.")

# Load logo safely if present
logo_html = ""
logo_path = "logo.png"
if not os.path.exists(logo_path) and os.path.exists("logo.png.jpg"):
    logo_path = "logo.png.jpg"

if os.path.exists(logo_path):
    with open(logo_path, "rb") as image_file:
        encoded_logo = base64.b64encode(image_file.read()).decode()
    logo_html = f'<img src="data:image/png;base64,{encoded_logo}" style="max-height: 85px; background: white; padding: 10px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">'


# ==========================================
# 2. VISION AI DETECTION & REDACTION ENGINE
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

def vision_ai_detect_and_redact(page, client):
    """Sends page image to Vision AI to identify PII text fragments, then redacts them."""
    
    # Render PDF page to high-res PNG image bytes
    pix = page.get_pixmap(dpi=150)
    img_bytes = pix.tobytes("png")
    base64_image = base64.b64encode(img_bytes).decode('utf-8')

    # Prompt the Vision AI to find exact sensitive text strings to redact
    prompt = (
        "Analyze this medical lab report image. Identify all Personally Identifiable Information (PII) "
        "that needs redaction for client review demonstrations. Specifically look for:\n"
        "1. Real patient names\n"
        "2. Referring doctor names or customer names\n"
        "3. TPL Codes, SID numbers, or PID numbers\n"
        "4. Pathologist names or signatures at the bottom\n\n"
        "Return ONLY the exact text strings found on the page that correspond to these sensitive values, "
        "formatted as a Python list of strings (e.g., [\"Patient Name Value\", \"Doctor Name\", \"SID Number\"]). "
        "Do not include labels like 'Patient Name:', only return the actual sensitive values."
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/png;base64,{base64_image}"}
                        }
                    ]
                }
            ],
            max_tokens=300
        )
        
        ai_content = response.choices[0].message.content
        # Simple parser to extract list items from AI text output
        import ast
        # Clean up code blocks if model returned markdown
        cleaned_text = ai_content.replace("```python", "").replace("```", "").strip()
        sensitive_phrases = ast.literal_eval(cleaned_text)
        
        if isinstance(sensitive_phrases, list):
            for phrase in sensitive_phrases:
                matches = page.search_for(phrase)
                for inst in matches:
                    page.add_redact_annot(inst, fill=(1, 1, 1))
            page.apply_redactions()

    except Exception as e:
        # Fallback keyword approach if Vision API fails or key is missing
        st.warning(f"Vision AI call skipped/failed on page: {str(e)}. Using fallback safety scrubber.")
        for keyword in ["Patient Name", "Ref.Doctor", "SID/PID"]:
            matches = page.search_for(keyword)
            for m in matches:
                val_box = fitz.Rect(m.x1, m.y0 - 2, m.x1 + 120, m.y1 + 2)
                page.add_redact_annot(val_box, fill=(1, 1, 1))
        page.apply_redactions()

    # Apply Margin Watermark Banner
    apply_margin_watermark(page)


# ==========================================
# 3. STREAMLIT DASHBOARD EXECUTION
# ==========================================
uploaded_files = st.file_uploader("Upload Lab Report PDFs", type=["pdf"], accept_multiple_files=True)

if uploaded_files:
    if not api_key:
        st.error("⚠️ Please enter your OpenAI API key in the sidebar to enable Vision AI processing.")
    elif st.button("🤖 Run Vision AI Processing"):
        client = openai.OpenAI(api_key=api_key)
        progress_bar = st.progress(0)
        status_text = st.empty()

        try:
            combined_pdf = fitz.open()
            total_pages = sum(len(fitz.open(stream=f.read(), filetype="pdf")) for f in uploaded_files)
            for f in uploaded_files: f.seek(0)

            current_page = 0
            for uploaded_file in uploaded_files:
                doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
                for page_num in range(len(doc)):
                    status_text.text(f"Vision AI inspecting page {current_page + 1} of {total_pages}...")
                    page = doc[page_num]
                    vision_ai_detect_and_redact(page, client)
                    combined_pdf.insert_pdf(doc, from_page=page_num, to_page=page_num)
                    current_page += 1
                    progress_bar.progress(current_page / total_pages)

            output_bytes = io.BytesIO()
            combined_pdf.save(output_bytes, garbage=4, deflate=True)
            combined_pdf.close()

            st.session_state["vision_output"] = output_bytes.getvalue()
            status_text.empty()
            progress_bar.empty()
            st.success("✅ Vision AI Processing Complete!")

        except Exception as e:
            st.error(f"Processing error: {str(e)}")

    if "vision_output" in st.session_state:
        st.download_button(
            label="📥 Download Vision-AI Scrubbed PDF",
            data=st.session_state["vision_output"],
            file_name="TruMed_VisionAI_Dummy_Report.pdf",
            mime="application/pdf",
        )
