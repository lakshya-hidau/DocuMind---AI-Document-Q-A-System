import os
import logging
from io import BytesIO
from dotenv import load_dotenv

import faiss
from docx import Document
from PyPDF2 import PdfReader

from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.docstore.in_memory import InMemoryDocstore

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough

from langchain_huggingface import (
    HuggingFaceEndpoint,
    ChatHuggingFace,
    HuggingFaceEndpointEmbeddings,
)

load_dotenv()
HUGGINGFACE_API_TOKEN = os.getenv("HUGGINGFACE_API_TOKEN")

logger = logging.getLogger(__name__)

if not HUGGINGFACE_API_TOKEN:
    raise RuntimeError("HUGGINGFACE_API_TOKEN is missing")


class RAGEngine:
    def __init__(self):
        self.vectorstores = {}

        logger.info("Initializing API-based embeddings and LLM...")

        # ✅ CORRECT embedding class
        self.embeddings = HuggingFaceEndpointEmbeddings(
            repo_id="sentence-transformers/all-MiniLM-L6-v2",
            huggingfacehub_api_token=HUGGINGFACE_API_TOKEN,
        )

        # LLM
        self.llm_endpoint = HuggingFaceEndpoint(
            repo_id="meta-llama/Llama-3.2-1B-Instruct",
            provider="novita",
            temperature=0.6,
            huggingfacehub_api_token=HUGGINGFACE_API_TOKEN,
        )

        self.llm = ChatHuggingFace(llm=self.llm_endpoint)

        self.prompt = ChatPromptTemplate.from_template(
            """Answer using ONLY the context below.
If you don't know, say you don't know.

Context:
{context}

Question:
{question}"""
        )

        logger.info("RAG Engine initialized successfully.")

    # --------------------------------------------------
    # Document Processing
    # --------------------------------------------------
    def process_input(self, session_id: str, input_type: str, input_data):
        texts = []

        if input_type == "Link":
            docs = WebBaseLoader(input_data).load()
            texts = [d.page_content for d in docs]

        elif input_type == "PDF":
            reader = PdfReader(BytesIO(input_data))
            texts = [p.extract_text() or "" for p in reader.pages]

        elif input_type == "DOCX":
            doc = Document(BytesIO(input_data))
            texts = [p.text for p in doc.paragraphs]

        elif input_type == "TXT":
            texts = [input_data.decode("utf-8")]

        elif input_type == "Text":
            texts = [input_data]

        else:
            raise ValueError("Unsupported input type")

        splitter = CharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100
        )

        chunks = splitter.split_text("\n".join(texts))

        if not chunks:
            raise ValueError("No valid text extracted from input")

        # ✅ CORRECT embedding call
        embeddings = self.embeddings.embed_documents(chunks)

        dim = len(embeddings[0])
        index = faiss.IndexFlatL2(dim)

        vectorstore = FAISS(
            index=index,
            docstore=InMemoryDocstore(),
            index_to_docstore_id={},
            embedding_function=self.embeddings,
        )

        vectorstore.add_texts(chunks)

        self.vectorstores[session_id] = vectorstore
        return True

    # --------------------------------------------------
    # Chat
    # --------------------------------------------------
    def answer_question(self, session_id: str, query: str):
        if session_id not in self.vectorstores:
            return "Session not found. Please upload a document first."

        retriever = self.vectorstores[session_id].as_retriever()

        chain = (
            {
                "context": retriever,
                "question": RunnablePassthrough(),
            }
            | self.prompt
            | self.llm
        )

        return chain.invoke(query).content

    # --------------------------------------------------
    # Streaming Chat
    # --------------------------------------------------
    def answer_question_stream(self, session_id: str, query: str):
        if session_id not in self.vectorstores:
            yield "Session not found. Please upload a document first."
            return

        retriever = self.vectorstores[session_id].as_retriever()

        chain = (
            {
                "context": retriever,
                "question": RunnablePassthrough(),
            }
            | self.prompt
            | self.llm
        )

        for chunk in chain.stream(query):
            if hasattr(chunk, "content"):
                yield chunk.content
