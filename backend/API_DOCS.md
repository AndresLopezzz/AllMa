# 📚 API Documentation - Inventory Management System

## Base URL
```
http://localhost:8000/api/
```

---

## 🔐 Authentication

La API utiliza **Token Authentication**. Después de hacer login o registro, obtendrás un token que debes incluir en los headers de las peticiones protegidas:

```
Authorization: Token <tu_token_aqui>
```

---

## 📋 Endpoints Disponibles

### 1. Registro de Usuario

**Endpoint:** `POST /api/register/`

**Descripción:** Crea una nueva cuenta de usuario y devuelve un token de autenticación.

**Permisos:** Público (no requiere autenticación)

**Body (JSON):**
```json
{
  "email": "usuario@ejemplo.com",
  "name": "Juan Pérez",
  "password": "contraseña123",
  "password2": "contraseña123",
  "role": "empleado",
  "plan": "free"
}
```

**Campos:**
- `email` (requerido): Email único del usuario
- `name` (requerido): Nombre completo
- `password` (requerido): Contraseña (mínimo 8 caracteres)
- `password2` (requerido): Confirmación de contraseña
- `role` (opcional): `admin` o `empleado` (default: `empleado`)
- `plan` (opcional): `free` o `pro` (default: `free`)

**Respuesta exitosa (201):**
```json
{
  "message": "User created successfully",
  "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
  "user": {
    "id": 1,
    "email": "usuario@ejemplo.com",
    "name": "Juan Pérez",
    "role": "empleado",
    "plan": "free"
  }
}
```

**Errores:**
- `400 Bad Request`: Contraseñas no coinciden, email ya existe, o campos inválidos

---

### 2. Login

**Endpoint:** `POST /api/login/`

**Descripción:** Autentica al usuario y devuelve un token.

**Permisos:** Público (no requiere autenticación)

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
  "user": {
    "id": 1,
    "email": "usuario@ejemplo.com",
    "name": "Juan Pérez",
    "role": "empleado",
    "plan": "free",
    "is_active": true
  }
}
```

**Errores:**
- `400 Bad Request`: Credenciales inválidas

---

### 3. Obtener Perfil

**Endpoint:** `GET /api/profile/`

**Descripción:** Obtiene los datos del usuario autenticado.

**Permisos:** Requiere autenticación (Token)

**Headers:**
```
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
```

**Respuesta exitosa (200):**
```json
{
  "id": 1,
  "email": "usuario@ejemplo.com",
  "name": "Juan Pérez",
  "role": "empleado",
  "plan": "free",
  "is_active": true,
  "date_joined": "2024-01-15T10:30:00Z"
}
```

**Errores:**
- `401 Unauthorized`: Token inválido o no proporcionado

---

### 4. Actualizar Perfil

**Endpoint:** `PUT /api/profile/`

**Descripción:** Actualiza los datos del usuario autenticado (actualización parcial permitida).

**Permisos:** Requiere autenticación (Token)

**Headers:**
```
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
```

**Body (JSON):**
```json
{
  "name": "Juan Carlos Pérez",
  "role": "admin"
}
```

**Campos editables:**
- `name`: Nombre completo
- `role`: `admin` o `empleado`
- `plan`: `free` o `pro`

**Campos de solo lectura:**
- `id`, `email`, `date_joined`

**Respuesta exitosa (200):**
```json
{
  "id": 1,
  "email": "usuario@ejemplo.com",
  "name": "Juan Carlos Pérez",
  "role": "admin",
  "plan": "free",
  "is_active": true,
  "date_joined": "2024-01-15T10:30:00Z"
}
```

**Errores:**
- `401 Unauthorized`: Token inválido o no proporcionado
- `400 Bad Request`: Datos inválidos

---

## 🧪 Ejemplos de Uso

### Ejemplo 1: Registro y Login con cURL

```bash
# Registro
curl -X POST http://localhost:8000/api/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@test.com",
    "name": "Test User",
    "password": "password123",
    "password2": "password123"
  }'

# Login
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test@test.com",
    "password": "password123"
  }'
```

### Ejemplo 2: Obtener Perfil con JavaScript (Fetch)

```javascript
const token = '9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b';

fetch('http://localhost:8000/api/profile/', {
  method: 'GET',
  headers: {
    'Authorization': `Token ${token}`,
    'Content-Type': 'application/json'
  }
})
  .then(response => response.json())
  .then(data => console.log(data))
  .catch(error => console.error('Error:', error));
```

### Ejemplo 3: Actualizar Perfil con Axios

```javascript
import axios from 'axios';

const token = '9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b';

axios.put('http://localhost:8000/api/profile/', 
  {
    name: 'Nuevo Nombre',
    role: 'admin'
  },
  {
    headers: {
      'Authorization': `Token ${token}`,
      'Content-Type': 'application/json'
    }
  }
)
  .then(response => console.log(response.data))
  .catch(error => console.error('Error:', error));
```

---

## 🚨 Códigos de Estado HTTP

| Código | Significado |
|--------|-------------|
| `200 OK` | Petición exitosa |
| `201 Created` | Recurso creado exitosamente |
| `400 Bad Request` | Datos inválidos o faltantes |
| `401 Unauthorized` | No autenticado o token inválido |
| `403 Forbidden` | No tienes permisos para esta acción |
| `404 Not Found` | Recurso no encontrado |
| `500 Internal Server Error` | Error del servidor |

---

## 📝 Notas Importantes

1. **Contraseñas**: Deben tener al menos 8 caracteres
2. **Tokens**: No expiran automáticamente (considera implementar JWT en el futuro)
3. **Email**: Se usa como identificador único en lugar de username
4. **CORS**: Configurado para aceptar peticiones desde `localhost:5173` y `localhost:3000`

---

## 🔜 Próximos Endpoints (En Desarrollo)

- `GET /api/inventory/products/` - Listar productos
- `POST /api/inventory/products/` - Crear producto
- `GET /api/inventory/products/{id}/` - Obtener producto
- `PUT /api/inventory/products/{id}/` - Actualizar producto
- `DELETE /api/inventory/products/{id}/` - Eliminar producto

---

**Última actualización:** Enero 2024
**Versión API:** 1.0