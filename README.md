# Document Analysis and Fraud Detection System for Bank-statement-verification
![image](https://github.com/user-attachments/assets/46721ed5-097b-405c-98fa-ca6b93956a88)

A comprehensive system for analyzing PDF documents (particularly bank statements) with features for fraud detection, text analysis, and interactive querying.

## Overview

This project implements a sophisticated document analysis pipeline that combines:
- RAG-based document querying
- Visual fraud detection
- Hidden text analysis
- Metadata analysis
- Interactive chat interface

## Features

### 1. Document Processing and Querying
- PDF text extraction and processing using Docling
- Hybrid chunking strategy for optimal text segmentation
- Vector embeddings stored in LanceDB
- RAG-based chatbot powered by GPT-4
- Interactive query interface using Gradio

### 2. Fraud Detection Suite

#### Visual Analysis
- PDF to image conversion
- Visual consistency checking using Gemini 2.0 Flash

  1. Visual Consistency:
        - Checks for inconsistent fonts, sizes, or spacing within transaction entries
        - Looks for misaligned columns or rows in transaction tables
        - Identifies any breaks in table lines or borders
        - Detects variations in text opacity or quality
        
  2. Numerical Analysis:
        - Checks if running balances correctly reflect transaction amounts
        - Looks for unrealistic or suspiciously rounded transaction amounts
        - Verifies that dates are in chronological order
        - Checks for duplicate transaction entries
        
  3. Document Integrity:
        - Identifies any signs of digital manipulation (blurring, pixelation, or artifacts)
        - Checks for inconsistent backgrounds or color variations
        - Looks for signs of cut-and-paste modifications
        - Verifies that bank logos and branding elements appear authentic
        
  4. Layout Analysis:
        - Verifies consistent spacing between transactions
        - Checks header and footer alignment across pages
        - Looks for unusual gaps or spacing in transaction lists
        - Verifies that account information formatting is consistent
        
  5. Content Examination:
        - Checks for unusual merchant names or descriptions
        - Looks for inconsistent date formats
        - Verifies that transaction codes follow expected patterns
        - Checks for appropriate use of currency symbols and decimal places
        

#### Hidden Text Analysis
- Detection of overlapping text elements
- Position-based text analysis
- Page-wise text overlap reporting

#### Metadata Analysis
- Placeholder detection
- Form field analysis
- Editing software signature detection
- Embedded link detection

## Technical Architecture

The system follows a modular pipeline architecture:

1. **Data Extraction & Embedding**
   - Extract data from PDF using Docling
   - Apply hybrid chunking
   - Create and store embeddings in LanceDB

2. **RAG Chatbot**
   - Context retrieval from database
   - Response generation using GPT-4
   - Interactive interface via Gradio

3. **Fraud Analysis**
   - Visual analysis using Gemini API
   - Hidden text detection
   - Metadata examination
   - Comprehensive report generation

## Setup

1. Install required dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
OPENAI_API_KEY=your_openai_api_key
GOOGLE_API_KEY=google_api_key

```

3. Create directory to store your pdf:
```bash
mkdir data/
```

## Usage

1. Run the main application:
```bash
python main.py
```

2. Enter the path to your PDF when prompted

3. Use the Gradio interface to:
   - Ask questions about the document
   - Run fraud analysis
   - View analysis reports

## Directory Structure

```
├── src/
│   ├── embeddings.py      # Document embedding and database operations
│   ├── chat.py            # RAG chatbot implementation
│   ├── fraud_analysis.py  # Visual fraud detection
│   ├── metadata_analysis.py # Metadata and placeholder detection
│   ├── overlap_detection.py # Hidden text analysis
│   └── utils/             # Utility functions
├── data/
│   └── lancedb/          # Vector database storage
└── main.py               # Application entry point
```

## Dependencies

- OpenAI GPT-4
- Google Gemini 2.0 Flash
- LanceDB
- Docling
- PDFPlumber
- PyPDF2
- Gradio
- pdf2image

## API Requirements

- OpenAI API key (for GPT-4)
- Google Cloud API key (for Gemini)

## Notes

- The system is optimized for bank statement analysis but can be adapted for other document types
- Fraud detection combines multiple analysis methods for comprehensive verification
- The chatbot uses a RAG approach to ensure responses are grounded in document content

