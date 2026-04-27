from flask import Flask, request, redirect, render_template_string
import sqlite3
from datetime import datetime

app = Flask(__name__)
DB = "horario.db"

def conectar():
    return sqlite3.connect(DB)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        fecha = request.form["fecha"]
        entrada = request.form["entrada"]
        salida = request.form["salida"]

        e = datetime.strptime(entrada, "%H:%M")
        s = datetime.strptime(salida, "%H:%M")
        horas = round((s - e).seconds / 3600, 2)

        con = conectar()
        con.execute("""
            INSERT INTO horarios (fecha, entrada, salida, horas)
            VALUES (?, ?, ?, ?)
        """, (fecha, entrada, salida, horas))
        con.commit()
        con.close()

        return redirect("/")

    con = conectar()
    datos = con.execute("SELECT * FROM horarios ORDER BY fecha").fetchall()
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

if __name__ == "__main__":
    con = conectar()
    con.execute("""
        CREATE TABLE IF NOT EXISTS horarios (
            fecha TEXT,
            entrada TEXT,
            salida TEXT,
            horas REAL
        )
    """)
    con.close()

    app.run()
