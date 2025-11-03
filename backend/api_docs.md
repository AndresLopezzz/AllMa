# 📚 Documentación de API - Sistema de Gestión de Inventarios

## Información General

- **Base URL:** `http://localhost:8000/api`
- **Autenticación:** JWT (JSON Web Tokens)
- **Formato de respuesta:** JSON
- **Codificación:** UTF-8

---

## 📋 Tabla de Endpoints

### Autenticación (`/accounts`)

| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| POST | `/accounts/register/` | Registrar nuevo usuario | No |
| POST | `/accounts/login/` | Iniciar sesión | No |
| GET | `/accounts/profile/` | Obtener perfil del usuario autenticado | Sí |

### Plantillas de Negocio (`/templates`)

| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| GET | `/templates/` | Listar todas las plantillas activas | Sí |
| POST | `/templates/` | Crear nueva plantilla (solo admin) | Sí |
| GET | `/templates/{id}/` | Obtener detalle de plantilla | Sí |
| PUT/PATCH | `/templates/{id}/` | Actualizar plantilla | Sí |
| DELETE | `/templates/{id}/` | Eliminar plantilla | Sí |
| POST | `/templates/{id}/toggle_active/` | Activar/desactivar plantilla | Sí |

### Inventarios (`/inventories`)

| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| GET | `/inventories/` | Listar inventarios del usuario | Sí |
| POST | `/inventories/` | Crear nuevo inventario | Sí |
| GET | `/inventories/{id}/` | Obtener detalle de inventario | Sí |
| PUT/PATCH | `/inventories/{id}/` | Actualizar inventario | Sí |
| DELETE | `/inventories/{id}/` | Eliminar inventario | Sí |
| PUT | `/inventories/{id}/custom-fields/` | Personalizar campos del inventario | Sí |
| GET | `/inventories/{id}/export/` | Exportar productos a CSV | Sí |
| GET | `/inventories/{id}/stats/` | Estadísticas detalladas del inventario | Sí |

### Productos (`/products`)

| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| GET | `/products/` | Listar productos del usuario | Sí |
| POST | `/products/` | Crear nuevo producto | Sí |
| GET | `/products/{id}/` | Obtener detalle de producto | Sí |
| PUT/PATCH | `/products/{id}/` | Actualizar producto | Sí |
| DELETE | `/products/{id}/` | Eliminar producto (soft delete) | Sí |
| POST | `/products/{id}/restore/` | Restaurar producto eliminado | Sí |
| POST | `/products/{id}/adjust_stock/` | Ajustar cantidad de stock | Sí |

### Dashboard (`/dashboard`)

| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| GET | `/dashboard/` | Métricas generales del usuario | Sí |

### Alertas (`/alerts`)

| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| GET | `/alerts/` | Listar productos con stock bajo | Sí |

---

## 🔐 Autenticación

### Registro de Usuario

**Endpoint:** `POST /api/accounts/register/`

**Request Body:**
```json
{
  "email": "usuario@example.com",
  "password": "contraseña_segura",
  "name": "Nombre Usuario",
  "plan": "free"
}
```

**Response:** `201 Created`
```json
{
  "user": {
    "id": 1,
    "email": "usuario@example.com",
    "name": "Nombre Usuario",
    "plan": "free",
    "is_active": true
  },
  "tokens": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  },
  "message": "Usuario registrado exitosamente"
}
```

### Login

**Endpoint:** `POST /api/accounts/login/`

**Request Body:**
```json
{
  "email": "usuario@example.com",
  "password": "contraseña_segura"
}
```

**Response:** `200 OK`
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "email": "usuario@example.com",
    "name": "Nombre Usuario",
    "plan": "free"
  }
}
```

### Uso del Token

En todas las peticiones autenticadas, incluir el header:

```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

---

## 🏪 Plantillas de Negocio

### Listar Plantillas

**Endpoint:** `GET /api/templates/`

**Query Parameters:**
- `template` (int): Filtrar por ID de plantilla
- `search` (string): Buscar por nombre
- `ordering` (string): Ordenar por campo (`name`, `-created_at`)

