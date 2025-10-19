import os
import sys
import json
import glob

CAT_OK = "😺"
CAT_FAIL = "😿"
CAT_WORK = "🐾"

WORKSPACE_FOLDER = "${workspaceFolder}/.env"

# ---------------------------------------------------------
# 1. Detectar instalación de QGIS
# ---------------------------------------------------------
def detect_qgis_installations():
    candidates = []
    candidates += glob.glob(r"C:\Program Files\QGIS*")
    candidates += glob.glob(r"C:\OSGeo4W*")
    return [c for c in candidates if os.path.isdir(c)]

def choose_qgis_installation(installs):
    if not installs:
        print(f"{CAT_FAIL} No se encontró ninguna instalación de QGIS.")
        sys.exit(1)

    if len(installs) == 1:
        return installs[0]

    print(f"{CAT_WORK} Se detectaron varias instalaciones de QGIS:\n")
    for i, inst in enumerate(installs, 1):
        print(f" {i}. {inst}")
    choice = input("\nElige el número de la instalación que deseas usar: ")
    try:
        idx = int(choice) - 1
        return installs[idx]
    except:
        print(f"{CAT_FAIL} Selección inválida.")
        sys.exit(1)

# ---------------------------------------------------------
# 2. Configurar rutas de QGIS
# ---------------------------------------------------------
def get_qgis_info(root):
    python_dirs = glob.glob(os.path.join(root, "apps", "Python*"))
    if not python_dirs:
        print(f"{CAT_FAIL} No se encontró directorio Python en {root}\\apps")
        sys.exit(1)

    python_dir = os.path.basename(python_dirs[0])
    python_exe = os.path.join(root, "apps", python_dir, "python.exe")

    qgis_variants = ["qgis-ltr", "qgis"]
    qgis_version = None
    for variant in qgis_variants:
        if os.path.exists(os.path.join(root, "apps", variant, "python")):
            qgis_version = variant
            break
    if not qgis_version:
        print(f"{CAT_FAIL} No se encontró carpeta 'qgis' o 'qgis-ltr' en {root}\\apps")
        sys.exit(1)

    return {
        "root": root,
        "python_dir": python_dir,
        "python_exe": python_exe,
        "qgis_version": qgis_version
    }

# ---------------------------------------------------------
# 3. Crear archivos de configuración
# ---------------------------------------------------------
def create_qgis_pth(site_packages, qgis_python, qgis_plugins):
    pth_file = os.path.join(site_packages, "qgis.pth")
    try:
        with open(pth_file, "w", encoding="utf-8") as f:
            f.write(qgis_python + "\n")
            f.write(qgis_plugins + "\n")
        print(f"{CAT_OK} Archivo qgis.pth creado en: {pth_file}")
    except PermissionError:
        pth_file = os.path.join(os.getcwd(), "qgis.pth")
        with open(pth_file, "w", encoding="utf-8") as f:
            f.write(qgis_python + "\n")
            f.write(qgis_plugins + "\n")
        print(" ")
        print(f"⚠️  {CAT_FAIL} No se pudo crear qgis.pth en la carpeta de instalación de QGIS (permiso denegado).")
        print("⚠️ ⚠️ ⚠️   Intenta ejecutar este script como Administrador. O copie el archivo qgis.pth en:")
        print(site_packages)
        print(" ")

def create_workspace(python_exe, qgis_python, qgis_plugins):
    workspace = {
        "folders": [{"path": "."}],
        "settings": {
            "python.defaultInterpreterPath": python_exe,
            "python.envFile": WORKSPACE_FOLDER,
            "python.analysis.extraPaths": [qgis_python, qgis_plugins],
            "terminal.integrated.env.windows": {
                "Path": f"{os.path.dirname(python_exe)};{os.path.dirname(python_exe)}\\Scripts;${{env:Path}}"
            }
        },
        "launch": {
            "version": "0.2.0",
            "configurations": [
                {
                    "name": "QGIS python",
                    "type": "debugpy",
                    "request": "launch",
                    "program": "${file}",
                    "console": "integratedTerminal",
                    "envFile": WORKSPACE_FOLDER,
                    "justMyCode": False,
                    "stopOnEntry": False
                }
            ]
        }
    }

    workspace_file = os.path.join(os.getcwd(), "qgis.code-workspace")
    with open(workspace_file, "w", encoding="utf-8") as f:
        json.dump(workspace, f, indent=4)
    print(f"{CAT_OK} Archivo qgis.code-workspace creado en: {workspace_file}")

def create_env_example(qgis_root, qgis_version):
    env_file = os.path.join(os.getcwd(), ".env.example")
    if os.path.exists(env_file):
        print(f"{CAT_WORK} Ya existe .env.example, no se sobrescribió.")
        return

    content = f"""# QGIS Environment Variables
        OSGEO4W_ROOT={qgis_root}
        QGIS_PREFIX_PATH={qgis_root}/apps/{qgis_version}
        PYTHONPATH=${{QGIS_PREFIX_PATH}}/python;${{QGIS_PREFIX_PATH}}/python/plugins
        GDAL_DATA=${{OSGEO4W_ROOT}}/apps/gdal/share/gdal
        QT_PLUGIN_PATH=${{QGIS_PREFIX_PATH}}/qtplugins
        """
    with open(env_file, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"{CAT_OK} Archivo .env.example creado en: {env_file}")

def ensure_gitignore():
    gitignore = os.path.join(os.getcwd(), ".gitignore")
    if os.path.exists(gitignore):
        with open(gitignore, "r", encoding="utf-8") as f:
            lines = f.read().splitlines()
    else:
        lines = []

    if ".env" not in lines:
        lines.append(".env")
        with open(gitignore, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
        print(f"{CAT_OK} Se agregó .env a .gitignore")
    else:
        print(f"{CAT_WORK} .env ya estaba en .gitignore")

# ---------------------------------------------------------
# 4. Verificación opcional (--check)
# ---------------------------------------------------------
def check_import(qgis_python, qgis_plugins):
    print(f"\n{CAT_WORK} Verificando importación de QGIS...")
    try:
        sys.path.append(qgis_python)
        sys.path.append(qgis_plugins)
        import qgis #type: ignore
        print(f"{CAT_OK} QGIS importado correctamente desde: {qgis.__file__}")
    except Exception as e:
        print(f"{CAT_FAIL} Error al importar QGIS: {e}")

# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------
if __name__ == "__main__":
    installs = detect_qgis_installations()
    chosen = choose_qgis_installation(installs)
    qgis_info = get_qgis_info(chosen)

    QGIS_ROOT = qgis_info["root"]
    PYTHON_DIR = qgis_info["python_dir"]
    PYTHON_EXE = qgis_info["python_exe"]
    QGIS_VERSION = qgis_info["qgis_version"]

    SITE_PACKAGES = os.path.join(QGIS_ROOT, "apps", PYTHON_DIR, "Lib", "site-packages")
    QGIS_PYTHON = os.path.join(QGIS_ROOT, "apps", QGIS_VERSION, "python")
    QGIS_PLUGINS = os.path.join(QGIS_PYTHON, "plugins")

    # Crear archivos
    create_qgis_pth(SITE_PACKAGES, QGIS_PYTHON, QGIS_PLUGINS)
    create_workspace(PYTHON_EXE, QGIS_PYTHON, QGIS_PLUGINS)
    create_env_example(QGIS_ROOT, QGIS_VERSION)
    ensure_gitignore()

    # Opción de verificación
    if "--check" in sys.argv:
        check_import(QGIS_PYTHON, QGIS_PLUGINS)