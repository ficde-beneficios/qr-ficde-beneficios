# QR FICDE Beneficios

Sistema base en Flask para mostrar y validar un QR temporal de membresía FICDE.

## Funciones
- Login demo para prueba
- Generación de QR temporal
- Validación de membresía
- Pantalla de aprobado o rechazado

## Archivos principales
- `app.py`: aplicación Flask
- `templates/`: vistas HTML
- `static/`: estilos
- `requirements.txt`: dependencias
- `Procfile`: arranque en Render
- `render.yaml`: configuración del servicio

## Prueba local
```bash
pip install -r requirements.txt
python app.py
```

Abrir:
- `/login-demo`
- `/mi-qr`

## Deploy en Render
- Build Command: `pip install -r requirements.txt`
- Start Command: `gunicorn app:app`

## Variables de entorno
- `FLASK_SECRET_KEY`
- `TOKEN_SECRET`
- `QR_LIFETIME_SECONDS=600`
- `BASE_URL=https://TU-APP.onrender.com`