**Response:** `200 OK`
```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Ferretería",
      "description": "Plantilla para ferreterías",
      "custom_fields": [
        {
          "name": "marca",
          "type": "text",
          "required": true
        },
        {
          "name": "material",
          "type": "text",
          "required": false
        }
      ],
      "created_by": 1,
      "created_by_name": "Admin",
      "created_by_email": "admin@example.com",
      "is_active": true,
      "created_at": "2024-01-01T10:00:00Z",
      "updated_at": "2024-01-01T10:00:00Z"
    }
  ]
}
```

### Crear Plantilla (Admin)

**Endpoint:** `POST /api/templates/`

**Request Body:**
```json
{
  "name": "Ropa",
  "description": "Plantilla para tiendas de ropa",
  "custom_fields": [
    {
      "name": "talla",
      "type": "select",
      "required": true,
      "options": ["XS", "S", "M", "L", "XL"]
    },
    {
      "name": "color",
      "type": "text",
      "required": true
    }
  ]
}
```

**Response:** `201 Created`

---

## 📦 Inventarios

### Listar Inventarios

**Endpoint:** `GET /api/inventories/`

**Response:** `200 OK`
```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Bodega Principal",
      "owner": 1,
      "owner_name": "Usuario",
      "template": 1,
      "template_name": "Ferretería",
      "created_at": "2024-01-01T10:00:00Z",
      "updated_at": "2024-01-01T10:00:00Z"
    }
  ]
}
```

### Crear Inventario

**Endpoint:** `POST /api/inventories/`

**Request Body:**
```json
{
  "name": "Bodega Secundaria",
  "template": 1
}
```

**Response:** `201 Created`

### Estadísticas de Inventario

**Endpoint:** `GET /api/inventories/{id}/stats/`

**Response:** `200 OK`
```json
{
  "inventory_id": 1,
  "inventory_name": "Bodega Principal",
  "total_products": 150,
  "total_value": 45000.00,
  "low_stock_products": 5,
  "out_of_stock_products": 2,
  "stock_distribution": {
    "in_stock": 100,
    "low_stock": 40,
    "out_of_stock": 10
  },
  "categories": [
    {
      "name": "Electrónica",
      "count": 30,
      "total_value": 15000.00
    }
  ],
  "top_products_by_value": [
    {
      "id": 1,
      "name": "Laptop HP",
      "sku": "LAP-001",
      "quantity": 10,
      "price": 800.00,
      "total_value": 8000.00,
      "category": "Electrónica"
    }
  ],
  "recent_movements": [
    {
      "id": 1,
      "product_name": "Laptop HP",
      "product_sku": "LAP-001",
      "movement_type": "entrada",
      "quantity": 5,
      "quantity_before": 5,
      "quantity_after": 10,
      "reason": "Compra a proveedor",
      "performed_by": "usuario@example.com",
      "timestamp": "2024-01-01T10:00:00Z"
    }
  ]
}
```

### Exportar a CSV

**Endpoint:** `GET /api/inventories/{id}/export/`

**Response:** `200 OK`
- **Content-Type:** `text/csv; charset=utf-8`
- **Content-Disposition:** `attachment; filename="inventario_{id}_{name}.csv"`

Descarga un archivo CSV con todas las columnas estándar y custom_fields aplanadas.

---

## 🏷️ Productos

### Listar Productos

**Endpoint:** `GET /api/products/`

**Query Parameters:**
- `inventory` (int): Filtrar por inventario
- `category` (string): Filtrar por categoría
- `low_stock` (boolean): Solo productos con stock bajo
- `search` (string): Buscar por nombre o SKU
- `ordering` (string): Ordenar (`name`, `-price`, `-quantity`)
- `page` (int): Número de página
- `page_size` (int): Tamaño de página (default: 20)

