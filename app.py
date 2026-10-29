
import streamlit as st
from PIL import Image, ImageEnhance, ImageFilter
from io import BytesIO
from datetime import datetime

st.set_page_config(
    page_title="Structure Doctor AI",
    page_icon="🏗️",
    layout="wide"
)

st.title("🏗️ Structure Doctor AI")
st.subheader("RCC Load Calculation & Crack Assessment")
st.caption("Indian Standards framework | Hyderabad, Telangana")

st.warning(
    "PRELIMINARY SCREENING ONLY. This application is not a "
    "construction-ready structural design. A qualified structural "
    "engineer must verify all inputs, loads, code provisions and findings."
)

# ---------------- PROJECT INPUTS ----------------
st.header("1. Project Inputs")

c1, c2, c3 = st.columns(3)

with c1:
    location = st.text_input(
        "Building location", "Hyderabad, Telangana"
    )
    building_type = st.selectbox(
        "Building type",
        ["Residential", "Commercial", "Office", "Institutional", "Other"]
    )
    floors = st.number_input(
        "Number of floors", min_value=1, max_value=100, value=3
    )

with c2:
    floor_height = st.number_input(
        "Floor-to-floor height (m)",
        min_value=2.0, max_value=6.0, value=3.0, step=0.1
    )
    length = st.number_input(
        "Building length (m)", min_value=1.0, value=12.0
    )
    width = st.number_input(
        "Building width (m)", min_value=1.0, value=10.0
    )

with c3:
    slab_mm = st.number_input(
        "Slab thickness (mm)", min_value=80, max_value=300, value=125
    )
    concrete_density = st.number_input(
        "Concrete unit weight (kN/m³)",
        min_value=20.0, max_value=30.0, value=25.0
    )
    image_file = st.file_uploader(
        "Upload crack image", type=["jpg", "jpeg", "png"]
    )

# ---------------- LOAD ASSUMPTIONS ----------------
st.header("2. Load Assumptions")

a1, a2, a3 = st.columns(3)

with a1:
    finishes = st.number_input(
        "Floor finishes/services (kN/m²)",
        min_value=0.0, value=1.0, step=0.25
    )

with a2:
    live_load = st.number_input(
        "Imposed load (kN/m²)",
        min_value=0.0, value=2.0, step=0.25,
        help="Illustrative default only. Verify occupancy-specific value."
    )

with a3:
    wall_allowance = st.number_input(
        "Wall/partition allowance (kN/m²)",
        min_value=0.0, value=1.0, step=0.25,
        help="Simplified allowance, not a calculation of actual wall loads."
    )

other_dead = st.number_input(
    "Other dead load allowance (kN/m²)",
    min_value=0.0, value=0.0, step=0.25
)

# ---------------- PRELIMINARY CALCULATIONS ----------------
area = length * width
height_total = floors * floor_height

slab_dead = (slab_mm / 1000.0) * concrete_density

dead_load = slab_dead + finishes + wall_allowance + other_dead
service_load = dead_load + live_load

floor_total = area * service_load
all_floor_total = floor_total * floors
total_dead = area * dead_load * floors
total_live = area * live_load * floors

st.header("3. Preliminary RCC Load Results")

m1, m2, m3 = st.columns(3)
m1.metric("Typical floor area", f"{area:.2f} m²")
m2.metric("Approx. building height", f"{height_total:.2f} m")
m3.metric("Slab self-weight", f"{slab_dead:.2f} kN/m²")

m1, m2, m3 = st.columns(3)
m1.metric("Assumed dead load", f"{dead_load:.2f} kN/m²")
m2.metric("Service load per floor", f"{service_load:.2f} kN/m²")
m3.metric("Load per typical floor", f"{floor_total:.2f} kN")

st.metric(
    "Simple total across all floors",
    f"{all_floor_total:.2f} kN"
)

st.markdown("### Transparent calculation trail")

st.latex(
    r"w_{slab}=t_{slab}\times \gamma_{concrete}"
)
st.write(
    f"Slab self-weight = {slab_mm}/1000 × "
    f"{concrete_density} = {slab_dead:.3f} kN/m²"
)

