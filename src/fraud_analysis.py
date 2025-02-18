# This script is for the visual analysis 

import os
from google import genai
from pdf2image import convert_from_path
from src.overlap_detection import generate_overlap_report
from src.metadata_analysis import analyze_bank_statement

client_gemini = genai.Client()



# --------------------------------------------------------------
# 1. Visual Analysis
# --------------------------------------------------------------
# Function to convert PDF to image (for fraud analysis)
def convert_pdf_to_image(pdf_path: str):
    """Convert the first page of a PDF to an image."""
    images = convert_from_path(pdf_path, dpi=300)
    return images

def run_fraud_analysis_with_gemini(image) -> str:
    """Run specialized fraud analysis for bank statements using Gemini."""
    model = "gemini-2.0-flash"
    fraud_prompt = (
        "Analyze this bank statement for potential fraud or tampering. Examine the following aspects in detail:\n\n"
        
        "1. Visual Consistency:\n"
        "- Check for inconsistent fonts, sizes, or spacing within transaction entries\n"
        "- Look for misaligned columns or rows in transaction tables\n"
        "- Identify any breaks in table lines or borders\n"
        "- Detect variations in text opacity or quality\n"
        
        "2. Numerical Analysis:\n"
        "- Check if running balances correctly reflect transaction amounts\n"
        "- Look for unrealistic or suspiciously rounded transaction amounts\n"
        "- Verify that dates are in chronological order\n"
        "- Check for duplicate transaction entries\n"
        
        "3. Document Integrity:\n"
        "- Identify any signs of digital manipulation (blurring, pixelation, or artifacts)\n"
        "- Check for inconsistent backgrounds or color variations\n"
        "- Look for signs of cut-and-paste modifications\n"
        "- Verify that bank logos and branding elements appear authentic\n"
        
        "4. Layout Analysis:\n"
        "- Verify consistent spacing between transactions\n"
        "- Check header and footer alignment across pages\n"
        "- Look for unusual gaps or spacing in transaction lists\n"
        "- Verify that account information formatting is consistent\n"
        
        "5. Content Examination:\n"
        "- Check for unusual merchant names or descriptions\n"
        "- Look for inconsistent date formats\n"
        "- Verify that transaction codes follow expected patterns\n"
        "- Check for appropriate use of currency symbols and decimal places\n"
        
        "Provide a detailed report of any suspicious findings, organizing them by category. "
        "For each potential issue, specify its location in the document and explain why it raises concerns. "
        "If no signs of tampering are found in a category, explicitly state that."
    )
    
    response = client_gemini.models.generate_content(
        model=model, 
        contents=[fraud_prompt, image]
    )
    return response.text
