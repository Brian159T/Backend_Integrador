from flask import Blueprint, request, redirect, url_for, flash
from db import mysql

crud_bp = Blueprint('crud_bp', __name__)

@crud_bp.route('/eliminar_usuario', methods=['POST'])
def eliminar_usuario():
    correo = request.form['correo']
    
    cursor = mysql.connection.cursor()
    sql = "DELETE FROM usuarios WHERE Correos = %s"
    cursor.execute(sql, (correo,))
    mysql.connection.commit()
    cursor.close()
    
    flash('Usuario eliminado correctamente ✅')
    return redirect(url_for('mostrar_gestion_usuarios'))




@crud_bp.route('/registrar_usuario_admin', methods=['POST'])
def registrar_usuario_ad():
     
    email = request.form['email']
    password = request.form['password']
    coordenadas = request.form['Coordenadas']
    celular = request.form['celular']
    nombre = request.form['nombre']
    Rol = request.form['Rol']

    cursor = mysql.connection.cursor()  # corregido aqui
    
    sql = "INSERT INTO usuarios (Roles, Contrasenas, Coordenadas, Celulares, Correos, Nombres) VALUES (%s, %s, %s, %s, %s, %s)"
    datos = (Rol, password, coordenadas, celular, email, nombre)
    cursor.execute(sql, datos)
    mysql.connection.commit()  # corregido aqui
    flash('Cuenta creada correctamente ✅')

    return redirect(url_for('mostrar_gestion_usuarios'))     