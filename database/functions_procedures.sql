-- Procedimiento Almacenado para registrar un nuevo préstamo
-- Verifica si hay stock, inserta el préstamo y actualiza la cantidad de libros.
CREATE OR REPLACE PROCEDURE registrar_prestamo(
    p_libro_id INT,
    p_miembro_id INT,
    p_dias_prestamo INT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_cantidad_actual INT;
BEGIN
    -- 1. Verificar si el libro existe y tiene stock
    SELECT cantidad_disponible INTO v_cantidad_actual FROM libros WHERE id = p_libro_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'El libro con ID % no existe.', p_libro_id;
    END IF;

    IF v_cantidad_actual < 1 THEN
        RAISE EXCEPTION 'No hay copias disponibles del libro "%".', (SELECT titulo FROM libros WHERE id = p_libro_id);
    END IF;

    -- 2. Insertar el nuevo préstamo
    INSERT INTO prestamos (libro_id, miembro_id, fecha_vencimiento)
    VALUES (p_libro_id, p_miembro_id, CURRENT_DATE + p_dias_prestamo);

    -- 3. Actualizar la cantidad de libros disponibles (restar 1)
    UPDATE libros SET cantidad_disponible = cantidad_disponible - 1 WHERE id = p_libro_id;

    COMMIT;
END;
$$;

-- Función para obtener los préstamos vencidos (que no han sido devueltos)
-- Esto cumple con el requisito de "Funciones SQL personalizadas" y "Consultas avanzadas"
CREATE OR REPLACE FUNCTION obtener_prestamos_vencidos()
RETURNS TABLE (
    prestamo_id INT,
    titulo_libro VARCHAR,
    nombre_miembro VARCHAR,
    fecha_prestamo DATE,
    fecha_vencimiento DATE
)
LANGUAGE sql
AS $$
    SELECT
        p.id AS prestamo_id,
        l.titulo AS titulo_libro,
        m.nombre AS nombre_miembro,
        p.fecha_prestamo,
        p.fecha_vencimiento
    FROM prestamos p
    JOIN libros l ON p.libro_id = l.id
    JOIN miembros m ON p.miembro_id = m.id
    WHERE p.fecha_devolucion IS NULL AND p.fecha_vencimiento < CURRENT_DATE;
$$;