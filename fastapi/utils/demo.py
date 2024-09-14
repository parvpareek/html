import requests

def get_section_content(section_id):
    url = f"http://localhost:8000/get_section_content/{section_id}"
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

# Example usage
section_id = "827a4c4b88b8117e7d9f8b38e3b1f54e|121|4f7c5b74b16fc695333aa8aac7d5f6d0"
result = get_section_content(section_id)
if result:
    print(result)
