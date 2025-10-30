# 📚 API Documentation - Inventory Management System

## Base URL
```
http://localhost:8000/api/
```

---

## 🔐 Authentication

La API utiliza **JWT Authentication** (JSON Web Tokens). Hay dos tipos de tokens:

- **Access Token**: Token de corta duración (1 hora) para hacer peticiones
- **Refresh Token**: Token de larga duración (7 días) para renovar el access token

Debes incluir el access token en los headers de las peticiones protegidas:

```
Authorization: Bearer <access_token_aqui>
```

---

## 📋 Endpoints de Autenticación

### 1. Registro de Usuario

**Endpoint:** `POST /api/register/`

**Descripción:** Crea una nueva cuenta de usuario y devuelve tokens de autenticación.

**Permisos:** Público (no requiere autenticación)

**Body (JSON):**
```json
{
  "email": "usuario@ejemplo.com",
  "name": "Juan Pérez",
  "password": "contraseña123",
  "password2": "contraseña123",
  "role": "employee",
  "plan": "free"
}
```

**Campos:**
- `email` (requerido): Email único del usuario
- `name` (requerido): Nombre completo
- `password` (requerido): Contraseña (mínimo 8 caracteres)
- `password2` (requerido): Confirmación de contraseña
- `role` (opcional): `admin` o `employee` (default: `employee`)
- `plan` (opcional): `free`, `pro`, o `premium` (default: `free`)

**Respuesta exitosa (201):**
```json
{
  "message": "User created successfully",
  "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "email": "usuario@ejemplo.com",
    "name": "Juan Pérez",
    "role": "employee",
    "plan": "free"
  }
}
```

---

### 2. Login

**Endpoint:** `POST /api/login/`

**Descripción:** Autentica al usuario y devuelve tokens.

**Permisos:** Público

**Body (JSON):**
```json
{
  "username": "usuario@ejemplo.com",
  "password": "contraseña123"
}
```

**Nota:** Aunque el campo se llama `username`, debes enviar el **email** del usuario.

**Respuesta exitosa (200):**
```json
{
  "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "email": "usuario@ejemplo.com",
    "name": "Juan Pérez",
    "role": "employee",
    "plan": "free",
    "is_active": true
  }
}
```

---

### 3. Renovar Access Token

**Endpoint:** `POST /api/token/refresh/`

**Descripción:** Obtiene un nuevo access token usando el refresh token.

**Permisos:** Público

**Body (JSON):**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Respuesta exitosa (200):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

---

### 4. Obtener Perfil

**Endpoint:** `GET /api/profile/`

**Descripción:** Obtiene los datos del usuario autenticado.

**Permisos:** Requiere autenticación (JWT)

**Headers:**
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

**Respuesta exitosa (200):**
```json
{
  "id": 1,
  "email": "usuario@ejemplo.com",
  "name": "Juan Pérez",
  "role": "employee",
  "plan": "free",
  "is_active": true,
  "date_joined": "2024-01-15T10:30:00Z"
}
```

---

## 🏢 Endpoints de Plantillas de Negocio (Business Templates)

### 1. Listar Plantillas

**Endpoint:** `GET /api/templates/`

**Descripción:** Lista todas las plantillas de negocio activas.

**Permisos:** Requiere autenticación

**Query Parameters:**
- `search=<texto>`: Busca en nombre y descripción
- `ordering=<campo>`: Ordena por campo (`name`, `created_at`, `-created_at`)
- `show_inactive=true`: (Solo admin) Muestra plantillas inactivas

**Respuesta exitosa (200):**
```json
{
  "count": 3,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Ferretería",
      "description": "Plantilla para ferreterías y negocios de herramientas",
      "custom_fields": [
        {
          "name": "material",
          "type": "select",
          "required": false,
          "options": ["Acero", "Aluminio", "Plástico"]
        },
        {
          "name": "marca",
          "type": "text",
          "required": false
        }
      ],
      "created_by": 1,
      "created_by_name": "Admin",
      "created_by_email": "admin@test.com",
      "is_active": true,
      "created_at": "2024-01-15T10:00:00Z",
      "updated_at": "2024-01-15T10:00:00Z"
    }
  ]
}
```

---

