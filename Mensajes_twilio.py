from twilio.rest import Client
from flask import Blueprint, Response, request, jsonify
from db import mysql

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

        # Configuración de Twilio (ficticia para evitar bloqueos)
        account_sid = 'TWILIO_SID_AQUI'
        auth_token = 'TWILIO_TOKEN_AQUI'
        client = Client(account_sid, auth_token)

        message = client.messages.create(
            from_='whatsapp:+14155238886',
            body=texto,
            to=f'whatsapp:{numero}'
        )

        return jsonify({'mensaje': '✅ Alerta enviada', 'sid': message.sid}), 200

    except Exception as e:
        return jsonify({'mensaje': '❌ Error al enviar la alerta', 'error': str(e)}), 500
