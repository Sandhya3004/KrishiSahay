from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

class GeminiLLM:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("⚠️ No Gemini API key. Using mock responses.")
            self.use_mock = True
            return

        self.client = genai.Client(api_key=api_key)
        self.use_mock = False
        self.model = "models/gemini-2.0-flash"
        print(f"✅ Gemini model '{self.model}' ready.")

    def generate_response(self, query, context=None, target_lang='en'):
        """Generate a response in the target language."""
        if self.use_mock:
            return self._mock_response(query, context)

        # Language instruction for the model
        lang_instruction = {
            'en': "Respond in English only.",
            'hi': "केवल हिंदी में उत्तर दें।",
            'te': "తెలుగులో మాత్రమే సమాధానం ఇవ్వండి.",
            'ta': "தமிழில் மட்டும் பதில் அளிக்கவும்.",
            'kn': "ಕನ್ನಡದಲ್ಲಿ ಮಾತ್ರ ಉತ್ತರಿಸಿ.",
            'ml': "മലയാളത്തിൽ മാത്രം ഉത്തരം നൽകുക.",
            'bn': "শুধুমাত্র বাংলায় উত্তর দিন।",
            'mr': "फक्त मराठीत उत्तर द्या.",
            'gu': "માત્ર ગુજરાતીમાં જવાબ આપો.",
            'pa': "ਕੇਵਲ ਪੰਜਾਬੀ ਵਿੱਚ ਉੱਤਰ ਦਿਓ।",
            'or': "କେବଳ ଓଡ଼ିଆରେ ଉତ୍ତର ଦିଅନ୍ତୁ।",
            'as': "কেৱল অসমীয়াত উত্তৰ দিয়ক।"
        }.get(target_lang, "Respond in English only.")

        if context and context.strip():
            prompt = f"""You are KrishiSahay, an expert agricultural assistant for Indian farmers.
Below is relevant information from the Kisan Call Centre database. Use it if helpful.

{context}

Farmer's Question: {query}

{lang_instruction}
Be practical, specific, and helpful. If unsure, give your best guess based on common farming practices.
"""
        else:
            prompt = f"""You are KrishiSahay, an expert agricultural assistant for Indian farmers.

Farmer's Question: {query}

{lang_instruction}
Be practical, specific, and helpful. If unsure, give your best guess based on common farming practices.
"""

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt
            )
            return response.text
        except Exception as e:
            print(f"Gemini API error: {e}")
            return self._mock_response(query, context)

    def generate_with_retrieval(self, query, results, target_lang='en'):
        """Use retrieved results as context and respond in target language."""
        if not results:
            return self.generate_response(query, target_lang=target_lang)
        context = "Relevant Q&A pairs from Kisan Call Centre:\n\n"
        for i, r in enumerate(results, 1):
            meta = r['metadata']
            context += f"{i}. प्रश्न: {meta['question']}\n   उत्तर: {meta['answer']}\n   (फसल: {meta['crop']})\n\n"
        return self.generate_response(query, context, target_lang)

    def _mock_response(self, query, context=None):
        # (same as before)
        q = query.lower()
        if "सरसों" in q or "mustard" in q or "aphid" in q:
            return "🌾 **सरसों में कीट नियंत्रण:** इमिडाक्लोफिड 17.8 SL 100 ml/एकड़ (200 लीटर पानी) या नीम तेल 2% का छिड़काव करें।"
        elif "मूंग" in q or "moong" in q or "बुवाई" in q:
            return "🌱 **मूंग बुवाई का समय:** 10 मार्च से 10 अप्रैल (ग्रीष्मकालीन)। उन्नत किस्में: पंत मूंग-5, एसएमएल-668।"
        else:
            return "🤝 कृपया अपना प्रश्न स्पष्ट करें या किसान कॉल सेंटर 1800-180-1551 पर संपर्क करें।"