# from pypdf import PdfReader

# def read(file_path: str)->str:
#     reader = PdfReader(file_path)

#     full_text = ""
#     for page in reader.pages:
#         text = page.extract_text()
#         if text:
#             full_text += text + "\n"

#     return full_text

from pypdf import PdfReader

def read(file_path: str) -> str:
    try:
        reader = PdfReader(file_path, strict=False)
        full_text = ""
        for page in reader.pages:
            text = page.extract_text()
            if text:
                full_text += text + "\n"
        return full_text.strip()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return ""  # Return empty string if file fails
