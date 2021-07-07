from flask import (
    jsonify,
    request,
)
from datetime import datetime
from voluptuous import (
    Invalid,
    MultipleInvalid,
    Required,
    Schema,
)

DEFAULT_DATE_FMT = "%Y-%m-%d"

def validate_date(str_date):
    try:
        date_obj = datetime.strptime(str_date, DEFAULT_DATE_FMT)
        return date_obj.date()
    except ValueError:
        raise Invalid("Invalid date format: {}".format(str_date))


rates_input_schema = Schema({
    Required("date_from"): validate_date,
    Required("date_to"): validate_date,
    Required("origin"): str,
    Required("destination"): str,
})


def validate_rates_inputs(func):
    """
    Decorator for validating rates API payload.
    """
    def decorated(*args, **kwargs):
        try:
            input_args =  {
                key: val for key, val in request.args.items()
            }
            validated_args = rates_input_schema(input_args)
            kwargs.update(validated_args)

        except MultipleInvalid as e:
            errors = [str(error) for error in e.errors]
            return jsonify(
                message="Bad Request",
                args=input_args,
                errors=errors
            ), 400

        return func(*args, **kwargs)

    return decorated
