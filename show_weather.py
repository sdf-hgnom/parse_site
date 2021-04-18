# -*- coding: utf-8 -*-

# use Python 3.7.3

"""

# В очередной спешке, проверив приложение с прогнозом погоды, вы выбежали
# навстречу ревью вашего кода, которое ожидало вас в офисе.
# И тут же день стал хуже - вместо обещанной облачности вас встретил ливень.

# Вы промокли, настроение было испорчено, и на ревью вы уже пришли не в духе.
# В итоге такого сокрушительного дня вы решили написать свою программу для прогноза погоды
# из источника, которому вы доверяете.

# Для этого вам нужно:

# Создать модуль-движок с классом WeatherMaker, необходимым для получения и формирования предсказаний.
# В нём должен быть метод, получающий прогноз с выбранного вами сайта (парсинг + re) за некоторый диапазон дат,
# а затем, получив данные, сформировать их в словарь {погода: Облачная, температура: 10, дата:datetime...}

# Добавить класс ImageMaker.
# Снабдить его методом рисования открытки
# (использовать OpenCV, в качестве заготовки брать lesson_016/python_snippets/external_data/probe.jpg):
#   С текстом, состоящим из полученных данных (пригодится cv2.putText)
#   С изображением, соответствующим типу погоды
# (хранятся в lesson_016/python_snippets/external_data/weather_img ,но можно нарисовать/добавить свои)
#   В качестве фона добавить градиент цвета, отражающего тип погоды
# Солнечно - от желтого к белому
# Дождь - от синего к белому
# Снег - от голубого к белому
# Облачно - от серого к белому

# Добавить класс DatabaseUpdater с методами:
#   Получающим данные из базы данных за указанный диапазон дат.
#   Сохраняющим прогнозы в базу данных (использовать peewee)

# Сделать программу с консольным интерфейсом, постаравшись все выполняемые действия вынести в отдельные функции.
# Среди действий, доступных пользователю, должны быть:
#   Добавление прогнозов за диапазон дат в базу данных
#   Получение прогнозов за диапазон дат из базы
#   Создание открыток из полученных прогнозов
#   Выведение полученных прогнозов на консоль
# При старте консольная утилита должна загружать прогнозы за прошедшую неделю.
"""


import argparse
import datetime
import weather
import model


def run_delete(args=None):
    """Режим Отчистки данных"""
    weather.log.info('Отчистка данных БД')
    print('Go delete records')
    model.delete_data()


def run_show(args):
    """Режим просмотра"""
    weather.log.info('Режим просмотра прогноза')
    if args.from_date is None:
        from_date = datetime.datetime.today()
        delta = datetime.timedelta(hours=from_date.hour, minutes=from_date.minute, seconds=from_date.second,
                                   microseconds=from_date.microsecond)
        from_date -= delta
    else:
        date_format = weather.detect_date_format(args.from_date)
        from_date = datetime.datetime.strptime(args.from_date, date_format)
    if args.to_date is None:
        delta = datetime.timedelta(days=7)
        to_date = from_date + delta
    else:
        date_format = weather.detect_date_format(args.to_date)
        to_date = datetime.datetime.strptime(args.to_date, date_format)
    if to_date < from_date:
        raise weather.ExceptionWeatherError('Дата окончания должна быть больше даты начала')
    if args.city.lower() == 'self' and args.local:
        raise weather.ExceptionWeatherError('Невозможно опредилить Ваше местопорложение в локальном режиме')
    weather.log.info(f'Запрошен прогноз погоды по {args.city} с {from_date} по {to_date}')
    manager = weather.Manager(city=args.city, from_date=from_date, to_date=to_date, local=args.local)
    manager.run()
    if not args.picture:
        manager.print_result()
    else:
        manager.view_images()
    running_time = datetime.datetime.strftime(datetime.datetime.utcfromtimestamp(manager.time_total), '%H:%M:%S')
    weather.log.info(f'Затрачено {running_time} времени на  работу')
    print(f'Затрачено {running_time} времени на  работу')


def get_init_args():
    """Разбор аргументов коммандной строки (данные пользователя)"""
    parser = argparse.ArgumentParser(description='Прогноз погоды и открытки')
    subparsers = parser.add_subparsers(title='Команды скрипта', description='Перечень команд вызова')
    delete_parser = subparsers.add_parser('del', help='Удалить данные из б/д')
    delete_parser.set_defaults(func=run_delete)
    show_parser = subparsers.add_parser('show', help='Просмотр прогноза погоды')
    show_parser.set_defaults(func=run_show)

    show_parser.add_argument('city', type=str, help='Город в котором смотрим прогноз (если указать self - '
                                                    'то текущее местоположение)')
    show_parser.add_argument('-f', '--from_date', type=str, help='Число начала прогноза (dd-mm-yyyy)', default=None)
    show_parser.add_argument('-t', '--to_date', type=str, help='Число окончания прогноза (dd-mm-yyyy)', default=None)
    show_parser.add_argument('-p', '--picture', help='Просмотр в виде открытки(если не указан - то на консоль)',
                             action='store_true', default=False)
    show_parser.add_argument('-l', '--local', help='Просмотр прогноза по ранее сохраненным данным (Без Инет !!)',
                             default=False, action='store_true')
    args = parser.parse_args()

    return args


def main():
    user_input = get_init_args()
    print('u_o:',user_input)
    user_input.func(user_input)
    print('All Done')


if __name__ == '__main__':
    main()

# зачет!