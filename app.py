from flask import Flask, request, render_template, redirect, url_for, flash
import json

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta'  # Necesaria para usar flash


# Formato de la BD
#       [
#           {
#               "id": 0,
#               "usuario": "Aguss",
#               "contraseña": "1234",
#               "correo": "aguss@example.com",
#               "permisos": "admin"
#           }
#       ]





# Cargar usuarios desde el archivo JSON
def load_users():
    with open('data/users.json', encoding='utf-8') as f:
        data = json.load(f)
    return data

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/client')
def client():
    return render_template("client.html")

@app.route('/employee')
def employee():
    return render_template("employee.html")

@app.route('/admin')
def admin():
    return render_template("admin.html")

@app.route('/form-login', methods=['GET','POST'])
def login():
    data = load_users()
    _user = request.form['txtuser']
    _pass = request.form['txtpassword']

    for credenciales in data:
        if _user == credenciales["usuario"] and _pass == credenciales["contraseña"]:
            permision = credenciales["permisos"]
            if permision == "cliente":
                return render_template("client.html")
            elif permision == "empleado":
                return render_template("employee.html")
            elif permision == "admin":
                return render_template("admin.html")


    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)