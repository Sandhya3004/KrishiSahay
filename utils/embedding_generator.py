#!/usr/bin/env python3
"""
Embedding Generator for KrishiSahay
Converts Q&A pairs into vector embeddings and creates FAISS index
"""

import json
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer
import os
import time

class EmbeddingGenerator:
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        """
        Initialize the embedding generator with a sentence transformer model
        """
        print(f"🔄 Loading embedding model: {model_name}...")
        self.model = SentenceTransformer(model_name)
        self.model_name = model_name
        print(f"✅ Model loaded successfully!")
        
    def load_qa_data(self, file_path):
        """
        Load Q&A data from JSON file
        """
        print(f"🔄 Loading data from {file_path}...")
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"✅ Loaded {len(data)} Q&A pairs")
            return data
        except FileNotFoundError:
            print(f"❌ File not found: {file_path}")
            return None
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing JSON: {e}")
            return None
    
    def prepare_texts(self, qa_data):
        """
        Prepare texts for embedding by combining question and answer
        """
        texts = []
        for item in qa_data:
            # Create a combined text with question and answer
            combined = f"प्रश्न: {item['question']} उत्तर: {item['answer']}"
            texts.append(combined)
        
        print(f"✅ Prepared {len(texts)} texts for embedding")
        return texts
    
    def generate_embeddings(self, texts, batch_size=32):
        """
        Generate embeddings for texts in batches
        """
        print(f"🔄 Generating embeddings for {len(texts)} texts...")
        print(f"   Batch size: {batch_size}")
        
        start_time = time.time()
        
        # Generate embeddings in batches to show progress
        embeddings = self.model.encode(
            texts, 
            batch_size=batch_size, 
            show_progress_bar=True,
            convert_to_numpy=True
        )
        
        end_time = time.time()
        print(f"✅ Generated {len(embeddings)} embeddings")
        print(f"   Embedding dimension: {embeddings.shape[1]}")
        print(f"   Time taken: {end_time - start_time:.2f} seconds")
        
        return embeddings
    
    def save_embeddings(self, embeddings, qa_data, output_file):
        """
        Save embeddings along with metadata
        """
        print(f"🔄 Saving embeddings to {output_file}...")
        
        # Create list of records with embeddings and metadata
        embedded_records = []
        for i, (emb, item) in enumerate(zip(embeddings, qa_data)):
            embedded_records.append({
                'id': i,
                'embedding': emb,
                'metadata': {
                    'question': item['question'],
                    'answer': item['answer'],
                    'crop': item.get('crop', 'unknown'),
                    'category': item.get('category', 'unknown'),
                    'language': item.get('language', 'hi')
                }
            })
        
        # Save to pickle file
        with open(output_file, 'wb') as f:
            pickle.dump(embedded_records, f)
        
        print(f"✅ Saved {len(embedded_records)} records to {output_file}")
        return embedded_records
    
    def create_faiss_index(self, embeddings, metadata, output_file):
        """
        Create FAISS index from embeddings
        """
        try:
            import faiss
        except ImportError:
            print("❌ FAISS not installed. Installing...")
            import subprocess
            subprocess.check_call(['pip', 'install', 'faiss-cpu'])
            import faiss
        
        print(f"🔄 Creating FAISS index...")
        
        # Convert embeddings to float32 (required by FAISS)
        embeddings = np.array(embeddings).astype('float32')
        
        # Get dimension
        dimension = embeddings.shape[1]
        
        # Create index
        index = faiss.IndexFlatL2(dimension)  # L2 distance index
        index.add(embeddings)
        
        print(f"✅ FAISS index created with {index.ntotal} vectors")
        print(f"   Index dimension: {dimension}")
        
        # Save index and metadata
        index_data = {
            'index': index,
            'metadata': metadata,
            'dimension': dimension,
            'num_vectors': index.ntotal
        }
        
        with open(output_file, 'wb') as f:
            pickle.dump(index_data, f)
        
        print(f"✅ FAISS index saved to {output_file}")
        
        return index, metadata

def main():
    """
    Main function to run the embedding generation process
    """
    print("=" * 60)
    print("🌾 KRISHISHAY - EMBEDDING GENERATOR")
    print("=" * 60)
    
    # Create output directories if they don't exist
    os.makedirs('embeddings', exist_ok=True)
    
    # Initialize generator
    generator = EmbeddingGenerator()
    
    # Load data
    qa_data = generator.load_qa_data('data/kcc_qa_pairs.json')
    if qa_data is None:
        return
    
    # Prepare texts
    texts = generator.prepare_texts(qa_data)
    
    # Generate embeddings
    embeddings = generator.generate_embeddings(texts)
    
    # Save embeddings with metadata
    embeddings_file = 'embeddings/kcc_embeddings.pkl'
    embedded_records = generator.save_embeddings(embeddings, qa_data, embeddings_file)
    
    # Create FAISS index
    metadata = [rec['metadata'] for rec in embedded_records]
    index_file = 'embeddings/faiss_index.pkl'
    index, metadata = generator.create_faiss_index(embeddings, metadata, index_file)
    
    print("\n" + "=" * 60)
    print("✅ EMBEDDING GENERATION COMPLETE!")
    print("=" * 60)
    print(f"📊 Statistics:")
    print(f"   - Total Q&A pairs: {len(qa_data)}")
    print(f"   - Embedding dimension: {embeddings.shape[1]}")
    print(f"   - Embeddings file: embeddings/kcc_embeddings.pkl")
    print(f"   - FAISS index file: embeddings/faiss_index.pkl")
    print("=" * 60)
    
    # Print sample of what was embedded
    print("\n📝 Sample of embedded data:")
    for i, item in enumerate(qa_data[:3]):
        print(f"\n{i+1}. Q: {item['question'][:50]}...")
        print(f"   A: {item['answer'][:50]}...")
        print(f"   Crop: {item.get('crop', 'N/A')}")

if __name__ == "__main__":
    main()
