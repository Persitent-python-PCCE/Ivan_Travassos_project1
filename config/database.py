# config/database.py

import os
from urllib.parse import quote_plus
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


def init_db(app):
    # Keep an explicitly configured URI (used by tests); otherwise build the MySQL URI from .env.
    if app.config.get("SQLALCHEMY_DATABASE_URI"):
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
        db.init_app(app)
        return

    db_user = os.getenv("DB_USER", "root")
    db_password = os.getenv("DB_PASSWORD", "")
    db_host = os.getenv("DB_HOST", "localhost")
    db_name = os.getenv("DB_NAME", "hr_management")
    db_port = os.getenv("DB_PORT", "3306")

    password = quote_plus(db_password)
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"mysql+pymysql://{db_user}:{password}@{db_host}:{db_port}/{db_name}"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
