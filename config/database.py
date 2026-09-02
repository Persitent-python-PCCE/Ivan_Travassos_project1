
# config/database.py

import os
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def init_db(app):

    database_url = os.getenv(
        "MYSQL_DB_URL",
        "mysql+pymysql://root:root@mysql_app:3306/testdb"
    )

    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

