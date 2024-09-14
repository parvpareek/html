from fastapi import FastAPI, HTTPException
from fastapi import File, UploadFile
from fastapi.responses import JSONResponse
import uuid
from pydantic import BaseModel
from typing import Optional
from utils.content_extraction import ContentExtractor
from utils.insert_graph import InsertDoc
from utils.question_generation import QuestionGen
from neo4j import GraphDatabase
import asyncio

import ngrok
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Create NEO4J auth constants from environment variables
NEO4J_URL = os.getenv("NEO4J_URL")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE", "neo4j") 
GOOGLE_API = os.getenv("GOOGLE_API")  # Default to "neo4j" if not specified
ngrok_token = os.getenv("NGROK_AUTH_TOKEN")
llmsherpa_api_url = "http://127.0.0.1:5010/api/parseDocument?renderFormat=all&useNewIndentParser=true"
# Validate that required environment variables are set

app = FastAPI()
qg = QuestionGen(GOOGLE_API)
neo = InsertDoc(
            NEO4J_URL,
            NEO4J_USER,
            NEO4J_PASSWORD,
            NEO4J_DATABASE
        )

extractor = ContentExtractor(llmsherpa_api_url)


ngrok.set_auth_token(ngrok_token)


if not all([NEO4J_URL, NEO4J_USER, NEO4J_PASSWORD]):
    raise ValueError("Missing required NEO4J environment variables")

if not ngrok_token:
    raise ValueError("NGROK_AUTH_TOKEN is not set in the environment variables")
# Set up ngrok
class UploadPdfRequest(BaseModel):
    file: UploadFile = File(...)

@app.post("/upload_pdf")
async def upload_pdf(request: UploadPdfRequest):
    try:
        file = request.file
        content = await file.read()

        # Check if the uploaded file is a PDF
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")

        # Generate a unique filename
        filename = f"{uuid.uuid4()}_{file.filename}"
        
        storage_dir = "pdfs"
        os.makedirs(storage_dir, exist_ok=True)
        
        # Construct the full file path
        file_path = os.path.join(storage_dir, filename)

        # Write the file to disk
        with open(file_path, "wb") as pdf_file:
            pdf_file.write(content)

        # Extract content from the saved PDF
        docs = extractor.extract_content(file_path)
        
        try:
            worked = neo.ingestDocumentNeo4j(docs, file_path)
            response = {
                "file_name": filename,
                "file_path": file_path,
                "message": "Graph creation successful",
                "status": "success"
            }
        except Exception as e:
            response = {
                "file_name": filename,
                "file_path": file_path,
                "message": f"Error during graph creation: {str(e)}",
                "status": "error"
            }
        
        if worked:
            return response
        else:
            return {
                "file_name": filename,
                "file_path": file_path,
                "message": "Graph creation failed",
                "status": "error"
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/get_section_content/{section_id}")
async def get_section_content(section_id: str):
    try:
        # Initialize Neo4j connection
        driver = GraphDatabase.driver(
            NEO4J_URL,
            auth=(NEO4J_USER, NEO4J_PASSWORD),
            database=NEO4J_DATABASE
        )
        
        # Query to fetch chunk sentences for the given section_id
        query = """
        MATCH (c:Chunk {key: $section_id})
        RETURN c.sentences AS sentences
        """

        with driver.session() as session:
            result = session.run(query, section_id=section_id)
            sentences = [record["sentences"] for record in result]

        if not sentences:
            raise HTTPException(status_code=404, detail="No content found for the given section_id")

        #return {"section_id": section_id, "content": sentences}
        
        sentences = " ".join(sentences)
        
        questions = qg.get_questions(sentences)
        
        # Prepare the response JSON
        response = {
            "section_id": section_id,
            "content": sentences[:10] + "...",
            "questions": questions
        }
        
        return JSONResponse(content=response)
        
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if driver:
            driver.close()
            
            
if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
            