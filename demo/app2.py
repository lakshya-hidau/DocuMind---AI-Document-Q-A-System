import streamlit as st
import faiss
import os
import time
from typing import List, Optional
from dotenv import load_dotenv

from langchain_community.document_loaders import TextLoader, PyPDFLoader, Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough

# Load environment variables
load_dotenv()
HUGGINGFACE_API_TOKEN = os.getenv("HUGGINGFACE_API_TOKEN")

# ==================== PAGE CONFIG ====================
st.set_page_config(
    page_title="RAG Assistant",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== MINIMAL CSS ====================
st.markdown("""
<style>
    /* Minimal CSS only for essential styling */
    .stButton > button {
        background-color: #2563eb;
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 6px;
        font-weight: 500;
        cursor: pointer;
        transition: opacity 0.2s;
    }
    
    .stButton > button:hover {
        opacity: 0.9;
    }
    
    .stButton > button:disabled {
        background-color: #94a3b8;
        cursor: not-allowed;
    }
    
    .status-ready {
        background-color: #dcfce7;
        color: #166534;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 500;
        display: inline-block;
    }
    
    .status-not-ready {
        background-color: #fee2e2;
        color: #991b1b;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 500;
        display: inline-block;
    }
    
    .message-user {
        background-color: #f1f5f9;
        padding: 12px 16px;
        margin: 8px 0;
        border-radius: 8px;
        border-left: 4px solid #2563eb;
    }
    
    .message-assistant {
        background-color: #ffffff;
        padding: 12px 16px;
        margin: 8px 0;
        border-radius: 8px;
        border-left: 4px solid #10b981;
        border: 1px solid #e2e8f0;
    }
    
    .source-card {
        background-color: #f8fafc;
        padding: 12px;
        margin: 8px 0;
        border-radius: 6px;
        border: 1px solid #e2e8f0;
        font-size: 14px;
    }
    
    .file-item {
        padding: 8px 12px;
        margin: 4px 0;
        background-color: #f8fafc;
        border-radius: 6px;
        font-size: 14px;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ==================== SESSION STATE ====================
if 'vectorstore' not in st.session_state:
    st.session_state.vectorstore = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'processed_files' not in st.session_state:
    st.session_state.processed_files = []
if 'processing' not in st.session_state:
    st.session_state.processing = False
if 'querying' not in st.session_state:
    st.session_state.querying = False

# ==================== CACHED FUNCTIONS ====================
@st.cache_resource(show_spinner=False)
def get_embeddings():
    """Cache embeddings model to avoid reloading"""
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-mpnet-base-v2",
        model_kwargs={'device': 'cpu'}
    )

@st.cache_resource(show_spinner=False)
def get_llm():
    """Cache LLM model"""
    if not HUGGINGFACE_API_TOKEN:
        return None
    
    llm_endpoint = HuggingFaceEndpoint(
        repo_id="meta-llama/Meta-Llama-3-8B-Instruct",
        provider="novita",
        temperature=0.7,
        huggingfacehub_api_token=HUGGINGFACE_API_TOKEN,
        max_length=500
    )
    return ChatHuggingFace(llm=llm_endpoint)

@st.cache_data(show_spinner=False, max_entries=10)
def load_document(file, file_type: str):
    """Load and cache document content"""
    try:
        if file_type == "pdf":
            from PyPDF2 import PdfReader
            reader = PdfReader(file)
            text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
        elif file_type == "docx":
            import docx2txt
            text = docx2txt.process(file)
        elif file_type == "txt":
            text = file.read().decode("utf-8")
        else:
            return None
        return text[:1000000]  # Limit to 1MB to prevent memory issues
    except Exception as e:
        st.error(f"Error loading {file_type}: {str(e)}")
        return None

def build_vector_store(texts: List[str]):
    """Build vector store from texts"""
    if not texts:
        return None
    
    # Split texts efficiently
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100,
        length_function=len,
    )
    
    chunks = text_splitter.split_text("\n".join(texts))
    
    if not chunks:
        return None
    
    # Get cached embeddings
    embeddings = get_embeddings()
    
    # Create FAISS index
    dim = 768  # Standard dimension for all-mpnet-base-v2
    index = faiss.IndexFlatL2(dim)
    
    vectorstore = FAISS(
        embedding_function=embeddings.embed_query,
        index=index,
        docstore=InMemoryDocstore(),
        index_to_docstore_id={}
    )
    
    # Add texts in batches for better performance
    batch_size = 50
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        vectorstore.add_texts(batch)
    
    return vectorstore

def ask_question(query: str, vectorstore) -> Optional[str]:
    """Ask question and get answer"""
    if not vectorstore or not query:
        return None
    
    llm = get_llm()
    if not llm:
        return "Error: LLM not available. Check API token."
    
    prompt = ChatPromptTemplate.from_template("""
    Context: {context}
    
    Question: {question}
    
    Answer the question based only on the context above.
    If the context doesn't contain relevant information, say "I cannot answer this based on the provided documents."
    Be concise and accurate.
    
    Answer:
    """)
    
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    
    chain = (
        {
            "context": retriever,
            "question": RunnablePassthrough(),
        }
        | prompt
        | llm
    )
    
    try:
        result = chain.invoke(query)
        return result.content
    except Exception as e:
        return f"Error generating answer: {str(e)}"

# ==================== SIDEBAR ====================
with st.sidebar:
    st.title("📁 Documents")
    st.markdown("---")
    
    # File uploader
    uploaded_files = st.file_uploader(
        "Choose files",
        type=['pdf', 'docx', 'txt'],
        accept_multiple_files=True,
        key="file_uploader"
    )
    
    # Process button
    process_disabled = len(uploaded_files) == 0 or st.session_state.processing
    if st.button("⚡ Process Documents", disabled=process_disabled, use_container_width=True):
        if uploaded_files:
            st.session_state.processing = True
            start_time = time.time()
            
            # Load and process documents
            texts = []
            file_names = []
            
            progress_text = st.empty()
            progress_bar = st.progress(0)
            
            for i, file in enumerate(uploaded_files):
                progress_text.text(f"Processing {file.name}...")
                file_type = file.name.split('.')[-1].lower()
                
                text = load_document(file, file_type)
                if text:
                    texts.append(text)
                    file_names.append(file.name)
                
                progress_bar.progress((i + 1) / len(uploaded_files))
            
            if texts:
                # Build vector store
                progress_text.text("Building vector index...")
                vectorstore = build_vector_store(texts)
                
                if vectorstore:
                    st.session_state.vectorstore = vectorstore
                    st.session_state.processed_files = file_names
                    processing_time = time.time() - start_time
                    
                    st.success(f"✅ Processed {len(file_names)} files in {processing_time:.1f}s")
                else:
                    st.error("Failed to build vector store")
            else:
                st.error("No valid text extracted from files")
            
            progress_text.empty()
            progress_bar.empty()
            st.session_state.processing = False
            
            # Force rerun to update UI
            st.rerun()
    
    st.markdown("---")
    
    # Model settings
    st.subheader("Settings")
    model_option = st.selectbox(
        "Model",
        ["Llama 3 8B", "Llama 2 7B", "Mistral 7B"],
        index=0,
        disabled=st.session_state.processing
    )
    
    temperature = st.slider(
        "Temperature",
        0.0, 1.0, 0.7, 0.1,
        disabled=st.session_state.processing
    )
    
    st.markdown("---")
    
    # Clear session button
    if st.button("🗑️ Clear All", type="secondary", use_container_width=True):
        st.session_state.vectorstore = None
        st.session_state.chat_history = []
        st.session_state.processed_files = []
        st.rerun()

# ==================== MAIN CONTENT ====================
# Header
col1, col2 = st.columns([3, 1])
with col1:
    st.title("AI Document Assistant")
    st.caption("Ask questions about your uploaded documents")

with col2:
    status = "Ready" if st.session_state.vectorstore else "Not Ready"
    status_class = "status-ready" if st.session_state.vectorstore else "status-not-ready"
    st.markdown(f'<div class="{status_class}">Vector DB: {status}</div>', unsafe_allow_html=True)

st.markdown("---")

# Chat history
chat_container = st.container()

with chat_container:
    if not st.session_state.chat_history:
        st.info("Upload documents and click 'Process Documents' to start asking questions.")
    
    # Limit chat history to last 20 messages for performance
    display_messages = st.session_state.chat_history[-20:] if st.session_state.chat_history else []
    
    for msg in display_messages:
        if msg["role"] == "user":
            st.markdown(f"""
            <div class="message-user">
                <strong>You:</strong> {msg["content"]}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="message-assistant">
                <strong>Assistant:</strong> {msg["content"]}
            </div>
            """, unsafe_allow_html=True)

# Query input at bottom
st.markdown("---")
query_container = st.container()

with query_container:
    col1, col2 = st.columns([4, 1])
    
    with col1:
        query = st.text_input(
            "Your question",
            placeholder="Ask a question about your documents...",
            label_visibility="collapsed",
            disabled=not st.session_state.vectorstore or st.session_state.querying,
            key="query_input"
        )
    
    with col2:
        ask_disabled = not query or not st.session_state.vectorstore or st.session_state.querying
        if st.button("Ask", disabled=ask_disabled, use_container_width=True):
            if query and st.session_state.vectorstore:
                st.session_state.querying = True
                start_time = time.time()
                
                # Add user message to history
                st.session_state.chat_history.append({"role": "user", "content": query})
                
                # Get answer
                answer = ask_question(query, st.session_state.vectorstore)
                
                if answer:
                    query_time = time.time() - start_time
                    answer_with_time = f"{answer}\n\n*Generated in {query_time:.1f}s*"
                    st.session_state.chat_history.append({"role": "assistant", "content": answer_with_time})
                else:
                    st.session_state.chat_history.append({"role": "assistant", "content": "Sorry, I couldn't generate an answer."})
                
                st.session_state.querying = False
                st.rerun()

# Show processed files
if st.session_state.processed_files:
    st.markdown("---")
    with st.expander(f"📄 Processed Files ({len(st.session_state.processed_files)})"):
        for file_name in st.session_state.processed_files:
            st.markdown(f'<div class="file-item">{file_name}</div>', unsafe_allow_html=True)

# Show sources for last query (lazy-loaded)
if st.session_state.vectorstore and st.session_state.chat_history:
    last_user_queries = [msg["content"] for msg in st.session_state.chat_history if msg["role"] == "user"]
    if last_user_queries:
        last_query = last_user_queries[-1]
        
        with st.expander("🔍 View Sources", expanded=False):
            if st.session_state.vectorstore:
                try:
                    retriever = st.session_state.vectorstore.as_retriever(search_kwargs={"k": 3})
                    docs = retriever.invoke(last_query)
                    
                    for i, doc in enumerate(docs):
                        preview = doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content
                        st.markdown(f"""
                        <div class="source-card">
                            <strong>Source {i+1}</strong><br>
                            {preview}
                        </div>
                        """, unsafe_allow_html=True)
                except Exception as e:
                    st.warning(f"Could not retrieve sources: {str(e)}")

# Status indicator at bottom
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    if st.session_state.processing:
        st.info("🔄 Processing documents...")

with col2:
    if st.session_state.querying:
        st.info("🤔 Generating answer...")

with col3:
    if st.session_state.vectorstore:
        st.caption(f"📚 {len(st.session_state.processed_files)} files loaded")

# Footer
st.markdown("---")
st.caption("Powered by LangChain • HuggingFace • FAISS")