### 2. Ver Detalle de Plantilla

**Endpoint:** `GET /api/templates/{id}/`

**Descripción:** Obtiene el detalle completo de una plantilla.

**Permisos:** Requiere autenticación

**Respuesta exitosa (200):**
```json
{
  "id": 1,
  "name": "Ferretería",
  "description": "Plantilla para ferreterías y negocios de herramientas",
  "custom_fields": [
    {
      "name": "material",
      "type": "select",
      "required": false,
      "options": ["Acero", "Aluminio", "Plástico"]
    }
  ],
  "created_by": 1,
  "created_by_name": "Admin",
  "created_by_email": "admin@test.com",
  "is_active": true,
  "created_at": "2024-01-15T10:00:00Z",
  "updated_at": "2024-01-15T10:00:00Z"
}
```

---

### 3. Crear Plantilla (Solo Admin)

**Endpoint:** `POST /api/templates/`

**Descripción:** Crea una nueva plantilla de negocio.

**Permisos:** Requiere autenticación + Rol Admin

**Body (JSON):**
```json
{
  "name": "Restaurante",
  "description": "Plantilla para restaurantes y negocios de comida",
  "custom_fields": [
    {
      "name": "categoria_alimento",
      "type": "select",
      "required": true,
      "options": ["Entrada", "Plato Principal", "Postre", "Bebida"]
    },
    {
      "name": "calorias",
      "type": "number",
      "required": false
    }
  ],
  "is_active": true
}
```

**Estructura de custom_fields:**
- `name` (string): Nombre del campo
- `type` (string): Tipo de campo (`text`, `number`, `select`, `checkbox`, `textarea`, `date`)
- `required` (boolean): Si es obligatorio
- `options` (array): Solo para type="select", lista de opciones

**Respuesta exitosa (201):**
```json
{
  "id": 4,
  "name": "Restaurante",
  "description": "Plantilla para restaurantes y negocios de comida",
  "custom_fields": [...],
  "created_by": 1,
  "created_by_name": "Admin",
  "created_by_email": "admin@test.com",
  "is_active": true,
  "created_at": "2024-01-20T14:30:00Z",
  "updated_at": "2024-01-20T14:30:00Z"
}
```

---

### 4. Actualizar Plantilla (Solo Admin)

**Endpoint:** `PUT /api/templates/{id}/` o `PATCH /api/templates/{id}/`

**Descripción:** Actualiza una plantilla existente.

**Permisos:** Requiere autenticación + Rol Admin

**Body (JSON - PATCH permite actualización parcial):**
```json
{
  "description": "Descripción actualizada"
}
```

---

### 5. Activar/Desactivar Plantilla (Solo Admin)

**Endpoint:** `POST /api/templates/{id}/toggle_active/`

**Descripción:** Activa o desactiva una plantilla.

**Permisos:** Requiere autenticación + Rol Admin

**Respuesta exitosa (200):**
```json
{
  "message": "Plantilla activada",
  "data": { /* plantilla completa */ }
}
```

---

## 📦 Endpoints de Inventarios

### 1. Listar Inventarios

**Endpoint:** `GET /api/inventories/`

**Descripción:** Lista los inventarios del usuario autenticado.

**Permisos:** Requiere autenticación (cada usuario ve solo los suyos, admin ve todos)

**Query Parameters:**
- `search=<texto>`: Busca por nombre
- `template=<id>`: Filtra por plantilla
- `ordering=<campo>`: Ordena por campo

