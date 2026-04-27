# -------------------------
# IMPORTS (librerías)
# -------------------------

from flask import Flask, request, redirect, render_template
import sqlite3
from datetime import datetime
import os

# -------------------------
# CREAR LA APP FLASK
# -------------------------

app = Flask(__name__)

# Base de datos (Render permite escribir solo en /tmp)
DB = os.path.join("/tmp", "horario.db")


# -------------------------
# FUNCIÓN PARA CONECTAR A LA BASE DE DATOS
# (y crear la tabla si no existe)
# -------------------------

def conectar():
    con = sqlite3.connect(DB, check_same_thread=False)

    # Crear la tabla si no existe
    con.execute("""
        CREATE TABLE IF NOT EXISTS horarios (
            fecha TEXT,
            entrada TEXT,
            salida TEXT,
            horas REAL
        )
    """)

    return con


# -------------------------
# RUTA PRINCIPAL "/"
# -------------------------

@app.route("/", methods=["GET", "POST"])
def index():

    # -------------------------
    # SI EL USUARIO ENVÍA EL FORMULARIO
    # -------------------------
    if request.method == "POST":
        try:
            # Leer datos del formulario
            fecha = request.form["fecha"]
            entrada = request.form["entrada"]
            salida = request.form["salida"]

            # Convertir horas a datetime
            hora_entrada = datetime.strptime(entrada, "%H:%M")
            hora_salida = datetime.strptime(salida, "%H:%M")

            # Comprobar que la salida es posterior a la entrada
            if hora_salida <= hora_entrada:
                raise ValueError("La hora de salida debe ser posterior a la de entrada")

            # Calcular horas trabajadas
            horas = round((hora_salida - hora_entrada).seconds / 3600, 2)

            # Guardar en la base de datos
            con = conectar()
            con.execute(
                "INSERT INTO horarios (fecha, entrada, salida, horas) VALUES (?, ?, ?, ?)",
                (fecha, entrada, salida, horas)
            )
            con.commit()
            con.close()

            # Volver a la página principal
            return redirect("/")

        except Exception as error:
            return f"Error al guardar los datos: {error}"


    # -------------------------
    # SI EL USUARIO SOLO ENTRA A VER LA WEB (GET)
    # -------------------------

    con = conectar()
    datos = con.execute(
        "SELECT fecha, entrada, salida, horas FROM horarios ORDER BY fecha"
    ).fetchall()
    con.close()

    # Enviar los datos al HTML
    return render_template("index.html", datos=datos)


# -------------------------
# ARRANQUE LOCAL (solo para pruebas)
# -------------------------

if __name__ == "__main__":
    app.run(debug=True)
