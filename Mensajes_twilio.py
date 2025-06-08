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
