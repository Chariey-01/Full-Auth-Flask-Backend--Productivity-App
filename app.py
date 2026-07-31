from flask import Flask

from config import Config
from extensions import db, migrate, bcrypt, jwt
import models  #  (needed so Flask-Migrate can see the models)


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    jwt.init_app(app)

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
