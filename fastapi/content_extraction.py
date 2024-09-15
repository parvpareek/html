import os
from llmsherpa.readers import LayoutPDFReader # type: ignore
import typing

class ContentExtractor():
 
    def __init__(self, llmsherpa_api):
        self.api_url = llmsherpa_api
        
    def extract_content(self, file_path):
        
        pdf_reader = LayoutPDFReader(self.api_url)
        doc = pdf_reader.read_pdf(file_path)
        
        return doc
        
        
    
    
    

    
    
