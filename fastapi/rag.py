from neo4j import GraphDatabase
import os
from google.generativeai import GenerativeModel, configure
from google.ai import generativelanguage as glm

class RAGPipeline:
    def __init__(self, neo4j_url, neo4j_user, neo4j_password, neo4j_database):
        self.driver = GraphDatabase.driver(
            neo4j_url,
            auth=(neo4j_user, neo4j_password),
            database=neo4j_database
        )
        
        configure(api_key=os.getenv('GOOGLE_API_KEY'))
        self.llm = GenerativeModel('gemini-pro')

    def process(self, question: str, answer: str):
        # Use Gemini to generate an answer
        generated_answer = self.generate_answer(question)

        # Compare provided answer with generated answer using Gemini
        comparison_prompt = f"""
        Compare the following two answers to the question: "{question}"

        Provided Answer: {answer}

        Generated Answer: {generated_answer}

        Rate the provided answer on a scale of 1 to 5, where:
        5: The provided answer is very good and contains almost all things that the generated answer contains.
        1: The provided answer is terrible and doesn't contain anything mentioned in the generated answer.

        Please provide only the numeric rating (1-5) as your response.
        """

        score = self.compare_answers(comparison_prompt)

        return {
            "question": question,
            "provided_answer": answer,
            "generated_answer": generated_answer,
            "answer_score": score
        }

    def generate_answer(self, question):
        prompt = f"Question: {question}\nAnswer: "
        response = self.llm.generate_content(prompt)
        return response.text

    def compare_answers(self, prompt):
        response = self.llm.generate_content(prompt)
        try:
            score = int(response.text.strip())
            return score if 1 <= score <= 5 else 0
        except ValueError:
            return 0  # Default score if parsing fails

    def __del__(self):
        if self.driver:
            self.driver.close()
