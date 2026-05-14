"""
Generate synthetic sample lab PDFs for biomarker_brief demo.

100% fake data. Three vendor styles (Quest-like, LabCorp-like,
Function-Health-like) plus one CSV. Three draw dates so the trend cell
has something to plot.

Run once to regenerate:
    python3 _generate_samples.py
"""

from __future__ import annotations

import csv
from pathlib import Path

from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak,
)

OUT = Path(__file__).parent

# All values below are SYNTHETIC. Patient is a fictitious composite.
PATIENT = {
    "name": "DOE, JANE Q (FICTIONAL)",
    "dob": "1985-04-12",
    "sex": "F",
    "mrn": "SAMPLE-000000",
    "provider": "Dr. Example, MD",
}

# Three draw dates spanning ~14 months so trends are visible.
DRAWS = [
    {"date": "2024-03-04", "vendor": "quest",         "file": "labs_2024-03-04_quest.pdf"},
    {"date": "2024-09-18", "vendor": "labcorp",       "file": "labs_2024-09-18_labcorp.pdf"},
    {"date": "2025-04-22", "vendor": "function",      "file": "labs_2025-04-22_function.pdf"},
]

# Values progress over time so the trend cell finds something interesting:
# - LDL drifts down (improvement)
# - HbA1c drifts up (worsening, but still in-range -> good trend-detection demo)
# - Vitamin D recovers after supplementation
# - Ferritin drops (mild iron decline)
RESULTS_BY_DATE = {
    "2024-03-04": [
        ("Cholesterol, Total",        "215",  "mg/dL",      "125-200",   "HIGH"),
        ("LDL Cholesterol (calc)",    "138",  "mg/dL",      "0-100",     "HIGH"),
        ("HDL Cholesterol",           "58",   "mg/dL",      ">=40",      ""),
        ("Triglycerides",             "112",  "mg/dL",      "0-150",     ""),
        ("Glucose, Fasting",          "94",   "mg/dL",      "70-100",    ""),
        ("Hemoglobin A1c",            "5.5",  "%",          "<5.7",      ""),
        ("TSH",                       "2.1",  "uIU/mL",     "0.45-4.5",  ""),
        ("Vitamin D, 25-Hydroxy",     "22",   "ng/mL",      "30-100",    "LOW"),
        ("Ferritin",                  "78",   "ng/mL",      "30-400",    ""),
        ("Creatinine",                "0.82", "mg/dL",      "0.60-1.30", ""),
        ("ALT (SGPT)",                "19",   "U/L",        "7-35",      ""),
        ("AST (SGOT)",                "21",   "U/L",        "10-40",     ""),
        ("WBC",                       "6.4",  "10^3/uL",    "4.0-11.0",  ""),
        ("Hemoglobin",                "13.1", "g/dL",       "12.0-17.5", ""),
        ("Platelets",                 "248",  "10^3/uL",    "150-400",   ""),
        ("hs-CRP",                    "1.8",  "mg/L",       "0-3.0",     ""),
    ],
    "2024-09-18": [
        ("CHOLESTEROL, TOTAL",        "198",  "mg/dL",      "125-200",   ""),
        ("LDL-C, CALCULATED",         "118",  "mg/dL",      "0-100",     "H"),
        ("HDL-C",                     "61",   "mg/dL",      ">=40",      ""),
        ("TRIGLYCERIDES",             "94",   "mg/dL",      "0-150",     ""),
        ("FASTING GLUCOSE",           "97",   "mg/dL",      "70-100",    ""),
        ("HEMOGLOBIN A1C",            "5.6",  "%",          "<5.7",      ""),
        ("TSH, 3RD GENERATION",       "1.9",  "uIU/mL",     "0.45-4.5",  ""),
        ("25-OH VITAMIN D",           "34",   "ng/mL",      "30-100",    ""),
        ("FERRITIN",                  "55",   "ng/mL",      "30-400",    ""),
        ("CREATININE, SERUM",         "0.85", "mg/dL",      "0.60-1.30", ""),
        ("ALT",                       "22",   "U/L",        "7-35",      ""),
        ("AST",                       "24",   "U/L",        "10-40",     ""),
        ("WBC COUNT",                 "5.9",  "10^3/uL",    "4.0-11.0",  ""),
        ("HEMOGLOBIN (HB)",           "13.4", "g/dL",       "12.0-17.5", ""),
        ("PLATELET COUNT",            "232",  "10^3/uL",    "150-400",   ""),
        ("C-REACTIVE PROTEIN, HS",    "1.2",  "mg/L",       "0-3.0",     ""),
        ("APOLIPOPROTEIN B",          "92",   "mg/dL",      "0-90",      "H"),
    ],
    "2025-04-22": [
        ("Total Cholesterol",         "182",  "mg/dL",      "125-200",   ""),
        ("LDL Cholesterol",           "104",  "mg/dL",      "0-100",     "H"),
        ("HDL Cholesterol",           "64",   "mg/dL",      ">=40",      ""),
        ("Triglycerides",             "82",   "mg/dL",      "0-150",     ""),
        ("Fasting Glucose",           "99",   "mg/dL",      "70-100",    ""),
        ("HbA1c",                     "5.7",  "%",          "<5.7",      "H"),  # tips into prediabetes
        ("Fasting Insulin",           "9.4",  "uIU/mL",     "2.6-24.9",  ""),
        ("TSH",                       "2.3",  "uIU/mL",     "0.45-4.5",  ""),
        ("Free T4",                   "1.2",  "ng/dL",      "0.8-1.8",   ""),
        ("Vitamin D",                 "46",   "ng/mL",      "30-100",    ""),
        ("Ferritin",                  "38",   "ng/mL",      "30-400",    ""),
        ("Creatinine",                "0.84", "mg/dL",      "0.60-1.30", ""),
        ("eGFR",                      "98",   "mL/min/1.73m2", ">=60",   ""),
        ("ALT",                       "18",   "U/L",        "7-35",      ""),
        ("AST",                       "20",   "U/L",        "10-40",     ""),
        ("WBC",                       "6.1",  "10^3/uL",    "4.0-11.0",  ""),
        ("Hemoglobin",                "13.6", "g/dL",       "12.0-17.5", ""),
        ("Platelets",                 "241",  "10^3/uL",    "150-400",   ""),
        ("hs-CRP",                    "0.9",  "mg/L",       "0-3.0",     ""),
        ("ApoB",                      "84",   "mg/dL",      "0-90",      ""),
        ("Lp(a)",                     "62",   "nmol/L",     "0-75",      ""),
        ("Homocysteine",              "8.1",  "umol/L",     "0-11.4",    ""),
    ],
}


