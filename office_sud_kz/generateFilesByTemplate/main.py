from docx import Document
import os

def run(data: dict, worker_id):
    output_dir = "generated_files"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, data['generated_file_name'])

    doc = Document(data['template_file_name'])

    for paragraph in doc.paragraphs:
        for key, val in data['replace'].items():
            if key in paragraph.text:
                paragraph.text = paragraph.text.replace(key, val)

    # for table in doc.tables:
    #     for row in table.rows:
    #         for cell in row.cells:
    #             for key, val in replacements.items():
    #                 if key in cell.text:
    #                     cell.text = cell.text.replace(key, val)

    doc.save(output_path)
