# Allma Inventory

Sistema modular de inventarios diseñado para adaptarse a diferentes tipos de negocios mediante plantillas personalizables. Permite a pequeñas y medianas empresas gestionar sus productos con campos dinámicos según sus necesidades específicas.

## Descripción del Proyecto

Este sistema ofrece una solución flexible para la gestión de inventarios que se adapta a distintos rubros comerciales. A diferencia de sistemas rígidos, utiliza un sistema de plantillas que permite definir campos personalizados según el tipo de negocio (ferretería, ropa, restaurante, etc.).

### Características Principales

**Sistema de plantillas dinámicas**
- Cada tipo de negocio puede definir sus propios campos personalizados
- Validaciones automáticas según la estructura definida
- Soporte para diferentes tipos de datos (texto, número, selección múltiple)

**Gestión de inventarios**
- Control de stock con alertas de bajo inventario
- Soporte para múltiples inventarios por usuario
- SKU único por inventario para evitar duplicados
- Soft delete para mantener historial

**Autenticación y permisos**
- Sistema de roles (administrador/empleado)
- Planes de suscripción con límites configurables
- Autenticación mediante JWT con tokens de corta y larga duración

**Almacenamiento de imágenes**
- Integración con Cloudinary para almacenamiento externo
- Optimización automática de imágenes (WebP/AVIF)
- Múltiples versiones (thumbnail, medium, full)

## Stack Tecnológico

**Backend:** Django 5.2 + Django REST Framework + PostgreSQL
**Autenticación:** JWT (djangorestframework-simplejwt)
**Almacenamiento:** Cloudinary
**Testing:** Django TestCase (78% coverage)

**Frontend:** React + TypeScript + TanStack Router/Query (en desarrollo)

## Estructura del Proyecto

```
inventory/
├── backend/
│   ├── accounts/          # Gestión de usuarios y autenticación
│   ├── inventory/         # Lógica de inventarios y productos
│   ├── backend/           # Configuración del proyecto
│   └── manage.py
├── frontend/              # Aplicación React (próximamente)
└── README.md
```

## Instalación y Configuración

### Prerrequisitos

- Python 3.11+
- PostgreSQL 14+
- Cuenta en Cloudinary (para imágenes)

### Configuración Inicial

1. Clonar el repositorio y crear entorno virtual
2. Instalar dependencias: `pip install -r requirements.txt`
3. Configurar variables de entorno en archivo `.env`
4. Ejecutar migraciones: `python manage.py migrate`
5. Crear superusuario: `python manage.py createsuperuser`
6. Iniciar servidor: `python manage.py runserver`

### Variables de Entorno Requeridas

```
SECRET_KEY=
DEBUG=
ALLOWED_HOSTS=

DB_NAME=
DB_USER=
DB_PASSWORD=
DB_HOST=
DB_PORT=

CLOUDINARY_CLOUD_NAME=
CLOUDINARY_API_KEY=
CLOUDINARY_API_SECRET=
```

## API

La API REST está documentada en `/backend/API_DOCS.md` con ejemplos de uso para cada endpoint.

**Endpoints principales:**
- `/api/register/` - Registro de usuarios
- `/api/login/` - Autenticación
- `/api/templates/` - Plantillas de negocio
- `/api/inventories/` - Gestión de inventarios
- `/api/products/` - CRUD de productos

## Testing

```bash
# Ejecutar todos los tests
python manage.py test

# Ejecutar tests con cobertura
coverage run --source='.' manage.py test
coverage report
```

**Cobertura actual:** 78% (31 tests implementados)

Los tests cubren funcionalidades críticas: autenticación, permisos, validaciones de negocio y operaciones CRUD.

## Modelo de Negocio

El sistema está diseñado para ofrecer diferentes planes de suscripción:

**Plan Free:** Límites básicos para prueba del servicio
**Plan Pro:** Límites extendidos para pequeñas empresas
**Plan Premium:** Sin límites para empresas establecidas

Los límites se configuran en `inventory/constants.py` y se validan automáticamente en cada operación.

## Próximos Pasos

- Completar frontend con React y TanStack
- Implementar dashboard con estadísticas
- Sistema de reportes y exportación
- Historial de movimientos de inventario
- Notificaciones por email
- API pública con rate limiting

## Deploy

**Backend:** Railway o similar (PostgreSQL incluido)
**Frontend:** Vercel
**Imágenes:** Cloudinary

## Desarrollo

El proyecto sigue las convenciones estándar de Django. Para contribuir:

1. Crear rama desde `main`
2. Implementar cambios con tests
3. Verificar que todos los tests pasen
4. Crear pull request con descripción clara

## Licencia

MIT License

---

**Estado:** En desarrollo activo
**Versión:** 0.1.0 (MVP)
