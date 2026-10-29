import streamlit as st
from PIL import Image, ImageEnhance, ImageFilter, ImageDraw
from io import BytesIO
from datetime import datetime
import numpy as np

st.set_page_config(page_title="Structure Doctor AI", page_icon="🏗️", layout="wide")

st.markdown("""
<style>
:root { color-scheme: light; }
.stApp { background:#f7fbff; color:#122f50; }
.block-container {max-width:1600px;padding-top:1rem;padding-bottom:2rem;}
header[data-testid="stHeader"] {background:rgba(247,251,255,.95);}
.hero {background:linear-gradient(110deg,#092849,#104876);color:white;border-radius:15px;padding:22px 26px;margin-bottom:16px;box-shadow:0 4px 12px #0c315015;}
.hero h1 {font-size:2.15rem;color:#fff;margin:0;font-weight:800;}
.hero p {color:#d9eafa;margin:5px 0 0 0;font-size:1rem;}
.hero-side {border-left:2px solid #86b9dd;padding-left:20px;font-size:1rem;}
.section-label {font-size:1.25rem;font-weight:800;color:#123e69;margin:8px 0 10px 0;}
.panel {border:1px solid #cdddea;border-radius:13px;padding:15px 16px;background:#fff;box-shadow:0 2px 5px #153b5c0b;height:100%;}
.panel-blue {background:#edf8ff;border-color:#a9d9f2;}
.panel-purple {background:#f6f2ff;border-color:#c9b7f5;}
.panel-green {background:#effbf5;border-color:#9bd9bd;}
.panel-pink {background:#fff1f5;border-color:#f0b5cb;}
.panel-yellow {background:#fff9e9;border-color:#ead28a;}
.panel h3 {font-size:1.08rem;line-height:1.25;color:#103b68;margin:0 0 8px 0;}
.panel p {font-size:.91rem;color:#233f60;margin:0 0 8px 0;}
.stephead {display:flex;align-items:center;gap:9px;margin-bottom:9px;}
.stepnum {display:inline-flex;align-items:center;justify-content:center;min-width:37px;height:37px;border-radius:50%;background:#104d91;color:white;font-size:1.15rem;font-weight:800;}
.stepnum.purple {background:#5b35c5}.stepnum.green {background:#07865e}.stepnum.pink {background:#b42f60}.stepnum.gold {background:#aa7209}
.tag {display:inline-block;border-radius:8px;background:#104d91;color:white;padding:6px 10px;font-weight:750;font-size:.92rem;}
.tag.purple {background:#5b35c5}.tag.green {background:#07865e}.tag.pink {background:#b42f60}.tag.gold {background:#aa7209}
.arrow {text-align:center;color:#15528d;font-size:1.55rem;font-weight:900;line-height:1.1;padding:2px;}
.darkbox {background:#0b2c50;color:white;padding:13px;border-radius:10px;}
.darkbox h4 {color:white;margin:0 0 8px 0;font-size:1rem;}
.darkbox hr {border:0;border-top:1px solid #335675;margin:6px 0;}
.darkbox p {color:white;font-size:.87rem;margin:4px 0;}
.pill {display:inline-block;border-radius:20px;padding:3px 10px;background:#f4c542;color:#17324c;font-weight:800;}
.muted {font-size:.82rem;color:#526a82;}
.report-paper {background:#fff;border:1px solid #bad1e2;border-radius:11px;padding:14px;color:#173655;}
div[data-testid="stMetric"] {background:#f1f8fd;border:1px solid #d5e6f1;padding:10px;border-radius:10px;}
.stButton>button,.stDownloadButton>button {border-radius:8px;font-weight:700;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
 <div style="display:flex;align-items:center;justify-content:space-between;gap:20px;flex-wrap:wrap">
  <div><h1>⌂ Structure Doctor <span style="color:#68d9ed">AI</span></h1>
  <p>Smart Crack Review &nbsp;|&nbsp; Image Processing &nbsp;|&nbsp; Structural Inspection Report</p></div>
  <div class="hero-side"><b style="font-size:1.2rem">WORKFLOW</b><br>From building image to inspection report</div>
 </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="background:#fff6df;border:1px solid #f0d28b;padding:10px 14px;border-radius:10px;margin-bottom:14px;color:#63450a">
<b>Safety note:</b> This prototype provides visual screening, not certified structural analysis. A photo alone cannot establish building safety or remaining safe life in years.
</div>
""", unsafe_allow_html=True)

