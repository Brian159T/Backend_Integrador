from flask import Flask, jsonify, request
from flask_cors import CORS
from db import mysql
from Control_usuario import usuario_bp
from Crud import crud_bp
from Graficos import graficos_bp
from Mensajes_twilio import mensajes_bp
from Mapas import mapasbp
from MapasG import mapasgbp
from Descarga_automatica import Descargas_bp, iniciar_scheduler, descargar_pdfs_desde
import threading
from datetime import datetime
from Lectura import lectura_bp

app = Flask(__name__)
CORS(app)

app.secret_key = 'miclave123'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'satdb'

mysql.init_app(app)

# Registrar blueprints
app.register_blueprint(usuario_bp)
app.register_blueprint(crud_bp)
app.register_blueprint(graficos_bp)
app.register_blueprint(mensajes_bp)
app.register_blueprint(mapasbp)
app.register_blueprint(mapasgbp)
app.register_blueprint(Descargas_bp)
app.register_blueprint(lectura_bp)

# Rutas API
@app.route('/api/registrar_usuario', methods=['POST'])
def registrar_usuario():
    data = request.get_json()
    correo = data.get('correo')
    password = data.get('password')
    latitud = data.get('latitud')
    longitud = data.get('longitud')
    celular = data.get('celular')
    nombre = data.get('nombre')
    rol = data.get('rol', 'Usuario')

    try:
        cursor = mysql.connection.cursor()
        sql = """
            INSERT INTO usuarios (Roles, Contrasenas, Celulares, Correos, Nombres, Longitudes, Latitudes)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        datos = (rol, password, celular, correo, nombre, longitud, latitud)
        cursor.execute(sql, datos)
        mysql.connection.commit()
        cursor.close()
        return jsonify({'mensaje': 'Cuenta creada correctamente ✅'})
    except Exception as ex:
        return jsonify({'mensaje': 'Error al registrar usuario ❌', 'error': str(ex)}), 500

@app.route('/api/registrar_alerta', methods=['POST'])
def registrar_alerta():
    data = request.get_json()
    cuenca = data.get('cuenca')
    rio = data.get('rio')
    nivel = data.get('nivel')
    condicion = data.get('condicion')
    pronostico = data.get('pronostico')
    periodo = data.get('periodo')

    try:
        cursor = mysql.connection.cursor()
        sql = """
            INSERT INTO Alertas (Cuencas, Rios, Niveles, Condiciones, Pronosticos, Periodos)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        datos = (cuenca, rio, nivel, condicion, pronostico, periodo)
        cursor.execute(sql, datos)
        mysql.connection.commit()
        cursor.close()
        return jsonify({'mensaje': 'Alerta Guardada correctamente ✅'})
    except Exception as ex:
        return jsonify({'mensaje': 'Error al Guardar Alerta ❌', 'error': str(ex)}), 500

@app.route('/')
def index():
    return jsonify({'mensaje': 'API HidroAlert funcionando ✅'})

# 🔹 Función para ejecutar la descarga inicial en segundo plano
def descarga_inicial():
    try:
        print(f"[{datetime.now()}] 🚀 Ejecutando descarga inicial en segundo plano...")
        descargar_pdfs_desde(
            "https://senamhi.gob.bo/index.php/repositorio_pronostico_hidrologico",
            r"D:\PDF_SENAMHI"
        )
    except Exception as e:
        print(f"[{datetime.now()}] ❌ Error en la descarga inicial: {e}")

if __name__ == "__main__":
    # Iniciar scheduler
    iniciar_scheduler(app)

    # Lanzar descarga inicial en hilo separado
    threading.Thread(target=descarga_inicial, daemon=True).start()

    # Ejecutar Flask
    app.run(debug=True, use_reloader=False)
