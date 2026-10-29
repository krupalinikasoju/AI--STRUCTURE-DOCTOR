
import html
from io import BytesIO
from datetime import datetime

import streamlit as st
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageDraw

# PDF report imports
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        Image as PDFImage, PageBreak
    )
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Structure Doctor AI",
    page_icon="🏗️",
    layout="wide"
)

# ============================================================
# ORIGINAL DASHBOARD STYLE
# ============================================================

st.markdown("""
<style>
.stApp {
    background: #f3f7fc;
    color: #172b4d;
}
.block-container {
    padding-top: 1.5rem;
    padding-bottom: 3rem;
    max-width: 1400px;
}
.hero {
    background: linear-gradient(120deg, #082f62, #0879bd);
    padding: 30px;
    border-radius: 18px;
    color: white;
    margin-bottom: 24px;
    box-shadow: 0 8px 24px rgba(0, 45, 95, 0.16);
}
.hero h1 {
    color: white;
    font-size: 2.35rem;
    margin-bottom: 8px;
}
.hero p {
    color: #e0efff;
    font-size: 1.02rem;
}
.stage {
    background: white;
    border: 1px solid #dbe6f2;
    border-radius: 14px;
    padding: 18px;
    margin-bottom: 14px;
}
.stage-title {
    color: #075985;
    font-size: 1.25rem;
    font-weight: 750;
    margin-bottom: 8px;
}
.small-note {
    color: #64748b;
    font-size: 0.9rem;
}
.metric-card {
    background: white;
    border: 1px solid #dbe6f2;
    border-radius: 12px;
    padding: 16px;
}
</style>
""", unsafe_allow_html=True)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def enhance_image(img):
    """Improve image visibility; this does not diagnose cracks."""
    img = ImageEnhance.Contrast(img).enhance(1.35)
    img = ImageEnhance.Sharpness(img).enhance(1.7)
    img = ImageEnhance.Color(img).enhance(0.85)
    return img.filter(ImageFilter.MedianFilter(size=3))