**Respuesta exitosa (200):**
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
      "owner_name": "Juan Pérez",
      "template": 1,
      "template_name": "Ferretería",
      "created_at": "2024-01-15T11:00:00Z",
      "updated_at": "2024-01-15T11:00:00Z"
    }
  ]
}
```

---

### 2. Ver Detalle de Inventario

**Endpoint:** `GET /api/inventories/{id}/`

**Descripción:** Obtiene el detalle completo de un inventario.

**Permisos:** Requiere autenticación + ser dueño (o admin)

**Respuesta exitosa (200):**
```json
{
  "id": 1,
  "name": "Bodega Principal",
  "owner": 1,
  "owner_name": "Juan Pérez",
  "template": 1,
  "template_data": {
    "id": 1,
    "name": "Ferretería",
    "description": "Plantilla para ferreterías",
    "custom_fields": [...]
  },
  "custom_template_fields": null,
  "created_at": "2024-01-15T11:00:00Z",
  "updated_at": "2024-01-15T11:00:00Z"
}
```

---

### 3. Crear Inventario

**Endpoint:** `POST /api/inventories/`

**Descripción:** Crea un nuevo inventario.

**Permisos:** Requiere autenticación

**Body (JSON):**
```json
{
  "name": "Tienda Centro",
  "template": 1,
  "custom_template_fields": {
    "campo_extra": "valor"
  }
}
```

**Respuesta exitosa (201):**
```json
{
  "id": 2,
  "name": "Tienda Centro",
  "owner": 1,
  "owner_name": "Juan Pérez",
  "template": 1,
  "template_data": {...},
  "custom_template_fields": {...},
  "created_at": "2024-01-20T15:00:00Z",
  "updated_at": "2024-01-20T15:00:00Z"
}
```

---

### 4. Actualizar Inventario

**Endpoint:** `PUT /api/inventories/{id}/` o `PATCH /api/inventories/{id}/`

**Descripción:** Actualiza un inventario existente.

**Permisos:** Requiere autenticación + ser dueño (o admin)

---

### 5. Eliminar Inventario

**Endpoint:** `DELETE /api/inventories/{id}/`

**Descripción:** Elimina un inventario.

**Permisos:** Requiere autenticación + ser dueño (o admin)

**Respuesta exitosa (204):** Sin contenido

---

## 📦 Endpoints de Productos

### 1. Listar Productos

**Endpoint:** `GET /api/products/`

**Descripción:** Lista los productos de los inventarios del usuario.

**Permisos:** Requiere autenticación

**Query Parameters:**
- `search=<texto>`: Busca en nombre, SKU y descripción
- `inventory=<id>`: Filtra por inventario
- `category=<texto>`: Filtra por categoría
- `low_stock=true`: Solo productos con stock bajo
- `out_of_stock=true`: Solo productos sin stock
- `ordering=<campo>`: Ordena por campo (`name`, `sku`, `quantity`, `price`, `created_at`)

**Respuesta exitosa (200):**
```json
{
  "count": 50,
  "next": "http://localhost:8000/api/products/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Martillo de Garra 16oz",
      "sku": "MART-001",
      "description": "Martillo profesional con mango de fibra de vidrio",
      "quantity": 45,
      "price": "25.99",
      "category": "Herramientas Manuales",
      "inventory": 1,
      "inventory_name": "Bodega Principal",
      "custom_data": {
        "material": "Acero",
        "marca": "Stanley"
      },
      "low_stock_threshold": 10,
      "stock_status": "En Stock",
      "is_low_stock": false,
      "is_out_of_stock": false,
      "created_at": "2024-01-15T12:00:00Z",
      "updated_at": "2024-01-18T09:30:00Z"
    },
    {
      "id": 2,
      "name": "Destornilladores Set 6pz",
      "sku": "DEST-002",
      "description": "Set de 6 destornilladores planos y phillips",
      "quantity": 8,
      "price": "15.50",
      "category": "Herramientas Manuales",
      "inventory": 1,
      "inventory_name": "Bodega Principal",
      "custom_data": {},
      "low_stock_threshold": 10,
      "stock_status": "Stock Bajo",
      "is_low_stock": true,
      "is_out_of_stock": false,
      "created_at": "2024-01-15T12:05:00Z",
      "updated_at": "2024-01-19T10:15:00Z"
    }
  ]
}
```

---

### 2. Ver Detalle de Producto

**Endpoint:** `GET /api/products/{id}/`

**Descripción:** Obtiene el detalle completo de un producto.

**Permisos:** Requiere autenticación + acceso al inventario

**Respuesta exitosa (200):**
```json
{
  "id": 1,
  "name": "Martillo de Garra 16oz",
  "sku": "MART-001",
  "description": "Martillo profesional con mango de fibra de vidrio",
  "quantity": 45,
  "price": "25.99",
  "category": "Herramientas Manuales",
  "inventory": 1,
  "inventory_name": "Bodega Principal",
  "custom_data": {
    "material": "Acero",
    "marca": "Stanley"
  },
  "low_stock_threshold": 10,
  "stock_status": "En Stock",
  "is_low_stock": false,
  "is_out_of_stock": false,
  "created_at": "2024-01-15T12:00:00Z",
  "updated_at": "2024-01-18T09:30:00Z"
}
```

---

### 3. Crear Producto

**Endpoint:** `POST /api/products/`

**Descripción:** Crea un nuevo producto en un inventario.

**Permisos:** Requiere autenticación + ser dueño del inventario

**Body (JSON):**
```json
{
  "name": "Taladro Eléctrico 1/2",
  "sku": "TAL-003",
  "description": "Taladro eléctrico de 1/2 pulgada, 750W",
  "quantity": 15,
  "price": 89.99,
  "category": "Herramientas Eléctricas",
  "inventory": 1,
  "custom_data": {
    "material": "Acero y Plástico",
    "marca": "DeWalt"
  },
  "low_stock_threshold": 5
}
```

**Validaciones:**
- SKU debe ser único dentro del inventario
- Quantity y price deben ser >= 0
- El inventario debe pertenecer al usuario

**Respuesta exitosa (201):**
```json
{
  "id": 3,
  "name": "Taladro Eléctrico 1/2",
  "sku": "TAL-003",
  /* ... resto de campos ... */
}
```

---

### 4. Actualizar Producto

**Endpoint:** `PUT /api/products/{id}/` o `PATCH /api/products/{id}/`

**Descripción:** Actualiza un producto existente.

**Permisos:** Requiere autenticación + ser dueño del inventario

**Body (JSON - PATCH permite actualización parcial):**
```json
{
  "quantity": 20,
  "price": 85.99
}
```

---

### 5. Eliminar Producto

**Endpoint:** `DELETE /api/products/{id}/`

**Descripción:** Elimina un producto.

**Permisos:** Requiere autenticación + ser dueño del inventario

**Respuesta exitosa (204):** Sin contenido

---

### 6. Ajustar Stock de Producto

**Endpoint:** `POST /api/products/{id}/adjust_stock/`

**Descripción:** Ajusta el stock de un producto (sumar o restar).

**Permisos:** Requiere autenticación + ser dueño del inventario

**Body (JSON):**
```json
{
  "adjustment": -5
}
```

**Nota:** 
- Valores positivos suman al stock actual
- Valores negativos restan del stock actual
- No permite resultados negativos

**Respuesta exitosa (200):**
```json
{
  "message": "Stock ajustado: -5",
  "previous_quantity": 45,
  "current_quantity": 40,
  "data": {
    /* producto completo actualizado */
  }
}
```

**Errores:**
- `400 Bad Request`: Ajuste resultaría en cantidad negativa

---

## 🧪 Ejemplos de Uso

### Ejemplo 1: Flujo Completo de Autenticación

```javascript
// 1. Registro
const registerResponse = await fetch('http://localhost:8000/api/register/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'nuevo@test.com',
    name: 'Usuario Nuevo',
    password: 'password123',
    password2: 'password123'
  })
});
const { access, refresh } = await registerResponse.json();

