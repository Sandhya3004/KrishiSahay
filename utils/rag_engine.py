#!/usr/bin/env python3
"""
RAG Engine for KrishiSahay
Combines FAISS retrieval with LLM generation
"""

import pickle
import numpy as np
from sentence_transformers import SentenceTransformer
import os
import json
from typing import List, Dict, Any

class RAGEngine:
    def __init__(self, index_path="embeddings/faiss_index.pkl", model_name="all-MiniLM-L6-v2"):
        """
        Initialize the RAG engine with FAISS index and embedding model
        """
        print("🌾 Initializing RAG Engine...")
        
        # Load FAISS index and metadata
        try:
            with open(index_path, 'rb') as f:
                index_data = pickle.load(f)
            
            self.index = index_data['index']
            self.metadata = index_data['metadata']
            print(f"✅ Loaded FAISS index with {len(self.metadata)} vectors")
        except FileNotFoundError:
            print(f"❌ Index not found at {index_path}")
            print("Please run embedding generator first")
            raise
        
        # Load embedding model
        print("🔄 Loading embedding model...")
        self.embedding_model = SentenceTransformer(model_name)
        print(f"✅ Model loaded: {model_name}")
        
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for most similar Q&A pairs
        """
        # Generate query embedding
        query_vec = self.embedding_model.encode(query).astype('float32')
        
        # Search in FAISS
        distances, indices = self.index.search(np.array([query_vec]), top_k * 2)
        
        # Deduplicate answers
        seen_answers = set()
        results = []
        
        for idx in indices[0]:
            if idx < len(self.metadata):
                answer = self.metadata[idx]['answer'].strip()
                if answer not in seen_answers:
                    seen_answers.add(answer)
                    results.append({
                        'metadata': self.metadata[idx],
                        'distance': float(distances[0][len(results)]),
                        'similarity_score': 1 / (1 + float(distances[0][len(results)]))
                    })
            
            if len(results) >= top_k:
                break
        
        return results
    
    def format_context(self, results: List[Dict[str, Any]]) -> str:
        """
        Format search results into context for LLM
        """
        context = "Here are relevant questions and answers from the Kisan Call Centre database:\n\n"
        
        for i, result in enumerate(results, 1):
            meta = result['metadata']
            context += f"[{i}] Question: {meta['question']}\n"
            context += f"    Answer: {meta['answer']}\n"
            context += f"    (Crop: {meta['crop']}, Category: {meta['category']})\n\n"
        
        return context
    
    def get_offline_answer(self, query: str, top_k: int = 3) -> str:
        """
        Get answer using only retrieved results (offline mode)
        """
        results = self.search(query, top_k)
        
        if not results:
            return "क्षमा करें, इस सवाल से मिलता-जुलता कोई सवाल डेटाबेस में नहीं मिला।"
        
        response = "📋 **किसान कॉल सेंटर डेटाबेस से मिलते-जुलते सवाल:**\n\n"
        
        for i, result in enumerate(results, 1):
            meta = result['metadata']
            response += f"**{i}. प्रश्न:** {meta['question']}\n"
            response += f"**उत्तर:** {meta['answer']}\n"
            response += f"*फसल: {meta['crop']} | श्रेणी: {meta['category']}*\n"
            response += f"*(समानता: {result['similarity_score']:.2f})*\n\n"
        
        return response
    
    def hybrid_search(self, query: str, crop_filter: str = None, category_filter: str = None, top_k: int = 5):
        """
        Search with filters for crop and category
        """
        # First get more results than needed
        results = self.search(query, top_k * 3)
        
        # Apply filters if specified
        filtered_results = []
        for result in results:
            meta = result['metadata']
            
            if crop_filter and crop_filter.lower() not in meta['crop'].lower():
                continue
                
            if category_filter and category_filter.lower() not in meta['category'].lower():
                continue
            
            filtered_results.append(result)
            
            if len(filtered_results) >= top_k:
                break
        
        return filtered_results if filtered_results else results[:top_k]

# Test the engine
if __name__ == "__main__":
    print("=" * 60)
    print("🔍 TESTING RAG ENGINE")
    print("=" * 60)
    
    # Initialize engine
    engine = RAGEngine()
    
    # Test queries
    test_queries = [
        "सरसों में कीट कैसे नियंत्रित करें?",
        "मूंग बोने का समय",
        "गेहूं में खाद",
        "PM किसान योजना"
    ]
    
    for query in test_queries:
        print(f"\n📝 Query: {query}")
        print("-" * 40)
        
        # Search
        results = engine.search(query, top_k=3)
        
        print(f"Found {len(results)} results:")
        for i, result in enumerate(results, 1):
            print(f"\n  {i}. [{result['similarity_score']:.2f}] {result['metadata']['question'][:60]}...")
            print(f"     Crop: {result['metadata']['crop']}")
        
        # Show offline answer format
        print("\n  📋 Offline answer preview:")
        offline = engine.get_offline_answer(query, top_k=2)
        print(f"  {offline[:200]}...")
    
    print("\n" + "=" * 60)
    print("✅ RAG Engine test complete!")
    print("=" * 60)
