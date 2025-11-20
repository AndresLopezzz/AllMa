# Allma Inventory

Sistema modular de inventarios diseñado para adaptarse a diferentes tipos de negocios mediante plantillas personalizables. Permite a pequeñas y medianas empresas gestionar sus productos con campos dinámicos, múltiples inventarios, control de stock y tracking de movimientos.

**Estado actual:** MVP completo (Backend + Frontend)  
**Versión:** 1.0.0 (MVP)  
**Última actualización:** 2025-11-20

---

## Resumen

Allma Inventory es una solución SaaS orientada a gestionar inventarios con flexibilidad mediante plantillas dinámicas (custom_fields). El proyecto ya incluye una API REST completa, autenticación JWT, control de planes, integración con Cloudinary para imágenes y una interfaz de usuario (frontend) lista para uso MVP.

---

## Características principales (MVP)

- Sistema de plantillas dinámicas por tipo de negocio (ej. Ferretería, Ropa, Restaurante).
- Inventarios por usuario con plantillas y plantillas personalizables por inventario.
- CRUD completo de productos con validación de campos dinámicos (custom_fields).
- SKU único por inventario y validaciones de integridad (cantidad y precio).
- Control de stock con alertas de stock bajo y endpoint de alertas.
- Tracking de movimientos (registro de entradas/salidas/ajustes).
- Exportación a CSV de inventarios completos.
- Autenticación con JWT (access/refresh tokens) y endpoints de cuenta (registro, login, perfil).
- Planes (Free / Pro / Premium) con límites configurables (inventarios/productos).
- Soft delete en productos e historial para restauración.
- Integración con Cloudinary para almacenamiento y optimización de imágenes (thumbnail/medium/full).
- Frontend completo usando React + TypeScript con TanStack Router, TanStack Query y formularios dinámicos.
- CI: pipeline de GitHub Actions que compila frontend con Bun/Vite y ejecuta tests (pytest).

---

## Stack Tecnológico

- Backend: Django 5.2 + Django REST Framework + PostgreSQL
- Autenticación: JWT (djangorestframework-simplejwt)
- Almacenamiento: Cloudinary (django-cloudinary-storage)
- Testing: pytest + pytest-django + coverage (cobertura: ~85%)
- Frontend: React + TypeScript + Bun + Vite
  - Routing: TanStack Router
  - Server state: TanStack Query
  - Forms: TanStack Form + Zod
  - UI: shadcn/ui + Tailwind CSS
  - Gráficas: Recharts
  - Notificaciones: Sonner
- CI: GitHub Actions (build frontend + run tests)

---

## Estructura del Proyecto

```
inventory/
├── backend/                # Django app y API
│   ├── accounts/           # Usuarios y autenticación
│   ├── inventory/          # Lógica de inventarios, productos y movimientos
│   ├── backend/            # Configuración del proyecto (settings, urls)
│   └── manage.py
├── frontend/               # Aplicación React + Bun + Vite
│   ├── src/
│   └── bun.lock
└── README.md               # Este archivo
```

---

## Requisitos previos

- Python 3.11+
- PostgreSQL 14+
- Bun (para desarrollo del frontend) — alternativamente Node 18+ si no se usa Bun
- Cuenta en Cloudinary para subir/optimizar imágenes
- (Opcional) Docker/Docker Compose para levantar Postgres localmente

---

## Instalación y configuración local (rápido)

### Backend

1. Crear y activar un entorno virtual:
   ```bash
   python -m venv venv
   # Unix/macOS
   source venv/bin/activate
   # Windows
   venv\Scripts\activate
   ```

2. Instalar dependencias:
   ```bash
   pip install -r backend/requirements.txt
   ```

3. Copiar el archivo de ejemplo de variables de entorno y configurarlo:
   ```bash
   cp backend/.env.example backend/.env
   # Edita backend/.env con las credenciales DB, SECRET_KEY, CLOUDINARY_*
   ```

4. Ejecutar migraciones y crear superuser:
   ```bash
   python backend/manage.py migrate
   python backend/manage.py createsuperuser
   ```

5. (Opcional) Poblar con datos de ejemplo:
   ```bash
   python backend/manage.py seed_data --clear
   ```

6. Levantar servidor de desarrollo:
   ```bash
   python backend/manage.py runserver
   ```

### Frontend

1. Instalar Bun (o usar Node):
   ```bash
   curl -fsSL https://bun.sh/install | bash
   ```

