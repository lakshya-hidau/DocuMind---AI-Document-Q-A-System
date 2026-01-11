import streamlit as st
import faiss
import os
from dotenv import load_dotenv
from io import BytesIO
from docx import Document
import numpy as np
import time

from langchain_community.document_loaders import WebBaseLoader
from PyPDF2 import PdfReader
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.docstore.in_memory import InMemoryDocstore

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough

from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace

load_dotenv()
HUGGINGFACE_API_TOKEN = os.getenv("HUGGINGFACE_API_TOKEN")


# -------------------- INDEXING --------------------
def process_input(input_type, input_data):
    """Process various input types and create vector embeddings"""
    if input_type == "Website URL":
        loader = WebBaseLoader(input_data)
        documents = loader.load()
        texts = [doc.page_content for doc in documents]

    elif input_type == "PDF File":
        reader = PdfReader(input_data)
        texts = [page.extract_text() for page in reader.pages]

    elif input_type == "Word Document":
        doc = Document(input_data)
        texts = [p.text for p in doc.paragraphs]

    elif input_type == "Text File":
        texts = [input_data.read().decode("utf-8")]

    elif input_type == "Direct Text":
        texts = [input_data]

    else:
        raise ValueError("Unsupported input type")

    splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = splitter.split_text("\n".join(texts))

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-mpnet-base-v2"
    )

    dim = len(embeddings.embed_query("test"))
    index = faiss.IndexFlatL2(dim)

    vectorstore = FAISS(
        embedding_function=embeddings.embed_query,
        index=index,
        docstore=InMemoryDocstore(),
        index_to_docstore_id={}
    )

    vectorstore.add_texts(chunks)
    return vectorstore, len(chunks), chunks


# -------------------- RAG QA --------------------
def answer_question(vectorstore, query):
    """Generate answer using RAG pipeline"""
    llm_endpoint = HuggingFaceEndpoint(
        repo_id="meta-llama/Meta-Llama-3-8B-Instruct",
        provider="novita",
        temperature=0.6,
        huggingfacehub_api_token=HUGGINGFACE_API_TOKEN,
    )

    llm = ChatHuggingFace(llm=llm_endpoint)

    prompt = ChatPromptTemplate.from_template(
        """Answer using the context below.
If you don't know, say you don't know.

Context:
{context}

Question:
{question}"""
    )

    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    
    # Get relevant documents
    docs = retriever.get_relevant_documents(query)

    chain = (
        {
            "context": retriever,
            "question": RunnablePassthrough(),
        }
        | prompt
        | llm
    )

    answer = chain.invoke(query).content
    return answer, docs


