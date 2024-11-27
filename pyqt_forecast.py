import json
import os
import sys
from datetime import datetime

import pandas as pd
import pytz
from PyQt6.QtGui import QPixmap
from pytz import timezone
from requests_cache import utcnow

from class_location import Location
from class_forecast import Forecasts

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, \
    QWidget, QVBoxLayout, QLineEdit, QTextEdit, QHBoxLayout, QTableWidget, \
    QTableWidgetItem, QMessageBox


class MainWindow(QMainWindow):
    
    def __init__(self):
        super(MainWindow, self).__init__()

        self.setWindowTitle("Погода")
        self.setMinimumSize(QSize(1200, 600))
        
        self.user_city = QTextEdit()
        self.user_city.setFixedSize(400, 30)
        self.user_city.setPlaceholderText('Введите город')
        self.add_btn = QPushButton('Найти')
        self.add_btn.setFixedSize(60, 30)
        self.add_btn.clicked.connect(self.check_text_editor)
        
        self.current_weather = QLabel('Текущая погода')
        self.city = QLabel('           ')
        city_font = self.city.font()
        city_font.setPointSize(30)
        self.city.setFont(city_font)
        self.local_time = QLabel('           ')
        time_font = self.local_time.font()
        time_font.setPointSize(30)
        self.local_time.setFont(time_font)
        self.current_table = QTableWidget(2, 9)
        self.current_table.resizeColumnsToContents()


        self.today_weather = QLabel('Погода на сегодня')
        self.today_table = QTableWidget(4, 25)
        self.today_table.resizeColumnsToContents()

        self.future_days_weather = QLabel('Погода на ближайшие 3 дня')
        # self.future_days_weather.setFont(time_font)
        self.future_table = QTableWidget(4, 5)
        for i in range (1,5):
            self.future_table.setColumnWidth(i, 250)
        
        user_city_layout = QHBoxLayout()
        user_city_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        user_city_layout.addWidget(self.user_city)
        user_city_layout.addWidget(self.add_btn)
        
        current_weather_layout = QVBoxLayout()
        current_weather_layout.addWidget(self.current_weather)
        current_weather_layout.addWidget(self.current_table)
        city_and_time_layout = QVBoxLayout()
        city_and_time_layout.addWidget(self.city)
        city_and_time_layout.addWidget(self.local_time)
        
        city_weather_layout = QHBoxLayout()
        city_weather_layout.addLayout(city_and_time_layout)
        city_weather_layout.addLayout(current_weather_layout)
        
        today_weather_layout = QVBoxLayout()
        today_weather_layout.addWidget(self.today_weather)
        today_weather_layout.addWidget(self.today_table)

        future_days_weather_layout = QVBoxLayout()
        future_days_weather_layout.addWidget(self.future_days_weather)
        future_days_weather_layout.addWidget(self.future_table)
        
        base_layout = QVBoxLayout()
        base_layout.addLayout(user_city_layout)
        base_layout.addLayout(city_weather_layout)
        base_layout.addLayout(today_weather_layout)
        base_layout.addLayout(future_days_weather_layout)
        
        
        widget = QWidget()
        widget.setLayout(base_layout)
        self.setCentralWidget(widget)
        
        try:
            self.user_city_location = Location.read_json()
        except (json.decoder.JSONDecodeError, FileNotFoundError):
            self.user_city_location = None
        
        try:
            with open('forecast.json', 'r', encoding='utf-8') as file:
                self.forecast_params = json.load(file)
        except (json.decoder.JSONDecodeError, FileNotFoundError):
            self.forecast_params = None
        
        if self.user_city_location and self.forecast_params:
            self.fill_tables_with_forecasts()
           
    def get_forecast_for_city(self):
        
        # if not self.user_city_location:
        if (not os.path.isfile(
                'location.json') or self.user_city.toPlainText() !=
                Location.read_json()[
                    'city_name']) and self.user_city.toPlainText() != '':
            self.user_city_location = Location(self.user_city.toPlainText())
            self.user_city_location.get_json()
            self.forecast_params = self.user_city_location.read_json()
            with open('forecast.json', 'w', encoding='utf-8') as file:
                json.dump(self.forecast_params, file)
            
            forecast = Forecasts(self.forecast_params['latitude'],
                                 self.forecast_params['longitude'],
                                 self.forecast_params['timezone'],
                                 self.forecast_params['city_name'])
        else:
            forecast = Forecasts(self.forecast_params['latitude'],
                                 self.forecast_params['longitude'],
                                 self.forecast_params['timezone'],
                                 self.forecast_params['city_name'])
        return forecast
        
    def fill_tables_with_forecasts(self):
        
        forecast_data = self.get_forecast_for_city()
        
        self.current_table.clearContents()
        self.today_table.clearContents()
        self.future_table.clearContents()
        
        current_forecast_data = forecast_data.get_current_weather()
        for i, data in enumerate(current_forecast_data.items()):
            item_params = QTableWidgetItem(data[0])
            item_values = QTableWidgetItem(str(data[1]))
            
            self.current_table.setItem(0, i, item_params)
            self.current_table.setItem(1, i, item_values)
        
        today_forecast_data = forecast_data.get_today_weather()
        for i, data in enumerate(today_forecast_data.items()):
            item_time = QTableWidgetItem(str(data[0]))
            self.today_table.setItem(i, 0, item_time)
            for x in range(0,24):
                item_temperature = QTableWidgetItem(str(data[1][x]))
                self.today_table.setItem(i, x+1, item_temperature)
                
        future_forecast_data = forecast_data.get_3days_weather()
        for i, data in enumerate(future_forecast_data.items()):
            item_params = QTableWidgetItem(str(data[0]))
            self.future_table.setItem(0, i, item_params)
            for x in range(1,4):
                item_values = QTableWidgetItem(str(data[1][x]))
                self.future_table.setItem(x, i, item_values)
        
        self.city.setText(forecast_data.get_city_time()[0])
        self.local_time.setText(forecast_data.get_city_time()[1])
        
    def error(self):
        try:
            error = QMessageBox()
            error.setWindowTitle('Предупреждение')
            error.setText('Для поиска прогноза погоды введите город!')
            error.setIcon(QMessageBox.Icon.Warning)
            error.setStandardButtons(
                QMessageBox.StandardButton.Close
            )
            error.exec()
        except Exception as ex:
            print(ex)
    
    def check_text_editor(self):
        if self.user_city.toPlainText() != '':
            self.fill_tables_with_forecasts()
        else:
            self.error()
            
            
if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    window = MainWindow()
    window.show()
    
    app.exec()