# use Python 3.7.3
import unittest
from datetime import datetime
from unittest.mock import Mock
from weather import Manager, detect_date_format, DATE_FORMAT_POINT, DATE_FORMAT_MINUS, DATE_FORMAT_HEY, split_portion


class ManagerTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self.from_date = datetime(year=2020, month=10, day=1)
        self.to_date = datetime(year=2020, month=10, day=4)

        self.manager = Manager(city='Усть-Илимск',
                               from_date=self.from_date,
                               to_date=self.to_date,
                               local=True)

    def test_create(self):
        self.assertEqual(len(self.manager.weathers_info), 4)

    def test_run(self):
        self.manager.get_weather = Mock()
        self.manager.make_images = Mock()
        self.manager.run()
        self.manager.get_weather.assert_called_once()
        self.manager.make_images.assert_called_once()

    def test_detect_date_format(self):
        """Проверка ф-ции detect_date_format"""
        test_string = '01.01.2020'
        result_string = detect_date_format(test_string)
        self.assertEqual(result_string, DATE_FORMAT_POINT)
        test_string = '01-01-2020'
        result_string = detect_date_format(test_string)
        self.assertEqual(result_string, DATE_FORMAT_MINUS)
        test_string = '01/01/2020'
        result_string = detect_date_format(test_string)
        self.assertEqual(result_string, DATE_FORMAT_HEY)

    def test_split_portion(self):
        """Проверка ф-ции split_portion"""
        test_list = [i for i in range(0, 30)]
        result = split_portion(what=test_list, num=12)
        self.assertEqual(len(result), 3, 'Должно быть 3')
        self.assertEqual(result[0][0], 0, 'Должно быть 0')
        self.assertEqual(result[-1][-1], 29, 'Должно быть 29')

    def test_get_weather(self):
        self.manager.run_by_portion = Mock()
        self.manager.get_weather()
        self.manager.run_by_portion.assert_called_once()

    def test_make_images(self):
        self.manager.run_by_portion = Mock()
        self.assertEqual(len(self.manager.images_info), 0, 'Должно быть 0')
        self.manager.make_images()
        self.assertEqual(len(self.manager.images_info), len(self.manager.images_info), 'Должны быть равны')
        self.manager.run_by_portion.assert_called_once()


if __name__ == '__main__':
    unittest.main()
