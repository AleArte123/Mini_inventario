from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
from config import db_config  # Importamos la configuración de conexión

app = Flask(__name__)

app.secret_key = 'super_admin_zxc'


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

# Ruta para el formulario de loggeo


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        nombre = request.form['nombre']
        contrasena = request.form['contrasena']

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM usuarios WHERE nombre = %s AND contrasena = %s", (nombre, contrasena))
        usuario = cursor.fetchone()
        cursor.close()
        conn.close()

        if usuario:
            session['usuario'] = usuario[1]       # nombre
            session['rol'] = usuario[3]           # rol (admin o usuario)
            return redirect(url_for('mostrar_medicamentos'))
        else:
            error = "Usuario o contraseña incorrectos"

    return render_template('login.html', error=error)

# Ruta para eliminar medicamentos


@app.route('/eliminar/<int:id>', methods=['GET'])
def eliminar_medicamento(id):

    # Validar si hay sesión activa y si el rol es 'admin'

    if 'rol' not in session or session['rol'] != 'admin':
        return "Acceso denegado: Solo administradores pueden eliminar medicamentos.", 403

    # Conexión a la base de datos
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # Ejecutar la eliminación
    cursor.execute("DELETE FROM medicamentos WHERE id = %s", (id,))
    conn.commit()

    cursor.close()
    conn.close()

    # Redirigir a la lista
    return redirect(url_for('mostrar_medicamentos'))

  # Ruta para cerrar sesión


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/movimientos')
def ver_movimientos():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT m.id, med.nombre, m.tipo, m.cantidad, m.fecha, m.observacion
        FROM movimientos m
        JOIN medicamentos med ON m.medicamento_id = med.id
        ORDER BY m.fecha DESC
    """)
    movimientos = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('movimientos.html', movimientos=movimientos)


@app.route('/registrar_movimiento', methods=['GET', 'POST'])
def registrar_movimiento():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    if request.method == 'POST':
        medicamento_id = request.form['medicamento_id']
        tipo = request.form['tipo']
        cantidad = int(request.form['cantidad'])
        observacion = request.form['observacion']

        cursor.execute("""
            INSERT INTO movimientos (medicamento_id, tipo, cantidad, observacion)
            VALUES (%s, %s, %s, %s)
        """, (medicamento_id, tipo, cantidad, observacion))
        conn.commit()
        cursor.close()
        conn.close()

        return redirect(url_for('ver_movimientos'))

    # Si es GET, obtener lista de medicamentos para el select
    cursor.execute("SELECT id, nombre FROM medicamentos")
    medicamentos = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('registrar_movimiento.html', medicamentos=medicamentos)


# Ejecutar la app en modo debug
if __name__ == '__main__':
    app.run(debug=True)


# Recordar escalar este archivo al de la farmacia
