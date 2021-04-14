import unittest
from datetime import datetime
from unittest.mock import patch
from peewee import *
from peewee import SqliteDatabase

from model import Towns, WeatherReport, delete_data, db_prepare

memory_db = SqliteDatabase(':memory:')



MODELS = [Towns, WeatherReport]


class ModelTestCase(unittest.TestCase):

    def setUp(self) -> None:
        patch(target='model.psql_db', new=memory_db)
        memory_db.bind(MODELS, bind_refs=False, bind_backrefs=False)
        memory_db.connect()
        memory_db.create_tables(MODELS)
        self.date = datetime(year=2020, month=10, day=1)

    def test_towns_not_found(self):
        with self.assertRaises(DoesNotExist,msg='Not Raise') as exc:
            res1 = Towns.get_by_id('2')

    def test_table_data_create_delete(self):
        town = Towns.create(name='test', latitude='51.9728565', longitude='113.4097271')
        cursor = memory_db.execute_sql("select count('id') from towns")
        result = cursor.fetchall()
        spam = result[0]
        count = spam[0]

        self.assertEqual(count,1,'Должна быть 1')
        weather = WeatherReport.create(town = 1,
                                       date = self.date,
                                       first_tempera = '-7 at 7am',
                                       second_tempera = '7 at 16 pm',
                                       precipitation = '4 mm',
                                       cloudiness = 'Rain starting',
                                       picture_file_name ='52_033409-113_500893-01.10.2020.png')
        weather.save()
        cursor1 = memory_db.execute_sql("select count('*') from weather_report")
        w_res = cursor1.fetchall()
        self.assertEqual(w_res[0][0], 1, 'Должна быть 1')
        delete_data()
        cursor1 = memory_db.execute_sql("select count('*') from weather_report")
        cursor = memory_db.execute_sql("select count('id') from towns")
        w_res = cursor1.fetchall()
        t_res = cursor.fetchall()
        self.assertEqual(w_res[0][0], 0, 'Должна быть 0')
        self.assertEqual(t_res[0][0], 0, 'Должна быть 0')

    def test_db_prepare(self):
        if memory_db.is_closed():
            memory_db.connect()
        memory_db.drop_tables(MODELS)
        db_prepare()
        cursor1 = memory_db.execute_sql("select count('*') from weather_report")
        cursor = memory_db.execute_sql("select count('id') from towns")
        w_res = cursor1.fetchall()
        t_res = cursor.fetchall()
        self.assertEqual(w_res[0][0], 0, 'Должна быть 0')
        self.assertEqual(t_res[0][0], 0, 'Должна быть 0')

    def tearDown(self) -> None:
        memory_db.drop_tables(MODELS)
        memory_db.close()


if __name__ == '__main__':
    unittest.main()
    #E:/work/prog/sckillbox/python_base/lesson_016/tests/model_tests.py
