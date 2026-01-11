import streamlit as st
import faiss
import os
from dotenv import load_dotenv
from io import BytesIO
from docx import Document
import numpy as np

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
    if input_type == "Link":
        loader = WebBaseLoader(input_data)
        documents = loader.load()
        texts = [doc.page_content for doc in documents]

    elif input_type == "PDF":
        reader = PdfReader(input_data)
        texts = [page.extract_text() for page in reader.pages]

    elif input_type == "DOCX":
        doc = Document(input_data)
        texts = [p.text for p in doc.paragraphs]

    elif input_type == "TXT":
        texts = [input_data.read().decode("utf-8")]

    elif input_type == "Text":
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
    return vectorstore


# -------------------- RAG QA --------------------
def answer_question(vectorstore, query):
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

    retriever = vectorstore.as_retriever()

    chain = (
        {
            "context": retriever,
            "question": RunnablePassthrough(),
        }
        | prompt
        | llm
    )

    return chain.invoke(query).content


# -------------------- STREAMLIT UI --------------------
def main():
    st.title("RAG Q&A App")

    input_type = st.selectbox("Input Type", ["Link", "PDF", "Text", "DOCX", "TXT"])

    if input_type == "Link":
        url = st.text_input("Enter URL")
        input_data = [url]

    elif input_type == "Text":
        input_data = st.text_area("Enter text")

    else:
        input_data = st.file_uploader("Upload file")

    if st.button("Process"):
        st.session_state.vectorstore = process_input(input_type, input_data)
        st.success("Index created!")

    if "vectorstore" in st.session_state:
        query = st.text_input("Ask a question")
        if st.button("Ask"):
            answer = answer_question(st.session_state.vectorstore, query)
            st.write(answer)


if __name__ == "__main__":
    main()
