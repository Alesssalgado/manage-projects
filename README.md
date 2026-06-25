# 📁 manage-projects

REST API para gestión de proyectos y documentos, construida con principalmente **FastAPI** y **PostgreSQL**.

---

## 📂 Estructura del proyecto

```
.
├── .github/
│   └── workflows/          # CI/CD pipelines
├── app/
│   ├── routers/            # Endpoints organizados por recurso
│   │   ├── documents.py    # Rutas de documentos
│   │   ├── projects.py     # Rutas de proyectos
│   │   └── users.py        # Rutas de usuarios
│   ├── auth.py             # Lógica JWT
│   ├── config.py           # Variables de configuración
│   ├── crud_postgresql.py  # Operaciones CRUD en base de datos
│   ├── database.py         # Configuración del motor SQLAlchemy
│   ├── dependencies.py     # Dependencias de FastAPI
│   ├── main.py             # Punto de entrada de la aplicación
│   ├── models.py           # Modelos ORM (SQLAlchemy)
│   └── schemas.py          # Esquemas de validación (Pydantic)
├── .env                    # Variables de entorno
├── docker-compose.yml      # Configuración de servicios Docker
└── Dockerfile              # Imagen Docker de la aplicación
```

---

## ⚙️ Instalación y configuración

### 1. Clonar y crear entorno virtual

```bash
git clone <url-del-repositorio>
cd <nombre-del-proyecto>

python -m venv venv
source venv/bin/activate        # Linux / macOS
venv\Scripts\activate           # Windows
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

**Dependencias principales:**

| Paquete | Uso |
|---------|-----|
| `fastapi` | Framework web |
| `sqlalchemy` | ORM |
| `psycopg2-binary` | Driver PostgreSQL |
| `uvicorn` | Servidor ASGI |
| `pydantic` / `pydantic-settings` | Validación y configuración |
| `pyjwt` / `python-jose` | JSON Web Tokens |
| `python-multipart` | Subida de archivos |
| `ruff` | Linter y formateador de código |

### 3. Configurar variables de entorno

```bash
cp .env.example .env
```

---

## 🔑 Variables de entorno

| Variable | Descripción |
|----------|-------------|
| `DATABASE_URL` | URL de conexión a PostgreSQL |
| `SECRET_KEY` | Clave secreta para firmar los JWT |

---

## 🚀 Ejecutar el servidor

```bash
uvicorn app.main:app --reload
```

La API quedará disponible en `http://localhost:8000`.  
La documentación interactiva estará en `http://localhost:8000/docs`.

---

## 🔐 Autenticación

La API usa **JWT Bearer tokens** con una validez de **2 hora**. Para acceder a los endpoints protegidos, incluye el token en el header:

```
Authorization: Bearer <access_token>
```

---

## 👥 Roles y permisos

| Acción | Admin (owner) | Participante |
|--------|:---:|:---:|
| Ver proyecto e info | ✅ | ✅ |
| Actualizar nombre/descripción | ✅ | ✅ |
| Ver documentos | ✅ | ✅ |
| Subir documentos | ✅ | ✅ |
| Descargar documentos | ✅ | ✅ |
| Actualizar documentos | ✅ | ✅ |
| Invitar usuarios | ✅ | ❌ |
| Eliminar documentos | ✅ | ❌ |
| Eliminar proyecto | ✅ | ❌ |

---

## 🗄 Modelos de datos

```
users
├── id_user       INTEGER PK
├── username      TEXT UNIQUE NOT NULL
├── password      TEXT NOT NULL  (SHA-256)
└── date_at       DATETIME

projects
├── id_project    INTEGER PK
├── name          TEXT NOT NULL
├── description   TEXT
└── date_at       DATETIME

project_users  (tabla de unión)
├── id_project1   FK → projects.id_project  PK
├── id_user1      FK → users.id_user        PK
└── TypeUser      ENUM('admin', 'participant')

documents
├── id_document   INTEGER PK
├── name          TEXT NOT NULL
├── filename      TEXT NOT NULL  (nombre original)
├── filepath      TEXT NOT NULL  (ruta en disco)
├── date_at       DATETIME
└── id_project2   FK → projects.id_project
```
