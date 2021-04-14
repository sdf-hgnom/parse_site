# use Python 3.7.3
import os
import re
import time
from datetime import datetime, timedelta
from typing import Text, Tuple, List, Union

import numpy as np
import bs4
import requests
import peewee
import cv2 as cv
import matplotlib as mpl

from model import Towns, WeatherReport, WeatherDayInfo, psql_run_transaction
import logging.config
from log_settings import log_config
from geopy.geocoders import Nominatim
import threading
from multiprocessing import Process, cpu_count
import copy

logging.config.dictConfig(log_config)
log = logging.getLogger('weather')

DATE_FORMAT_MINUS = '%d-%m-%Y'
DATE_FORMAT_POINT = '%d.%m.%Y'
DATE_FORMAT_HEY = '%d/%m/%Y'


class ExceptionWeatherError(ValueError):
    pass


class WeatherOneDay(threading.Thread):
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) " \
                 "Chrome/84.0.4147.135 YaBrowser/20.8.3.115 Yowser/2.5 Safari/537.36"
    URL_DATE_FORMAT = '%Y-%m-%d'
    URL_WEATHER_FROM = 'https://darksky.net/details/'
    HEADER = {
        "Accept-Encoding": "gzip,deflate",
    }

    def __init__(self, city: Text, date: datetime, local: bool):
        """
        Инициализация
        :param city: город
        :param date: дата
        :param local: режим
        """
        threading.Thread.__init__(self)
        self.city: Text = city
        self.date: datetime = date
        self.local: bool = local
        self.town_id: Union[int, None] = None
        self.result: Union[WeatherReport, None] = None
        self.towns_table: Towns = Towns()
        self.weather_table = WeatherReport()
        self._get_town_id()

    def __str__(self):
        return f'Get weather in {self.city} for {self.date}'

    def __repr__(self):
        return f'{self.__class__.__name__}(city={self.city},date={self.date})'

    def _ident_file_name(self, latitude, longitude) -> Text:
        """
        Генирация имени файла скартинкой
        :param latitude: широта города
        :param longitude: долгота города
        :return: имя файла сохранения
        """
        latitude = latitude.replace('.', '_')
        longitude = longitude.replace('.', '_')
        res = f'{latitude}-{longitude}-{self.date.strftime(DATE_FORMAT_POINT)}.png'
        return res

    @staticmethod
    def _from_fahrenheit_to_village(input_str) -> int:
        """
        Перевести градусы по Фарингейту в градусы по Цельсию
        :param input_str: градус по Фарингейту
        :return: градус по Цельсию
        """
        input_fahrenheit = int(input_str)
        celiac = (input_fahrenheit - 32) / 1.8
        return round(celiac)

    def _get_town_id(self):
        """Опредилить id города в Б/Д"""
        try:
            town_id = self.get_town_id_db(town=self.city)
        except peewee.DoesNotExist:
            _, _, town_id = self.get_coordinates(town=self.city)
        self.town_id = town_id

    @psql_run_transaction
    def get_town_id_db(self, town: Text) -> int:
        """
        Взять id города из Б/Д
        :param town: город
        :return: id
        """
        town_id = self.towns_table.get(Towns.name == town)
        return town_id

    @psql_run_transaction
    def save_town_db(self, town: Text, longitude, latitude) -> int:
        """
        Сохранить инфу по городу в Б/Д
        :param town: город
        :param longitude: долгота
        :param latitude: широта
        :return: id города
        """
        town_id = Towns.create(name=town, longitude=longitude, latitude=latitude)
        return town_id

    @psql_run_transaction
    def get_coordinates_db(self, town_id: int) -> Tuple[Text, Text]:
        """
        Взять координаты города из Б/Д по id
        :param town_id: id города
        :return: координаты
        """
        return self.towns_table.get_by_id(town_id).latitude, self.towns_table.get_by_id(town_id).longitude

    def _get_coordinates_inet(self, town: Text) -> Tuple[Text, Text]:
        """
        Опредилить координаты места по Интернет-опредтлителю
        :param town: место
        :return: координаты
        """
        locator = Nominatim(user_agent=self.USER_AGENT)
        location = locator.geocode(town)
        if location:
            return location.latitude, location.longitude
        else:
            log.error(f'No town detect {town}')
            raise ExceptionWeatherError('No Town in World')

    def get_coordinates(self, town: Text) -> Tuple[Text, Text, int]:
        """
        Вернет геогафическую долготу и ширину города
        :param town:
        :return: долгота, ширина
        """
        town_id = None
        get_inet = False
        try:

            town_id = self.get_town_id_db(town)
        except peewee.DoesNotExist:
            log.info(f'Получаем координаты города {town} из Интернета')
            get_inet = True
        if get_inet:
            if self.local:
                log.error(f'Запрошен локальный режим но в базе нет информации для города {self.city}')
                raise ExceptionWeatherError(f'В базе нет информациии о городе {self.city} [local mode]')
            latitude, longitude = self._get_coordinates_inet(town)
            town_id = self.save_town_db(town, longitude, latitude)
        else:
            latitude, longitude = self.get_coordinates_db(town_id)

        return latitude, longitude, town_id

    def _get_weather_inet(self) -> WeatherDayInfo:
        """Парсинг инфы из Инет"""
        log.info(f'Получаем погоду для города {self.city} и числа {self.date} из Интернета')
        latitude, longitude, town_id = self.get_coordinates(town=self.city)
        image_file_name = self._ident_file_name(latitude, longitude)
        date_in_request = self.date.strftime(self.URL_DATE_FORMAT)
        request_url = f'{self.URL_WEATHER_FROM}{latitude},{longitude}/{date_in_request}'
        response = requests.get(request_url, headers=self.HEADER)
        if response.status_code != 200:
            log.error(f'Inet request return (get weather info) {response.status_code}')
            raise ExceptionWeatherError(f'request abort : {response.status_code}')
        html_doc = bs4.BeautifulSoup(response.text, features='html.parser')
        day_detail = html_doc.find('div', {'class': 'dayDetails'})
        day_detail_summary = day_detail.contents[3]
        result = str(day_detail_summary)
        cloudiness = result[16:-4].strip()
        if not cloudiness:
            cloudiness = 'Clear throughout the day'
        span_first = html_doc.find('span', {'class': 'highTemp'})
        spam = ''
        second_tempera = ''
        first_tempera = ''
        for index, item in enumerate(span_first.children):

            if index == 1:
                spam = self._from_fahrenheit_to_village(item.text[:-1])
            if index == 3:
                first_tempera = f'{spam} в {item.text}'
        span_second = html_doc.find('span', {'class': 'lowTemp'})
        for index, item in enumerate(span_second.children):

            if index == 1:
                spam = self._from_fahrenheit_to_village(item.text[:-1])
            if index == 3:
                second_tempera = f'{spam} в {item.text}'
        precipitation = html_doc.find('div', {'class': 'precipAccum swap'})
        spam = str(precipitation.contents[1])
        precipitation_name = spam[25:-7]
        spam = str(precipitation.contents[3].contents[1])
        precipitation_count = spam[25:-7]
        precipitation_decr = f'{precipitation_name} {precipitation_count} mm'

        out = WeatherDayInfo(town=town_id,
                             date=self.date,
                             town_name=self.city,
                             first_tempera=first_tempera,
                             second_tempera=second_tempera,
                             cloudiness=cloudiness,
                             precipitation=precipitation_decr,
                             picture_file_name=image_file_name
                             )
        return out

    @psql_run_transaction
    def _get_weather_from_table(self):
        return self.weather_table.get_or_none(WeatherReport.town == self.town_id and WeatherReport.date == self.date)

    @staticmethod
    @psql_run_transaction
    def save_weather_db(what: WeatherDayInfo):
        try:
            WeatherReport.get_or_create(town=what.town,
                                        date=what.date,
                                        first_tempera=what.first_tempera,
                                        second_tempera=what.second_tempera,
                                        precipitation=what.precipitation,
                                        cloudiness=what.cloudiness,
                                        picture_file_name=what.picture_file_name
                                        )
        except peewee.IntegrityError:
            query = WeatherReport.update(first_tempera=what.first_tempera,
                                         second_tempera=what.second_tempera,
                                         precipitation=what.precipitation,
                                         cloudiness=what.cloudiness,
                                         picture_file_name=what.picture_file_name).where(
                (WeatherReport.town == what.town)
                and (WeatherReport.date == what.date))
            query.execute()

    def get_weather_db(self):
        weather = self._get_weather_from_table()
        if weather is None:
            return None

        else:
            result = WeatherDayInfo(town=self.town_id,
                                    date=self.date,
                                    town_name=self.city,
                                    first_tempera=weather.first_tempera,
                                    second_tempera=weather.second_tempera,
                                    cloudiness=weather.cloudiness,
                                    precipitation=weather.precipitation,
                                    picture_file_name=weather.picture_file_name
                                    )
            return result

    def run(self):
        result = self.get_weather_db()
        if result is None:
            if not self.local:
                result = self._get_weather_inet()
                self.save_weather_db(what=result)
            else:
                log.error(f'В базе нет информации для города {self.city} за число {self.date} [режим local]')
                raise ExceptionWeatherError(f'В базе нет информации для города {self.city} '
                                            f'за число {self.date} [режим local]')
        self.result = result


