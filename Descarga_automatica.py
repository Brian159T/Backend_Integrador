import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from flask import Blueprint, jsonify, request
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import unicodedata

# Definir Blueprint
Descargas_bp = Blueprint('descargas_bp', __name__)

# Scheduler global
scheduler = None

# Función para normalizar (quita acentos, convierte a minúsculas)
def normalizar(texto: str) -> str:
    return ''.join(
        c for c in unicodedata.normalize('NFD', texto.lower())
        if unicodedata.category(c) != 'Mn'
    )

# Función auxiliar (descarga PDFs filtrados)
def descargar_pdfs_desde(url, carpeta_destino=r"D:\PDF_SENAMHI"):
    try:
        if not os.path.exists(carpeta_destino):
            os.makedirs(carpeta_destino, exist_ok=True)
            print(f"[{datetime.now()}] Carpeta creada: {carpeta_destino}")
        else:
            print(f"[{datetime.now()}] Carpeta ya existe: {carpeta_destino}")
    except Exception as e:
        print(f"[{datetime.now()}] ❌ Error al crear la carpeta {carpeta_destino}: {e}")
        return {
            "total": 0,
            "descargados": [],
            "omitidos": [],
            "errores": [{"carpeta": carpeta_destino, "error": str(e)}]
        }

    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    # ✅ Buscar todos los links PDF
    enlaces_pdf = [a.get("href") for a in soup.find_all("a", href=True) if a["href"].lower().endswith(".pdf")]

    descargados, omitidos, errores = [], [], []

    for enlace in enlaces_pdf:
        enlace_completo = urljoin(url, enlace)
        nombre_archivo = os.path.basename(enlace_completo)

        # Normalizar nombre (minúsculas y sin tildes)
        nombre_norm = normalizar(nombre_archivo)

        #  Filtro: debe contener estas palabras
        if not all(palabra in nombre_norm for palabra in ["planilla", "pronostico", "hidrologico", "senamhi"]):
            continue

        ruta_guardado = os.path.join(carpeta_destino, nombre_archivo)

        # Si ya existe, lo omitimos
        if os.path.exists(ruta_guardado):
            omitidos.append(nombre_archivo)
            continue

        try:
            r = requests.get(enlace_completo, timeout=15)
            r.raise_for_status()
            with open(ruta_guardado, "wb") as f:
                f.write(r.content)
            descargados.append(nombre_archivo)
        except Exception as e:
            errores.append({"archivo": nombre_archivo, "error": str(e)})

    print(f"[{datetime.now()}] Descarga ejecutada → Total encontrados: {len(enlaces_pdf)}, "
          f"Filtrados: {len(descargados)+len(omitidos)}, Nuevos: {len(descargados)}, "
          f"Omitidos: {len(omitidos)}")

    return {"total": len(enlaces_pdf), "descargados": descargados, "omitidos": omitidos, "errores": errores}

# Endpoint manual (POST)
@Descargas_bp.route('/api/descargar_pdfs', methods=['POST'])
def api_descargar_pdfs():
    data = request.get_json()
    url = data.get("url", "https://senamhi.gob.bo/index.php/repositorio_pronostico_hidrologico")
    carpeta = data.get("carpeta", r"D:\PDF_SENAMHI")
    resultado = descargar_pdfs_desde(url, carpeta)
    return jsonify(resultado)

# 🔹 Scheduler para ejecutar cada 5 min (y al inicio)
def iniciar_scheduler(app):
    global scheduler
    if scheduler is None:
        scheduler = BackgroundScheduler()
        scheduler.add_job(
            func=descargar_pdfs_desde,
            trigger="interval",
            minutes=5,
            next_run_time=datetime.now(),
            args=["https://senamhi.gob.bo/index.php/repositorio_pronostico_hidrologico", r"D:\PDF_SENAMHI"]
        )
        scheduler.start()
        print("✅ Scheduler iniciado")

        @app.teardown_appcontext
        def shutdown_scheduler(exception=None):
            global scheduler
            if scheduler and scheduler.running:
                scheduler.shutdown()
                print("✅ Scheduler detenido")
            else:
                print("⚠ Scheduler no estaba corriendo")
