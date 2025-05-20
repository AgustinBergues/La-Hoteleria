from flask import Flask, request, render_template, redirect, url_for, flash
import json
import os
from datetime import datetime
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash

app = Flask(__name__)
app.secret_key = '8273645912037485'  # Necesaria para usar flash
DATA_FILE = 'static/hotels.json'
hoy = datetime.today()
hoy = hoy.strftime("%d/%m/%Y")

print(hoy)

impuestos = {
    "Alquiler_online": 10,  
    "Mantenimiento": 5       
}


# Cargar usuarios desde el archivo JSON
def load_users():
    with open('data/users.json', encoding='utf-8') as f:
        data = json.load(f)
    return data


def cargar_hoteles():
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)
    
def cargar_reservas():
    with open('data/reservas.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def cargar_mantenimientos():
    with open('data/mantenimientos.json', 'r', encoding='utf-8') as f:
        return json.load(f)



def guardar_hoteles(hoteles):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(hoteles, f, indent=4, ensure_ascii=False)



@app.route('/')
def home():
    return render_template('index.html')







@app.route('/client')
def client():
    hoteles = cargar_hoteles()

    # Ordenar por visitas, de mayor a menor
    hoteles.sort(key=lambda h: h['visitas'], reverse=True)
    hoteles_mas_buscados = hoteles[:3]  # Los 3 más buscados

    # Ordenar por precio más bajo (habitación 'Simple')
    hoteles.sort(key=lambda h: h['precios']['Simple'])
    hoteles_mas_economicos = hoteles[:3]  # Los 3 más económicos

   # Mostrar todos los hoteles
    hoteles_todos = cargar_hoteles()

    return render_template("client.html", hoteles_mas_buscados=hoteles_mas_buscados, hoteles_mas_economicos=hoteles_mas_economicos, hoteles_todos=hoteles_todos)


@app.route('/hotel/<int:hotel_id>')
def ver_hotel(hotel_id):
    global hotel_actual
    hoteles = cargar_hoteles()
    hotel_actual = hotel_id
    # Buscar hotel por id
    hotel = next((h for h in hoteles if h["id"] == hotel_id), None)

    if hotel:
        hotel["visitas"] += 1
        guardar_hoteles(hoteles)

        return render_template("ver_hotel.html", hotel=hotel)
    else:
        return "Hotel no encontrado", 404

@app.route('/formulario')
def formulario_reserva():
    hotel_id=hotel_actual
    return render_template('Form.html', hotel_id=hotel_id)


@app.route('/reservar', methods=['POST'])
def reservar():
    nombre = request.form.get('name')
    telefono = request.form.get('phone')
    correo = request.form.get('email')
    habitacion = request.form.get('room')



    print(f"Reserva recibida: {nombre}, {telefono}, {correo}, {habitacion}")


    return redirect(url_for('client'))






@app.route('/dashboard')
def empleado():
    mantenimientos = cargar_mantenimientos()

    return render_template("dash_empleado.html", mantenimientos=mantenimientos)

@app.route('/checks')
def checks():
    reservas = cargar_reservas()

    return render_template("checks_empleado.html", reservas=reservas)




@app.route('/admin')
def admin():
    return render_template("dashboard_admin.html")

@app.route('/form-login', methods=['GET', 'POST'])
def login():
    data = load_users()
    _user = request.form['txtuser'].lower()
    _pass = request.form['txtpassword']

    for credenciales in data:
        if _user == credenciales["user"].lower():
            if check_password_hash(credenciales["password"], _pass):
                permiso = credenciales["permisos"]
                if permiso == "cliente":
                    return redirect(url_for('client'))
                elif permiso == "empleado":
                    return redirect(url_for('empleado'))
                elif permiso == "admin":
                    return redirect(url_for('admin'))
            else:
                flash("Contraseña incorrecta", "error")
                return redirect(url_for('home'))

    flash("Usuario no encontrado", "error")
    return redirect(url_for('home'))


@app.route('/error')
def error():
    return render_template("error_page.html")




@app.route('/registro', methods=['GET'])
def registro():
    return render_template('register.html')


@app.route('/registrar_usuario', methods=['POST'])
def registrar_usuario():
    users_file = 'data/users.json'

    # Crear archivo si no existe
    if not os.path.exists(users_file):
        with open(users_file, 'w', encoding='utf-8') as f:
            json.dump([], f, indent=4)

    # Leer usuarios existentes
    with open(users_file, 'r', encoding='utf-8') as f:
        usuarios = json.load(f)

    # Obtener datos del formulario
    user_input = request.form['user']
    email_input = request.form['email']

    # Verificar si el usuario o el email ya existen
    for u in usuarios:
        if u['user'].lower() == user_input.lower():
            flash('Nombre de usuario ya registrado. Elegí otro.', 'error')
            return redirect(url_for('registro'))
        if u['email'].lower() == email_input.lower():
            flash('Correo electrónico ya registrado.', 'error')
            return redirect(url_for('registro'))

    # Obtener el último ID usado
    ultimo_id = max((u.get("id", 0) for u in usuarios), default=-1)
    if request.form['password'] != request.form['confirm-password']:
        flash('La contraseña no coincide.', 'error')
        return redirect(url_for('registro'))

    nuevo_usuario = {
        "id": ultimo_id + 1,
        "user": user_input.lower(),
        "nombre": request.form['nombre'],
        "apellido": request.form['apellido'],
        "telefono": request.form['telefono'],
        "email": email_input,
        "password": generate_password_hash(request.form['password']),
        "fecha_nacimiento": request.form['fecha'],
        "permisos": "cliente"
    }

    usuarios.append(nuevo_usuario)

    with open(users_file, 'w', encoding='utf-8') as f:
        json.dump(usuarios, f, indent=4, ensure_ascii=False)

    flash(f'Registro exitoso. ID asignado: {nuevo_usuario["id"]}', 'success')
    return redirect(url_for('home'))









if __name__ == '__main__':
    app.run(debug=True)