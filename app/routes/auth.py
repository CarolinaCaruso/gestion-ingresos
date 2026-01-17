from flask import Blueprint, redirect, render_template, url_for
from flask_login import login_user
from app.models import Usuario, db
from app.extensions import oauth


auth = Blueprint("auth", __name__, url_prefix="/auth")


@auth.route("/login")
def login():
    return render_template("login.html")


@auth.route("/login/google")
def login_google():
    redirect_uri = url_for("auth.google_callback", _external=True)
    return oauth.google.authorize_redirect(redirect_uri)



@auth.route("/login/google/callback")
def google_callback():
    token = oauth.google.authorize_access_token()
    user_info = token["userinfo"]

    email = user_info["email"]
    nombre = user_info.get("name", email)
    foto = user_info.get("picture")

    usuario = Usuario.query.filter_by(email=email).first()

    if not usuario:
        usuario = Usuario(
            email=email,
            nombre=nombre,
            foto_url=foto
        )
        db.session.add(usuario)
    else:
        usuario.foto_url = foto  # por si cambia

    db.session.commit()
    login_user(usuario)

    return redirect(url_for("main.index"))


from flask_login import logout_user, login_required

@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
