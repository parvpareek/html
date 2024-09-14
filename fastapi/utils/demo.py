import requests
import json

def make_post_request():
    url = "http://127.0.0.1:8000/create_graph"
    
    import os
    
    # Assuming the PDF file is in the same directory as this script
    pdf_file_path = "../dox/paper.pdf"
    file_name = pdf_file_path[:-10]
    # Create the payload
    payload = {
        "file_name": file_name,
        "file_path": pdf_file_path
    }
    # Convert payload to JSON
    json_payload = json.dumps(payload)

    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, json_payload,headers=headers)
        response.raise_for_status()
        print("Response:", response.json())
    except requests.exceptions.RequestException as e:
        print("Error occurred:", e)

if __name__ == "__main__":
    make_post_request()
