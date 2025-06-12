import os
import pandas as pd
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, CSVLoader
from typing import List
from difflib import SequenceMatcher

# Load environment variables
load_dotenv()

# Get Hugging Face token
hf = os.getenv("HUGGINGFACE_API_TOKEN")
if hf:
    os.environ["HUGGINGFACE_API_TOKEN"] = hf
    print("✅ Loaded Hugging Face token.")
else:
    print("❌ Failed to load Hugging Face token from .env")


# Load CSV
def csvloader(csv_path: str) -> List[Document]:
    loader = CSVLoader(
        file_path=csv_path,
        csv_args={'delimiter': ',', 'quotechar': '"'}
    )
    return loader.load()

# Load PDF
def pdfloader(pdf_path: str) -> List[Document]:
    loader = PyPDFLoader(pdf_path)
    return loader.load()

# Chunk documents
def chunking(documents: List[Document], chunk_size: int = 300, chunk_overlap: int = 20) -> List[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, 
        chunk_overlap=chunk_overlap
    )
    return splitter.split_documents(documents)

# Remove redundant chunks
def is_similar(a: str, b: str, threshold: float = 0.95) -> bool:
    return SequenceMatcher(None, a, b).ratio() > threshold

def deduplicate_chunks(chunks: List[Document]) -> List[Document]:
    seen = []
    unique_chunks = []
    for doc in chunks:
        content = doc.page_content.strip()
        if not any(is_similar(content, s) for s in seen):
            seen.append(content)
            unique_chunks.append(doc)
    return unique_chunks

# Embed documents using FAISS
def embed(docs: List[Document], model_name: str = "BAAI/bge-base-en-v1.5") -> FAISS:
    print(f"📌 Using embedding model: {model_name}")
    embeddings = HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )
    vs = FAISS.from_documents(docs, embedding=embeddings)
    vs.save_local("faiss_index")
    return vs


if __name__ == "__main__":
    print("📥 Loading documents...")
    csv_docs = csvloader("D:\\qar\\data\\catalog.csv")

    try:
        pdf_docs = pdfloader("D:\\qar\\data\\Qahwa Info.pdf")
    except FileNotFoundError:
        pdf_docs = []
        print("⚠️ No FAQ PDF found. Skipping...")

    all_docs = csv_docs + pdf_docs
    print(f"📄 Loaded {len(all_docs)} raw documents")

    chunks = chunking(all_docs)
    print(f"🔪 Split into {len(chunks)} chunks")

    clean_chunks = deduplicate_chunks(chunks)
    print(f"🧹 Deduplicated to {len(clean_chunks)} unique chunks")

    print("🔗 Embedding and saving to FAISS...")
    vs = embed(clean_chunks)
    print("✅ FAISS vectorstore saved as 'faiss_index'")
