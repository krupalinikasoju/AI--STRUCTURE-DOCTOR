import streamlit as st
from PIL import Image, ImageEnhance, ImageFilter
from io import BytesIO
from datetime import datetime
import html

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Structure Doctor AI",
    page_icon="🏗️",
    layout="wide"
)

st.title("🏗️ Structure Doctor AI")
st.subheader("RCC Load Calculation & Crack Assessment")
st.caption(
    "Indian Standards framework | Hyderabad, Telangana | "
    "Preliminary engineering screening"
)

st.warning(
    "SAFETY NOTICE: This application provides preliminary estimates only. "
    "It is not a structural design certificate and must not be used as "
    "construction approval. A qualified structural engineer must verify "
    "the building, inputs, calculations, code provisions, and findings."
)

# --------------------------------------------------
# 1. PROJECT INPUTS
# --------------------------------------------------

st.header("1. Project Inputs")

c1, c2, c3 = st.columns(3)

with c1:
    location = st.text_input(
        "Building location",
        value="Hyderabad, Telangana"
    )

    building_type = st.selectbox(
        "Building type",
        [
            "Residential",
            "Commercial",
            "Office",
            "Institutional",
            "Other"
        ]
    )

    floors = st.number_input(
        "Number of floors",
        min_value=1,
        max_value=100,
        value=3,
        step=1
    )

with c2:
    floor_height = st.number_input(
        "Typical floor-to-floor height (m)",
        min_value=2.0,
        max_value=6.0,
        value=3.0,
        step=0.1
    )

    length = st.number_input(
        "Building length (m)",
        min_value=1.0,
        max_value=500.0,
        value=12.0,
        step=0.5
    )

    width = st.number_input(
        "Building width (m)",
        min_value=1.0,
        max_value=500.0,
        value=10.0,
        step=0.5
    )

with c3:
    slab_mm = st.number_input(
        "Slab thickness (mm)",
        min_value=80,
        max_value=500,
        value=125,
        step=5
    )

    concrete_density = st.number_input(
        "Concrete unit weight (kN/m³)",
        min_value=20.0,
        max_value=30.0,
        value=25.0,
        step=0.5
    )

    image_file = st.file_uploader(
        "Upload crack image",
        type=["jpg", "jpeg", "png"]
    )

# --------------------------------------------------
# 2. LOAD ASSUMPTIONS
# --------------------------------------------------

st.header("2. Load Assumptions")

st.caption(
    "Default loads below are illustrative inputs, not verified code values. "
    "Select loads appropriate to the actual occupancy and building details."
)

a1, a2, a3 = st.columns(3)

with a1:
    finishes = st.number_input(
        "Floor finishes/services (kN/m²)",
        min_value=0.0,
        value=1.0,
        step=0.25
    )

with a2:
    live_load = st.number_input(
        "Imposed/live load (kN/m²)",
        min_value=0.0,
        value=2.0,
        step=0.25,
        help=(
            "Illustrative only. Verify the applicable occupancy category "
            "and requirements of IS 875 Part 2."
        )
    )

with a3:
    wall_allowance = st.number_input(
        "Wall/partition allowance (kN/m²)",
        min_value=0.0,
        value=1.0,
        step=0.25,
        help=(
            "Simplified area allowance. Not a calculation of actual "
            "wall loads or their distribution."
        )
    )

other_dead = st.number_input(
    "Other dead load allowance (kN/m²)",
    min_value=0.0,
    value=0.0,
    step=0.25
)

# --------------------------------------------------
# 3. PRELIMINARY LOAD CALCULATIONS
# --------------------------------------------------

area = length * width
height_total = floors * floor_height

slab_thickness_m = slab_mm / 1000.0

# Slab self-weight per unit plan area
slab_dead = slab_thickness_m * concrete_density

# Simplified area loads
dead_load = (
    slab_dead
    + finishes
    + wall_allowance
    + other_dead
)

service_load = dead_load + live_load

