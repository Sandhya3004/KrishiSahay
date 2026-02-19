# utils/voice.py
import streamlit as st

def voice_component(lang="hi", key="voice"):
    lang_map = {
        'en': 'en-IN', 'hi': 'hi-IN', 'te': 'te-IN', 'ta': 'ta-IN',
        'kn': 'kn-IN', 'ml': 'ml-IN', 'bn': 'bn-IN', 'mr': 'mr-IN',
        'gu': 'gu-IN', 'pa': 'pa-IN', 'or': 'or-IN', 'as': 'as-IN'
    }
    recognition_lang = lang_map.get(lang, 'hi-IN')

    html_code = f"""
    <div style="text-align: center; margin: 10px 0;">
        <button id="mic-{key}" style="
            background: #2e7d32;
            color: white;
            border: none;
            border-radius: 50px;
            padding: 10px 20px;
            font-size: 16px;
            cursor: pointer;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        ">
            🎤 Speak
        </button>
        <p id="status-{key}" style="color: #666; margin-top: 5px;"></p>
    </div>
    <script>
    (function() {{
        const mic = document.getElementById('mic-{key}');
        const status = document.getElementById('status-{key}');
        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {{
            status.innerText = '❌ Not supported';
            mic.disabled = true;
            return;
        }}
        const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
        recognition.lang = '{recognition_lang}';
        recognition.continuous = false;
        recognition.interimResults = false;

        mic.onclick = () => {{
            recognition.start();
            status.innerText = '🎤 Listening...';
            mic.disabled = true;
        }};
        recognition.onresult = (e) => {{
            const text = e.results[0][0].transcript;
            status.innerText = '✅ Done';
            // Find the input with aria-label="VoiceTranscript"
            const input = document.querySelector('input[aria-label="VoiceTranscript"]');
            if (input) {{
                input.value = text;
                input.dispatchEvent(new Event('input', {{ bubbles: true }}));
            }}
            mic.disabled = false;
        }};
        recognition.onerror = (e) => {{
            status.innerText = '❌ Error: ' + e.error;
            mic.disabled = false;
        }};
        recognition.onend = () => {{
            mic.disabled = false;
        }};
    }})();
    </script>
    """
    return html_code