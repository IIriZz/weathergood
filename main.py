# -*- coding: utf-8 -*-


# Загрузка нужных библеотек
import sys
import requests
import sqlite3

from PyQt5 import uic
from pprint import pprint

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt, QPoint

from pymorphy2 import MorphAnalyzer

from datetime import datetime

from config import *


def hex_to_rgb(value):
    value = value.lstrip('#')
    lv = len(value)
    return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))

def rgb_to_hex(rgb):
    return '#%02x%02x%02x' % rgb


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('frame.ui', self)

        # Нужно, чтобы шрифт можно было выбирать до выбора цвета кнопок, фона и текста
        self.color = None
        self.font_color = None
        self.background_color = None

        # Много списков
        self.BUTTONS = [
            self.favouriteButton,
            self.searchButton,
            self.background_colorButton,
            self.colorButton,
            self.fontButton,
            self.font_colorButton
        ]

        self.RADIO_BUTTONS = [
            self.celsius_radioButton,
            self.kelvin_radioButton,
            self.fahrenheit_radioButton
        ]

        self.LABELS = [
            self.pressureLabel,
            self.visibilityLabel,
            self.wind_speedLabel,
            self.humidityLabel,
            self.city_nameLabel,
            self.degreesLabel,
            self.feels_likeLabel,
            self.weather_typeLabel,
            self.sunriseLabel,
            self.sunsetLabel
        ]

        self.DAYS_TEMP = [
            self.temp1_label,
            self.temp2_label,
            self.temp3_label,
            self.temp4_label,
            self.temp5_label,
            self.temp6_label,
            self.temp7_label
        ]

        self.DAYS = [
            self.day1_label,
            self.day2_label,
            self.day3_label,
            self.day4_label,
            self.day5_label,
            self.day6_label,
            self.day7_label
        ]

        self.IMAGES = [
            self.Image1,
            self.Image2,
            self.Image3,
            self.Image4,
            self.Image5,
            self.Image6,
            self.Image7
        ]

        self.setFixedSize(*SCREEN_SIZE)
        self.initUI()

        self.setWindowIcon(QIcon("img/weather.jpg"))
        self.setWindowTitle('Погода')
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        self.favouriteButton.hide()

        self.humidityImage.hide()
        self.wind_speedImage.hide()
        self.visibilityImage.hide()
        self.pressureImage.hide()

        for i in self.LABELS:
            i.hide()

        self.Image.hide()

        # Нужно, чтобы изначально были градусы Цельсия
        self.celsius_radioButton.setChecked(True)

    def initUI(self):
        self.searchButton.clicked.connect(self.get_weather_data)
        self.background_colorButton.clicked.connect(self.set_background_color)
        self.colorButton.clicked.connect(self.set_buttons_color)
        self.font_colorButton.clicked.connect(self.set_font_color)
        self.fontButton.clicked.connect(self.set_font)

        self.minButton.clicked.connect(self.showMinimized)
        self.exitButton.clicked.connect(self.close)

        self.favouriteButton.clicked.connect(self.add_to_f)

    # Поскольку window рамок нет, нужно переопределить методы mousePressEvent и mouseMoveEvent
    # Чтобы была возможность двигать окно
    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        delta = QPoint(event.globalPos() - self.oldPos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPos()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return:
            self.get_weather_data()
        elif event.key() == Qt.Key_Left:
            self.tabWidget.TabPosition(1)

    # Метод, который ищет погоду
    def get_weather_data(self):
        # self.city - название города, которое ввёл пользователь
        # name_city - название города, которое будет выводиться на экране
        morph = MorphAnalyzer()
        self.city = self.city_nameLine.text()
        name_city = morph.parse(self.city)[0]

        # Проверяет, в каких градусах измерять температуру
        if self.celsius_radioButton.isChecked():
            self.unit = 'metric'
            self.sign = '°C'
        elif self.kelvin_radioButton.isChecked():
            self.unit = 'standard'
            self.sign = 'K'
        elif self.fahrenheit_radioButton.isChecked():
            self.unit = 'imperial'
            self.sign = '°F'

        try:
            # Загружаем информацию о погоде в нужном городе, с помощью requests
            r = requests.get(
                f'https://api.openweathermap.org/data/2.5/weather?q={self.city}&appid={WEATHER_TOKEN}&units={self.unit}'
            )
            self.data = r.json()

            self.lat = self.data["coord"]["lat"]
            self.lon = self.data["coord"]["lon"]

            # Загружаем информацию о погоде на неделю в нужном городе, с помощью requests
            r2 = requests.get(
                f'https://api.openweathermap.org/data/2.5/onecall?lat={self.lat}&lon={self.lon}&appid={WEATHER_TOKEN}'
            )
            days_temp = []
            days = []
            images = []

            self.data2 = r2.json()
            for i in self.data2["daily"]:
                days_temp.append(round(i["temp"]["day"] - 273.15))

            for i in self.data2["daily"]:
                days.append(datetime.fromtimestamp(i["dt"]))

            for i in self.data2["daily"]:
                img = i["weather"][0]["main"]
                if img in WEATHER_TYPES:
                    wt = WEATHER_TYPES[img]
                    if wt == 'Ясно':
                        images.append(QPixmap('img/weather_icons/sun.jpg'))
                    elif wt == 'Облачно':
                        images.append(QPixmap('img/weather_icons/cloudy.jpg'))
                    elif wt == 'Дождь':
                        images.append(QPixmap('img/weather_icons/rainy.jpg'))
                    elif wt == 'Снег':
                        images.append(QPixmap('img/weather_icons/snowflake.jpg'))
                    elif wt == 'Гроза':
                        images.append(QPixmap('img/weather_icons/rain.jpg'))
                    elif wt == 'Туман':
                        images.append(QPixmap('img/weather_icons/fog.jpg'))

            weather_type = self.data["weather"][0]["main"]
            pprint(self.data)

            # В зависимости от типа погоды, выбераем соответствующую иконку
            if weather_type in WEATHER_TYPES:
                self.wt = WEATHER_TYPES[weather_type]
                if self.wt == 'Ясно':
                    self.image = QPixmap('img/weather_icons/sun.jpg')
                elif self.wt == 'Облачно':
                    self.image = QPixmap('img/weather_icons/cloudy.jpg')
                elif self.wt == 'Дождь':
                    self.image = QPixmap('img/weather_icons/rainy.jpg')
                elif self.wt == 'Снег':
                    self.image = QPixmap('img/weather_icons/snowflake.jpg')
                elif self.wt == 'Гроза':
                    self.image = QPixmap('img/weather_icons/rain.jpg')
                elif self.wt == 'Туман':
                    self.image = QPixmap('img/weather_icons/fog.jpg')

            # Переменные, содержащие температуру, давление, скорость ветра и т.д.
            temp = self.data["main"]["temp"]
            feels_like = self.data["main"]["feels_like"]
            pressure = self.data["main"]["pressure"]
            humidity = self.data["main"]["humidity"]
            wind_speed = self.data["wind"]["speed"]
            visibility = self.data["visibility"]

            self.sunrise = datetime.fromtimestamp(self.data["sys"]["sunrise"])
            self.sunset = datetime.fromtimestamp(self.data["sys"]["sunset"])

            # Выводит на экране нужную погоду
            self.city_nameLabel.setText(f'В {(name_city.inflect({"sing", "loct"}).word).capitalize()} сейчас:')
            self.degreesLabel.setText(f'{round(temp)}{self.sign}')
            self.feels_likeLabel.setText(f'Ощущается как {round(feels_like)}{self.sign}')
            self.weather_typeLabel.setText(f'{self.wt}')
            self.pressureLabel.setText(f'Давление {pressure} гПа')
            self.humidityLabel.setText(f'Влажность воздуха {humidity}%')
            if self.unit == 'imperial':
                self.wind_speedLabel.setText(f'Скорость ветра {wind_speed} миль в час')
            else:
                self.wind_speedLabel.setText(f'Скорость ветра {wind_speed} м/с')
            self.visibilityLabel.setText(f'Видимость {visibility // 1000} км')
            self.sunriseLabel.setText(f"{self.sunrise} - Время рассвета")
            self.sunsetLabel.setText(f"{self.sunset} - Время заката")

            # Выставляет нужные значения для прогноза на 7 дней
            count = 1
            for i in self.DAYS_TEMP:
                i.setText(f'    {days_temp[count]}°C')
                count += 1
            count = 1
            for i in self.DAYS:
                i.setText(f'{days[count]}')
                count += 1
            count = 1
            for i in self.IMAGES:
                i.setPixmap(images[count])
                count += 1

            self.errorLabel.hide()

            self.Image.setPixmap(self.image)

            self.humidityImage.setPixmap(QPixmap('img/info_icons/drop.jpg'))
            self.wind_speedImage.setPixmap(QPixmap('img/info_icons/windy.jpg'))
            self.visibilityImage.setPixmap(QPixmap('img/info_icons/eye.jpg'))
            self.pressureImage.setPixmap(QPixmap('img/info_icons/pressure.jpg'))

            self.Image.show()

            self.humidityImage.show()
            self.wind_speedImage.show()
            self.visibilityImage.show()
            self.pressureImage.show()

            for i in self.DAYS:
                i.show()
            for i in self.DAYS_TEMP:
                i.show()
            for i in self.LABELS:
                i.show()

            self.favouriteButton.show()

        # Если нет интернета
        except requests.ConnectionError:
            self.errorLabel.setText("Проверьте интернет \nсоединение!")
            for i in self.LABELS:
                i.hide()
            for i in self.DAYS:
                i.hide()
            for i in self.DAYS_TEMP:
                i.hide()
            for i in self.IMAGES:
                i.hide()

            self.Image.hide()

            self.favouriteButton.hide()

            self.forecastLabel.hide()
            self.humidityImage.hide()
            self.wind_speedImage.hide()
            self.visibilityImage.hide()
            self.pressureImage.hide()

            self.errorLabel.show()
        # Если неправильное название города
        except Exception as err:
            print(err)
            self.errorLabel.setText("Проверьте название \nгорода!")

            for i in self.LABELS:
                i.hide()
            for i in self.DAYS:
                i.hide()
            for i in self.DAYS_TEMP:
                i.hide()
            for i in self.IMAGES:
                i.hide()

            self.Image.hide()

            self.favouriteButton.hide()

            self.forecastLabel.hide()
            self.humidityImage.hide()
            self.wind_speedImage.hide()
            self.visibilityImage.hide()
            self.pressureImage.hide()

            self.errorLabel.show()

    def add_to_f(self):
        from PyQt5.QtSql import QSqlDatabase, QSqlTableModel

        con = sqlite3.connect('f_db.sqlite')

        cur = con.cursor()
        cur.execute('CREATE TABLE IF NOT EXISTS cities (Город TEXT, Температура TEXT)')


        res = cur.execute('''SELECT * FROM cities
        WHERE Город = ?''', (self.city,)).fetchone()
        if res is None:
            cur.execute(f'''INSERT INTO cities 
            VALUES ('{self.city}', '{str(round(self.data["main"]["temp"])) + self.sign}')''')

        if self.unit == 'metric':
            cur.execute('''UPDATE cities
            SET Температура = CAST(CAST(Температура AS INT) - 273 AS TEXT) || '°C'
            WHERE Температура like "%K"''')
            cur.execute('''UPDATE cities
            SET Температура = CAST(TRUNC(CAST(Температура AS INT) - 32) * 5 / 9 AS TEXT) || '°C'
            WHERE Температура like "%°F"''')
        elif self.unit == 'standard':
            cur.execute('''UPDATE cities
            SET Температура = CAST(TRUNC(CAST(Температура AS INT) + 273) AS TEXT) || 'K'
            WHERE Температура like "%°C"''')
            cur.execute('''UPDATE cities
            SET Температура = CAST(TRUNC((CAST(Температура AS INT) + 459) / 1.8) AS TEXT) || 'K'
            WHERE Температура like "%°F"''')
        elif self.unit == 'imperial':
            cur.execute('''UPDATE cities
            SET Температура = CAST(TRUNC(CAST(Температура AS INT) * 1.8 + 32) AS TEXT) || '°F'
            WHERE Температура like "%°C"''')
            cur.execute('''UPDATE cities
            SET Температура = CAST(TRUNC(CAST(Температура AS INT) * 1.8 - 459) AS TEXT) || '°F'
            WHERE Температура like "%K"''')

        con.commit()
        con.close()

        # Зададим тип базы данных
        db = QSqlDatabase.addDatabase('QSQLITE')
        # Укажем имя базы данных
        db.setDatabaseName('f_db.sqlite')
        # И откроем подключение
        db.open()

        model = QSqlTableModel(self, db)
        model.setTable('cities')
        model.select()

        # Для отображения данных на виджете
        # свяжем его и нашу модель данных
        self.FavoriteTableView.setModel(model)

    # Метод, устанавливающий цвет для фона
    def set_background_color(self):
        self.background_color = QtWidgets.QColorDialog.getColor()
        if self.background_color.isValid():
            self.tabWidget.setStyleSheet("QTabWidget::pane {border: 1px; border-radius: 5px;"
                                         f"background: {self.background_color.name()}" + '}'
                                         'QTabBar::tab {'
                                        f'background: {self.background_color.name()}; '
                                         'min-width: 40ex;'
                                         'min-height: 10ex;'
                                         'margin-left: 5px;'
                                         'margin-bottom: 5px;'
                                         'border-radius: 5px;'
                                         'left: -5px;'
                                         'color: white}'
                                         'QTabBar::tab:selected {'
                                        f'background: {rgb_to_hex(tuple(i + 30 for i in list(hex_to_rgb(self.background_color.name()))))}' + '}'
                                         'QLabel {color: black;}')
            self.frame.setStyleSheet('QFrame {'
                                    f'background-color: {self.background_color.name()};'
                                     'border-radius: 5px}')
            self.frame_2.setStyleSheet('QFrame {'
                                       f'background-color: black;'
                                       'border-radius: 5px}')

    # Метод, устанавливающий цвет для кнопок
    def set_buttons_color(self):
        self.color = QtWidgets.QColorDialog.getColor()
        if self.color.isValid():
            for i in self.BUTTONS:
                i.setStyleSheet("QPushButton {"
                                f"background-color: {self.color.name()};"
                                f"color: white; "
                                "border-radius: 5px;}"
                                "QPushButton::hover {"
                               f"background-color: {rgb_to_hex(tuple(i - 20 for i in list(hex_to_rgb(self.color.name()))))};"
                               f"color: white;"
                                "border-radius: 5px;"
                                "min-width: 40ex;"
                                "min-height: 10ex;}")

    def set_font_color(self):
        self.font_color = QtWidgets.QColorDialog.getColor()
        if self.font_color.isValid():
            for i in self.LABELS:
                i.setStyleSheet("QLabel {"
                                f"color: {self.font_color.name()}" + ";}")
            for i in self.RADIO_BUTTONS:
                i.setStyleSheet("QRadioButton {"
                                f"color: {self.font_color.name()}" + ";}")
            for i in self.DAYS:
                i.setStyleSheet("QLabel {"
                                f"color: {self.font_color.name()}" + ";}")
            for i in self.DAYS_TEMP:
                i.setStyleSheet("QLabel {"
                                f"color: {self.font_color.name()}" + ";}")

            self.errorLabel.setStyleSheet("QLabel {"
                                          f"color: {self.font_color.name()}" + ";}")
            self.forecastLabel.setStyleSheet("QLabel {"
                                             f"color: {self.font_color.name()}" + ";}")

    def set_font(self):
        self.font_name = self.fontLine.text()
        self.setStyleSheet("QPushButton {"
                                f"background-color: {self.color.name()};"
                                f"color: white; "
                                f"font-family: {self.font_name};"
                                "border-radius: 5px;}"
                                "QPushButton::hover {"
                               f"background-color: {rgb_to_hex(tuple(i - 20 for i in list(hex_to_rgb(self.color.name()))))};"
                               f"color: white;"
                               f"font-family: {self.font_name};"
                                "border-radius: 5px;"
                                "min-width: 40ex;"
                                "min-height: 10ex;}")
        self.errorLabel.setStyleSheet("QLabel {"
                                      f"font-family: {self.font_name}" + ";}")
        self.forecastLabel.setStyleSheet("QLabel {"
                                         f"font-family: {self.font_name};"
                                         f"color: {self.font_color.name()}" + "}")
        for i in self.LABELS:
            i.setStyleSheet("QLabel {"
                            f"font-family: {self.font_name};"
                            f"color: {self.font_color.name()}" + "}")
        for i in self.RADIO_BUTTONS:
            i.setStyleSheet("QRadioButton {"
                            f"font-family: {self.font_name};"
                            f"color: {self.font_color.name()}" + "}")
        for i in self.DAYS:
            i.setStyleSheet("QLabel {"
                            f"font-family: {self.font_name};"
                            f"color: {self.font_color.name()}" + "}")
        for i in self.DAYS_TEMP:
            i.setStyleSheet("QLabel {"
                            f"font-family: {self.font_name};"
                            f"color: {self.font_color.name()}" + "}")
        self.fontLine.setStyleSheet("QLineEdit {border-radius: 5px}")


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec_())