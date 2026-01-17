from flask import Flask
from app.extensions import login_manager, oauth


from app.models import db, Usuario, TipoTrabajo




def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    app.config["SECRET_KEY"] = "super-secret-key"

    # ===== EXTENSIONES =====
    db.init_app(app)
    login_manager.init_app(app)
    oauth.init_app(app)

    login_manager.login_view = "auth.login"

    # ===== GOOGLE OAUTH =====
    oauth.register(
        name="google",
        client_id=app.config["GOOGLE_CLIENT_ID"],
        client_secret=app.config["GOOGLE_CLIENT_SECRET"],
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_kwargs={
            "scope": "openid email profile"
        }
    )

    with app.app_context():
        db.create_all()

        # 🌱 Seed solo si está vacío
        if TipoTrabajo.query.first() is None:
            from app.seed import run_seed
            run_seed()

    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(int(user_id))

    # ===== BLUEPRINTS =====
    from app.routes.auth import auth
    from app.routes.main import main
    from app.routes.insumos import insumos
    from app.routes.tipos_trabajo import tipos_trabajo
    from app.routes.trabajos import trabajos
    from app.routes.movimientos import movimientos
    from app.routes.recomendaciones import recomendaciones

    app.register_blueprint(auth)
    app.register_blueprint(main)
    app.register_blueprint(insumos)
    app.register_blueprint(tipos_trabajo)
    app.register_blueprint(trabajos)
    app.register_blueprint(movimientos)
    app.register_blueprint(recomendaciones)

    return app
