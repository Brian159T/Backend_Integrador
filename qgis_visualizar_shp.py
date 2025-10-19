import os
import sys
from qgis.core import (
    QgsApplication,
    QgsProject,
    QgsRasterLayer,
    QgsVectorLayer,
    QgsLayout,
    QgsLayoutItemMap,
    QgsLayoutExporter
)

# ------------------------------------------------
# Inicializar QGIS (modo sin GUI)
# ------------------------------------------------
QgsApplication.setPrefixPath(r"C:/Program Files/QGIS 3.40.11", True)
qgs = QgsApplication([], False)
qgs.initQgis()

# ------------------------------------------------
# Rutas de los archivos GIS
# ------------------------------------------------
base_dir = r"D:\Archivos_Gis"

red_path = os.path.join(base_dir, "Red25m.shp")
cuenca_path = os.path.join(base_dir, "2cuengrlpolig.shp")
raster_path = os.path.join(base_dir, "DEMUNIDO.TIF")

# ------------------------------------------------
# Crear proyecto y cargar capas
# ------------------------------------------------
project = QgsProject.instance()
layers = []

# Cargar raster DEM
if os.path.exists(raster_path):
    raster_layer = QgsRasterLayer(raster_path, "DEMUNIDO")
    if raster_layer.isValid():
        project.addMapLayer(raster_layer)
        layers.append(raster_layer)
    else:
        print(f"[ERROR] Error al cargar {raster_path}")
else:
    print(f"[ERROR] No existe {raster_path}")

# Cargar capa de cuenca
if os.path.exists(cuenca_path):
    cuenca_layer = QgsVectorLayer(cuenca_path, "Cuenca", "ogr")
    if cuenca_layer.isValid():
        project.addMapLayer(cuenca_layer)
        layers.append(cuenca_layer)
    else:
        print(f"[ERROR] Error al cargar {cuenca_path}")
else:
    print(f"[ERROR] No existe {cuenca_path}")

# Cargar capa de red
if os.path.exists(red_path):
    red_layer = QgsVectorLayer(red_path, "Red25m", "ogr")
    if red_layer.isValid():
        project.addMapLayer(red_layer)
        layers.append(red_layer)
    else:
        print(f"[ERROR] Error al cargar {red_path}")
else:
    print(f"[ERROR] No existe {red_path}")

if not layers:
    print("[ERROR] Ninguna capa se pudo cargar correctamente.")
    qgs.exitQgis()
    sys.exit(1)

# ------------------------------------------------
# Crear layout del mapa
# ------------------------------------------------
layout = QgsLayout(project)
layout.initializeDefaults()

map_item = QgsLayoutItemMap(layout)
map_item.setRect(0, 0, 200, 200)

# Calcular extensión combinada de las capas
extent = layers[0].extent()
for lyr in layers[1:]:
    extent.combineExtentWith(lyr.extent())

map_item.setExtent(extent)
layout.addLayoutItem(map_item)

# ------------------------------------------------
# Exportar mapa como imagen
# ------------------------------------------------
output_dir = os.path.join(os.path.dirname(__file__), "temp")
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, "cuenca_taquina.png")

exporter = QgsLayoutExporter(layout)
result = exporter.exportToImage(output_path, QgsLayoutExporter.ImageExportSettings())

if result == QgsLayoutExporter.Success:
    print(f"[OK] Mapa generado correctamente en: {output_path}")
else:
    print("[ERROR] Error al exportar el mapa")

# ------------------------------------------------
# Finalizar QGIS
# ------------------------------------------------
qgs.exitQgis()
