from docx import Document
import os
from docx.shared import Pt
from docx.oxml.ns import qn

def set_times_new_roman(run):
    run.font.name = "Times New Roman"
    run._element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")

def run(data: dict, worker_id):
    output_dir = "generated_files"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, data['generated_file_name'])

    doc = Document(data['template_file_name'])

    for paragraph in doc.paragraphs:
        text = paragraph.text

        for key, val in data['replace'].items():
            text = text.replace(key, val)

        for r in paragraph.runs:
            r.clear()

        new_run = paragraph.add_run(text)
        set_times_new_roman(new_run)

    # for table in doc.tables:
    #     for row in table.rows:
    #         for cell in row.cells:
    #             for paragraph in cell.paragraphs:
    #                 text = paragraph.text

    #                 for key, val in data['replace'].items():
    #                     text = text.replace(key, val)

    #                 for r in paragraph.runs:
    #                     r.clear()

    #                 new_run = paragraph.add_run(text)
    #                 set_times_new_roman(new_run)

    doc.save(output_path)
