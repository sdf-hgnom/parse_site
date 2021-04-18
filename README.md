# parse_site

Консольная программа отображения прогноза погоды  
Запуск :  python show_weather.py  

C аргументами  

Прогноз погоды и открытки

optional arguments:
  -h, --help  show this help message and exit

Команды скрипта:
  Перечень команд вызова

  {del,show}
    del       Удалить данные из б/д
    show      Просмотр прогноза погоды
  
Что было использованно  
argparse  
numpy  
bs4  
requests  
peewee  
cv2  
geopy.geocoders  
threading  
multiprocessing  

База данных Postgres  
Для прогноза парсится сайт https://darksky.net  
Открытки с прогнозом сохраняются в БД и на диск  
