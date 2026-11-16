from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_ALIGN_VERTICAL, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor


OUT = Path("docs/FaceGuard_Edge_AI_NHAI_Hackathon_Proposal.docx")

BLUE = "1F4D78"
LIGHT_BLUE = "E8EEF5"
LIGHT_GRAY = "F4F6F9"
DARK = "17211D"
GREEN = "136F4A"


def shade_cell(cell, fill):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), fill)
    tc_pr.append(shd)


def set_cell_text(cell, text, bold=False, color=DARK, size=10):
    cell.text = ""
    p = cell.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    run = p.add_run(text)
    run.bold = bold
    run.font.name = "Calibri"
    run.font.size = Pt(size)
    run.font.color.rgb = RGBColor.from_string(color)
    cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER


def set_table_geometry(table):
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    tbl = table._tbl
    tbl_pr = tbl.tblPr
    tbl_w = tbl_pr.find(qn("w:tblW"))
    if tbl_w is None:
        tbl_w = OxmlElement("w:tblW")
        tbl_pr.append(tbl_w)
    tbl_w.set(qn("w:w"), "9360")
    tbl_w.set(qn("w:type"), "dxa")
    for row in table.rows:
        for cell in row.cells:
            tc_pr = cell._tc.get_or_add_tcPr()
            tc_mar = tc_pr.find(qn("w:tcMar"))
            if tc_mar is None:
                tc_mar = OxmlElement("w:tcMar")
                tc_pr.append(tc_mar)
            for side, value in [("top", "80"), ("bottom", "80"), ("start", "120"), ("end", "120")]:
                node = tc_mar.find(qn(f"w:{side}"))
                if node is None:
                    node = OxmlElement(f"w:{side}")
                    tc_mar.append(node)
                node.set(qn("w:w"), value)
                node.set(qn("w:type"), "dxa")


def add_title(doc, title, subtitle=None):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(8)
    r = p.add_run(title)
    r.font.name = "Calibri"
    r.font.size = Pt(24)
    r.font.bold = True
    r.font.color.rgb = RGBColor.from_string(BLUE)
    if subtitle:
        p2 = doc.add_paragraph()
        p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p2.paragraph_format.space_after = Pt(18)
        r2 = p2.add_run(subtitle)
        r2.font.name = "Calibri"
        r2.font.size = Pt(13)
        r2.font.color.rgb = RGBColor.from_string(DARK)


def add_heading(doc, text, level=1):
    p = doc.add_paragraph()
    if level == 1:
        p.style = "Heading 1"
    elif level == 2:
        p.style = "Heading 2"
    else:
        p.style = "Heading 3"
    p.add_run(text)
    return p


def add_body(doc, text, bold_lead=None):
    p = doc.add_paragraph()
    p.style = "Body Text"
    if bold_lead:
        r = p.add_run(bold_lead)
        r.bold = True
        p.add_run(text)
    else:
        p.add_run(text)
    return p


def add_bullets(doc, items):
    for item in items:
        p = doc.add_paragraph(style="List Bullet")
        p.add_run(item)


def add_numbered(doc, items):
    for item in items:
        p = doc.add_paragraph(style="List Number")
        p.add_run(item)


def add_callout(doc, title, body, fill=LIGHT_GRAY):
    table = doc.add_table(rows=1, cols=1)
    set_table_geometry(table)
    cell = table.cell(0, 0)
    shade_cell(cell, fill)
    p = cell.paragraphs[0]
    p.paragraph_format.space_after = Pt(4)
    r = p.add_run(title)
    r.bold = True
    r.font.color.rgb = RGBColor.from_string(BLUE)
    r.font.size = Pt(11)
    p.add_run("\n" + body)
    doc.add_paragraph()


def add_table(doc, headers, rows, widths=None):
    table = doc.add_table(rows=1, cols=len(headers))
    table.style = "Table Grid"
    set_table_geometry(table)
    for i, header in enumerate(headers):
        cell = table.rows[0].cells[i]
        shade_cell(cell, LIGHT_BLUE)
        set_cell_text(cell, header, bold=True, color=BLUE, size=9)
        if widths:
            cell.width = Inches(widths[i])
    for row in rows:
        cells = table.add_row().cells
        for i, value in enumerate(row):
            set_cell_text(cells[i], str(value), size=9)
            if widths:
                cells[i].width = Inches(widths[i])
    doc.add_paragraph()
    return table


