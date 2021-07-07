
from api import api
from db import DBAPI

from flask import Flask

from os import getenv


def create_app():
    app = Flask(__name__)
    app.db = DBAPI(getenv("DATABASE_URI"))
    app.register_blueprint(api)

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
