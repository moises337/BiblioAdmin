from flask import Flask, render_template, request, redirect, url_for, flash
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import database as db

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'tu_clave_secreta_aqui') # Importante para que `flash` funcione

@app.route('/')
def dashboard():
    """Página principal con estadísticas."""
    try:
        total_libros_result = db.execute_query("SELECT COUNT(*) FROM libros;", fetch="one")
        total_miembros_result = db.execute_query("SELECT COUNT(*) FROM miembros;", fetch="one")
        prestamos_activos_result = db.execute_query("SELECT COUNT(*) FROM prestamos WHERE fecha_devolucion IS NULL;", fetch="one")
        
        total_libros = total_libros_result[0] if total_libros_result else 0
        total_miembros = total_miembros_result[0] if total_miembros_result else 0
        prestamos_activos = prestamos_activos_result[0] if prestamos_activos_result else 0
        
        return render_template('dashboard.html', total_libros=total_libros, total_miembros=total_miembros, prestamos_activos=prestamos_activos)
    except Exception as e:
        flash(f'Error al cargar el dashboard: {e}', 'danger')
        return render_template('dashboard.html', total_libros=0, total_miembros=0, prestamos_activos=0)

# --- Rutas para Libros ---
@app.route('/libros')
def listar_libros():
    try:
        libros = db.execute_query("SELECT * FROM libros ORDER BY titulo;", fetch="all")
        return render_template('libros.html', libros=libros or [])
    except Exception as e:
        flash(f'Error al cargar los libros: {e}', 'danger')
        return render_template('libros.html', libros=[])

@app.route('/libros/nuevo', methods=['GET', 'POST'])
def anadir_libro():
    if request.method == 'POST':
        try:
            titulo = request.form['titulo']
            autor = request.form['autor']
            anio = request.form['anio']
            cantidad = request.form['cantidad']
            db.execute_query(
                "INSERT INTO libros (titulo, autor, anio_publicacion, cantidad_disponible) VALUES (%s, %s, %s, %s);",
                (titulo, autor, anio, cantidad)
            )
            flash('¡Libro añadido con éxito!', 'success')
            return redirect(url_for('listar_libros'))
        except Exception as e:
            flash(f'Error al añadir el libro: {e}', 'danger')
    return render_template('formulario_libro.html')

# --- Rutas para Miembros ---
@app.route('/miembros')
def listar_miembros():
    try:
        miembros = db.execute_query("SELECT * FROM miembros ORDER BY nombre;", fetch="all")
        return render_template('miembros.html', miembros=miembros or [])
    except Exception as e:
        flash(f'Error al cargar los miembros: {e}', 'danger')
        return render_template('miembros.html', miembros=[])

# --- Rutas para Préstamos ---
@app.route('/prestamos')
def listar_prestamos():
    try:
        # Consulta avanzada con JOIN para mostrar información legible
        query = """
        SELECT p.id, l.titulo, m.nombre, p.fecha_prestamo, p.fecha_vencimiento, p.fecha_devolucion
        FROM prestamos p
        JOIN libros l ON p.libro_id = l.id
        JOIN miembros m ON p.miembro_id = m.id
        ORDER BY p.fecha_prestamo DESC;
        """
        prestamos = db.execute_query(query, fetch="all")
        return render_template('prestamos.html', prestamos=prestamos or [])
    except Exception as e:
        flash(f'Error al cargar los préstamos: {e}', 'danger')
        return render_template('prestamos.html', prestamos=[])

@app.route('/prestamos/nuevo', methods=['GET', 'POST'])
def anadir_prestamo():
    if request.method == 'POST':
        try:
            libro_id = request.form['libro_id']
            miembro_id = request.form['miembro_id']
            # Llamamos al procedimiento almacenado
            db.execute_query("CALL registrar_prestamo(%s, %s, 15);", (libro_id, miembro_id))
            flash('Préstamo registrado con éxito.', 'success')
        except Exception as e:
            flash(f'Error al registrar el préstamo: {e}', 'danger')
        return redirect(url_for('listar_prestamos'))
    
    try:
        # Preparamos los datos para los dropdowns del formulario
        libros_disponibles = db.execute_query("SELECT id, titulo FROM libros WHERE cantidad_disponible > 0 ORDER BY titulo;", fetch="all")
        miembros = db.execute_query("SELECT id, nombre FROM miembros ORDER BY nombre;", fetch="all")
        return render_template('formulario_prestamo.html', libros=libros_disponibles or [], miembros=miembros or [])
    except Exception as e:
        flash(f'Error al cargar el formulario: {e}', 'danger')
        return render_template('formulario_prestamo.html', libros=[], miembros=[])

@app.route('/prestamos/<int:id>/devolver', methods=['POST'])
def devolver_prestamo(id):
    # Marcar un libro como devuelto y aumentar el stock
    # Esto demuestra una transacción simple
    conn = db.get_db_connection()
    try:
        cur = conn.cursor()
        # 1. Actualizar la fecha de devolución
        cur.execute("UPDATE prestamos SET fecha_devolucion = CURRENT_DATE WHERE id = %s RETURNING libro_id;", (id,))
        libro_id = cur.fetchone()[0]
        # 2. Aumentar el stock del libro
        cur.execute("UPDATE libros SET cantidad_disponible = cantidad_disponible + 1 WHERE id = %s;", (libro_id,))
        conn.commit()
        flash('Devolución registrada correctamente.', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'Error al registrar la devolución: {e}', 'danger')
    finally:
        db.release_db_connection(conn)
    return redirect(url_for('listar_prestamos'))

if __name__ == '__main__':
    # Solo usar debug=True en desarrollo
    debug_mode = os.environ.get('FLASK_ENV') != 'production'
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=debug_mode, host='0.0.0.0', port=port)

# Para gunicorn, exportamos la app
app_for_gunicorn = app