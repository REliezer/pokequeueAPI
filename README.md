# PokeQueue API

Una API REST desarrollada con FastAPI para gestionar solicitudes de Pokémon de forma asíncrona utilizando Azure Storage Queue y Azure Blob Storage.

## 🏗️ Arquitectura del Sistema PokeQueue

Este repositorio es parte de un ecosistema completo de microservicios para el procesamiento de reportes de Pokémon. El sistema completo está compuesto por los siguientes componentes:

### 🔗 Repositorios Relacionados

| Componente | Repositorio | Descripción |
|------------|-------------|-------------|
| **Frontend** | [PokeQueue UI](https://github.com/REliezer/pokequeue-ui) | Interfaz de usuario web para solicitar y gestionar reportes de Pokémon |
| **API REST** | [PokeQueue API](https://github.com/REliezer/pokequeueAPI) | Este repositorio - API principal que gestiona solicitudes de reportes y coordinación del sistema |
| **Azure Functions** | [PokeQueue Functions](https://github.com/REliezer/pokequeue-function) | Procesamiento asíncrono de reportes |
| **Base de Datos** | [PokeQueue SQL Scripts](https://github.com/REliezer/pokequeue-sql) | Scripts SQL para la configuración y mantenimiento de la base de datos |
| **Infraestructura** | [PokeQueue Terraform](https://github.com/REliezer/pokequeue-terrafom) | Configuración de infraestructura como código (IaC) |

### 🔄 Flujo de Datos del Sistema Completo

1. **PokeQueue UI** → Usuario solicita reporte desde la interfaz web
2. **PokeQueue UI** → Envía solicitud a **PokeQueue API**
3. **PokeQueue API** *(este repo)* → Valida la solicitud y la guarda en la base de datos
4. **PokeQueue API** → Envía mensaje a la cola de Azure Storage
5. **PokeQueue Function** → Procesa el mensaje de la cola
6. **PokeQueue Function** → Consulta PokéAPI y genera el reporte CSV
7. **PokeQueue Function** → Almacena el CSV en Azure Blob Storage
8. **PokeQueue Function** → Notifica el estado a **PokeQueue API**
9. **PokeQueue UI** → Consulta el estado y permite descargar el reporte terminado

### 🏗️ Diagrama de Arquitectura

```
   ┌─────────────────┐
   │   PokeQueue UI  │
   │ (Frontend Web)  │
   └─────────┼───────┘
             │
             ▼ HTTP/REST
  ┌─────────────────┐    ┌─────────────────┐
  │  PokeQueue API  │────│   Azure SQL DB  │
  │   (REST API)    │    │  (Persistencia) │
  └─────────┼───────┘    └─────────────────┘
            │
            ▼ Queue Message
   ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
   │  Azure Storage  │────│ PokeQueue Func  │────│   Azure Blob    │
   │     Queue       │    │ (Procesamiento) │    │    Storage      │
   └─────────────────┘    └─────────┼───────┘    └─────────────────┘
                                    │
                                    ▼ HTTP API Call
                           ┌─────────────────┐
                           │    PokéAPI      │
                           │ (Datos Pokémon) │
                           └─────────────────┘
```

## 🚀 Características

- **API REST** construida con FastAPI
- **Procesamiento asíncrono** usando Azure Storage Queue
- **Almacenamiento de archivos** con Azure Blob Storage
- **Base de datos SQL Server** con procedimientos almacenados
- **CORS habilitado** para integración con frontends
- **Containerización** con Docker
- **Despliegue en Azure** con Azure Container Registry

## 📋 Requisitos Previos

- Python 3.13+
- Cuenta de Azure con:
  - Azure Storage Account
  - SQL Server Database
  - Azure Container Registry (para despliegue)
- Docker (opcional, para containerización)

## 🛠️ Instalación

### Instalación Local

1. **Clonar el repositorio**
   ```bash
   git clone https://github.com/REliezer/pokequeueAPI
   cd pokequeueAPI
   ```

2. **Crear entorno virtual**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar variables de entorno**
   
   Crear un archivo `.env` en la raíz del proyecto:
   ```env
   AZURE_SAK=your_azure_storage_connection_string
   AZURE_STORAGE_CONTAINER=your_container_name
   QUEUE_NAME=your_queue_name
   # Agregar otras variables de conexión a BD
   ```

5. **Ejecutar la aplicación**
   ```bash
   python main.py
   ```

   La API estará disponible en: `http://localhost:8000`

### Instalación con Docker

1. **Construir la imagen**
   ```bash
   docker buildx build --platform linux/amd64 -t pokeapi:latest . --load
   ```

2. **Ejecutar el contenedor**
   ```bash
   docker run -d -p 8000:8000 --name pokeapi-container --env-file .env pokeapi:latest
   ```

## 🔗 Endpoints de la API

### Información General

- **GET** `/` - Obtener todos los mensajes
- **GET** `/api/version` - Obtener versión de la API (v0.5.0)

### Gestión de Solicitudes de Pokémon

- **GET** `/api/request` - Obtener todas las solicitudes con estado
- **GET** `/api/request/{id}` - Obtener solicitud específica por ID
- **POST** `/api/request` - Crear nueva solicitud de Pokémon
- **PUT** `/api/request` - Actualizar solicitud existente
- **DELETE** `/api/report/{id}` - Eliminar solicitud y archivo asociado

### Documentación Interactiva

Una vez que la aplicación esté ejecutándose, puedes acceder a:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 📝 Modelo de Datos

### PokemonRequest

```json
{
  "id": 1,
  "pokemon_type": "fire",
  "url": "https://storage.blob.core.windows.net/container/file.csv",
  "status": "completed",
  "sample_size": 100
}
```

#### Campos:

- **id** (opcional): ID único de la solicitud
- **pokemon_type** (opcional): Tipo de Pokémon (ej: "fire", "water", "grass")
- **url** (opcional): URL del archivo CSV generado
- **status** (opcional): Estado de la solicitud
  - `sent` - Enviada
  - `inprogress` - En progreso
  - `completed` - Completada
  - `failed` - Fallida
- **sample_size** (opcional): Número máximo de registros a procesar

## 🧪 Estructura del Proyecto

```
pokequeueAPI/
├── controllers/
│   └── PokeRequestController.py    # Lógica de negocio para solicitudes
├── models/
│   └── PokeRequest.py              # Modelo de datos Pydantic
├── utils/
│   ├── ABlob.py                    # Utilidades para Azure Blob Storage
│   ├── AQueue.py                   # Utilidades para Azure Storage Queue
│   └── database.py                 # Conexión y operaciones de BD
├── main.py                         # Punto de entrada de la aplicación
├── requirements.txt                # Dependencias de Python
├── Dockerfile                      # Imagen Docker
├── release.txt                     # Comandos de despliegue
└── README.md                       # Este archivo
```

## 🚀 Instalación Completa del Sistema PokeQueue

Para desplegar el sistema completo, necesitas configurar todos los componentes en el siguiente orden:

### 1. Infraestructura (Terraform)
```bash
# Clonar el repositorio de infraestructura
git clone https://github.com/REliezer/pokequeue-terrafom.git
cd pokequeue-terrafom

# Configurar variables de Terraform
terraform init
terraform plan
terraform apply
```

### 2. Base de Datos (SQL Scripts)
```bash
# Clonar el repositorio de base de datos
git clone https://github.com/REliezer/pokequeue-sql.git
cd pokequeue-sql

# Ejecutar scripts SQL en Azure SQL Database
# (Revisar el README del repositorio SQL para instrucciones específicas)
```

### 3. API REST  (Este Repositorio)
```bash
# Clonar y desplegar la API
git clone https://github.com/REliezer/pokequeueAPI.git
cd pokequeueAPI

# Seguir las instrucciones del README de la API
```

### 4. Azure Functions
```bash
# Clonar este repositorio
git clone https://github.com/REliezer/pokequeue-function.git
cd pokequeue-function

# Seguir las instrucciones del README para configuración y despliegue
```

### 5. Frontend UI
```bash
# Clonar y desplegar el frontend
git clone https://github.com/REliezer/pokequeue-ui.git
cd pokequeue-ui

# Seguir las instrucciones del README del UI para configuración y despliegue
```

## 🚀 Despliegue en Azure

### Usando Azure Container Registry

1. **Login en ACR**
   ```bash
   az acr login --name acrpokequeuerefedev
   ```

2. **Etiquetar imagen**
   ```bash
   docker tag pokeapi:latest acrpokequeuerefedev.azurecr.io/pokeapi:latest
   docker tag pokeapi:latest acrpokequeuerefedev.azurecr.io/pokeapi:0.5.0
   ```

3. **Subir imagen**
   ```bash
   docker push acrpokequeuerefedev.azurecr.io/pokeapi:latest
   docker push acrpokequeuerefedev.azurecr.io/pokeapi:0.5.0
   ```

## 🔧 Configuración de Base de Datos

La API utiliza procedimientos almacenados en el esquema `pokequeue`:

- `pokequeue.create_poke_request` - Crear nueva solicitud
- `pokequeue.update_poke_request` - Actualizar solicitud existente
- `pokequeue.delete_poke_request` - Eliminar solicitud

### Tablas Principales:

- `pokequeue.requests` - Solicitudes de Pokémon
- `pokequeue.status` - Estados de las solicitudes
- `pokequeue.MESSAGES` - Mensajes del sistema

## 🛡️ Características de Seguridad

- **CORS** configurado para permitir orígenes específicos
- **URLs firmadas** para acceso seguro a archivos blob
- **Validación de datos** con Pydantic
- **Manejo de errores** robusto con logging
- **Eliminación segura** de archivos con verificación previa

## 🔍 Logging y Monitoreo

La aplicación incluye logging detallado para:
- Operaciones de base de datos
- Operaciones de Azure Storage
- Errores y excepciones
- Flujo de procesamiento de solicitudes

## 🤝 Contribuir

1. Fork el proyecto
2. Crear rama para nueva funcionalidad (`git checkout -b feature/nueva-funcionalidad`)
3. Commit los cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abrir Pull Request

## Licencia

Este proyecto es parte de un trabajo académico para Sistemas Expertos II PAC 2025.

---

**Versión Actual:** 0.5.0  
**Última Actualización:** 2025