// 2. Guardar tokens
localStorage.setItem('access_token', access);
localStorage.setItem('refresh_token', refresh);

// 3. Hacer petición autenticada
const profileResponse = await fetch('http://localhost:8000/api/profile/', {
  headers: {
    'Authorization': `Bearer ${access}`,
    'Content-Type': 'application/json'
  }
});

// 4. Renovar token cuando expire (usar interceptor)
const refreshResponse = await fetch('http://localhost:8000/api/token/refresh/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ refresh })
});
const { access: newAccess } = await refreshResponse.json();
localStorage.setItem('access_token', newAccess);
```

---

### Ejemplo 2: Crear Inventario con Productos

```javascript
const accessToken = localStorage.getItem('access_token');

// 1. Crear inventario
const inventoryResponse = await fetch('http://localhost:8000/api/inventories/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    name: 'Mi Primera Tienda',
    template: 1 // ID de plantilla "Ferretería"
  })
});
const inventory = await inventoryResponse.json();

// 2. Agregar productos al inventario
const productResponse = await fetch('http://localhost:8000/api/products/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    name: 'Martillo',
    sku: 'MART-001',
    description: 'Martillo de garra',
    quantity: 50,
    price: 25.99,
    category: 'Herramientas',
    inventory: inventory.id,
    custom_data: {
      material: 'Acero',
      marca: 'Stanley'
    }
  })
});
```

---

### Ejemplo 3: Buscar Productos con Filtros

```javascript
const accessToken = localStorage.getItem('access_token');

