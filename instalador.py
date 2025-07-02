import os

def instalar_dependencias():
    print("Actualizando pip...")
    os.system("pip install --upgrade pip")
    print("Instalando librerías necesarias...")
    os.system("pip install -r requirements.txt")
    print("✅ Instalación completa.")

if __name__ == "__main__":
    instalar_dependencias()
