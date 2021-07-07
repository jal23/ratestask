
from ratestask.api import api
from ratestask.db import DBAPI

from flask import Flask

from os import getenv


def create_app(config=None):
    app = Flask(__name__)
    if config:
        app.config.from_mapping(config)

    app.db = DBAPI(app.config.get("DATABASE_URI"))
    app.register_blueprint(api)

    return app


app = create_app({
    "DATABASE_URI": getenv("DATABASE_URI"),
})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
