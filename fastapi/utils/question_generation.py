class QuestionGen():
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        
    def get_questions(self, context):
        
        import google.generativeai as genai

        # Configure the Gemini API
        genai.configure(api_key=self.api_key)

        # Set up the model
        model = genai.GenerativeModel('gemini-pro')

        # Create the prompt
        prompt = f"""
        
        You are an experienced instructor.
        
        The following are the revised Bloom's skill levels and their explanation:

        3. Skill: Apply, Explanation: Carry out or use a procedure in a given situation
        4. Skill: Analyze, Explanation: Break material into foundational parts and determine how parts relate to one another and the overall structure or purpose
        5. Skill:Evaluate, Explanation: Make judgments based on criteria and standards
        6. Skill: Create, Explanation: Put elements together to form a coherent whole; reorganize into a new pattern or structure

        You are supposed to create 2 question corresponding to each level in revised Bloom's taxonomy for the topic. 
        These questions are created to evaluate students on a range of cognitive skills, from basic knowledge to critical thinking and problem-solving.

        """

        # Generate content
        response = model.generate_content(prompt)

        # Extract and return the generated questions
        questions = response.text.strip().split('\n')
        return questions