def add_ascii_diagram(doc):
    diagram = r"""
+--------------------+       +-----------------------+
| Mobile Camera / UI | ----> | Face Quality Control |
+--------------------+       +-----------------------+
           |                              |
           v                              v
+--------------------+       +-----------------------+
| Face Detection     | ----> | Liveness Detection   |
| OpenCV / ArcFace   |       | Blink + Motion +     |
+--------------------+       | Anti-Spoofing        |
           |                 +-----------------------+
           v                              |
+--------------------+                    v
| Recognition Engine | ----> +-----------------------+
| Local Embeddings   |       | Decision Engine      |
+--------------------+       | Live / Fake / Match  |
           |                 +-----------------------+
           v                              |
+--------------------+                    v
| Encrypted SQLite   | <---- +-----------------------+
| Local Database     |       | Dashboard + Audit    |
+--------------------+       +-----------------------+
           |
           v
+--------------------+
| DataLake 3.0 Queue |
| REST / Local Sync  |
+--------------------+
"""
    table = doc.add_table(rows=1, cols=1)
    set_table_geometry(table)
    cell = table.cell(0, 0)
    shade_cell(cell, "F8FAFC")
    p = cell.paragraphs[0]
    run = p.add_run(diagram.strip())
    run.font.name = "Courier New"
    run.font.size = Pt(8.5)
    run.font.color.rgb = RGBColor.from_string(DARK)
    doc.add_paragraph()


def configure_styles(doc):
    section = doc.sections[0]
    section.top_margin = Inches(1)
    section.bottom_margin = Inches(1)
    section.left_margin = Inches(1)
    section.right_margin = Inches(1)
    section.header_distance = Inches(0.492)
    section.footer_distance = Inches(0.492)

    styles = doc.styles
    normal = styles["Normal"]
    normal.font.name = "Calibri"
    normal.font.size = Pt(11)
    normal.font.color.rgb = RGBColor.from_string(DARK)
    normal.paragraph_format.space_after = Pt(8)
    normal.paragraph_format.line_spacing = 1.25

    for name in ["Body Text", "List Bullet", "List Number"]:
        style = styles[name]
        style.font.name = "Calibri"
        style.font.size = Pt(11)
        style.paragraph_format.space_after = Pt(4 if "List" in name else 8)
        style.paragraph_format.line_spacing = 1.208 if "List" in name else 1.25

    for name, size, color, before, after in [
        ("Heading 1", 16, BLUE, 16, 8),
        ("Heading 2", 13, BLUE, 12, 6),
        ("Heading 3", 12, "1F4D78", 8, 4),
    ]:
        style = styles[name]
        style.font.name = "Calibri"
        style.font.size = Pt(size)
        style.font.bold = True
        style.font.color.rgb = RGBColor.from_string(color)
        style.paragraph_format.space_before = Pt(before)
        style.paragraph_format.space_after = Pt(after)


def add_footer(doc):
    for section in doc.sections:
        footer = section.footer.paragraphs[0]
        footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = footer.add_run("FaceGuard Edge AI | NHAI Innovation Hackathon 7.0 | Confidential Proposal")
        run.font.size = Pt(8)
        run.font.color.rgb = RGBColor.from_string("666666")


