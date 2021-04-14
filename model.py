# use Python 3.7.3
import logging.config
from collections import namedtuple

from peewee import *

import settings
from log_settings import log_config

from playhouse.pool import PooledPostgresqlExtDatabase

logging.config.dictConfig(log_config)
log = logging.getLogger('peewee')

# import peewee
# psql_db = peewee.SqliteDatabase('weather.db')
psql_db = PooledPostgresqlExtDatabase(settings.DBNAME,
                                      user=settings.DBUSER,
                                      password=settings.DBPASS,
                                      host=settings.DBHOST,
                                      port=settings.DBPORT, max_connections=100, autoconnect=False, stale_timeout=300)

WeatherDayInfo = namedtuple('WeatherDayInfo', 'town,date, cloudiness,first_tempera,second_tempera,'
                                              'precipitation,town_name,picture_file_name',
                            defaults=('', '', '', '', '', ''))


class BaseModel(Model):
    class Meta:
        database = psql_db
        legacy_table_names = False


class Towns(BaseModel):
    """Модель таблицы города
    name - название
    latitude - широта
    longitude - долгота
    """
    name = CharField(unique=True)
    latitude = CharField(null=False)
    longitude = CharField(null=False)


class WeatherReport(BaseModel):
    """
    Модель таблицы с данными о погоде
    town              - город
    date              - дата
    first_tempera     - низшая темпиратура
    second_tempera    - высшая темпиратура
    precipitation     - осадки
    cloudiness        - состояние (ясно , облачно , дождь, снег)
    picture_file_name - имя файла с открыткой
    """
    town = ForeignKeyField(Towns)
    date = DateTimeField(null=False)
    first_tempera = CharField(null=False)
    second_tempera = CharField(null=False)
    precipitation = CharField()
    cloudiness = CharField()
    picture_file_name = CharField(default='')

    class Meta:
        primary_key = CompositeKey('date', 'town')


def psql_run_transaction(func):
    """
    Транзакция в БД
    Используем как декоратор к функциям
    """

    def run_func(*args, **kwargs):
        if psql_db.is_closed():
            psql_db.connect()
        psql_db.begin()
        result_value = func(*args, **kwargs)
        psql_db.commit()
        psql_db.close()
        return result_value

    return run_func


@psql_run_transaction
def db_prepare():
    """Создание таблиц"""
    models = [Towns, WeatherReport]
    psql_db.create_tables(models=models)


def delete_data():
    """Отчистка таблиц"""
    log.info('Clear database')
    psql_db.connect()
    psql_db.begin()
    WeatherReport.delete().execute()
    psql_db.commit()
    psql_db.begin()
    Towns.delete().execute()
    psql_db.commit()
    psql_db.close()


if __name__ == '__main__':
    db_prepare()
