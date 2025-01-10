import os
import re
import vertexai
import google.generativeai as genai
import vertexai.preview.generative_models as generative_models
from vertexai.generative_models import GenerativeModel, Part, FinishReason
from base64 import b64encode, b64decode
from dotenv import load_dotenv
load_dotenv()


safety_settings = {
    generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
}

# Adjust generation parameters
generation_config = {
    "max_output_tokens": 8192,
    "temperature": 0.1,  # Reduce randomness
    "top_k": 40,         # Consider top 50 tokens
    "top_p": 0.9         # Cover 90% of cumulative probability mass
}

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GCP_PROJECT_NAME = os.getenv("GCP_PROJECT_NAME")
GENERATIVE_MODEL = os.getenv("GENERATIVE_MODEL")



class Gemini_model():

    def __init__(self):
        genai.configure(api_key=GOOGLE_API_KEY)
        vertexai.init(project=GCP_PROJECT_NAME, location="us-central1")


    def load_prompt(self):
        file_path = "prompt.md"
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                prompt = file.read()
        except FileNotFoundError:
            print(f"Error: The file '{file_path}' was not found.")
        except Exception as e:
            print(f"An error occurred: {e}")
        return prompt 
            

    def clean_json_string(self, json_string):
        # Regular expression to match and remove ```json at the start and ``` at the end
        cleaned_json_string = re.sub(r'(^```json\s*|\s*```$)', '', json_string.strip(), flags=re.MULTILINE)
        return cleaned_json_string
            
    
    def text_prompt(self, user_query='', retrieved_documents='', previous_conversation='' ):
        # output = self.model.invoke([message]).content
        PROMPT = self.load_prompt()
        formated_prompt = PROMPT.format(user_query=user_query, retrieved_documents=retrieved_documents, previous_conversation=previous_conversation)
        model = GenerativeModel(GENERATIVE_MODEL, system_instruction=[''])
        responses = model.generate_content(
                    [formated_prompt],
                    generation_config=generation_config,
                    safety_settings=safety_settings,
                    stream=True)
        res = ""
        for i, response in enumerate(responses):
            res += response.text
                            
        output = self.clean_json_string(res) 
        return output
          