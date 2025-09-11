from flask import Blueprint, request, jsonify
import PyPDF2

lectura_bp = Blueprint('lectura_bp', __name__)

@lectura_bp.route('/api/lectura', methods=['POST'])
def lectura_pdf():
    pdf_path = r'D:\PDF_SENAMHI\prueba\pronostico.pdf'
    pdf_file_obj = open(pdf_path, 'rb')
    pdf_reader = PyPDF2.PdfReader(pdf_file_obj)

    num_pages = len(pdf_reader.pages)
    print(f"Total páginas: {num_pages}")

    texto_total = ""
    for page_num in range(num_pages):
        page_obj = pdf_reader.pages[page_num]
        text = page_obj.extract_text()
        print(text)
        texto_total += text if text else ""

    pdf_file_obj.close()
    return jsonify({"pages": num_pages, "texto": texto_total})
    

    

