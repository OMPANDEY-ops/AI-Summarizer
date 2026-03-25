import streamlit as st
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import PyPDF2
from docx import Document
import torch

# 1. Set up the web page with custom styling
st.set_page_config(page_title="AI Notes Summarizer", page_icon="📝", layout="wide", initial_sidebar_state="collapsed")

# Check if GPU is available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Custom CSS for ultra-creative aesthetic design
st.markdown("""
    <style>
        * {
            margin: 0;
            padding: 0;
        }
        
        .stApp {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
            min-height: 100vh;
        }
        
        .main {
            background: transparent;
        }
        
        /* Title styling with animation */
        @keyframes fadeInDown {
            from {
                opacity: 0;
                transform: translateY(-30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .title-container {
            text-align: center;
            padding: 40px 20px;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 30px;
            box-shadow: 0 20px 60px rgba(102, 126, 234, 0.3);
            margin: 20px auto;
            max-width: 800px;
            animation: fadeInDown 0.8s ease-out;
            border: 2px solid rgba(240, 147, 251, 0.3);
            backdrop-filter: blur(10px);
        }
        
        .title-container h1 {
            font-size: 3.5em;
            margin: 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-weight: 900;
            letter-spacing: -2px;
        }
        
        .title-container p {
            font-size: 1.3em;
            margin: 15px 0 0 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-weight: 600;
        }
        
        /* Input sections */
        @keyframes slideInUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .input-section {
            background: rgba(255, 255, 255, 0.92);
            padding: 30px;
            border-radius: 25px;
            box-shadow: 0 15px 50px rgba(102, 126, 234, 0.2);
            margin: 20px 0;
            animation: slideInUp 0.8s ease-out;
            border: 2px solid rgba(240, 147, 251, 0.2);
            backdrop-filter: blur(10px);
            transition: all 0.3s ease;
        }
        
        .input-section:hover {
            transform: translateY(-5px);
            box-shadow: 0 20px 60px rgba(102, 126, 234, 0.3);
            border-color: rgba(240, 147, 251, 0.5);
        }
        
        .input-section h3 {
            color: #667eea;
            margin-bottom: 15px;
            font-size: 1.3em;
        }
        
        /* Output section */
        .output-section {
            background: rgba(255, 255, 255, 0.95);
            padding: 30px;
            border-radius: 25px;
            box-shadow: 0 15px 50px rgba(240, 147, 251, 0.3);
            border-left: 6px solid;
            border-image: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%) 1;
            animation: slideInUp 0.9s ease-out;
            backdrop-filter: blur(10px);
        }
        
        /* Button styling */
        .stButton > button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px 50px;
            border-radius: 50px;
            border: none;
            font-weight: bold;
            font-size: 1.1em;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .stButton > button:hover {
            transform: scale(1.08);
            box-shadow: 0 12px 35px rgba(102, 126, 234, 0.5);
        }
        
        .stButton > button:active {
            transform: scale(0.95);
        }
        
        /* Text area styling */
        .stTextArea textarea {
            border-radius: 15px;
            border: 2px solid #667eea !important;
            background-color: #f8f9ff !important;
            font-family: 'Segoe UI', sans-serif;
        }
        
        .stTextArea textarea:focus {
            border-color: #764ba2 !important;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
        }
        
        /* File uploader styling */
        .stFileUploader {
            background: rgba(102, 126, 234, 0.05);
            border-radius: 15px;
            padding: 10px;
        }
        
        /* Progress bar */
        .stProgress > div > div > div {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
            border-radius: 10px;
        }
        
        /* Success/Error messages */
        .stSuccess, .stError, .stWarning, .stInfo {
            border-radius: 15px;
            padding: 15px;
            font-weight: 500;
        }
        
        .stSuccess {
            background-color: rgba(34, 197, 94, 0.1);
            border-left: 4px solid #22c55e;
        }
        
        .stError {
            background-color: rgba(239, 68, 68, 0.1);
            border-left: 4px solid #ef4444;
        }
        
        /* Footer */
        .footer {
            text-align: center;
            color: white;
            padding: 30px 20px;
            font-size: 0.9em;
            opacity: 0.9;
        }
    </style>
""", unsafe_allow_html=True)

