# main.py
from src.embeddings import extract_and_process_pdf
from src.chat import init_db, get_context, get_chat_response, convert_from_path, process_message, run_fraud_analysis
import os
import gradio as gr

def main(pdf_path):
    # -----------------------------
    # extract text and create embeddings
    # -----------------------------
    extract_and_process_pdf(pdf_path)
    
    # -----------------------------
    # Gradio Interface
    # -----------------------------
    # todo: make the interface full screen 
    with gr.Blocks() as demo:
        
        gr.Markdown("## Arva AI MVP demo")
        
        chatbot = gr.Chatbot()
        state_chat_history = gr.State([])
        state_conversation = gr.State([])
        state_pdf_path = gr.State(pdf_path)  # Store PDF path in state
        
        with gr.Row():
            txt = gr.Textbox(show_label=False, placeholder="Ask a question about the document")
            fraud_button = gr.Button("Run Fraud Analysis")
        
        txt.submit(
            fn=process_message,
            inputs=[txt, state_chat_history, state_conversation],
            outputs=[chatbot, state_chat_history, state_conversation],
        )
        
        fraud_button.click(
            fn=lambda history, conv, path: run_fraud_analysis(history, conv, path),
            inputs=[state_chat_history, state_conversation, state_pdf_path],
            outputs=[chatbot, state_chat_history, state_conversation],
        )

    demo.launch()

if __name__ == "__main__":
    pdf_path = input("Enter the path to your PDF: ")
    if os.path.exists(pdf_path):
        main(pdf_path)
    else:
        print("The provided PDF path does not exist.")