2. Instalar dependencias en `frontend/`:
   ```bash
   cd frontend
   bun install
   ```

3. Configurar variables (ej.: `VITE_API_URL` en `.env.local`):
   ```bash
   cp .env.example .env.local
   # o crear .env.local con:
   # VITE_API_URL=http://localhost:8000
   ```

4. Levantar en modo desarrollo:
   ```bash
   bun run dev
   ```

5. Build de producción:
   ```bash
   bun run build
   ```

---

## Endpoints principales (Resumen)

La API está documentada en `/backend/api_docs.md`. A continuación algunos endpoints principales:

- POST `/api/accounts/register/` — registrar usuario
- POST `/api/accounts/login/` — login (tokens access + refresh)
- GET `/api/accounts/profile/` — perfil del usuario
- GET/POST `/api/templates/` — plantillas de negocio
- GET/POST/PUT/DELETE `/api/inventories/` — inventarios
- GET `/api/inventories/{id}/stats/` — estadísticas por inventario
- GET `/api/inventories/{id}/export/` — exportar a CSV
- GET/POST/PUT/DELETE `/api/products/` — productos
- POST `/api/products/{id}/adjust_stock/` — ajustar cantidad y crear movimiento
- GET `/api/dashboard/` — métricas y datos para gráficas
- GET `/api/alerts/` — productos en stock bajo

Para detalles (request/response) revisa `backend/api_docs.md`.

---

## Datos de prueba / Seed

El comando `seed_data` crea usuarios, plantillas, inventarios y productos de ejemplo para pruebas y desarrollo.
Datos generados típicamente:
- 3 usuarios (free / pro / pro2)
- 5 plantillas (Ferretería, Ropa, Electrónica, Alimentos, Librería)
- 10 inventarios
- ~100+ productos
- 50 movimientos

Credenciales de ejemplo (seed):
- `free@example.com` | `password123` (Plan Free)
- `pro@example.com` | `password123` (Plan Pro)
- `pro2@example.com` | `password123` (Plan Pro)

---

## Pruebas y cobertura

Ejecutar tests en el backend:

```bash
# desde la raíz del proyecto
python -m pytest -q
# o con cobertura
coverage run --source='backend' -m pytest -q
coverage report
```

Cobertura reportada (backend): ~85%.

La pipeline de CI (`.github/workflows/ci.yml`) construye el frontend y ejecuta los tests para proteger la rama `main`.

---

## Integraciones y herramientas relevantes

- Cloudinary para subir y optimizar imágenes (tamaños `thumbnail`, `medium`, `full`).
- django-filter para filtros en endpoints de list.
- WhiteNoise para servir static files en producción.
- Gunicorn como WSGI para producción.
- TanStack Query + TanStack Router en frontend para estado y routing.
- shadcn/ui + Tailwind para componentes UI.

---

## Desarrollo y contribución

Sugerencias para contribuir:
1. Crea una rama desde `main` (naming: `feature/*`, `fix/*`).
2. Implementa los cambios con tests automáticos.
3. Ejecuta los tests localmente.
4. Crea un Pull Request con descripción clara y referencia a issues.

Recomendación:
- Mantener PRs pequeños y enfocados.
- Añadir tests a nuevas funcionalidades.
- Mantener consistencia en los estilos (eslint + prettier/tailwind).

---

## Próximos pasos y mejoras (V2 y beyond)

- Pulir la experiencia de usuario (UX) y accesibilidad.
- Integración de notificaciones por email y push (por ejemplo para alertas).
- Sistema de pago / suscripción (billing) y Webhooks.
- Rate limiting para API pública y endpoints con límites por plan.
- Reportes avanzados y exportación a XLSX/PDF.
- Analíticas y métricas (event tracking) para el dashboard.
- Monitoreo, alertas y logs centralizados.
- Mejoras de pruebas end-to-end (Playwright/Cypress).

---

## Changelog (resumen v1.0 — MVP)

- Implementación completa del backend (API REST).
- Plantillas dinámicas y custom_fields por inventario.
- CRUD de inventarios y productos con validaciones.
- Tracking de movimientos y exportación a CSV.
- Alertas de stock bajo y dashboard con métricas.
- Integración con Cloudinary y optimizaciones de imágenes.
- Frontend con React + Bun + Vite + TanStack (MVP completado).
- Tests automáticos y CI configurado (build + tests).

---

## Licencia

MIT License

---
