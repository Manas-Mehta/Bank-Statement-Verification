# FLOW for Metadata analysis
    # 1. detect placeholders
    # 2. Detect form fields
    # 3. Detect editing softare signatures and links, generate final report



import re
from pdfminer.high_level import extract_text
import pdfplumber
import PyPDF2


# --------------------------------------------------------------
# 1. detect placeholders
# --------------------------------------------------------------

def detect_placeholders(pdf_path):
   
    text = extract_text(pdf_path)
    
    # Common placeholder patterns (case insensitive)
    placeholder_patterns = [
        r"\{.*?\}",            # e.g. {Name}, {Date}
        r"<.*?>",              # e.g. <Insert Amount>
        r"_{4,}",              # e.g. __________ (four or more underscores)
        r"\[\[.*?\]\]",        # e.g. [[Placeholder]]
        r"\bTBD\b",            # TBD (to be determined)
        r"\bN/?A\b",           # N/A or NA
        r"\bNot Available\b",  # Not Available
        r"\bSAMPLE\b",         # SAMPLE
        r"\bDUMMY\b",          # DUMMY
        r"\bTEST\b",           # TEST
        r"\bX{4,}\b"           # 4 or more consecutive X's
    ]
    
    found_placeholders = []
    for pattern in placeholder_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            found_placeholders.extend(matches)
    
    return found_placeholders


# --------------------------------------------------------------
# 2. Detect form fields
# --------------------------------------------------------------

def detect_empty_form_fields(pdf_path):
    """
    Detects empty fillable form fields (if any) in a PDF.
    Bank statements rarely use interactive fields,
    but this is here just in case.
    """
    empty_fields = []
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages):
            annotations = page.annots or []
            for field in annotations:
                # pdfplumber annotations may store field info under 'field'
                field_info = field.get("field", {})
                field_name = field_info.get("T")
                field_value = field_info.get("V")
                if field_value in [None, "", " "]:
                    empty_fields.append(f"Page {page_num+1}: {field_name}")
    
    return empty_fields


# --------------------------------------------------------------
# 3. Detect editing softare signatures and links, generate final report
# --------------------------------------------------------------
def analyze_bank_statement(pdf_path):
    """
    Run all checks on the bank statement PDF, including placeholder detection,
    empty form field detection, traces of editing software, and embedded links.
    """
    report = f"Analyzing bank statement: {pdf_path}\n"
    
    # Check for placeholder/dummy text
    placeholders = detect_placeholders(pdf_path)
    if placeholders:
        report += f"📌 Found {len(placeholders)} placeholder tokens: {placeholders}\n"
    else:
        report += "✅ No obvious placeholders detected.\n"
    
    # Check for empty form fields (if applicable)
    empty_fields = detect_empty_form_fields(pdf_path)
    if empty_fields:
        report += f"📌 Found {len(empty_fields)} empty form fields: {empty_fields}\n"
    else:
        report += "✅ No empty form fields detected.\n"
    
    # Detect editing software traces from metadata
    editing_software_signatures = [
        'Adobe Photoshop',
        'Adobe Acrobat',
        'Foxit',
        'Nitro',
        'InDesign',
        'Microsoft Word',
        # Add other common software signatures here
    ]
    
    with open(pdf_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        metadata = reader.metadata

    # Add metadata to the report
    report += f"\n📋 PDF Metadata:\n"
    for key, value in metadata.items():
        report += f"{key}: {value}\n"

    # check for editing softwares used    
    software_used = []
    for software in editing_software_signatures:
        if metadata.get("/Producer") and re.search(software, metadata.get("/Producer"), re.IGNORECASE):
            software_used.append(software)
    
    if software_used:
        report += f"📌 Detected editing software: {', '.join(software_used)}\n"
    else:
        report += "✅ No editing software traces detected.\n"
    
    # Check for embedded links in the document
    with pdfplumber.open(pdf_path) as pdf:
        links = []
        for page_number in range(len(pdf.pages)):
            page = pdf.pages[page_number]
            links.extend(page.hyperlinks)
        if links:
            report += f"📌 Found {len(links)} embedded links: {links}\n"
        else:
            report += "✅ No embedded links found.\n"
    
    return report
