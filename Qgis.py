from flask import Blueprint, jsonify, request, send_file
import subprocess
import os
import datetime

q_gis_bp = Blueprint('q_gis_bp', __name__)

# ------------------------------------------------
# CONFIGURACIÓN
# ------------------------------------------------
QGIS_PYTHON = r"C:\Program Files\QGIS 3.40.11\apps\Python312\python.exe"
QGIS_SCRIPTS_DIR = r"C:\laragon\www\Proyecto Integrador Angular-Flask\Backend"
TEMP_DIR = os.path.join(QGIS_SCRIPTS_DIR, "temp")
LOG_FILE = os.path.join(TEMP_DIR, "qgis_log.txt")
os.makedirs(TEMP_DIR, exist_ok=True)


# ------------------------------------------------
# Función auxiliar: ejecutar script QGIS
# ------------------------------------------------
def ejecutar_qgis(script_filename):
    """Ejecuta un script QGIS usando Python de QGIS y devuelve stdout/stderr detallado."""
    script_path = os.path.join(QGIS_SCRIPTS_DIR, script_filename)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if not os.path.exists(script_path):
        msg = f"[{timestamp}] [ERROR] Script no encontrado: {script_path}\n"
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(msg)
        return {
            "stdout": "",
            "stderr": msg,
            "returncode": 1
        }

    try:
        result = subprocess.run(
            [QGIS_PYTHON, script_path],
            capture_output=True,
            text=True,
            errors="replace"
        )

        # Registrar ejecución en log
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"\n[{timestamp}] --- EJECUCIÓN DE {script_filename} ---\n")
            f.write(f"RETURNCODE: {result.returncode}\n")
            f.write("STDOUT:\n" + result.stdout + "\n")
            f.write("STDERR:\n" + result.stderr + "\n")
            f.write("--------------------------------------------------------\n")

        return {
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "returncode": result.returncode
        }

    except Exception as e:
        error_msg = f"[{timestamp}] [ERROR] Error al ejecutar subprocess: {str(e)}\n"
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(error_msg)
        return {
            "stdout": "",
            "stderr": error_msg,
            "returncode": 1
        }


# ------------------------------------------------
# API: Verificar ejecución (demo)
# ------------------------------------------------
@q_gis_bp.route('/api/qgis_demo', methods=['GET'])
def ejecutar_demo():
    """
    Ejecuta qgis_visualizar_shp.py y devuelve resultados JSON detallados.
    """
    script_name = "qgis_visualizar_shp.py"
    resultado = ejecutar_qgis(script_name)
    output_img = os.path.join(TEMP_DIR, "cuenca_taquina.png")

    response = {
        "mensaje": "Script ejecutado correctamente" if resultado["returncode"] == 0 else "Error al ejecutar el script",
        "stdout": resultado["stdout"].splitlines(),
        "stderr": resultado["stderr"].splitlines(),
        "imagen_generada": os.path.exists(output_img),
        "ruta_imagen": output_img if os.path.exists(output_img) else "No generada",
        "log": LOG_FILE,
        "returncode": resultado["returncode"]
    }

    status_code = 200 if resultado["returncode"] == 0 else 500
    return jsonify(response), status_code


# ------------------------------------------------
# API: Generar mapa QGIS y devolver imagen
# ------------------------------------------------
@q_gis_bp.route('/api/visualizar_shp', methods=['GET'])
def visualizar_shp():
    """
    Genera y devuelve la imagen PNG del mapa QGIS (DEM + cuenca + red).
    Si ocurre un error, devuelve JSON con información detallada.
    """
    script_name = "qgis_visualizar_shp.py"
    output_img = os.path.join(TEMP_DIR, "cuenca_taquina.png")

    resultado = ejecutar_qgis(script_name)

    # Si el script falló
    if resultado["returncode"] != 0:
        return jsonify({
            "mensaje": "Error al generar mapa QGIS",
            "stdout": resultado["stdout"].splitlines(),
            "stderr": resultado["stderr"].splitlines(),
            "ruta_log": LOG_FILE
        }), 500

    # Si no se generó la imagen
    if not os.path.exists(output_img):
        return jsonify({
            "mensaje": "La imagen no se generó",
            "stdout": resultado["stdout"].splitlines(),
            "stderr": resultado["stderr"].splitlines(),
            "ruta_log": LOG_FILE
        }), 500

    # Éxito: devolver imagen
    return send_file(output_img, mimetype="image/png")
