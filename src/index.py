from flask import Flask, render_template, request, redirect, url_for, flash
import database as db

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_aqui' # Importante para que `flash` funcione

@app.route('/')
def dashboard():
    """Página principal con estadísticas."""
    total_libros = db.execute_query("SELECT COUNT(*) FROM libros;", fetch="one")[0]
    total_miembros = db.execute_query("SELECT COUNT(*) FROM miembros;", fetch="one")[0]
    prestamos_activos = db.execute_query("SELECT COUNT(*) FROM prestamos WHERE fecha_devolucion IS NULL;", fetch="one")[0]
    return render_template('dashboard.html', total_libros=total_libros, total_miembros=total_miembros, prestamos_activos=prestamos_activos)

# --- Rutas para Libros ---
@app.route('/libros')
def listar_libros():
    libros = db.execute_query("SELECT * FROM libros ORDER BY titulo;", fetch="all")
    return render_template('libros.html', libros=libros)

@app.route('/libros/nuevo', methods=['GET', 'POST'])
def anadir_libro():
    if request.method == 'POST':
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
    return render_template('formulario_libro.html')

# --- Rutas para Miembros ---
@app.route('/miembros')
def listar_miembros():
    miembros = db.execute_query("SELECT * FROM miembros ORDER BY nombre;", fetch="all")
    return render_template('miembros.html', miembros=miembros)

@app.route('/miembros/nuevo', methods=['GET', 'POST'])
def anadir_miembro():
    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        
        try:
            # Comprobar si el email ya existe para evitar errores de base de datos
            existe = db.execute_query("SELECT id FROM miembros WHERE email = %s;", (email,), fetch="one")
            if existe:
                flash('El correo electrónico ya está registrado.', 'warning')
                return redirect(url_for('anadir_miembro'))

            db.execute_query(
                "INSERT INTO miembros (nombre, email) VALUES (%s, %s);",
                (nombre, email)
            )
            flash('¡Miembro añadido con éxito!', 'success')
            return redirect(url_for('listar_miembros'))
        except Exception as e:
            flash(f'Error al añadir miembro: {e}', 'danger')
            
    return render_template('formulario_miembro.html')

@app.route('/miembros/<int:id>/editar', methods=['GET', 'POST'])
def editar_miembro(id):
    if request.method == 'POST':
        # Procesar los datos del formulario enviado
        nombre = request.form['nombre']
        email = request.form['email']
        try:
            db.execute_query(
                "UPDATE miembros SET nombre = %s, email = %s WHERE id = %s;",
                (nombre, email, id)
            )
            flash('¡Miembro actualizado con éxito!', 'success')
            return redirect(url_for('listar_miembros'))
        except Exception as e:
            flash(f'Error al actualizar el miembro: {e}', 'danger')
            return redirect(url_for('editar_miembro', id=id))

    # Si es GET, buscar el miembro y mostrar el formulario
    miembro = db.execute_query("SELECT * FROM miembros WHERE id = %s;", (id,), fetch="one")
    if not miembro:
        flash('Miembro no encontrado.', 'warning')
        return redirect(url_for('listar_miembros'))
    
    return render_template('editar_miembro.html', miembro=miembro)

@app.route('/miembros/<int:id>/eliminar', methods=['POST'])
def eliminar_miembro(id):
    try:
        # Una buena práctica sería verificar si el miembro tiene préstamos activos antes de borrar.
        # Por ahora, la restricción de la BD (ON DELETE CASCADE) lo manejará.
        db.execute_query("DELETE FROM miembros WHERE id = %s;", (id,))
        flash('Miembro eliminado correctamente.', 'success')
    except Exception as e:
        flash(f'Error al eliminar el miembro: {e}', 'danger')
    
    return redirect(url_for('listar_miembros'))

# --- Rutas para Préstamos ---
@app.route('/prestamos')
def listar_prestamos():
    # Consulta avanzada con JOIN para mostrar información legible
    query = """
    SELECT p.id, l.titulo, m.nombre, p.fecha_prestamo, p.fecha_vencimiento, p.fecha_devolucion
    FROM prestamos p
    JOIN libros l ON p.libro_id = l.id
    JOIN miembros m ON p.miembro_id = m.id
    ORDER BY p.fecha_prestamo DESC;
    """
    prestamos = db.execute_query(query, fetch="all")
    return render_template('prestamos.html', prestamos=prestamos)

@app.route('/prestamos/nuevo', methods=['GET', 'POST'])
def anadir_prestamo():
    if request.method == 'POST':
        libro_id = request.form['libro_id']
        miembro_id = request.form['miembro_id']
        # Llamamos al procedimiento almacenado
        try:
            db.execute_query("CALL registrar_prestamo(%s, %s, 15);", (libro_id, miembro_id))
            flash('Préstamo registrado con éxito.', 'success')
        except Exception as e:
            flash(f'Error al registrar el préstamo: {e}', 'danger')
        return redirect(url_for('listar_prestamos'))
    
    # Preparamos los datos para los dropdowns del formulario
    libros_disponibles = db.execute_query("SELECT id, titulo FROM libros WHERE cantidad_disponible > 0 ORDER BY titulo;", fetch="all")
    miembros = db.execute_query("SELECT id, nombre FROM miembros ORDER BY nombre;", fetch="all")
    return render_template('formulario_prestamo.html', libros=libros_disponibles, miembros=miembros)

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
    app.run(debug=True)