# Title section with creative design
st.markdown("""
    <div class="title-container">
        <h1>✨ AI Notes Summarizer ✨</h1>
        <p>🚀 Transform chaos into clarity in seconds!</p>
    </div>
""", unsafe_allow_html=True)

# Load the ultra-fast model
@st.cache_resource
def load_summarizer():
    try:
        # Try to use the faster 3-3 model
        model_name = "sshleifer/distilbart-cnn-3-3"
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
        model.to(device)
        return model, tokenizer
    except:
        # Fallback to 6-6 if 3-3 fails
        model_name = "sshleifer/distilbart-cnn-6-6"
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
        model.to(device)
        return model, tokenizer

model, tokenizer = load_summarizer()

# Create two columns for better layout
col1, col2 = st.columns([1, 1], gap="medium")

with col1:
    st.markdown('<div class="input-section">', unsafe_allow_html=True)
    st.markdown("### 📝 Paste Your Notes")
    user_notes = st.text_area(
        "Your Notes:", 
        height=220, 
        placeholder="✍️ Paste your messy notes, thoughts, or ideas here...",
        label_visibility="collapsed"
    )
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="input-section">', unsafe_allow_html=True)
    st.markdown("### 📄 Upload Document")
    uploaded_file = st.file_uploader(
        "Upload PDF or Word document", 
        type=["pdf", "docx"],
        label_visibility="collapsed"
    )
    if uploaded_file:
        st.success(f"✅ {uploaded_file.name} ready!")
    st.markdown('</div>', unsafe_allow_html=True)

# Summarize button
st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
col_btn1, col_btn2, col_btn3 = st.columns([1, 1.2, 1])
with col_btn2:
    summarize_clicked = st.button("🚀 SUMMARIZE NOW", use_container_width=True, key="summarize_btn")

if summarize_clicked:
    if not user_notes and uploaded_file is None:
        st.error("❌ Please paste notes or upload a file!")
    else:
        try:
            # Extract text
            text_to_summarize = user_notes
            if uploaded_file is not None:
                if uploaded_file.type == "application/pdf":
                    reader = PyPDF2.PdfReader(uploaded_file)
                    for page in reader.pages:
                        extracted = page.extract_text()
                        if extracted:
                            text_to_summarize += " " + extracted
                elif "wordprocessingml" in uploaded_file.type:
                    doc = Document(uploaded_file)
                    text_to_summarize += " " + "\n".join([para.text for para in doc.paragraphs])
            
            # Progress tracking
            progress_placeholder = st.empty()
            status_placeholder = st.empty()
            
            with st.spinner("🔄 Working magic..."):
                # Stage 1: Analysis
                status_placeholder.markdown("#### ⚙️ Analyzing content...")
                progress_placeholder.progress(20)
                
                # Truncate to avoid token limit
                words = text_to_summarize.split()
                if len(words) > 500:
                    text_to_summarize = " ".join(words[:500])
                
                # Stage 2: Processing
                status_placeholder.markdown("#### 🧠 Generating summary...")
                progress_placeholder.progress(50)
                
                # Generate summary
                inputs = tokenizer.encode(text_to_summarize, return_tensors="pt", max_length=1024, truncation=True)
                inputs = inputs.to(device)
                
                summary_ids = model.generate(
                    inputs,
                    max_length=100,
                    min_length=30,
                    length_penalty=2.0,
                    num_beams=4,
                    early_stopping=True
                )
                
                summary_text = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
                
                # Stage 3: Formatting
                status_placeholder.markdown("#### ✨ Formatting...")
                progress_placeholder.progress(85)
                
                # Convert to bullet points
                sentences = summary_text.split('.')
                bullet_summary = "\n".join([f"• {s.strip()}" for s in sentences if s.strip()])
                
                progress_placeholder.progress(100)
                status_placeholder.markdown("#### ✅ Complete!")
            
            # Display result
            st.markdown('<div class="output-section">', unsafe_allow_html=True)
            st.markdown("### 🎯 Your Summary:")
            st.markdown(bullet_summary)
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.success("🎉 Summary generated in lightning speed!")
            
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

# Footer
st.markdown("""
    <div class="footer">
        <p>⚡ Powered by DistilBART (ultra-fast) | No API Key Required | Lightning Fast Processing</p>
        <p>💡 Pro Tip: Best results with 50-500 words. Longer texts use first 500 words.</p>
    </div>
""", unsafe_allow_html=True)
