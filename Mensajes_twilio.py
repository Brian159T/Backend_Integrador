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
        account_sid = ''
        auth_token = ''  # Reemplaza esto con tu token real
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
    try:
        # 1. Obtener datos de usuarios
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM usuarios")
        resultados_usuario = cursor.fetchall()
        cursor.close()

        Coordenadas_usuario = {}
        for fila in resultados_usuario:
            id_usuarios, Roles, Contrasenas, Celulares, Correos, Nombres, Longitudes, Latitudes = fila
            Coordenadas_usuario[Nombres] = [id_usuarios, Nombres, Latitudes, Longitudes, Celulares]

        # 2. Obtener coordenadas del punto A (corrigido: Latitudes y Longitudes)
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT Latitudes, Longitudes FROM coordenadas_rio_taquina WHERE Nombres = %s", ('Punto A',))
        resultado = cursor.fetchone()
        cursor.close()

        if not resultado:
            return jsonify({'mensaje': "❌ No se encontró 'Punto A' en la base de datos"}), 404

        T1 = math.radians(resultado[0])  # Latitudes
        L1 = math.radians(resultado[1])  # Longitudes

        # 3. Calcular distancia y enviar alertas si corresponde
        r = 6371  # Radio de la Tierra en km
        Distancia_punto_A = {}

        data = request.get_json()
        print("📦 Datos recibidos:", data)

        alerta = data.get('alerta')
        if not alerta:
            return jsonify({'mensaje': '❌ Falta el campo \"alerta\" en el cuerpo JSON'}), 400

        for nombre, datos in Coordenadas_usuario.items():
            N = datos[1]
            T2 = math.radians(datos[2])
            L2 = math.radians(datos[3])
            C = datos[4]

            d = 2 * r * math.asin(math.sqrt(
                math.sin((T2 - T1) / 2) ** 2 +
                math.cos(T1) * math.cos(T2) * math.sin((L2 - L1) / 2) ** 2
            ))

            Distancia_punto_A[N] = [N, C, round(d, 3)]

            if d < 3:
                numero = C

                if not numero.startswith('+'):
                    print(f"⚠️ Número inválido: {numero}")
                    continue

                texto = f"""
🚨 *Alerta Hidrológica* 🚨
Cuenca: {alerta.get('Cuencas')}
Río: {alerta.get('Rios')}
Caudal: {alerta.get('Niveles')} m³/s
Condición: {alerta.get('Condiciones')}
Pronóstico: {alerta.get('Pronosticos')}
Periodo: {alerta.get('Periodos')}
"""

                # Enviar mensaje con Twilio
                account_sid = ''
                auth_token = ''
                client = Client(account_sid, auth_token)

                try:
                    message = client.messages.create(
                        from_='whatsapp:+14155238886',
                        body=texto,
                        to=f'whatsapp:{numero}'
                    )
                    print(f"✅ Menssssaje enviado a {numero}")
                except Exception as twilio_error:
                    print(f"❌ Error al enviar a {numero}: {twilio_error}")

        return jsonify({'mensaje': '✅ Alertas procesadas correctamente'}), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'mensaje': '❌ Error al enviar las alertas', 'error': str(e)}), 500




           

    




   

