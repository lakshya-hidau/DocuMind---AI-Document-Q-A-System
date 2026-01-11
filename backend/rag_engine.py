import os
from dotenv import load_dotenv
from io import BytesIO
from docx import Document
import faiss
import numpy as np
import logging

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

logger = logging.getLogger(__name__)

if not HUGGINGFACE_API_TOKEN:
    raise RuntimeError(
        "HUGGINGFACE_API_TOKEN is not set. Provide an api_key to work with the novita provider or run `hf auth login`. "
        "Set `HUGGINGFACE_API_TOKEN` in a `.env` file or your environment before starting the server."
    )

class RAGEngine:
    def __init__(self):
        self.vectorstores = {} # session_id -> vectorstore
        
        logger.info("Initializing models (Caching for speed)...")
        # Pre-initialize embeddings - This is a large model, we only want to load it once
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        
        # Pre-initialize LLM endpoint
        self.llm_endpoint = HuggingFaceEndpoint(
            repo_id="meta-llama/Llama-3.2-1B-Instruct",
            provider="novita",
            temperature=0.6,
            huggingfacehub_api_token=HUGGINGFACE_API_TOKEN,
        )
        self.llm = ChatHuggingFace(llm=self.llm_endpoint)
        
        self.prompt = ChatPromptTemplate.from_template(
            """Answer using the context below.
If you don't know, say you don't know.

Context:
{context}

Question:
{question}"""
        )
        logger.info("Models initialized successfully.")

    def process_input(self, session_id: str, input_type: str, input_data):
        texts = []
        if input_type == "Link":
            loader = WebBaseLoader(input_data)
            documents = loader.load()
            texts = [doc.page_content for doc in documents]

        elif input_type == "PDF":
            reader = PdfReader(BytesIO(input_data))
            texts = [page.extract_text() for page in reader.pages]

        elif input_type == "DOCX":
            doc = Document(BytesIO(input_data))
            texts = [p.text for p in doc.paragraphs]

        elif input_type == "TXT":
            texts = [input_data.decode("utf-8")]

        elif input_type == "Text":
            texts = [input_data]

        else:
            raise ValueError("Unsupported input type")

        splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        chunks = splitter.split_text("\n".join(texts))

        # Use the cached embeddings
        dim = len(self.embeddings.embed_query("test"))
        index = faiss.IndexFlatL2(dim)

        vectorstore = FAISS(
            embedding_function=self.embeddings.embed_query,
            index=index,
            docstore=InMemoryDocstore(),
            index_to_docstore_id={}
        )

        vectorstore.add_texts(chunks)
        self.vectorstores[session_id] = vectorstore
        return True

    def answer_question(self, session_id: str, query: str):
        if session_id not in self.vectorstores:
            return "Session not found or index not created. Please upload a document first."
        
        vectorstore = self.vectorstores[session_id]
        retriever = vectorstore.as_retriever()

        chain = (
            {
                "context": retriever,
                "question": RunnablePassthrough(),
            }
            | self.prompt
            | self.llm
        )

        return chain.invoke(query).content

    def answer_question_stream(self, session_id: str, query: str):
        if session_id not in self.vectorstores:
            yield "Session not found or index not created. Please upload a document first."
            return
        
        vectorstore = self.vectorstores[session_id]
        retriever = vectorstore.as_retriever()

        chain = (
            {
                "context": retriever,
                "question": RunnablePassthrough(),
            }
            | self.prompt
            | self.llm
        )

        for chunk in chain.stream(query):
            if hasattr(chunk, 'content'):
                yield chunk.content
            else:
                yield str(chunk)
