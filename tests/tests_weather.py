import unittest
from collections import namedtuple
from unittest.mock import Mock, patch

from peewee import SqliteDatabase

from model import Towns, WeatherReport
from datetime import datetime
import weather

memory_db = SqliteDatabase(':memory:')

MODELS = [Towns, WeatherReport]

Locator = namedtuple('Locator', 'latitude longitude')
location_t = Locator('51.9728565', '113.4097271')
TestResponce = namedtuple('TestResponce', 'status_code text')
return_responce = TestResponce(200, b'<!doctype html>\n<html lang="en">\n<head>\n  '
                                    b'<meta charset="utf-8" lang="en">\n  '
                                    b'<meta name="apple-itunes-app" content="app-id=517329357, affiliate-data=darkskynet">\n\n  '
                                    b'<title>Dark Sky - Thursday, Oct 1st, 2020</title>\n\n  '
                                    b'<script async src="//storage.googleapis.com/outfox/dnt_min.js"></script>\n\n  '
                                    b'<link href=\'https://fonts.googleapis.com/css?family=Lato:300,400,700,900\' '
                                    b'rel=\'stylesheet\' type=\'text/css\'>\n\n  '
                                    b'<link rel="stylesheet" href="https://darksky.net/css/lib/selectric.css">\n  '
                                    b'<link type="text/css" href="https://darksky.net/dist/css/styletwo.min.css" rel="stylesheet">\n  \n'
                                    b'</head>\n\n<body class="day">\n\n  <section>\n\n  <nav>\n    '
                                    b'<div class="inner">\n      <a class="logo" href="/">\n        '
                                    b'<img src="/images/darkskylogo.png" alt="Dark Sky Logo">'
                                    b'<span style="position: relative; top: -10px;">Dark Sky by Apple</span>\n      </a>\n      '
                                    b'<a href="/app" class="headerAppLink">\n        '
                                    b'<span id="phone-icon"><img src="/images/mobile-app-icon.png" alt="Smartphone Icon"></span>App\n      '
                                    b'</a>\n      <a href="/maps">\n        Maps\n      </a>\n      '
                                    b'<a href="/dev">\n        Dark Sky API\n      </a>\n      '
                                    b'<a href="/help/website">\n        Help\n      </a>\n    </div>\n  </nav>\n'
                                    b'</section>\n  <!-- views/partials/header.ejs -->\n\n<div id="header">\n  '
                                    b'<a class="backToForecast" href="/forecast/51.9729,113.4097/us12/en">\xe2\x86\x90 Go Back</a>\n\n  '
                                    b'<form id="searchForm">\n    '
                                    b'<a class="currentLocationButton" style="display:none">\n      '
                                    b'<img width="16" height="16" src="/images/current-location.png" alt="Current Location Button">\n    </a>\n\n    '
                                    b'<input type="text" value="">\n\n    <a class="searchButton">\n      '
                                    b'<img width="16" height="16" src="/images/search.png" alt="Search Button">\n    </a>\n\n    '
                                    b'<div id="savedLocations">\n      '
                                    b'<div class="autocomplete__container" style="margin: 20px; margin-bottom: 5px; display: none; overflow: hidden;">\n        '
                                    b'<div class="autocomplete__results__container" id="autocomplete__results__container"></div>\n      </div>\n      '
                                    b'<div class="inner"></div>\n    </div>\n    \n  </form>\n\n  <div class="options">\n    '
                                    b'<select class="units">\n      <option value="us">\xcb\x9aF,&nbsp;mph</option>\n      '
                                    b'<option value="si">\xcb\x9aC,&nbsp;m/s</option>\n      '
                                    b'<option value="ca">\xcb\x9aC,&nbsp;km/h</option>\n      '
                                    b'<option value="uk2">\xcb\x9aC,&nbsp;mph</option>\n    </select>\n\n    '
                                    b'<select class="language">\n      <option value="de">Deutsch</option>\n      '
                                    b'<option value="en">English</option>\n      '
                                    b'<option value="es">Espa\xc3\xb1ol</option>\n      '
                                    b'<option value="fr">Fran\xc3\xa7ais</option>\n      '
                                    b'<option value="it">Italiano</option>\n      '
                                    b'<option value="nl">Nederlands</option>\n      '
                                    b'<option value="tr">T\xc3\xbcrk</option>\n      '
                                    b'<option value="ar">\xd8\xb9\xd8\xb1\xd8\xa8\xd9\x8a</option>\n      '
                                    b'<option value="zh">\xe4\xb8\xad\xe6\x96\x87</option>\n      '
                                    b'<option value="zh-tw">\xe7\xb9\x81\xe9\xab\x94\xe4\xb8\xad\xe6\x96\x87</option>\n      '
                                    b'<option value="ja">\xe6\x97\xa5\xe6\x9c\xac\xe8\xaa\x9e</option>\n      '
                                    b'<option value="x-pig-latin">Pig Latin</option>\n    </select>\n  </div>\n\n</div>\n\n  '
                                    b'<div id="main" class="center">\n\n    '
                                    b'<div class="dayDetails center">\n\n      '
                                    b'<div class="title">\n        \n        '
                                    b'<a class="prev day swip" href="/details/51.9729,113.4097/2020-9-30/us12/en" '
                                    b'rel="nofollow">\xe2\x86\x90 Wednesday, Sep 30th</a>\n        '
                                    b'<div class="date">Thursday, Oct 1st, 2020</div>\n        '
                                    b'<a class="next day swap" href="/details/51.9729,113.4097/2020-10-2/us12/en" '
                                    b'rel="nofollow">Friday, Oct 2nd \xe2\x86\x92</a>\n      </div>\n\n      \n      '
                                    b'<p id="summary">Light rain and  throughout the&nbsp;day.</p>\n\n      '
                                    b'<div class="dayExtras">\n        '
                                    b'<div class="highLowTemp swip">\n          '
                                    b'<span class="highTemp swip">\n            '
                                    b'<span class="temp">32\xcb\x9a</span>\n            '
                                    b'<span class="time">4am</span>\n          '
                                    b'</span>\n          \n          '
                                    b'<span class="arrow">\xe2\x86\x92</span>\n          \n          '
                                    b'<span class="lowTemp swap">\n            '
                                    b'<span class="temp">44\xcb\x9a</span>\n            '
                                    b'<span class="time">1pm</span>\n          </span>\n        '
                                    b'</div>\n\n        '
                                    b'<div class="sunTimes">\n          \n          '
                                    b'<span class="sunrise swip">\n            '
                                    b'<img src="/images/sunrise.png" width="28" height="30" />\n            '
                                    b'<span class="time">7:29am</span>\n          </span>\n\n          \n\n          \n          '
                                    b'<span class="sunset swap">\n            '
                                    b'<img src="/images/sunset.png" width="28" height="30" />\n            '
                                    b'<span class="time">7:05pm</span>\n          '
                                    b'</span>\n          \n        </div>\n\n        '
                                    b'<div class="precipAccum swap">\n          '
                                    b'<span class="label swip">Rain</span>\n          '
                                    b'<span class="val swap">\n          \n            <span class="num swip">0.2</span>\n'
                                    b'            <span class="unit swap">in</span>\n          </span>\n        '
                                    b'</div>\n      </div>\n    </div>\n\n    '
                                    b'<div id="slider">\n      '
                                    b'<div class="handle">\n        '
                                    b'<div class="line"></div>\n      '
                                    b'</div>\n    </div>\n\n    '
                                    b'<div class="scroll-container">\n      '
                                    b'<div id="timeline" class="timeline_container">\n        '
                                    b'<div class="timeline">\n          '
                                    b'<div class="stripes"></div>\n          '
                                    b'<div class="hour_ticks"></div>\n          '
                                    b'<div class="hours"></div>\n          '
                                    b'<div class="temps"></div>\n        </div>\n      </div>\n    </div>\n\n    '
                                    b'<div id="currentDetails">\n      <div class="section">\n        '
                                    b'<div class="temperature">\n          '
                                    b'<span class="label swip">Temp:</span>\n          '
                                    b'<span class="val swap">\n            '
                                    b'<span class="num">43</span><span class="unit">\xcb\x9a</span>\n        </div>\n  '
                                    b'<div class="precipProbability">\n          '
                                    b'<span class="label swip">Precip:</span>\n          '
                                    b'<span class="val swap">\n            '
                                    b'<span class="num swip">41</span><span class="unit swap">%</span>\n          '
                                    b'</span>\n        </div>\n      </div>\n\n      <div class="section">\n        '
                                    b'<div class="wind">\n          '
                                    b'<span class="label swip">Wind:</span>\n          '
                                    b'<span class="val swap">\n            '
                                    b'<span class="num swip">6</span>\n            '
                                    b'<span class="unit swap">mph</span>\n            \n            '
                                    b'<span class="direction" title="S" style="display:inline-block;'
                                    b'-ms-transform:rotate(181deg);-webkit-transform:rotate(181deg);'
                                    b'transform:rotate(181deg);">\xe2\x86\x91</span>\n          </span>\n   </div>\n   '
                                    b'<div class="pressure">\n          <span class="label swip">Pressure:</span>\n '
                                    b'<span class="val swap">\n            '
                                    b'<span class="num swip">1011</span>\n            '
                                    b'<span class="unit swap">mb</span>\n          </span>\n        </div>\n      '
                                    b'</div>\n\n      <div class="section">\n        '
                                    b'<div class="humidity">\n          '
                                    b'<span class="label swip">Humidity:</span>\n          '
                                    b'<span class="val swap">\n            '
                                    b'<span class="num swip">67</span><span class="unit swap">%</span>\n          '
                                    b'</span>\n        </div>\n        '
                                    b'<div class="dew_point">\n          '
                                    b'<span class="label swip">Dew Pt:</span>\n          '
                                    b'<span class="val swap">\n            '
                                    b'<span class="num">33</span><span class="unit">\xcb\x9a</span>\n          '
                                    b'</span>\n        '
                                    b'</div>\n      </div>\n\n      '
                                    b'<div class="section">\n        '
                                    b'<div class="uv_index">\n          '
                                    b'<span class="label swip">UV Index:</span>\n          '
                                    b'<span class="val swap">\n            '
                                    b'<span class="num">2</span>\n          </span>\n        </div>\n        '
                                    b'<div class="visibility">\n          '
                                    b'<span class="label swip">Visibility:</span>\n          '
                                    b'<span class="val swap">\n            '
                                    b'<span class="num swip">10+</span>\n            '
                                    b'<span class="unit swap">mi</span>\n          </span>\n        </div>\n      '
                                    b'</div>\n    </div>\n\n      '
                                    b'<div class="plotContainer">\n        '
                                    b'<div class="plotLabel">Temperature / <span style="opacity:0.5">Feels Like</span></div>\n        '
                                    b'<div id="temperature_graph" class="plot"></div>\n      </div>\n\n      '
                                    b'<div class="plotContainer">\n        '
                                    b'<div class="plotLabel">Precip Probability</div>\n        '
                                    b'<div id="precip_graph" class="plot"></div>\n      </div>\n\n      '
                                    b'<div class="plotContainer">\n        '
                                    b'<div class="plotLabel">Humidity</div>\n        '
                                    b'<div id="humidity_test" class="plot"></div>\n      </div>\n\n      '
                                    b'<div class="plotContainer">\n        '
                                    b'<div class="plotLabel">Dew Point</div>\n        '
                                    b'<div id="dew_point_graph" class="plot"></div>\n      '
                                    b'</div>\n\n      <!-- <div class="plotContainer">\n        '
                                    b'<div class="plotLabel">Humidity / <span style="opacity:0.5">Dew Point</span></div>\n        '
                                    b'<div id="humidity_graph" class="plot"></div>\n      </div> -->\n\n      '
                                    b'<div class="plotContainer">\n        '
                                    b'<div class="plotLabel">Wind</div>\n        '
                                    b'<div id="wind_graph" class="plot"></div>\n      </div>\n\n      '
                                    b'<div class="plotContainer">\n        '
                                    b'<div class="plotLabel">Atmospheric Pressure</div>\n        '
                                    b'<div id="pressure_graph" class="plot"></div>\n      </div>\n\n      '
                                    b'<div class="plotContainer">\n        '
                                    b'<div class="plotLabel">UV Index</div>\n        '
                                    b'<div id="uv_graph" class="plot"></div>\n      </div>\n\n      '
                                    b'<div class="plotContainer">\n        '
                                    b'<div class="plotLabel">Visibility</div>\n        '
                                    b'<div id="visibility_graph" class="plot"></div>\n      </div>\n    </div>\n  </div>\n\n\n  '
                                    b'<div id="footer">\n\n  \n\n  <div id="units-container">\n    '
                                    b'<div class="options">\n      '
                                    b'<select class="units">\n        '
                                    b'<option value="us">\xcb\x9aF,&nbsp;mph</option>\n        '
                                    b'<option value="si">\xcb\x9aC,&nbsp;m/s</option>\n        '
                                    b'<option value="ca">\xcb\x9aC,&nbsp;km/h</option>\n        '
                                    b'<option value="uk2">\xcb\x9aC,&nbsp;mph</option>\n      </select>\n\n      '
                                    b'<select class="language">\n        '
                                    b'<option value="de">Deutsch</option>\n        '
                                    b'<option value="en">English</option>\n        '
                                    b'<option value="es">Espa\xc3\xb1ol</option>\n        '
                                    b'<option value="fr">Fran\xc3\xa7ais</option>\n        '
                                    b'<option value="it">Italiano</option>\n        '
                                    b'<option value="nl">Nederlands</option>\n        '
                                    b'<option value="tr">T\xc3\xbcrk</option>\n        '
                                    b'<option value="ar">\xd8\xb9\xd8\xb1\xd8\xa8\xd9\x8a</option>\n        '
                                    b'<option value="zh">\xe4\xb8\xad\xe6\x96\x87</option>\n        '
                                    b'<option value="ja">\xe6\x97\xa5\xe6\x9c\xac\xe8\xaa\x9e</option>\n        '
                                    b'<option value="x-pig-latin">Pig Latin</option>\n      </select>\n    </div>\n  '
                                    b'</div>\n\n  \n  <div id="footer-section-container">\n    '
                                    b'<div class="footer-section contribute">\n      '
                                    b'<p><img alt="Dark Sky Logo" src="/images/darkskylogo.png"> Dark Sky</p>\n    '
                                    b'</div>\n    <div class="footer-section">\n      <ul>\n        '
                                    b'<li><a href="/app">iOS app</a></li>\n        '
                                    b'<li><a href="/tos">Terms of Service</a></li>\n        '
                                    b'<li><a href="/attribution">Attribution</a></li>\n        '
                                    b'<li><a href="https://blog.darksky.net/">Blog</a></li>\n        '
                                    b'<li><a href="/help">Help</a></li>\n        '
                                    b'<li><a href="/contact">Contact</a></li>\n        '
                                    b'<li><a href="/privacy">Privacy</a></li>\n      </ul>\n    </div>\n  '
                                    b'</div>\n\n  <div class="copyright">\n    '
                                    b'<span class="copyright">Copyright &copy; 2020 '
                                    b'<a href="https://apple.com">Apple Inc.</a> All rights reserved.&nbsp;</span>\n  '
                                    b'</div>\n</div>\n\n  <script>\n  var hours = [{"time":1601478000,'
                                    b'"summary":"Partly Cloudy","icon":"partly-cloudy-night","precipIntensity":0.0002,'
                                    b'"precipProbability":0.03,"precipType":"rain","temperature":36.09,'
                                    b'"apparentTemperature":32.78,"dewPoint":30.59,"humidity":0.8,"pressure":1012.9,'
                                    b'"windSpeed":4.02,"windGust":4.27,"windBearing":1,"cloudCover":0.38,'
                                    b'"uvIndex":0,"visibility":10,"ozone":311.4},{"time":1601481600,'
                                    b'"summary":"Partly Cloudy","icon":"partly-cloudy-night",'
                                    b'"precipIntensity":0,"precipProbability":0,"temperature":35.12,'
                                    b'"apparentTemperature":31.89,"dewPoint":30.7,"humidity":0.84,'
                                    b'"pressure":1012.8,"windSpeed":3.8,"windGust":4.17,"windBearing":3,'
                                    b'"cloudCover":0.35,"uvIndex":0,"visibility":10,"ozone":309.3},{"time":1601485200,'
                                    b'"summary":"Partly Cloudy","icon":"partly-cloudy-night","precipIntensity":0,'
                                    b'"precipProbability":0,"temperature":34.49,"apparentTemperature":31.04,'
                                    b'"dewPoint":30.56,"humidity":0.85,"pressure":1012.6,"windSpeed":3.91,"windGust":4.63,'
                                    b'"windBearing":1,"cloudCover":0.4,"uvIndex":0,"visibility":10,"ozone":307.6},'
                                    b'{"time":1601488800,"summary":"Partly Cloudy","icon":"partly-cloudy-night",'
                                    b'"precipIntensity":0,"precipProbability":0,"temperature":33.68,'
                                    b'"apparentTemperature":30.09,"dewPoint":29.93,"humidity":0.86,"pressure":1012.3,'
                                    b'"windSpeed":3.92,"windGust":4.94,"windBearing":2,"cloudCover":0.45,"uvIndex":0,'
                                    b'"visibility":10,"ozone":307.8},{"time":1601492400,"summary":"Partly Cloudy",'
                                    b'"icon":"partly-cloudy-night","precipIntensity":0,"precipProbability":0,'
                                    b'"temperature":32.96,"apparentTemperature":29.24,"dewPoint":29.32,"humidity":0.86,'
                                    b'"pressure":1012.4,"windSpeed":3.95,"windGust":5.27,"windBearing":3,'
                                    b'"cloudCover":0.58,"uvIndex":0,"visibility":10,"ozone":309.9},{"time":1601496000,'
                                    b'"summary":"Mostly Cloudy","icon":"partly-cloudy-night","precipIntensity":0,'
                                    b'"precipProbability":0,"temperature":32.44,"apparentTemperature":28.34,'
                                    b'"dewPoint":28.38,"humidity":0.85,"pressure":1012.9,'
                                    b'"windSpeed":4.23,"windGust":5.7,"windBearing":3,'
                                    b'"cloudCover":0.73,"uvIndex":0,"visibility":10,"ozone":313.2},{"time":1601499600,'
                                    b'"summary":"Mostly Cloudy","icon":"partly-cloudy-night","precipIntensity":0,'
                                    b'"precipProbability":0,"temperature":33.15,"apparentTemperature":28.99,'
                                    b'"dewPoint":28.24,"humidity":0.82,"pressure":1012.5,"windSpeed":4.41,'
                                    b'"windGust":6.43,"windBearing":6,"cloudCover":0.67,"uvIndex":0,'
                                    b'"visibility":10,"ozone":315.5},{"time":1601503200,"summary":"Partly Cloudy",'
                                    b'"icon":"partly-cloudy-night","precipIntensity":0,"precipProbability":0,'
                                    b'"temperature":32.99,"apparentTemperature":28.8,"dewPoint":27.19,'
                                    b'"humidity":0.79,"pressure":1013.1,"windSpeed":4.41,"windGust":7.72,'
                                    b'"windBearing":5,"cloudCover":0.5,"uvIndex":0,"visibility":10,"ozone":315.5},'
                                    b'{"time":1601506800,"summary":"Partly Cloudy","icon":"partly-cloudy-day",'
                                    b'"precipIntensity":0.0009,"precipProbability":0.08,"precipType":"rain",'
                                    b'"temperature":32.85,"apparentTemperature":28.36,"dewPoint":26.62,"humidity":0.78,'
                                    b'"pressure":1013.5,"windSpeed":4.69,"windGust":9.33,"windBearing":5,"cloudCover":0.55,'
                                    b'"uvIndex":0,"visibility":10,"ozone":314.6,"solar":{"azimuth":101,"altitude":4,'
                                    b'"dni":209.1,"ghi":16.7,"dhi":1.5,"etr":1357.6}},{"time":1601510400,"summary":'
                                    b'"Partly Cloudy","icon":"partly-cloudy-day","precipIntensity":0.0049,'
                                    b'"precipProbability":0.18,"precipType":"rain","temperature":34.59,'
                                    b'"apparentTemperature":31.36,"dewPoint":27.73,"humidity":0.76,'
                                    b'"pressure":1013.5,"windSpeed":3.72,"windGust":5.96,"windBearing":359,'
                                    b'"cloudCover":0.58,"uvIndex":0,"visibility":10,"ozone":314.1,'
                                    b'"solar":{"azimuth":113,"altitude":13,"dni":411.4,"ghi":101.6,"dhi":9.2,"etr":1357.6}},'
                                    b'{"time":1601514000,"summary":"Mostly Cloudy","icon":'
                                    b'"partly-cloudy-day","precipIntensity":0.0063,"precipProbability":0.23,'
                                    b'"precipType":"rain","temperature":36.57,"apparentTemperature":34,"dewPoint":28.83,'
                                    b'"humidity":0.73,"pressure":1013.2,"windSpeed":3.4,"windGust":7.7,"windBearing":355,'
                                    b'"cloudCover":0.87,"uvIndex":1,"visibility":10,"ozone":314.4,"solar":{"azimuth":126,'
                                    b'"altitude":21,"dni":295.1,"ghi":116.3,"dhi":10.6,"etr":1357.6}},'
                                    b'{"time":1601517600,"summary":"Possible Drizzle","icon":"rain",'
                                    b'"precipIntensity":0.0075,"precipProbability":0.27,"precipType":"rain",'
                                    b'"temperature":38.78,"apparentTemperature":34.94,"dewPoint":30.06,"humidity":0.71,'
                                    b'"pressure":1012.7,"windSpeed":5.12,"windGust":10.1,"windBearing":353,"cloudCover":1,'
                                    b'"uvIndex":2,"visibility":10,"ozone":315.1,"solar":{"azimuth":141,"altitude":28,'
                                    b'"dni":203,"ghi":103.7,"dhi":9.4,"etr":1357.7}},{"time":1601521200,"summary":'
                                    b'"Possible Light Rain","icon":"rain","precipIntensity":0.0092,'
                                    b'"precipProbability":0.32,"precipType":"rain","temperature":40.49,'
                                    b'"apparentTemperature":36.35,"dewPoint":31.73,"humidity":0.71,"pressure":1012.2,'
                                    b'"windSpeed":5.99,"windGust":11.43,"windBearing":354,"cloudCover":1,"uvIndex":2,'
                                    b'"visibility":10,"ozone":315.8,"solar":{"azimuth":157,"altitude":32,"dni":212.4,'
                                    b'"ghi":125.2,"dhi":11.4,"etr":1357.7}},{"time":1601524800,"summary":'
                                    b'"Possible Light Rain","icon":"rain","precipIntensity":0.0116,"precipProbability":0.38,'
                                    b'"precipType":"rain","temperature":42.4,"apparentTemperature":38.53,'
                                    b'"dewPoint":32.75,"humidity":0.68,"pressure":1011.6,"windSpeed":6.13,'
                                    b'"windGust":10.72,"windBearing":359,"cloudCover":1,"uvIndex":2,"visibility":10,'
                                    b'"ozone":316.7,"solar":{"azimuth":175,"altitude":35,"dni":216.1,"ghi":134.9,"dhi":12.3,'
                                    b'"etr":1357.7}},{"time":1601528400,"summary":"Possible Light Rain","icon":"rain",'
                                    b'"precipIntensity":0.0145,"precipProbability":0.46,"precipType":"rain","temperature":43.78,'
                                    b'"apparentTemperature":40.46,"dewPoint":33.52,"humidity":0.67,'
                                    b'"pressure":1011.2,"windSpeed":5.66,"windGust":8.96,'
                                    b'"windBearing":3,"cloudCover":1,"uvIndex":2,"visibility":10,"ozone":317.6,"solar":'
                                    b'{"azimuth":193,"altitude":34,"dni":215,"ghi":131.8,"dhi":12,"etr":1357.7}},'
                                    b'{"time":1601532000,"summary":"Possible Light Rain","icon":"rain","precipIntensity"'
                                    b':0.0195,"precipProbability":0.56,"precipType":"rain","temperature":41.62,'
                                    b'"apparentTemperature":38.04,"dewPoint":33.15,"humidity":0.72,"pressure":1011,'
                                    b'"windSpeed":5.47,"windGust":8.8,"windBearing":4,"cloudCover":0.99,"uvIndex":2,'
                                    b'"visibility":7.015,"ozone":318.3,"solar":{"azimuth":211,"altitude":30,"dni":220.2,'
                                    b'"ghi":122.6,"dhi":11.1,"etr":1357.8}},{"time":1601535600,"summary":'
                                    b'"Possible Light Rain","icon":"rain","precipIntensity":0.0198,"precipProbability":0.56,'
                                    b'"precipType":"rain","temperature":41.61,"apparentTemperature":38.26,"dewPoint":33.48,'
                                    b'"humidity":0.73,"pressure":1011.2,"windSpeed":5.14,"windGust":6.96,"windBearing":0,'
                                    b'"cloudCover":0.98,"uvIndex":1,"visibility":6.927,"ozone":318.7,"solar":{"azimuth":226,'
                                    b'"altitude":25,"dni":212.3,"ghi":97.5,"dhi":8.9,"etr":1357.8}},{"time":1601539200,'
                                    b'"summary":"Possible Light Rain","icon":"rain","precipIntensity":0.0185,'
                                    b'"precipProbability":0.54,"precipType":"rain","temperature":41.77,'
                                    b'"apparentTemperature":38.79,"dewPoint":33.64,"humidity":0.73,"pressure":1011.5,'
                                    b'"windSpeed":4.69,"windGust":4.9,"windBearing":352,"cloudCover":0.99,"uvIndex":1,'
                                    b'"visibility":7.521,"ozone":319,"solar":{"azimuth":240,"altitude":17,"dni":180.6,'
                                    b'"ghi":59,"dhi":5.4,"etr":1357.8}},{"time":1601542800,"summary":'
                                    b'"Possible Light Rain","icon":"rain","precipIntensity":0.0169,"precipProbability":0.52,'
                                    b'"precipType":"rain","temperature":41.74,"apparentTemperature":39,"dewPoint":34.06,'
                                    b'"humidity":0.74,"pressure":1011.9,"windSpeed":4.38,"windGust":4.45,"windBearing":346,'
                                    b'"cloudCover":0.99,"uvIndex":0,"visibility":8.097,"ozone":318.8,"solar":{"azimuth":253,'
                                    b'"altitude":9,"dni":128.3,"ghi":21.6,"dhi":2,"etr":1357.9}},{"time":1601546400,'
                                    b'"summary":"Possible Light Rain","icon":"rain","precipIntensity":0.0147,'
                                    b'"precipProbability":0.49,"precipType":"rain","temperature":41.12,'
                                    b'"apparentTemperature":38.35,"dewPoint":34.33,"humidity":0.77,"pressure":1012.5,'
                                    b'"windSpeed":4.31,"windGust":5.22,"windBearing":348,"cloudCover":0.99,"uvIndex":0,'
                                    b'"visibility":8.469,"ozone":318},{"time":1601550000,"summary":"Possible Light Rain",'
                                    b'"icon":"rain","precipIntensity":0.0125,"precipProbability":0.45,"precipType":"rain",'
                                    b'"temperature":40.39,"apparentTemperature":37.03,"dewPoint":34.2,"humidity":0.78,'
                                    b'"pressure":1013.2,"windSpeed":4.86,"windGust":7.61,"windBearing":348,"cloudCover":0.99,'
                                    b'"uvIndex":0,"visibility":8.815,"ozone":316.6},{"time":1601553600,'
                                    b'"summary":"Possible Light Rain","icon":"rain","precipIntensity":0.0115,'
                                    b'"precipProbability":0.43,"precipType":"rain","temperature":39.73,'
                                    b'"apparentTemperature":36.05,"dewPoint":34.13,"humidity":0.8,"pressure":1013.7,'
                                    b'"windSpeed":5.13,"windGust":9.58,"windBearing":346,"cloudCover":0.99,"uvIndex":0,'
                                    b'"visibility":8.941,"ozone":315.7},{"time":1601557200,"summary":"Possible Light Rain",'
                                    b'"icon":"rain","precipIntensity":0.0134,"precipProbability":0.51,"precipType":'
                                    b'"rain","temperature":39.03,"apparentTemperature":35.09,"dewPoint":34.03,'
                                    b'"humidity":0.82,"pressure":1013.9,"windSpeed":5.32,"windGust":10.59,'
                                    b'"windBearing":325,"cloudCover":0.99,"uvIndex":0,"visibility":8.779,'
                                    b'"ozone":315.1},{"time":1601560800,"summary":"Possible Light Rain",'
                                    b'"icon":"rain","precipIntensity":0.0158,"precipProbability":0.58,'
                                    b'"precipType":"rain","temperature":38.41,"apparentTemperature":34.83,"dewPoint":34.33,'
                                    b'"humidity":0.85,"pressure":1014.1,"windSpeed":4.73,"windGust":6.92,"windBearing":312,'
                                    b'"cloudCover":1,"uvIndex":0,"visibility":6.108,"ozone":314.7}],\n      '
                                    b'startHour = undefined,\n      latitude = 51.9729,\n      longitude = 113.4097,\n      '
                                    b'forecastTime = 1601526382,\n      tz_offset = 9,\n      units = "us",\n      '
                                    b'unitsList = {"pressure":"mb","distance":"mi","speed":"mph","length":"in"},\n      '
                                    b'language = "en",\n      timeFormat = "12",\n      languageReversed = false,\n      '
                                    b'conditions = {"clear":"clear","light-clouds":"partly cloudy","heavy-clouds":'
                                    b'"overcast","medium-rain":"rain","very-light-rain":"drizzle","light-rain":'
                                    b'"light rain","heavy-rain":"heavy rain","medium-sleet":"sleet","very-light-sleet":'
                                    b'"light sleet","light-sleet":"light sleet","heavy-sleet":"heavy sleet","medium-snow":'
                                    b'"snow","very-light-snow":"flurries","light-snow":"light snow","heavy-snow":'
                                    b'"heavy snow"},\n      cityName = "",\n      cityNameOnly = false;\n  </script>\n\n  '
                                    b'<script type="text/javascript" src="/dist/js/daytwo.js"></script>\n\n</body>\n</html>\n')