def enhance(img):
    return ImageEnhance.Sharpness(ImageEnhance.Contrast(img).enhance(1.24)).enhance(1.55).filter(ImageFilter.MedianFilter(3))

def overlay_edges(img):
    # An edge-review visualization, not an AI model or a crack segmentation result.
    out = img.convert("RGB").copy()
    arr = np.asarray(out).astype(np.float32)
    gray = arr.mean(axis=2)
    gy, gx = np.gradient(gray)
    mag = np.sqrt(gx*gx + gy*gy)
    mask = mag >= max(20, float(np.percentile(mag, 94)))
    ys, xs = np.where(mask)
    draw = ImageDraw.Draw(out, "RGBA")
    if len(xs):
        stride = max(1, len(xs)//1600)
        for x,y in zip(xs[::stride],ys[::stride]):
            draw.ellipse((int(x)-1,int(y)-1,int(x)+2,int(y)+2),fill=(245,55,60,185))
    return out

def pdf_report(data, findings, risk, img, over):
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RImage
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import mm
    except ImportError:
        return None
    buf=BytesIO()
    doc=SimpleDocTemplate(buf,pagesize=A4,rightMargin=15*mm,leftMargin=15*mm,topMargin=14*mm,bottomMargin=14*mm)
    styles=getSampleStyleSheet()
    styles.add(ParagraphStyle(name="SDTitle",parent=styles["Title"],textColor=colors.HexColor("#0b2c50"),alignment=0))
    story=[Paragraph("STRUCTURE DOCTOR AI",styles["SDTitle"]),
           Paragraph("Building Crack Inspection Report — Preliminary Screening",styles["Heading2"]),
           Paragraph("Generated: "+datetime.now().strftime("%d %b %Y, %H:%M"),styles["Normal"]),Spacer(1,10)]
    rows=[["Project details","Value"],["Building type",data["building"]],["Floors",str(data["floors"])],
          ["Location",data["location"] or "Not supplied"],["Observed area",data["area"]],
          ["Image",data["filename"] or "Not supplied"],["Observed pattern",data["pattern"]],
          ["User-entered width",f'{data["width"]:.1f} mm' if data["width"] else "Not supplied"],
          ["User-entered length",f'{data["length"]:.1f} m' if data["length"] else "Not supplied"]]
    table=Table(rows,colWidths=[45*mm,122*mm])
    table.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.HexColor("#0b2c50")),("TEXTCOLOR",(0,0),(-1,0),colors.white),
       ("GRID",(0,0),(-1,-1),.4,colors.HexColor("#bed0df")),("BACKGROUND",(0,1),(-1,-1),colors.HexColor("#f4f9fc")),("PADDING",(0,0),(-1,-1),6)]))
    story += [table,Spacer(1,12),Paragraph("Screening summary",styles["Heading2"]),
              Paragraph("<b>Screening prompt:</b> "+risk,styles["Normal"]),
              Paragraph("<b>Remaining safe life:</b> Cannot be determined from a photograph alone. Requires a qualified on-site structural assessment.",styles["Normal"]),
              Spacer(1,8),Paragraph("Findings and next steps",styles["Heading2"])]
    for f in findings:
        story += [Paragraph("• "+f,styles["Normal"]),Spacer(1,4)]
    story += [Spacer(1,8),Paragraph("Limitations",styles["Heading2"]),
      Paragraph("The image overlay is based on high-contrast edges and is not a trained AI crack detector. It may highlight texture, joints, shadows or stains. No AI confidence score or remaining-life estimate is generated. All dimensions are user-entered and must be verified on site. This report is not a safety certificate or repair specification.",styles["Normal"])]
    for title,im in [("Uploaded image",img),("Edge-review overlay",over)]:
        if im:
            tmp=BytesIO(); copy=im.copy(); copy.thumbnail((1200,800)); copy.save(tmp,format="JPEG",quality=82); tmp.seek(0)
            story += [Spacer(1,8),Paragraph(title,styles["Heading2"]),RImage(tmp,width=145*mm,height=82*mm)]
    doc.build(story)
    return buf.getvalue()

# Inputs
st.markdown('<div class="section-label">① Project Inputs</div>',unsafe_allow_html=True)
a,b,c=st.columns([1.3,1,1])
with a:
    uploaded=st.file_uploader("Upload building / crack image",type=["jpg","jpeg","png","webp"])