// Buscar productos con stock bajo en un inventario específico
const url = new URL('http://localhost:8000/api/products/');
url.searchParams.append('inventory', '1');
url.searchParams.append('low_stock', 'true');
url.searchParams.append('ordering', '-quantity');

const response = await fetch(url, {
  headers: {
    'Authorization': `Bearer ${accessToken}`
  }
});

const { results } = await response.json();
console.log('Productos con stock bajo:', results);
```

---

### Ejemplo 4: Ajustar Stock de Producto

```javascript
const accessToken = localStorage.getItem('access_token');
const productId = 1;

// Restar 10 unidades (venta)
const response = await fetch(`http://localhost:8000/api/products/${productId}/adjust_stock/`, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    adjustment: -10
  })
});

const result = await response.json();
console.log(result.message); // "Stock ajustado: -10"
console.log(`Cantidad anterior: ${result.previous_quantity}`);
console.log(`Cantidad actual: ${result.current_quantity}`);
```

---

## 🚨 Códigos de Estado HTTP

| Código | Significado |
|--------|-------------|
| `200 OK` | Petición exitosa |
| `201 Created` | Recurso creado exitosamente |
| `204 No Content` | Recurso eliminado exitosamente |
| `400 Bad Request` | Datos inválidos o faltantes |
| `401 Unauthorized` | No autenticado o token inválido/expirado |
| `403 Forbidden` | No tienes permisos para esta acción |
| `404 Not Found` | Recurso no encontrado |
| `500 Internal Server Error` | Error del servidor |

---

## 🔒 Seguridad y Mejores Prácticas

### Renovación Automática de Tokens

Implementa un interceptor en tu cliente HTTP para renovar automáticamente el access token:

```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api'
});

// Interceptor para agregar token a todas las peticiones
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Interceptor para renovar token si expira
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // Si el error es 401 y no hemos intentado renovar aún
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        const response = await axios.post(
          'http://localhost:8000/api/token/refresh/',
          { refresh: refreshToken }
        );

        const { access } = response.data;
        localStorage.setItem('access_token', access);

        // Reintentar la petición original con el nuevo token
        originalRequest.headers.Authorization = `Bearer ${access}`;
        return api(originalRequest);
      } catch (refreshError) {
        // Si falla la renovación, redirigir a login
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export default api;
```

---

## 📊 Paginación

Todos los endpoints de lista soportan paginación. La respuesta incluye:

```json
{
  "count": 100,
  "next": "http://localhost:8000/api/products/?page=2",
  "previous": null,
  "results": [...]
}
```

- `count`: Total de resultados
- `next`: URL de la siguiente página (null si es la última)
- `previous`: URL de la página anterior (null si es la primera)
- `results`: Array de resultados de la página actual

**Query Parameters:**
- `page=<número>`: Número de página (default: 1)
- `page_size=<número>`: Resultados por página (default: 20, max: 100)

---

## 📝 Notas Importantes

1. **Tokens JWT**: 
   - Access tokens expiran en 1 hora
   - Refresh tokens expiran en 7 días
   - Implementa renovación automática en tu cliente

2. **Permisos**:
   - Cada usuario solo puede ver/editar sus propios inventarios y productos
   - Los admins tienen acceso completo a todo

3. **SKUs**: Deben ser únicos dentro de cada inventario (no globalmente)

4. **Custom Fields**: 
   - Definidos en BusinessTemplate
   - Valores almacenados en Product.custom_data
   - Estructura flexible con validación de tipos

5. **Stock Status**: Calculado automáticamente basado en quantity y low_stock_threshold

6. **CORS**: Configurado para `localhost:5173` y `localhost:3000`

---

**Última actualización:** Enero 2024  
**Versión API:** 2.0  
**Django:** 5.2  
**DRF:** 3.15