from flask import (
    Blueprint,
    current_app as app,
    jsonify,
)
from validator import validate_rates_inputs


api = Blueprint("api", __name__)


@api.route("/rates", methods=["GET"])
@validate_rates_inputs
def get_rates(date_from, date_to, origin, destination):
    """
    API handler for fetching daily average price rates between origin
    and destination port/region.
    """
    db_conn = app.db.get_db_conn()
    db_cursor = db_conn.cursor()

    # TODO: Implement DB connection pool to reuse DB connections - avoid
    # establishing DB connection for every request.

    rates = app.db.get_avg_rates(
        db_cursor,
        date_from,
        date_to,
        origin,
        destination
    )
    db_conn.close()

    return jsonify(
        [
            {
                "day": day.strftime("%Y-%m-%d"),
                "average_price": (
                    round(float(avg_price), 3)
                    if avg_price is not None else None
                )
            }
            for day, avg_price in rates
        ]
    )
