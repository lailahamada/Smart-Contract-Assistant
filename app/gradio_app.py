import gradio as gr
import requests

BASE_URL = "http://127.0.0.1:8000"

def upload_file(file):
    if file is None: return "Please upload a PDF file."
    with open(file.name, "rb") as f:
        files = {"file": (file.name, f, "application/pdf")}
        try:
            res = requests.post(f"{BASE_URL}/upload", files=files)
            if res.status_code == 200:
                return "✅ File uploaded and indexed successfully! You can now chat or summarize."
            return "❌ Upload failed."
        except Exception as e: return f"Error: {str(e)}"

def get_summary():
    try:
        res = requests.get(f"{BASE_URL}/summary")
        return res.json().get("summary", "Could not generate summary.")
    except Exception as e: return f"Error: {str(e)}"

def ask_assistant(message, history):
    payload = {"input": message}
    try:
        response = requests.post(f"{BASE_URL}/rag/invoke", json=payload)
        if response.status_code == 200:
            return response.json().get("output", "I couldn't find an answer in the contract.")
        return "Assistant unavailable."
    except Exception as e: return f"Error: {str(e)}"

# --- UI Theme ---
custom_theme = gr.themes.Soft(primary_hue="purple", neutral_hue="slate").set(
    body_background_fill="*neutral_950",
    block_background_fill="*neutral_900",
    button_primary_background_fill="*primary_600",
)

with gr.Blocks(title="Contract AI Assistant") as demo:
    gr.Markdown("# 📜 Smart Contract AI Assistant")

    # 1. قسم الرفع (أول حاجة)
    with gr.Row():
        with gr.Column():
            gr.Markdown("### 📂 1. Upload Document")
            file_input = gr.File(label="Upload Contract (PDF)")
            upload_status = gr.Markdown("") # لعرض حالة الرفع
            upload_btn = gr.Button("Process Document", variant="primary")

    gr.HTML("<hr style='border: 0.5px solid #444; margin: 20px 0;'>")

    # 2. قسم الشات (تاني حاجة)
    gr.Markdown("### 💬 2. Chat with Your Contract")
    chatbot = gr.ChatInterface(fn=ask_assistant)

    gr.HTML("<hr style='border: 0.5px solid #444; margin: 20px 0;'>")

    # 3. قسم التلخيص (آخر حاجة)
    with gr.Row():
        with gr.Column():
            gr.Markdown("### 📝 3. Executive Summary")
            summary_btn = gr.Button("Generate Full Summary", variant="secondary")
            summary_output = gr.Textbox(label="", lines=10, placeholder="Summary will appear here...")

    # ربط الأزرار بالوظائف
    upload_btn.click(fn=upload_file, inputs=file_input, outputs=upload_status)
    summary_btn.click(fn=get_summary, outputs=summary_output)

if __name__ == "__main__":
    demo.launch(server_port=7860, theme=custom_theme)