from flask import Flask, request, render_template, redirect, url_for, flash
import json
import os
from datetime import datetime

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
        hotel["visitas"] += 1  # Sumar visita
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

@app.route('/form-login', methods=['GET','POST'])
def login():
    data = load_users()
    _user = request.form['txtuser']
    _pass = request.form['txtpassword']
    _user = _user.lower()

    for credenciales in data:
        if _user == credenciales["usuario"] and _pass == credenciales["contraseña"]:
            permision = credenciales["permisos"]
            if permision == "cliente":
                return redirect(url_for('client'))
            elif permision == "empleado":
                return redirect(url_for('empleado'))
            elif permision == "admin":
                return redirect(url_for('admin'))


    return redirect(url_for('home'))


@app.route('/error')
def error():
    return render_template("error_page.html")




if __name__ == '__main__':
    app.run(debug=True)