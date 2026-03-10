# 🍰 Stiman Dessert - Configuración de Base de Datos Supabase (PostgreSQL)

## ✅ Configuración completada

Tu proyecto ahora está configurado para usar **PostgreSQL en Supabase Cloud**.

### 📊 Detalles de la Base de Datos

- **Proveedor:** Supabase (PostgreSQL)
- **Base de Datos:** `sweet_house`
- **Host:** `db.ypqywzdpghsmhqslifwz.supabase.co`
- **Puerto:** `5432`
- **Usuario:** `postgres.ypqywzdpghsmhqslifwz`
- **URL Supabase:** `https://ypqywzdpghsmhqslifwz.supabase.co`
- **SSL:** Requerido (configurado automáticamente)

### 🔐 Variables de Entorno

Las credenciales están en el archivo `.env` (NO se commitea al repositorio).
Usa `.env.example` como referencia.

### 🚀 Desarrollo Local

1. **Configura las variables de entorno:**
   ```powershell
   # Copia .env.example a .env y llena los valores reales
   copy .env.example .env
   ```

2. **Activa el entorno virtual:**
   ```powershell
   .\env\Scripts\Activate.ps1
   ```

3. **Instala dependencias:**
   ```powershell
   pip install -r requirements.txt
   ```

4. **Aplica migraciones:**
   ```powershell
   python manage.py migrate
   ```

5. **Inicia el servidor Django:**
   ```powershell
   python manage.py runserver
   ```

### 🐳 Docker (Producción)

1. **Construye y levanta los contenedores:**
   ```bash
   docker-compose up --build -d
   ```

2. **Verifica el estado:**
   ```bash
   docker-compose ps
   docker-compose logs -f web
   ```

3. **Accede a la aplicación:**
   - Aplicación: `http://localhost/`
   - Admin: `http://localhost/admin/`

### 📱 Acceso a la Base de Datos

**Opción 1: Dashboard de Supabase (recomendado)**
- URL: `https://supabase.com/dashboard/project/ypqywzdpghsmhqslifwz`

**Opción 2: Terminal psql**
```powershell
psql "postgresql://postgres.ypqywzdpghsmhqslifwz:[PASSWORD]@db.ypqywzdpghsmhqslifwz.supabase.co:5432/sweet_house"
```

### 🔄 Comandos útiles Django

```powershell
# Crear migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Recolectar archivos estáticos (producción)
python manage.py collectstatic --noinput
```

### 🐳 Comandos Docker útiles

```bash
# Levantar contenedores
docker-compose up -d

# Ver logs en tiempo real
docker-compose logs -f

# Parar contenedores
docker-compose down

# Reconstruir imagen
docker-compose build --no-cache

# Ejecutar comando Django dentro del contenedor
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
```

### 📝 Arquitectura del proyecto

```
Stiman-Dessert/
├── .env                    # Variables de entorno (NO commitear)
├── .env.example            # Plantilla de variables de entorno
├── .gitignore              # Archivos excluidos de Git
├── .dockerignore           # Archivos excluidos de Docker
├── Dockerfile              # Imagen Docker para producción
├── docker-compose.yml      # Orquestación de servicios
├── entrypoint.sh           # Script de inicio del contenedor
├── requirements.txt        # Dependencias Python
├── manage.py               # CLI de Django
├── stimandessert/           # Configuración del proyecto Django
│   ├── settings.py         # Settings con soporte Supabase
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── tienda/                 # App de la tienda
├── web/                    # App web (solicitudes, feedback)
├── templates/              # Plantillas HTML
├── static/                 # Archivos estáticos
├── media/                  # Archivos subidos
└── nginx/
    └── nginx.conf          # Configuración Nginx
```

### ⚠️ Notas importantes

- La base de datos está en la nube (Supabase), no se necesita MySQL/XAMPP local
- El archivo `.env` NUNCA debe estar en el repositorio (está en `.gitignore`)
- Para producción, cambiar `DJANGO_DEBUG=False` en `.env`
- El SSL está habilitado por defecto para la conexión a Supabase
- Docker usa **Gunicorn** como servidor WSGI y **Nginx** como reverse proxy