class ImageMaker(Process):
    """Работа с изображениями"""
    FILE_SUN = 'images/sun.jpg'
    FILE_SNOW = 'images/snow.jpg'
    FILE_COULD = 'images/cloud.jpg'
    FILE_RAIN = 'images/rain.jpg'
    COLORS_CLEAR = ('yellow', 'white')
    COLORS_RAIN = ('blue', 'white')
    COLORS_COULD = ('grey', 'white')
    COLORS_SNOW = ('#42aaff', 'white')
    IMAGE_HEIGHT = 512
    IMAGE_WIDTH = 256
    TIME_FORMAT = '%d.%m.%Y'
    IMAGE_SAVE_FOLDER = 'result_images'

    def __init__(self, info: WeatherDayInfo):
        """
        Инициализация
        :param info: информация о погоде
        """
        Process.__init__(self)
        self.info: WeatherDayInfo = info
        self.image: Union[np.ndarray, None] = None

    def __repr__(self):
        return f'{self.__class__.__name__} with {self.info}'

    def _create_blanc(self):
        """Создаем пустое изображение"""
        ret = np.zeros((self.IMAGE_WIDTH, self.IMAGE_HEIGHT, 3), np.uint8)
        return ret

    @staticmethod
    def _color_fader(color_from: Text, color_to: Text, count: int) -> List:
        """
        Определение цветов для градиента
        :param color_from: начальный цвет
        :param color_to: конечный цвет
        :param count: сколько в промежктке
        :return: список цветов
        """
        ret = []
        color_from = np.array(mpl.colors.to_rgb(color_from))
        color_to = np.array(mpl.colors.to_rgb(color_to))
        for i in range(1, count, 1):
            mix = i / count
            ret.append(mpl.colors.to_hex((1 - mix) * color_from + mix * color_to))

        return ret

    def fill_gradient(self, start_color, end_color):
        """
        Заливка градиентом
        :param start_color: начальный цвет
        :param end_color: конечный цвет
        :return:
        """
        height, width, _ = self.image.shape
        colors = self._color_fader(start_color, end_color, height)

        for y in range(0, height - 1, 1):
            r, g, b = mpl.colors.to_rgb(colors[y])
            self.image = cv.line(self.image, (0, y), (width, y), (b * 255, g * 255, r * 255), lineType=cv.LINE_AA)

    def insert_label_image(self, what):
        """
        Вставить изображение-иконку
        :param what: изображение
        :return:
        """
        image_insert = cv.imread(what)
        could_resized = cv.resize(image_insert, dsize=(50, 50))
        self.image[10:10 + could_resized.shape[0], 450:450 + could_resized.shape[1]] = could_resized

    @staticmethod
    def view_image(src: np.ndarray, win_title: Text = 'Image'):
        """
        Просмотр изображения
        :param src: изображение
        :param win_title: текст заголовка
        :return:
        """
        title = f'{win_title}  {src.shape[0]} x {src.shape[1]} '
        cv.namedWindow(title)
        cv.imshow(title, src)
        cv.waitKey(0)
        cv.destroyWindow(title)

    def add_text(self):
        """Добавить текст на изображение"""
        display_date = self.info.date.strftime(self.TIME_FORMAT)
        chars = list(self.info.cloudiness)
        for index, char in enumerate(chars):
            if not char.isalpha():
                chars[index] = ' '
        display_info = ''.join(chars)
        display_tempr = f'Темпиратура от {self.info.first_tempera} до {self.info.second_tempera}'

        cv.putText(img=self.image, text=f'Погода в {self.info.town_name}', org=(120, 20),
                   fontFace=cv.FONT_HERSHEY_COMPLEX, fontScale=0.5, color=[0, 0, 0])
        cv.putText(img=self.image, text=f'на {display_date}', org=(120, 40), fontFace=cv.FONT_HERSHEY_COMPLEX,
                   fontScale=0.5, color=[0, 0, 0])
        cv.putText(img=self.image, text=display_info, org=(20, 100), fontFace=cv.FONT_HERSHEY_COMPLEX, fontScale=0.5,
                   color=[0, 0, 0])
        cv.putText(img=self.image, text=display_tempr, org=(20, 120), fontFace=cv.FONT_HERSHEY_COMPLEX, fontScale=0.5,
                   color=[0, 0, 0])
        pass

    def create_image(self):
        """Создание изображения"""
        description = self.info.cloudiness.lower()
        res_could = re.search('cloudy', description)
        res_overcast = re.search('overcast', description)
        res_foggy = re.search('foggy', description)
        res_snow = re.search('snow', description)
        res_rain = re.search('rain', description)
        res_drizzle = re.search('drizzle', description)

        if res_snow:
            insert_file = self.FILE_SNOW
            colors = self.COLORS_SNOW
        elif res_could or res_foggy or res_overcast:
            insert_file = self.FILE_COULD
            colors = self.COLORS_COULD
        elif res_rain or res_drizzle:
            insert_file = self.FILE_RAIN
            colors = self.COLORS_RAIN
        else:
            insert_file = self.FILE_SUN
            colors = self.COLORS_CLEAR

        self.fill_gradient(colors[0], colors[1])
        self.insert_label_image(what=insert_file)
        self.add_text()

    def run(self):
        """Обработка
        Проверим есть-ли картинка на диске
        Создать ее если нету
        """
        if not os.path.isdir(self.IMAGE_SAVE_FOLDER):
            os.mkdir(self.IMAGE_SAVE_FOLDER)
        file_name = os.path.join(self.IMAGE_SAVE_FOLDER, self.info.picture_file_name)
        if not os.path.exists(file_name):
            self.image = self._create_blanc()
            self.create_image()
            file_name = os.path.normpath(file_name)
            cv.imwrite(file_name, img=self.image)


