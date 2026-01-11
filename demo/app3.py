import streamlit as st
import os
import time
from io import BytesIO
from PyPDF2 import PdfReader
from docx import Document
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings, HuggingFaceEndpoint, ChatHuggingFace
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_community.docstore.in_memory import InMemoryDocstore
import faiss

# --- 1. CONFIGURATION & STYLING ---
st.set_page_config(page_title="Pro RAG", page_icon="⚡", layout="wide")

# Minimal CSS for professional look and tight spacing
st.markdown("""
    <style>
    .block-container {padding-top: 2rem; padding-bottom: 0rem;}
    .stDeployButton {display:none;}
    [data-testid="stStatusWidget"] {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stChatMessage {background-color: transparent !important; border-bottom: 1px solid #f0f2f6 !important; border-radius: 0px !important;}
    .stButton button {border-radius: 4px; border: 1px solid #1677ff; background-color: #1677ff; color: white;}
    .stButton button:hover {background-color: #0958d9; border-color: #0958d9;}
    </style>
""", unsafe_allow_html=True)

# --- 2. RESOURCE CACHING (Performance Core) ---
@st.cache_resource
def get_embedding_model():
    return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

@st.cache_resource
def get_llm():
    # Use environment variable for token
    api_token = os.getenv("HUGGINGFACE_API_TOKEN")
    llm_endpoint = HuggingFaceEndpoint(
        repo_id="meta-llama/Meta-Llama-3-8B-Instruct",
        task="text-generation",
        max_new_tokens=512,
        temp=0.1,
        huggingfacehub_api_token=api_token,
    )
    return ChatHuggingFace(llm=llm_endpoint)

# --- 3. DOCUMENT PROCESSING ---
def extract_text(uploaded_files):
    all_text = ""
    for file in uploaded_files:
        if file.name.endswith(".pdf"):
            reader = PdfReader(file)
            for page in reader.pages:
                all_text += page.extract_text() + "\n"
        elif file.name.endswith(".docx"):
            doc = Document(file)
            all_text += "\n".join([p.text for p in doc.paragraphs])
        elif file.name.endswith(".txt"):
            all_text += file.read().decode("utf-8") + "\n"
    return all_text

def build_vector_store(text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=50)
    chunks = text_splitter.split_text(text)
    
    embeddings = get_embedding_model()
    vectorstore = FAISS.from_texts(chunks, embeddings)
    return vectorstore

# --- 4. SESSION STATE INIT ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "vectorstore" not in st.session_state:
    st.session_state.vectorstore = None

# --- 5. UI - HEADER ---
col1, col2 = st.columns([4, 1])
with col1:
    st.subheader("⚡ AI Document Assistant")
with col2:
    if st.session_state.vectorstore:
        st.write("🟢 **System Ready**")
    else:
        st.write("⚪ **No Context**")

# --- 6. UI - SIDEBAR ---
with st.sidebar:
    st.markdown("### 🛠 Configuration")
    uploaded_files = st.file_uploader(
        "Upload Documents", 
        type=["pdf", "docx", "txt"], 
        accept_multiple_files=True,
        help="Max 5MB per file"
    )
    
    if st.button("Process Documents", use_container_width=True):
        if uploaded_files:
            with st.spinner("Indexing..."):
                raw_text = extract_text(uploaded_files)
                st.session_state.vectorstore = build_vector_store(raw_text)
                st.success("Indexing Complete")
                st.rerun()
        else:
            st.error("Please upload files first.")

    st.divider()
    if st.button("Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.vectorstore = None
        st.rerun()

# --- 7. MAIN CHAT AREA ---
# Display limit history to maintain performance
for message in st.session_state.messages[-10:]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 8. QUERY LOGIC ---
if query := st.chat_input("Ask a question about your documents..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)

    # Generate response
    with st.chat_message("assistant"):
        if st.session_state.vectorstore is None:
            response = "Please upload and process documents in the sidebar first."
            st.warning(response)
        else:
            start_time = time.time()
            with st.spinner("Thinking..."):
                # Retrieval
                retriever = st.session_state.vectorstore.as_retriever(search_kwargs={"k": 3})
                docs = retriever.invoke(query)
                context = "\n\n".join([doc.page_content for doc in docs])
                
                # Generation
                prompt = ChatPromptTemplate.from_template("""
                Answer based strictly on context. If unknown, say "Information not found in documents."
                Context: {context}
                Question: {question}
                """)
                
                chain = prompt | get_llm()
                res = chain.invoke({"context": context, "question": query})
                response = res.content
                
                # Sources Expander (Lazy-load style)
                st.markdown(response)
                elapsed = round(time.time() - start_time, 2)
                st.caption(f"Latency: {elapsed}s")
                
                with st.expander("View Source Chunks"):
                    for i, doc in enumerate(docs):
                        st.markdown(f"**Source {i+1}:**\n{doc.page_content[:200]}...")

        st.session_state.messages.append({"role": "assistant", "content": response})