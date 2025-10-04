from flask import Blueprint, jsonify
import os
import camelot

lectura_bp = Blueprint('lectura_bp', __name__)

@lectura_bp.route('/api/lectura', methods=['POST'])
def lectura_pdf():
    carpeta = r"D:\PDF_SENAMHI"
    resultados = {}
    contador = 1

    for archivo in os.listdir(carpeta):
        if archivo.lower().endswith(".pdf"):
            pdf_path = os.path.join(carpeta, archivo)

            try:
                print(f"\n📄 Procesando: {archivo}")
                
                # ⚡ Solo leer la primera página para depurar
                tablas = camelot.read_pdf(pdf_path, pages="1", flavor="lattice")

                print(f"   Tablas encontradas en la página 1: {tablas.n}")

                tablas_json = []
                for i, t in enumerate(tablas):
                    print(f"\n--- Tabla {i+1} del PDF {archivo} ---")
                    print(t.df)  # 👈 Esto imprime la tabla en consola

                    df = t.df
                    columnas = df.iloc[0].tolist()  # primera fila como encabezado
                    datos = df.iloc[1:].to_dict(orient="records")
                    tablas_json.append({
                        "tabla": i + 1,
                        "columnas": columnas,
                        "datos": datos
                    })

                resultados[f"archivo{contador}"] = {
                    "nombre": archivo,
                    "tablas": tablas_json
                }
                contador += 1

            except Exception as e:
                print(f"⚠️ Error leyendo {archivo}: {e}")
                resultados[f"archivo{contador}"] = {
                    "nombre": archivo,
                    "error": str(e)
                }
                contador += 1

    return jsonify(resultados)