# -------------------- CUSTOM CSS --------------------
def inject_custom_css():
    """Inject custom CSS for premium UI styling"""
    st.markdown("""
    <style>
    /* Import Google Fonts - Distinctive typography */
    @import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
    
    /* Root variables for consistent theming */
    :root {
        --bg-primary: #0a0a0f;
        --bg-secondary: #151520;
        --bg-tertiary: #1a1a2e;
        --accent-primary: #00d4ff;
        --accent-secondary: #6366f1;
        --accent-glow: rgba(0, 212, 255, 0.3);
        --text-primary: #ffffff;
        --text-secondary: #a1a1aa;
        --text-muted: #71717a;
        --border-color: rgba(255, 255, 255, 0.1);
        --glass-bg: rgba(26, 26, 46, 0.6);
        --success: #10b981;
        --warning: #f59e0b;
        --error: #ef4444;
    }
    
    /* Global resets and base styles */
    * {
        font-family: 'Sora', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Main app container */
    .stApp {
        background: linear-gradient(135deg, #0a0a0f 0%, #151520 50%, #1a1a2e 100%);
        background-attachment: fixed;
    }
    
    /* Animated background effect */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: 
            radial-gradient(circle at 20% 50%, rgba(99, 102, 241, 0.1) 0%, transparent 50%),
            radial-gradient(circle at 80% 80%, rgba(0, 212, 255, 0.1) 0%, transparent 50%);
        pointer-events: none;
        z-index: 0;
    }
    
    /* Sidebar styling - glassmorphism */
    [data-testid="stSidebar"] {
        background: var(--glass-bg);
        backdrop-filter: blur(20px) saturate(180%);
        border-right: 1px solid var(--border-color);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
    }
    
    [data-testid="stSidebar"] > div:first-child {
        padding: 2rem 1.5rem;
    }
    
    /* Main content area */
    .main .block-container {
        padding: 2rem 3rem;
        max-width: 100%;
    }
    
    /* Logo/Header styling */
    .app-logo {
        font-family: 'Sora', sans-serif;
        font-size: 1.8rem;
        font-weight: 700;
        background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5rem;
        letter-spacing: -0.02em;
    }
    
    .app-tagline {
        color: var(--text-secondary);
        font-size: 0.875rem;
        margin-bottom: 2rem;
        font-weight: 300;
    }
    
    /* Status indicator */
    .status-indicator {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.75rem 1rem;
        background: var(--bg-tertiary);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        margin: 1.5rem 0;
        font-size: 0.875rem;
    }
    
    .status-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: var(--success);
        box-shadow: 0 0 10px var(--success);
        animation: pulse 2s ease-in-out infinite;
    }
    
    .status-dot.inactive {
        background: var(--text-muted);
        box-shadow: none;
        animation: none;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    /* Glass card component */
    .glass-card {
        background: var(--glass-bg);
        backdrop-filter: blur(20px) saturate(180%);
        border: 1px solid var(--border-color);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .glass-card:hover {
        border-color: rgba(255, 255, 255, 0.2);
        box-shadow: 0 12px 48px rgba(0, 0, 0, 0.4);
        transform: translateY(-2px);
    }
    
    /* Chat message styling */
    .chat-message {
        display: flex;
        gap: 1rem;
        margin-bottom: 1.5rem;
        animation: fadeInUp 0.5s ease-out;
    }
    
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .message-avatar {
        width: 40px;
        height: 40px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
        font-size: 1.2rem;
        font-weight: 600;
    }
    
    .user-avatar {
        background: linear-gradient(135deg, var(--accent-secondary), var(--accent-primary));
        box-shadow: 0 4px 12px var(--accent-glow);
    }
    
    .assistant-avatar {
        background: var(--bg-tertiary);
        border: 1px solid var(--border-color);
    }
    
    .message-content {
        flex: 1;
        background: var(--glass-bg);
        backdrop-filter: blur(20px);
        border: 1px solid var(--border-color);
        border-radius: 16px;
        padding: 1.25rem;
        color: var(--text-primary);
        line-height: 1.7;
    }
    
    .user-message .message-content {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.2), rgba(0, 212, 255, 0.2));
        border-color: rgba(99, 102, 241, 0.3);
    }
    
    .message-meta {
        font-size: 0.75rem;
        color: var(--text-muted);
        margin-top: 0.5rem;
        font-family: 'JetBrains Mono', monospace;
    }
    
    /* Source card styling */
    .source-card {
        background: var(--bg-tertiary);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 1rem;
        transition: all 0.3s ease;
    }
    
    .source-card:hover {
        border-color: var(--accent-primary);
        box-shadow: 0 0 20px rgba(0, 212, 255, 0.2);
    }
    
    .source-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 0.75rem;
    }
    
    .source-title {
        font-weight: 600;
        color: var(--text-primary);
        font-size: 0.875rem;
    }
    
    .source-score {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
        color: var(--accent-primary);
        padding: 0.25rem 0.5rem;
        background: rgba(0, 212, 255, 0.1);
        border-radius: 6px;
    }
    
    .source-content {
        color: var(--text-secondary);
        font-size: 0.875rem;
        line-height: 1.6;
        max-height: 100px;
        overflow: hidden;
        position: relative;
    }
    
    .source-content::after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 0;
        width: 100%;
        height: 30px;
        background: linear-gradient(transparent, var(--bg-tertiary));
    }
    
    /* Button styling */
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, var(--accent-secondary), var(--accent-primary));
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.875rem 1.5rem;
        font-weight: 600;
        font-size: 0.95rem;
        letter-spacing: 0.01em;
        cursor: pointer;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 12px var(--accent-glow);
        position: relative;
        overflow: hidden;
    }
    
    .stButton > button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
        transition: left 0.5s;
    }
    
    .stButton > button:hover::before {
        left: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px var(--accent-glow);
    }
    
    .stButton > button:active {
        transform: translateY(0);
    }
    
    /* Secondary button (Reset) */
    .stButton > button[kind="secondary"] {
        background: var(--bg-tertiary);
        border: 1px solid var(--border-color);
        box-shadow: none;
    }
    
    .stButton > button[kind="secondary"]:hover {
        background: var(--bg-secondary);
        border-color: var(--accent-primary);
    }
    
    /* Input styling */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background: var(--bg-tertiary);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        color: var(--text-primary);
        padding: 0.875rem 1rem;
        font-size: 0.95rem;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: var(--accent-primary);
        box-shadow: 0 0 0 3px var(--accent-glow);
        outline: none;
    }
    
    /* File uploader */
    [data-testid="stFileUploader"] {
        background: var(--bg-tertiary);
        border: 2px dashed var(--border-color);
        border-radius: 12px;
        padding: 2rem;
        transition: all 0.3s ease;
    }
    
    [data-testid="stFileUploader"]:hover {
        border-color: var(--accent-primary);
        background: rgba(0, 212, 255, 0.05);
    }
    
    /* Select box */
    .stSelectbox > div > div {
        background: var(--bg-tertiary);
        border: 1px solid var(--border-color);
        border-radius: 12px;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: var(--bg-tertiary);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        color: var(--text-primary);
        font-weight: 600;
    }
    
    .streamlit-expanderHeader:hover {
        border-color: var(--accent-primary);
    }
    
    /* Progress bar */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, var(--accent-secondary), var(--accent-primary));
        border-radius: 10px;
    }
    
    /* Metrics */
    .metric-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin: 1.5rem 0;
    }
    
    .metric-card {
        background: var(--glass-bg);
        backdrop-filter: blur(20px);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 1.25rem;
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 32px rgba(0, 0, 0, 0.3);
    }
    
    .metric-label {
        font-size: 0.75rem;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.5rem;
        font-weight: 500;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    /* Section headers */
    .section-header {
        font-size: 1.25rem;
        font-weight: 600;
        color: var(--text-primary);
        margin: 2rem 0 1rem 0;
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    
    .section-header::before {
        content: '';
        width: 4px;
        height: 24px;
        background: linear-gradient(180deg, var(--accent-primary), var(--accent-secondary));
        border-radius: 2px;
    }
    
    /* Typing indicator */
    .typing-indicator {
        display: flex;
        gap: 0.5rem;
        padding: 1rem;
    }
    
    .typing-dot {
        width: 8px;
        height: 8px;
        background: var(--accent-primary);
        border-radius: 50%;
        animation: typing 1.4s infinite;
    }
    
    .typing-dot:nth-child(2) {
        animation-delay: 0.2s;
    }
    
    .typing-dot:nth-child(3) {
        animation-delay: 0.4s;
    }
    
    @keyframes typing {
        0%, 60%, 100% {
            transform: translateY(0);
            opacity: 0.7;
        }
        30% {
            transform: translateY(-10px);
            opacity: 1;
        }
    }
    
    /* Footer */
    .custom-footer {
        text-align: center;
        padding: 2rem;
        color: var(--text-muted);
        font-size: 0.875rem;
        border-top: 1px solid var(--border-color);
        margin-top: 4rem;
    }
    
    .custom-footer a {
        color: var(--accent-primary);
        text-decoration: none;
        transition: color 0.3s ease;
    }
    
    .custom-footer a:hover {
        color: var(--accent-secondary);
    }
    
    /* Badge */
    .badge {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 1rem;
        background: rgba(0, 212, 255, 0.1);
        border: 1px solid rgba(0, 212, 255, 0.3);
        border-radius: 20px;
        font-size: 0.75rem;
        color: var(--accent-primary);
        font-weight: 500;
        font-family: 'JetBrains Mono', monospace;
    }
    
    /* Toast notification */
    .stToast {
        background: var(--glass-bg);
        backdrop-filter: blur(20px);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        color: var(--text-primary);
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--bg-secondary);
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--accent-primary);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--accent-secondary);
    }
    
    /* Label styling */
    .stTextInput label, .stTextArea label, .stSelectbox label {
        color: var(--text-secondary);
        font-size: 0.875rem;
        font-weight: 500;
        margin-bottom: 0.5rem;
    }
    
    /* Divider */
    hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, var(--border-color), transparent);
        margin: 2rem 0;
    }
    
    /* Loading animation */
    @keyframes shimmer {
        0% {
            background-position: -1000px 0;
        }
        100% {
            background-position: 1000px 0;
        }
    }
    
    .loading-shimmer {
        background: linear-gradient(90deg, var(--bg-tertiary) 0%, var(--bg-secondary) 50%, var(--bg-tertiary) 100%);
        background-size: 1000px 100%;
        animation: shimmer 2s infinite;
    }
    </style>
    """, unsafe_allow_html=True)


