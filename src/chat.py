# FLOW of this script

# RAG-Based Chatbot
    # 1. Initialize the database
    # 2. Retrieve information from the database
    # 3. Generate Response

# Run Fraud Analysis
    # 4.  Run visual Analysis through gemini
    # 5. Run Hidden text analysis and Metadata Analysis, create a final report



import gradio as gr
import lancedb
from openai import OpenAI
from dotenv import load_dotenv
import os
from google import genai
from pdf2image import convert_from_path
import numpy as np
import pandas as pd
from src.overlap_detection import generate_overlap_report
from src.fraud_analysis import convert_pdf_to_image, run_fraud_analysis_with_gemini
from src.metadata_analysis import analyze_bank_statement


# Load openAI and Gemini API keys
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=openai_api_key)
client_gemini = genai.Client()



# --------------------------------------------------------------
# 1. Initialize the database
# --------------------------------------------------------------
def init_db():
    db = lancedb.connect("data/lancedb")
    return db.open_table("docling")


# --------------------------------------------------------------
# 2. Retrieve information from the database
# --------------------------------------------------------------

def get_context(query: str, table, num_results: int = 3) -> str:
    results = table.search(query).limit(num_results).to_pandas()
    contexts = []
    for _, row in results.iterrows():
        filename = row["metadata"].get("filename")
        page_numbers = row["metadata"].get("page_numbers")
        title = row["metadata"].get("title")
        
        source_parts = []
        if filename:
            source_parts.append(filename)
        if isinstance(page_numbers, (list, np.ndarray, pd.Series)) and any(page_numbers):
            source_parts.append(f"p. {', '.join(str(p) for p in page_numbers)}")
        
        source = f"\nSource: {' - '.join(source_parts)}" if source_parts else ""
        if title:
            source += f"\nTitle: {title}"
        
        contexts.append(f"{row['text']}{source}")
    
    return "\n\n".join(contexts)



# --------------------------------------------------------------
# 3. Generate Response
# --------------------------------------------------------------
def get_chat_response(messages, context: str) -> str:
    """Get a response from OpenAI based on the conversation and provided context."""
    system_prompt = f"""You are a helpful assistant that answers questions based on the provided context.
Use only the information from the context to answer questions. If you're unsure or the context
doesn't contain the relevant information, say so.

Context:
{context}
"""
    messages_with_context = [{"role": "system", "content": system_prompt}, *messages]
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages_with_context,
        temperature=0.7,
        stream=False,
    )
    return response.choices[0].message.content

#  This function manages the flow of the chatbot

def process_message(user_input, chat_history, conversation):
    """Process user messages and generate responses."""
    table = init_db()  # Get fresh table connection
    conversation.append({"role": "user", "content": user_input})
    context = get_context(user_input, table)
    assistant_response = get_chat_response(conversation, context)
    conversation.append({"role": "assistant", "content": assistant_response})
    chat_history.append((user_input, assistant_response))
    return chat_history, chat_history, conversation



# --------------------------------------------------------------
# 4.  Run visual Analysis through gemini
# --------------------------------------------------------------
def run_fraud_analysis(chat_history, conversation, pdf_path):
    """Run fraud analysis with the provided PDF path."""
    final_report = run_full_fraud_analysis(pdf_path)
    conversation.append({"role": "assistant", "content": final_report})
    chat_history.append(("Fraud Analysis, Overlap & Hidden Text Detection", final_report))
    return chat_history, chat_history, conversation



# --------------------------------------------------------------
# 5. Run Hidden text analysis and Metadata Analysis, create a final report
# --------------------------------------------------------------
def run_full_fraud_analysis(pdf_path: str):
    """Run full fraud analysis including image conversion, Gemini analysis, and overlap detection."""
    images = convert_pdf_to_image(pdf_path)
    image = images[0] if images else None
    
    fraud_analysis_result = run_fraud_analysis_with_gemini(image)
    overlap_report = generate_overlap_report(pdf_path)
    metadata_report = analyze_bank_statement(pdf_path)

    
     # Combine all reports into a final report
    final_report = (
    "# 1. Fraud Analysis Result:\n" 
    f"{fraud_analysis_result}\n\n"
    "-------------------------------------\n"
    "# 2. Overlapping Text Analysis Report:\n" 
    f"{overlap_report}\n\n"
    "# 3. Metadata Analysis Report:\n" 
    f"{metadata_report}\n\n"

   
    )
    
    return final_report