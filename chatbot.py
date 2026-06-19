import json
from google import genai
from google.genai import types
from config import Config

class ChatbotEngine:
    def __init__(self):
        # Initializes using GEMINI_API_KEY from environment/config variables
        self.client = genai.Client(api_key=Config.GEMINI_API_KEY)
        self.model_name = "gemini-2.5-flash"

    def generate_response(self, chat_history, new_message):
        """
        Generates a contextual chatbot response based on conversation history.
        chat_history format: list of dicts with {'sender': 'user'/'bot', 'message_text': '...'}
        """
        contents = []
        # Map DB structure to Gemini role types
        for msg in chat_history:
            role = "user" if msg['sender'] == 'user' else "model"
            contents.append(types.Content(
                role=role,
                parts=[types.Part.from_text(text=msg['message_text'])]
            ))
        
        # Add the incoming user message
        contents.append(types.Content(role="user", parts=[types.Part.from_text(text=new_message)]))
        
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction="You are a helpful, clever, and friendly AI Assistant."
                )
            )
            return response.text
        except Exception as e:
            return f"Error connecting to AI Engine: {str(e)}"

    def analyze_sentiment(self, text):
        """
        Analyzes textual sentiment using structured JSON responses.
        """
        prompt = f"Analyze the sentiment of the following text. Respond strictly with a single JSON object containing a 'sentiment' key whose value is exactly one of 'Positive', 'Negative', or 'Neutral'.\n\nText: {text}"
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            data = json.loads(response.text)
            return data.get('sentiment', 'Neutral')
        except Exception:
            return "Neutral"
