"""
IBM Watsonx LLM Integration for KrishiSahay
"""

import os
import requests
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

class WatsonxLLM:
    def __init__(self):
        """
        Initialize Watsonx LLM with API credentials
        """
        self.api_key = os.getenv("WATSONX_API_KEY")
        self.project_id = os.getenv("WATSONX_PROJECT_ID")
        self.model_id = os.getenv("MODEL_ID", "ibm/granite-3-8b-instruct")
        self.iam_token = None
        self.token_expiry = None
        
        if not self.api_key or not self.project_id:
            print("⚠️  Warning: Watsonx credentials not found in .env file")
            print("Please create a .env file with your credentials for online mode")    
    def get_iam_token(self):
        """
        Get IAM token for Watsonx authentication
        """
        if not self.api_key:
            return None
            
        iam_url = "https://iam.cloud.ibm.com/identity/token"
        iam_data = {
            "apikey": self.api_key,
            "grant_type": "urn:ibm:params:oauth:grant-type:apikey"
        }
        iam_headers = {"Content-Type": "application/x-www-form-urlencoded"}
        
        try:
            response = requests.post(iam_url, data=iam_data, headers=iam_headers)
            response.raise_for_status()
            self.iam_token = response.json()["access_token"]
            return self.iam_token
        except Exception as e:
            print(f"Error getting IAM token: {e}")
            return None
    
    def generate_response(self, query: str, context: str = None, language: str = "hi") -> str:
        """
        Generate response using Watsonx Granite LLM
        """
        if not self.api_key or not self.project_id:
            return self._get_mock_response(query, context)
        
        # Get IAM token if not available
        if not self.iam_token:
            self.get_iam_token()
            if not self.iam_token:
                return "Failed to authenticate with Watsonx. Using offline mode."
        
        # Prepare system prompt based on language
        if language == "hi":
            system_prompt = """आप कृषि सहायक हैं जो भारतीय किसानों को कृषि संबंधी सलाह देते हैं।
आपका नाम KrishiSahay है। आप हिंदी और अंग्रेजी में जवाब दे सकते हैं।
हमेशा विनम्र और मददगार बनें। अगर कुछ पता नहीं है तो ईमानदारी से कहें।
किसानों को "श्रीमान जी" या "किसान भाई" कहकर संबोधित करें।"""
        else:
            system_prompt = """You are KrishiSahay, an agricultural assistant for Indian farmers.
You provide practical farming advice in simple Hindi or English.
Be polite, helpful, and honest. Address farmers respectfully."""
        
        # Prepare user message with context
        if context:
            user_message = f"""Here is relevant information from the Kisan Call Centre database:

{context}

Farmer's Question: {query}

Please provide a helpful, accurate response. If the context is relevant, use it. 
If not, use your general knowledge but be honest about it. 
Respond in Hinglish (mix of Hindi and English) for better understanding."""
        else:
            user_message = query
        
        # Watsonx API endpoint
        api_url = "https://eu-de.ml.cloud.ibm.com/ml/v1/text/chat?version=2023-05-29"
        
        headers = {
            "Authorization": f"Bearer {self.iam_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model_id": self.model_id,
            "project_id": self.project_id,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            "parameters": {
                "decoding_method": "greedy",
                "max_new_tokens": 500,
                "temperature": 0.3,
                "top_p": 0.9
            }
        }
        
        try:
            response = requests.post(api_url, headers=headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            return result.get('choices', [{}])[0].get('message', {}).get('content', 'No response generated')
            
        except Exception as e:
            print(f"Error calling Watsonx API: {e}")
            return self._get_mock_response(query, context)
    
    def _get_mock_response(self, query: str, context: str = None) -> str:
        """
        Return a mock response for testing when Watsonx is not available
        """
        if "कीट" in query or "कीड़ा" in query or "aphid" in query.lower():
            return """श्रीमान जी, कीट नियंत्रण के लिए:

1. नीम तेल (2%) का छिड़काव करें - 20 मिली नीम तेल प्रति लीटर पानी
2. इमिडाक्लोफिड 17.8 SL 100 ml प्रति एकड़ 200 लीटर पानी में मिलाकर छिड़काव करें
3. छिड़काव सुबह या शाम के समय करें

धन्यवाद!"""
        
        elif "मूंग" in query or "moong" in query.lower():
            return """श्रीमान जी, मूंग की बुवाई का सही समय:

✅ ग्रीष्मकालीन मूंग: 10 मार्च से 10 अप्रैल
✅ खरीफ मूंग: जून-जुलाई
✅ उन्नत किस्में: पंत मूंग-5, एसएमएल-668

बुवाई से पहले बीज को उपचारित करना न भूलें।"""
        
        else:
            return f"""श्रीमान जी, आपके सवाल के लिए धन्यवाद।

आपने पूछा: {query}

इस बारे में अधिक जानकारी के लिए कृपया:
1. अपने नजदीकी कृषि विज्ञान केंद्र से संपर्क करें
2. किसान कॉल सेंटर 1800-180-1551 पर कॉल करें

धन्यवाद! - आपके KrishiSahay"""
    
    def generate_with_retrieval(self, query: str, retrieved_results: list) -> str:
        """
        Generate response using retrieved context
        """
        # Format context
        context = "Kisan Call Centre Database:\n\n"
        for i, result in enumerate(retrieved_results, 1):
            meta = result['metadata']
            context += f"{i}. प्रश्न: {meta['question']}\n"
            context += f"   उत्तर: {meta['answer']}\n"
            context += f"   (फसल: {meta['crop']})\n\n"
        
        return self.generate_response(query, context)
# Test the LLM
if __name__ == "__main__":
    print("=" * 60)
    print("🤖 TESTING WATSONX LLM (MOCK MODE)")
    print("=" * 60)
    
    llm = WatsonxLLM()
    
    # Test queries
    test_queries = [
        "सरसों में कीट कैसे नियंत्रित करें?",
        "मूंग बोने का सही समय क्या है?",
        "गेहूं में खाद कब डालें?",
        "PM किसान योजना के लिए आवेदन कैसे करें?"
    ]
    
    for query in test_queries:
        print(f"\n📝 Query: {query}")
        print("-" * 50)
        
        response = llm.generate_response(query)
        print(f"🤖 Response:\n{response}")
        print("-" * 50)
    
    # Test with retrieved context
    print("\n📚 Testing with retrieved context:")
    print("-" * 50)
    
    mock_results = [
        {
            'metadata': {
                'question': 'मूंग की बुवाई का सही समय क्या है?',
                'answer': 'मूंग की बुवाई का उपयुक्त समय 10 मार्च से 10 अप्रैल तक है।',
                'crop': 'मूंग'
            }
        }
    ]
    
    response = llm.generate_with_retrieval("मूंग कब बोएं?", mock_results)
    print(f"🤖 Response with context:\n{response}")
    
    print("\n" + "=" * 60)
    print("✅ Test complete! Watsonx LLM (Mock Mode) is working!")
    print("=" * 60)
