# Sistema de Gestión de Biblioteca

Una aplicación web Flask para gestionar libros, miembros y préstamos de una biblioteca.

## Características

- Gestión de libros (añadir, listar)
- Gestión de miembros
- Sistema de préstamos y devoluciones
- Dashboard con estadísticas
- Base de datos PostgreSQL
- Procedimientos almacenados y triggers

## Despliegue en Render

### 1. Configurar la Base de Datos

1. Crea un servicio PostgreSQL en Render
2. Copia la URL de conexión interna

### 2. Configurar la Aplicación Web

1. Conecta tu repositorio de GitHub
2. Configura las siguientes variables de entorno:
   - `DATABASE_URL`: URL de tu base de datos PostgreSQL
   - `SECRET_KEY`: Una clave secreta para Flask (genera una aleatoria)
   - `FLASK_ENV`: `production`

### 3. Inicializar la Base de Datos

Después del primer despliegue, ejecuta el script de inicialización:

```bash
python src/init_db.py
```

Esto creará las tablas necesarias y añadirá datos de ejemplo.

## Desarrollo Local

### 1. Clonar el Repositorio

```bash
git clone <tu-repositorio>
cd biblioadmin-app
```

### 2. Crear Entorno Virtual

```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar Variables de Entorno

Copia `.env.example` a `.env` y configura tus variables:

```bash
cp .env.example .env
```

Edita `.env` con tu configuración de base de datos local.

### 5. Inicializar Base de Datos

```bash
python src/init_db.py
```

### 6. Ejecutar la Aplicación

```bash
python src/index.py
```

La aplicación estará disponible en `http://localhost:5000`

## Estructura del Proyecto

```
├── src/
│   ├── index.py          # Aplicación Flask principal
│   ├── database.py       # Conexión y operaciones de BD
│   └── init_db.py        # Script de inicialización
├── database/
│   ├── create_tables.sql # Esquema de la BD
│   ├── functions_procedures.sql
│   ├── triggers.sql
│   └── sample_data.sql
├── templates/            # Plantillas HTML
├── static/              # Archivos estáticos (CSS, JS)
├── requirements.txt     # Dependencias Python
├── Procfile            # Configuración para Render
└── .env.example        # Variables de entorno de ejemplo
```

## Solución de Problemas

### Error: "module 'database' has no attribute 'execute_query'"

Este error se soluciona asegurándose de que:
1. El archivo `database.py` está en la ruta correcta
2. Las variables de entorno están configuradas
3. La base de datos está accesible

### Error de Conexión a la Base de Datos

1. Verifica que `DATABASE_URL` está correctamente configurada
2. Asegúrate de que la base de datos PostgreSQL está funcionando
3. Verifica que las credenciales son correctas

### La aplicación no inicia en Render

1. Verifica que el `Procfile` existe y tiene el contenido correcto
2. Asegúrate de que todas las variables de entorno están configuradas
3. Revisa los logs de Render para errores específicos