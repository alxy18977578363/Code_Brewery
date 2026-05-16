from flask import Flask

from app.routes.overview_routes import overview_bp


def create_app():
    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static",
    )
    app.register_blueprint(overview_bp)
    return app
