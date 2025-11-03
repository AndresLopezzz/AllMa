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
6. **(Opcional)** Poblar con datos de prueba: `python manage.py seed_data --clear`
7. Iniciar servidor: `python manage.py runserver`

### Datos de Prueba (Seed Data)

El proyecto incluye un comando personalizado para poblar la base de datos con datos de ejemplo:

```bash
# Crear datos de prueba (mantiene datos existentes)
python manage.py seed_data

# Limpiar base de datos y crear datos frescos
python manage.py seed_data --clear
```

**Datos generados:**
- 3 usuarios con diferentes planes (free, pro)
- 5 plantillas de negocio (Ferretería, Ropa, Electrónica, Alimentos, Librería)
- 10 inventarios distribuidos entre usuarios
- ~110 productos con stock variado
- 50 movimientos de inventario

**Credenciales de acceso:**
- Email: `free@example.com` | Password: `password123` (Plan Free)
- Email: `pro@example.com` | Password: `password123` (Plan Pro)
- Email: `pro2@example.com` | Password: `password123` (Plan Pro)

Estos datos son ideales para:
- Probar la API sin crear datos manualmente
- Desarrollo del frontend con datos realistas
- Demos y presentaciones
- Testing de features

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

La API REST está completamente documentada en `/backend/api_docs.md` con:
- Tabla completa de endpoints
- Ejemplos de request/response para cada uno
- Códigos de error comunes
- Notas sobre paginación, filtros y ordenamiento
- Información sobre límites por plan

**Endpoints principales:**
- `/api/register/` - Registro de usuarios
- `/api/login/` - Autenticación
- `/api/templates/` - Plantillas de negocio
- `/api/inventories/` - Gestión de inventarios
- `/api/inventories/{id}/stats/` - Estadísticas detalladas por inventario
- `/api/inventories/{id}/export/` - Exportar productos a CSV
- `/api/products/` - CRUD de productos
- `/api/products/{id}/adjust_stock/` - Ajustar stock con tracking
- `/api/dashboard/` - Métricas generales del usuario
- `/api/alerts/` - Productos con stock bajo ordenados por criticidad

### Dashboard API

El endpoint `/api/dashboard/` proporciona métricas clave y datos listos para visualización.

**Métricas básicas:**
- `total_products` - Cantidad total de productos activos
- `total_inventory_value` - Valor total del inventario (precio × cantidad)
- `low_stock_count` - Productos con stock bajo o igual al umbral
- `out_of_stock_count` - Productos sin stock
- `total_inventories` - Cantidad de inventarios del usuario

**Datos para gráficas:**
- `products_by_category` - Array de objetos `{category, count}` ordenado por cantidad
- `value_by_inventory` - Array de objetos `{inventory_id, inventory_name, value}` ordenado por valor
- `recent_movements` - Últimos 10 movimientos con información completa del producto

**Filtros opcionales:**
- `?inventory=<id>` - Filtra todas las métricas por un inventario específico

**Ejemplo de respuesta:**
```json
{
  "total_products": 23,
  "total_inventory_value": 49644.38,
  "low_stock_count": 14,
  "out_of_stock_count": 3,
  "total_inventories": 9,
  "products_by_category": [
    {"category": "Herramientas", "count": 8},
    {"category": "Electrónica", "count": 5}
  ],
  "value_by_inventory": [
    {"inventory_id": 1, "inventory_name": "Bodega 1", "value": 25000.50}
  ],
  "recent_movements": [
    {
      "id": 45,
      "product_name": "Martillo",
      "movement_type": "salida",
      "quantity": -15,
      "timestamp": "2025-11-02T19:16:00Z"
    }
  ]
}
```

**Performance:**
- Optimizado con agregaciones a nivel de base de datos
- Máximo 9 queries independiente del tamaño del dataset
- Respuesta < 500ms con 100+ productos

## Testing

```bash
# Ejecutar todos los tests
python manage.py test

# Ejecutar tests específicos
python manage.py test inventory.tests.AlertAPITests
python manage.py test accounts.tests

# Ejecutar tests con cobertura
coverage run --source='.' manage.py test
coverage report
```

**Cobertura actual:** 85% (93 tests implementados)

Los tests cubren:
- ✅ Autenticación y permisos (registro, login, perfil)
- ✅ CRUD completo de productos con validaciones
- ✅ Gestión de inventarios y plantillas
- ✅ Sistema de alertas de stock bajo
- ✅ Dashboard con métricas y gráficas
- ✅ Exportación a CSV
- ✅ Estadísticas por inventario
- ✅ Tracking de movimientos
- ✅ Soft delete y restauración
- ✅ Ajustes de stock con diferentes tipos
</parameter>

<old_text line=177>
## Próximos Pasos

- Completar frontend con React y TanStack
- Implementar dashboard con estadísticas
- Sistema de reportes y exportación
- Historial de movimientos de inventario
- Notificaciones por email
- API pública con rate limiting

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

**Estado:** Backend completo - Frontend en desarrollo
**Versión:** 1.0.0 (Backend MVP completo)
**Última actualización:** Noviembre 2024
