import streamlit as st
from streamlit_drawable_canvas import st_canvas
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image as RLImage
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT
import tempfile
import os
from datetime import datetime
from PIL import Image
import io
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import re
import numpy as np

# -----------------------------
# Page configuration & styling
# -----------------------------
st.set_page_config(
    page_title="Ad Manager & Partnership Agreement - The ATM Agency",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #0ea5a4;
        color: white;
        font-weight: 600;
        padding: 0.6rem 1rem;
        border-radius: 0.5rem;
        border: none;
    }
    .info-box { background-color: #eef2ff; padding: 1rem; border-left: 4px solid #6366f1; border-radius: 6px; margin: 1rem 0; }
    .warning-box { background-color: #fff7ed; padding: 1rem; border-left: 4px solid #f59e0b; border-radius: 6px; margin: 1rem 0; }
    .success-box { background-color: #ecfdf5; padding: 1rem; border-left: 4px solid #10b981; border-radius: 6px; margin: 1rem 0; }
    h1 { color: #0f172a; font-size: 2rem !important; }
    h2 { color: #0f172a; }
    </style>
""", unsafe_allow_html=True)

# -----------------------------
# Email config from secrets
# -----------------------------
try:
    EMAIL_ADDRESS = st.secrets["email"]["sender_email"]
    EMAIL_PASSWORD = st.secrets["email"]["password"]
    SMTP_SERVER = st.secrets["email"]["smtp_server"]
    PORT = st.secrets["email"]["port"]
    ADMIN_EMAIL = st.secrets["email"].get("admin_email", None)
except Exception:
    EMAIL_ADDRESS = None
    EMAIL_PASSWORD = None
    SMTP_SERVER = None
    PORT = None
    ADMIN_EMAIL = None
    st.warning("⚠️ Email credentials not found in secrets. Email sending will be disabled; PDF download will still work.")

# -----------------------------
# Session state initialization
# -----------------------------
if 'agreement_accepted' not in st.session_state:
    st.session_state.agreement_accepted = False
if 'client_name' not in st.session_state:
    st.session_state.client_name = ""
if 'client_rep_name' not in st.session_state:
    st.session_state.client_rep_name = ""
if 'client_email' not in st.session_state:
    st.session_state.client_email = ""
if 'agency_rep_name' not in st.session_state:
    st.session_state.agency_rep_name = "The ATM Agency Representative"
if 'agency_email' not in st.session_state:
    st.session_state.agency_email = ""
if 'state_law' not in st.session_state:
    st.session_state.state_law = ""
if 'effective_date' not in st.session_state:
    st.session_state.effective_date = datetime.now().date()

# -----------------------------
# Agreement text (replace in PDF)
# -----------------------------
agreement_text = """
AD MANAGER & PARTNERSHIP AGREEMENT

This Ad Manager & Partnership Agreement (“Agreement”) is entered into between:

The ATM Agency (“Agency”)  
and  
[Client Name] (“Client”)  
Effective as of [Effective Date].

1. SCOPE OF SERVICES
The Agency will manage paid advertising campaigns, strategy, creative assets, and performance optimization for the Client’s digital products, online courses, and associated offers.

Core responsibilities include:
• Full ad account management (Facebook/Meta, Instagram, TikTok, Google, YouTube, or other platforms as needed)
• Ad creation, creative direction, and copywriting
• Campaign testing and optimization
• Funnel monitoring and recommendations
• Weekly and monthly performance reporting
• Scaling campaigns based on performance metrics
• Audience research and targeting
• Offer positioning assistance
• Budget allocation guidance

2. COMMISSION & PAYMENT TERMS
The Client agrees to pay The ATM Agency a commission of:

10% of all sales generated from paid advertising campaigns managed by the Agency.

Details:
• Commission applies to digital products, online courses, downloads, coaching programs, and all digital-based revenue generated through Agency-managed campaigns.
• Commission is calculated from gross revenue (before refunds, payment processor fees, or deductions).
• Payments to the Agency are due within 7 days of each completed calendar month.
• The Client must provide accurate sales data, dashboards, and reporting access.
• If the Client uses a third-party payment processor, the Agency must be granted read-only access.

3. AD SPEND & ACCOUNT ACCESS
The Client agrees to:
• Pay all advertising spend directly to the ad platform.
• Provide necessary account access (Ad Manager, Pixel/Conversions API, Website, CRM, Funnels, etc.).
• Maintain all accounts in good standing to prevent disruption.

The Agency is not responsible for platform bans, disabled accounts, or restricted features.

4. CONTENT & CREATIVE
The Agency may create and test ad creatives, including images, videos, ad copy, headlines, and marketing scripts. The Client agrees to provide brand guidelines, product access, testimonials, and any requested materials.

5. PERFORMANCE DISCLAIMER
The Agency does not guarantee specific results, performance metrics, earnings, or sales outcomes. All advertising includes risk and is subject to platform algorithm changes.

6. TERM & TERMINATION
This Agreement renews month-to-month unless terminated with 14 days written notice by either party.

Upon termination:
• All commissions owed remain payable to the Agency.
• The Agency will provide a transition period of up to 7 days.
• The Client retains ownership of all ad accounts and assets the Client originally owned.
• The Agency retains ownership of any proprietary frameworks or templates.

7. CONFIDENTIALITY
Both parties agree to strict confidentiality regarding customer data, funnels, sales systems, and marketing strategies. This clause survives termination.

8. INTELLECTUAL PROPERTY
The Client owns all content, funnels, products, and materials they provide. The Agency owns its internal processes, frameworks, and optimization systems. Creations specifically for the Client (ad copy, creatives, audiences, etc.) become Client-owned upon payment of all commissions.

9. NON-DISPARAGEMENT
Both parties agree not to make negative or harmful public statements about the other.

10. LIMITATION OF LIABILITY
The Agency shall not be liable for loss of revenue, ad account shutdowns, platform instability, third-party software issues, chargebacks, or customer disputes. Liability is limited to the amount paid by the Client in the last 30 days.

11. GOVERNING LAW
This Agreement is governed by the laws of the State of [State].

12. ENTIRE AGREEMENT
This Agreement constitutes the full understanding between the parties and supersedes all prior discussions.

AGREED & ACCEPTED:

______________________________
Client
Name: [Client Name]
Date: _______________

______________________________
The ATM Agency
Name: [Agency Rep Name]
Date: _______________
"""

# -----------------------------
# UI Header
# -----------------------------
st.title("📄 Ad Manager & Partnership Agreement")
st.markdown("### Commission-Based Ad Management Contract — The ATM Agency")
st.markdown("---")
st.markdown('<div class="info-box">🔎 This agreement establishes a 10% commission structure for ad-driven sales of digital products & courses. Review carefully before signing.</div>', unsafe_allow_html=True)

# -----------------------------
# Display agreement preview
# -----------------------------
with st.expander("📜 View Full Agreement Text", expanded=False):
    st.markdown(agreement_text.replace("\n", "  \n"))

agreement_checkbox = st.checkbox(
    "✅ I have read, understand, and agree to the terms of this agreement",
    value=st.session_state.agreement_accepted
)
st.session_state.agreement_accepted = agreement_checkbox

# -----------------------------
# Helpers
# -----------------------------
def is_valid_email(email: str) -> bool:
    if not email:
        return False
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def send_agreement_email(recipient_email, recipient_name, role, pdf_data, pdf_filename):
    if not EMAIL_ADDRESS:
        return False
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = recipient_email
        msg['Subject'] = f"Signed Ad Manager Agreement - The ATM Agency - {recipient_name}"
        body = f"""Dear {recipient_name},

Please find attached the signed Ad Manager & Partnership Agreement between The ATM Agency and {recipient_name}.

Role: {role}
Date Signed: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}

If you have any questions, reply to this email.

Regards,
The ATM Agency
"""
        msg.attach(MIMEText(body, 'plain'))

        part = MIMEBase('application', 'octet-stream')
        part.set_payload(pdf_data)
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename={pdf_filename}')
        msg.attach(part)

        server = smtplib.SMTP(SMTP_SERVER, int(PORT))
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        st.error(f"Email send error: {e}")
        return False

# -----------------------------
# Step 2: Enter Agreement Details
# -----------------------------
if st.session_state.agreement_accepted:
    st.markdown("---")
    st.header("Step 1 — Enter Agreement Details")

    col1, col2 = st.columns(2)
    with col1:
        client_name = st.text_input("Client / Company Name *", value=st.session_state.client_name, placeholder="Client Company LLC")
        st.session_state.client_name = client_name

        client_rep_name = st.text_input("Client Representative Name *", value=st.session_state.client_rep_name, placeholder="Jane Client")
        st.session_state.client_rep_name = client_rep_name

        client_email = st.text_input("Client Email *", value=st.session_state.client_email, placeholder="jane@client.com")
        st.session_state.client_email = client_email

    with col2:
        st.markdown("**Agency details (pre-filled)**")
        st.markdown(f"**Agency:** The ATM Agency")
        agency_rep_name = st.text_input("Agency Representative Name", value=st.session_state.agency_rep_name)
        st.session_state.agency_rep_name = agency_rep_name
        agency_email = st.text_input("Agency Email (optional)", value=st.session_state.agency_email, placeholder="agency@theatm.agency")
        st.session_state.agency_email = agency_email

        effective_date = st.date_input("Effective Date *", value=st.session_state.effective_date)
        st.session_state.effective_date = effective_date

    state_law = st.text_input("Governing State Law *", value=st.session_state.state_law, placeholder="Delaware")
    st.session_state.state_law = state_law

    # validation
    valid = True
    if not client_name.strip():
        st.error("Please enter the Client / Company name.")
        valid = False
    if not client_rep_name.strip():
        st.error("Please enter the Client representative name.")
        valid = False
    if not is_valid_email(client_email):
        st.error("Please enter a valid client email.")
        valid = False
    if not state_law.strip():
        st.error("Please enter the governing state for law.")
        valid = False

    if valid:
        st.success("All required fields filled. Proceed to signatures below.")
else:
    st.info("Please read and accept the agreement to continue.")

# -----------------------------
# Step 3: Signatures & PDF
# -----------------------------
if st.session_state.agreement_accepted and valid:
    st.markdown("---")
    st.header("Step 2 — Digital Signatures")

    st.markdown('<div class="warning-box">⚠️ Digital signatures are legally binding. Both parties must sign the form below.</div>', unsafe_allow_html=True)

    # Client signature
    st.subheader("Client Signature")
    st.markdown(f"**Signing as:** {st.session_state.client_rep_name} (Client Representative)")
    client_canvas = st_canvas(
        fill_color="rgba(255, 255, 255, 0)",
        stroke_width=2,
        stroke_color="#000000",
        background_color="#ffffff",
        update_streamlit=True,
        height=180,
        width=700,
        drawing_mode="freedraw",
        key="client_sig_canvas",
    )
    if st.button("Clear Client Signature", key="clear_client_sig"):
        st.session_state.pop("client_sig_canvas", None)
        st.experimental_rerun()

    st.markdown("---")

    # Agency signature
    st.subheader("Agency Signature")
    st.markdown(f"**Signing as:** {st.session_state.agency_rep_name} (The ATM Agency)")
    agency_canvas = st_canvas(
        fill_color="rgba(255, 255, 255, 0)",
        stroke_width=2,
        stroke_color="#000000",
        background_color="#ffffff",
        update_streamlit=True,
        height=180,
        width=700,
        drawing_mode="freedraw",
        key="agency_sig_canvas",
    )
    if st.button("Clear Agency Signature", key="clear_agency_sig"):
        st.session_state.pop("agency_sig_canvas", None)
        st.experimental_rerun()

    # Generate PDF button
    st.markdown("---")
    st.header("Step 3 — Generate & Download Agreement")

    generate_clicked = st.button("📥 Generate Signed Agreement PDF")

    if generate_clicked:
        # check signatures exist
        client_sig_exists = client_canvas.image_data is not None and client_canvas.image_data.sum() > 0
        agency_sig_exists = agency_canvas.image_data is not None and agency_canvas.image_data.sum() > 0

        if not client_sig_exists or not agency_sig_exists:
            st.warning("Both signatures are required to generate the signed PDF.")
        else:
            with st.spinner("Creating PDF..."):
                try:
                    # personalize agreement text
                    personalized = agreement_text.replace("[Client Name]", st.session_state.client_name)\
                        .replace("[Effective Date]", st.session_state.effective_date.strftime("%B %d, %Y"))\
                        .replace("[State]", st.session_state.state_law)\
                        .replace("[Agency Rep Name]", st.session_state.agency_rep_name)

                    # create temporary files
                    with tempfile.TemporaryDirectory() as tmpdir:
                        pdf_path = os.path.join(tmpdir, "Ad_Agreement.pdf")
                        doc = SimpleDocTemplate(pdf_path, pagesize=LETTER,
                                                rightMargin=72, leftMargin=72,
                                                topMargin=72, bottomMargin=72)

                        styles = getSampleStyleSheet()
                        styles.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY, fontSize=11, leading=14))
                        styles.add(ParagraphStyle(name='CustomTitle', fontSize=14, alignment=TA_LEFT, spaceAfter=12, textColor='#0f172a'))

                        elements = []
                        # Title
                        elements.append(Paragraph("Ad Manager & Partnership Agreement", styles['CustomTitle']))
                        elements.append(Spacer(1, 0.1*inch))

                        # Add personalized agreement body
                        for block in personalized.strip().split('\n\n'):
                            block = block.strip().replace('\n', '<br/>')
                            elements.append(Paragraph(block, styles['Justify']))
                            elements.append(Spacer(1, 0.12*inch))

                        elements.append(PageBreak())
                        elements.append(Paragraph("<b>SIGNATURES</b>", styles['CustomTitle']))
                        elements.append(Spacer(1, 0.2*inch))

                        # Save client signature image
                        client_sig_path = os.path.join(tmpdir, "client_sig.png")
                        client_img_arr = client_canvas.image_data
                        # convert to PIL image
                        client_img = Image.fromarray((client_img_arr).astype('uint8'))
                        client_img = client_img.convert("RGBA")
                        client_img.save(client_sig_path)

                        elements.append(Paragraph("<b>Client Representative</b>", styles['Normal']))
                        elements.append(Spacer(1, 0.08*inch))
                        elements.append(RLImage(client_sig_path, width=3*inch, height=0.75*inch))
                        elements.append(Paragraph(f"<b>Name:</b> {st.session_state.client_rep_name}", styles['Normal']))
                        elements.append(Paragraph(f"<b>Company:</b> {st.session_state.client_name}", styles['Normal']))
                        elements.append(Paragraph(f"<b>Email:</b> {st.session_state.client_email}", styles['Normal']))
                        elements.append(Paragraph(f"<b>Date:</b> {datetime.now().strftime('%B %d, %Y')}", styles['Normal']))

                        elements.append(Spacer(1, 0.4*inch))

                        # Save agency signature image
                        agency_sig_path = os.path.join(tmpdir, "agency_sig.png")
                        agency_img_arr = agency_canvas.image_data
                        agency_img = Image.fromarray((agency_img_arr).astype('uint8'))
                        agency_img = agency_img.convert("RGBA")
                        agency_img.save(agency_sig_path)

                        elements.append(Paragraph("<b>The ATM Agency</b>", styles['Normal']))
                        elements.append(Spacer(1, 0.08*inch))
                        elements.append(RLImage(agency_sig_path, width=3*inch, height=0.75*inch))
                        elements.append(Paragraph(f"<b>Name:</b> {st.session_state.agency_rep_name}", styles['Normal']))
                        if st.session_state.agency_email:
                            elements.append(Paragraph(f"<b>Email:</b> {st.session_state.agency_email}", styles['Normal']))
                        elements.append(Paragraph(f"<b>Date:</b> {datetime.now().strftime('%B %d, %Y')}", styles['Normal']))

                        # build pdf
                        doc.build(elements)

                        # read pdf bytes
                        with open(pdf_path, "rb") as f:
                            pdf_bytes = f.read()

                        pdf_filename = f"Ad_Agreement_{st.session_state.client_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf"

                        st.success("Signed agreement created successfully.")
                        st.download_button("⬇️ Download Signed Agreement PDF", data=pdf_bytes, file_name=pdf_filename, mime="application/pdf")

                        # attempt to email if config present
                        if EMAIL_ADDRESS:
                            with st.spinner("Sending agreement to parties via email..."):
                                sent_client = send_agreement_email(st.session_state.client_email, st.session_state.client_rep_name, "Client Representative", pdf_bytes, pdf_filename)
                                sent_agency = False
                                if st.session_state.agency_email:
                                    sent_agency = send_agreement_email(st.session_state.agency_email, st.session_state.agency_rep_name, "Agency Representative", pdf_bytes, pdf_filename)
                                # admin copy
                                sent_admin = False
                                if ADMIN_EMAIL:
                                    sent_admin = send_agreement_email(ADMIN_EMAIL, "Admin", "Admin Copy", pdf_bytes, pdf_filename)

                                if sent_client or sent_agency or sent_admin:
                                    st.info("Emails attempted. Check logs or inboxes.")
                                else:
                                    st.warning("Email sending failed - check SMTP configuration in Streamlit secrets.")

                except Exception as e:
                    st.error(f"An error occurred while generating the PDF: {e}")

# Footer / disclaimer
st.markdown("---")
st.markdown("""
<div style='text-align:center; color:#64748b; padding:1rem 0'>
    <strong>The ATM Agency — Ad Manager & Partnership Agreement System</strong><br/>
    This is a legally binding agreement. Consult legal counsel for legal advice.
</div>
""", unsafe_allow_html=True)