**Response:** `200 OK`
```json
{
  "count": 150,
  "next": "http://localhost:8000/api/products/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Martillo",
      "sku": "MART-001",
      "description": "Martillo de acero",
      "quantity": 50,
      "price": "25.99",
      "category": "Herramientas",
      "image": null,
      "image_url": null,
      "image_versions": null,
      "inventory": 1,
      "inventory_name": "Bodega Principal",
      "custom_data": {
        "marca": "Stanley",
        "material": "Acero"
      },
      "template_info": [
        {"name": "marca", "type": "text", "required": true}
      ],
      "low_stock_threshold": 10,
      "stock_status": "En stock",
      "is_low_stock": false,
      "is_out_of_stock": false,
      "is_active": true,
      "created_at": "2024-01-01T10:00:00Z",
      "updated_at": "2024-01-01T10:00:00Z"
    }
  ]
}
```

### Crear Producto

**Endpoint:** `POST /api/products/`

**Request Body:**
```json
{
  "name": "Destornillador",
  "sku": "DEST-001",
  "description": "Destornillador Phillips #2",
  "quantity": 100,
  "price": "12.50",
  "low_stock_threshold": 20,
  "category": "Herramientas",
  "inventory": 1,
  "custom_data": {
    "marca": "Truper",
    "material": "Acero cromado"
  }
}
```

**Response:** `201 Created`

### Ajustar Stock

**Endpoint:** `POST /api/products/{id}/adjust_stock/`

**Request Body:**
```json
{
  "adjustment_type": "entrada",
  "quantity": 50,
  "reason": "Compra a proveedor XYZ"
}
```

**Opciones para `adjustment_type`:**
- `entrada`: Suma stock
- `salida`: Resta stock
- `ajuste`: Establece cantidad exacta

**Response:** `200 OK`
```json
{
  "message": "Stock ajustado exitosamente",
  "product": {
    "id": 1,
    "name": "Martillo",
    "quantity": 100,
    "stock_status": "En stock"
  },
  "movement": {
    "id": 5,
    "movement_type": "entrada",
    "quantity": 50,
    "quantity_before": 50,
    "quantity_after": 100
  }
}
```

---

## 📊 Dashboard

### Métricas Generales

**Endpoint:** `GET /api/dashboard/`

**Response:** `200 OK`
```json
{
  "total_inventories": 3,
  "total_products": 250,
  "total_value": 125000.50,
  "low_stock_count": 15,
  "out_of_stock_count": 5,
  "products_by_category": [
    {
      "category": "Electrónica",
      "count": 50,
      "total_value": 45000.00
    }
  ],
  "products_by_inventory": [
    {
      "inventory_name": "Bodega Principal",
      "count": 150,
      "total_value": 80000.00
    }
  ],
  "stock_distribution": {
    "in_stock": 200,
    "low_stock": 40,
    "out_of_stock": 10
  },
  "recent_movements": [
    {
      "id": 1,
      "product_name": "Laptop",
      "movement_type": "salida",
      "quantity": -2,
      "quantity_before": 10,
      "quantity_after": 8,
      "reason": "Venta",
      "performed_by": "usuario@example.com",
      "timestamp": "2024-01-01T15:30:00Z"
    }
  ]
}
```

---

## 🚨 Alertas

### Listar Alertas de Stock Bajo

**Endpoint:** `GET /api/alerts/`

**Query Parameters:**
- `inventory` (int): Filtrar por inventario
- `new_only` (boolean): Solo alertas no enviadas (`alert_sent=false`)
- `page` (int): Número de página
- `page_size` (int): Tamaño de página (default: 10, max: 50)

**Response:** `200 OK`
```json
{
  "count": 15,
  "next": "http://localhost:8000/api/alerts/?page=2",
  "previous": null,
  "results": [
    {
      "id": 3,
      "name": "Tornillos",
      "sku": "TORN-001",
      "quantity": 2,
      "low_stock_threshold": 10,
      "price": "0.50",
      "category": "Ferretería",
      "image_url": null,
      "inventory_id": 1,
      "inventory_name": "Bodega Principal",
      "owner_email": "usuario@example.com",
      "owner_name": "Usuario",
      "criticality_ratio": 0.2,
      "alert_sent": false,
      "stock_status": "Stock bajo",
      "is_out_of_stock": false,
      "created_at": "2024-01-01T10:00:00Z",
      "updated_at": "2024-01-01T12:00:00Z"
    }
  ]
}
```

**Nota:** Los productos están ordenados por `criticality_ratio` (más bajo = más crítico).

