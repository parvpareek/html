import google.generativeai as genai
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Configure the Google API
genai.configure(api_key=os.getenv('GOOGLE_API'))

class EmbeddingModel():
    
    def __init__(self, api_key: str):
        """
        Initialize the EmbeddingModel with the given API key.
        
        Args:
        api_key (str): The Google API key for authentication.
        """
        self.api_key = api_key
        genai.configure(api_key=self.api_key)
        
        
    def embed_text(self, text: str) -> list:
        """
        Embed the given text using Google's embedding model.
        
        Args:
        text (str): The text to be embedded.
        
        Returns:
        list: The embedding vector.
        """
        # Set up the embedding model
        model = 'models/embedding-001'
        
        try:
            embedding = genai.embed_content(model=model,
                                            content=text,
                                            task_type="retrieval_document")
            return embedding['embedding']
        except Exception as e:
            print(f"Error occurred while embedding text: {e}")
            return []
