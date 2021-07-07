import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from statistics import mean

from tests.test_base import TestBase


class DBQueryTest(TestBase):

    def test_get_avg_rates(self):
        """
        Test for fetching daily average rates between the given
        origin/destination port codes, and start_date/end_dates.
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

        daily_avg_rates = self.db.get_avg_rates(
            db_cursor,
            start_date="2021-01-01",
            end_date="2021-01-02",
            origin="CNSGH",
            destination="GBLON"
        )

        self.assertEqual(len(daily_avg_rates), 2)

        day_1, avg_rate_1 = daily_avg_rates[0]
        day_2, avg_rate_2 = daily_avg_rates[1]

        expected_avg_rate_1 = mean([rate["price"] for rate in test_rates[0:3]])
        expected_avg_rate_2 = mean([rate["price"] for rate in test_rates[3:6]])

        self.assertEqual(str(day_1), "2021-01-01")
        self.assertEqual(str(day_2), "2021-01-02")

        self.assertIsNotNone(avg_rate_1)
        self.assertIsNotNone(avg_rate_2)

        self.assertEqual(
            round(float(avg_rate_1), 3),
            round(float(expected_avg_rate_1), 3),
        )
        self.assertEqual(
            round(float(avg_rate_2), 3),
            round(float(expected_avg_rate_2), 3),
        )

    def test_get_avg_rates_null_avg(self):
        """
        Test for fetching daily average rates, given that a day has less than
        3 prices available, a null average value is returned for that day.
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
            {"day": "2021-01-02", "price": 4000.0, "orig_code": "CNSGH", "dest_code": "GBLON"},
        ]

        db_cursor = self.get_db_cursor()
        self.create_db_entries(db_cursor, table_name="regions", data_dicts=test_regions)
        self.create_db_entries(db_cursor, table_name="ports", data_dicts=test_ports)
        self.create_db_entries(db_cursor, table_name="prices", data_dicts=test_rates)

        daily_avg_rates = self.db.get_avg_rates(
            db_cursor,
            start_date="2021-01-01",
            end_date="2021-01-02",
            origin="CNSGH",
            destination="GBLON"
        )

        self.assertEqual(len(daily_avg_rates), 2)

        day_1, avg_rate_1 = daily_avg_rates[0]
        day_2, avg_rate_2 = daily_avg_rates[1]

        expected_avg_rate_1 = mean([rate["price"] for rate in test_rates[0:3]])
        expected_avg_rate_2 = None # Only one rate/price exists in day_2

        self.assertEqual(str(day_1), "2021-01-01")
        self.assertEqual(str(day_2), "2021-01-02")

        self.assertIsNotNone(avg_rate_1)
        self.assertIsNone(avg_rate_2)

        self.assertEqual(
            round(float(avg_rate_1), 3),
            round(float(expected_avg_rate_1), 3),
        )
        self.assertEqual(avg_rate_2, expected_avg_rate_2)

    def test_get_avg_rates_region_name_given(self):
        """
        Test for fetching daily average rates, when the given origin
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

        # Origin/destination regions cointains muliple different ports.
        daily_avg_rates = self.db.get_avg_rates(
            db_cursor,
            start_date="2021-01-01",
            end_date="2021-01-02",
            origin="china_east_main",
            destination="uk_sub"
        )

        self.assertEqual(len(daily_avg_rates), 2)

        day_1, avg_rate_1 = daily_avg_rates[0]
        day_2, avg_rate_2 = daily_avg_rates[1]

        expected_avg_rate_1 = mean([rate["price"] for rate in test_rates[0:3]])
        expected_avg_rate_2 = mean([rate["price"] for rate in test_rates[3:6]])

        self.assertEqual(str(day_1), "2021-01-01")
        self.assertEqual(str(day_2), "2021-01-02")

        self.assertIsNotNone(avg_rate_1)
        self.assertIsNotNone(avg_rate_2)

        self.assertEqual(
            round(float(avg_rate_1), 3),
            round(float(expected_avg_rate_1), 3),
        )
        self.assertEqual(
            round(float(avg_rate_2), 3),
            round(float(expected_avg_rate_2), 3),
        )

    def test_get_avg_rates_nested_region(self):
        """
        Test for fetching daily average rates, given that the
        origin/destination is a region rather than port code, and that region
        has nested sub-regions, all ports prices that belongs to that sub-
        regions should be included in the average.
        """
        test_regions = [
            {"slug": "northern_europe", "name": "Northern Europe", "parent_slug": None},
            {"slug": "baltic", "name": "Baltic", "parent_slug": "northern_europe"},
            {"slug": "finland_main", "name": "Finland Main", "parent_slug": "baltic"},
            {"slug": "poland_main", "name": "Poland Main", "parent_slug": "baltic"},
            {"slug": "china_east_main", "name": "China East Main", "parent_slug": None},
        ]
        test_ports = [
            {"code": "CNNBO", "name": "Ningbo", "parent_slug": "china_east_main"},
            {"code": "FIIMA", "name": "Imatra", "parent_slug": "baltic"},
            {"code": "FIRAU", "name": "Rauma", "parent_slug": "finland_main"},
            {"code": "PLGDY", "name": "Gdynia", "parent_slug": "poland_main"},
        ]
        test_rates =[
            {"day": "2021-01-01", "price": 1000.0, "orig_code": "CNNBO", "dest_code": "FIIMA"},
            {"day": "2021-01-01", "price": 3000.0, "orig_code": "CNNBO", "dest_code": "FIRAU"},
            {"day": "2021-01-01", "price": 2000.0, "orig_code": "CNNBO", "dest_code": "PLGDY"},
            {"day": "2021-01-02", "price": 3000.0, "orig_code": "CNNBO", "dest_code": "FIIMA"},
            {"day": "2021-01-02", "price": 4000.0, "orig_code": "CNNBO", "dest_code": "FIRAU"},
            {"day": "2021-01-02", "price": 5000.0, "orig_code": "CNNBO", "dest_code": "PLGDY"},
        ]

        db_cursor = self.get_db_cursor()
        self.create_db_entries(db_cursor, table_name="regions", data_dicts=test_regions)
        self.create_db_entries(db_cursor, table_name="ports", data_dicts=test_ports)
        self.create_db_entries(db_cursor, table_name="prices", data_dicts=test_rates)

        # Destination region cointains many sub-regions with their own ports.
        daily_avg_rates = self.db.get_avg_rates(
            db_cursor,
            start_date="2021-01-01",
            end_date="2021-01-02",
            origin="china_east_main",
            destination="northern_europe"
        )

        self.assertEqual(len(daily_avg_rates), 2)

        day_1, avg_rate_1 = daily_avg_rates[0]
        day_2, avg_rate_2 = daily_avg_rates[1]

        expected_avg_rate_1 = mean([rate["price"] for rate in test_rates[0:3]])
        expected_avg_rate_2 = mean([rate["price"] for rate in test_rates[3:6]])

        self.assertEqual(str(day_1), "2021-01-01")
        self.assertEqual(str(day_2), "2021-01-02")

        self.assertIsNotNone(avg_rate_1)
        self.assertIsNotNone(avg_rate_2)

        self.assertEqual(
            round(float(avg_rate_1), 3),
            round(float(expected_avg_rate_1), 3),
        )
        self.assertEqual(
            round(float(avg_rate_2), 3),
            round(float(expected_avg_rate_2), 3),
        )


if __name__ == "__main__":
    unittest.main()
