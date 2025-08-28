"""Initialize Flask app."""
from flask import Flask

from .controllers.components_controller import components_controller
from .controllers.home_controller import home_controller
from .dependencies.model import load_model


def init_app() -> Flask:
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object("config.Config")
    app.nlp = load_model()  # type: ignore[attr-defined]

    with app.app_context():
        # Import parts of our core Flask app
        app.register_blueprint(home_controller, url_prefix="/")
        app.register_blueprint(components_controller)

        return app
