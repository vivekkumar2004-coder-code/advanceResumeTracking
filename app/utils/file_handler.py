import os
import uuid
from werkzeug.utils import secure_filename
import PyPDF2
import docx
from flask import current_app

ALLOWED_EXTENSIONS = {
    'pdf': ['pdf'],
    'doc': ['doc', 'docx'],
    'txt': ['txt']
}

def allowed_file(filename, allowed_types=None):
    """Check if the file extension is allowed"""
    if not filename or '.' not in filename:
        return False
    
    extension = filename.rsplit('.', 1)[1].lower()
    
    if allowed_types:
        return extension in allowed_types
    
    # Default: allow all supported types
    all_extensions = []
    for ext_list in ALLOWED_EXTENSIONS.values():
        all_extensions.extend(ext_list)
    
    return extension in all_extensions

def save_file(file_obj, category, upload_folder, is_text=False):
    """Save uploaded file or text content to the appropriate directory"""
    category_folder = os.path.join(upload_folder, category)
    os.makedirs(category_folder, exist_ok=True)
    
    if is_text:
        # Save text content as a .txt file
        filename = f"{str(uuid.uuid4())}.txt"
        filepath = os.path.join(category_folder, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(file_obj)
        return filename
    else:
        # Save uploaded file
        if file_obj and file_obj.filename:
            # Generate unique filename to avoid conflicts
            original_filename = secure_filename(file_obj.filename)
            name, ext = os.path.splitext(original_filename)
            filename = f"{name}_{str(uuid.uuid4())}{ext}"
            filepath = os.path.join(category_folder, filename)
            file_obj.save(filepath)
            return filename
    
    raise ValueError("Invalid file object or text content")

def get_file_type(filename):
    """Get file type from filename extension"""
    if '.' not in filename:
        return 'unknown'
    return filename.rsplit('.', 1)[1].lower()

def get_file_path(file_id, category):
    """Get full file path from file ID and category"""
    try:
        upload_folder = current_app.config['UPLOAD_FOLDER']
        category_folder = os.path.join(upload_folder, category)
        
        if not os.path.exists(category_folder):
            return None
        
        # Find file that starts with the file_id
        for filename in os.listdir(category_folder):
            if filename.startswith(file_id):
                return os.path.join(category_folder, filename)
        
        return None
    except Exception:
        return None

def extract_text_from_file(filepath, enhanced=True):
    """
    Extract text content from various file formats
    
    Args:
        filepath (str): Path to the file
        enhanced (bool): Whether to use enhanced parsing with entity extraction
        
    Returns:
        str or dict: Plain text if enhanced=False, structured data if enhanced=True
    """
    if not os.path.exists(filepath):
        return None
    
    try:
        file_extension = get_file_type(filepath)
        
        if enhanced and file_extension in ['pdf', 'docx', 'doc']:
            # Use enhanced parser for better structure extraction
            from .resume_parser import extract_resume_entities
            return extract_resume_entities(filepath)
        
        # Fall back to basic text extraction
        if file_extension == 'txt':
            with open(filepath, 'r', encoding='utf-8') as file:
                return file.read()
        
        elif file_extension == 'pdf':
            return extract_text_from_pdf(filepath)
        
        elif file_extension in ['doc', 'docx']:
            return extract_text_from_docx(filepath)
        
        else:
            return None
    
    except Exception as e:
        print(f"Error extracting text from {filepath}: {str(e)}")
        return None

def extract_text_from_file_simple(filepath):
    """
    Simple text extraction for backward compatibility
    """
    return extract_text_from_file(filepath, enhanced=False)

def extract_text_from_pdf(filepath):
    """Extract text from PDF file"""
    try:
        text = ""
        with open(filepath, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        print(f"Error reading PDF {filepath}: {str(e)}")
        return None

def extract_text_from_docx(filepath):
    """Extract text from DOCX file"""
    try:
        doc = docx.Document(filepath)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text.strip()
    except Exception as e:
        print(f"Error reading DOCX {filepath}: {str(e)}")
        return None

def cleanup_old_files(max_age_hours=24):
    """Clean up old uploaded files (optional utility)"""
    import time
    
    try:
        upload_folder = current_app.config['UPLOAD_FOLDER']
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        for category in ['resumes', 'job_descriptions']:
            category_folder = os.path.join(upload_folder, category)
            if os.path.exists(category_folder):
                for filename in os.listdir(category_folder):
                    filepath = os.path.join(category_folder, filename)
                    if os.path.isfile(filepath):
                        file_age = current_time - os.path.getmtime(filepath)
                        if file_age > max_age_seconds:
                            os.remove(filepath)
                            print(f"Removed old file: {filepath}")
    
    except Exception as e:
        print(f"Error cleaning up files: {str(e)}")


def save_text_file(text_content, category='resumes', upload_folder=None):
    """Save text content as a file - used by tests and text upload endpoints"""
    if upload_folder is None:
        upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
    
    try:
        # Create unique filename
        file_id = str(uuid.uuid4())
        filename = f"{file_id}.txt"
        
        # Create category directory
        category_folder = os.path.join(upload_folder, category)
        os.makedirs(category_folder, exist_ok=True)
        
        # Save file
        file_path = os.path.join(category_folder, filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(text_content)
        
        return {
            'success': True,
            'file_id': file_id,
            'filename': filename,
            'file_path': file_path
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }