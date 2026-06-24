from datetime import datetime, timedelta
import io

from flask import Flask, request, session, redirect, url_for, render_template_string, send_file, abort
import qrcode
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired

app = Flask(__name__)
app.secret_key = "CAMBIA_ESTA_CLAVE_SUPER_SECRETA"  # clave de Flask
token_secret = "CLAVE_SECRETA_TOKENS_FICDE"        # clave para tokens

# Configuración de tiempo de validez del QR (10 minutos)
QR_LIFETIME_SECONDS = 600

serializer = URLSafeTimedSerializer(token_secret)

# -----------------------------
# Simulación de login y membresía
# -----------------------------

def fake_current_user():
    """
    Simula un usuario logueado en el campus.
    En producción esto viene de tu sistema real (Flask-Login, JWT, etc.).
    """
    return session.get("user")

@app.route("/login-demo")
def login_demo():
    # Simula que el usuario entra al campus y queda logueado
    session["user"] = {
        "id": "FICDE-ARPY-0001",
        "country": request.args.get("country", "PY"),
        "is_member": True
    }
    return "Usuario demo logueado. Ahora entra a /mi-qr"

@app.route("/logout")
def logout():
    session.clear()
    return "Sesión cerrada. El QR ya no debe mostrarse."

# -----------------------------
# Generación del token seguro
# -----------------------------

def create_membership_token(user):
    """
    Crea un token firmado con datos mínimos: id interno y país.
    No incluye nombre ni datos personales.
    """
    data = {
        "member_id": user["id"],
        "country": user["country"]
    }
    token = serializer.dumps(data)  # firma y serializa
    return token

def verify_membership_token(token, max_age=QR_LIFETIME_SECONDS):
    """
    Verifica firma y expiración del token.
    max_age = segundos desde que se emitió.
    """
    try:
        data = serializer.loads(token, max_age=max_age)
        return data
    except SignatureExpired:
        # token válido pero vencido
        return None
    except BadSignature:
        # token manipulado o inválido
        return None

# -----------------------------
# Vista del alumno: muestra el QR
# -----------------------------

@app.route("/mi-qr")
def mi_qr():
    user = fake_current_user()
    if not user:
        return "Debes estar logueado en el campus FICDE para ver tu QR.", 401

    if not user.get("is_member"):
        return "No perteneces a la comunidad FICDE. No puedes generar el QR.", 403

    token = create_membership_token(user)
    validate_url = url_for("validar_qr", token=token, _external=True)

    # Plantilla mínima en línea (puedes pasarla a un .html)
    html = """
    <!doctype html>
    <html lang="es">
    <head>
        <meta charset="utf-8">
        <title>Mi QR FICDE</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body { font-family: sans-serif; text-align: center; padding: 20px;}
            .box { max-width: 420px; margin: 0 auto; padding:20px; border-radius:16px;
                   border:1px solid #ddd; background:#fafafa;}
            img { max-width: 100%; height: auto; }
            .msg { margin-top: 10px; color: #555; }
        </style>
    </head>
    <body>
        <div class="box">
            <h1>QR de membresía FICDE</h1>
            <p>Muéstrale este QR al comercio adherido para validar tu descuento.</p>
            <img src="{{ qr_url }}" alt="QR FICDE">
            <p class="msg">
                Este código es temporal (aprox. 10 minutos).<br>
                Si el comercio recibe mensaje de código vencido, vuelve a abrir esta página.
            </p>
        </div>
    </body>
    </html>
    """
    qr_image_url = url_for("qr_image", data=validate_url)
    return render_template_string(html, qr_url=qr_image_url)

# -----------------------------
# Generación de la imagen QR
# -----------------------------

@app.route("/qr-image")
def qr_image():
    data = request.args.get("data")
    if not data:
        abort(400, "Falta parámetro 'data'")

    # Genera imagen QR en memoria
    img = qrcode.make(data)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)

    return send_file(buf, mimetype="image/png")

# -----------------------------
# Vista del comerciante: validación
# -----------------------------

@app.route("/validar/<token>")
def validar_qr(token):
    data = verify_membership_token(token)
    now = datetime.now()

    if not data:
        # Token inválido o vencido
        html = """
        <!doctype html>
        <html lang="es">
        <head>
            <meta charset="utf-8">
            <title>Validación FICDE</title>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body { font-family:sans-serif; text-align:center; padding:20px; background:#fff4f4;}
                .box { max-width:460px; margin:0 auto; padding:20px; border-radius:16px;
                       border:2px solid #e6a8a8; background:#ffecec;}
                h1 { color:#b00020; }
                .small { color:#555; font-size:14px; margin-top:10px;}
            </style>
        </head>
        <body>
            <div class="box">
                <h1>Código rechazado</h1>
                <p>El código no es válido o ya venció.</p>
                <p>Solicite al alumno que abra nuevamente su QR dentro del campus FICDE.</p>
                <p class="small">Fecha y hora de verificación: {{ ts }}</p>
            </div>
        </body>
        </html>
        """
        return render_template_string(html, ts=now.strftime("%d/%m/%Y %H:%M:%S"))

    # Si el token es válido, asumimos que sigue siendo miembro activo.
    # (En producción podrías reconsultar base de datos con data["member_id"])
    html = """
    <!doctype html>
    <html lang="es">
    <head>
        <meta charset="utf-8">
        <title>Validación FICDE</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body { font-family:sans-serif; text-align:center; padding:20px; background:#f5fff8;}
            .box { max-width:460px; margin:0 auto; padding:20px; border-radius:16px;
                   border:2px solid #82c89a; background:#e9fff0;}
            h1 { color:#0a7c3c; }
            .small { color:#555; font-size:14px; margin-top:10px;}
        </style>
    </head>
    <body>
        <div class="box">
            <h1>Descuento aprobado</h1>
            <p>Esta persona es miembro de la comunidad FICDE.</p>
            <p>Descuento aprobado en comercios adheridos de Paraguay y Argentina.</p>
            <p class="small">
                País declarado del miembro: {{ country }}<br>
                Fecha y hora de verificación: {{ ts }}
            </p>
        </div>
    </body>
    </html>
    """
    return render_template_string(
        html,
        country=data.get("country", "N/D"),
        ts=now.strftime("%d/%m/%Y %H:%M:%S"),
    )

if __name__ == "__main__":
    app.run(debug=True)