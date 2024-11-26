import json
import sys

import pandas as pd
from PyQt6.QtGui import QPixmap

from class_Location import GetLocation
from class_Forecast import Forecasts

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, \
    QWidget, QVBoxLayout, QLineEdit, QTextEdit, QHBoxLayout, QTableWidget, \
    QTableWidgetItem


class MainWindow(QMainWindow):
    
    def __init__(self):
        super(MainWindow, self).__init__()

        self.setWindowTitle("Погода")
        self.setFixedSize(QSize(1200, 600))
        
        self.user_city = QTextEdit()
        self.user_city.setFixedSize(400, 30)
        self.user_city.setPlaceholderText('Введите город')
        self.add_btn = QPushButton('Найти')
        self.add_btn.setFixedSize(60, 30)
        self.add_btn.clicked.connect(self.fill_tables_with_forecasts)
        
        self.current_weather = QLabel('Текущая погода')
        # self.city =
        # self.current_time =
        self.current_table = QTableWidget(2, 9)
        self.current_table.setRowCount(2)
        self.current_table.setColumnCount(9)

        self.today_weather = QLabel('Погода на сегодня')
        self.today_table = QTableWidget()
        self.today_table.setRowCount(4)
        self.today_table.setColumnCount(25)

        self.future_days_weather = QLabel('Погода на ближайшие 3 дня')
        self.future_table = QTableWidget()
        self.future_table.setRowCount(4)
        self.future_table.setColumnCount(5)
        
        user_city_layout = QHBoxLayout()
        user_city_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        user_city_layout.addWidget(self.user_city)
        user_city_layout.addWidget(self.add_btn)
        
        current_weather_layout = QHBoxLayout()
        current_weather_layout.addWidget(self.current_weather)
        current_weather_layout.addWidget(self.current_table)
        
        today_weather_layout = QHBoxLayout()
        today_weather_layout.addWidget(self.today_weather)
        today_weather_layout.addWidget(self.today_table)

        future_days_weather_layout = QHBoxLayout()
        future_days_weather_layout.addWidget(self.future_days_weather)
        future_days_weather_layout.addWidget(self.future_table)
        
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
        except (json.decoder.JSONDecodeError, FileNotFoundError) as ex:
            self.user_city_location = None
        print(self.user_city_location)
      
        try:
            with open("forecast.json", "r", encoding="utf-8") as file:
                self.forecast_params = json.load(file)
        except (json.decoder.JSONDecodeError, FileNotFoundError) as ex:
            self.forecast_params = None
        print(self.forecast_params)
        
        if self.user_city_location and self.forecast_params:
            self.fill_tables_with_forecasts()
        

    
    def get_forecast_for_city(self):
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
            
        forecast = Forecasts(self.forecast_params['latitude'],
                                self.forecast_params['longitude'],
                                self.forecast_params['timezone'])
        
        return forecast
    
    def fill_tables_with_forecasts(self):
        
        forecast_data = self.get_forecast_for_city()
        
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

            
if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    window = MainWindow()
    window.show()
    
    app.exec()