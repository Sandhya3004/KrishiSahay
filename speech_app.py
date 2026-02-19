from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
import sys
sys.path.append('utils')

from rag_engine import RAGEngine
from dynamic_translator import translate_text_cached
from gemini_llm import GeminiLLM  # Use Gemini instead of Groq

load_dotenv()

app = Flask(__name__)
CORS(app)

rag = RAGEngine()
llm = GeminiLLM()  # This will use mock if no API key
@app.route('/')
def index():
    return app.send_static_file('index.html')
@app.route('/process', methods=['POST'])
def process():
    data = request.json
    query_text = data.get('text', '')
    source_lang = data.get('lang', 'en')

    if source_lang != 'en':
        english_query = translate_text_cached(query_text, 'en')
    else:
        english_query = query_text

    results = rag.search(english_query, top_k=3)
    answer_english = llm.generate_with_retrieval(english_query, results)

    if source_lang != 'en':
        final_answer = translate_text_cached(answer_english, source_lang)
    else:
        final_answer = answer_english

    return jsonify({
        'answer': final_answer,
        'lang': source_lang
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)