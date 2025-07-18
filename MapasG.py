from flask import Blueprint, render_template, request, jsonify

mapasgbp = Blueprint('mapasgbp', __name__)

# Lista para guardar coordenadas en memoria (demo)
marcadores_guardados = []

@mapasgbp.route('/api/mapa', methods=['GET'])
def mostrar_mapa():
    # Pasa los marcadores guardados a la plantilla
    return render_template('mapa_google.html', marcadores=marcadores_guardados)

@mapasgbp.route('/api/guardar-coordenadas', methods=['POST'])
def guardar_coordenadas():
    data = request.json
    lat = float(data.get('lat'))
    lng = float(data.get('lng'))

    marcadores_guardados.append({'lat': lat, 'lng': lng})
    print(f"Guardado marcador: {lat}, {lng}")

    return jsonify({"status": "ok", "lat": lat, "lng": lng})
