import os
import time
import random
import re
import io
import sys
from dotenv import load_dotenv
import google.generativeai as genai
from groq import Groq

load_dotenv()

class HiddenPrints:
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = io.StringIO()
    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout = self._original_stdout

def human_delay(min_delay=0.5, max_delay=1.5):
    time.sleep(random.uniform(min_delay, max_delay))
    
class ReplyGenerator:

    """ReplyGenerator class for generating Business localities for the Provided Query"""

    def __init__(self, provider: str = "groq"):  # Set Groq as default __init__ is the contructor of the class whatsAppReplyGenerator
        
        self.provider = provider.lower() 

        self.system_prompt = """
            You are a commercial locality extraction assistant.

            **REQUIREMENTS:**
            - Return ONLY a clean, comma-separated list
            - Focus on areas with abundant commercial activity
            - Include popular shopping hubs, business districts, marketplaces, and food zones
            - Exclude purely residential areas, rural zones, or industrial-only regions

            **INCLUDE:**
            Major pouplation abundant areas
            Shopping malls and complexes
            Market areas and bazaars  
            Restaurant districts and food streets
            Central business districts (CBD)
            Commercial plazas and centers
            Entertainment and retail zones
            Popular cafe and dining areas
            Tourist commercial areas
            Mixed-use developments with retail

            """

        if self.provider == "gemini":
            gemini_api_key = os.getenv("GEMINI_API_KEY")
            if not gemini_api_key:
                raise ValueError("GEMINI_API_KEY environment variable not set.")
            genai.configure(api_key=gemini_api_key)
            self.model_name = "models/gemini-1.5-flash-latest"
            self.llm_client = genai.GenerativeModel(self.model_name)
            # print(f"Using Gemini model: {self.model_name}")

        elif self.provider == "groq":
            groq_api_key = os.getenv("GROQ_API_KEY")
            if not groq_api_key:
                raise ValueError("GROQ_API_KEY environment variable not set.")
            self.llm_client = Groq(api_key=groq_api_key)
            self.model_name = "deepseek-r1-distill-llama-70b" # A fast and capable Groq model
            # print(f"Using Groq model: {self.model_name}")
        else:
            raise ValueError("Invalid provider specified. Choose 'Gemini' or 'Groq'.")

    def generate_reply(self, customer_message: str) -> str:
        with HiddenPrints():
            try:
                messages = [
                    {"role": "user", "parts": [self.system_prompt]} if self.provider == "gemini" else {"role": "system", "content": self.system_prompt},
                    {"role": "user", "parts": [customer_message]} if self.provider == "gemini" else {"role": "user", "content": customer_message}
                ]

                if self.provider == "gemini":
                    response = self.llm_client.generate_content(
                        contents=messages,
                        generation_config=genai.types.GenerationConfig(
                            temperature=0.3,
                            max_output_tokens=2000
                        )
                    )

                    reply = response.text.strip()
                elif self.provider == "groq":
                    chat_completion = self.llm_client.chat.completions.create(
                        messages=messages,
                        model=self.model_name,
                        temperature=0.3,
                        max_tokens=6000, # Use max_tokens for Groq
                    )
                    reply = chat_completion.choices[0].message.content.strip()
                
                return self._clean_response(reply)
            except Exception as e:
                print(f"AI Error with {self.provider}: {e}") 
                return None  # Return None instead of error message

    def _clean_response(self, text: str) -> str:
        text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
        text = re.sub(r'<[^>]+>', '', text)
        return text.strip()

# --- Utility functions ---
def human_delay(min_delay=0.5, max_delay=1.5):
    """Adds a human-like delay between actions."""
    time.sleep(random.uniform(min_delay, max_delay))

