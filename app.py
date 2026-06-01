from flask import Flask, request, redirect, url_for, session
import requests
from componentes import BarraNivelAgua

app = Flask(__name__)
app.secret_key = "clave_secreta_tinaco"

USUARIO_CORRECTO = "admin"
PASSWORD_CORRECTO = "1234"

BASE_URL = "https://proyectoiot-4b519-default-rtdb.firebaseio.com"
TINACO_URL = BASE_URL + "/tinaco.json"
HISTORIAL_URL = BASE_URL + "/historial.json"
CONTROL_BOMBA_URL = BASE_URL + "/tinaco/control_bomba.json"


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


@app.route("/control/<modo>")
def cambiar_control_bomba(modo):
    if not session.get("logueado"):
        return redirect(url_for("login"))

    modo = modo.upper()

    if modo not in ["AUTO", "ENCENDER", "APAGAR"]:
        return redirect(url_for("dashboard"))

    try:
        requests.put(CONTROL_BOMBA_URL, json=modo, timeout=5)
    except Exception as e:
        print("Error cambiando control de bomba:", e)

    return redirect(url_for("dashboard"))


@app.route("/dashboard")
def dashboard():
    if not session.get("logueado"):
        return redirect(url_for("login"))

    porcentaje = 0
    hora = "Sin datos"
    estado = "Sin datos"
    bomba = "Sin datos"
    control_bomba = "AUTO"
    historial_filas = ""

    try:
        r = requests.get(TINACO_URL, timeout=5)
        datos = r.json() or {}

        porcentaje = round(float(datos.get("porcentaje_agua", 0)), 1)
        hora = datos.get("hora_chequeo", "Sin datos")
        estado = datos.get("estado", "Sin datos")
        bomba = datos.get("bomba", "Sin datos")
        control_bomba = datos.get("control_bomba", "AUTO")

    except Exception as e:
        print("Error leyendo tinaco:", e)
        hora = "Error al leer Firebase"
        estado = "Error"
        bomba = "Error"
        control_bomba = "Error"

    try:
        r_hist = requests.get(HISTORIAL_URL, timeout=5)
        historial = r_hist.json() or {}

        lista = list(historial.values())
        ultimas = lista[-4:]
        ultimas.reverse()

        for lectura in ultimas:
            h = lectura.get("hora_chequeo", "--")
            p = lectura.get("porcentaje_agua", "--")
            e = lectura.get("estado", "--")
            b = lectura.get("bomba", "--")

            historial_filas += f"""
            <tr>
                <td>{h}</td>
                <td>{p}%</td>
                <td>{e}</td>
                <td>{b}</td>
            </tr>
            """

    except Exception as e:
        print("Error leyendo historial:", e)
        historial_filas = """
        <tr>
            <td colspan="4">Sin historial disponible</td>
        </tr>
        """

    if historial_filas == "":
        historial_filas = """
        <tr>
            <td colspan="4">Aún no hay historial</td>
        </tr>
        """

    barra = BarraNivelAgua("Nivel actual del Tinaco", porcentaje)

    return f"""
    <html>
    <head>
        <title>Sistema Tinaco IoT</title>
        <meta http-equiv="refresh" content="5">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">

        <style>
            body {{
                font-family: Arial, sans-serif;
                background: #eef2f3;
                margin: 0;
                padding: 20px;
            }}
            .contenedor {{
                max-width: 560px;
                margin: auto;
            }}
            h1 {{
                text-align: center;
                color: #1e3a5f;
                margin-bottom: 5px;
            }}
            .subtitulo {{
                text-align: center;
                color: #555;
                margin-bottom: 20px;
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
                transition: width 0.5s ease;
            }}
            .estado {{
                font-size: 22px;
                font-weight: bold;
            }}
            .dato {{
                font-size: 19px;
                margin: 10px 0;
            }}
            .bomba {{
                font-size: 21px;
                font-weight: bold;
                margin: 12px 0;
                color: #1e3a5f;
            }}
            .botones {{
                display: flex;
                gap: 8px;
                justify-content: center;
                flex-wrap: wrap;
                margin-top: 15px;
            }}
            .btn {{
                padding: 10px 14px;
                border-radius: 8px;
                color: white;
                text-decoration: none;
                font-weight: bold;
                font-size: 14px;
            }}
            .auto {{
                background: #1e88e5;
            }}
            .on {{
                background: #388e3c;
            }}
            .off {{
                background: #d32f2f;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 12px;
                font-size: 14px;
            }}
            th {{
                background: #1e3a5f;
                color: white;
                padding: 10px;
            }}
            td {{
                padding: 10px;
                border-bottom: 1px solid #ddd;
                text-align: center;
            }}
            tr:nth-child(even) {{
                background: #f5f5f5;
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
            <div class="subtitulo">Monitoreo de nivel de agua</div>

            {barra.render()}

            <div class="card">
                <div class="dato"><b>Estado actual:</b> {estado}</div>
                <div class="bomba">Bomba: {bomba}</div>
                <div class="dato"><b>Control:</b> {control_bomba}</div>
                <div class="dato"><b>Hora del chequeo:</b> {hora}</div>

                <div class="botones">
                    <a class="btn auto" href="/control/AUTO">Automático</a>
                    <a class="btn on" href="/control/ENCENDER">Encender bomba</a>
                    <a class="btn off" href="/control/APAGAR">Apagar bomba</a>
                </div>
            </div>

            <div class="card">
                <h2>Últimas 4 actualizaciones</h2>
                <table>
                    <tr>
                        <th>Hora</th>
                        <th>Nivel</th>
                        <th>Estado</th>
                        <th>Bomba</th>
                    </tr>
                    {historial_filas}
                </table>
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
    app.run(debug=False)
