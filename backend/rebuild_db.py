import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

DB_PATH = os.path.join(os.path.dirname(__file__), "rgukt2_db")
DATASETS_PATH = os.path.join(os.path.dirname(__file__), "rgukt_datasets")

print("Loading embeddings model...")
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

print("Loading PDFs...")
docs = []
for filename in os.listdir(DATASETS_PATH):
    if filename.endswith(".pdf"):
        filepath = os.path.join(DATASETS_PATH, filename)
        print(f"  Loading {filename}...")
        loader = PyPDFLoader(filepath)
        docs.extend(loader.load())

print(f"Total pages loaded: {len(docs)}")

print("Splitting documents...")
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = splitter.split_documents(docs)
print(f"Total chunks: {len(chunks)}")

print("Building vector store...")
vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory=DB_PATH
)
vectorstore.persist()
print(f"✅ Vector database built successfully at {DB_PATH}")