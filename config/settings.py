import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Gemini
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    
   
    
    # Paths & models
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"
    FAISS_INDEX_PATH = "embeddings/faiss_index.index"
    METADATA_PATH = "embeddings/meta.pkl"
    DATA_PATH = "data/kcc_qa_pairs.json"