def make_review_overlay(img):
    """
    Create an edge-visualization overlay.
    This is not a trained crack detector and does not identify
    cracks automatically.
    """
    rgb = img.convert("RGB")
    edges = rgb.filter(ImageFilter.FIND_EDGES).convert("L")
    edges = edges.point(lambda p: 255 if p > 35 else 0)

    overlay = Image.new("RGBA", rgb.size, (0, 0, 0, 0))
    edge_pixels = edges.load()
    draw = ImageDraw.Draw(overlay)

    width, height = rgb.size
    step = max(1, min(width, height) // 500)

    for y in range(0, height, step):
        for x in range(0, width, step):
            if edge_pixels[x, y] > 0:
                draw.rectangle(
                    (x, y, min(x + step, width - 1),
                     min(y + step, height - 1)),
                    fill=(255, 60, 60, 170)
                )

    return Image.alpha_composite(rgb.convert("RGBA"), overlay).convert("RGB")


def classify_screening(width_mm):
    """
    Simple preliminary width screening bands.
    These bands are not a structural safety assessment and
    are not a substitute for applicable code requirements.
    """
    if width_mm is None:
        return (
            "Not assessed",
            "Enter an observed crack width if it can be measured reliably."
        )

    if width_mm < 0:
        return (
            "Invalid input",
            "Crack width cannot be negative."
        )

    if width_mm < 0.3:
        return (
            "Lower-width screening band",
            "Record and monitor the crack. Its cause and significance "
            "cannot be determined from width alone."
        )

    if width_mm < 1.0:
        return (
            "Further assessment recommended",
            "Arrange an on-site inspection, especially if the crack is "
            "growing, leaking, diagonal, or near a beam-column joint."
        )

    return (
        "Prompt professional assessment recommended",
        "Arrange prompt inspection by a qualified structural engineer. "
        "If the crack is sudden, widening, associated with displacement, "
        "or accompanied by unusual sounds or deformation, keep people "
        "away from the affected area and seek urgent professional help."
    )


def calculate_loads(
    length_m,
    width_m,
    floors,
    floor_height_m,
    slab_thickness_mm,
    concrete_density,
    floor_finish,
    wall_allowance,
    live_load,
    other_dead_load
):
    """
    Simplified preliminary floor-area load estimate.

    It does NOT calculate beam/column reactions, bending moments,
    shear, reinforcement, foundations, wind or seismic forces.
    """
    area_m2 = length_m * width_m
    total_height_m = floors * floor_height_m

    slab_thickness_m = slab_thickness_mm / 1000.0
    slab_self_weight = slab_thickness_m * concrete_density

    dead_load_kpa = (
        slab_self_weight
        + floor_finish
        + wall_allowance
        + other_dead_load
    )

    service_load_kpa = dead_load_kpa + live_load

    dead_load_per_floor_kn = area_m2 * dead_load_kpa
    live_load_per_floor_kn = area_m2 * live_load
    service_load_per_floor_kn = area_m2 * service_load_kpa

    total_dead_load_kn = floors * dead_load_per_floor_kn
    total_live_load_kn = floors * live_load_per_floor_kn
    total_service_load_kn = floors * service_load_per_floor_kn

    return {
        "area_m2": area_m2,
        "total_height_m": total_height_m,
        "slab_self_weight_kpa": slab_self_weight,
        "dead_load_kpa": dead_load_kpa,
        "live_load_kpa": live_load,
        "service_load_kpa": service_load_kpa,
        "dead_load_per_floor_kn": dead_load_per_floor_kn,
        "live_load_per_floor_kn": live_load_per_floor_kn,
        "service_load_per_floor_kn": service_load_per_floor_kn,
        "total_dead_load_kn": total_dead_load_kn,
        "total_live_load_kn": total_live_load_kn,
        "total_service_load_kn": total_service_load_kn,
    }


def make_load_summary(project, load):
    return f"""
PRELIMINARY RCC LOAD ESTIMATE

Location: {project['location']}
Building type: {project['building_type']}
Number of floors: {project['floors']}
Floor-to-floor height: {project['floor_height_m']:.2f} m
Approximate total height: {load['total_height_m']:.2f} m
Assumed rectangular floor dimensions:
{project['length_m']:.2f} m x {project['width_m']:.2f} m

Floor area = length x width
           = {project['length_m']:.2f} x {project['width_m']:.2f}
           = {load['area_m2']:.2f} m²

Slab self-weight = slab thickness x concrete unit weight
                 = {project['slab_thickness_mm']:.0f}/1000
                   x {project['concrete_density']:.2f}
                 = {load['slab_self_weight_kpa']:.2f} kN/m²

Estimated dead load intensity =
    slab self-weight + finishes + wall allowance + other dead load
  = {load['slab_self_weight_kpa']:.2f}
    + {project['floor_finish']:.2f}
    + {project['wall_allowance']:.2f}
    + {project['other_dead_load']:.2f}
  = {load['dead_load_kpa']:.2f} kN/m²

Assumed live load intensity = {load['live_load_kpa']:.2f} kN/m²

Estimated service load intensity = dead load + live load
                                 = {load['service_load_kpa']:.2f} kN/m²

Estimated dead load per floor =
    floor area x dead load intensity
  = {load['dead_load_per_floor_kn']:.2f} kN

Estimated live load per floor =
    floor area x live load intensity
  = {load['live_load_per_floor_kn']:.2f} kN

Estimated service load per floor =
    floor area x service load intensity
  = {load['service_load_per_floor_kn']:.2f} kN

Simplified sum across {project['floors']} floors:
Dead load total = {load['total_dead_load_kn']:.2f} kN
Live load total = {load['total_live_load_kn']:.2f} kN
Service load total = {load['total_service_load_kn']:.2f} kN

IMPORTANT:
These are simplified floor-area estimates only. They are not column
loads, foundation loads, member design forces, or a complete analysis.
Actual load paths, walls, beams, columns, stairs, roof, tanks, equipment,
openings, load combinations, wind and seismic effects are not fully
modelled. Inputs must be verified by a qualified structural engineer.
"""


def build_pdf(project, findings, severity, stability_text, load_summary,
              code_references, original=None, overlay=None):
    if not PDF_AVAILABLE:
        raise RuntimeError(
            "PDF support is unavailable. Install reportlab using "
            "'pip install reportlab'."
        )

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=17 * mm,
        leftMargin=17 * mm,
        topMargin=16 * mm,
        bottomMargin=16 * mm
    )

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="ReportHeading",
        parent=styles["Heading1"],
        textColor=colors.HexColor("#075985"),
        spaceAfter=8
    ))
    styles.add(ParagraphStyle(
        name="ReportSmall",
        parent=styles["BodyText"],
        fontSize=8,
        leading=11
    ))

    story = []

    def add_para(text, style="BodyText"):
        safe_text = html.escape(str(text)).replace("\n", "<br/>")
        story.append(Paragraph(safe_text, styles[style]))
        story.append(Spacer(1, 5))

    story.append(Paragraph(
        "Structure Doctor AI",
        styles["ReportHeading"]
    ))
    add_para("Combined preliminary RCC load estimate and crack screening report")
    add_para("Generated: " + datetime.now().strftime("%d-%m-%Y %H:%M"))
    story.append(Spacer(1, 8))

    story.append(Paragraph("1. Project Details", styles["Heading2"]))
    project_rows = [
        ["Parameter", "Value"],
        ["Location", project["location"]],
        ["Building type", project["building_type"]],
        ["Floors", str(project["floors"])],
        ["Floor-to-floor height", f'{project["floor_height_m"]:.2f} m'],
        ["Approximate total height", f'{project["floor_height_m"] * project["floors"]:.2f} m'],
        ["Assumed floor dimensions",
         f'{project["length_m"]:.2f} m x {project["width_m"]:.2f} m'],
        ["Floor area", f'{project["length_m"] * project["width_m"]:.2f} m²'],
    ]

    table = Table(project_rows, colWidths=[60 * mm, 105 * mm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#075985")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cbd5e1")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(table)
    story.append(Spacer(1, 12))

    story.append(Paragraph("2. Preliminary RCC Load Estimate", styles["Heading2"]))
    add_para(load_summary, "ReportSmall")

    story.append(Paragraph("3. Crack Screening", styles["Heading2"]))
    add_para("Screening category: " + severity)
    add_para("Observed progression: " + project["progression"])
    add_para("Water ingress: " + project["water_ingress"])
    add_para("Observed location: " + project["observed_area"])
    add_para("Notes/findings: " + (findings or "No additional notes entered."))
    add_para("Screening guidance: " + stability_text)

    if original is not None:
        try:
            story.append(Paragraph("Uploaded Image", styles["Heading3"]))
            image_buffer = BytesIO()
            original.convert("RGB").save(image_buffer, format="JPEG")
            image_buffer.seek(0)
            story.append(PDFImage(
                image_buffer,
                width=75 * mm,
                height=55 * mm,
                kind="proportional"
            ))
            story.append(Spacer(1, 8))
        except Exception:
            add_para("Original image could not be embedded.")

    if overlay is not None:
        try:
            story.append(Paragraph("Image Edge-Visualization Overlay", styles["Heading3"]))
            overlay_buffer = BytesIO()
            overlay.convert("RGB").save(overlay_buffer, format="JPEG")
            overlay_buffer.seek(0)
            story.append(PDFImage(
                overlay_buffer,
                width=75 * mm,
                height=55 * mm,
                kind="proportional"
            ))
            story.append(Spacer(1, 8))
        except Exception:
            add_para("Overlay image could not be embedded.")

    story.append(Paragraph("4. Reference Standards", styles["Heading2"]))
    add_para(code_references, "ReportSmall")

    story.append(Paragraph("5. Limitations and Safety", styles["Heading2"]))
    add_para(
        "This report is a preliminary screening and simplified load estimate. "
        "The image overlay is edge visualization, not a validated crack detector. "
        "A photograph cannot establish the cause of a crack, structural capacity, "
        "or remaining building life. This report does not provide reinforcement "
        "design, member capacity verification, foundation design, or a full "
        "wind/seismic analysis. Verify the applicable editions, amendments, "
        "occupancy loads, site conditions, drawings and measurements with a "
        "qualified structural engineer before making repair or safety decisions."
    )

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


# ============================================================
# HEADER
# ============================================================

st.markdown("""
<div class="hero">
    <h1>🏗️ Structure Doctor AI</h1>
    <p>Building condition screening, preliminary RCC load estimation,
    crack review and combined engineering report.</p>
</div>
""", unsafe_allow_html=True)

st.info(
    "Engineering prototype: image processing and load estimates are preliminary. "
    "They do not replace an on-site structural inspection or a signed engineering design."
)


# ============================================================
# STEP 1 — PROJECT INPUTS
# ============================================================

st.markdown('<div class="stage">', unsafe_allow_html=True)
st.markdown(
    '<div class="stage-title">STEP 1 — Project Inputs</div>',
    unsafe_allow_html=True
)

col1, col2, col3 = st.columns(3)

with col1:
    building_type = st.selectbox(
        "Building type",
        ["Residential RCC", "Commercial RCC", "Institutional RCC", "Other RCC"]
    )
    location = st.text_input(
        "Building location",
        value="Hyderabad, Telangana"
    )
    floors = st.number_input(
        "Number of floors",
        min_value=1,
        max_value=100,
        value=3,
        step=1
    )

with col2:
    floor_height_m = st.number_input(
        "Floor-to-floor height (m)",
        min_value=2.0,
        max_value=6.0,
        value=3.0,
        step=0.1
    )
    length_m = st.number_input(
        "Approximate floor length (m)",
        min_value=1.0,
        max_value=500.0,
        value=12.0,
        step=0.5
    )
    width_m = st.number_input(
        "Approximate floor width (m)",
        min_value=1.0,
        max_value=500.0,
        value=10.0,
        step=0.5
    )

with col3:
    observed_area = st.selectbox(
        "Area being inspected",
        [
            "Beam",
            "Column",
            "Slab",
            "Beam-column joint",
            "Wall",
            "Staircase",
            "Foundation/plinth",
            "Unknown"
        ]
    )
    crack_progression = st.selectbox(
        "Crack progression",
        ["Unknown", "No known change", "Widening", "Sudden change"]
    )
    water_ingress = st.selectbox(
        "Water ingress",
        ["Unknown", "Not observed", "Present"]
    )

st.markdown('</div>', unsafe_allow_html=True)


# ============================================================
# PRELIMINARY RCC LOAD INPUTS
# ============================================================

st.markdown('<div class="stage">', unsafe_allow_html=True)
st.markdown(
    '<div class="stage-title">RCC Load Calculation Inputs</div>',
    unsafe_allow_html=True
)
st.caption(
    "Defaults are illustrative assumptions, not verified design values. "
    "Edit them to match the actual drawings, occupancy and site conditions."
)

c1, c2, c3 = st.columns(3)

with c1:
    slab_thickness_mm = st.number_input(
        "Assumed slab thickness (mm)",
        min_value=75.0,
        max_value=400.0,
        value=125.0,
        step=5.0
    )
    concrete_density = st.number_input(
        "Concrete unit weight (kN/m³)",
        min_value=10.0,
        max_value=30.0,
        value=25.0,
        step=0.5
    )

with c2:
    floor_finish = st.number_input(
        "Floor finish allowance (kN/m²)",
        min_value=0.0,
        max_value=5.0,
        value=1.0,
        step=0.1
    )
    wall_allowance = st.number_input(
        "Wall/partition allowance (kN/m²)",
        min_value=0.0,
        max_value=10.0,
        value=1.0,
        step=0.1
    )

with c3:
    live_load = st.number_input(
        "Assumed live load (kN/m²)",
        min_value=0.0,
        max_value=10.0,
        value=2.0,
        step=0.1
    )
    other_dead_load = st.number_input(
        "Other dead load allowance (kN/m²)",
        min_value=0.0,
        max_value=10.0,
        value=0.0,
        step=0.1
    )

st.markdown('</div>', unsafe_allow_html=True)


project = {
    "building_type": building_type,
    "location": location,
    "floors": int(floors),
    "floor_height_m": float(floor_height_m),
    "length_m": float(length_m),
    "width_m": float(width_m),
    "observed_area": observed_area,
    "progression": crack_progression,
    "water_ingress": water_ingress,
    "slab_thickness_mm": float(slab_thickness_mm),
    "concrete_density": float(concrete_density),
    "floor_finish": float(floor_finish),
    "wall_allowance": float(wall_allowance),
    "live_load": float(live_load),
    "other_dead_load": float(other_dead_load),
}

load = calculate_loads(
    length_m=float(length_m),
    width_m=float(width_m),
    floors=int(floors),
    floor_height_m=float(floor_height_m),
    slab_thickness_mm=float(slab_thickness_mm),
    concrete_density=float(concrete_density),
    floor_finish=float(floor_finish),
    wall_allowance=float(wall_allowance),
    live_load=float(live_load),
    other_dead_load=float(other_dead_load)
)

load_summary = make_load_summary(project, load)


# ============================================================
# LOAD ESTIMATE RESULTS
# ============================================================

st.markdown('<div class="stage">', unsafe_allow_html=True)
st.markdown(
    '<div class="stage-title">Preliminary Load Estimate Results</div>',
    unsafe_allow_html=True
)

m1, m2, m3 = st.columns(3)

with m1:
    st.metric("Floor area", f"{load['area_m2']:.2f} m²")
with m2:
    st.metric("Estimated dead load intensity", f"{load['dead_load_kpa']:.2f} kN/m²")
with m3:
    st.metric("Estimated service load intensity", f"{load['service_load_kpa']:.2f} kN/m²")

m4, m5, m6 = st.columns(3)

with m4:
    st.metric(
        "Service load per floor",
        f"{load['service_load_per_floor_kn']:.2f} kN"
    )
with m5:
    st.metric(
        "Simplified dead load sum",
        f"{load['total_dead_load_kn']:.2f} kN"
    )
with m6:
    st.metric(
        "Simplified service load sum",
        f"{load['total_service_load_kn']:.2f} kN"
    )

with st.expander("View formulas and assumptions"):
    st.code(load_summary, language="text")

st.warning(
    "These values are area-based estimates only. They are not column reactions, "
    "foundation loads, member design forces, or a verification that the building is safe."
)
st.markdown('</div>', unsafe_allow_html=True)


# ============================================================
# STEP 2 — IMAGE PROCESSING
# ============================================================

st.markdown('<div class="stage">', unsafe_allow_html=True)
st.markdown(
    '<div class="stage-title">STEP 2 — Image Processing</div>',
    unsafe_allow_html=True
)

uploaded_file = st.file_uploader(
    "Upload a crack or structural-condition photograph",
    type=["png", "jpg", "jpeg"]
)

original_image = None
enhanced_image = None
overlay_image = None

if uploaded_file is not None:
    try:
        original_image = Image.open(uploaded_file).convert("RGB")
        enhanced_image = enhance_image(original_image)
        overlay_image = make_review_overlay(enhanced_image)

        image_col1, image_col2 = st.columns(2)
        with image_col1:
            st.image(
                original_image,
                caption="Original uploaded image",
                use_container_width=True
            )
        with image_col2:
            st.image(
                enhanced_image,
                caption="Enhanced image for visual review",
                use_container_width=True
            )
    except Exception as exc:
        st.error(f"Could not process the uploaded image: {exc}")

st.markdown('</div>', unsafe_allow_html=True)


# ============================================================
# STEP 3 — CRACK SCREENING OVERLAY
# ============================================================

st.markdown('<div class="stage">', unsafe_allow_html=True)
st.markdown(
    '<div class="stage-title">STEP 3 — Crack Overlay / Visual Screening</div>',
    unsafe_allow_html=True
)

if overlay_image is not None:
    st.image(
        overlay_image,
        caption="Edge-visualization overlay — not an AI crack detection result",
        use_container_width=True
    )

    image_buffer = BytesIO()
    overlay_image.save(image_buffer, format="PNG")
    st.download_button(
        "Download visual overlay",
        data=image_buffer.getvalue(),
        file_name="structure_doctor_visual_overlay.png",
        mime="image/png"
    )
else:
    st.info("Upload an image in Step 2 to view the processing overlay.")

st.markdown('</div>', unsafe_allow_html=True)


# ============================================================
# STEP 4 — CRACK MEASUREMENT / CLASSIFICATION
# ============================================================

st.markdown('<div class="stage">', unsafe_allow_html=True)
st.markdown(
    '<div class="stage-title">STEP 4 — Crack Measurement / Classification</div>',
    unsafe_allow_html=True
)

crack_col1, crack_col2 = st.columns(2)

with crack_col1:
    crack_width = st.number_input(
        "Observed crack width (mm)",
        min_value=0.0,
        max_value=100.0,
        value=0.3,
        step=0.1,
        help="Enter a measured value. Do not estimate exact width from an unscaled photo."
    )

with crack_col2:
    crack_length = st.number_input(
        "Observed crack length (mm, if measured)",
        min_value=0.0,
        max_value=100000.0,
        value=0.0,
        step=10.0,
        help="Enter 0 if the length has not been measured."
    )

crack_pattern = st.selectbox(
    "Observed crack pattern",
    [
        "Unknown",
        "Vertical",
        "Horizontal",
        "Diagonal",
        "Map / network pattern",
        "Along reinforcement",
        "At beam-column joint",
        "Other"
    ]
)

findings = st.text_area(
    "Inspection notes",
    placeholder=(
        "Describe visible conditions, approximate location, nearby leakage, "
        "rust staining, displacement or changes over time."
    ),
    height=100
)

severity, stability_text = classify_screening(float(crack_width))

st.markdown("**Preliminary width screening**")
st.write(f"**Category:** {severity}")
st.write(stability_text)

if crack_progression in ["Widening", "Sudden change"]:
    st.error(
        "The reported crack progression needs prompt on-site professional assessment."
    )

if water_ingress == "Present":
    st.warning(
        "Water ingress is reported. Investigate the moisture source and check for "
        "corrosion or material deterioration during the site inspection."
    )

if crack_pattern in ["Diagonal", "At beam-column joint", "Along reinforcement"]:
    st.warning(
        "The reported crack pattern warrants a careful on-site inspection. "
        "The pattern alone does not establish the cause."
    )

st.markdown('</div>', unsafe_allow_html=True)


# ============================================================
# STEP 5 — STRUCTURAL ASSESSMENT REPORT
# ============================================================

st.markdown('<div class="stage">', unsafe_allow_html=True)
st.markdown(
    '<div class="stage-title">STEP 5 — Structural Assessment Report</div>',
    unsafe_allow_html=True
)

st.subheader("Project and load summary")

st.write(f"**Location:** {location}")
st.write(f"**Building type:** {building_type}")
st.write(f"**Floors:** {int(floors)}")
st.write(f"**Assumed floor-to-floor height:** {floor_height_m:.2f} m")
st.write(f"**Approximate total height:** {load['total_height_m']:.2f} m")
st.write(f"**Inspected area:** {observed_area}")

st.subheader("Crack screening summary")
st.write(f"**Width entered:** {crack_width:.2f} mm")
st.write(f"**Length entered:** {crack_length:.0f} mm")
st.write(f"**Pattern:** {crack_pattern}")
st.write(f"**Progression:** {crack_progression}")
st.write(f"**Water ingress:** {water_ingress}")
st.write(f"**Screening category:** {severity}")

st.subheader("Standards to consult")

code_references = (
    "IS 875 (Part 1): dead loads; IS 875 (Part 2): imposed/live loads; "
    "IS 875 (Part 3): wind loads where applicable; IS 456: plain and "
    "reinforced concrete design; IS 1893 (Part 1): earthquake-resistant "
    "design criteria where applicable; IS 13920: ductile detailing where "
    "applicable. Confirm the currently applicable editions, amendments, "
    "occupancy requirements and local regulations. These standards are "
    "listed as references; this prototype does not implement a complete "
    "code-compliant structural design."
)

st.write(code_references)

st.markdown('</div>', unsafe_allow_html=True)


# ============================================================
# STEP 6 — REPAIR / SAFETY ACTIONS
# ============================================================

st.markdown('<div class="stage">', unsafe_allow_html=True)
st.markdown(
    '<div class="stage-title">STEP 6 — Recommended Repair & Safety Actions</div>',
    unsafe_allow_html=True
)

st.markdown("**Suggested next steps based on the information entered**")

if crack_progression == "Sudden change":
    st.error(
        "Treat the sudden change as urgent. Keep people away from the affected "
        "area and contact a qualified structural engineer promptly. If there are "
        "signs of active movement or possible instability, follow local emergency "
        "guidance and do not re-enter the affected area until it is assessed."
    )
elif crack_progression == "Widening":
    st.warning(
        "Arrange prompt on-site assessment. Record crack width and location with "
        "dated measurements, but do not delay the inspection while monitoring."
    )
else:
    st.write(
        "- Record the crack location, pattern, width and date.\n"
        "- Compare against dated measurements if earlier records exist.\n"
        "- Check for moisture, rust staining, spalling, deformation and nearby changes.\n"
        "- Have a qualified structural engineer assess cracks in structural members."
    )

if water_ingress == "Present":
    st.write(
        "- Investigate the water source and drainage/waterproofing condition.\n"
        "- Have any suspected reinforcement corrosion assessed before selecting repairs."
    )

if crack_width >= 1.0 or crack_pattern in [
    "Diagonal", "At beam-column joint", "Along reinforcement"
]:
    st.write(
        "- Obtain an on-site structural assessment before deciding on a repair method.\n"
        "- Do not cover or inject the crack before its cause and activity are evaluated."
    )

st.caption(
    "Do not select a structural repair method solely from this app. "
    "Repair specifications depend on the verified cause, member condition and design."
)

st.markdown('</div>', unsafe_allow_html=True)


# ============================================================
# STEP 7 — FINAL INSPECTION REPORT
# ============================================================

st.markdown('<div class="stage">', unsafe_allow_html=True)
st.markdown(
    '<div class="stage-title">STEP 7 — Final Inspection Report</div>',
    unsafe_allow_html=True
)

st.write(
    "Generate a combined report containing project inputs, preliminary RCC load "
    "estimates, crack-screening entries, standards to consult, limitations and "
    "the uploaded/processed images when available."
)

st.warning(
    "A photograph cannot determine the remaining safe life of a building. "
    "The load estimates do not establish structural capacity or safety."
)

if PDF_AVAILABLE:
    try:
        pdf_data = build_pdf(
            project=project,
            findings=(
                f"Crack pattern: {crack_pattern}. "
                f"Width: {crack_width:.2f} mm. "
                f"Length: {crack_length:.0f} mm. "
                f"Notes: {findings}"
            ),
            severity=severity,
            stability_text=stability_text,
            load_summary=load_summary,
            code_references=code_references,
            original=original_image,
            overlay=overlay_image
        )

        st.download_button(
            "Download Combined Engineering Screening Report (PDF)",
            data=pdf_data,
            file_name="Structure_Doctor_AI_Combined_Report.pdf",
            mime="application/pdf",
            type="primary"
        )
    except Exception as exc:
        st.error(f"Could not generate the PDF report: {exc}")
else:
    st.error(
        "PDF library is missing. Install it with: pip install reportlab"
    )

st.markdown('</div>', unsafe_allow_html=True)


# ============================================================
# FOOTER
# ============================================================

st.caption(
    "Structure Doctor AI | Preliminary engineering prototype | "
    "Not a substitute for site inspection, verified structural analysis "
    "or approval by a qualified structural engineer."
)