---

## 📄 Paginación

Todos los endpoints de lista incluyen paginación:

**Parámetros:**
- `page`: Número de página (default: 1)
- `page_size`: Tamaño de página (varía según endpoint)

**Respuesta:**
```json
{
  "count": 100,
  "next": "http://localhost:8000/api/products/?page=3",
  "previous": "http://localhost:8000/api/products/?page=1",
  "results": [...]
}
```

---

## 🔍 Filtros y Ordenamiento

### Productos

**Filtros disponibles:**
- `?inventory=1` - Por inventario
- `?category=Electrónica` - Por categoría
- `?low_stock=true` - Solo stock bajo
- `?search=martillo` - Búsqueda en nombre/SKU

**Ordenamiento:**
- `?ordering=name` - Alfabético A-Z
- `?ordering=-name` - Alfabético Z-A
- `?ordering=price` - Precio ascendente
- `?ordering=-price` - Precio descendente
- `?ordering=quantity` - Cantidad ascendente

**Combinar:**
```
GET /api/products/?inventory=1&category=Herramientas&ordering=-price&page_size=50
```

---

## ⚠️ Códigos de Error

### Errores de Cliente (4xx)

**400 Bad Request**
```json
{
  "error": "Datos inválidos",
  "details": {
    "price": ["Este campo es requerido"],
    "quantity": ["Debe ser mayor o igual a 0"]
  }
}
```

**401 Unauthorized**
```json
{
  "detail": "Las credenciales de autenticación no se proveyeron."
}
```

**403 Forbidden**
```json
{
  "error": "No tienes permiso para realizar esta acción"
}
```

**404 Not Found**
```json
{
  "detail": "No encontrado."
}
```

### Errores de Servidor (5xx)

**500 Internal Server Error**
```json
{
  "error": "Error interno del servidor",
  "message": "Contacta al administrador"
}
```

---

## 📝 Notas Importantes

### Límites por Plan

Los usuarios tienen límites según su plan:

| Plan | Inventarios | Productos por Inventario |
|------|-------------|--------------------------|
| Free | 1 | 50 |
| Pro | 5 | 500 |
| Premium | Ilimitado | Ilimitado |

Al exceder límites, se retorna error `400`:
```json
{
  "error": "Plan limit exceeded",
  "error_code": "plan_limit_exceeded",
  "upgrade_required": true
}
```

### Soft Delete

Los productos eliminados no se borran de la base de datos, solo se marcan como `is_active=false`.

Para restaurar:
```
POST /api/products/{id}/restore/
```

### Tracking de Movimientos

Todos los cambios en el stock se registran automáticamente en la tabla `Movement`:
- Creación de producto
- Actualización de cantidad
- Ajustes de stock

### Imágenes

Las imágenes se almacenan en **Cloudinary** con optimizaciones automáticas:
- **Formato:** WebP/AVIF (automático según navegador)
- **Calidad:** Automática
- **Versiones:** thumbnail (200x200), medium (800px), full

---

## 🚀 Performance

### Optimizaciones Implementadas

1. **Select Related:** Queries optimizados con `select_related()` y `prefetch_related()`
2. **Índices:** Campos frecuentes indexados en base de datos
3. **Paginación:** Todas las listas paginadas por defecto
4. **Agregaciones:** Cálculos realizados en base de datos

### Benchmarks

| Endpoint | Tiempo Promedio |
|----------|-----------------|
| Dashboard | ~600ms |
| Listar Productos | ~200ms |
| Estadísticas Inventario | ~450ms |
| Alertas | ~300ms |

---

## 🔄 Versiones

**Versión Actual:** v1.0  
**Última Actualización:** Noviembre 2024

### Changelog

**v1.0 (Semana 3)**
- ✅ CRUD completo de productos
- ✅ Gestión de inventarios
- ✅ Sistema de alertas
- ✅ Dashboard con métricas
- ✅ Exportación a CSV
- ✅ Estadísticas por inventario
- ✅ Tracking de movimientos
- ✅ Imágenes con Cloudinary

---

## 📞 Soporte

Para reportar bugs o sugerencias, contacta al equipo de desarrollo.