with b:
    building=st.selectbox("Building type",["Residential","Commercial","Industrial","Institutional","Other"])
    floors=st.number_input("Number of floors",min_value=1,max_value=100,value=3)
with c:
    location=st.text_input("Building location",placeholder="e.g. Telangana, Hyderabad")
    area=st.selectbox("Observed area",["Wall - North side","Wall - South side","Wall - East side","Beam","Column","Slab / ceiling","Foundation","Other"])

img=None
filename=""
if uploaded:
    filename=uploaded.name
    try:
        img=Image.open(uploaded).convert("RGB")
        if img.width>2000:
            nh=int(img.height*2000/img.width); img=img.resize((2000,nh))
    except Exception:
        st.error("Could not read this image. Please upload a JPG or PNG.")

st.markdown('<div class="arrow">↓</div>',unsafe_allow_html=True)

# Workflow cards 2-4
c2,c3,c4=st.columns([1,1.35,1.4],gap="medium")
with c2:
    st.markdown('<div class="panel panel-purple"><div class="stephead"><span class="stepnum purple">2</span><span class="tag purple">Image Processing</span></div><p>The uploaded image is enhanced for visual review.</p></div>',unsafe_allow_html=True)
    if img:
        st.image(img,caption="Original image",use_container_width=True)
        enhanced=enhance(img)
        st.image(enhanced,caption="Enhanced image",use_container_width=True)
    else:
        st.info("Upload an image to see original and enhanced views.")
        enhanced=None
with c3:
    st.markdown('<div class="panel panel-green"><div class="stephead"><span class="stepnum green">3</span><span class="tag green">Crack Image Review</span></div><p>High-contrast edges are highlighted for manual review.</p></div>',unsafe_allow_html=True)
    if img:
        over=overlay_edges(enhanced)
        st.image(over,caption="Edge-review overlay — not AI crack detection",use_container_width=True)
        st.caption("Red marks may include cracks, texture, joints, shadows or stains.")
    else:
        over=None
        st.info("The image review overlay appears after upload.")
with c4:
    st.markdown('<div class="panel panel-pink"><div class="stephead"><span class="stepnum pink">4</span><span class="tag pink">Measurement & Classification</span></div><p>Enter dimensions measured on site. The app cannot infer real-world scale from an uncalibrated photo.</p></div>',unsafe_allow_html=True)
    pattern=st.selectbox("Observed crack pattern",["Not assessed","Vertical","Horizontal","Diagonal","Map / network","Hairline / fine","Multiple / irregular"])
    width=st.number_input("Measured width (mm)",min_value=0.0,max_value=100.0,value=0.0,step=0.1)
    length=st.number_input("Measured length (m)",min_value=0.0,max_value=1000.0,value=0.0,step=0.1)
    if width<=0:
        risk="Not assessed"
        advice="Enter a site-measured width for a basic screening prompt."
        color="#52657b"
    elif width<0.3:
        risk="Lower width band — monitor context"
        advice="Document and monitor; width alone does not prove the crack is harmless."
        color="#087c52"
    elif width<1:
        risk="Professional review recommended"
        advice="Arrange an assessment if recurring, widening, damp, or associated with movement."
        color="#aa7209"
    else:
        risk="Prompt professional assessment"
        advice="Seek an on-site structural assessment promptly. This is not a diagnosis of failure."
        color="#b42336"
    st.markdown(f'<div style="border-radius:9px;background:#fff;padding:10px;border:1px solid #d9e3ed"><b>Screening prompt</b><br><span style="color:{color};font-weight:800">{risk}</span><p style="margin:6px 0 0;color:#52657b;font-size:.85rem">{advice}</p></div>',unsafe_allow_html=True)

st.markdown('<div class="arrow">↓</div>',unsafe_allow_html=True)

# Assessment and recommendations
findings=[]
if img:
    findings.append("Image supplied; lighting, focus, surface texture and angle can affect visual review.")
else:
    findings.append("No image has been uploaded.")
if pattern!="Not assessed":
    findings.append(f"User-selected observed pattern: {pattern.lower()} at {area.lower()}.")
if width>0:
    findings.append(f"User-entered width: {width:.1f} mm; verify with a crack gauge on site.")
if length>0:
    findings.append(f"User-entered length: {length:.1f} m; verify on site.")
findings.extend(["Record dated photographs and monitor whether the crack changes.",
                 "Have a qualified structural engineer assess cracks near beams, columns, slabs or foundations, or cracks associated with movement, sagging, water ingress or falling concrete."])
