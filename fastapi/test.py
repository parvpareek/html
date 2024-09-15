import requests
import io

# URL of the /upload_pdf endpoint
url = "http://127.0.0.1:8000/upload_pdf"

# Path to your PDF file
pdf_file_path = "pdfs/ch5.pdf"

# Open the PDF file in binary mode
with open(pdf_file_path, "rb") as file:
    # Create a file-like object from the binary data
    pdf_file = io.BytesIO(file.read())

# Prepare the files dictionary for the request
files = {"file": ("file.pdf", pdf_file, "application/pdf")}

# Send the POST request
response = requests.post(url, files=files)

# Check the response
if response.status_code == 200:
    print("PDF uploaded successfully!")
    print("Response:", response.json())
else:
    print("Failed to upload PDF.")
    print("Status code:", response.status_code)
    print("Response:", response.text)
