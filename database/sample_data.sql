-- Insertar algunos libros
INSERT INTO libros (titulo, autor, anio_publicacion, cantidad_disponible) VALUES
('Cien Años de Soledad', 'Gabriel García Márquez', 1967, 5),
('Don Quijote de la Mancha', 'Miguel de Cervantes', 1605, 3),
('El Principito', 'Antoine de Saint-Exupéry', 1943, 10);

-- Insertar algunos miembros
INSERT INTO miembros (nombre, email) VALUES
('Ana Torres', 'ana.torres@email.com'),
('Carlos Ruiz', 'carlos.ruiz@email.com');

-- Registrar un préstamo usando el procedimiento almacenado (15 días de préstamo)
CALL registrar_prestamo(1, 1, 15); -- Ana Torres toma prestado 'Cien Años de Soledad'