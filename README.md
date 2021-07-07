## Application Setup

## Setup using docker/docker-compose:
    $ docker-compose up

That's it. The app should be accessible via port 80, Postgres DB via port 5432.

    $ curl "http://127.0.0.1/rates?date_from=2016-01-01&date_to=2016-01-10&origin=CNSGH&destination=north_europe_main" | python -m json.tool

    [
        {
            "average_price": 1111.917,
            "day": "2016-01-01"
        },
        {
            "average_price": 1112.0,
            "day": "2016-01-02"
        },
        ...
    ]

## Setup without Docker
1. Create virtual environment (Skip if you prefer alternatives or want to install libraries globally):

        $ virtualenv venv
        $ source venv/bin/activate
2. Install Dependencies:

        $ pip install -r requirements.txt
3. Set Environmental variables:

        $ export PYTHONPATH=$PYTHONPATH:$(pwd)
    Assuming DB has already setup:

        $ export DATABASE_URI=postgresql://[DB_USER]:[DB_PASS]@[HOST]/[DB_NAME]
     Sample: `postgresql://postgres:ratestask@postgres/ratestask`
4. Run the app:

        python ratestask/app.py

## Running tests within Docker

    $ docker-compose -f docker-compose.test.yml run test

## Running tests without Docker
1. Create virtual environment:

        $ virtualenv venv
        $ source venv/bin/activate
2. Install Dependencies:

        $ pip install -r requirements.txt
3. Run tests:

        $ pytest tests/