# Simple plan-area-based totals
floor_dead_total = area * dead_load
floor_live_total = area * live_load
floor_total = area * service_load

total_dead = floor_dead_total * floors
total_live = floor_live_total * floors
all_floor_total = total_dead + total_live

st.header("3. Preliminary RCC Load Results")

m1, m2, m3 = st.columns(3)

m1.metric(
    "Typical floor area",
    f"{area:,.2f} m²"
)

m2.metric(
    "Approx. total height",
    f"{height_total:,.2f} m"
)

m3.metric(
    "Slab self-weight",
    f"{slab_dead:.3f} kN/m²"
)

m1, m2, m3 = st.columns(3)

m1.metric(
    "Assumed dead load",
    f"{dead_load:.3f} kN/m²"
)

m2.metric(
    "Assumed live load",
    f"{live_load:.3f} kN/m²"
)

m3.metric(
    "Unfactored service load",
    f"{service_load:.3f} kN/m²"
)

m1, m2, m3 = st.columns(3)

m1.metric(
    "Typical-floor dead load",
    f"{floor_dead_total:,.2f} kN"
)

m2.metric(
    "Typical-floor live load",
    f"{floor_live_total:,.2f} kN"
)

m3.metric(
    "Typical-floor total",
    f"{floor_total:,.2f} kN"
)

st.metric(
    "Simplified total across all floors",
    f"{all_floor_total:,.2f} kN"
)

st.markdown("### Transparent calculation trail")

st.markdown("**Step 1 — Slab self-weight**")

st.latex(r"w_{slab}=t_{slab}\times\gamma_{concrete}")

st.write(
    f"Slab thickness = {slab_mm} / 1000 "
    f"= {slab_thickness_m:.3f} m"
)

st.write(
    f"Slab self-weight = {slab_thickness_m:.3f} × "
    f"{concrete_density:.2f} "
    f"= **{slab_dead:.3f} kN/m²**"
)

st.markdown("**Step 2 — Assumed dead load**")

st.latex(
    r"w_D=w_{slab}+w_{finishes}+w_{walls}+w_{other}"
)

st.write(
    f"wD = {slab_dead:.3f} + {finishes:.3f} + "
    f"{wall_allowance:.3f} + {other_dead:.3f} "
    f"= **{dead_load:.3f} kN/m²**"
)

st.markdown("**Step 3 — Unfactored service load**")

st.latex(r"w_{service}=w_D+w_L")

st.write(
    f"wservice = {dead_load:.3f} + {live_load:.3f} "
    f"= **{service_load:.3f} kN/m²**"
)

st.markdown("**Step 4 — Typical-floor load estimate**")

st.latex(r"A=L\times B")

st.write(
    f"Plan area = {length:.2f} × {width:.2f} "
    f"= **{area:.2f} m²**"
)

st.latex(r"W_{floor}=A\times w_{service}")

st.write(
    f"Wfloor = {area:.2f} × {service_load:.3f} "
    f"= **{floor_total:.2f} kN**"
)

st.markdown("**Step 5 — Simplified all-floor total**")

st.latex(
    r"W_{total}=N_{floors}\times A\times w_{service}"
)

st.write(
    f"Wtotal = {floors} × {area:.2f} × {service_load:.3f} "
    f"= **{all_floor_total:.2f} kN**"
)

st.write(
    f"Dead-load subtotal = {floors} × {area:.2f} × "
    f"{dead_load:.3f} = **{total_dead:.2f} kN**"
)

st.write(
    f"Live-load subtotal = {floors} × {area:.2f} × "
    f"{live_load:.3f} = **{total_live:.2f} kN**"
)

st.info(
    "Interpretation: these are simplified, unfactored, gravity-load "
    "estimates based on the full plan area and entered area-load assumptions. "
    "They are not column reactions or verified structural forces. "
    "The model does not calculate beam and column self-weight separately, "
    "tributary areas, load combinations, lateral forces, member capacity, "
    "or foundation capacity."
)

