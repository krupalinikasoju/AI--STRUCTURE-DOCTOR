import streamlit as st
from PIL import Image, ImageEnhance, ImageFilter, ImageDraw
from io import BytesIO
from datetime import datetime
import numpy as np

st.set_page_config(page_title="Structure Doctor AI", page_icon="🏗️", layout="wide")

# ---------- Theme ----------
st.markdown("""
<style>
.block-container {max-width: 1500px; padding-top: 1rem; padding-bottom: 2rem;}
.hero {background:linear-gradient(110deg,#092748,#10466f);color:#fff;border-radius:16px;padding:22px 26px;margin-bottom:14px;border:1px solid #1b4f77;}
.hero h1 {color:white;font-size:2.15rem;margin:0;}
.hero p {color:#d9eafa;margin:.35rem 0 0 0;}
.hero-right {border-left:2px solid #8db9d8;padding-left:18px;}
.stage {border:1px solid #cbdce9;border-radius:14px;padding:14px 16px;min-height:110px;background:#f6fbff;}
.stage h3 {font-size:1.05rem;color:#123b66;margin:0 0 8px 0;}
.panel {border:1px solid #d7e2ed;border-radius:14px;padding:15px;background:#fff;height:100%;}
.panel h3 {font-size:1.08rem;margin:0 0 8px 0;}
.panel p {font-size:.93rem;}
.panel-purple {background:#f7f3ff;border-color:#c9b8f5;}
.panel-green {background:#effbf5;border-color:#9bd9bd;}
.panel-pink {background:#fff1f5;border-color:#f2b7cb;}
.panel-yellow {background:#fff9e9;border-color:#ecd48a;}
.panel-blue {background:#eff8ff;border-color:#a8d9f2;}
.num {display:inline-flex;align-items:center;justify-content:center;background:#104b8f;color:white;border-radius:50%;width:38px;height:38px;font-weight:800;font-size:1.2rem;margin-right:8px;}
.reportbox {background:#0b2b4f;color:#fff;padding:15px;border-radius:12px;}
.reportbox h4 {color:white;margin:0 0 8px 0;}
.smallmuted {font-size:.82rem;color:#52657b;}
.flowarrow {text-align:center;font-size:1.7rem;font-weight:bold;color:#154b83;padding:0;margin:-4px 0;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
 <div style="display:flex;align-items:center;justify-content:space-between;gap:20px;flex-wrap:wrap">
  <div><h1>⌂ Structure Doctor <span style="color:#69d8ef">AI</span></h1>
  <p>Smart Crack Review &nbsp;|&nbsp; Image-Based Screening &nbsp;|&nbsp; Structural Inspection Report</p></div>
  <div class="hero-right"><b style="font-size:1.25rem">WORKFLOW</b><br>From building image to inspection report</div>
 </div>
</div>
""", unsafe_allow_html=True)
st.warning("Engineering safety note: a photograph alone cannot establish structural safety or predict a building's remaining safe life in years. This prototype provides image-specific visual screening, not a certified structural assessment. It does not replace an on-site inspection by a qualified structural engineer.")

# ---------- Helpers ----------
def enhance_image(img):
    img = ImageEnhance.Contrast(img).enhance(1.25)
    img = ImageEnhance.Sharpness(img).enhance(1.6)
    img = ImageEnhance.Color(img).enhance(0.92)
    return img.filter(ImageFilter.MedianFilter(size=3))

