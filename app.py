from flask import Flask, request, redirect, render_template_string
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)
DB = os.path.join("/tmp", "horario.db")

def conectar():
    con = sqlite3.connect(DB, check_same_thread=False)
    con.execute("""
        CREATE TABLE IF NOT EXISTS horarios (
            fecha TEXT,
            entrada TEXT,
            salida TEXT,
            horas REAL
        )
    """)
    return con

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        try:
            fecha = request.form["fecha"]
            entrada = request.form["entrada"]
            salida = request.form["salida"]

            e = datetime.strptime(entrada, "%H:%M")
            s = datetime.strptime(salida, "%H:%M")
            if s <= e:
                raise ValueError("La salida debe ser posterior a la entrada")

            horas = round((s - e).seconds / 3600, 2)

            con = conectar()
            con.execute(
                "INSERT INTO horarios (fecha, entrada, salida, horas) VALUES (?, ?, ?, ?)",
                (fecha, entrada, salida, horas)
            )
            con.commit()
            con.close()

            return redirect("/")

        except Exception as err:
            return f"Error: {err}"

    con = conectar()
    datos = con.execute(
        "SELECT fecha, entrada, salida, horas FROM horarios ORDER BY fecha"
    ).fetchall()
    con.close()

    return render_template_string("""
    <h2>🕒 Horario mensual</h2>
    <form method="post">
        Fecha: <input type="date" name="fecha" required><br>
        Entrada: <input type="time" name="entrada" required><br>
        Salida: <input type="time" name="salida" required><br>
        <button>Guardar</button>
    </form>
    <hr>
    <h3>Registros</h3>
    {% for f,e,s,h in datos %}
        {{f}} → {{h}} horas<br>
    {% endfor %}
    """, datos=datos)
