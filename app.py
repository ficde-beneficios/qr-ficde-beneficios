import os
import io
import time
import base64
import hashlib
import hmac

from flask import Flask, render_template, session, redirect, url_for, request
import qrcode

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret-change-this")

TOKEN_SECRET = os.getenv("TOKEN_SECRET", "token-secret-change-this")
QR_LIFETIME_SECONDS = int(os.getenv("QR_LIFETIME_SECONDS", "600"))
BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:5000").rstrip("/")


def sign_payload(payload: str) -> str:
    return hmac.new(
        TOKEN_SECRET.encode("utf-8"),
        payload.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()


def build_token(user_id: str, country: str) -> str:
    ts = int(time.time())
    payload = f"{user_id}|{country}|{ts}"
    signature = sign_payload(payload)
    return f"{payload}|{signature}"


def parse_and_validate_token(token: str):
    try:
        parts = token.split("|")
        if len(parts) != 4:
            return False, "Formato de código inválido.", None

        user_id, country, ts_str, signature = parts
        payload = f"{user_id}|{country}|{ts_str}"
        expected_signature = sign_payload(payload)

        if not hmac.compare_digest(signature, expected_signature):
            return False, "La firma del código no es válida.", None

        ts = int(ts_str)
        now = int(time.time())

        if now - ts > QR_LIFETIME_SECONDS:
            return False, "El código venció. Solicite al miembro que genere un nuevo QR.", country

        return True, "Código válido para beneficios FICDE.", country

    except Exception:
        return False, "No se pudo validar el código.", None


def generate_qr_base64(data: str) -> str:
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{encoded}"


@app.route("/")
def home():
    return mi_qr()


@app.route("/ingresar")
@app.route("/login-demo")
def login_demo():
    session["user"] = {
        "id": "FICDE-001",
        "country": "Paraguay",
        "is_member": True
    }
    return render_template("login_ok.html", user=session["user"])


@app.route("/logout")
def logout():
    session.clear()
    return render_template("logout.html")


@app.route("/mi-qr")
def mi_qr():
    user = session.get("user")

    if not user:
        return render_template(
            "error.html",
            title="Acceso requerido",
            message="Debes ingresar primero para generar tu código QR."
        ), 401

    if not user.get("is_member"):
        return render_template(
            "error.html",
            title="Acceso no autorizado",
            message="El usuario actual no posee membresía habilitada."
        ), 403

    token = build_token(user["id"], user["country"])
    validate_url = f"{BASE_URL}/validar/{token}"
    qr_url = generate_qr_base64(validate_url)

    return render_template(
    "mi_qr.html",
    qr_url=qr_image_url,
    lifetime_minutes=QR_LIFETIME_SECONDS // 60,
    refresh_url=url_for("mi_qr"),
)


@app.route("/validar/<path:token>")
def validar(token):
    ok, message, country = parse_and_validate_token(token)
    ts = time.strftime("%d/%m/%Y %H:%M:%S")

    return render_template(
        "validacion.html",
        ok=ok,
        message=message,
        ts=ts,
        country=country
    )


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=True)