def make_review_overlay(img):
    """High-contrast edge visualization for manual review; not a trained crack detector."""
    base_img = img.convert("RGB").copy()
    arr = np.asarray(base_img).astype(np.float32)
    gray = arr.mean(axis=2)
    gy, gx = np.gradient(gray)
    edges = np.sqrt(gx * gx + gy * gy)
    cutoff = max(18, float(np.percentile(edges, 93)))
    mask = edges >= cutoff
    ys, xs = np.where(mask)
    draw = ImageDraw.Draw(base_img, "RGBA")
    if len(xs):
        stride = max(1, len(xs) // 1800)
        for x, y in zip(xs[::stride], ys[::stride]):
            draw.ellipse((int(x)-1, int(y)-1, int(x)+2, int(y)+2), fill=(245, 60, 58, 180))
    return base_img, int(mask.sum()), int(mask.size)

def classify_screening(width):
    if width is None or width <= 0:
        return ("Not assessed", "Enter a site-measured crack width to show a screening prompt.", "gray")
    if width < 0.3:
        return ("Lower width screening band", "Document and monitor; width alone does not prove the crack is harmless.", "green")
    if width < 1.0:
        return ("Professional review recommended", "Arrange a qualified assessment, especially if the crack is changing or recurring.", "orange")
    return ("Prompt professional assessment", "Do not infer safety from this image. Seek an on-site structural assessment promptly.", "red")

def build_pdf(project, findings, severity, stability_text, original=None, overlay=None):
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import mm
    except ImportError:
        return None
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=16*mm, leftMargin=16*mm, topMargin=14*mm, bottomMargin=14*mm)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="SDTitle", parent=styles["Title"], textColor=colors.HexColor("#0b2b4f"), alignment=0))
    story = [
        Paragraph("STRUCTURE DOCTOR AI", styles["SDTitle"]),
        Paragraph("Building Crack Inspection — Preliminary Screening Report", styles["Heading2"]),
        Paragraph("Generated: " + datetime.now().strftime("%d %b %Y, %H:%M"), styles["Normal"]),
        Spacer(1, 10)
    ]
    rows = [["Project details", "Value"],
            ["Building type", project["building_type"]],
            ["Number of floors", str(project["floors"])],
            ["Location", project["location"] or "Not supplied"],
            ["Observed area", project["area"]],
            ["Image file", project["filename"] or "No image"]]
    t = Table(rows, colWidths=[43*mm, 124*mm])
    t.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#0b2b4f")),
        ("TEXTCOLOR",(0,0),(-1,0),colors.white),
        ("GRID",(0,0),(-1,-1),.4,colors.HexColor("#b8cad9")),
        ("BACKGROUND",(0,1),(-1,-1),colors.HexColor("#f3f8fc")),
        ("PADDING",(0,0),(-1,-1),6)
    ]))
    story += [t, Spacer(1, 12), Paragraph("Screening summary", styles["Heading2"]),
              Paragraph("<b>Image screening status:</b> " + severity, styles["Normal"]),
              Paragraph("<b>Remaining safe life:</b> " + stability_text, styles["Normal"]),
              Spacer(1, 8), Paragraph("Findings and next steps", styles["Heading2"])]
    for f in findings:
        story.extend([Paragraph("• " + f, styles["Normal"]), Spacer(1, 4)])
    story += [Spacer(1, 10), Paragraph("Limitations", styles["Heading2"]),
              Paragraph("This is a prototype screening report. The image overlay highlights high-contrast edges and is not a validated AI crack detector. It does not calculate a building's remaining safe life or certify structural safety. Measurements are user-entered and must be verified on site. A qualified structural engineer must assess the building before repair or occupancy decisions.", styles["Normal"])]
    for label, image in [("Uploaded image", original), ("Review overlay", overlay)]:
        if image is not None:
            tmp = BytesIO()
            copy = image.copy()
            copy.thumbnail((1200, 800))
            copy.save(tmp, format="JPEG", quality=82)
            tmp.seek(0)
            story += [Spacer(1, 10), Paragraph(label, styles["Heading2"]), RLImage(tmp, width=145*mm, height=85*mm)]
    doc.build(story)
    return buf.getvalue()

# ---------- Step 1 ----------
st.markdown("## <span style='color:#1456a0'>1</span> Project Inputs", unsafe_allow_html=True)
i1, i2, i3 = st.columns([1.3, 1, 1])
with i1:
    upload = st.file_uploader("1. Upload a clear building / crack image", type=["jpg", "jpeg", "png", "webp"])
