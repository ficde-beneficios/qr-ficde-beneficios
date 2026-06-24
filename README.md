# Beneficios FICDE QR

Sistema institucional de validación temporal mediante código QR para beneficios y descuentos de la comunidad FICDE.

La aplicación permite generar un QR temporal desde una sesión activa y validarlo desde un celular o navegador en comercios adheridos. Está pensada para una experiencia simple, rápida y clara, con enfoque institucional para uso en Paraguay y Argentina.

## Objetivo

Brindar una forma práctica de acreditar membresía o pertenencia a la comunidad FICDE mediante un código QR con vencimiento, evitando validaciones manuales y facilitando el uso de beneficios institucionales.

## Funcionalidades

- Inicio institucional con acceso demo.
- Generación de QR temporal para el usuario autenticado.
- Validación web del QR desde un comercio adherido.
- Mensajes visuales claros para aprobación o rechazo.
- Diseño institucional FICDE con identidad visual azul y naranja.
- Despliegue online con Render.

## Estructura del proyecto

```text
qr-ficde-beneficios/
├─ app.py
├─ requirements.txt
├─ Procfile
├─ render.yaml
├─ README.md
├─ static/
│  ├─ style.css
│  └─ images/
│     └─ logo-ficde.jpg
└─ templates/
   ├─ home.html
   ├─ login_ok.html
   ├─ logout.html
   ├─ error.html
   ├─ mi_qr.html
   └─ validacion.html
```

## Requisitos

- Python 3.11 o compatible
- pip
- Entorno virtual recomendado

## Instalación local

1. Clonar el repositorio:

```bash
git clone https://github.com/ficde-beneficios/qr-ficde-beneficios.git
cd qr-ficde-beneficios
```

2. Crear y activar entorno virtual:

### Windows
```bash
python -m venv .venv
.venv\Scripts\activate
```

### macOS / Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. Instalar dependencias:

```bash
pip install -r requirements.txt
```

4. Configurar variables de entorno.

5. Ejecutar la aplicación:

```bash
python app.py
```

Luego abrir en el navegador:

```text
http://127.0.0.1:5000
```

## Variables de entorno

La aplicación utiliza variables de entorno para configuración y seguridad:

```text
FLASK_SECRET_KEY=tu_clave_secreta
TOKEN_SECRET=tu_token_secreto
QR_LIFETIME_SECONDS=600
BASE_URL=https://tu-dominio-o-url-render
```

### Descripción

- `FLASK_SECRET_KEY`: clave de sesión de Flask.
- `TOKEN_SECRET`: clave para firmar o validar el token temporal.
- `QR_LIFETIME_SECONDS`: tiempo de validez del QR en segundos.
- `BASE_URL`: URL pública usada para construir el enlace de validación del QR.

## Uso

### Flujo demo

1. Ingresar a `/login-demo`
2. Abrir `/mi-qr`
3. Mostrar o escanear el QR
4. Abrir la URL `/validar/<token>`
5. Ver resultado:
   - `Descuento aprobado`
   - `Código rechazado`

## Despliegue en Render

La aplicación puede desplegarse como **Web Service** en Render.

### Configuración recomendada

- Environment: `Python 3`
- Build Command:
```bash
pip install -r requirements.txt
```

- Start Command:
```bash
gunicorn app:app
```

Render volverá a desplegar automáticamente la app al hacer push a la rama conectada del repositorio.

## Diseño institucional

La interfaz fue ajustada con identidad visual FICDE:

- Logo institucional
- Paleta azul y naranja
- Diseño claro y responsive
- Pantallas optimizadas para celular y navegador

## Estado actual

Versión funcional para demostración institucional:

- QR temporal operativo
- Validación online operativa
- Diseño institucional aplicado
- Deploy activo en Render

## Próximas mejoras posibles

- Login real con usuarios institucionales
- Panel de administración para comercios
- Historial de validaciones
- Dominio personalizado
- Favicon institucional
- README con capturas de pantalla

## Notas

Este proyecto fue desarrollado como prototipo funcional para validación temporal de beneficios institucionales FICDE.

## Autoría

Proyecto desarrollado para FICDE.