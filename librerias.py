import os 
librerias=["flask","datatime","os","json","werkzeug.security"]
os.system("pip install -U pip")  # Actualizar pip a la última versión
for libreria in librerias:
    os.system(f"pip install {libreria}")
