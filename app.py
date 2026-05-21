from flask import Flask, request, redirect, url_for, session
import requests
from componentes import BarraNivelAgua

app = Flask(__name__)

app.secret_key = "clave_secreta_tinaco"

USUARIO_CORRECTO = "admin"
PASSWORD_CORRECTO = "1234"

FIREBASE_URL = "https://proyectoiot-4b519-default-rtdb.firebaseio.com/tinaco.json"


@app.route("/", methods=["GET", "POST"])
def login():
    error = ""

    if request.method == "POST":
        usuario = request.form.get("usuario")
        password = request.form.get("password")

        if usuario == USUARIO_CORRECTO and password == PASSWORD_CORRECTO:
            session["logueado"] = True
            return redirect(url_for("dashboard"))
        else:
            error = "Usuario o contraseña incorrectos"

    return f"""
    <html>
    <head>
        <title>Login Tinaco</title>
        <style>
            body {{
                font-family: Arial;
                background: #eef2f3;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
            }}

            .login {{
                background: white;
                padding: 30px;
                border-radius: 15px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.2);
                text-align: center;
                width: 300px;
            }}

            input {{
                width: 90%;
                padding: 10px;
                margin: 8px;
                border-radius: 8px;
                border: 1px solid #ccc;
            }}

            button {{
                width: 95%;
                padding: 10px;
                background: #1e88e5;
                color: white;
                border: none;
                border-radius: 8px;
                cursor: pointer;
            }}

            .error {{
                color: red;
                margin-top: 10px;
            }}
        </style>
    </head>

    <body>
        <div class="login">
            <h2>Acceso al sistema</h2>

            <form method="POST">
                <input type="text" name="usuario" placeholder="Usuario" required>
                <input type="password" name="password" placeholder="Contraseña" required>
                <button type="submit">Entrar</button>
            </form>

            <div class="error">{error}</div>
        </div>
    </body>
    </html>
    """


@app.route("/dashboard")
def dashboard():
    if not session.get("logueado"):
        return redirect(url_for("login"))

    try:
        respuesta = requests.get(FIREBASE_URL, timeout=5)
        datos = respuesta.json()

        porcentaje = float(datos.get("porcentaje_agua", 0))
        porcentaje = round(porcentaje, 1)

        hora = datos.get("hora_chequeo", "Sin datos")

    except Exception as e:
        print("Error leyendo Firebase:", e)
        porcentaje = 0
        hora = "Error al leer Firebase"

    barra = BarraNivelAgua("Nivel del Tinaco", porcentaje)

    return f"""
    <html>
    <head>
        <title>Sistema Tinaco IoT</title>
        <meta http-equiv="refresh" content="5">

        <style>
            body {{
                font-family: Arial;
                background: #eef2f3;
                margin: 0;
                padding: 20px;
            }}

            .contenedor {{
                max-width: 480px;
                margin: auto;
            }}

            h1 {{
                text-align: center;
                color: #1e3a5f;
            }}

            .card {{
                background: white;
                padding: 20px;
                border-radius: 18px;
                margin-top: 20px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                text-align: center;
            }}

            .nivel-numero {{
                font-size: 55px;
                font-weight: bold;
                color: #1e3a5f;
            }}

            .barra-contenedor {{
                width: 100%;
                height: 32px;
                background: #ddd;
                border-radius: 20px;
                overflow: hidden;
                margin: 18px 0;
            }}

            .barra-relleno {{
                height: 100%;
                border-radius: 20px;
            }}

            .estado {{
                font-size: 22px;
                font-weight: bold;
            }}

            .dato {{
                font-size: 20px;
                margin: 12px 0;
            }}

            .logout {{
                display: block;
                text-align: center;
                margin-top: 20px;
                color: red;
                font-weight: bold;
                text-decoration: none;
            }}
        </style>
    </head>

    <body>
        <div class="contenedor">
            <h1>Sistema IoT de Tinaco</h1>

            {barra.render()}

            <div class="card">
                <div class="dato"><b>Hora del chequeo:</b> {hora}</div>
            </div>

            <a class="logout" href="/logout">Cerrar sesión</a>
        </div>
    </body>
    </html>
    """


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=False)