# --------------------------------------------------
# 4. CRACK ASSESSMENT
# --------------------------------------------------

st.header("4. Crack Assessment")

q1, q2, q3 = st.columns(3)

with q1:
    crack_location = st.selectbox(
        "Crack location",
        [
            "Wall",
            "Beam",
            "Column",
            "Slab",
            "Foundation",
            "Unknown"
        ]
    )

    crack_width = st.number_input(
        "Measured crack width (mm)",
        min_value=0.0,
        max_value=100.0,
        value=0.0,
        step=0.1
    )

with q2:
    crack_length = st.number_input(
        "Measured crack length (m)",
        min_value=0.0,
        max_value=1000.0,
        value=0.0,
        step=0.1
    )

    pattern = st.selectbox(
        "Crack pattern",
        [
            "Not assessed",
            "Vertical",
            "Horizontal",
            "Diagonal",
            "Map/network",
            "Multiple/irregular"
        ]
    )

with q3:
    progression = st.selectbox(
        "Crack progression",
        [
            "Unknown",
            "Stable based on monitoring",
            "Widening or recurring",
            "Sudden change"
        ]
    )

    dampness = st.selectbox(
        "Water ingress",
        [
            "Unknown",
            "Not observed",
            "Present"
        ]
    )

image_available = image_file is not None

if image_available:
    try:
        image = Image.open(image_file).convert("RGB")

        enhanced = ImageEnhance.Contrast(image).enhance(1.2)
        enhanced = ImageEnhance.Sharpness(enhanced).enhance(1.5)
        filtered = enhanced.filter(ImageFilter.MedianFilter(size=3))

        original_col, enhanced_col = st.columns(2)

        with original_col:
            st.image(
                image,
                caption="Uploaded image",
                use_container_width=True
            )

        with enhanced_col:
            st.image(
                filtered,
                caption="Enhanced image for visual review",
                use_container_width=True
            )

        st.caption(
            "Image enhancement only. This application does not run a "
            "validated AI crack detector and does not infer physical crack "
            "width, length, structural capacity, or remaining building life "
            "from image pixels."
        )

    except Exception as error:
        st.error(
            "The uploaded image could not be processed. "
            "Try a valid JPG or PNG image."
        )
        image_available = False

# --------------------------------------------------
# 5. PRELIMINARY FINDINGS AND RECOMMENDATIONS
# --------------------------------------------------

st.header("5. Preliminary Findings & Recommendations")

recommendations = []

if progression == "Sudden change":
    recommendations.append(
        "URGENT: Arrange immediate assessment by a qualified structural "
        "engineer. If there are signs of instability, significant movement, "
        "or falling material, keep people away from the affected area and "
        "contact appropriate emergency or building authorities."
    )

elif progression == "Widening or recurring":
    recommendations.append(
        "Arrange prompt professional inspection. Record dated photographs "
        "and repeat measurements using a suitable crack gauge."
    )

if crack_location in ["Beam", "Column", "Foundation"]:
    recommendations.append(
        f"A reported crack in a {crack_location.lower()} requires "
        "on-site structural assessment. Its cause and significance cannot "
        "be diagnosed from location or image alone."
    )

if crack_location == "Slab":
    recommendations.append(
        "Have the slab inspected in context, including crack location, "
        "support conditions, deflection, loading, water ingress, and "
        "any exposed or corroded reinforcement."
    )

if pattern == "Diagonal":
    recommendations.append(
        "Document the crack location, geometry, nearby supports, and "
        "movement history. A diagonal pattern alone does not establish "
        "shear failure or its cause."
    )

if pattern == "Map/network":
    recommendations.append(
        "Arrange inspection to investigate possible shrinkage, surface "
        "deterioration, moisture-related damage, or other causes. The "
        "pattern alone is not a confirmed diagnosis."
    )

if dampness == "Present":
    recommendations.append(
        "Investigate the source of water ingress and assess possible "
        "reinforcement corrosion or material deterioration before "
        "choosing a repair method."
    )