with i2:
    building_type = st.selectbox("2. Building type", ["Residential", "Commercial", "Industrial", "Institutional", "Other"])
    floors = st.number_input("3. Number of floors", 1, 100, 3)
with i3:
    location = st.text_input("Building location", placeholder="e.g. Telangana, Hyderabad")
    area = st.selectbox("Observed area", ["Wall - North side", "Wall - South side", "Beam", "Column", "Slab / ceiling", "Foundation", "Other"])

img = None
filename = ""
if upload:
    filename = upload.name
    try:
        img = Image.open(upload).convert("RGB")
        if img.width > 2200:
            new_h = int(img.height * 2200 / img.width)
            img = img.resize((2200, new_h))
    except Exception:
        st.error("Could not read the image. Upload a JPG or PNG file.")

st.markdown("<div class='flowarrow'>↓</div>", unsafe_allow_html=True)

# ---------- Step 2 ----------
st.markdown("## 2 · Image Processing")
if img:
    enhanced = enhance_image(img)
    a, b = st.columns(2)
    with a:
        st.markdown("<div class='panel panel-purple'><h3>Original Image</h3></div>", unsafe_allow_html=True)
        st.image(img, use_container_width=True)
    with b:
        st.markdown("<div class='panel panel-purple'><h3>Enhanced Image</h3></div>", unsafe_allow_html=True)
        st.image(enhanced, use_container_width=True)
else:
    st.info("Upload an image in Project Inputs to see the original and enhanced versions.")

st.markdown("<div class='flowarrow'>↓</div>", unsafe_allow_html=True)

# ---------- Step 3 and 4 ----------
c3, c4 = st.columns([1.05, 1])
with c3:
    st.markdown("<div class='panel panel-green'><h3>3 · AI-Based Crack Detection</h3><p>Image-specific edge review with a visual overlay.</p></div>", unsafe_allow_html=True)
    if img:
        overlay, edge_count, total_pixels = make_review_overlay(enhanced)
        st.image(overlay, caption="High-contrast edges for manual review — not AI detection", use_container_width=True)
        st.caption("The overlay can mark surface texture, joints, stains and shadows as well as cracks.")
    else:
        overlay = None
        st.caption("Upload an image to generate its review overlay.")
with c4:
    st.markdown("<div class='panel panel-pink'><h3>4 · Crack Measurement & Classification</h3><p>Enter measurements taken on site. The app does not infer physical dimensions from a photo without a scale reference.</p></div>", unsafe_allow_html=True)
    pattern = st.selectbox("Observed crack pattern", ["Not assessed", "Vertical", "Horizontal", "Diagonal", "Map / network", "Hairline / fine", "Multiple / irregular"])
    width = st.number_input("Measured crack width (mm)", min_value=0.0, max_value=100.0, value=0.0, step=0.1)
    length = st.number_input("Measured crack length (m)", min_value=0.0, max_value=1000.0, value=0.0, step=0.1)
    screening, screening_note, color = classify_screening(width)
    st.markdown(f"**Screening prompt:** :{color}[{screening}]")
    st.caption(screening_note)

st.markdown("<div class='flowarrow'>↓</div>", unsafe_allow_html=True)

# ---------- Step 5 and 6 ----------
left, right = st.columns([1, 1])
findings = []
if img:
    findings.append("An image was uploaded; lighting, focus, texture and image angle affect visual review.")
else:
    findings.append("No building image has been uploaded.")
if pattern != "Not assessed":
    findings.append(f"Selected observed pattern: {pattern.lower()} in {area.lower()}.")
if width > 0:
    findings.append(f"User-entered measured width: {width:.1f} mm; verify with a crack gauge on site.")
if length > 0:
    findings.append(f"User-entered measured length: {length:.1f} m; verify on site.")
