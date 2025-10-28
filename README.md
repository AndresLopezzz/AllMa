# 🏢 Sistema de Gestión de Inventarios - SaaS

Sistema completo de inventarios con backend Django y frontend React, diseñado para pequeñas y medianas empresas.

---

## 📋 Tabla de Contenidos

- [Stack Tecnológico](#-stack-tecnológico)
- [Características](#-características)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Instalación](#-instalación)
- [Configuración](#-configuración)
- [API Endpoints](#-api-endpoints)
- [Desarrollo](#-desarrollo)
- [Deploy](#-deploy)

---

## 🚀 Stack Tecnológico

### **Backend:**
- **Django 5.2+** - Framework web
- **Django REST Framework** - API REST
- **PostgreSQL** - Base de datos
- **JWT (Simple JWT)** - Autenticación
- **Cloudinary** - Almacenamiento de imágenes
- **psycopg3** - Adaptador PostgreSQL

### **Frontend:**
- **React 18+** - Librería UI
- **TypeScript** - Tipado estático
- **Vite** - Build tool
- **Bun** - Runtime y package manager
- **TanStack Router** - Enrutamiento (file-based)
- **TanStack Query** - Manejo de estado del servidor
- **TanStack Form** - Formularios con validación
- **shadcn/ui** - Componentes UI
- **Tailwind CSS** - Estilos

### **Deploy:**
- **Railway** - Backend
- **Vercel** - Frontend

---

## ✨ Características

### **Autenticación:**
- ✅ Registro de usuarios con email
- ✅ Login con JWT (Access + Refresh tokens)
- ✅ Renovación automática de tokens
- ✅ Roles: Admin y Empleado
- ✅ Planes: Free y Pro

### **Inventario (En desarrollo):**
- [ ] CRUD de productos
- [ ] Categorías
- [ ] Proveedores
- [ ] Control de stock
- [ ] Historial de movimientos
- [ ] Alertas de stock bajo

---

## 📁 Estructura del Proyecto

```
inventory/
├── backend/                 # Backend Django
│   ├── accounts/           # App de usuarios
│   │   ├── models.py       # Modelo User personalizado
│   │   ├── serializers.py  # Serializers DRF
│   │   ├── views.py        # Vistas API
│   │   └── urls.py         # Rutas
│   ├── inventory/          # App de inventario
│   ├── backend/            # Configuración Django
│   │   └── settings.py
│   ├── manage.py
│   ├── requirements.txt    # Dependencias Python
│   ├── .env               # Variables de entorno (no versionado)
│   └── API_DOCS.md        # Documentación API
│
├── frontend/              # Frontend React (próximamente)
│
└── README.md
```

---

## 🛠️ Instalación

### **Prerrequisitos:**
- Python 3.11+ (⚠️ Si usas 3.14, algunas librerías pueden tener problemas)
- PostgreSQL 14+
- Node.js 18+ / Bun
- Git

### **Backend:**

```bash
# 1. Clonar el repositorio
git clone <tu-repo>
cd inventory/backend

# 2. Crear entorno virtual
python -m venv venv

# 3. Activar entorno virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 4. Instalar dependencias
pip install -r requirements.txt

# 5. Configurar variables de entorno
# Copia .env.example a .env y edita los valores
cp .env.example .env

# 6. Ejecutar migraciones
python manage.py migrate

# 7. Crear superusuario
python manage.py createsuperuser

# 8. Iniciar servidor
python manage.py runserver
```

El servidor estará disponible en: `http://localhost:8000`

---

## ⚙️ Configuración

### **Variables de Entorno (`.env`):**

```env
# Django
SECRET_KEY=tu-secret-key-aqui
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Base de datos
DB_NAME=inventario_db
DB_USER=postgres
DB_PASSWORD=tu-password
DB_HOST=localhost
DB_PORT=5432

# Cloudinary (opcional por ahora)
# CLOUDINARY_CLOUD_NAME=
# CLOUDINARY_API_KEY=
# CLOUDINARY_API_SECRET=
```

### **Crear base de datos PostgreSQL:**

```sql
CREATE DATABASE inventario_db;
CREATE USER postgres WITH PASSWORD 'tu-password';
GRANT ALL PRIVILEGES ON DATABASE inventario_db TO postgres;
```

---

## 📡 API Endpoints

### **Autenticación:**

| Método | Endpoint              | Descripción                    | Auth |
|--------|-----------------------|--------------------------------|------|
| POST   | `/api/register/`      | Registro de usuario            | No   |
| POST   | `/api/login/`         | Login (devuelve JWT)           | No   |
| POST   | `/api/token/`         | Obtener tokens JWT             | No   |
| POST   | `/api/token/refresh/` | Renovar access token           | No   |
| GET    | `/api/profile/`       | Obtener perfil de usuario      | Sí   |
| PUT    | `/api/profile/`       | Actualizar perfil              | Sí   |

### **Ejemplos de uso:**

#### **Registro:**
```bash
POST /api/register/
Content-Type: application/json

{
  "email": "usuario@ejemplo.com",
  "name": "Juan Pérez",
  "password": "password123",
  "password2": "password123",
  "role": "empleado",
  "plan": "free"
}
```

#### **Login:**
```bash
POST /api/login/
Content-Type: application/json

{
  "username": "usuario@ejemplo.com",
  "password": "password123"
}
```

Respuesta:
```json
{
  "token": "...",
  "access": "eyJhbGci...",
  "refresh": "eyJhbGci...",
  "user": { ... }
}
```

#### **Perfil (con autenticación):**
```bash
GET /api/profile/
Authorization: Bearer <access_token>
```

📖 **Documentación completa:** Ver `backend/API_DOCS.md`

---

## 💻 Desarrollo

### **Backend:**

```bash
# Activar entorno virtual
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Crear nueva app
python manage.py startapp nombre_app

# Crear migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Ejecutar tests
python manage.py test

# Acceder al admin
http://localhost:8000/admin/
```

### **Frontend (Próximamente):**

```bash
cd frontend

# Instalar dependencias con Bun
bun install

# Modo desarrollo
bun run dev

# Build para producción
bun run build
```

---

## 🚢 Deploy

### **Backend (Railway):**

1. Crear cuenta en [Railway](https://railway.app/)
2. Conectar repositorio de GitHub
3. Agregar PostgreSQL plugin
4. Configurar variables de entorno
5. Deploy automático

### **Frontend (Vercel):**

1. Crear cuenta en [Vercel](https://vercel.com/)
2. Importar repositorio
3. Configurar variables de entorno
4. Deploy automático

---

## 📝 Notas Importantes

### **Seguridad:**
- ✅ `.env` está en `.gitignore` - NUNCA subir credenciales
- ✅ JWT tokens expiran (Access: 1h, Refresh: 7d)
- ✅ Contraseñas hasheadas con PBKDF2
- ✅ CORS configurado para dominios específicos

### **Base de datos:**
- SQLite disponible para desarrollo rápido
- PostgreSQL recomendado para producción

### **Compatibilidad Python:**
- ⚠️ Python 3.14 puede tener problemas con Pillow
- ✅ Python 3.11-3.12 totalmente compatible

---

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama: `git checkout -b feature/nueva-funcionalidad`
3. Commit: `git commit -m 'Agregar nueva funcionalidad'`
4. Push: `git push origin feature/nueva-funcionalidad`
5. Abre un Pull Request

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT.

---

## 👥 Autores

- **Tu Nombre** - Desarrollo inicial

---

## 🙏 Agradecimientos

- Django Team
- React Team
- TanStack Team
- shadcn/ui

---

**Estado del Proyecto:** 🟡 En Desarrollo Activo

**Última actualización:** Enero 2025