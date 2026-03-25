# Stiman Dessert - Instrucciones para Agentes AI

## Descripción General del Proyecto
Stiman Dessert es una **plataforma de e-commerce basada en Django** para un negocio colombiano de postres. Proporciona gestión de catálogo de productos, funcionalidad de carrito de compras, solicitudes de pedidos y flujos de aprobación de administradores. La aplicación usa SQLite para desarrollo y soporta migración a MySQL.

## Arquitectura

### Componentes Principales
- **Django 5.2** con dos apps principales:
  - `tienda` (Tienda): Gestión de productos, carrito, checkout, solicitudes de pedidos
  - `web`: Solicitudes de administrador (flujo de aprobación para staff)
- **Base de Datos**: SQLite (dev) → MySQL/MariaDB (configurada en DATABASE_CONFIG.md)
- **Frontend**: Templates de Django + JavaScript vanilla (sin framework)
- **Autenticación**: Auth nativa de Django con login personalizado basado en email

### Modelos de Datos Clave
- **Producto** (`tienda/models.py`): Productos con categorías (postre, galleta, pudín, otro)
- **SolicitudPedido** (`web/models.py`): Solicitudes de pedidos personalizados (nombre, email, producto, cantidad, notas)
- **AdminRequest** (`web/models.py`): Solicitudes de aprobación para staff (pendiente/aprobado/rechazado)

### Estructura de URLs
- URLs raíz de app en `stimandessert/urls.py`
- URLs de app `tienda/` en `tienda/urls.py` (productos, carrito, checkout, solicitudes)
- Rutas de autenticación usan patrones nativa de Django + vista personalizada de login

## Patrones y Convenciones Críticos

### 1. Gestión del Carrito (Basada en Sesión)
El carrito se almacena en `request.session['cart']` como dict: `{producto_id: cantidad}`
- Se actualiza vía peticiones POST: `carrito/agregar/`, `carrito/actualizar/`, `carrito/eliminar/`
- El contexto del carrito siempre se proporciona vía `tienda/context_processors.py:cart_summary()`
- **Importante**: El context processor también construye el dict `productos_por_categoria` para navegación del catálogo con lógica de categorización personalizada (flanes, galletas, pudines, postres)

### 2. Validación de Formularios y Nombrado
- Validación de username: solo letras, mín 3 caracteres (`forms.py:validate_username_letters_only`)
- Form de producto (`ProductoForm`) usa help_texts descriptivos y atributos HTML5 personalizados (dropzone, contador, indicadores de moneda)
- ProductoForm está en views.py, no en forms.py (patrón de consolidación, pendiente refactorizar)

### 3. Modelo de Autenticación
- Usa el modelo User estándar de Django, pero almacena email en el campo `User.username`
- `EmailAuthenticationForm` personalizado solicita "Nombre de usuario" (campo username)
- `EmailUserCreationForm` personalizado requiere email + username + first_name
- Vista de login: `CustomLoginView` con `EmailAuthenticationForm`

### 4. Categorización de Productos
Los productos tienen un CharField `category` con opciones fijas. Pero las vistas del catálogo agregan categorización semántica:
- "flan" en name.lower() → categoría "flanes"
- category="galleta" → "galletas"
- category="pudin" → "pudines"
- Caso contrario → "postres"

Esta asignación está en `context_processors.py` y debe referenciarse al mostrar productos.

### 5. Manejo de Imágenes
- Imágenes cargadas a `MEDIA_ROOT/productos/`
- ImageField es nullable (`blank=True, null=True`)
- Script de seed (`scripts/seed_products.py`) importa imágenes preexistentes de media/
- Productos sin imágenes se muestran correctamente (sin enlaces rotos)

### 6. Flujo de Solicitudes
- **SolicitudPedido**: Solicitud pública de pedidos (puede ser anónima o autenticada)
- **AdminRequest**: Flujo interno de aprobación para staff (solo usuarios autenticados pueden solicitar estatus admin)
- Ambas usan timestamps `created_at` y ordenamiento predeterminado `-created_at` (más reciente primero)

## Flujos de Trabajo de Desarrolladores

### Setup e Inicialización
```bash
# Activar venv
.\env\Scripts\Activate.ps1

# Aplicar migraciones
python manage.py migrate

# Seed de productos de ejemplo (si la bd está vacía)
python scripts/seed_products.py

# Iniciar servidor dev
python manage.py runserver
```

### Comandos de Gestión Comunes
- `python manage.py createsuperuser` - Crear cuenta de admin
- `python manage.py makemigrations` - Crear archivos de migración
- `python manage.py showmigrations` - Listar migraciones aplicadas
- Comando personalizado: `python manage.py load_products` (en `tienda/management/commands/`)

### Configuración de Base de Datos
- **Desarrollo**: SQLite (`db.sqlite3` en raíz del repositorio)
- **Lista para Producción**: Backend MySQL configurado en `settings.py` con adaptador PyMySQL (sin compilación de mysqlclient)
- Credenciales: Ver `DATABASE_CONFIG.md` para setup de XAMPP MySQL
- **Importante**: Si cambias a MySQL, asegúrate de que PyMySQL esté instalado y `DATABASES['default']` en settings.py esté actualizado

