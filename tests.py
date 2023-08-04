import unittest
from datetime import datetime
from utils import convert_date_string_to_datetime, check_for_consecutive_dates


class TestDateTime(unittest.TestCase):
    def test_string_to_date(self):
        string = "2019-09-09"
        result = convert_date_string_to_datetime(string)
        self.assertEqual(result, datetime(2019, 9, 9))

    def test_consecutive_dates(self):
        date1 = datetime(2019, 9, 9)
        date2 = datetime(2019, 9, 10)
        date3 = datetime(2019, 9, 11)
        self.assertTrue(check_for_consecutive_dates(date1, date2))
        self.assertTrue(check_for_consecutive_dates(date2, date1))
        self.assertFalse(check_for_consecutive_dates(date1, date3))
        self.assertFalse(check_for_consecutive_dates(date3, date1))


if __name__ == '__main__':
    unittest.main()