# def create_responce():
#     result= requests.Response()
#     result.status_code = 200
#     result.raw._content = b'<!doctype html>\n<html lang="en">\n<head>\n  <meta charset="utf-8" lang="en">\n  <meta name="apple-itunes-app" content="app-id=517329357, affiliate-data=darkskynet">\n\n  <title>Dark Sky - Thursday, Oct 1st, 2020</title>\n\n  <script async src="//storage.googleapis.com/outfox/dnt_min.js"></script>\n\n  <link href=\'https://fonts.googleapis.com/css?family=Lato:300,400,700,900\' rel=\'stylesheet\' type=\'text/css\'>\n\n  <link rel="stylesheet" href="https://darksky.net/css/lib/selectric.css">\n  <link type="text/css" href="https://darksky.net/dist/css/styletwo.min.css" rel="stylesheet">\n  \n</head>\n\n<body class="day">\n\n  <section>\n\n  <nav>\n    <div class="inner">\n      <a class="logo" href="/">\n        <img src="/images/darkskylogo.png" alt="Dark Sky Logo"><span style="position: relative; top: -10px;">Dark Sky by Apple</span>\n      </a>\n      <a href="/app" class="headerAppLink">\n        <span id="phone-icon"><img src="/images/mobile-app-icon.png" alt="Smartphone Icon"></span>App\n      </a>\n      <a href="/maps">\n        Maps\n      </a>\n      <a href="/dev">\n        Dark Sky API\n      </a>\n      <a href="/help/website">\n        Help\n      </a>\n    </div>\n  </nav>\n</section>\n  <!-- views/partials/header.ejs -->\n\n<div id="header">\n  <a class="backToForecast" href="/forecast/51.9729,113.4097/us12/en">\xe2\x86\x90 Go Back</a>\n\n  <form id="searchForm">\n    <a class="currentLocationButton" style="display:none">\n      <img width="16" height="16" src="/images/current-location.png" alt="Current Location Button">\n    </a>\n\n    <input type="text" value="">\n\n    <a class="searchButton">\n      <img width="16" height="16" src="/images/search.png" alt="Search Button">\n    </a>\n\n    <div id="savedLocations">\n      <div class="autocomplete__container" style="margin: 20px; margin-bottom: 5px; display: none; overflow: hidden;">\n        <div class="autocomplete__results__container" id="autocomplete__results__container"></div>\n      </div>\n      <div class="inner"></div>\n    </div>\n    \n  </form>\n\n  <div class="options">\n    <select class="units">\n      <option value="us">\xcb\x9aF,&nbsp;mph</option>\n      <option value="si">\xcb\x9aC,&nbsp;m/s</option>\n      <option value="ca">\xcb\x9aC,&nbsp;km/h</option>\n      <option value="uk2">\xcb\x9aC,&nbsp;mph</option>\n    </select>\n\n    <select class="language">\n      <option value="de">Deutsch</option>\n      <option value="en">English</option>\n      <option value="es">Espa\xc3\xb1ol</option>\n      <option value="fr">Fran\xc3\xa7ais</option>\n      <option value="it">Italiano</option>\n      <option value="nl">Nederlands</option>\n      <option value="tr">T\xc3\xbcrk</option>\n      <option value="ar">\xd8\xb9\xd8\xb1\xd8\xa8\xd9\x8a</option>\n      <option value="zh">\xe4\xb8\xad\xe6\x96\x87</option>\n      <option value="zh-tw">\xe7\xb9\x81\xe9\xab\x94\xe4\xb8\xad\xe6\x96\x87</option>\n      <option value="ja">\xe6\x97\xa5\xe6\x9c\xac\xe8\xaa\x9e</option>\n      <option value="x-pig-latin">Pig Latin</option>\n    </select>\n  </div>\n\n</div>\n\n  <div id="main" class="center">\n\n    <div class="dayDetails center">\n\n      <div class="title">\n        \n        <a class="prev day swip" href="/details/51.9729,113.4097/2020-9-30/us12/en" rel="nofollow">\xe2\x86\x90 Wednesday, Sep 30th</a>\n        <div class="date">Thursday, Oct 1st, 2020</div>\n        <a class="next day swap" href="/details/51.9729,113.4097/2020-10-2/us12/en" rel="nofollow">Friday, Oct 2nd \xe2\x86\x92</a>\n      </div>\n\n      \n      <p id="summary">Light rain throughout the&nbsp;day.</p>\n\n      <div class="dayExtras">\n        <div class="highLowTemp swip">\n          <span class="highTemp swip">\n            <span class="temp">32\xcb\x9a</span>\n            <span class="time">4am</span>\n          </span>\n          \n          <span class="arrow">\xe2\x86\x92</span>\n          \n          <span class="lowTemp swap">\n            <span class="temp">44\xcb\x9a</span>\n            <span class="time">1pm</span>\n          </span>\n        </div>\n\n        <div class="sunTimes">\n          \n          <span class="sunrise swip">\n            <img src="/images/sunrise.png" width="28" height="30" />\n            <span class="time">7:29am</span>\n          </span>\n\n          \n\n          \n          <span class="sunset swap">\n            <img src="/images/sunset.png" width="28" height="30" />\n            <span class="time">7:05pm</span>\n          </span>\n          \n        </div>\n\n        <div class="precipAccum swap">\n          <span class="label swip">Rain</span>\n          <span class="val swap">\n          \n            <span class="num swip">0.2</span>\n            <span class="unit swap">in</span>\n          </span>\n        </div>\n      </div>\n    </div>\n\n    <div id="slider">\n      <div class="handle">\n        <div class="line"></div>\n      </div>\n    </div>\n\n    <div class="scroll-container">\n      <div id="timeline" class="timeline_container">\n        <div class="timeline">\n          <div class="stripes"></div>\n          <div class="hour_ticks"></div>\n          <div class="hours"></div>\n          <div class="temps"></div>\n        </div>\n      </div>\n    </div>\n\n    <div id="currentDetails">\n      <div class="section">\n        <div class="temperature">\n          <span class="label swip">Temp:</span>\n          <span class="val swap">\n            <span class="num">43</span><span class="unit">\xcb\x9a</span>\n        </div>\n        <div class="precipProbability">\n          <span class="label swip">Precip:</span>\n          <span class="val swap">\n            <span class="num swip">41</span><span class="unit swap">%</span>\n          </span>\n        </div>\n      </div>\n\n      <div class="section">\n        <div class="wind">\n          <span class="label swip">Wind:</span>\n          <span class="val swap">\n            <span class="num swip">6</span>\n            <span class="unit swap">mph</span>\n            \n            <span class="direction" title="S" style="display:inline-block;-ms-transform:rotate(181deg);-webkit-transform:rotate(181deg);transform:rotate(181deg);">\xe2\x86\x91</span>\n          </span>\n        </div>\n        <div class="pressure">\n          <span class="label swip">Pressure:</span>\n          <span class="val swap">\n            <span class="num swip">1011</span>\n            <span class="unit swap">mb</span>\n          </span>\n        </div>\n      </div>\n\n      <div class="section">\n        <div class="humidity">\n          <span class="label swip">Humidity:</span>\n          <span class="val swap">\n            <span class="num swip">67</span><span class="unit swap">%</span>\n          </span>\n        </div>\n        <div class="dew_point">\n          <span class="label swip">Dew Pt:</span>\n          <span class="val swap">\n            <span class="num">33</span><span class="unit">\xcb\x9a</span>\n          </span>\n        </div>\n      </div>\n\n      <div class="section">\n        <div class="uv_index">\n          <span class="label swip">UV Index:</span>\n          <span class="val swap">\n            <span class="num">2</span>\n          </span>\n        </div>\n        <div class="visibility">\n          <span class="label swip">Visibility:</span>\n          <span class="val swap">\n            <span class="num swip">10+</span>\n            <span class="unit swap">mi</span>\n          </span>\n        </div>\n      </div>\n    </div>\n\n      <div class="plotContainer">\n        <div class="plotLabel">Temperature / <span style="opacity:0.5">Feels Like</span></div>\n        <div id="temperature_graph" class="plot"></div>\n      </div>\n\n      <div class="plotContainer">\n        <div class="plotLabel">Precip Probability</div>\n        <div id="precip_graph" class="plot"></div>\n      </div>\n\n      <div class="plotContainer">\n        <div class="plotLabel">Humidity</div>\n        <div id="humidity_test" class="plot"></div>\n      </div>\n\n      <div class="plotContainer">\n        <div class="plotLabel">Dew Point</div>\n        <div id="dew_point_graph" class="plot"></div>\n      </div>\n\n      <!-- <div class="plotContainer">\n        <div class="plotLabel">Humidity / <span style="opacity:0.5">Dew Point</span></div>\n        <div id="humidity_graph" class="plot"></div>\n      </div> -->\n\n      <div class="plotContainer">\n        <div class="plotLabel">Wind</div>\n        <div id="wind_graph" class="plot"></div>\n      </div>\n\n      <div class="plotContainer">\n        <div class="plotLabel">Atmospheric Pressure</div>\n        <div id="pressure_graph" class="plot"></div>\n      </div>\n\n      <div class="plotContainer">\n        <div class="plotLabel">UV Index</div>\n        <div id="uv_graph" class="plot"></div>\n      </div>\n\n      <div class="plotContainer">\n        <div class="plotLabel">Visibility</div>\n        <div id="visibility_graph" class="plot"></div>\n      </div>\n    </div>\n  </div>\n\n\n  <div id="footer">\n\n  \n\n  <div id="units-container">\n    <div class="options">\n      <select class="units">\n        <option value="us">\xcb\x9aF,&nbsp;mph</option>\n        <option value="si">\xcb\x9aC,&nbsp;m/s</option>\n        <option value="ca">\xcb\x9aC,&nbsp;km/h</option>\n        <option value="uk2">\xcb\x9aC,&nbsp;mph</option>\n      </select>\n\n      <select class="language">\n        <option value="de">Deutsch</option>\n        <option value="en">English</option>\n        <option value="es">Espa\xc3\xb1ol</option>\n        <option value="fr">Fran\xc3\xa7ais</option>\n        <option value="it">Italiano</option>\n        <option value="nl">Nederlands</option>\n        <option value="tr">T\xc3\xbcrk</option>\n        <option value="ar">\xd8\xb9\xd8\xb1\xd8\xa8\xd9\x8a</option>\n        <option value="zh">\xe4\xb8\xad\xe6\x96\x87</option>\n        <option value="ja">\xe6\x97\xa5\xe6\x9c\xac\xe8\xaa\x9e</option>\n        <option value="x-pig-latin">Pig Latin</option>\n      </select>\n    </div>\n  </div>\n\n  \n  <div id="footer-section-container">\n    <div class="footer-section contribute">\n      <p><img alt="Dark Sky Logo" src="/images/darkskylogo.png"> Dark Sky</p>\n    </div>\n    <div class="footer-section">\n      <ul>\n        <li><a href="/app">iOS app</a></li>\n        <li><a href="/tos">Terms of Service</a></li>\n        <li><a href="/attribution">Attribution</a></li>\n        <li><a href="https://blog.darksky.net/">Blog</a></li>\n        <li><a href="/help">Help</a></li>\n        <li><a href="/contact">Contact</a></li>\n        <li><a href="/privacy">Privacy</a></li>\n      </ul>\n    </div>\n  </div>\n\n  <div class="copyright">\n    <span class="copyright">Copyright &copy; 2020 <a href="https://apple.com">Apple Inc.</a> All rights reserved.&nbsp;</span>\n  </div>\n</div>\n\n  <script>\n  var hours = [{"time":1601478000,"summary":"Partly Cloudy","icon":"partly-cloudy-night","precipIntensity":0.0002,"precipProbability":0.03,"precipType":"rain","temperature":36.09,"apparentTemperature":32.78,"dewPoint":30.59,"humidity":0.8,"pressure":1012.9,"windSpeed":4.02,"windGust":4.27,"windBearing":1,"cloudCover":0.38,"uvIndex":0,"visibility":10,"ozone":311.4},{"time":1601481600,"summary":"Partly Cloudy","icon":"partly-cloudy-night","precipIntensity":0,"precipProbability":0,"temperature":35.12,"apparentTemperature":31.89,"dewPoint":30.7,"humidity":0.84,"pressure":1012.8,"windSpeed":3.8,"windGust":4.17,"windBearing":3,"cloudCover":0.35,"uvIndex":0,"visibility":10,"ozone":309.3},{"time":1601485200,"summary":"Partly Cloudy","icon":"partly-cloudy-night","precipIntensity":0,"precipProbability":0,"temperature":34.49,"apparentTemperature":31.04,"dewPoint":30.56,"humidity":0.85,"pressure":1012.6,"windSpeed":3.91,"windGust":4.63,"windBearing":1,"cloudCover":0.4,"uvIndex":0,"visibility":10,"ozone":307.6},{"time":1601488800,"summary":"Partly Cloudy","icon":"partly-cloudy-night","precipIntensity":0,"precipProbability":0,"temperature":33.68,"apparentTemperature":30.09,"dewPoint":29.93,"humidity":0.86,"pressure":1012.3,"windSpeed":3.92,"windGust":4.94,"windBearing":2,"cloudCover":0.45,"uvIndex":0,"visibility":10,"ozone":307.8},{"time":1601492400,"summary":"Partly Cloudy","icon":"partly-cloudy-night","precipIntensity":0,"precipProbability":0,"temperature":32.96,"apparentTemperature":29.24,"dewPoint":29.32,"humidity":0.86,"pressure":1012.4,"windSpeed":3.95,"windGust":5.27,"windBearing":3,"cloudCover":0.58,"uvIndex":0,"visibility":10,"ozone":309.9},{"time":1601496000,"summary":"Mostly Cloudy","icon":"partly-cloudy-night","precipIntensity":0,"precipProbability":0,"temperature":32.44,"apparentTemperature":28.34,"dewPoint":28.38,"humidity":0.85,"pressure":1012.9,"windSpeed":4.23,"windGust":5.7,"windBearing":3,"cloudCover":0.73,"uvIndex":0,"visibility":10,"ozone":313.2},{"time":1601499600,"summary":"Mostly Cloudy","icon":"partly-cloudy-night","precipIntensity":0,"precipProbability":0,"temperature":33.15,"apparentTemperature":28.99,"dewPoint":28.24,"humidity":0.82,"pressure":1012.5,"windSpeed":4.41,"windGust":6.43,"windBearing":6,"cloudCover":0.67,"uvIndex":0,"visibility":10,"ozone":315.5},{"time":1601503200,"summary":"Partly Cloudy","icon":"partly-cloudy-night","precipIntensity":0,"precipProbability":0,"temperature":32.99,"apparentTemperature":28.8,"dewPoint":27.19,"humidity":0.79,"pressure":1013.1,"windSpeed":4.41,"windGust":7.72,"windBearing":5,"cloudCover":0.5,"uvIndex":0,"visibility":10,"ozone":315.5},{"time":1601506800,"summary":"Partly Cloudy","icon":"partly-cloudy-day","precipIntensity":0.0009,"precipProbability":0.08,"precipType":"rain","temperature":32.85,"apparentTemperature":28.36,"dewPoint":26.62,"humidity":0.78,"pressure":1013.5,"windSpeed":4.69,"windGust":9.33,"windBearing":5,"cloudCover":0.55,"uvIndex":0,"visibility":10,"ozone":314.6,"solar":{"azimuth":101,"altitude":4,"dni":209.1,"ghi":16.7,"dhi":1.5,"etr":1357.6}},{"time":1601510400,"summary":"Partly Cloudy","icon":"partly-cloudy-day","precipIntensity":0.0049,"precipProbability":0.18,"precipType":"rain","temperature":34.59,"apparentTemperature":31.36,"dewPoint":27.73,"humidity":0.76,"pressure":1013.5,"windSpeed":3.72,"windGust":5.96,"windBearing":359,"cloudCover":0.58,"uvIndex":0,"visibility":10,"ozone":314.1,"solar":{"azimuth":113,"altitude":13,"dni":411.4,"ghi":101.6,"dhi":9.2,"etr":1357.6}},{"time":1601514000,"summary":"Mostly Cloudy","icon":"partly-cloudy-day","precipIntensity":0.0063,"precipProbability":0.23,"precipType":"rain","temperature":36.57,"apparentTemperature":34,"dewPoint":28.83,"humidity":0.73,"pressure":1013.2,"windSpeed":3.4,"windGust":7.7,"windBearing":355,"cloudCover":0.87,"uvIndex":1,"visibility":10,"ozone":314.4,"solar":{"azimuth":126,"altitude":21,"dni":295.1,"ghi":116.3,"dhi":10.6,"etr":1357.6}},{"time":1601517600,"summary":"Possible Drizzle","icon":"rain","precipIntensity":0.0075,"precipProbability":0.27,"precipType":"rain","temperature":38.78,"apparentTemperature":34.94,"dewPoint":30.06,"humidity":0.71,"pressure":1012.7,"windSpeed":5.12,"windGust":10.1,"windBearing":353,"cloudCover":1,"uvIndex":2,"visibility":10,"ozone":315.1,"solar":{"azimuth":141,"altitude":28,"dni":203,"ghi":103.7,"dhi":9.4,"etr":1357.7}},{"time":1601521200,"summary":"Possible Light Rain","icon":"rain","precipIntensity":0.0092,"precipProbability":0.32,"precipType":"rain","temperature":40.49,"apparentTemperature":36.35,"dewPoint":31.73,"humidity":0.71,"pressure":1012.2,"windSpeed":5.99,"windGust":11.43,"windBearing":354,"cloudCover":1,"uvIndex":2,"visibility":10,"ozone":315.8,"solar":{"azimuth":157,"altitude":32,"dni":212.4,"ghi":125.2,"dhi":11.4,"etr":1357.7}},{"time":1601524800,"summary":"Possible Light Rain","icon":"rain","precipIntensity":0.0116,"precipProbability":0.38,"precipType":"rain","temperature":42.4,"apparentTemperature":38.53,"dewPoint":32.75,"humidity":0.68,"pressure":1011.6,"windSpeed":6.13,"windGust":10.72,"windBearing":359,"cloudCover":1,"uvIndex":2,"visibility":10,"ozone":316.7,"solar":{"azimuth":175,"altitude":35,"dni":216.1,"ghi":134.9,"dhi":12.3,"etr":1357.7}},{"time":1601528400,"summary":"Possible Light Rain","icon":"rain","precipIntensity":0.0145,"precipProbability":0.46,"precipType":"rain","temperature":43.78,"apparentTemperature":40.46,"dewPoint":33.52,"humidity":0.67,"pressure":1011.2,"windSpeed":5.66,"windGust":8.96,"windBearing":3,"cloudCover":1,"uvIndex":2,"visibility":10,"ozone":317.6,"solar":{"azimuth":193,"altitude":34,"dni":215,"ghi":131.8,"dhi":12,"etr":1357.7}},{"time":1601532000,"summary":"Possible Light Rain","icon":"rain","precipIntensity":0.0195,"precipProbability":0.56,"precipType":"rain","temperature":41.62,"apparentTemperature":38.04,"dewPoint":33.15,"humidity":0.72,"pressure":1011,"windSpeed":5.47,"windGust":8.8,"windBearing":4,"cloudCover":0.99,"uvIndex":2,"visibility":7.015,"ozone":318.3,"solar":{"azimuth":211,"altitude":30,"dni":220.2,"ghi":122.6,"dhi":11.1,"etr":1357.8}},{"time":1601535600,"summary":"Possible Light Rain","icon":"rain","precipIntensity":0.0198,"precipProbability":0.56,"precipType":"rain","temperature":41.61,"apparentTemperature":38.26,"dewPoint":33.48,"humidity":0.73,"pressure":1011.2,"windSpeed":5.14,"windGust":6.96,"windBearing":0,"cloudCover":0.98,"uvIndex":1,"visibility":6.927,"ozone":318.7,"solar":{"azimuth":226,"altitude":25,"dni":212.3,"ghi":97.5,"dhi":8.9,"etr":1357.8}},{"time":1601539200,"summary":"Possible Light Rain","icon":"rain","precipIntensity":0.0185,"precipProbability":0.54,"precipType":"rain","temperature":41.77,"apparentTemperature":38.79,"dewPoint":33.64,"humidity":0.73,"pressure":1011.5,"windSpeed":4.69,"windGust":4.9,"windBearing":352,"cloudCover":0.99,"uvIndex":1,"visibility":7.521,"ozone":319,"solar":{"azimuth":240,"altitude":17,"dni":180.6,"ghi":59,"dhi":5.4,"etr":1357.8}},{"time":1601542800,"summary":"Possible Light Rain","icon":"rain","precipIntensity":0.0169,"precipProbability":0.52,"precipType":"rain","temperature":41.74,"apparentTemperature":39,"dewPoint":34.06,"humidity":0.74,"pressure":1011.9,"windSpeed":4.38,"windGust":4.45,"windBearing":346,"cloudCover":0.99,"uvIndex":0,"visibility":8.097,"ozone":318.8,"solar":{"azimuth":253,"altitude":9,"dni":128.3,"ghi":21.6,"dhi":2,"etr":1357.9}},{"time":1601546400,"summary":"Possible Light Rain","icon":"rain","precipIntensity":0.0147,"precipProbability":0.49,"precipType":"rain","temperature":41.12,"apparentTemperature":38.35,"dewPoint":34.33,"humidity":0.77,"pressure":1012.5,"windSpeed":4.31,"windGust":5.22,"windBearing":348,"cloudCover":0.99,"uvIndex":0,"visibility":8.469,"ozone":318},{"time":1601550000,"summary":"Possible Light Rain","icon":"rain","precipIntensity":0.0125,"precipProbability":0.45,"precipType":"rain","temperature":40.39,"apparentTemperature":37.03,"dewPoint":34.2,"humidity":0.78,"pressure":1013.2,"windSpeed":4.86,"windGust":7.61,"windBearing":348,"cloudCover":0.99,"uvIndex":0,"visibility":8.815,"ozone":316.6},{"time":1601553600,"summary":"Possible Light Rain","icon":"rain","precipIntensity":0.0115,"precipProbability":0.43,"precipType":"rain","temperature":39.73,"apparentTemperature":36.05,"dewPoint":34.13,"humidity":0.8,"pressure":1013.7,"windSpeed":5.13,"windGust":9.58,"windBearing":346,"cloudCover":0.99,"uvIndex":0,"visibility":8.941,"ozone":315.7},{"time":1601557200,"summary":"Possible Light Rain","icon":"rain","precipIntensity":0.0134,"precipProbability":0.51,"precipType":"rain","temperature":39.03,"apparentTemperature":35.09,"dewPoint":34.03,"humidity":0.82,"pressure":1013.9,"windSpeed":5.32,"windGust":10.59,"windBearing":325,"cloudCover":0.99,"uvIndex":0,"visibility":8.779,"ozone":315.1},{"time":1601560800,"summary":"Possible Light Rain","icon":"rain","precipIntensity":0.0158,"precipProbability":0.58,"precipType":"rain","temperature":38.41,"apparentTemperature":34.83,"dewPoint":34.33,"humidity":0.85,"pressure":1014.1,"windSpeed":4.73,"windGust":6.92,"windBearing":312,"cloudCover":1,"uvIndex":0,"visibility":6.108,"ozone":314.7}],\n      startHour = undefined,\n      latitude = 51.9729,\n      longitude = 113.4097,\n      forecastTime = 1601526382,\n      tz_offset = 9,\n      units = "us",\n      unitsList = {"pressure":"mb","distance":"mi","speed":"mph","length":"in"},\n      language = "en",\n      timeFormat = "12",\n      languageReversed = false,\n      conditions = {"clear":"clear","light-clouds":"partly cloudy","heavy-clouds":"overcast","medium-rain":"rain","very-light-rain":"drizzle","light-rain":"light rain","heavy-rain":"heavy rain","medium-sleet":"sleet","very-light-sleet":"light sleet","light-sleet":"light sleet","heavy-sleet":"heavy sleet","medium-snow":"snow","very-light-snow":"flurries","light-snow":"light snow","heavy-snow":"heavy snow"},\n      cityName = "",\n      cityNameOnly = false;\n  </script>\n\n  <script type="text/javascript" src="/dist/js/daytwo.js"></script>\n\n</body>\n</html>\n'
#     # result.content = b'<!doctype html>\n<html lang="en">\n<head>\n  <meta charset="utf-8" lang="en">\n  <meta name="apple-itunes-app" content="app-id=517329357, affiliate-data=darkskynet">\n\n  <title>Dark Sky - Thursday, Oct 1st, 2020</title>\n\n  <script async src="//storage.googleapis.com/outfox/dnt_min.js"></script>\n\n  <link href=\'https://fonts.googleapis.com/css?family=Lato:300,400,700,900\' rel=\'stylesheet\' type=\'text/css\'>\n\n  <link rel="stylesheet" href="https://darksky.net/css/lib/selectric.css">\n  <link type="text/css" href="https://darksky.net/dist/css/styletwo.min.css" rel="stylesheet">\n  \n</head>\n\n<body class="day">\n\n  <section>\n\n  <nav>\n    <div class="inner">\n      <a class="logo" href="/">\n        <img src="/images/darkskylogo.png" alt="Dark Sky Logo"><span style="position: relative; top: -10px;">Dark Sky by Apple</span>\n      </a>\n      <a href="/app" class="headerAppLink">\n        <span id="phone-icon"><img src="/images/mobile-app-icon.png" alt="Smartphone Icon"></span>App\n      </a>\n      <a href="/maps">\n        Maps\n      </a>\n      <a href="/dev">\n        Dark Sky API\n      </a>\n      <a href="/help/website">\n        Help\n      </a>\n    </div>\n  </nav>\n</section>\n  <!-- views/partials/header.ejs -->\n\n<div id="header">\n  <a class="backToForecast" href="/forecast/51.9729,113.4097/us12/en">\xe2\x86\x90 Go Back</a>\n\n  <form id="searchForm">\n    <a class="currentLocationButton" style="display:none">\n      <img width="16" height="16" src="/images/current-location.png" alt="Current Location Button">\n    </a>\n\n    <input type="text" value="">\n\n    <a class="searchButton">\n      <img width="16" height="16" src="/images/search.png" alt="Search Button">\n    </a>\n\n    <div id="savedLocations">\n      <div class="autocomplete__container" style="margin: 20px; margin-bottom: 5px; display: none; overflow: hidden;">\n        <div class="autocomplete__results__container" id="autocomplete__results__container"></div>\n      </div>\n      <div class="inner"></div>\n    </div>\n    \n  </form>\n\n  <div class="options">\n    <select class="units">\n      <option value="us">\xcb\x9aF,&nbsp;mph</option>\n      <option value="si">\xcb\x9aC,&nbsp;m/s</option>\n      <option value="ca">\xcb\x9aC,&nbsp;km/h</option>\n      <option value="uk2">\xcb\x9aC,&nbsp;mph</option>\n    </select>\n\n    <select class="language">\n      <option value="de">Deutsch</option>\n      <option value="en">English</option>\n      <option value="es">Espa\xc3\xb1ol</option>\n      <option value="fr">Fran\xc3\xa7ais</option>\n      <option value="it">Italiano</option>\n      <option value="nl">Nederlands</option>\n      <option value="tr">T\xc3\xbcrk</option>\n      <option value="ar">\xd8\xb9\xd8\xb1\xd8\xa8\xd9\x8a</option>\n      <option value="zh">\xe4\xb8\xad\xe6\x96\x87</option>\n      <option value="zh-tw">\xe7\xb9\x81\xe9\xab\x94\xe4\xb8\xad\xe6\x96\x87</option>\n      <option value="ja">\xe6\x97\xa5\xe6\x9c\xac\xe8\xaa\x9e</option>\n      <option value="x-pig-latin">Pig Latin</option>\n    </select>\n  </div>\n\n</div>\n\n  <div id="main" class="center">\n\n    <div class="dayDetails center">\n\n      <div class="title">\n        \n        <a class="prev day swip" href="/details/51.9729,113.4097/2020-9-30/us12/en" rel="nofollow">\xe2\x86\x90 Wednesday, Sep 30th</a>\n        <div class="date">Thursday, Oct 1st, 2020</div>\n        <a class="next day swap" href="/details/51.9729,113.4097/2020-10-2/us12/en" rel="nofollow">Friday, Oct 2nd \xe2\x86\x92</a>\n      </div>\n\n      \n      <p id="summary">Light rain throughout the&nbsp;day.</p>\n\n      <div class="dayExtras">\n        <div class="highLowTemp swip">\n          <span class="highTemp swip">\n            <span class="temp">32\xcb\x9a</span>\n            <span class="time">4am</span>\n          </span>\n          \n          <span class="arrow">\xe2\x86\x92</span>\n          \n          <span class="lowTemp swap">\n            <span class="temp">44\xcb\x9a</span>\n            <span class="time">1pm</span>\n          </span>\n        </div>\n\n        <div class="sunTimes">\n          \n          <span class="sunrise swip">\n            <img src="/images/sunrise.png" width="28" height="30" />\n            <span class="time">7:29am</span>\n          </span>\n\n          \n\n          \n          <span class="sunset swap">\n            <img src="/images/sunset.png" width="28" height="30" />\n            <span class="time">7:05pm</span>\n          </span>\n          \n        </div>\n\n        <div class="precipAccum swap">\n          <span class="label swip">Rain</span>\n          <span class="val swap">\n          \n            <span class="num swip">0.2</span>\n            <span class="unit swap">in</span>\n          </span>\n        </div>\n      </div>\n    </div>\n\n    <div id="slider">\n      <div class="handle">\n        <div class="line"></div>\n      </div>\n    </div>\n\n    <div class="scroll-container">\n      <div id="timeline" class="timeline_container">\n        <div class="timeline">\n          <div class="stripes"></div>\n          <div class="hour_ticks"></div>\n          <div class="hours"></div>\n          <div class="temps"></div>\n        </div>\n      </div>\n    </div>\n\n    <div id="currentDetails">\n      <div class="section">\n        <div class="temperature">\n          <span class="label swip">Temp:</span>\n          <span class="val swap">\n            <span class="num">43</span><span class="unit">\xcb\x9a</span>\n        </div>\n        <div class="precipProbability">\n          <span class="label swip">Precip:</span>\n          <span class="val swap">\n            <span class="num swip">41</span><span class="unit swap">%</span>\n          </span>\n        </div>\n      </div>\n\n      <div class="section">\n        <div class="wind">\n          <span class="label swip">Wind:</span>\n          <span class="val swap">\n            <span class="num swip">6</span>\n            <span class="unit swap">mph</span>\n            \n            <span class="direction" title="S" style="display:inline-block;-ms-transform:rotate(181deg);-webkit-transform:rotate(181deg);transform:rotate(181deg);">\xe2\x86\x91</span>\n          </span>\n        </div>\n        <div class="pressure">\n          <span class="label swip">Pressure:</span>\n          <span class="val swap">\n            <span class="num swip">1011</span>\n            <span class="unit swap">mb</span>\n          </span>\n        </div>\n      </div>\n\n      <div class="section">\n        <div class="humidity">\n          <span class="label swip">Humidity:</span>\n          <span class="val swap">\n            <span class="num swip">67</span><span class="unit swap">%</span>\n          </span>\n        </div>\n        <div class="dew_point">\n          <span class="label swip">Dew Pt:</span>\n          <span class="val swap">\n            <span class="num">33</span><span class="unit">\xcb\x9a</span>\n          </span>\n        </div>\n      </div>\n\n      <div class="section">\n        <div class="uv_index">\n          <span class="label swip">UV Index:</span>\n          <span class="val swap">\n            <span class="num">2</span>\n          </span>\n        </div>\n        <div class="visibility">\n          <span class="label swip">Visibility:</span>\n          <span class="val swap">\n            <span class="num swip">10+</span>\n            <span class="unit swap">mi</span>\n          </span>\n        </div>\n      </div>\n    </div>\n\n      <div class="plotContainer">\n        <div class="plotLabel">Temperature / <span style="opacity:0.5">Feels Like</span></div>\n        <div id="temperature_graph" class="plot"></div>\n      </div>\n\n      <div class="plotContainer">\n        <div class="plotLabel">Precip Probability</div>\n        <div id="precip_graph" class="plot"></div>\n      </div>\n\n      <div class="plotContainer">\n        <div class="plotLabel">Humidity</div>\n        <div id="humidity_test" class="plot"></div>\n      </div>\n\n      <div class="plotContainer">\n        <div class="plotLabel">Dew Point</div>\n        <div id="dew_point_graph" class="plot"></div>\n      </div>\n\n      <!-- <div class="plotContainer">\n        <div class="plotLabel">Humidity / <span style="opacity:0.5">Dew Point</span></div>\n        <div id="humidity_graph" class="plot"></div>\n      </div> -->\n\n      <div class="plotContainer">\n        <div class="plotLabel">Wind</div>\n        <div id="wind_graph" class="plot"></div>\n      </div>\n\n      <div class="plotContainer">\n        <div class="plotLabel">Atmospheric Pressure</div>\n        <div id="pressure_graph" class="plot"></div>\n      </div>\n\n      <div class="plotContainer">\n        <div class="plotLabel">UV Index</div>\n        <div id="uv_graph" class="plot"></div>\n      </div>\n\n      <div class="plotContainer">\n        <div class="plotLabel">Visibility</div>\n        <div id="visibility_graph" class="plot"></div>\n      </div>\n    </div>\n  </div>\n\n\n  <div id="footer">\n\n  \n\n  <div id="units-container">\n    <div class="options">\n      <select class="units">\n        <option value="us">\xcb\x9aF,&nbsp;mph</option>\n        <option value="si">\xcb\x9aC,&nbsp;m/s</option>\n        <option value="ca">\xcb\x9aC,&nbsp;km/h</option>\n        <option value="uk2">\xcb\x9aC,&nbsp;mph</option>\n      </select>\n\n      <select class="language">\n        <option value="de">Deutsch</option>\n        <option value="en">English</option>\n        <option value="es">Espa\xc3\xb1ol</option>\n        <option value="fr">Fran\xc3\xa7ais</option>\n        <option value="it">Italiano</option>\n        <option value="nl">Nederlands</option>\n        <option value="tr">T\xc3\xbcrk</option>\n        <option value="ar">\xd8\xb9\xd8\xb1\xd8\xa8\xd9\x8a</option>\n        <option value="zh">\xe4\xb8\xad\xe6\x96\x87</option>\n        <option value="ja">\xe6\x97\xa5\xe6\x9c\xac\xe8\xaa\x9e</option>\n        <option value="x-pig-latin">Pig Latin</option>\n      </select>\n    </div>\n  </div>\n\n  \n  <div id="footer-section-container">\n    <div class="footer-section contribute">\n      <p><img alt="Dark Sky Logo" src="/images/darkskylogo.png"> Dark Sky</p>\n    </div>\n    <div class="footer-section">\n      <ul>\n        <li><a href="/app">iOS app</a></li>\n        <li><a href="/tos">Terms of Service</a></li>\n        <li><a href="/attribution">Attribution</a></li>\n        <li><a href="https://blog.darksky.net/">Blog</a></li>\n        <li><a href="/help">Help</a></li>\n        <li><a href="/contact">Contact</a></li>\n        <li><a href="/privacy">Privacy</a></li>\n      </ul>\n    </div>\n  </div>\n\n  <div class="copyright">\n    <span class="copyright">Copyright &copy; 2020 <a href="https://apple.com">Apple Inc.</a> All rights reserved.&nbsp;</span>\n  </div>\n</div>\n\n  <script>\n  var hours = [{"time":1601478000,"summary":"Partly Cloudy","icon":"partly-cloudy-night","precipIntensity":0.0002,"precipProbability":0.03,"precipType":"rain","temperature":36.09,"apparentTemperature":32.78,"dewPoint":30.59,"humidity":0.8,"pressure":1012.9,"windSpeed":4.02,"windGust":4.27,"windBearing":1,"cloudCover":0.38,"uvIndex":0,"visibility":10,"ozone":311.4},{"time":1601481600,"summary":"Partly Cloudy","icon":"partly-cloudy-night","precipIntensity":0,"precipProbability":0,"temperature":35.12,"apparentTemperature":31.89,"dewPoint":30.7,"humidity":0.84,"pressure":1012.8,"windSpeed":3.8,"windGust":4.17,"windBearing":3,"cloudCover":0.35,"uvIndex":0,"visibility":10,"ozone":309.3},{"time":1601485200,"summary":"Partly Cloudy","icon":"partly-cloudy-night","precipIntensity":0,"precipProbability":0,"temperature":34.49,"apparentTemperature":31.04,"dewPoint":30.56,"humidity":0.85,"pressure":1012.6,"windSpeed":3.91,"windGust":4.63,"windBearing":1,"cloudCover":0.4,"uvIndex":0,"visibility":10,"ozone":307.6},{"time":1601488800,"summary":"Partly Cloudy","icon":"partly-cloudy-night","precipIntensity":0,"precipProbability":0,"temperature":33.68,"apparentTemperature":30.09,"dewPoint":29.93,"humidity":0.86,"pressure":1012.3,"windSpeed":3.92,"windGust":4.94,"windBearing":2,"cloudCover":0.45,"uvIndex":0,"visibility":10,"ozone":307.8},{"time":1601492400,"summary":"Partly Cloudy","icon":"partly-cloudy-night","precipIntensity":0,"precipProbability":0,"temperature":32.96,"apparentTemperature":29.24,"dewPoint":29.32,"humidity":0.86,"pressure":1012.4,"windSpeed":3.95,"windGust":5.27,"windBearing":3,"cloudCover":0.58,"uvIndex":0,"visibility":10,"ozone":309.9},{"time":1601496000,"summary":"Mostly Cloudy","icon":"partly-cloudy-night","precipIntensity":0,"precipProbability":0,"temperature":32.44,"apparentTemperature":28.34,"dewPoint":28.38,"humidity":0.85,"pressure":1012.9,"windSpeed":4.23,"windGust":5.7,"windBearing":3,"cloudCover":0.73,"uvIndex":0,"visibility":10,"ozone":313.2},{"time":1601499600,"summary":"Mostly Cloudy","icon":"partly-cloudy-night","precipIntensity":0,"precipProbability":0,"temperature":33.15,"apparentTemperature":28.99,"dewPoint":28.24,"humidity":0.82,"pressure":1012.5,"windSpeed":4.41,"windGust":6.43,"windBearing":6,"cloudCover":0.67,"uvIndex":0,"visibility":10,"ozone":315.5},{"time":1601503200,"summary":"Partly Cloudy","icon":"partly-cloudy-night","precipIntensity":0,"precipProbability":0,"temperature":32.99,"apparentTemperature":28.8,"dewPoint":27.19,"humidity":0.79,"pressure":1013.1,"windSpeed":4.41,"windGust":7.72,"windBearing":5,"cloudCover":0.5,"uvIndex":0,"visibility":10,"ozone":315.5},{"time":1601506800,"summary":"Partly Cloudy","icon":"partly-cloudy-day","precipIntensity":0.0009,"precipProbability":0.08,"precipType":"rain","temperature":32.85,"apparentTemperature":28.36,"dewPoint":26.62,"humidity":0.78,"pressure":1013.5,"windSpeed":4.69,"windGust":9.33,"windBearing":5,"cloudCover":0.55,"uvIndex":0,"visibility":10,"ozone":314.6,"solar":{"azimuth":101,"altitude":4,"dni":209.1,"ghi":16.7,"dhi":1.5,"etr":1357.6}},{"time":1601510400,"summary":"Partly Cloudy","icon":"partly-cloudy-day","precipIntensity":0.0049,"precipProbability":0.18,"precipType":"rain","temperature":34.59,"apparentTemperature":31.36,"dewPoint":27.73,"humidity":0.76,"pressure":1013.5,"windSpeed":3.72,"windGust":5.96,"windBearing":359,"cloudCover":0.58,"uvIndex":0,"visibility":10,"ozone":314.1,"solar":{"azimuth":113,"altitude":13,"dni":411.4,"ghi":101.6,"dhi":9.2,"etr":1357.6}},{"time":1601514000,"summary":"Mostly Cloudy","icon":"partly-cloudy-day","precipIntensity":0.0063,"precipProbability":0.23,"precipType":"rain","temperature":36.57,"apparentTemperature":34,"dewPoint":28.83,"humidity":0.73,"pressure":1013.2,"windSpeed":3.4,"windGust":7.7,"windBearing":355,"cloudCover":0.87,"uvIndex":1,"visibility":10,"ozone":314.4,"solar":{"azimuth":126,"altitude":21,"dni":295.1,"ghi":116.3,"dhi":10.6,"etr":1357.6}},{"time":1601517600,"summary":"Possible Drizzle","icon":"rain","precipIntensity":0.0075,"precipProbability":0.27,"precipType":"rain","temperature":38.78,"apparentTemperature":34.94,"dewPoint":30.06,"humidity":0.71,"pressure":1012.7,"windSpeed":5.12,"windGust":10.1,"windBearing":353,"cloudCover":1,"uvIndex":2,"visibility":10,"ozone":315.1,"solar":{"azimuth":141,"altitude":28,"dni":203,"ghi":103.7,"dhi":9.4,"etr":1357.7}},{"time":1601521200,"summary":"Possible Light Rain","icon":"rain","precipIntensity":0.0092,"precipProbability":0.32,"precipType":"rain","temperature":40.49,"apparentTemperature":36.35,"dewPoint":31.73,"humidity":0.71,"pressure":1012.2,"windSpeed":5.99,"windGust":11.43,"windBearing":354,"cloudCover":1,"uvIndex":2,"visibility":10,"ozone":315.8,"solar":{"azimuth":157,"altitude":32,"dni":212.4,"ghi":125.2,"dhi":11.4,"etr":1357.7}},{"time":1601524800,"summary":"Possible Light Rain","icon":"rain","precipIntensity":0.0116,"precipProbability":0.38,"precipType":"rain","temperature":42.4,"apparentTemperature":38.53,"dewPoint":32.75,"humidity":0.68,"pressure":1011.6,"windSpeed":6.13,"windGust":10.72,"windBearing":359,"cloudCover":1,"uvIndex":2,"visibility":10,"ozone":316.7,"solar":{"azimuth":175,"altitude":35,"dni":216.1,"ghi":134.9,"dhi":12.3,"etr":1357.7}},{"time":1601528400,"summary":"Possible Light Rain","icon":"rain","precipIntensity":0.0145,"precipProbability":0.46,"precipType":"rain","temperature":43.78,"apparentTemperature":40.46,"dewPoint":33.52,"humidity":0.67,"pressure":1011.2,"windSpeed":5.66,"windGust":8.96,"windBearing":3,"cloudCover":1,"uvIndex":2,"visibility":10,"ozone":317.6,"solar":{"azimuth":193,"altitude":34,"dni":215,"ghi":131.8,"dhi":12,"etr":1357.7}},{"time":1601532000,"summary":"Possible Light Rain","icon":"rain","precipIntensity":0.0195,"precipProbability":0.56,"precipType":"rain","temperature":41.62,"apparentTemperature":38.04,"dewPoint":33.15,"humidity":0.72,"pressure":1011,"windSpeed":5.47,"windGust":8.8,"windBearing":4,"cloudCover":0.99,"uvIndex":2,"visibility":7.015,"ozone":318.3,"solar":{"azimuth":211,"altitude":30,"dni":220.2,"ghi":122.6,"dhi":11.1,"etr":1357.8}},{"time":1601535600,"summary":"Possible Light Rain","icon":"rain","precipIntensity":0.0198,"precipProbability":0.56,"precipType":"rain","temperature":41.61,"apparentTemperature":38.26,"dewPoint":33.48,"humidity":0.73,"pressure":1011.2,"windSpeed":5.14,"windGust":6.96,"windBearing":0,"cloudCover":0.98,"uvIndex":1,"visibility":6.927,"ozone":318.7,"solar":{"azimuth":226,"altitude":25,"dni":212.3,"ghi":97.5,"dhi":8.9,"etr":1357.8}},{"time":1601539200,"summary":"Possible Light Rain","icon":"rain","precipIntensity":0.0185,"precipProbability":0.54,"precipType":"rain","temperature":41.77,"apparentTemperature":38.79,"dewPoint":33.64,"humidity":0.73,"pressure":1011.5,"windSpeed":4.69,"windGust":4.9,"windBearing":352,"cloudCover":0.99,"uvIndex":1,"visibility":7.521,"ozone":319,"solar":{"azimuth":240,"altitude":17,"dni":180.6,"ghi":59,"dhi":5.4,"etr":1357.8}},{"time":1601542800,"summary":"Possible Light Rain","icon":"rain","precipIntensity":0.0169,"precipProbability":0.52,"precipType":"rain","temperature":41.74,"apparentTemperature":39,"dewPoint":34.06,"humidity":0.74,"pressure":1011.9,"windSpeed":4.38,"windGust":4.45,"windBearing":346,"cloudCover":0.99,"uvIndex":0,"visibility":8.097,"ozone":318.8,"solar":{"azimuth":253,"altitude":9,"dni":128.3,"ghi":21.6,"dhi":2,"etr":1357.9}},{"time":1601546400,"summary":"Possible Light Rain","icon":"rain","precipIntensity":0.0147,"precipProbability":0.49,"precipType":"rain","temperature":41.12,"apparentTemperature":38.35,"dewPoint":34.33,"humidity":0.77,"pressure":1012.5,"windSpeed":4.31,"windGust":5.22,"windBearing":348,"cloudCover":0.99,"uvIndex":0,"visibility":8.469,"ozone":318},{"time":1601550000,"summary":"Possible Light Rain","icon":"rain","precipIntensity":0.0125,"precipProbability":0.45,"precipType":"rain","temperature":40.39,"apparentTemperature":37.03,"dewPoint":34.2,"humidity":0.78,"pressure":1013.2,"windSpeed":4.86,"windGust":7.61,"windBearing":348,"cloudCover":0.99,"uvIndex":0,"visibility":8.815,"ozone":316.6},{"time":1601553600,"summary":"Possible Light Rain","icon":"rain","precipIntensity":0.0115,"precipProbability":0.43,"precipType":"rain","temperature":39.73,"apparentTemperature":36.05,"dewPoint":34.13,"humidity":0.8,"pressure":1013.7,"windSpeed":5.13,"windGust":9.58,"windBearing":346,"cloudCover":0.99,"uvIndex":0,"visibility":8.941,"ozone":315.7},{"time":1601557200,"summary":"Possible Light Rain","icon":"rain","precipIntensity":0.0134,"precipProbability":0.51,"precipType":"rain","temperature":39.03,"apparentTemperature":35.09,"dewPoint":34.03,"humidity":0.82,"pressure":1013.9,"windSpeed":5.32,"windGust":10.59,"windBearing":325,"cloudCover":0.99,"uvIndex":0,"visibility":8.779,"ozone":315.1},{"time":1601560800,"summary":"Possible Light Rain","icon":"rain","precipIntensity":0.0158,"precipProbability":0.58,"precipType":"rain","temperature":38.41,"apparentTemperature":34.83,"dewPoint":34.33,"humidity":0.85,"pressure":1014.1,"windSpeed":4.73,"windGust":6.92,"windBearing":312,"cloudCover":1,"uvIndex":0,"visibility":6.108,"ozone":314.7}],\n      startHour = undefined,\n      latitude = 51.9729,\n      longitude = 113.4097,\n      forecastTime = 1601526382,\n      tz_offset = 9,\n      units = "us",\n      unitsList = {"pressure":"mb","distance":"mi","speed":"mph","length":"in"},\n      language = "en",\n      timeFormat = "12",\n      languageReversed = false,\n      conditions = {"clear":"clear","light-clouds":"partly cloudy","heavy-clouds":"overcast","medium-rain":"rain","very-light-rain":"drizzle","light-rain":"light rain","heavy-rain":"heavy rain","medium-sleet":"sleet","very-light-sleet":"light sleet","light-sleet":"light sleet","heavy-sleet":"heavy sleet","medium-snow":"snow","very-light-snow":"flurries","light-snow":"light snow","heavy-snow":"heavy snow"},\n      cityName = "",\n      cityNameOnly = false;\n  </script>\n\n  <script type="text/javascript" src="/dist/js/daytwo.js"></script>\n\n</body>\n</html>\n'
#     return result