# ── PDF rendering ────────────────────────────────────────────────────────

styles = getSampleStyleSheet()
H1 = ParagraphStyle("H1", parent=styles["Heading1"], fontSize=16, spaceAfter=6)
H2 = ParagraphStyle("H2", parent=styles["Heading2"], fontSize=11, spaceAfter=4, textColor=colors.HexColor("#444"))
BODY = ParagraphStyle("Body", parent=styles["BodyText"], fontSize=9, leading=12)
SMALL = ParagraphStyle("Small", parent=styles["BodyText"], fontSize=7.5, leading=10, textColor=colors.HexColor("#666"))


def _header_quest(date: str):
    return [
        Paragraph("<b>QUEST DIAGNOSTICS (FICTIONAL)</b>", H1),
        Paragraph("Synthetic data &mdash; for demo only &mdash; not from a real laboratory.", SMALL),
        Spacer(1, 6),
        Paragraph(f"<b>Patient:</b> {PATIENT['name']} &nbsp;&nbsp; <b>DOB:</b> {PATIENT['dob']} &nbsp;&nbsp; <b>Sex:</b> {PATIENT['sex']}", BODY),
        Paragraph(f"<b>Specimen ID:</b> SP-{date.replace('-', '')}-001 &nbsp;&nbsp; <b>MRN:</b> {PATIENT['mrn']}", BODY),
        Paragraph(f"<b>Collected:</b> {date} 07:42 &nbsp;&nbsp; <b>Reported:</b> {date} 16:10", BODY),
        Paragraph(f"<b>Ordering Provider:</b> {PATIENT['provider']}", BODY),
        Spacer(1, 10),
        Paragraph("<b>Test Results</b>", H2),
    ]