def build():
    doc = Document()
    configure_styles(doc)

    # Cover page
    for _ in range(5):
        doc.add_paragraph()
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("NHAI Innovation Hackathon 7.0")
    r.font.size = Pt(18)
    r.font.bold = True
    r.font.color.rgb = RGBColor.from_string(BLUE)
    p.paragraph_format.space_after = Pt(18)

    add_title(doc, "FaceGuard Edge AI", "Mobile-Based Secure Offline Facial Recognition and Liveness Detection System for Remote Locations")

    meta = doc.add_table(rows=5, cols=2)
    set_table_geometry(meta)
    meta.alignment = WD_TABLE_ALIGNMENT.CENTER
    data = [
        ("Team Name", "FaceGuard Innovators"),
        ("Team Members", "Karnatakam Srivalli\nKalapala Sri Sai Krishna"),
        ("Institution", "Woxsen University"),
        ("Submission Type", "Innovation Proposal and Prototype Solution"),
        ("Focus Area", "Offline Identity Verification, Edge AI, Anti-Spoofing, Secure Field Deployment"),
    ]
    for i, (k, v) in enumerate(data):
        set_cell_text(meta.cell(i, 0), k, bold=True, color=BLUE)
        set_cell_text(meta.cell(i, 1), v)
        shade_cell(meta.cell(i, 0), LIGHT_BLUE)
    doc.add_paragraph()
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("Prepared for Government Evaluation")
    r.bold = True
    r.font.size = Pt(11)
    r.font.color.rgb = RGBColor.from_string(GREEN)
    doc.add_page_break()

    add_heading(doc, "1. Executive Summary", 1)
    add_body(
        doc,
        "FaceGuard Edge AI is a secure, mobile-ready, offline facial recognition and liveness detection platform designed for remote highway infrastructure locations where reliable network access cannot be assumed. The solution addresses a critical operational gap: identity verification systems used in field offices, security checkpoints, toll plazas, and control rooms often depend on cloud connectivity, external authentication services, or centralized inference pipelines. These dependencies create delays, downtime, and security exposure when deployed in low-connectivity regions.",
    )
    add_body(
        doc,
        "Our proposed system performs face registration, recognition, liveness detection, audit logging, and dashboard analytics entirely on the edge device. The architecture uses local AI inference through OpenCV, InsightFace/ArcFace-compatible embeddings, MediaPipe-based motion cues, ONNX Runtime acceleration, and an encrypted SQLite identity store. The system is designed for offline-first operation: once deployed, it does not require internet access for facial matching, liveness scoring, attendance capture, or audit review.",
    )
    add_body(
        doc,
        "The innovation lies in combining lightweight edge AI with multi-layer anti-spoofing in a mobile-friendly deployment model. FaceGuard Edge AI verifies blink evidence, head movement, micro facial motion, texture quality, screen glare patterns, and replay-like artifacts before accepting an identity match. This directly reduces the risk of printed photograph attacks, mobile screen attacks, and replay attempts.",
    )
    add_body(
        doc,
        "For NHAI, the expected impact is a practical and scalable identity verification system that supports secure operations in zero-network environments. It can strengthen field attendance, access control, site security, and auditability while remaining future-ready for DataLake 3.0 integration through a local queue and sync adapter architecture.",
    )

    add_heading(doc, "2. Problem Statement", 1)
    add_body(
        doc,
        "Remote highway and infrastructure locations often operate under difficult connectivity conditions. Field teams, security staff, contractors, and administrative personnel may need identity verification at toll plazas, control centers, checkpoints, maintenance zones, and regional offices where network quality is inconsistent or unavailable.",
    )
    add_bullets(
        doc,
        [
            "Poor network connectivity can interrupt cloud-based identity systems and delay operational decisions.",
            "Security risks increase when identity verification falls back to manual checks or paper-based registers.",
            "Cloud-dependent facial recognition systems may fail when remote locations cannot maintain continuous internet access.",
            "Centralized systems can introduce latency, privacy concerns, and operational dependency on external services.",
        ],
    )
    add_body(
        doc,
        "Traditional facial recognition platforms are usually designed around online enrollment, cloud inference, centralized databases, or API-based verification. These assumptions are not suitable for remote deployment scenarios. When connectivity fails, identity workflows stop. When latency is high, operators lose confidence in the system. When sensitive biometric data must travel over networks, the security and privacy burden increases.",
    )
    add_callout(
        doc,
        "Core Challenge",
        "NHAI needs a secure facial recognition and liveness detection system that can continue functioning in zero-network environments without compromising accuracy, auditability, or deployment practicality.",
    )

    doc.add_page_break()
    add_heading(doc, "3. Proposed Solution: FaceGuard Edge AI", 1)
    add_body(
        doc,
        "FaceGuard Edge AI is an offline-first identity verification solution that can be deployed on a mobile device, laptop, or compact edge machine. The solution captures a live camera frame, validates face quality, performs local face detection, generates or compares facial embeddings, evaluates liveness, and records the decision in a secure local audit trail.",
    )
    add_heading(doc, "How the Solution Works Without Internet", 2)
    add_numbered(
        doc,
        [
            "The user registers through a mobile or web camera interface with employee details and a facial image.",
            "The system validates image quality and detects a face locally using the edge AI pipeline.",
            "A facial embedding is generated on-device and stored in an encrypted local database.",
            "During recognition, the live camera frame is processed locally and compared against stored embeddings.",
            "A liveness score is calculated before accepting the match.",
            "Attendance, security events, and audit logs are stored locally and queued for future DataLake 3.0 synchronization.",
        ],
    )
    add_bullets(
        doc,
        [
            "Offline facial recognition for field verification and attendance workflows.",
            "Offline liveness detection to prevent spoofing through photographs or screens.",
            "Mobile-ready deployment through a browser-based interface and lightweight backend.",
            "Secure local database for employee profiles, encrypted embeddings, attendance, and audit logs.",
            "Future-ready DataLake 3.0 integration through REST and local sync adapters.",
        ],
    )

    add_heading(doc, "4. Innovation and Uniqueness", 1)
    add_body(
        doc,
        "FaceGuard Edge AI differs from conventional systems because it treats offline capability as a primary design requirement rather than a fallback. The system is optimized for edge execution, local security, rapid response, and field usability.",
    )
    add_table(
        doc,
        ["Parameter", "Traditional Cloud-Based Systems", "FaceGuard Edge AI"],
        [
            ["Connectivity", "Requires continuous or frequent internet access", "Operates fully offline after deployment"],
            ["Inference", "Often depends on cloud APIs or centralized servers", "Runs recognition and liveness locally on edge device"],
            ["Latency", "Affected by network round-trip time", "Designed for sub-500 ms local recognition"],
            ["Data Privacy", "Biometric data may leave the site", "Embeddings remain encrypted in local storage"],
            ["Spoof Resistance", "May require separate online anti-spoofing service", "Integrated multi-layer liveness scoring"],
            ["Deployment", "Server/cloud dependency", "Mobile, laptop, or compact edge machine"],
            ["DataLake Readiness", "Direct online sync assumed", "Queue-first sync for offline continuity"],
        ],
        widths=[1.55, 2.45, 2.5],
    )

    add_heading(doc, "5. Technical Architecture", 1)
    add_ascii_diagram(doc)
    add_body(doc, "Input Layer: Mobile camera or web camera captures the user face and employee metadata during registration or recognition.")
    add_body(doc, "Face Detection Layer: OpenCV-based local detection identifies candidate face regions and applies quality validation.")
    add_body(doc, "Liveness Detection Layer: Blink, head movement, facial micro-motion, texture, and anti-spoofing checks generate a liveness score.")
    add_body(doc, "Recognition Layer: ArcFace/InsightFace-compatible embeddings are compared with encrypted local embeddings using similarity scoring.")
    add_body(doc, "Decision Engine: Combines recognition confidence and liveness score to classify the result as Recognized, Unknown, Suspicious, or Fake.")
    add_body(doc, "Local Database and Dashboard: SQLite stores employees, attendance, audit logs, and sync queue entries. The dashboard presents metrics, trends, incidents, and exportable reports.")

    doc.add_page_break()
    add_heading(doc, "6. Technology Stack", 1)
    add_table(
        doc,
        ["Layer", "Technology", "Reason for Selection"],
        [
            ["AI", "OpenCV", "Reliable offline image processing, face detection, quality checks, and efficient CPU execution."],
            ["AI", "InsightFace", "Strong facial recognition ecosystem with production-proven embedding models."],
            ["AI", "ArcFace", "High-discriminability face embedding approach suitable for identity verification."],
            ["AI", "MediaPipe", "Lightweight facial landmark and motion analysis for liveness cues."],
            ["AI Runtime", "ONNX Runtime", "Optimized local inference with CPU provider and future GPU/INT8 acceleration."],
            ["Backend", "FastAPI", "High-performance Python API framework with clear validation and integration support."],
            ["Database", "SQLite", "Portable, lightweight, offline database suitable for edge machines."],
            ["Frontend", "React", "Responsive operator dashboard with webcam-based workflows."],
            ["Frontend", "TailwindCSS", "Clean UI styling, rapid iteration, and mobile-friendly layouts."],
            ["Deployment", "Docker", "Repeatable packaging for offline edge deployment and portability."],
        ],
        widths=[1.15, 1.45, 3.9],
    )

    add_heading(doc, "7. Liveness Detection Methodology", 1)
    add_table(
        doc,
        ["Layer", "Method", "Purpose"],
        [
            ["Layer 1", "Blink Detection", "Identifies eye movement evidence and reduces risk from static printed photographs."],
            ["Layer 2", "Head Movement Verification", "Checks natural pose variation and face geometry consistency."],
            ["Layer 3", "Micro Facial Motion Detection", "Uses local facial texture and motion evidence to distinguish live subjects from flat images."],
            ["Layer 4", "Anti-Spoofing Detection", "Detects print-like texture, screen glare, saturation patterns, and replay artifacts."],
        ],
        widths=[1.0, 2.1, 3.4],
    )
    add_body(
        doc,
        "Printed photograph attacks are detected through low motion evidence, flat texture characteristics, and weak liveness scores. Mobile screen attacks are identified through glare, high brightness, saturation anomalies, and screen-like image artifacts. Replay attacks are flagged using frame artifact cues, banding patterns, and inconsistent liveness evidence. The final liveness score is combined with the recognition confidence so that a face match alone is not sufficient for acceptance.",
    )

    add_heading(doc, "8. Security Features", 1)
    add_bullets(
        doc,
        [
            "Local encryption of facial embeddings and sensitive identity artifacts.",
            "Password-protected administrator access with session-based control.",
            "Audit logging for registration, recognition, failed attempts, suspicious events, and spoofing attempts.",
            "Secure local storage using SQLite for offline persistence and recoverability.",
            "Queue-based synchronization architecture so records are not lost when the network is unavailable.",
            "Decision-level separation between identity match and liveness acceptance.",
        ],
    )

    doc.add_page_break()
    add_heading(doc, "9. Expected Outcomes and Target Metrics", 1)
    add_table(
        doc,
        ["Metric", "Target", "Operational Meaning"],
        [
            ["Recognition Accuracy", "98%+", "Reliable identity verification under controlled field enrollment conditions."],
            ["Liveness Accuracy", "95%+", "Strong separation between live users and spoofing attempts."],
            ["Recognition Speed", "<500 ms", "Usable real-time verification on edge devices."],
            ["Offline Availability", "100%", "Core registration, recognition, liveness, and audit workflows continue without internet."],
            ["Spoof Detection Rate", "95%+", "High detection of printed photo, mobile screen, and replay attacks."],
        ],
        widths=[1.65, 1.2, 3.65],
    )

    add_heading(doc, "10. Scalability and Future Scope", 1)
    add_body(
        doc,
        "FaceGuard Edge AI is designed to scale from a single mobile device to multi-location deployment. Each site can operate independently while maintaining a local audit trail. When network connectivity becomes available, queued records can be synchronized with DataLake 3.0 or another approved central system.",
    )
    add_bullets(
        doc,
        [
            "Toll Plazas: Secure attendance and access control for operators, guards, contractors, and supervisors.",
            "Highway Control Centers: Local identity verification for sensitive command-room access.",
            "Security Checkpoints: Fast verification in temporary or remote checkpoints without relying on network availability.",
            "Field Offices: Offline staff attendance, visitor verification, and audit reporting.",
            "DataLake 3.0 Integration: REST adapter and local sync adapter support future centralized analytics and compliance workflows.",
        ],
    )

    add_heading(doc, "11. Development Roadmap", 1)
    add_table(
        doc,
        ["Phase", "Focus Area", "Key Deliverables"],
        [
            ["Phase 1", "Research and Design", "Threat model, offline architecture, UI workflows, database schema."],
            ["Phase 2", "Recognition Engine", "Face detection, embedding generation, duplicate prevention, matching thresholds."],
            ["Phase 3", "Liveness Detection", "Blink, head movement, micro-motion, print/screen/replay anti-spoofing."],
            ["Phase 4", "Dashboard", "Admin login, registration, real-time recognition, analytics, audit views."],
            ["Phase 5", "Testing and Optimization", "Latency benchmarking, low-light tests, spoof tests, memory and CPU tuning."],
            ["Phase 6", "Deployment", "Docker packaging, offline installation guide, DataLake sync adapter readiness."],
        ],
        widths=[1.1, 1.75, 3.65],
    )

    add_heading(doc, "12. Social and Operational Impact", 1)
    add_body(
        doc,
        "For NHAI, the solution strengthens security operations and improves the reliability of identity verification in difficult field conditions. It can reduce manual verification burden, improve audit quality, and support faster operational decisions at distributed infrastructure locations.",
    )
    add_body(
        doc,
        "For government agencies, the system demonstrates a privacy-conscious edge AI model where sensitive biometric data remains local and encrypted. For remote infrastructure projects, it provides a practical path to secure digital verification even when connectivity is intermittent. For security teams, it provides immediate visibility into failed attempts, suspicious liveness results, and spoofing incidents.",
    )

    add_heading(doc, "13. Conclusion", 1)
    add_body(
        doc,
        "FaceGuard Edge AI presents a practical, secure, and scalable approach to mobile-based offline facial recognition and liveness detection for remote locations. The solution is built around offline-first architecture, local AI inference, encrypted storage, auditability, and future-ready DataLake 3.0 integration.",
    )
    add_body(
        doc,
        "By combining edge-optimized facial recognition with multi-layer liveness detection, FaceGuard Edge AI addresses the key limitations of cloud-dependent systems and offers a deployment-ready model for NHAI field environments. The proposal is designed not only as a hackathon prototype, but as a foundation for real-world government infrastructure security workflows.",
    )
    add_callout(
        doc,
        "Final Value Proposition",
        "FaceGuard Edge AI enables secure identity verification anywhere: no cloud dependency, no internet requirement during inference, strong anti-spoofing, encrypted local storage, and scalable integration readiness for NHAI's digital ecosystem.",
        fill="ECF8F0",
    )

    add_footer(doc)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc.save(OUT)
    print(OUT.resolve())


if __name__ == "__main__":
    build()