r1,r2=st.columns([1,1],gap="medium")
with r1:
    st.markdown('<div class="panel panel-yellow"><div class="stephead"><span class="stepnum gold">5</span><span class="tag gold">Structural Assessment</span></div><p>Summary based on the image upload and details entered.</p></div>',unsafe_allow_html=True)
    st.markdown('<div class="darkbox"><h4>Preliminary screening</h4><hr>',unsafe_allow_html=True)
    st.markdown(f"**Screening prompt:** {risk}")
    st.markdown("**Possible causes to investigate**")
    st.write("• Shrinkage or temperature movement")
    st.write("• Water ingress, poor curing or joint movement")
    st.write("• Settlement, corrosion or structural movement")
    st.markdown("**Possible structural concern**")
    st.write("Image-only screening cannot determine whether the crack is structural.")
    st.markdown("</div>",unsafe_allow_html=True)
with r2:
    st.markdown('<div class="panel panel-purple"><div class="stephead"><span class="stepnum purple">6</span><span class="tag purple">Repair & Safety Actions</span></div><p>Recommended next steps for professional review.</p></div>',unsafe_allow_html=True)
    st.markdown('<div class="panel" style="margin-top:8px"><b>🔎 Possible causes</b><br>• Shrinkage / thermal movement<br>• Poor curing, water ingress or structural movement<hr><b>🔧 Recommended actions</b><br>• Document and monitor the crack<br>• Ask an engineer to determine the cause before selecting a repair<hr><b>🛡️ Safety advice</b><br>• If there is sudden movement, major sagging, falling concrete or rapid crack growth, keep people away and seek urgent professional help.</div>',unsafe_allow_html=True)

st.markdown('<div class="arrow">↓</div>',unsafe_allow_html=True)

# Final report
st.markdown('<div class="section-label">⑦ Final Inspection Report</div>',unsafe_allow_html=True)
project={"building":building,"floors":int(floors),"location":location.strip(),"area":area,"filename":filename,"pattern":pattern,"width":width,"length":length}
paper1,paper2=st.columns([1.15,1])
with paper1:
    st.markdown('<div class="report-paper"><h3 style="color:#0b2c50;margin:0">⌂ STRUCTURE DOCTOR AI</h3><b>Building Inspection Report</b><hr>',unsafe_allow_html=True)
    st.write(f"**Building:** {building} · **Floors:** {floors}")
    st.write(f"**Location:** {location.strip() or 'Not supplied'}")
    st.write(f"**Observed area:** {area}")
    st.write(f"**Crack pattern:** {pattern}")
    st.write(f"**Measured width:** {width:.1f} mm" if width>0 else "**Measured width:** Not supplied")
    st.write(f"**Measured length:** {length:.1f} m" if length>0 else "**Measured length:** Not supplied")
    st.write(f"**Screening:** {risk}")
    if img:
        st.image(img,caption="Uploaded building image",use_container_width=True)
    st.markdown('</div>',unsafe_allow_html=True)
with paper2:
    st.markdown('<div class="panel panel-blue"><h3>Remaining safe life</h3><p>A number of years cannot be reliably calculated from a photograph alone.</p></div>',unsafe_allow_html=True)
    st.error("Remaining safe life: not determined. A qualified structural engineer must assess the building on site.")
    st.markdown("**Key findings**")
    for f in findings:
        st.write("• "+f)
    st.caption("No validated AI model is connected, so no AI confidence score is reported.")

pdf=pdf_report(project,findings,risk,img,over if img else None)
d1,d2=st.columns(2)
with d1:
    if pdf:
        st.download_button("⬇ Save Final Inspection Report as PDF",data=pdf,file_name="structure_doctor_inspection_report.pdf",mime="application/pdf",type="primary",use_container_width=True)
    else:
        st.error("Install reportlab using: py -m pip install reportlab")
with d2:
    if img:
        ib=BytesIO(); over.save(ib,format="PNG")
        st.download_button("⬇ Download review overlay",data=ib.getvalue(),file_name="crack_review_overlay.png",mime="image/png",use_container_width=True)

st.markdown('<div style="margin-top:18px;padding:14px;border:1px solid #b8dff3;border-radius:10px;background:#f0f9ff;color:#16456a">✓ <b>Review workflow ready</b><br><span style="font-size:.88rem">This prototype updates its images and report fields when you change the upload or project inputs. It is not a structural safety certificate.</span></div>',unsafe_allow_html=True)
