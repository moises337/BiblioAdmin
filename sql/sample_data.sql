-- Insertar algunos libros
-- Insertar algunos libros para iniciar
INSERT INTO libros (titulo, autor, anio_publicacion, cantidad_disponible) VALUES
('Cien Años de Soledad', 'Gabriel García Márquez', 1967, 5),
('Don Quijote de la Mancha', 'Miguel de Cervantes', 1605, 3),
('El Principito', 'Antoine de Saint-Exupéry', 1943, 10),
('1984', 'George Orwell', 1949, 7),
('Ficciones', 'Jorge Luis Borges', 1944, 4);

-- Insertar algunos miembros para iniciar
INSERT INTO miembros (nombre, email) VALUES
('Ana Torres', 'ana.torres@email.com'),
('Carlos Ruiz', 'carlos.ruiz@email.com'),
('Luisa Fernandez', 'luisa.fernandez@email.com');

-- Registrar un préstamo de ejemplo usando el procedimiento almacenado
-- Ana Torres (id=1) toma prestado 'Cien Años de Soledad' (id=1) por 15 días.
CALL registrar_prestamo(1, 1);

-- Registrar otro préstamo
-- Carlos Ruiz (id=2) toma prestado '1984' (id=4) por 15 días.
CALL registrar_prestamo(4, 2);