import os
import sqlite3
import streamlit as st
import pandas as pd

# Crear una carpeta para guardar las fotos subidas
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Archivo CSV para almacenar los registros de usuarios
USER_DATA_FILE = 'user_data.csv'

# Función para cargar datos de usuarios
def load_user_data():
    if os.path.exists(USER_DATA_FILE):
        return pd.read_csv(USER_DATA_FILE)
    else:
        return pd.DataFrame(columns=['username', 'password', 'user_type'])

# Función para guardar datos de usuarios
def save_user_data(user_data):
    user_data.to_csv(USER_DATA_FILE, index=False)

# Cargar datos de usuarios
user_data = load_user_data()

st.title("Registro de Usuarios")

# Formulario de registro
username = st.text_input("Nombre de usuario")
password = st.text_input("Contraseña", type="password")
user_type = st.selectbox("Tipo de usuario", ["Estudiante", "Propietario"])
register_button = st.button("Registrarse")

if register_button:
    if username and password and user_type:
        if username in user_data['username'].values:
            st.warning("El nombre de usuario ya está registrado.")
        else:
            new_user = pd.DataFrame({'username': [username], 'password': [password], 'user_type': [user_type]})
            user_data = pd.concat([user_data, new_user], ignore_index=True)
            save_user_data(user_data)
            st.success("Usuario registrado exitosamente.")
    else:
        st.warning("Por favor, complete todos los campos.")


        # Función para verificar el tipo de usuario
        def get_user_type(username):
            user = user_data[user_data['username'] == username]
            if not user.empty:
                return user.iloc[0]['user_type']
            return None


        # Formulario de inicio de sesión
        st.title("Inicio de Sesión")
        login_username = st.text_input("Nombre de usuario", key="login_username")
        login_password = st.text_input("Contraseña", type="password", key="login_password")
        login_button = st.button("Iniciar Sesión")

        if login_button:
            user_type = get_user_type(login_username)
            if user_type:
                if user_type == "Estudiante":
                    st.success("Bienvenido, Estudiante. Acceso gratuito.")
                    # Funcionalidades gratuitas para estudiantes
                elif user_type == "Propietario":
                    st.warning("Bienvenido, Propietario. Acceso pago.")
                    # Funcionalidades pagas para propietarios
            else:
                st.error("Usuario o contraseña incorrectos.")

# Formulario para subir fotos y distancia
uploaded_files = st.file_uploader("Sube tus fotos aquí", accept_multiple_files=True, type=["jpg", "jpeg", "png"], key="file_uploader_1")
distance = st.number_input("Distancia a la UNSAM (en km)", min_value=0.0, step=0.1, key="distance_input_1")

if uploaded_files:
    for uploaded_file in uploaded_files:
        # Guardar las fotos en la carpeta de uploads
        with open(os.path.join(UPLOAD_FOLDER, uploaded_file.name), "wb") as f:
            f.write(uploaded_file.getbuffer())
        # Guardar la distancia en un archivo de texto
        with open(os.path.join(UPLOAD_FOLDER, f"{uploaded_file.name}.txt"), "w") as f:
            f.write(str(distance))
        st.success(f"Archivo {uploaded_file.name} subido exitosamente con distancia {distance} km")

# Mostrar las fotos subidas con la distancia
st.header("Fotos Subidas")
uploaded_photos = os.listdir(UPLOAD_FOLDER)
for photo in uploaded_photos:
    if photo.endswith((".jpg", ".jpeg", ".png")):
        photo_path = os.path.join(UPLOAD_FOLDER, photo)
        distance_path = os.path.join(UPLOAD_FOLDER, f"{photo}.txt")
        if os.path.exists(distance_path):
            with open(distance_path, "r") as f:
                distance = f.read()
        else:
            distance = "No especificada"
        st.image(photo_path, caption=f"{photo} - Distancia a la UNSAM: {distance} km")

# Simular precios para las fotos subidas (en un caso real, estos precios vendrían de una base de datos)
photo_prices = {photo: (i + 1) * 100 for i, photo in enumerate(os.listdir(UPLOAD_FOLDER))}

# Control deslizante para seleccionar el rango de precios
min_price, max_price = st.slider("Selecciona el rango de precios", 0, 1000, (100, 500), key="price_slider_1")

# Filtrar las fotos en base al rango de precios seleccionado
filtered_photos = [photo for photo, price in photo_prices.items() if min_price <= price <= max_price]

# Mostrar las fotos filtradas
st.header("Fotos Filtradas por Precio")
for photo in filtered_photos:
    st.image(os.path.join(UPLOAD_FOLDER, photo), caption=f"{photo} - ${photo_prices[photo]}")

# Crear una carpeta para la base de datos
DB_FOLDER = 'database'
if not os.path.exists(DB_FOLDER):
    os.makedirs(DB_FOLDER)

# Conectar a la base de datos
conn = sqlite3.connect(os.path.join(DB_FOLDER, 'chat.db'))
c = conn.cursor()

# Crear la tabla de mensajes si no existe
c.execute('''
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user TEXT,
        message TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
''')
conn.commit()

# Función para agregar un mensaje a la base de datos
def add_message(user, message):
    c.execute('INSERT INTO messages (user, message) VALUES (?, ?)', (user, message))
    conn.commit()

# Función para obtener todos los mensajes de la base de datos
def get_messages():
    c.execute('SELECT user, message, timestamp FROM messages ORDER BY timestamp ASC')
    return c.fetchall()

st.title("Chat entre Propietarios y Estudiantes")

# Formulario para enviar mensajes
user = st.text_input("Usuario")
message = st.text_area("Mensaje")
send_button = st.button("Enviar")

if send_button and user and message:
    add_message(user, message)
    st.success("Mensaje enviado")

# Mostrar los mensajes
st.header("Mensajes")
messages = get_messages()
for msg in messages:
    st.write(f"{msg[2]} - **{msg[0]}**: {msg[1]}")

# Cerrar la conexión a la base de datos al final
conn.close()
