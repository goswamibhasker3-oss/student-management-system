from flask import Flask, redirect, url_for
from flask_login import LoginManager

from config import Config
import models
from models import User


class AppLoginManager(LoginManager):
    login_view: str | None


login_manager = AppLoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message = "Please log in to access this page."
login_manager.login_message_category = "warning"


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    models.mysql.init_app(app)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.get_by_id(int(user_id))

    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.students import students_bp
    from routes.courses import courses_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(students_bp, url_prefix="/students")
    app.register_blueprint(courses_bp, url_prefix="/courses")

    @app.route("/")
    def root():
        return redirect(url_for("dashboard.index"))

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)