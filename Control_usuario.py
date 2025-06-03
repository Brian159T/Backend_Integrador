from flask import Blueprint, request, jsonify
from db import mysql  

usuario_bp = Blueprint('usuario_bp', __name__)

@usuario_bp.route("/api/control", methods=["POST"])
def control_usuarios():
    email = request.json.get('email')
    contrasena = request.json.get('contrasena')

    cursor = mysql.connection.cursor()
    sql = "SELECT Roles, Nombres FROM usuarios WHERE Correos=%s AND Contrasenas=%s"
    cursor.execute(sql, (email, contrasena))
    usuario = cursor.fetchone()
    cursor.close()
    
    if usuario:
        return jsonify({
            "status": "success",
            "rol": usuario[0],
            "nombre": usuario[1]
        }), 200
    else:
        return jsonify({"status": "error", "message": "Usuario no encontrado"}), 401