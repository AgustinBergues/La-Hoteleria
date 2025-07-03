from flask import Flask, request, render_template, redirect, url_for, flash
import json
import os
from flask import jsonify
from datetime import datetime
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename

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

def cargar_habitaciones():
    with open('data/habitaciones.json', 'r', encoding='utf-8') as f:
        return json.load(f)
    
def cargar_reportes():
    with open('data/reportes.json', 'r', encoding='utf-8') as f:
        return json.load(f)


def guardar_hoteles(hoteles):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(hoteles, f, indent=4, ensure_ascii=False)

def guardar_reportes(reportes):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(reportes, f, indent=4, ensure_ascii=False)

    
@app.route('/')
def home():
    return render_template('index.html')



from flask import session  # Agregalo al import

@app.route('/form-login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    data = load_users()
    _user = request.form['txtuser'].lower()
    _pass = request.form['txtpassword']

    try:
        for credenciales in data:
            if _user == credenciales["user"].lower():
                if check_password_hash(credenciales["password"], _pass):
                    session['user'] = credenciales["user"]  # Guardar en sesión
                    session['permiso'] = credenciales["permisos"]
                    
                    if credenciales["permisos"] == "cliente":
                        return redirect(url_for('client'))
                    elif credenciales["permisos"] == "empleado":
                        return redirect(url_for('empleado'))
                    elif credenciales["permisos"] == "admin":
                        return redirect(url_for('admin'))
                    else:
                        flash("Permiso no reconocido", "error")
                        return redirect(url_for('home'))
                else:
                    flash("Contraseña incorrecta", "error")
                    return redirect(url_for('home'))

        flash("Usuario no encontrado", "error")
        return redirect(url_for('home'))

    except Exception as e:
        flash(f"Ocurrió un error: {str(e)}", "error")
        return redirect(url_for('home'))


@app.route('/recuperar')
def recuperar():
    return render_template('recuperar.html')


@app.route('/registro', methods=['GET'])
def registro():
    return render_template('register.html')


@app.route('/registrar_usuario', methods=['POST'])
def registrar_usuario():
    users_file = 'data/users.json'

    if not os.path.exists(users_file):
        with open(users_file, 'w', encoding='utf-8') as f:
            json.dump([], f, indent=4)

    with open(users_file, 'r', encoding='utf-8') as f:
        usuarios = json.load(f)

    user_input = request.form['user']
    email_input = request.form['email']


    for u in usuarios:
        if u['user'].lower() == user_input.lower():
            flash('Nombre de usuario ya registrado. Elegí otro.', 'error')
            return redirect(url_for('registro'))
        if u['email'].lower() == email_input.lower():
            flash('Correo electrónico ya registrado.', 'error')
            return redirect(url_for('registro'))


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








@app.route('/cliente')
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














@app.route('/empleado')
def empleado():

    reservas = cargar_reservas()
    habitaciones = cargar_habitaciones()
    mantenimientos = cargar_mantenimientos()

    checkins = sum(1 for r in reservas if r['estado'] == 'Check-in pendiente')
    checkouts = sum(1 for r in reservas if r['estado'] == 'Check-out pendiente')

    disponibles = sum(1 for h in habitaciones if h['estado'].lower() == 'disponible')
    ocupadas = sum(1 for h in habitaciones if h['estado'].lower() == 'ocupada')
    mantenimiento = sum(1 for h in habitaciones if h['estado'].lower() == 'mantenimiento')

    return render_template("dash_empleado.html", mantenimientos=mantenimientos, checkins=checkins, checkouts=checkouts, disponibles=disponibles, ocupadas=ocupadas, mantenimiento=mantenimiento)

@app.route('/checks')
def checks():
    reservas = cargar_reservas()

    return render_template("checks_empleado.html", reservas=reservas)


@app.route('/habitaciones')
def habitaciones_info():
    habitaciones = cargar_habitaciones()
    hotel = cargar_hoteles()
    m_habitaciones = []
    for u in habitaciones:
        for i in hotel:
            if u['hotel_id'] == i['id']:
                n_hotel = i['hotel']
                u['hotel_id'] = str(n_hotel).replace("Hotel ", "")
                m_habitaciones.append(u)



    return render_template("habitaciones_e.html", habitaciones=m_habitaciones)

@app.route('/reportar')
def reportar():
    

    return render_template('crear_reportes.html')





@app.route('/Micuenta')
def micuenta_e():
    if 'user' not in session:
        return redirect(url_for('home'))
    
    usuarios = load_users()
    usuario = next((u for u in usuarios if u["user"] == session["user"]), None)

    if not usuario:
        return redirect(url_for('home'))

    return render_template('micuenta_e.html', usuario=usuario)





@app.route('/admin')
def admin():

    reservas = cargar_reservas()
    habitaciones = cargar_habitaciones()
    mantenimientos = cargar_mantenimientos()
    reportes = cargar_reportes()
    

    checkins = sum(1 for r in reservas if r['estado'] == 'Check-in pendiente')
    checkouts = sum(1 for r in reservas if r['estado'] == 'Check-out pendiente')

    disponibles = sum(1 for h in habitaciones if h['estado'].lower() == 'disponible')
    ocupadas = sum(1 for h in habitaciones if h['estado'].lower() == 'ocupada')
    mantenimiento = sum(1 for h in habitaciones if h['estado'].lower() == 'mantenimiento')

    return render_template("dashboard_admin.html", mantenimientos=mantenimientos, checkins=checkins, checkouts=checkouts, disponibles=disponibles, ocupadas=ocupadas, mantenimiento=mantenimiento, reportes=reportes)


@app.route('/checks_a')
def checks_a():
    reservas = cargar_reservas()

    return render_template("checks_admin.html", reservas=reservas)



@app.route('/hoteles_admin')
def hoteles_admin():
    hoteles = cargar_hoteles()
    return render_template('mod_hotel.html', hoteles=hoteles)

@app.route('/guardar_hotel', methods=['POST'])
def guardar_hotel():
    hoteles = cargar_hoteles()
    nuevo_id = max((h['id'] for h in hoteles), default=-1) + 1
    nombre = request.form['hotel']
    simple = int(request.form['simple'])
    doble = int(request.form['doble'])
    suite = int(request.form['suite'])

    if request.form['hotel']:  # Editar hotel existente
        hotel_id = int(nuevo_id)
        for hotel in hoteles:
            if hotel['id'] == hotel_id:
                hotel['hotel'] = nombre
                hotel['precios'] = {"Simple": simple, "Doble": doble, "Suite": suite}
                if 'portada' in request.files:
                    archivo = request.files['portada']
                    if archivo.filename:
                        filename = secure_filename(archivo.filename)
                        archivo.save(os.path.join('static/img/', filename))
                        hotel['portada'] = f"static/img/{filename}"
                break
    else:  # Crear nuevo hotel
        nuevo_id = max((h['id'] for h in hoteles), default=-1) + 1
        archivo = request.files['portada']
        filename = secure_filename(archivo.filename)
        archivo.save(os.path.join('static/img/', filename))
        nuevo_hotel = {
            "id": nuevo_id,
            "hotel": nombre,
            "portada": f"static/img/{filename}",
            "habitaciones": [],
            "baño": "",
            "extras": [],
            "visitas": 0,
            "google_maps_url": "",
            "precios": {"Simple": simple, "Doble": doble, "Suite": suite}
        }
        hoteles.append(nuevo_hotel)


    guardar_hoteles(hoteles)
    return redirect(url_for('hoteles_admin'))


@app.route('/eliminar_hotel', methods=['POST'])
def eliminar_hotel():
    hotel_id = int(request.form['id'])
    hoteles = cargar_hoteles()
    hoteles = [h for h in hoteles if h['id'] != hotel_id]
    guardar_hoteles(hoteles)
    return redirect(url_for('hoteles_admin'))

@app.route('/nuevo_hotel')
def nuevo_hotel():
    return render_template('agregar_hotel.html')

@app.route('/guardar_hotel_nuevo', methods=['POST'])
def guardar_hotel_nuevo():
    hoteles = cargar_hoteles()
    nuevo_id = max((h['id'] for h in hoteles), default=-1) + 1

    nombre = request.form['hotel']
    maps = request.form['google_maps_url']
    simple = int(request.form['simple'])
    doble = int(request.form['doble'])
    suite = int(request.form['suite'])

    def guardar_imagen(campo):
        archivo = request.files.get(campo)
        if archivo and archivo.filename:
            filename = secure_filename(archivo.filename)
            ruta = f"static/img/{filename}"
            archivo.save(ruta)
            return ruta
        return ""

    nuevo_hotel = {
        "id": nuevo_id,
        "hotel": nombre,
        "portada": guardar_imagen('portada'),
        "habitaciones": [
            guardar_imagen('habitacion1'),
            guardar_imagen('habitacion2')
        ],
        "baño": guardar_imagen('baño'),
        "extras": [
            guardar_imagen('extra1'),
            guardar_imagen('extra2')
        ],
        "visitas": 0,
        "google_maps_url": maps,
        "precios": {
            "Simple": simple,
            "Doble": doble,
            "Suite": suite
        }
    }

    hoteles.append(nuevo_hotel)
    guardar_hoteles(hoteles)

    return redirect(url_for('hoteles_admin'))







@app.route('/reserva_admin')
def reservas_admin():
    reservas = cargar_reservas()

    return render_template("reservas_a.html", reservas=reservas)


@app.route('/mantenimiento_admin')
def mantenimiento_admin():
    mantenimientos = cargar_mantenimientos()

    return render_template("mantenimientos_a.html", mantenimientos=mantenimientos)



@app.route('/error')
def error():
    return render_template("error_page.html")

@app.route('/habitaciones_admin', methods=['GET', 'POST'])
def habitaciones_admin():
    hoteles_id = cargar_hoteles()
    hoteles_name = []
    habitaciones_dispo = []
    habitaciones_ocup  = [] 
    with open('data/habitaciones.json', 'r', encoding="UTF-8") as f:
        habitaciones = json.load(f)

    for i in habitaciones:
        if i['estado'] == "Disponible":
            habitaciones_dispo.append(i)
        if i['estado'] == "Ocupada":
            habitaciones_ocup.append(i)
    for i in hoteles_id:
        select = {"id" : i['id'], 'nombre': i['hotel']}
        hoteles_name.append(select)
    print(hoteles_name)



    return render_template('habitaciones_a.html', habitaciones=habitaciones, habitaciones_dispo=habitaciones_dispo, habitaciones_ocup=habitaciones_ocup)

@app.route('/habitaciones_admin_disponibles', methods=['GET', 'POST'])
def habitaciones_admin_disponibles():
    hoteles_id = cargar_hoteles()
    hoteles_name = {}
    habitaciones_dispo = []

    with open('data/habitaciones.json', 'r', encoding="UTF-8") as f:
        habitaciones = json.load(f)

    for i in hoteles_id:
        hoteles_name[str(i['id'])] = str(i['hotel']).replace("Hotel ","")



    for i in habitaciones:
        if i['estado'] == "Disponible":
            id_hotel = str(i['hotel_id'])
            i['hotel_nombre'] = hoteles_name.get(id_hotel, 'Hotel desconocido')
            habitaciones_dispo.append(i)




    return render_template('habitaciones_a_disponibles.html',habitaciones_dispo=habitaciones_dispo)


@app.route('/habitaciones_admin_ocupadas', methods=['GET', 'POST'])
def habitaciones_admin_ocupadas():
    hoteles_id = cargar_hoteles()
    hoteles_name = {}
    habitaciones_ocup  = [] 

    with open('data/habitaciones.json', 'r', encoding="UTF-8") as f:
        habitaciones = json.load(f)
        
    for i in hoteles_id:
        hoteles_name[str(i['id'])] = str(i['hotel']).replace("Hotel ","")

    for i in habitaciones:
        if i['estado'] == "Ocupada":
            id_hotel = str(i['hotel_id'])
            i['hotel_nombre'] = hoteles_name.get(id_hotel, 'Hotel desconocido')
            habitaciones_ocup.append(i)

    return render_template('habitaciones_a_ocupadas.html', habitaciones_ocup=habitaciones_ocup)





@app.route('/usuarios_admin', methods=['GET', 'POST'])
def usuarios_admin():
    users_file = 'data/users.json'

    with open(users_file, 'r', encoding='utf-8') as f:
        usuarios = json.load(f)

    if request.method == 'POST':
        user_id = int(request.form['id'])
        nuevo_permiso = request.form['permisos']

        for u in usuarios:
            if u['id'] == user_id:
                u['permisos'] = nuevo_permiso
                break

        with open(users_file, 'w', encoding='utf-8') as f:
            json.dump(usuarios, f, indent=4, ensure_ascii=False)

    return render_template('usuarios_a.html', usuarios=usuarios)

@app.route('/reportes')
def ver_quejas():
    with open('data/reportes.json', 'r', encoding='utf-8') as f:
        reportes = json.load(f)
    return render_template('reportes_a.html', reportes=reportes)
@app.route('/actualizar_reporte', methods=['POST'])
def actualizar_reporte():
    try:
        data = request.get_json()
        indice = data.get('indice')

        with open('data/reportes.json', 'r', encoding='utf-8') as f:
            reportes = json.load(f)

        if indice is None or not (0 <= indice < len(reportes)):
            return jsonify({'error': 'Índice inválido'}), 400

        if data.get('eliminar'):
            # Eliminar el reporte
            reportes.pop(indice)
        else:
            # Actualizar el reporte
            reportes[indice]['respuesta'] = data.get('respuesta', '')
            reportes[indice]['estado'] = data.get('estado', reportes[indice].get('estado', 'pendiente'))

        with open('data/reportes.json', 'w', encoding='utf-8') as f:
            json.dump(reportes, f, indent=4, ensure_ascii=False)

        return jsonify({'success': True})

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

@app.route('/habitaciones_matriz')
def habitaciones_matriz():
    habitaciones = cargar_habitaciones()
    hoteles = cargar_hoteles()
    reservas = cargar_reservas()

    # Crear un diccionario para encontrar huésped por habitación
    reserva_info = {}
    for r in reservas:
        if r['estado'].lower() != 'cancelada':
            reserva_info[r['habitacion_n']] = {
                'huesped': r['huesped'],
                'celular': r['celular']
            }

    hoteles_dict = {h["id"]: h["hotel"] for h in hoteles}
    matriz = {}

    for h in habitaciones:
        hotel_nombre = hoteles_dict.get(h["hotel_id"], "Desconocido")
        if hotel_nombre not in matriz:
            matriz[hotel_nombre] = []
        # Agregar datos si hay reserva
        info = reserva_info.get(h["id"], {})
        h['huesped'] = info.get('huesped', 'N/A')
        h['celular'] = info.get('celular', 'N/A')
        matriz[hotel_nombre].append(h)

    return render_template("habitaciones_matriz.html", matriz=matriz)




@app.route('/micuenta')
def micuenta():
    if 'user' not in session:
        return redirect(url_for('home'))
    
    usuarios = load_users()
    usuario = next((u for u in usuarios if u["user"] == session["user"]), None)

    if not usuario:
        return redirect(url_for('home'))  # Por seguridad

    return render_template('micuenta.html', usuario=usuario)
















if __name__ == '__main__':
    app.run(debug=True)