-- Tabla para los libros
CREATE TABLE libros (
    id SERIAL PRIMARY KEY,
    titulo VARCHAR(255) NOT NULL,
    autor VARCHAR(255) NOT NULL,
    anio_publicacion INT,
    cantidad_disponible INT NOT NULL CHECK (cantidad_disponible >= 0)
);

-- Tabla para los miembros de la biblioteca
CREATE TABLE miembros (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    fecha_registro DATE DEFAULT CURRENT_DATE
);

-- Tabla para registrar los préstamos
CREATE TABLE prestamos (
    id SERIAL PRIMARY KEY,
    libro_id INT REFERENCES libros(id) ON DELETE CASCADE,
    miembro_id INT REFERENCES miembros(id) ON DELETE CASCADE,
    fecha_prestamo DATE DEFAULT CURRENT_DATE,
    fecha_vencimiento DATE NOT NULL,
    fecha_devolucion DATE
);

-- Tabla de auditoría para registrar cambios en la tabla de libros
CREATE TABLE log_auditoria_libros (
    id SERIAL PRIMARY KEY,
    libro_id INT,
    titulo_libro VARCHAR(255),
    operacion VARCHAR(10) NOT NULL, -- 'INSERT', 'UPDATE', 'DELETE'
    usuario VARCHAR(100) DEFAULT CURRENT_USER,
    fecha_operacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);