class Manager:
    """Менеджер исполнения"""
    HEADER = {
        "Accept-Encoding": "gzip,deflate",
    }
    URL_IF_CONFIG_ME = 'https://ifconfig.me/'
    URL_YOU_SELF = 'http://ipwhois.app/json/'

    def __init__(self, city: Text, from_date: datetime, to_date: datetime, local: bool):
        """
        Инициализация
        :param city: город
        :param from_date: начальная двтв
        :param to_date: конечная дата
        :param local: локальный режим (без Internet)
        """
        self.time_start: float = time.monotonic()
        self.time_total: float = 0
        self.city: Text = city
        self.from_date: datetime = from_date
        self.to_date: datetime = to_date
        self.local: bool = local
        self.split_by = cpu_count()
        self.weathers_info: List[WeatherOneDay] = []
        self.images_info: List[ImageMaker] = []
        self._prepare()

    def _prepare(self):
        """
        Подготовка данных для запуска
        :return: None
        """
        if self.city.lower() == 'self':
            self._get_self_location_inet()
        delta = timedelta(days=1)
        current_date = self.from_date
        while current_date <= self.to_date:
            current_weather = WeatherOneDay(city=self.city, date=current_date, local=self.local)
            self.weathers_info.append(current_weather)
            current_date += delta

    def _get_self_location_inet(self):
        """
        Найти своё местоположение по публичному ip адресу
        Перезапишет sef.city
        :return: None
        """

        response = requests.get(self.URL_YOU_SELF, headers=self.HEADER)
        if response.status_code != 200:
            log.error(f'Inet request return (get owner location)  {response.status_code} '
                      f'for url {self.URL_YOU_SELF}')
        else:
            from_inet = response.json()
            self.city = from_inet['city']
            log.info(f'Owner location is {self.city}')

    @staticmethod
    def _is_alive(what: List):
        """
        Проверка всех из what на признак is_alive
        :param what:
        :return:
        """

        return any((item.is_alive() for item in what))

    def _wait_all_items_info(self, what: List):
        """
        Ждать завершения работы всех из what
        :param what: список обьектов в работе
        :return: Время работы в сек
        """
        count = 0
        while self._is_alive(what):
            time.sleep(1)
            count += 1
        return count

    def run_by_portion(self, what: List):
        """
        Взять инфу по погоде (treads)
        :return: время ожидания
        """
        time_wait = 0
        split_weathers_info = split_portion(what, self.split_by)
        for portion in split_weathers_info:
            for item in portion:
                item.start()

            time_wait += self._wait_all_items_info(what=portion)
            for item in portion:
                item.join()
        return time_wait

    def print_result(self):
        """
        Вывести прогноз на консоль
        :return: None
        """
        log.info('Вывод данных на консоль')
        print(f'Прогноз погодв для {self.city}')
        print(f'C {self.from_date} по {self.to_date}')
        print('-' * 40)
        for item in self.weathers_info:
            print(f'{item.result.date.strftime(DATE_FORMAT_POINT)} {item.result.first_tempera:10} '
                  f'{item.result.second_tempera:10} {item.result.cloudiness}')
        print('-' * 40)

    def view_images(self):
        """Просмотреть запрошенные излбражения"""

        for item in self.weathers_info:
            file = item.result.picture_file_name

            file_name = os.path.join(ImageMaker.IMAGE_SAVE_FOLDER, file)
            file_name = os.path.normpath(file_name)
            if os.path.isfile(file_name):
                src = cv.imread(file_name)
                ImageMaker.view_image(src, win_title=file_name)

    def run(self):
        """
        Взять инфу и нарисовать открытки
        :return: None
        """
        self.get_weather()
        self.make_images()
        self.time_total = time.monotonic() - self.time_start

    def get_weather(self):
        """Взять погоду"""
        log.info(f'Начинаем получение данных для погоды')
        time_wait = self.run_by_portion(what=self.weathers_info)
        log.info(f'время обработки {time_wait}')

    def make_images(self):
        """Создать открытки"""
        log.info(f'Начинаем создание открыток')
        self.images_info = [ImageMaker(info=item.result) for item in self.weathers_info]
        time_wait = self.run_by_portion(what=self.images_info)
        log.info(f'время обработки {time_wait}')


def split_portion(what: List, num: int) -> List:
    """
    Разделить по порциям
    :param what: что делим
    :param num: кол-во в 1 порции
    :return:
    """
    portion = []
    result = []
    for item in what:
        portion.append(item)
        if len(portion) == num:
            addition = copy.deepcopy(portion)
            result.append(addition)
            portion.clear()
    if len(portion) > 0:
        result.append(portion)
    return result


def detect_date_format(date_str: Text):
    """
    Опредилить формат даты  по разделителю ['.','-','/']
    :param date_str: строка с датой
    :return: формат строки
    """
    delimiter = date_str[-5:-4]
    if delimiter == '.':
        date_format = DATE_FORMAT_POINT
    elif delimiter == '-':
        date_format = DATE_FORMAT_MINUS
    else:
        date_format = DATE_FORMAT_HEY
    return date_format
