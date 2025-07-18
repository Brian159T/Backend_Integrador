from twilio.rest import Client
from flask import Blueprint, Response
from db import mysql

from flask import request, jsonify

mensajes_bp = Blueprint('mensajes_bp', __name__)



@mensajes_bp.route('/api/alertar', methods=['POST'])
def alertar_usuario():
    try:
        data = request.get_json()
        numero = data['numero']
        alerta = data['alerta']

        # Validación rápida del número
        if not numero.startswith('+'):
            return jsonify({'mensaje': 'Número inválido. Debe empezar con + (ej: +591...)'}), 400

        # Formar el mensaje de alerta
        texto = f"""
🚨 *Alerta Hidrológica* 🚨
Cuenca: {alerta['Cuencas']}
Río: {alerta['Rios']}
Caudal: {alerta['Niveles']} m3/s
Condición: {alerta['Condiciones']}
Pronóstico: {alerta['Pronosticos']}
Periodo: {alerta['Periodos']}
"""

        # Configuración de Twilio
        account_sid = 'AC8cc4389ace769f89d4d9d3767ec710aa'
        auth_token = 'ea2dbe882ac043e2bc5cf377659f3675'  # Reemplaza esto con tu token real
        client = Client(account_sid, auth_token)

        message = client.messages.create(
            from_='whatsapp:+14155238886',
            body=texto,
            to=f'whatsapp:{numero}'
        )

        return jsonify({'mensaje': '✅ Alerta enviada', 'sid': message.sid}), 200

    except Exception as e:
        return jsonify({'mensaje': '❌ Error al enviar la alerta', 'error': str(e)}), 500

@mensajes_bp.route('/api/alerta_personalizada', methods=['POST'])
def alerta_personalizada():
    cursor = mysql.connection.cursor()
    sql = "SELECT * FROM Coordenadas_rio_taquina;"
    cursor.execute(sql)
    
    resultados = cursor.fetchall()  # Obtener todos los registros
    cursor.close()
    
    # Construir el diccionario
    Coordenadas_rio = {}
    for fila in resultados:
        id_coordenada, nombre, latitud, longitud = fila
        Coordenadas_rio[nombre] = [latitud, longitud]

    cursor = mysql.connection.cursor()
    sql = "SELECT * FROM usuarios"
    cursor.execute(sql)
    
    resultados_usuario = cursor.fetchall()  # Obtener todos los registros
    cursor.close()
    
    # Construir el diccionario
    Coordenadas_usuario = {}
    for fila in resultados_usuario:
        id_usuarios,Roles,Contrasenas,Latitud,Celulares,Correos,Nombres,Longitud = fila
        Coordenadas_usuario[Nombres] = [Latitud, Longitud,Celulares]


    # Solo para ver que funciona
    print(Coordenadas_rio)
    
    return {"coordenadas": Coordenadas_rio}  # Retornar como respuesta JSON si lo deseas

