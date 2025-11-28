"""
نظام معالجة الملفات (PDF, DOCX, TXT)
"""

import PyPDF2
from docx import Document
from typing import Optional
import os

class FileProcessor:
    def __init__(self):
        """تهيئة معالج الملفات"""
        self.supported_types = ['.pdf', '.docx', '.txt', '.md']
        
    def process_file(self, file_path: str) -> Optional[str]:
        """معالجة ملف وإرجاع محتواه"""
        
        if not os.path.exists(file_path):
            return None
            
        file_ext = os.path.splitext(file_path)[1].lower()
        
        try:
            if file_ext == '.pdf':
                return self.read_pdf(file_path)
            elif file_ext == '.docx':
                return self.read_docx(file_path)
            elif file_ext in ['.txt', '.md']:
                return self.read_text(file_path)
            else:
                return f"نوع الملف غير مدعوم: {file_ext}"
                
        except Exception as e:
            return f"خطأ في قراءة الملف: {str(e)}"
            
    def read_pdf(self, file_path: str) -> str:
        """قراءة ملف PDF"""
        text = ""
        
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                num_pages = len(pdf_reader.pages)
                
                for page_num in range(num_pages):
                    page = pdf_reader.pages[page_num]
                    text += page.extract_text() + "\n\n"
                    
            return text.strip()
            
        except Exception as e:
            return f"خطأ في قراءة PDF: {str(e)}"
            
    def read_docx(self, file_path: str) -> str:
        """قراءة ملف DOCX"""
        try:
            doc = Document(file_path)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            return text.strip()
            
        except Exception as e:
            return f"خطأ في قراءة DOCX: {str(e)}"
            
    def read_text(self, file_path: str) -> str:
        """قراءة ملف نصي"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read().strip()
                
        except Exception as e:
            return f"خطأ في قراءة الملف النصي: {str(e)}"
            
    def chunk_text(self, text: str, chunk_size: int = 2000) -> list:
        """تقسيم النص الطويل إلى أجزاء"""
        words = text.split()
        chunks = []
        current_chunk = []
        current_length = 0
        
        for word in words:
            current_chunk.append(word)
            current_length += len(word) + 1
            
            if current_length >= chunk_size:
                chunks.append(" ".join(current_chunk))
                current_chunk = []
                current_length = 0
                
        if current_chunk:
            chunks.append(" ".join(current_chunk))
            
        return chunks
