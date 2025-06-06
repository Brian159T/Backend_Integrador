from flask import Blueprint, Response
from db import mysql
import matplotlib.pyplot as plt
from io import BytesIO

graficos_bp = Blueprint('graficos_bp', __name__)

@graficos_bp.route('/api/grafico-torta', methods=['GET'])
def obtener_grafico_torta():
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT Rios, Niveles FROM alertas")
        resultados = cursor.fetchall()
        cursor.close()

        # Separar en listas
        rios = []
        niveles = []

        for fila in resultados:
            rios.append(fila[0])
            niveles.append(float(fila[1]))

        # Crear gráfico de torta
        plt.figure(figsize=(8, 8))
        plt.pie(niveles, labels=rios, autopct='%1.1f%%', startangle=140)
        plt.title('Distribución de Niveles por Río')
        plt.axis('equal')  # Para que la torta sea circular

        # Guardar en memoria
        img = BytesIO()
        plt.savefig(img, format='png')
        plt.close()
        img.seek(0)

        return Response(img.getvalue(), mimetype='image/png')

    except Exception as ex:
        return {'mensaje': 'Error al generar gráfico de torta ❌', 'error': str(ex)}, 500
    
@graficos_bp.route('/api/grafico-barras', methods=['GET'])
def obtener_grafico_barras():
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT Rios, Niveles FROM alertas")
        resultados = cursor.fetchall()
        cursor.close()

        # Separar en listas
        rios = []
        niveles = []

        for fila in resultados:
            rios.append(fila[0])
            niveles.append(float(fila[1]))

        # Crear gráfico de barras
        plt.figure(figsize=(10, 6))
        plt.bar(rios, niveles, color='skyblue')
        plt.xlabel('Ríos')
        plt.ylabel('Niveles')
        plt.title('Niveles por Río')
        plt.xticks(rotation=45)
        plt.tight_layout()

        # Guardar en memoria
        img = BytesIO()
        plt.savefig(img, format='png')
        plt.close()
        img.seek(0)

        return Response(img.getvalue(), mimetype='image/png')

    except Exception as ex:
        return {'mensaje': 'Error al generar gráfico de barras ❌', 'error': str(ex)}, 500