class WeatherOneDayTestCase(unittest.TestCase):

    def setUp(self) -> None:
        patch(target='model.psql_db', new=memory_db)
        memory_db.bind(MODELS, bind_refs=False, bind_backrefs=False)
        if memory_db.is_closed():
            memory_db.connect()
        memory_db.create_tables(MODELS)
        weather.Nominatim.geocode = Mock(return_value=location_t)
        weather.requests.get = Mock(return_value=return_responce)
        self.date = datetime(year=2020, month=10, day=1)
        self.weather_one = weather.WeatherOneDay(city='Чита', date=self.date, local=False)

    def tearDown(self) -> None:
        memory_db.drop_tables(MODELS)
        memory_db.close()

    def test_init(self):
        self.assertEqual(self.weather_one.city, 'Чита', 'Должна быть "Чита"')

    def test_ident_file_name(self):
        result = self.weather_one._ident_file_name('52.033409', '113.500893')
        self.assertEqual(result, '52_033409-113_500893-01.10.2020.png',
                         'Должна быть "52_033409-113_500893-01.10.2020.png"')

    def test_from_fahrenheit_to_village(self):
        grad_faringate = [32, 43, 54]
        grad_celsii = [0, 6, 12]
        for index, grad in enumerate(grad_faringate):
            result = self.weather_one._from_fahrenheit_to_village(str(grad))
            self.assertEqual(grad_celsii[index], result, f'Должна быть {grad_celsii[index]}')

    def test_get_weather_inet(self):
        result = self.weather_one._get_weather_inet()
        self.assertEqual(result.cloudiness, 'Light rain and  throughout the\xa0day.',
                         'Должна быть "Light rain and  throughout the\xa0day."')

    def test_str_repr(self):
        ret_str = str(self.weather_one)
        ret_repr = repr(self.weather_one)
        self.assertEqual(ret_str, 'Get weather in Чита for 2020-10-01 00:00:00',
                         "Должна быть 'Get weather in Чита for 2020-10-01 00:00:00'")
        self.assertEqual(ret_repr, 'WeatherOneDay(city=Чита,date=2020-10-01 00:00:00)',
                         "Должна быть 'WeatherOneDay(city=Чита,date=2020-10-01 00:00:00)'")

    def test_bad_town_local(self):
        with self.assertRaises(weather.ExceptionWeatherError, msg='Not Raise ExceptionWeatherError') as exc:
            weather_bad = weather.WeatherOneDay(city='Москва', date=self.date, local=True)

    def test_get_weather_db_first(self):
        result = self.weather_one.get_weather_db()
        self.assertIsNone(result, msg='result Must be None')

    def test_run(self):
        self.weather_one.run()
        cursor1 = memory_db.execute_sql("select count('*') from weather_report")
        w_res = cursor1.fetchall()
        self.assertEqual(w_res[0][0], 1, 'Должна быть 1')
        self.assertEqual(self.weather_one.result.town_name, 'Чита', 'Должна быть 1')
        result = self.weather_one.get_weather_db()
        self.assertEqual(self.weather_one.result, result, 'Должны быть равны')

        date = datetime(year=2020, month=10, day=2)
        weather_two = weather.WeatherOneDay(city='Чита', date=date, local=True)

        with self.assertRaises(weather.ExceptionWeatherError, msg='Not Raise ExceptionWeatherError'):
            weather_two.run()
        with self.assertRaises(weather.ExceptionWeatherError, msg='Not Raise ExceptionWeatherError'):
            weather_three = weather.WeatherOneDay(city='Москва', date=date, local=True)


if __name__ == '__main__':
    unittest.main()
