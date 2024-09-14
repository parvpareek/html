from fastapi import FastAPI, HTTPException
from fastapi import File, UploadFile
import uuid
from pydantic import BaseModel
from typing import Optional
from utils.content_extraction import ContentExtractor
from utils.insert_graph import InsertDoc
from utils.question_generation import QuestionGen
from neo4j import GraphDatabase


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

if not all([NEO4J_URL, NEO4J_USER, NEO4J_PASSWORD]):
    raise ValueError("Missing required NEO4J environment variables")

class GraphRequest(BaseModel):
    file: UploadFile

@app.post("/upload_pdf")
async def upload_pdf(request: GraphRequest):
    try:
        file = request.file
        # Check if the uploaded file is a PDF
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")

        # Generate a unique filename
        filename = file.filename
        
        storage_dir = "pdfs"
        os.makedirs(storage_dir, exist_ok=True)
        
        # Unique filename for the uploaded file
        file_location = os.path.join(storage_dir, filename)
        with open(file_location, "wb") as file:
            content = await pdf_file.read()
            file.write(content)


        # Construct the full file path
        file_path = os.path.join(upload_dir, unique_filename)

        docs = extractor.extract_content(file_path)
        
        try:
            worked = neo.ingestDocumentNeo4j(docs, request.file_path)
            response = {
                "file_name": request.file_name,
                "file_path": request.file_path,
                "message": "Graph creation successful",
                "status": "success"
            }
        except Exception as e:
            response = {
                "file_name": request.file_name,
                "file_path": request.file_path,
                "message": f"Error during graph creation: {str(e)}",
                "status": "error"
            }
        
        if worked:
            return response
        else:
            return {
                "file_name": request.file_name,
                "file_path": request.file_path,
                "message": f"Error during graph creation: {str(e)}",
                "status": "error"
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/get_section_content/{section_id}")
async def get_section_content(section_id: str, request):
    try:
        # Initialize Neo4j connection
        driver = GraphDatabase.driver(
            NEO4J_URL,
            auth=(NEO4J_USER, NEO4J_PASSWORD),
            database=NEO4J_DATABASE
        )

        # Query to fetch chunk sentences for the given section_id
        query = """
        MATCH (s:Section {key: $section_id})<-[:HAS_PARENT]-(c:Chunk)
        RETURN c.sentences AS sentences
        """

        with driver.session() as session:
            result = session.run(query, section_id=section_id)
            sentences = [record["sentences"] for record in result]

        if not sentences:
            raise HTTPException(status_code=404, detail="No content found for the given section_id")

        #return {"section_id": section_id, "content": sentences}
        
        sentences = " ".join(sentences)
        
        
        
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if driver:
            driver.close()
