#!/usr/bin/env python3
"""
Dynamic Translator using deep-translator (Google Translate free)
"""

from deep_translator import GoogleTranslator
import streamlit as st

class DynamicTranslator:
    def __init__(self):
        self.supported_languages = {
            'en': 'English',
            'hi': 'हिन्दी (Hindi)',
            'te': 'తెలుగు (Telugu)',
            'ta': 'தமிழ் (Tamil)',
            'kn': 'ಕನ್ನಡ (Kannada)',
            'ml': 'മലയാളം (Malayalam)',
            'bn': 'বাংলা (Bengali)',
            'mr': 'मराठी (Marathi)',
            'gu': 'ગુજરાતી (Gujarati)',
            'pa': 'ਪੰਜਾਬੀ (Punjabi)',
            'or': 'ଓଡ଼ିଆ (Odia)',
            'as': 'অসমীয়া (Assamese)'
            
        }

    def translate_text(self, text, dest_lang):
        if dest_lang == 'en' or not text or not text.strip():
            return text
        try:
            from deep_translator import GoogleTranslator
            translated = GoogleTranslator(source='auto', target=dest_lang).translate(text)
            return translated
        except Exception as e:
            print(f"Translation error: {e}")
            return text  # fallback to original

# Simple cached translation function
@st.cache_data(ttl=3600)
def translate_text_cached(text, dest_lang):
    if dest_lang == 'en' or not text:
        return text
    try:
        translator = GoogleTranslator(source='auto', target=dest_lang)
        return translator.translate(text)
    except Exception as e:
        print(f"Translation error for '{text[:20]}...' to {dest_lang}: {e}")
        return text
# Global translator instance (not strictly needed now)
@st.cache_resource
def get_translator():
    return DynamicTranslator()