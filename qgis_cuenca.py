import sys
import os
from qgis.core import (
    QgsApplication,
    QgsVectorLayer,
    QgsProject,
    QgsMapSettings,
    QgsMapRendererCustomPainterJob
)
from qgis.PyQt.QtGui import QImage, QPainter
from qgis.PyQt.QtCore import QSize

# 🔹 Inicializar QGIS en modo sin interfaz
QgsApplication.setPrefixPath(r"C:\Program Files\QGIS 3.40.11\apps\qgis-ltr", True)
qgs = QgsApplication([], False)
qgs.initQgis()

# 🔹 Carpeta donde se guardará la imagen
TEMP_DIR = os.path.join(os.path.dirname(__file__), "temp")
os.makedirs(TEMP_DIR, exist_ok=True)
output_img = os.path.join(TEMP_DIR, "cuenca_taquina.png")

try:
    # 🔹 Cargar capa de la cuenca Taquina (archivo shapefile)
    # Asegúrate de tener el shapefile en la misma carpeta o ajusta la ruta
    shapefile_cuenca = os.path.join(os.path.dirname(__file__), "cuenca_taquina.shp")
    shapefile_rios = os.path.join(os.path.dirname(__file__), "rios_taquina.shp")

    cuenca_layer = QgsVectorLayer(shapefile_cuenca, "Cuenca Taquina", "ogr")
    rios_layer = QgsVectorLayer(shapefile_rios, "Ríos Taquina", "ogr")

    if not cuenca_layer.isValid() or not rios_layer.isValid():
        raise Exception("No se pudo cargar una o ambas capas")

    # 🔹 Agregar capas al proyecto
    project = QgsProject.instance()
    project.addMapLayer(cuenca_layer)
    project.addMapLayer(rios_layer)

    # 🔹 Configurar renderizado
    map_settings = QgsMapSettings()
    map_settings.setLayers([cuenca_layer, rios_layer])
    map_settings.setBackgroundColor(cuenca_layer.renderer().symbol().color())
    map_settings.setOutputSize(QSize(800, 600))
    map_settings.setExtent(cuenca_layer.extent())

    # 🔹 Renderizar imagen
    image = QImage(map_settings.outputSize(), QImage.Format_ARGB32_Premultiplied)
    image.fill(0xffffffff)  # fondo blanco
    painter = QPainter(image)
    job = QgsMapRendererCustomPainterJob(map_settings, painter)
    job.start()
    job.waitForFinished()
    painter.end()

    # 🔹 Guardar imagen
    image.save(output_img)
    print(f"Imagen generada en: {output_img}")

except Exception as e:
    print(f"Error: {str(e)}")

finally:
    qgs.exitQgis()
    print("Script finalizado")
