from twilio.rest import Client
from flask import Blueprint, Response
from db import mysql
import math

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
    sql = "SELECT * FROM usuarios"
    cursor.execute(sql)
    resultados_usuario = cursor.fetchall()  
    cursor.close()

    Coordenadas_usuario = {}
    for fila in resultados_usuario:
        id_usuarios, Roles, Contrasenas, Celulares, Correos, Nombres, Longitudes, Latitudes = fila
        Coordenadas_usuario[Nombres] = [id_usuarios, Nombres, Latitudes, Longitudes, Celulares]

    cursor = mysql.connection.cursor()
    sql = "SELECT Latitudes, Longitudes FROM coordenadas_rio_taquina WHERE Nombres = %s"
    cursor.execute(sql, ('Punto A',))
    resultado = cursor.fetchone()
    cursor.close()

    if resultado:
        T1 = math.radians(resultado[0])  # Latitud en radianes
        L1 = math.radians(resultado[1])  # Longitud en radianes
    else:
        T1 = L1 = None
        print("No se encontró 'Punto A'")

    Distancia_punto_A = {}
    r = 6371

    for nombre, datos in Coordenadas_usuario.items():
        N = datos[1]
        T2 = math.radians(datos[2])  # convertir a radianes
        L2 = math.radians(datos[3])
        C = datos[4]

        d = 2 * r * math.asin(math.sqrt(
            math.sin((T2 - T1) / 2) ** 2 +
            math.cos(T1) * math.cos(T2) * math.sin((L2 - L1) / 2) ** 2
        ))

        Distancia_punto_A[N] = [N, C, round(d, 3)]

    return jsonify(Distancia_punto_A)


           

    



   

