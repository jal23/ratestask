import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from statistics import mean

from tests.test_base import TestBase
from ratestask.app import create_app
import json


class APITest(TestBase):

    def setUp(self):
        super(APITest, self).setUp()
        self.app = create_app({
            "DATABASE_URI": os.getenv("DATABASE_URI"),
            "TESTING": True,
        })

    def test_get_avg_rates(self):
        """
        Test API for successfully fetching daily average rates between the given
        origin/destination port codes, and date_from/date_to.
        """
        db_cursor = self.get_db_cursor()
        test_regions = [
            {"slug": "china_east_main", "name": "China East Main", "parent_slug": None},
            {"slug": "uk_sub", "name": "UK Sub", "parent_slug": None},
        ]
        test_ports = [
            {"code": "CNSGH", "name": "Shanghai", "parent_slug": "china_east_main"},
            {"code": "GBLON", "name": "London", "parent_slug": "uk_sub"},
        ]
        test_rates =[
            {"day": "2021-01-01", "price": 1000.0, "orig_code": "CNSGH", "dest_code": "GBLON"},
            {"day": "2021-01-01", "price": 3000.0, "orig_code": "CNSGH", "dest_code": "GBLON"},
            {"day": "2021-01-01", "price": 2000.0, "orig_code": "CNSGH", "dest_code": "GBLON"},
            {"day": "2021-01-02", "price": 3000.0, "orig_code": "CNSGH", "dest_code": "GBLON"},
            {"day": "2021-01-02", "price": 4000.0, "orig_code": "CNSGH", "dest_code": "GBLON"},
            {"day": "2021-01-02", "price": 5000.0, "orig_code": "CNSGH", "dest_code": "GBLON"},
        ]
        db_cursor = self.get_db_cursor()
        self.create_db_entries(db_cursor, table_name="regions", data_dicts=test_regions)
        self.create_db_entries(db_cursor, table_name="ports", data_dicts=test_ports)
        self.create_db_entries(db_cursor, table_name="prices", data_dicts=test_rates)

        with self.app.test_client() as client:
            args = {
                "date_from": "2021-01-01",
                "date_to": "2021-01-02",
                "origin": "CNSGH",
                "destination": "GBLON",
            }
            resp = client.get("/rates", query_string=args)
            self.assertEqual(resp.status_code, 200)

            daily_avg_rates = json.loads(resp.data)
            self.assertEqual(len(daily_avg_rates), 2)

            avg_rate_1 = daily_avg_rates[0]
            avg_rate_2 = daily_avg_rates[1]

            expected_avg_rate_1 = mean([rate["price"] for rate in test_rates[0:3]])
            expected_avg_rate_2 = mean([rate["price"] for rate in test_rates[3:6]])

            self.assertEqual(avg_rate_1.get("day"), "2021-01-01")
            self.assertEqual(avg_rate_2.get("day"), "2021-01-02")

            self.assertIsNotNone(avg_rate_1.get("average_price"))
            self.assertIsNotNone(avg_rate_2.get("average_price"))

            self.assertEqual(
                round(float(avg_rate_1.get("average_price")), 3),
                round(float(expected_avg_rate_1), 3),
            )
            self.assertEqual(
                round(float(avg_rate_2.get("average_price")), 3),
                round(float(expected_avg_rate_2), 3),
            )

    def test_get_avg_rates_missing_payload(self):
        """
        Test API for fetching rates, given that required paylaod(s) aren't
        supplied, a 400 Bad Request response is returned.
        """
        with self.app.test_client() as client:
            args = {
                # Missing 'date_from' field.
                "date_to": "2021-01-02",
                "origin": "CNSGH",
                "destination": "GBLON",
            }
            resp = client.get("/rates", query_string=args)
            self.assertEqual(resp.status_code, 400)

            args = {
                # Missing 'date_to' field.
                "date_from": "2021-01-01",
                "date_to": "2021-01-02",
                "destination": "GBLON",
            }
            resp = client.get("/rates", query_string=args)
            self.assertEqual(resp.status_code, 400)

            args = {
                # Missing 'origin' field.
                "date_from": "2021-01-01",
                "date_to": "2021-01-02",
                "destination": "GBLON",
            }
            resp = client.get("/rates", query_string=args)
            self.assertEqual(resp.status_code, 400)

            args = {
                # Missing 'destination' field.
                "date_from": "2021-01-01",
                "date_to": "2021-01-02",
                "origin": "CNSGH",
            }
            resp = client.get("/rates", query_string=args)
            self.assertEqual(resp.status_code, 400)

    def test_get_avg_rates_invalid_date(self):
        """
        Test API for fetching rates, when the supplied date format invalid
        or not in YYYY-MM-DD form, a 400 Bad Request response is returned.
        """
        with self.app.test_client() as client:
            args = {
                "date_from": "01/01/2021",
                "date_to": "2021-01-02",
                "origin": "CNSGH",
                "destination": "GBLON",
            }
            resp = client.get("/rates", query_string=args)
            self.assertEqual(resp.status_code, 400)

            args = {
                "date_from": "2021-01-01",
                "date_to": "01/02/2021",
                "origin": "CNSGH",
                "destination": "GBLON",
            }
            resp = client.get("/rates", query_string=args)
            self.assertEqual(resp.status_code, 400)

    def test_get_avg_rates_null_avg(self):
        """
        Test API for fetching rates, given that a particular day within the
        given date range has less than 3 prices available, a NULL
        average value should returned for that day.
        """
        test_regions = [
            {"slug": "china_east_main", "name": "China East Main", "parent_slug": None},
            {"slug": "uk_sub", "name": "UK Sub", "parent_slug": None},
        ]
        test_ports = [
            {"code": "CNSGH", "name": "Shanghai", "parent_slug": "china_east_main"},
            {"code": "GBLON", "name": "London", "parent_slug": "uk_sub"},
        ]
        test_rates =[
            {"day": "2021-01-01", "price": 1000.0, "orig_code": "CNSGH", "dest_code": "GBLON"},
            {"day": "2021-01-01", "price": 2000.0, "orig_code": "CNSGH", "dest_code": "GBLON"},
            {"day": "2021-01-01", "price": 3000.0, "orig_code": "CNSGH", "dest_code": "GBLON"},
            # Only 1 price for day 2021-01-02
            {"day": "2021-01-02", "price": 4000.0, "orig_code": "CNSGH", "dest_code": "GBLON"},
        ]

        db_cursor = self.get_db_cursor()
        self.create_db_entries(db_cursor, table_name="regions", data_dicts=test_regions)
        self.create_db_entries(db_cursor, table_name="ports", data_dicts=test_ports)
        self.create_db_entries(db_cursor, table_name="prices", data_dicts=test_rates)

        with self.app.test_client() as client:
            args = {
                "date_from": "2021-01-01",
                "date_to": "2021-01-02",
                "origin": "CNSGH",
                "destination": "GBLON",
            }
            resp = client.get("/rates", query_string=args)
            self.assertEqual(resp.status_code, 200)

            daily_avg_rates = json.loads(resp.data)
            self.assertEqual(len(daily_avg_rates), 2)

            avg_rate_1 = daily_avg_rates[0]
            avg_rate_2 = daily_avg_rates[1]

            expected_avg_rate_1 = mean([rate["price"] for rate in test_rates[0:3]])
            expected_avg_rate_2 = None

            self.assertEqual(avg_rate_1.get("day"), "2021-01-01")
            self.assertEqual(avg_rate_2.get("day"), "2021-01-02")

            self.assertIsNotNone(avg_rate_1.get("average_price"))
            self.assertIsNone(avg_rate_2.get("average_price"))

            self.assertEqual(
                round(float(avg_rate_1.get("average_price")), 3),
                round(float(expected_avg_rate_1), 3),
            )
            self.assertEqual(
                avg_rate_2.get("average_price"),
                expected_avg_rate_2
            )

    def test_get_avg_rates_region_name_given(self):
        """
        Test API for fetching daily average rates, when the given origin
        and/or destination is a region rather than port code, all ports prices
        within that region should be included in the average.
        """
        test_regions = [
            {"slug": "china_east_main", "name": "China East Main", "parent_slug": None},
            {"slug": "uk_sub", "name": "UK Sub", "parent_slug": None},
        ]
        test_ports = [
            {"code": "CNSGH", "name": "Shanghai", "parent_slug": "china_east_main"},
            {"code": "CNNBO", "name": "Ningbo", "parent_slug": "china_east_main"},
            {"code": "GBLON", "name": "London", "parent_slug": "uk_sub"},
            {"code": "GBMNC", "name": "Manchester", "parent_slug": "uk_sub"},
        ]
        test_rates =[
            {"day": "2021-01-01", "price": 1000.0, "orig_code": "CNSGH", "dest_code": "GBLON"},
            {"day": "2021-01-01", "price": 3000.0, "orig_code": "CNNBO", "dest_code": "GBMNC"},
            {"day": "2021-01-01", "price": 2000.0, "orig_code": "CNSGH", "dest_code": "GBLON"},
            {"day": "2021-01-02", "price": 3000.0, "orig_code": "CNNBO", "dest_code": "GBMNC"},
            {"day": "2021-01-02", "price": 4000.0, "orig_code": "CNSGH", "dest_code": "GBLON"},
            {"day": "2021-01-02", "price": 5000.0, "orig_code": "CNNBO", "dest_code": "GBLON"},
        ]

        db_cursor = self.get_db_cursor()
        self.create_db_entries(db_cursor, table_name="regions", data_dicts=test_regions)
        self.create_db_entries(db_cursor, table_name="ports", data_dicts=test_ports)
        self.create_db_entries(db_cursor, table_name="prices", data_dicts=test_rates)

        with self.app.test_client() as client:
            args = {
                "date_from": "2021-01-01",
                "date_to": "2021-01-02",
                "origin": "china_east_main",
                "destination": "uk_sub",
            }
            resp = client.get("/rates", query_string=args)
            self.assertEqual(resp.status_code, 200)

            daily_avg_rates = json.loads(resp.data)
            self.assertEqual(len(daily_avg_rates), 2)

            avg_rate_1 = daily_avg_rates[0]
            avg_rate_2 = daily_avg_rates[1]

            expected_avg_rate_1 = mean([rate["price"] for rate in test_rates[0:3]])
            expected_avg_rate_2 = mean([rate["price"] for rate in test_rates[3:6]])

            self.assertEqual(avg_rate_1.get("day"), "2021-01-01")
            self.assertEqual(avg_rate_2.get("day"), "2021-01-02")

            self.assertIsNotNone(avg_rate_1.get("average_price"))
            self.assertIsNotNone(avg_rate_2.get("average_price"))

            self.assertEqual(
                round(float(avg_rate_1.get("average_price")), 3),
                round(float(expected_avg_rate_1), 3),
            )
            self.assertEqual(
                round(float(avg_rate_2.get("average_price")), 3),
                round(float(expected_avg_rate_2), 3),
            )

if __name__ == "__main__":
    unittest.main()
