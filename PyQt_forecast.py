import json
import sys
from pprint import pprint

import pandas as pd
from PyQt6.QtGui import QPixmap

from class_Location import GetLocation
from class_Forecast import Forecasts

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, \
    QWidget, QVBoxLayout, QLineEdit, QTextEdit, QHBoxLayout


class MainWindow(QMainWindow):
    
    def __init__(self):
        super(MainWindow, self).__init__()

        self.setWindowTitle("Погода")
        self.setFixedSize(QSize(800, 600))
        
        self.user_city = QTextEdit()
        self.user_city.setFixedSize(400, 30)
        self.user_city.setPlaceholderText('Введите город')
        self.add_btn = QPushButton('Найти')
        self.add_btn.setFixedSize(60, 30)
        self.add_btn.clicked.connect(self.get_forecast_for_new_city)
        
        self.current_weather = QLabel('Текущая погода')
        # self.city =
        # self.current_time =

        self.today_weather = QLabel('Погода на сегодня')

        self.future_days_weather = QLabel('Погода на ближайшие 3 дня')
        
        user_city_layout = QHBoxLayout()
        user_city_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        user_city_layout.addWidget(self.user_city)
        user_city_layout.addWidget(self.add_btn)
        
        current_weather_layout = QHBoxLayout()
        current_weather_layout.addWidget(self.current_weather)
        
        today_weather_layout = QHBoxLayout()
        today_weather_layout.addWidget(self.today_weather)

        future_days_weather_layout = QHBoxLayout()
        future_days_weather_layout.addWidget(self.future_days_weather)
        
        base_layout = QVBoxLayout()
        base_layout.addLayout(user_city_layout)
        base_layout.addLayout(current_weather_layout)
        base_layout.addLayout(today_weather_layout)
        base_layout.addLayout(future_days_weather_layout)
        
        
        widget = QWidget()
        widget.setLayout(base_layout)
        self.setCentralWidget(widget)
        
        
        try:
            with open('location.json', 'r', encoding='utf-8') as file:
                self.user_city_location = json.load(file)
        except json.decoder.JSONDecodeError as ex:
            self.user_city_location = None
        print(self.user_city_location)
      
        try:
            with open("forecast.json", "r", encoding="utf-8") as file:
                self.forecast_params = json.load(file)
        except json.decoder.JSONDecodeError as ex:
            self.forecast_params = None
        print(self.forecast_params)

    

    # def get_forecast_for_new_city(self):
    #     if not self.user_city_location:
    #         self.user_city_location = GetLocation(self.user_city.toPlainText())
    #         self.user_city_location.get_json()
    #     print(1)
    #     location_params = self.user_city_location.read_json()
    #     print(2)
    #
    #     if not self.forecast:
    #         self.forecast = Forecasts(location_params['latitude'],
    #                                   location_params['longitude'],
    #                                   location_params['timezone'])
    #         print(3)
    #         with open("forecast.txt", "w", newline="", encoding="utf-8") as file:
    #             json.dump(self.forecast, file)
    #         print(4)
    #     with open("forecast.txt", "r", encoding="utf-8") as file:
    #         self.forecast = json.load(file)
    #     print(5)
    #
    #     print(self.forecast.get_current_weather())
    #     pprint(self.forecast.get_today_weather().index)
    #     pprint(self.forecast.get_today_weather().columns)
    #     pd.set_option('display.max_columns', None)
    #     pprint(self.forecast.get_today_weather())
    #     pprint(self.forecast.get_3days_weather())
    
    def get_forecast_for_new_city(self):
        if not self.user_city_location:
            self.user_city_location = GetLocation(self.user_city.toPlainText())
            self.user_city_location.get_json()
            self.forecast_params = {
                    'latitude': self.user_city_location.read_json()[
                        'latitude'],
                    'longitude': self.user_city_location.read_json()[
                        'longitude'],
                    'timezone': self.user_city_location.read_json()['timezone']
                }
            with open("forecast.json", "w", encoding="utf-8") as file:
                json.dump(self.forecast_params, file)
            
        if not self.forecast_params:
            with open("forecast.json", "r", encoding="utf-8") as file:
                self.forecast_params = json.load(file)
            
        self.forecast = Forecasts(self.forecast_params['latitude'],
                                self.forecast_params['longitude'],
                                self.forecast_params['timezone'])
            
        print(self.forecast.get_current_weather())
        pprint(self.forecast.get_today_weather().index)
        pprint(self.forecast.get_today_weather().columns)
        pd.set_option('display.max_columns', None)
        pprint(self.forecast.get_today_weather())
        pprint(self.forecast.get_3days_weather())
    
        

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    window = MainWindow()
    window.show()
    
    app.exec()