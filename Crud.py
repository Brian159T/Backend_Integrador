from flask import Blueprint, request
from db import mysql
from flask import Flask, jsonify, request

crud_bp = Blueprint('crud_bp', __name__)

@crud_bp.route('/api/usuarios', methods=['GET'])
def obtener_usuarios():
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM usuarios")
        filas = cursor.fetchall()
        columnas = [col[0] for col in cursor.description]
        usuarios = [dict(zip(columnas, fila)) for fila in filas]
        cursor.close()
        return jsonify({'usuarios': usuarios})
    except Exception as ex:
        return jsonify({'mensaje': 'Error al obtener usuarios', 'error': str(ex)}), 500



@crud_bp.route('/api/usuarios/<int:id>', methods=['DELETE'])
def eliminar_usuario(id):
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("DELETE FROM usuarios WHERE id_usuarios = %s", (id,))
        mysql.connection.commit()
        cursor.close()
        return jsonify({'mensaje': 'Usuario eliminado correctamente'})
    except Exception as ex:
        return jsonify({'mensaje': 'Error al eliminar usuario', 'error': str(ex)}), 500



@crud_bp.route('/api/usuarios/<int:id>', methods=['PUT'])
def actualizar_usuario(id):
    try:
        data = request.json
        correo = data.get('Correos')
        latitud = data.get('Latitudes')   # Cambiado aquí
        longitud = data.get('Longitudes') # Cambiado aquí
        celular = data.get('Celulares')
        nombre = data.get('Nombres')

        cursor = mysql.connection.cursor()
        cursor.execute("""
            UPDATE usuarios 
            SET Correos = %s, Longitudes = %s, Latitudes = %s, Celulares = %s, Nombres = %s 
            WHERE id_usuarios = %s
        """, (correo, longitud, latitud, celular, nombre, id))
        mysql.connection.commit()
        cursor.close()
        return jsonify({'mensaje': 'Usuario actualizado correctamente'})
    except Exception as ex:
        return jsonify({'mensaje': 'Error al actualizar usuario', 'error': str(ex)}), 500
    

@crud_bp.route('/api/registrar_usuario_admi', methods=['POST'])
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
            INSERT INTO usuarios (Roles, Contrasenas, Coordenadas, Celulares, Correos, Nombres, Longitudes, Latitudes)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        datos = (rol, password, celular, correo, nombre, longitud, latitud)  # Orden correcto
        cursor.execute(sql, datos)
        mysql.connection.commit()
        cursor.close()
        return jsonify({'mensaje': 'Cuenta creada correctamente ✅'})
    except Exception as ex:
        return jsonify({'mensaje': 'Error al registrar usuario ❌', 'error': str(ex)}), 500
    
@crud_bp.route('/api/alertas', methods=['GET'])
def obtener_alertas():
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM Alertas")
        filas = cursor.fetchall()
        columnas = [col[0] for col in cursor.description]
        alertas = [dict(zip(columnas, fila)) for fila in filas]
        cursor.close()
        return jsonify({'alertas': alertas})
    except Exception as ex:
        return jsonify({'mensaje': 'Error al obtener alertas', 'error': str(ex)}), 500

@crud_bp.route('/api/alertas/<int:id>', methods=['DELETE'])
def eliminar_alerta(id):
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("DELETE FROM Alertas WHERE id_alertas = %s", (id,))
        mysql.connection.commit()
        cursor.close()
        return jsonify({'mensaje': 'Alerta eliminada correctamente'})
    except Exception as ex:
        return jsonify({'mensaje': 'Error al eliminar alerta', 'error': str(ex)}), 500

@crud_bp.route('/api/alertas/<int:id>', methods=['PUT'])
def actualizar_alerta(id):
    try:
        data = request.json
        cuenca = data.get('Cuencas')
        rio = data.get('Rios')
        nivel = data.get('Niveles')
        condicion = data.get('Condiciones')
        pronostico = data.get('Pronosticos')
        periodo = data.get('Periodos')

        cursor = mysql.connection.cursor()
        cursor.execute("""
            UPDATE Alertas 
            SET Cuencas = %s, Rios = %s, Niveles = %s, Condiciones = %s, Pronosticos = %s, Periodos = %s
            WHERE id_alertas = %s
        """, (cuenca, rio, nivel, condicion, pronostico, periodo, id))
        mysql.connection.commit()
        cursor.close()
        return jsonify({'mensaje': 'Alerta actualizada correctamente'})
    except Exception as ex:
        return jsonify({'mensaje': 'Error al actualizar alerta', 'error': str(ex)}), 500
