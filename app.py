from flask import Flask, request, redirect, render_template
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
        fecha = request.form["fecha"]
        entrada = request.form["entrada"]
        salida = request.form["salida"]

        h_entrada = datetime.strptime(entrada, "%H:%M")
        h_salida = datetime.strptime(salida, "%H:%M")

        if h_salida <= h_entrada:
            return "Error: la salida debe ser posterior a la entrada"

        horas = round((h_salida - h_entrada).seconds / 3600, 2)

        con = conectar()
        con.execute(
            "INSERT INTO horarios (fecha, entrada, salida, horas) VALUES (?, ?, ?, ?)",
            (fecha, entrada, salida, horas)
        )
        con.commit()
        con.close()

        return redirect("/")

    con = conectar()
    datos = con.execute(
        "SELECT fecha, entrada, salida, horas FROM horarios ORDER BY fecha"
    ).fetchall()
    con.close()

    return render_template("index.html", datos=datos)


if __name__ == "__main__":
    app.run(debug=True)