if crack_width > 0:
    recommendations.append(
        f"User-entered crack width: {crack_width:.2f} mm. Verify the "
        "measurement on site with an appropriate calibrated crack gauge."
    )

if crack_length > 0:
    recommendations.append(
        f"User-entered crack length: {crack_length:.2f} m. Verify the "
        "length and map the full extent during inspection."
    )

if not recommendations:
    recommendations.append(
        "Record the crack location, dimensions, dated photographs, and "
        "movement history. Seek professional review if the crack grows, "
        "recurs, leaks, or affects a structural member."
    )

recommendations.append(
    "Do not conceal or repair a potentially structural crack before its "
    "cause is assessed. Repair methods should be specified after diagnosis."
)

for item in recommendations:
    st.markdown(f"- {item}")

st.markdown("### Building life and safety")

st.write(
    "This application cannot estimate an exact number of remaining safe "
    "years from a photograph or the simplified load calculation. A "
    "condition assessment requires an on-site inspection and may require "
    "material testing, reinforcement assessment, structural analysis, "
    "and review of maintenance and exposure history."
)

# --------------------------------------------------
# 6. INDIAN STANDARDS REFERENCE FRAMEWORK
# --------------------------------------------------

st.header("6. Indian Standards Reference Framework")

st.markdown("""
| Standard | General application |
|---|---|
| IS 875 (Part 1) | Dead loads |
| IS 875 (Part 2) | Imposed/live loads |
| IS 875 (Part 3) | Wind loads |
| IS 456 | Plain and reinforced concrete |
| IS 1893 (Part 1) | Earthquake actions, where applicable |
| IS 13920 | Ductile detailing, where applicable |
""")

st.warning(
    "Reference framework only: this prototype does not implement every "
    "requirement of these standards. Confirm the current editions, "
    "amendments, applicable clauses, occupancy categories, site parameters, "
    "load combinations, and detailing requirements with the project engineer."
)

# --------------------------------------------------
# 7. COMBINED INSPECTION AND LOAD REPORT
# --------------------------------------------------

st.header("7. Combined Inspection & Load Report")

generated_time = datetime.now().strftime("%d-%m-%Y %H:%M")

image_status = (
    "Image uploaded; enhancement only, no validated AI detection"
    if image_available
    else "No image uploaded"
)

