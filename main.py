from flask import Flask, jsonify, request
from flask_cors import CORS
from db import mysql
from Control_usuario import usuario_bp
from Crud import crud_bp
from Graficos import graficos_bp
from Mensajes_twilio import mensajes_bp
from Mapas import mapasbp
from MapasG import mapasgbp

app = Flask(__name__)
CORS(app)


app.secret_key = 'miclave123'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'satdb'

mysql.init_app(app)  


app.register_blueprint(usuario_bp)
app.register_blueprint(crud_bp)
app.register_blueprint(graficos_bp)
app.register_blueprint(mensajes_bp)
app.register_blueprint(mapasbp)
app.register_blueprint(mapasgbp)


@app.route('/api/registrar_usuario', methods=['POST'])
def registrar_usuario():
    data = request.get_json()
    correo = data.get('correo')
    password = data.get('password')
    coordenadas = data.get('coordenadas')
    celular = data.get('celular')
    nombre = data.get('nombre')
    rol = data.get('rol', 'Usuario')  

    try:
        cursor = mysql.connection.cursor()
        sql = """
            INSERT INTO usuarios (Roles, Contrasenas, Coordenadas, Celulares, Correos, Nombres)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        datos = (rol, password, coordenadas, celular, correo, nombre)
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



if __name__ == '__main__':
    app.run(debug=True)