st.latex(
    r"w_D=w_{slab}+w_{finishes}+w_{walls}+w_{other}"
)
st.write(
    f"Assumed dead load = {slab_dead:.3f} + {finishes:.2f} + "
    f"{wall_allowance:.2f} + {other_dead:.2f} "
    f"= {dead_load:.3f} kN/m²"
)

st.latex(r"w_{service}=w_D+w_L")
st.write(
    f"Unfactored service load = {dead_load:.3f} + "
    f"{live_load:.2f} = {service_load:.3f} kN/m²"
)

st.latex(r"W_{floor}=A\times w_{service}")
st.write(
    f"Floor load = {area:.2f} × {service_load:.3f} "
    f"= {floor_total:.2f} kN"
)

st.latex(r"W_{total,\ simplified}=N_{floors}\times W_{floor}")
st.write(
    f"Simple all-floor total = {floors} × {floor_total:.2f} "
    f"= {all_floor_total:.2f} kN"
)

st.write(f"Approximate total height = {floors} × {floor_height:.2f} = {height_total:.2f} m")
st.write(f"Dead-load subtotal = {total_dead:.2f} kN")
st.write(f"Live-load subtotal = {total_live:.2f} kN")

st.info(
    "These are simplified, unfactored gravity-load estimates. "
    "The total across floors is NOT a column reaction. Actual member "
    "forces require the structural layout, tributary areas, member "
    "self-weights, load combinations and structural analysis."
)

# ---------------- CRACK ASSESSMENT ----------------
st.header("4. Crack Assessment")

q1, q2, q3 = st.columns(3)

with q1:
    crack_location = st.selectbox(
        "Crack location",
        ["Wall", "Beam", "Column", "Slab", "Foundation", "Unknown"]
    )
    crack_width = st.number_input(
        "Measured crack width (mm)", min_value=0.0, value=0.0, step=0.1
    )

with q2:
    crack_length = st.number_input(
        "Measured crack length (m)", min_value=0.0, value=0.0, step=0.1
    )
    pattern = st.selectbox(
        "Crack pattern",
        ["Not assessed", "Vertical", "Horizontal", "Diagonal",
         "Map/network", "Multiple/irregular"]
    )

with q3:
    progression = st.selectbox(
        "Crack progression",
        ["Unknown", "Stable based on monitoring",
         "Widening or recurring", "Sudden change"]
    )
    dampness = st.selectbox(
        "Water ingress",
        ["Unknown", "Not observed", "Present"]
    )

if image_file:
    image = Image.open(image_file).convert("RGB")
    enhanced = ImageEnhance.Contrast(image).enhance(1.2)
    enhanced = ImageEnhance.Sharpness(enhanced).enhance(1.5)

    original_col, enhanced_col = st.columns(2)
    with original_col:
        st.image(image, caption="Uploaded image", use_container_width=True)
    with enhanced_col:
        st.image(
            enhanced.filter(ImageFilter.MedianFilter(3)),
            caption="Enhanced image for visual review",
            use_container_width=True
        )

    st.caption(
        "Image enhancement is not validated AI crack detection. "
        "No physical crack width or length is inferred from pixels."
    )

# ---------------- CONTEXTUAL RECOMMENDATIONS ----------------
st.header("5. Preliminary Findings & Recommendations")

recommendations = []

if progression == "Sudden change":
    recommendations.append(
        "URGENT: Arrange immediate professional structural assessment. "
        "Keep people away from areas showing signs of instability and "
        "contact local emergency/building authorities if necessary."
    )

elif progression == "Widening or recurring":
    recommendations.append(
        "Arrange prompt inspection by a qualified structural engineer "
        "and document crack movement with dated measurements."
    )

if crack_location in ["Beam", "Column", "Foundation"]:
    recommendations.append(
        f"A reported crack in a {crack_location.lower()} needs an "
        "on-site structural assessment. Do not infer its cause from "
        "the image or crack width alone."
    )

if pattern == "Diagonal":
    recommendations.append(
        "Inspect the crack location, member geometry, support conditions "
        "and movement history. A diagonal pattern alone cannot diagnose "
        "shear failure."
    )

if dampness == "Present":
    recommendations.append(
        "Investigate water entry and assess possible reinforcement "
        "corrosion or concrete deterioration before selecting a repair."
    )