report = f"""
STRUCTURE DOCTOR AI
RCC PRELIMINARY LOAD AND CRACK SCREENING REPORT

Generated: {generated_time}

PROJECT INFORMATION
Location: {location}
Building type: {building_type}
Number of floors: {floors}
Floor-to-floor height: {floor_height:.2f} m
Approximate height (floors x floor-to-floor height): {height_total:.2f} m
Plan dimensions: {length:.2f} m x {width:.2f} m
Typical plan area: {area:.2f} m2
Image status: {image_status}

LOAD INPUTS AND ASSUMPTIONS
Slab thickness: {slab_mm} mm
Concrete unit weight: {concrete_density:.2f} kN/m3
Floor finishes/services allowance: {finishes:.2f} kN/m2
Wall/partition allowance: {wall_allowance:.2f} kN/m2
Other dead-load allowance: {other_dead:.2f} kN/m2
Imposed/live load: {live_load:.2f} kN/m2

PRELIMINARY LOAD CALCULATIONS
Slab thickness in metres = {slab_mm}/1000 = {slab_thickness_m:.3f} m

Slab self-weight:
w_slab = slab thickness x concrete unit weight
       = {slab_thickness_m:.3f} x {concrete_density:.2f}
       = {slab_dead:.3f} kN/m2

Assumed dead load:
w_D = slab self-weight + finishes + wall allowance + other dead load
    = {slab_dead:.3f} + {finishes:.3f} + {wall_allowance:.3f}
      + {other_dead:.3f}
    = {dead_load:.3f} kN/m2

Unfactored service load:
w_service = dead load + live load
          = {dead_load:.3f} + {live_load:.3f}
          = {service_load:.3f} kN/m2

Typical floor load estimate:
A = length x width = {length:.2f} x {width:.2f}
  = {area:.2f} m2

W_floor = A x w_service
        = {area:.2f} x {service_load:.3f}
        = {floor_total:.2f} kN

Simplified all-floor total:
W_total = floors x A x w_service
        = {floors} x {area:.2f} x {service_load:.3f}
        = {all_floor_total:.2f} kN

Dead-load subtotal across floors: {total_dead:.2f} kN
Live-load subtotal across floors: {total_live:.2f} kN

CRACK INFORMATION
Location: {crack_location}
User-entered width: {crack_width:.2f} mm
User-entered length: {crack_length:.2f} m
Pattern: {pattern}
Progression: {progression}
Water ingress: {dampness}

PRELIMINARY RECOMMENDATIONS
""" + "\n".join(
    f"- {item}" for item in recommendations
) + f"""

INDIAN STANDARDS REFERENCE FRAMEWORK
IS 875 Part 1: Dead loads.
IS 875 Part 2: Imposed/live loads.
IS 875 Part 3: Wind loads, where applicable.
IS 456: Plain and reinforced concrete.
IS 1893 Part 1: Earthquake actions, where applicable.
IS 13920: Ductile detailing, where applicable.

Verify current editions, amendments, applicable clauses and project-specific
requirements. Listing a standard does not mean the application has implemented
or verified all its provisions.

SAFETY LIMITATIONS
1. This report is a preliminary screening aid, not a design certificate.
2. Load values depend on user-entered assumptions and are unfactored.
3. The all-floor total is not a column reaction or verified member force.
4. The model does not perform full structural analysis, member design,
   wind/seismic analysis, or foundation design.
5. Wall loads, beams, columns, stairs, services, and other elements may
   require separate assessment.
6. Image enhancement is not validated AI crack detection.
7. Crack dimensions are user-entered and must be verified on site.
8. Remaining safe building life cannot be reliably determined from an image.
9. A qualified structural engineer must verify the building and findings.

END OF REPORT
"""

st.text_area(
    "Report preview",
    value=report,
    height=450
)

st.download_button(
    label="Download combined report (TXT)",
    data=report.encode("utf-8"),
    file_name="Structure_Doctor_AI_Report.txt",
    mime="text/plain",
    use_container_width=True
)

# --------------------------------------------------
# PDF REPORT EXPORT
# --------------------------------------------------

try:
    from reportlab.platypus import (
        SimpleDocTemplate,
        Paragraph,
        Spacer
    )
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm

    pdf_buffer = BytesIO()

    doc = SimpleDocTemplate(
        pdf_buffer,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm
    )

    styles = getSampleStyleSheet()

    body_style = ParagraphStyle(
        "ReportBody",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=12,
        spaceAfter=4
    )

    title_style = styles["Title"]
    story = []

    for index, line in enumerate(report.splitlines()):
        if not line.strip():
            story.append(Spacer(1, 5))
            continue

        safe_line = html.escape(line)

        if index == 0:
            story.append(
                Paragraph(safe_line, title_style)
            )
        elif line.isupper() and len(line) < 70:
            story.append(
                Paragraph(safe_line, styles["Heading2"])
            )
        else:
            story.append(
                Paragraph(safe_line, body_style)
            )

    doc.build(story)

    st.download_button(
        label="Download combined report (PDF)",
        data=pdf_buffer.getvalue(),
        file_name="Structure_Doctor_AI_Report.pdf",
        mime="application/pdf",
        use_container_width=True
    )

except ImportError:
    st.info(
        "PDF export requires ReportLab. Install it with: "
        "py -m pip install reportlab"
    )

except Exception as error:
    st.error(
        "PDF generation failed. Check that ReportLab is installed "
        "and try again."
    )

# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "Structure Doctor AI | Engineering prototype | "
    "Preliminary estimates only | Not construction approval"
)
