from flask import Blueprint, jsonify
import os
import PyPDF2
import re
import json

lectura_bp = Blueprint('lectura_bp', __name__)

def limpiar_numero(valor):
    if not valor:
        return None
    return float(valor.replace(".", "").replace(",", ".").replace(" ", "").replace("↑", "").replace("↓", ""))

def extraer_datos_tabla(texto):
    rios = []
    filas = []
    acumulador = []

    # Dividir en líneas limpias
    lineas = [l.strip() for l in texto.splitlines() if l.strip()]

    for linea in lineas:
        # Heurística: si empieza con "CUENCA" o una palabra mayúscula → nueva fila
        if re.match(r"^[A-ZÁÉÍÓÚÑÜ]{3,}", linea):
            if acumulador:
                filas.append(" ".join(acumulador))
                acumulador = []
        acumulador.append(linea)
    if acumulador:
        filas.append(" ".join(acumulador))

    patron = re.compile(
        r"(?P<cuenca>[A-ZÁÉÍÓÚÑÜ ]+)\s+"
        r"(?P<estacion>[A-Za-zÁÉÍÓÚÑüÜ0-9 ]+)\s+"
        r"(?P<rio>[A-Za-zÁÉÍÓÚÑüÜ ]+)\s+"
        r"(?P<poblados>[A-Za-zÁÉÍÓÚÑüÜ ,]+)\s+"
        r"(?P<alerta>Amarilla|Naranja|Roja)\s+"
        r"(?P<pronostico>Ascensos|Descensos|Estable)\s+"
        r"(?P<falta>[\d.,↑↓ ]+)\s+"
        r"(?P<caudal>[\d.,↑↓ ]+)\s+"
        r"(?P<volumen>[\d.,↑↓ ]+)\s+"
        r"(?P<periodo>.+)$",
        re.IGNORECASE
    )

    for fila in filas:
        match = patron.search(fila)
        if match:
            rios.append({
                "Cuenca": match.group("cuenca").strip(),
                "Estacion": match.group("estacion").strip(),
                "Rio": match.group("rio").strip(),
                "Poblados": match.group("poblados").strip(),
                "Alerta considerada": match.group("alerta").capitalize(),
                "Pronostico": match.group("pronostico").capitalize(),
                "Para el desborde falta (m3/s)": limpiar_numero(match.group("falta")),
                "Caudal actual (m3/s)": limpiar_numero(match.group("caudal")),
                "Volumen de alerta roja (m3/s)": limpiar_numero(match.group("volumen")),
                "Periodo de ocurrencia": match.group("periodo").strip()
            })

    return rios


@lectura_bp.route('/api/lectura', methods=['POST'])
def lectura_pdf():
    carpeta = r"D:\PDF_SENAMHI"
    resultados = {}
    contador = 1

    for archivo in os.listdir(carpeta):
        if archivo.lower().endswith(".pdf"):
            pdf_path = os.path.join(carpeta, archivo)

            with open(pdf_path, "rb") as pdf_file_obj:
                pdf_reader = PyPDF2.PdfReader(pdf_file_obj)
                texto_total = ""

                for page_num in range(len(pdf_reader.pages)):
                    page_obj = pdf_reader.pages[page_num]
                    text = page_obj.extract_text()
                    if text:
                        texto_total += text + "\n"

            rios = extraer_datos_tabla(texto_total)

            resultados[f"archivo{contador}"] = {
                "nombre": archivo,
                "rios": rios
            }
            contador += 1

    print(json.dumps(resultados, indent=4, ensure_ascii=False))
    return jsonify(resultados)