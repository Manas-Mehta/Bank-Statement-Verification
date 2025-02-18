# FLOW for Overlap/hidden text analysis
    # 1. Check overlap and hidden text
    # 2. get text postiions from the pdf
    # 3. calculate overlapping text, return pairs of overlapping text
    # 4. Generate overlap/hidden text reports


import pdfplumber
from typing import List, Tuple, Dict
from dataclasses import dataclass

@dataclass
class TextBox:
    text: str
    x0: float  # left
    x1: float  # right
    y0: float  # top
    y1: float  # bottom
    page_number: int


# --------------------------------------------------------------
# 1. Check overlap and hidden text
# --------------------------------------------------------------

def check_overlap(box1: TextBox, box2: TextBox) -> bool:
   
    # Only check overlap if they're on the same page
    if box1.page_number != box2.page_number:
        return False
        
    # Check for no overlap conditions
    if (box1.x1 < box2.x0 or  # box1 is completely to the left
        box2.x1 < box1.x0 or  # box1 is completely to the right
        box1.y1 < box2.y0 or  # box1 is completely above
        box2.y1 < box1.y0):   # box1 is completely below
        return False
        
    return True


# --------------------------------------------------------------
# 2. get text postiions from the pdf
# --------------------------------------------------------------
def get_text_positions(pdf_path: str) -> List[TextBox]:
   
    text_boxes = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, 1):
            words = page.extract_words()
            
            for word in words:
                text_box = TextBox(
                    text=word['text'],
                    x0=word['x0'],
                    x1=word['x1'],
                    y0=word['top'],
                    y1=word['bottom'],
                    page_number=page_num
                )
                text_boxes.append(text_box)
    
    return text_boxes


# --------------------------------------------------------------
# 3. calculate overlapping text, return pairs of overlapping text
# --------------------------------------------------------------
def find_overlapping_text(pdf_path: str) -> List[Tuple[TextBox, TextBox]]:
    
    text_boxes = get_text_positions(pdf_path)
    overlapping_pairs = []
    
    # Compare each text box with every other text box
    for i, box1 in enumerate(text_boxes):
        for box2 in text_boxes[i + 1:]:  # Only check each pair once
            if check_overlap(box1, box2):
                overlapping_pairs.append((box1, box2))
    
    return overlapping_pairs


# --------------------------------------------------------------
# 4. Generate overlap/hidden text reports
# --------------------------------------------------------------
def generate_overlap_report(pdf_path: str) -> str:
    """
    Generate a human-readable report of overlapping text in the PDF.
    """
    overlapping_pairs = find_overlapping_text(pdf_path)
    
    if not overlapping_pairs:
        return "No overlapping text found in the document."
    
    report = f"**Found {len(overlapping_pairs)} instances of overlapping text:**\n\n"
    
    for box1, box2 in overlapping_pairs:
        report += f"Page `{box1.page_number}`:\n"
        report += f"- Text 1: `{box1.text}` at position (`{box1.x0:.2f}, {box1.y0:.2f}`)\n"
        report += f"- Text 2: `{box2.text}` at position (`{box2.x0:.2f}, {box2.y0:.2f}`)\n"
        report += "`" + "-" * 50 + "`\n\n"
    
    return report

if __name__ == "__main__":
    # Example usage
    #pdf_path = "data/YourBank.pdf"
    pdf_path = "data/ChaseBank_edited.pdf"

    #pdf_path = "overlapping_text_2.pdf"

    print(generate_overlap_report(pdf_path))