### Testing y Debugging
- No hay archivos de test existentes detectados (archivos de test son stubs vacíos)
- Modo debug: `DEBUG=True` en settings.py (INSEGURO - cambiar para producción)
- Backend de email en consola para desarrollo (emails impresos en consola)

## Convenciones de Templates y Archivos Estáticos

### Templates Clave
- `base.html` - Layout base con navbar, resumen de carrito, footer
- `tienda/catalogo_publico.html` - Listado de productos con filtrado por categoría
- `tienda/checkout.html` - Checkout del carrito (stub de integración con Nequi)
- `registration/login.html` & `signup.html` - Formularios de autenticación
- `tienda/solicitudes_list.html` - Ver todas las solicitudes de pedidos (solo staff)

### Organización de CSS/JS
- Stylesheets: `static/css/{auth, catalogo, contacto, stiman}.css`
- Scripts: `static/js/{app, auth, catalogo}.js`
- Sin herramienta de build (CSS/JS servidos como están, sin minificación)
- Estilos de formularios usan clases CSS personalizadas (form-input, password-input, switch-input, file-input)

## Puntos de Integración y Dependencias Externas

### Highlights de Configuración de Django
- **INSTALLED_APPS**: Solo `tienda` y `web` (apps personalizadas)
- **TEMPLATES**: Templates en `BASE_DIR / 'templates'` con context processor `cart_summary`
- **MIDDLEWARE**: Incluye `LocaleMiddleware` (soporte de internacionalización, aunque no completamente utilizado)
- **MEDIA_URL/ROOT**: Configurado para carga de imágenes de productos

### Context Processor Personalizado
`tienda/context_processors.py:cart_summary()` proporciona:
- `cart_count` - Total de items en carrito
- `cart_total` - Total Decimal (filtra productos activos solamente)
- `productos_por_categoria` - Productos agrupados por categoría semántica (usado en nav del catálogo)

### Integración de Pagos (Stub)
- Vista de checkout existe (`tienda/views.py:checkout()`)
- Integración con Nequi referenciada pero incompleta
- Patrón de integración esperado: POST a gateway de pago, validar respuesta, actualizar estado de orden

## Estilo de Código y Detalles Importantes

### Convenciones de Nombrado
- Modelos: `Producto`, `SolicitudPedido`, `AdminRequest` (CamelCase)
- Vistas: funciones snake_case (`catalogo_estilizado`, `admin_dashboard`, `solicitud_pedido`)
- Nombres de URL: slug-case con underscore (`carrito_agregar`, `tienda_inicio`)
- Templates: nombres snake_case en subdirectorios específicos de app

### Manejo de Decimal/Moneda
- Precios de productos: `DecimalField(max_digits=10, decimal_places=2)`
- Cálculo del total del carrito: Usa tipo `Decimal` para evitar problemas de precisión de float
- Moneda: Peso Colombiano (COP) implícito en contexto
- Hints de formularios: "Usa punto para decimales. Ej: 12900.00"

### Procesamiento de Strings
- Input de formularios usa `.strip()` para validación (nombre, descripción)
- Validación de username: `value.isalpha()` (sin caracteres especiales)
- Categorización de productos usa `producto.name.lower()` para búsqueda de substrings

### Estrategia de Migraciones
- Migraciones almacenadas en `tienda/migrations/` y `web/migrations/`
- Migraciones iniciales existen para ambas apps
- Migraciones adicionales: `tienda/0002_producto_category.py` y `web/0002_adminrequest.py`
- Siempre ejecuta `python manage.py migrate` después de pull de nuevas migraciones

## Errores Comunes y Soluciones

| Problema | Causa Raíz | Solución |
|----------|-----------|---------|
| Carrito muestra 0 items | Sesión no inicializada o dict de carrito vacío | Inicializa `request.session['cart'] = {}` en vistas antes de usar |
| Imagen de producto rota | Archivo de imagen no en media/ o ruta incorrecta | Verifica setup de `MEDIA_ROOT` y que campo `.image` tenga ruta relativa como `productos/image.jpg` |
| Login falla con email | Código espera username, no email | Usa `EmailAuthenticationForm` y `EmailUserCreationForm`, nunca formularios Django estándar |
| Import de Producto falla | Imports circulares con tienda.Producto | Usa referencia string `'tienda.Producto'` en ForeignKey (como se hace en SolicitudPedido) |
| Conflictos de migración | Cambios de schema paralelos | Ejecuta `python manage.py showmigrations` y resuelve manualmente en directorios migrations/ |

## Consejos para Agentes AI

1. **Siempre revisa `context_processors.py`** antes de agregar contexto relacionado con catálogo—datos de carrito y categoría ya proporcionados
2. **Referencia `ProductoForm`** (en views.py) al modificar creación de productos—ya tiene help_texts extensos y widgets personalizados
3. **Preserva lógica de categorización semántica** en context_processor—no hardcodes nombres de categorías en templates
4. **Usa tipo Decimal** para cualquier cálculo de precios—evita aritmética de float
5. **Recuerda autenticación basada en email**—campo username es realmente email; formas personalizadas requeridas
6. **Patrón de carrito de sesión**—nunca mutes dict de sesión directamente; siempre reasigna: `request.session['cart'] = carrito_actualizado`