def _header_labcorp(date: str):
    return [
        Paragraph("<b>LABCORP &mdash; Patient Report (FICTIONAL)</b>", H1),
        Paragraph("Synthetic data &mdash; for demo only &mdash; not from a real laboratory.", SMALL),
        Spacer(1, 6),
        Paragraph(f"PATIENT NAME: {PATIENT['name']}", BODY),
        Paragraph(f"DOB: {PATIENT['dob']} &nbsp;&nbsp; AGE/SEX: 39/F &nbsp;&nbsp; PATIENT ID: {PATIENT['mrn']}", BODY),
        Paragraph(f"DATE COLLECTED: {date} &nbsp;&nbsp; DATE REPORTED: {date}", BODY),
        Paragraph(f"REQUESTING PHYSICIAN: {PATIENT['provider']}", BODY),
        Spacer(1, 10),
        Paragraph("<b>LABORATORY REPORT</b>", H2),
    ]


def _header_function(date: str):
    return [
        Paragraph("<b>Function Health &mdash; Member Lab Summary (FICTIONAL)</b>", H1),
        Paragraph("Synthetic data &mdash; for demo only &mdash; not from a real laboratory.", SMALL),
        Spacer(1, 6),
        Paragraph(f"Member: {PATIENT['name']}", BODY),
        Paragraph(f"Draw Date: {date}", BODY),
        Paragraph(f"Clinician of Record: {PATIENT['provider']}", BODY),
        Spacer(1, 10),
        Paragraph("<b>Your Results</b>", H2),
    ]


HEADERS = {
    "quest": _header_quest,
    "labcorp": _header_labcorp,
    "function": _header_function,
}


def build_pdf(path: Path, date: str, vendor: str, rows: list[tuple[str, str, str, str, str]]):
    doc = SimpleDocTemplate(
        str(path), pagesize=LETTER,
        leftMargin=0.6 * inch, rightMargin=0.6 * inch,
        topMargin=0.55 * inch, bottomMargin=0.55 * inch,
    )

    story: list = list(HEADERS[vendor](date))

    table_data = [["Test", "Result", "Units", "Reference Range", "Flag"]]
    for name, value, unit, ref, flag in rows:
        table_data.append([name, value, unit, ref, flag])

    table = Table(
        table_data,
        colWidths=[2.5 * inch, 0.9 * inch, 0.9 * inch, 1.6 * inch, 0.55 * inch],
    )
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eee")),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
        ("ALIGN", (1, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#bbb")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#fafafa")]),
        ("TEXTCOLOR", (4, 1), (4, -1), colors.HexColor("#a01010")),
        ("FONTNAME", (4, 1), (4, -1), "Helvetica-Bold"),
    ]))
    story.append(table)

    story.append(Spacer(1, 14))
    story.append(Paragraph(
        "<b>Disclaimer.</b> This document is a synthetic example produced for a software "
        "demonstration. It does not represent a real patient or a real laboratory report. "
        "No clinical decisions should be made from it.",
        SMALL,
    ))

    doc.build(story)


def write_csv(path: Path):
    """Bonus: a generic CSV export, mimicking what some patient portals offer."""
    with path.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["draw_date", "marker", "value", "unit", "reference_range", "flag"])
        for draw in DRAWS:
            for name, value, unit, ref, flag in RESULTS_BY_DATE[draw["date"]]:
                w.writerow([draw["date"], name, value, unit, ref, flag])


def main():
    for draw in DRAWS:
        out = OUT / draw["file"]
        build_pdf(out, draw["date"], draw["vendor"], RESULTS_BY_DATE[draw["date"]])
        print(f"wrote {out}")

    csv_dir = OUT.parent / "sample_csv"
    csv_dir.mkdir(exist_ok=True)
    csv_path = csv_dir / "example_portal_export.csv"
    write_csv(csv_path)
    print(f"wrote {csv_path}")


if __name__ == "__main__":
    main()