if crack_width > 0:
    recommendations.append(
        f"Recorded crack width: {crack_width:.2f} mm. Verify using a "
        "calibrated crack gauge and document repeat measurements."
    )

if crack_length > 0:
    recommendations.append(
        f"Recorded crack length: {crack_length:.2f} m. Verify and map "
        "the extent on site."
    )

if not recommendations:
    recommendations.append(
        "Record the crack location, dimensions and dated photographs. "
        "Arrange professional review if it grows, recurs, leaks or "
        "affects a structural member."
    )

recommendations.append(
    "Do not conceal or repair a potentially structural crack before "
    "its cause is assessed. A repair specification must follow diagnosis."
)

for item in recommendations:
    st.write("• " + item)

# ---------------- CODE REFERENCES ----------------
st.header("6. Indian Standards Reference Framework")

st.markdown("""
- **IS 875 (Part 1):** Dead loads.
- **IS 875 (Part 2):** Imposed/live loads.
- **IS 456:** Plain and reinforced concrete.
- **IS 1893 (Part 1):** Earthquake actions, where applicable.
- **IS 13920:** Ductile detailing, where applicable.

Verify current editions, amendments, occupancy categories, site parameters,
applicable clauses and load combinations with the project engineer.
This prototype does not implement every code requirement.
""")

# ---------------- COMBINED REPORT ----------------
st.header("7. Combined Inspection & Load Report")

report = f"""
STRUCTURE DOCTOR AI
RCC PRELIMINARY LOAD AND CRACK SCREENING REPORT

Generated: {datetime.now().strftime("%d-%m-%Y %H:%M")}
Location: {location}
Building type: {building_type}
Number of floors: {floors}
Floor-to-floor height: {floor_height:.2f} m
Approximate total height: {height_total:.2f} m
Plan dimensions: {length:.2f} m x {width:.2f} m
Typical floor area: {area:.2f} m²

LOAD CALCULATIONS
Slab self-weight: {slab_dead:.3f} kN/m²
Assumed dead load: {dead_load:.3f} kN/m²
Imposed load: {live_load:.3f} kN/m²
Unfactored service load: {service_load:.3f} kN/m²
Unfactored typical-floor total: {floor_total:.2f} kN
Simple all-floor total: {all_floor_total:.2f} kN
Dead-load subtotal: {total_dead:.2f} kN
Live-load subtotal: {total_live:.2f} kN

CRACK INFORMATION
Location: {crack_location}
Width: {crack_width:.2f} mm (user-entered)
Length: {crack_length:.2f} m (user-entered)
Pattern: {pattern}
Progression: {progression}
Water ingress: {dampness}

RECOMMENDATIONS
""" + "\n".join("- " + x for x in recommendations) + """

CODE REFERENCE FRAMEWORK
IS 875 Parts 1 and 2; IS 456; IS 1893 Part 1 where applicable;
IS 13920 where applicable. Verify current editions and amendments.

SAFETY LIMITATIONS
This is a preliminary screening report, not construction-ready design.
The all-floor sum is not a column reaction. The calculation excludes a
complete structural model, verified wall/member loads, load combinations,
wind/seismic analysis, member design and foundation analysis.
Image enhancement is not validated AI crack detection. Crack dimensions
must be measured on site. Remaining safe building life cannot be estimated
reliably from an image. Qualified structural-engineer review is required.
"""

st.text_area("Report preview", report, height=420)

st.download_button(
    "Download combined report (TXT)",
    data=report.encode("utf-8"),
    file_name="Structure_Doctor_AI_Report.txt",
    mime="text/plain"
)

# Optional PDF export
try:
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.pagesizes import A4

    pdf_buffer = BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    for line in report.splitlines():
        if line.strip():
            story.append(Paragraph(line.replace("&", "&amp;"), styles["BodyText"]))
        else:
            story.append(Spacer(1, 8))

    doc.build(story)

    st.download_button(
        "Download combined report (PDF)",
        data=pdf_buffer.getvalue(),
        file_name="Structure_Doctor_AI_Report.pdf",
        mime="application/pdf"
    )

except ImportError:
    st.caption("For PDF export, install reportlab: py -m pip install reportlab")

st.caption(
    "Engineering prototype • Preliminary estimates only • "
    "Not a design certificate or construction instruction."
)