findings += [
    "Photograph the crack with a ruler or crack gauge and record its location and date.",
    "Check whether the crack changes over time; recurring or widening cracks need professional review.",
    "A qualified structural engineer should investigate cracks near beams, columns, slabs or foundations, especially with movement, sagging, water ingress or falling concrete."
]
with left:
    st.markdown("<div class='panel panel-yellow'><h3>5 · Structural Assessment Report</h3></div>", unsafe_allow_html=True)
    st.metric("Screening category", screening)
    st.markdown("**Possible causes to investigate**")
    st.write("- Shrinkage or temperature movement")
    st.write("- Water ingress, poor curing or joint movement")
    st.write("- Settlement, corrosion or structural movement")
    st.caption("These are possibilities to investigate, not diagnoses from the photo.")
with right:
    st.markdown("<div class='panel panel-purple'><h3>6 · Recommended Repair & Safety Actions</h3></div>", unsafe_allow_html=True)
    st.markdown("**Recommended next steps**")
    st.write("- Document the crack and monitor changes.")
    st.write("- Do not conceal a changing crack before its cause is assessed.")
    st.write("- Ask a qualified structural engineer to specify repairs.")
    st.markdown("**Safety advice**")
    st.write("- If there is sudden movement, major sagging, falling concrete or rapid crack growth, keep people away from the affected area and seek urgent professional help.")

st.markdown("<div class='flowarrow'>↓</div>", unsafe_allow_html=True)

# ---------- Life estimate and final report ----------
st.markdown("## 7 · Final Inspection Report")
st.markdown("<div class='panel panel-blue'><h3>Building stability / remaining safe life</h3></div>", unsafe_allow_html=True)
st.error("Remaining safe life in years: NOT DETERMINABLE from a photograph alone. A numeric estimate here would be misleading. It requires an on-site structural inspection, crack history and movement monitoring, member details, material condition, loading, foundation/settlement information and engineering analysis.")
st.write("**Suggested urgency from the information entered:**")
if width >= 1.0 or pattern == "Diagonal" or area in ["Beam", "Column", "Foundation"]:
    st.warning("Arrange a prompt assessment by a qualified structural engineer. The selected member/location or entered width is a reason to obtain professional review, not a diagnosis of failure.")
elif width > 0:
    st.info("Document the crack and arrange professional advice if it is recurring, widening, damp, or associated with movement. Width alone cannot establish safety.")
else:
    st.info("Enter a site-measured crack width and observed pattern for a basic screening prompt. This still cannot estimate safe life in years.")

project = {"building_type": building_type, "floors": int(floors), "location": location.strip(), "area": area, "filename": filename}
st.markdown("### Report preview")
p1, p2 = st.columns(2)
with p1:
    st.write(f"**Building:** {building_type} · {floors} floor(s)")
    st.write(f"**Location:** {location.strip() or 'Not supplied'}")
    st.write(f"**Observed area:** {area}")
    st.write(f"**Crack pattern:** {pattern}")
with p2:
    st.write(f"**Measured width:** {width:.1f} mm" if width > 0 else "**Measured width:** Not supplied")
    st.write(f"**Measured length:** {length:.1f} m" if length > 0 else "**Measured length:** Not supplied")
    st.write(f"**Screening category:** {screening}")
    st.write("**AI confidence:** Not available — no validated model is connected.")
with st.expander("View findings included in the report", expanded=True):
    for f in findings:
        st.write("• " + f)

pdf = build_pdf(project, findings, screening, "Not determinable from image alone; an engineer's assessment is required.", img, overlay if img else None)
if pdf:
    st.download_button("⬇️ Save Final Inspection Report as PDF", data=pdf, file_name="structure_doctor_inspection_report.pdf", mime="application/pdf", type="primary")
else:
    st.error("PDF support is missing. Install packages using: py -m pip install -r requirements.txt")
if img:
    image_bytes = BytesIO()
    overlay.save(image_bytes, format="PNG")
    st.download_button("⬇️ Download highlighted review image", data=image_bytes.getvalue(), file_name="crack_review_overlay.png", mime="image/png")

st.caption("Structure Doctor AI • Streamlit prototype • Image-specific screening; not a structural certification tool.")
