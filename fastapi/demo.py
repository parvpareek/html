import requests

# Define the base URL
base_url = "http://127.0.0.1:8000"

# Define the section_id (you may want to make this dynamic or get it from user input)
section_id = "64f5c3fd32b5a1daa62cb733a2cb20bc|29|2bfb5a4a7336673f8daeff59cbf16cf6"


# Send GET request to get_section_content endpoint
get_content_url = f"{base_url}/get_section_content/{section_id}"
content_response = requests.get(get_content_url)

if content_response.status_code == 200:
    content_data = content_response.json()
    questions = content_data.get("questions", [])
    
    if questions:
        # Get the first question
        first_question = questions[2]
        
        # Define a sample answer (you may want to get this from user input)
        answer = "This is a sample answer to the first question."
        
        # Prepare payload for rag_pipeline
        rag_url = f"{base_url}/rag_pipeline"
        payload = {
            "question": first_question,
            "answer": answer
        }
        
        # Send POST request to rag_pipeline endpoint
        rag_response = requests.post(rag_url, json=payload)
        
        if rag_response.status_code == 200:
            print(rag_response.json())
        else:
            print(f"Error in rag_pipeline: {rag_response.status_code}")
    else:
        print("No questions found in the response.")
else:
    print(f"Error getting section content: {content_response.status_code}")
