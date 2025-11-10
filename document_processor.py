import os
from PyPDF2 import PdfReader
from docx import Document
import pandas as pd

def extract_text_from_file(file_path: str) -> str:
    ext = os.path.splitext(file_path)[1].lower()
    
    try:
        if ext == '.pdf':
            return extract_text_from_pdf(file_path)
        elif ext == '.docx':
            return extract_text_from_docx(file_path)
        elif ext == '.txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if not content.strip():
                    raise ValueError("Text file is empty")
                return content
        elif ext in ['.xls', '.xlsx']:
            return extract_text_from_excel(file_path)
        elif ext == '.csv':
            return extract_text_from_csv(file_path)
        else:
            raise ValueError(f"Unsupported file format: {ext}. Please use PDF, DOCX, TXT, XLS, XLSX, or CSV.")
    except Exception as e:
        raise Exception(f"Error reading document: {str(e)}")

def extract_text_from_pdf(file_path: str) -> str:
    try:
        reader = PdfReader(file_path)
        if len(reader.pages) == 0:
            raise ValueError("PDF file has no pages")
        
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        
        if not text.strip():
            raise ValueError("Could not extract text from PDF. The file may be image-based or corrupted.")
        
        return text
    except Exception as e:
        raise Exception(f"Error reading PDF: {str(e)}")

def extract_text_from_docx(file_path: str) -> str:
    try:
        doc = Document(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        
        if not text.strip():
            raise ValueError("DOCX file appears to be empty")
        
        return text
    except Exception as e:
        raise Exception(f"Error reading DOCX: {str(e)}")

def extract_text_from_excel(file_path: str) -> str:
    try:
        xls = pd.ExcelFile(file_path)
        text = ""
        
        for sheet_name in xls.sheet_names:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            text += f"\n=== Sheet: {sheet_name} ===\n"
            text += df.to_string(index=False, na_rep='')
            text += "\n\n"
        
        if not text.strip():
            raise ValueError("Excel file appears to be empty")
        
        return text
    except Exception as e:
        raise Exception(f"Error reading Excel file: {str(e)}")

def extract_text_from_csv(file_path: str) -> str:
    try:
        df = pd.read_csv(file_path)
        text = df.to_string(index=False, na_rep='')
        
        if not text.strip():
            raise ValueError("CSV file appears to be empty")
        
        return text
    except Exception as e:
        raise Exception(f"Error reading CSV file: {str(e)}")
