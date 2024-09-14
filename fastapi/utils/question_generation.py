class QuestionGen():
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        
    def get_questions(context):
        
        import google.generativeai as genai

        # Configure the Gemini API
        genai.configure(api_key=self.api_key)

        # Set up the model
        model = genai.GenerativeModel('gemini-pro')

        # Create the prompt
        prompt = f"""
        Given the following context, generate 3 relevant questions:

        Context:
        {context}

        Please provide 3 questions that can be answered based on the information in the context.
        """

        # Generate content
        response = model.generate_content(prompt)

        # Extract and return the generated questions
        questions = response.text.strip().split('\n')
        return questions[:3]  # Ensure we return exactly 3 questions