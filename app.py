from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
from config import db_config  # Importamos la configuración de conexión

app = Flask(__name__)


@app.route('/')
def index():
    return render_template("index.html")


# Ruta para mostrar los medicamentos

@app.route('/medicamentos', methods=['GET'])
def mostrar_medicamentos():
    # 1. Crear conexión a la base de datos
    conn = mysql.connector.connect(**db_config)

    # 2. Crear cursor para ejecutar consultas
    cursor = conn.cursor()

    # 3. Ejecutar consulta SQL
    cursor.execute("SELECT * FROM medicamentos")

    # 4. Obtener todos los resultados
    medicamentos = cursor.fetchall()

    # 5. Cerrar cursor y conexión
    cursor.close()
    conn.close()

    # 6. Renderizar plantilla HTML con los datos
    return render_template('medicamentos.html', medicamentos=medicamentos)


@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar_medicamento(id):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    if request.method == 'POST':
        nombre = request.form['nombre']
        presentacion = request.form['presentacion']
        fecha_vencimiento = request.form['fecha_vencimiento']

        cursor.execute("""
            UPDATE medicamentos
            SET nombre = %s, presentacion = %s, fecha_vencimiento = %s
            WHERE id = %s
        """, (nombre, presentacion, fecha_vencimiento, id))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('mostrar_medicamentos'))

    cursor.execute("SELECT * FROM medicamentos WHERE id = %s", (id,))
    medicamento = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('editar.html', medicamento=medicamento)


# Ejecutar la app en modo debug
if __name__ == '__main__':
    app.run(debug=True)
