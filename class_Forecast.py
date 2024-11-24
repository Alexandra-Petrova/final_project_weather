import json
import openmeteo_requests
from datetime import datetime, timedelta, timezone

import pytz
import requests_cache
import pandas as pd
from dateutil.utils import today
from retry_requests import retry


class Forecasts:
	"""
	Класс описывает прогноз погоды: текущий, на сутки, и на 3 дня вперед.
	"""

	def __init__(self, latitude, longitude, timezone):
		# self.latitude = latitude
		# self.longitude = longitude
		self.timezone = timezone
		# self.start_time = datetime.datetime.now().isoformat()
		self.url = "https://api.open-meteo.com/v1/forecast"
		self.params = {
			"latitude": latitude,
			"longitude": longitude,
			"current": ["temperature_2m", "relative_humidity_2m",
						"apparent_temperature", "precipitation",
						"weather_code", "cloud_cover", "pressure_msl",
						"wind_speed_10m", "wind_direction_10m"],
			"hourly": ["temperature_2m",
					   "precipitation_probability",
					   "weather_code"],
			"daily": ["weather_code", "temperature_2m_max",
					  "temperature_2m_min", "precipitation_probability_max"],
			"wind_speed_unit": "ms",
			"timezone": timezone,
			"start_date": datetime.now().strftime("%Y-%m-%d"),
			"end_date": (datetime.now() + timedelta(days=3)).strftime(
				"%Y-%m-%d")
		}

		openmeteo = openmeteo_requests.Client()
		responses = openmeteo.weather_api(self.url, params=self.params)
		self.response = responses[0]

	def get_current_weather(self):
		def calculate_wind_dir(dir_degrees):
			directions = ["Северный", "Северо-восточный", "Восточный",
						  "Юго-восточный", "Южный", "Юго-западный",
						  "Западный", "Северо-западный"]
			index = round(dir_degrees / 45) % 8
			return directions[index]

		def get_weather_descript(weather_code):
			weather_descrition = {
				0: 'Ясно',
				1: 'Преимущественно ясно',
				2: 'Переменная облачность',
				3: 'Облачно',
				45: 'Туман',
				48: 'Изморозь',
				51: 'Моросящий дождь (низкая плотность)',
				53: 'Моросящий дождь (средняя плотность)',
				55: 'Моросящий дождь (высокая плотность)',
				56: 'Замерзающий моросящий дождь (низкая плотность)',
				57: 'Замерзающий моросящий дождь (высокая плотность)',
				61: 'Небольшой дождь',
				63: 'Умеренный дождь',
				65: 'Сильный дождь',
				66: 'Небольшой замерзающий дождь',
				67: 'Сильный замерзающий дождь',
				71: 'Небольшой снегопад',
				73: 'Умеренный снегопад',
				75: 'Сильный снегопад',
				77: 'Снежные зёрна',
				80: 'Небольшой ливневый дождь',
				81: 'Умеренный ливневый дождь',
				82: 'Сильный ливневый дождь',
				85: 'Небольшая метель',
				86: 'Сильная метель',
				95: 'Небольшая или умеренная гроза',
				96: 'Гроза с небольшим градом',
				99: 'Гроза с умеренным градом'
			}
			return weather_descrition[weather_code]

		current = self.response.Current()
		current_params_text = ['Температура',
							   'Относительная влажность',
							   'Ощущается как',
							   'Осадки',
							   'Описание погоды',
							   'Общий уровень облачности',
							   'Атмосферное давление',
							   'Скорость ветра',
							   'Направление ветра']
		current_params_values = [current.Variables(i).Value()
								 for i in range(0, 9)]
		current_params_dict = dict(
			zip(current_params_text, current_params_values))

		current_params_dict['Направление ветра'] = (
			calculate_wind_dir(current_params_dict['Направление ветра']))
		current_params_dict['Описание погоды'] = (
			get_weather_descript(current_params_dict['Описание погоды']))
		current_params_dict['Атмосферное давление'] = (
			round(current_params_dict['Атмосферное давление'] * 0.750064))

		return current_params_dict

	def get_today_weather(self):
		# start_time = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
		# end_time = start_time + timedelta(days=1)
		# print(start_time, end_time)

		def get_weather_descript(weather_code):
			weather_descrition = {
				0: 'Ясно',
				1: 'Преимущественно ясно',
				2: 'Переменная облачность',
				3: 'Облачно',
				45: 'Туман',
				48: 'Изморозь',
				51: 'Моросящий дождь (низкая плотность)',
				53: 'Моросящий дождь (средняя плотность)',
				55: 'Моросящий дождь (высокая плотность)',
				56: 'Замерзающий моросящий дождь (низкая плотность)',
				57: 'Замерзающий моросящий дождь (высокая плотность)',
				61: 'Небольшой дождь',
				63: 'Умеренный дождь',
				65: 'Сильный дождь',
				66: 'Небольшой замерзающий дождь',
				67: 'Сильный замерзающий дождь',
				71: 'Небольшой снегопад',
				73: 'Умеренный снегопад',
				75: 'Сильный снегопад',
				77: 'Снежные зёрна',
				80: 'Небольшой ливневый дождь',
				81: 'Умеренный ливневый дождь',
				82: 'Сильный ливневый дождь',
				85: 'Небольшая метель',
				86: 'Сильная метель',
				95: 'Небольшая или умеренная гроза',
				96: 'Гроза с небольшим градом',
				99: 'Гроза с умеренным градом'
			}
			return weather_descrition[weather_code]

		hourly = self.response.Hourly()
		hourly_temperature = hourly.Variables(0).ValuesAsNumpy()
		hourly_precipitation = hourly.Variables(1).ValuesAsNumpy()
		hourly_weather_code = hourly.Variables(2).ValuesAsNumpy()

		hourly_data = {"Дата и время": pd.date_range(
			start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
			end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
			freq=pd.Timedelta(seconds=hourly.Interval()),
			inclusive="left"
		), "Температура": hourly_temperature,
			"Вероятность выпадения осадков": hourly_precipitation,
			"Описание погоды": hourly_weather_code}

		hourly_dataframe = pd.DataFrame(data=hourly_data)
		today_hourly_dataframe = hourly_dataframe.loc[:23].copy()
		today_hourly_dataframe['Дата и время'] = today_hourly_dataframe[
			'Дата и время'].apply(
			lambda x: x.astimezone(self.timezone))
		today_hourly_dataframe['Дата и время'] = today_hourly_dataframe[
			'Дата и время'].apply(lambda x: x.strftime("%Y-%m-%d %H:%M"))
		today_hourly_dataframe['Описание погоды'] = today_hourly_dataframe[
			'Описание погоды'].apply(get_weather_descript)

		return today_hourly_dataframe

	def get_3days_weather(self):
		def get_weather_descript(weather_code):
			weather_descrition = {
				0: 'Ясно',
				1: 'Преимущественно ясно',
				2: 'Переменная облачность',
				3: 'Облачно',
				45: 'Туман',
				48: 'Изморозь',
				51: 'Моросящий дождь (низкая плотность)',
				53: 'Моросящий дождь (средняя плотность)',
				55: 'Моросящий дождь (высокая плотность)',
				56: 'Замерзающий моросящий дождь (низкая плотность)',
				57: 'Замерзающий моросящий дождь (высокая плотность)',
				61: 'Небольшой дождь',
				63: 'Умеренный дождь',
				65: 'Сильный дождь',
				66: 'Небольшой замерзающий дождь',
				67: 'Сильный замерзающий дождь',
				71: 'Небольшой снегопад',
				73: 'Умеренный снегопад',
				75: 'Сильный снегопад',
				77: 'Снежные зёрна',
				80: 'Небольшой ливневый дождь',
				81: 'Умеренный ливневый дождь',
				82: 'Сильный ливневый дождь',
				85: 'Небольшая метель',
				86: 'Сильная метель',
				95: 'Небольшая или умеренная гроза',
				96: 'Гроза с небольшим градом',
				99: 'Гроза с умеренным градом'
			}
			return weather_descrition[weather_code]

		daily = self.response.Daily()
		daily_weather_code = daily.Variables(0).ValuesAsNumpy()
		daily_temperature_max = daily.Variables(1).ValuesAsNumpy()
		daily_temperature_min = daily.Variables(2).ValuesAsNumpy()
		daily_precipitation = daily.Variables(3).ValuesAsNumpy()

		daily_data = {"Дата": pd.date_range(
			start=pd.to_datetime(daily.Time(), unit="s", utc=True),
			end=pd.to_datetime(daily.TimeEnd(), unit="s", utc=True),
			freq=pd.Timedelta(seconds=daily.Interval()),
			inclusive="left"
		), "Описание погоды": daily_weather_code,
			"Максимальная температура": daily_temperature_max,
			"Минимальная температура": daily_temperature_min,
			"Максимальная вероятность выпадения осадков": daily_precipitation}

		daily_dataframe = pd.DataFrame(data=daily_data)
		days_3_dataframe = daily_dataframe.loc[1:3].copy()
		days_3_dataframe['Дата'] = days_3_dataframe[
			'Дата'].apply(lambda x: x.astimezone(self.timezone))
		days_3_dataframe['Дата'] = days_3_dataframe[
			'Дата'].apply(lambda x: x.strftime("%Y-%m-%d"))
		days_3_dataframe['Описание погоды'] = days_3_dataframe[
			'Описание погоды'].apply(get_weather_descript)

		return days_3_dataframe
