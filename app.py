import io
import os
from datetime import datetime

import qrcode
from flask import Flask, abort, render_template, request, send_file, session, url_for
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

app = Flask(__name__)

app.secret_key = os.getenv("FLASK_SECRET_KEY", "cambiar-esta-clave-flask")
TOKEN_SECRET = os.getenv("TOKEN_SECRET", "cambiar-esta-clave-token")
BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:5000").rstrip("/")
QR_LIFETIME_SECONDS = int(os.getenv("QR_LIFETIME_SECONDS", "600"))

serializer = URLSafeTimedSerializer(TOKEN_SECRET)


def fake_current_user():
    return session.get("user")


@app.route("/")
def home():
    return render_template("home.html", base_url=BASE_URL)


@app.route("/login-demo")
def login_demo():
    session["user"] = {
        "id": request.args.get("member_id", "FICDE-ARPY-0001"),
        "country": request.args.get("country", "PY"),
        "is_member": True,
    }
    return render_template("login_ok.html", user=session["user"])


@app.route("/logout")
def logout():
    session.clear()
    return render_template("logout.html")


def create_membership_token(user):
    data = {
        "member_id": user["id"],
        "country": user["country"],
        "is_member": user.get("is_member", False),
    }
    return serializer.dumps(data)


def verify_membership_token(token, max_age=QR_LIFETIME_SECONDS):
    try:
        return serializer.loads(token, max_age=max_age)
    except (SignatureExpired, BadSignature):
        return None


@app.route("/mi-qr")
def mi_qr():
    user = fake_current_user()
    if not user:
        return render_template(
            "error.html",
            title="Acceso restringido",
            message="Debes iniciar sesión en el campus FICDE para ver tu QR.",
        ), 401

    if not user.get("is_member"):
        return render_template(
            "error.html",
            title="No autorizado",
            message="Tu cuenta no pertenece a la comunidad FICDE.",
        ), 403

    token = create_membership_token(user)
    validate_url = f"{BASE_URL}/validar/{token}"
    qr_image_url = url_for("qr_image", data=validate_url)

    return render_template(
        "mi_qr.html",
        qr_url=qr_image_url,
        validate_url=validate_url,
        lifetime_minutes=QR_LIFETIME_SECONDS // 60,
    )


@app.route("/qr-image")
def qr_image():
    data = request.args.get("data")
    if not data:
        abort(400, "Falta parámetro data")

    img = qrcode.make(data)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return send_file(buf, mimetype="image/png")


@app.route("/validar/<token>")
def validar_qr(token):
    data = verify_membership_token(token)
    ts = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    if not data:
        return render_template(
            "validacion.html",
            ok=False,
            ts=ts,
            country=None,
            message="El código no es válido o ya venció. Solicite al alumno que abra nuevamente su QR dentro del campus FICDE.",
        )

    if not data.get("is_member"):
        return render_template(
            "validacion.html",
            ok=False,
            ts=ts,
            country=data.get("country"),
            message="La cuenta ya no pertenece a la comunidad FICDE.",
        )

    return render_template(
        "validacion.html",
        ok=True,
        ts=ts,
        country=data.get("country", "N/D"),
        message="Esta persona es miembro de la comunidad FICDE. Descuento aprobado.",
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)