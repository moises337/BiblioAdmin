-- Función que se ejecutará con el trigger
CREATE OR REPLACE FUNCTION log_cambio_libro()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF (TG_OP = 'DELETE') THEN
        INSERT INTO log_auditoria_libros (libro_id, titulo_libro, operacion)
        VALUES (OLD.id, OLD.titulo, 'DELETE');
        RETURN OLD;
    ELSIF (TG_OP = 'UPDATE') THEN
        INSERT INTO log_auditoria_libros (libro_id, titulo_libro, operacion)
        VALUES (NEW.id, NEW.titulo, 'UPDATE');
        RETURN NEW;
    ELSIF (TG_OP = 'INSERT') THEN
        INSERT INTO log_auditoria_libros (libro_id, titulo_libro, operacion)
        VALUES (NEW.id, NEW.titulo, 'INSERT');
        RETURN NEW;
    END IF;
    RETURN NULL;
END;
$$;

-- Creación del Trigger que se activa después de cualquier cambio en la tabla 'libros'
CREATE TRIGGER trigger_auditoria_libros
AFTER INSERT OR UPDATE OR DELETE ON libros
FOR EACH ROW EXECUTE FUNCTION log_cambio_libro();