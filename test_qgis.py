import qgis
from qgis.core import QgsApplication, QgsVectorLayer, Qgis

try:
    print("QGIS cargado correctamente desde:", qgis.__file__)
except Exception as e:
    print("Error al cargar QGIS:", str(e))

QgsApplication.setPrefixPath("", True)
qgs = QgsApplication([], False)
qgs.initQgis()

try:
    print("Versión de QGIS:", Qgis.QGIS_DEV_VERSION)
    print("Versión numérica:", Qgis.QGIS_VERSION_INT)
except Exception as e:
    print("Error al obtener versión de QGIS:", str(e))

layer = QgsVectorLayer("Point?crs=EPSG:4326", "test_layer", "memory")
if not layer.isValid():
    print("La capa no se pudo crear")
else:
    print("Capa creada con éxito:", layer.name())

qgs.exitQgis()
print("Script finalizado")