# -------------------- UI COMPONENTS --------------------
def render_sidebar():
    """Render the sidebar with logo, file uploader, and controls"""
    with st.sidebar:
        # Logo and branding
        st.markdown('<div class="app-logo">⚡ NeuralRAG</div>', unsafe_allow_html=True)
        st.markdown('<div class="app-tagline">AI-Powered Knowledge Assistant</div>', unsafe_allow_html=True)
        
        # Status indicator
        status = "active" if "vectorstore" in st.session_state else "inactive"
        status_text = "Knowledge Base Active" if status == "active" else "No Knowledge Base"
        status_class = "" if status == "active" else "inactive"
        
        st.markdown(f"""
        <div class="status-indicator">
            <div class="status-dot {status_class}"></div>
            <span>{status_text}</span>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # File uploader section
        st.markdown("### 📁 Upload Knowledge")
        
        input_type = st.selectbox(
            "Input Type",
            ["PDF File", "Word Document", "Text File", "Website URL", "Direct Text"],
            label_visibility="collapsed"
        )
        
        input_data = None
        
        if input_type == "Website URL":
            url = st.text_input("Enter URL", placeholder="https://example.com")
            input_data = url if url else None
            
        elif input_type == "Direct Text":
            input_data = st.text_area("Enter text", placeholder="Paste your text here...", height=150)
            
        else:
            uploaded_file = st.file_uploader(
                "Choose a file",
                type=["pdf", "docx", "txt"],
                label_visibility="collapsed"
            )
            input_data = uploaded_file
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Process button
        if st.button("🚀 Process Knowledge", type="primary"):
            if not input_data:
                st.error("Please provide input data first")
            else:
                with st.spinner("Processing..."):
                    progress_bar = st.progress(0)
                    for i in range(100):
                        time.sleep(0.01)
                        progress_bar.progress(i + 1)
                    
                    try:
                        vectorstore, chunks_count, chunks = process_input(input_type, input_data)
                        st.session_state.vectorstore = vectorstore
                        st.session_state.chunks_count = chunks_count
                        st.session_state.chunks = chunks
                        st.session_state.filename = uploaded_file.name if uploaded_file else "URL/Text"
                        st.success(f"✅ Processed {chunks_count} chunks")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
        
        st.markdown("---")
        
        # Model selector
        st.markdown("### 🤖 Model Settings")
        model = st.selectbox(
            "Select Model",
            ["meta-llama/Meta-Llama-3-8B-Instruct"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        # Metrics
        if "vectorstore" in st.session_state:
            st.markdown("### 📊 Statistics")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Chunks", st.session_state.chunks_count)
            with col2:
                chat_count = len(st.session_state.get('chat_history', []))
                st.metric("Queries", chat_count)
        
        st.markdown("---")
        
        # Reset button at bottom
        if st.button("🗑️ Reset Knowledge Base", type="secondary"):
            if 'vectorstore' in st.session_state:
                del st.session_state.vectorstore
            if 'chunks_count' in st.session_state:
                del st.session_state.chunks_count
            if 'chunks' in st.session_state:
                del st.session_state.chunks
            if 'chat_history' in st.session_state:
                st.session_state.chat_history = []
            st.rerun()
        
        # Version badge
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown('<div class="badge">v1.0.0 Beta</div>', unsafe_allow_html=True)


def render_chat_message(role, content, timestamp=None):
    """Render a chat message with avatar and styling"""
    avatar = "👤" if role == "user" else "🤖"
    avatar_class = "user-avatar" if role == "user" else "assistant-avatar"
    message_class = "user-message" if role == "user" else "assistant-message"
    
    st.markdown(f"""
    <div class="chat-message {message_class}">
        <div class="message-avatar {avatar_class}">{avatar}</div>
        <div>
            <div class="message-content">{content}</div>
            {f'<div class="message-meta">{timestamp}</div>' if timestamp else ''}
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_source_card(source, index, score=None):
    """Render a source document card"""
    preview = source[:200] + "..." if len(source) > 200 else source
    score_text = f"Relevance: {score:.2f}" if score else f"Source {index + 1}"
    
    st.markdown(f"""
    <div class="source-card">
        <div class="source-header">
            <div class="source-title">📄 Chunk {index + 1}</div>
            <div class="source-score">{score_text}</div>
        </div>
        <div class="source-content">{preview}</div>
    </div>
    """, unsafe_allow_html=True)


def render_typing_indicator():
    """Render animated typing indicator"""
    st.markdown("""
    <div class="typing-indicator">
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
    </div>
    """, unsafe_allow_html=True)


# -------------------- MAIN APP --------------------
def main():
    # Page config
    st.set_page_config(
        page_title="NeuralRAG - AI Knowledge Assistant",
        page_icon="⚡",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Inject custom CSS
    inject_custom_css()
    
    # Initialize session state
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'show_sources' not in st.session_state:
        st.session_state.show_sources = True
    
    # Render sidebar
    render_sidebar()
    
    # Main content area
    if "vectorstore" in st.session_state:
        # Two column layout
        col1, col2 = st.columns([1.5, 1])
        
        with col1:
            st.markdown('<div class="section-header">💬 Chat Interface</div>', unsafe_allow_html=True)
            
            # Chat history
            chat_container = st.container()
            with chat_container:
                if len(st.session_state.chat_history) == 0:
                    st.markdown("""
                    <div class="glass-card" style="text-align: center; padding: 3rem;">
                        <h3 style="color: var(--text-primary); margin-bottom: 1rem;">
                            👋 Welcome to NeuralRAG
                        </h3>
                        <p style="color: var(--text-secondary); margin-bottom: 0;">
                            Your knowledge base is ready. Ask me anything about your uploaded documents.
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    for chat in st.session_state.chat_history:
                        render_chat_message("user", chat['question'])
                        render_chat_message("assistant", chat['answer'])
            
            # Input area fixed at bottom
            st.markdown("<br>", unsafe_allow_html=True)
            query = st.text_input(
                "Ask a question",
                placeholder="Type your question here...",
                key="query_input",
                label_visibility="collapsed"
            )
            
            col_btn1, col_btn2 = st.columns([4, 1])
            with col_btn1:
                ask_button = st.button("🔍 Ask Question", type="primary", use_container_width=True)
            with col_btn2:
                if st.button("🗑️", use_container_width=True):
                    st.session_state.chat_history = []
                    st.rerun()
            
            if ask_button and query:
                with st.spinner(""):
                    render_typing_indicator()
                    try:
                        answer, docs = answer_question(st.session_state.vectorstore, query)
                        st.session_state.chat_history.append({
                            "question": query,
                            "answer": answer,
                            "sources": docs
                        })
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
        
        with col2:
            st.markdown('<div class="section-header">📚 Context Sources</div>', unsafe_allow_html=True)
            
            # Toggle sources
            st.session_state.show_sources = st.checkbox("Show retrieved sources", value=True)
            
            if st.session_state.show_sources and len(st.session_state.chat_history) > 0:
                latest_chat = st.session_state.chat_history[-1]
                if 'sources' in latest_chat:
                    st.markdown(f"""
                    <div class="glass-card">
                        <p style="color: var(--text-secondary); font-size: 0.875rem; margin-bottom: 1rem;">
                            Retrieved {len(latest_chat['sources'])} relevant chunks for your query
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    for idx, doc in enumerate(latest_chat['sources']):
                        render_source_card(doc.page_content, idx)
            else:
                st.markdown("""
                <div class="glass-card" style="text-align: center; padding: 2rem;">
                    <p style="color: var(--text-muted);">
                        No sources to display yet.<br>Ask a question to see relevant context.
                    </p>
                </div>
                """, unsafe_allow_html=True)
    
    else:
        # Welcome screen
        st.markdown("""
        <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 60vh; text-align: center;">
            <div style="font-size: 5rem; margin-bottom: 2rem;">⚡</div>
            <h1 style="font-size: 3rem; font-weight: 700; margin-bottom: 1rem; background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary)); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                Welcome to NeuralRAG
            </h1>
            <p style="font-size: 1.25rem; color: var(--text-secondary); max-width: 600px; margin-bottom: 3rem;">
                Upload your documents and start asking questions powered by advanced AI retrieval and generation.
            </p>
            <div class="glass-card" style="max-width: 800px; text-align: left;">
                <h3 style="color: var(--text-primary); margin-bottom: 1.5rem;">🚀 Getting Started</h3>
                <ol style="color: var(--text-secondary); line-height: 2;">
                    <li>Upload a PDF, Word document, or text file using the sidebar</li>
                    <li>Click "Process Knowledge" to build your vector database</li>
                    <li>Start asking questions about your documents</li>
                    <li>View relevant sources in the context panel</li>
                </ol>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Footer
    st.markdown("""
    <div class="custom-footer">
        <p>Powered by <strong>LangChain</strong> • <strong>FAISS</strong> • <strong>Meta Llama 3</strong></p>
        <p style="margin-top: 0.5rem;">Built with ⚡ by the future of AI</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()