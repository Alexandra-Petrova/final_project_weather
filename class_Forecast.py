from datetime import datetime, timedelta

import openmeteo_requests
import pandas as pd
import pytz
from numpy import ndarray
from openmeteo_requests import Client
from openmeteo_sdk.VariablesWithTime import VariablesWithTime
from openmeteo_sdk.WeatherApiResponse import WeatherApiResponse
from pandas import DataFrame, DatetimeIndex


class Forecasts:
    """
    Класс описывает прогноз погоды: текущий, на сутки, и на 3 дня вперед.
    """

    def __init__(self, latitude: float, longitude: float, timezone: str,
                 city: str):
        """Устанавливает атрибуты для объекта Forecasts.

        Args:
            latitude: Широта.
            longitude: Долгота.
            timezone: Часовой пояс.
            city: Город.
            start_date: Начальная дата.
            end_date: Конечная дата.
            url: URL-адрес для получения прогноза погоды.
            params: Параметры для запроса прогноза погоды.
            response: Результат запроса прогноза погоды.
        """
        self.latitude = latitude
        self.longitude = longitude
        self.timezone = timezone
        self.city = city
        self.start_date: str = datetime.now().strftime('%Y-%m-%d')
        self.end_date: str = (datetime.now() +
                              timedelta(days=3)).strftime('%Y-%m-%d')
        self.url: str = 'https://api.open-meteo.com/v1/forecast'
        self.params: dict[str, str | list[str] | float] = {
            'latitude': self.latitude,
            'longitude': self.longitude,
            'current': [
                'temperature_2m',
                'relative_humidity_2m',
                'apparent_temperature',
                'precipitation',
                'weather_code',
                'cloud_cover',
                'pressure_msl',
                'wind_speed_10m',
                'wind_direction_10m',
            ],
            'hourly': ['temperature_2m', 'precipitation_probability',
                       'weather_code'],
            'daily': [
                'weather_code',
                'temperature_2m_max',
                'temperature_2m_min',
                'precipitation_probability_max',
            ],
            'wind_speed_unit': 'ms',
            'timezone': self.timezone,
            'start_date': self.start_date,
            'end_date': self.end_date,
        }

        openmeteo: Client = openmeteo_requests.Client()
        responses:  list[WeatherApiResponse] = openmeteo.weather_api(
            self.url, params=self.params)
        self.response: WeatherApiResponse = responses[0]

    @staticmethod
    def calculate_wind_dir(dir_degrees: float) -> str:
        """Пересчет направления ветра из градусов в стороны света.

        Args:
            dir_degrees: Направление ветра в градусах.

        Returns:
            Направление ветра в сторонах света.
        """
        directions: list[str] = [
            'Северный',
            'Северо-восточный',
            'Восточный',
            'Юго-восточный',
            'Южный',
            'Юго-западный',
            'Западный',
            'Северо-западный',
        ]
        index: int = round(dir_degrees / 45) % 8
        return directions[index]

    @staticmethod
    def get_weather_descript(weather_code: int) -> str:
        """Определение описания погоды.

        Args:
            weather_code: Код описания погоды.

        Returns:
            Текстовое описание погоды.
        """
        weather_descrition: dict[int, str] = {
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
            99: 'Гроза с умеренным градом',
        }
        return weather_descrition[weather_code]

    def get_current_weather(self) -> dict[str, float | str | int]:
        """Получение текущей погоды.

        Returns:
            current_params_dict: Словарь с данными о текущей погоде.
        """
        current: VariablesWithTime = self.response.Current()
        current_params_text:  list[str] = [
            'Температура, °C',
            'Относительная влажность, %',
            'Ощущается как, °C',
            'Осадки, мм',
            'Описание погоды',
            'Общий уровень облачности, %',
            'Атмосферное давление, мм.рт.ст.',
            'Скорость ветра, м/с',
            'Направление ветра',
        ]
        current_params_values:  list[float] = [current.Variables(i).Value()
                                               for i in range(0, 9)]
        current_params_dict:  dict[str, float | str] = dict(
            zip(current_params_text, current_params_values))

        current_params_dict['Температура, °C'] = round(
            current_params_dict['Температура, °C']
        )
        current_params_dict['Ощущается как, °C'] = round(
            current_params_dict['Ощущается как, °C']
        )
        current_params_dict['Скорость ветра, м/с'] = round(
            current_params_dict['Скорость ветра, м/с'], 1
        )
        current_params_dict['Направление ветра'] = self.calculate_wind_dir(
            current_params_dict['Направление ветра']
        )
        current_params_dict['Описание погоды'] = self.get_weather_descript(
            current_params_dict['Описание погоды']
        )
        current_params_dict['Атмосферное давление, мм.рт.ст.'] = round(
            current_params_dict['Атмосферное давление, мм.рт.ст.'] * 0.750064
        )
        return current_params_dict

    def get_today_weather(self) -> DataFrame:
        """Получение почасового прогноза погоды на сегодня.

        Returns:
            today_hourly_dataframe: Набор данных о погоде на сегодня.
        """
        hourly: VariablesWithTime = self.response.Hourly()
        hourly_temperature: ndarray[float] = (
            hourly.Variables(0).ValuesAsNumpy())
        hourly_precipitation: ndarray[float] = (
            hourly.Variables(1).ValuesAsNumpy())
        hourly_weather_code: ndarray[int] = hourly.Variables(2).ValuesAsNumpy()

        hourly_data: dict[
            str, DatetimeIndex | ndarray[int] | ndarray[float]] = {
            'Дата и время': pd.date_range(
                start=pd.to_datetime(hourly.Time(), unit='s', utc=True),
                end=pd.to_datetime(hourly.TimeEnd(), unit='s', utc=True),
                freq=pd.Timedelta(seconds=hourly.Interval()),
                inclusive='left',
            ),
            'Температура, °C': hourly_temperature,
            'Вероятность выпадения осадков, %': hourly_precipitation,
            'Описание погоды': hourly_weather_code,
        }

        hourly_dataframe: DataFrame = pd.DataFrame(data=hourly_data)
        today_hourly_dataframe: DataFrame = hourly_dataframe.loc[:23].copy()
        today_hourly_dataframe['Дата и время'] = today_hourly_dataframe[
            'Дата и время'
        ].apply(lambda x: x.astimezone(self.timezone))
        today_hourly_dataframe['Дата и время'] = today_hourly_dataframe[
            'Дата и время'
        ].apply(lambda x: x.strftime('%Y-%m-%d %H:%M'))
        today_hourly_dataframe['Описание погоды'] = today_hourly_dataframe[
            'Описание погоды'
        ].apply(self.get_weather_descript)
        today_hourly_dataframe['Температура, °C'] = today_hourly_dataframe[
            'Температура, °C'].apply(round)
        return today_hourly_dataframe

    def get_3days_weather(self) -> DataFrame:
        """Получение погоды на три последующих дня.

        Returns:
            days_3_dataframe: Набор данных о погоде на три последующих дня.
        """
        daily: VariablesWithTime = self.response.Daily()
        daily_weather_code: ndarray[int] = daily.Variables(0).ValuesAsNumpy()
        daily_temperature_max: ndarray[float] = (
            daily.Variables(1).ValuesAsNumpy())
        daily_temperature_min: ndarray[float] = (
            daily.Variables(2).ValuesAsNumpy())
        daily_precipitation: ndarray[float] = (
            daily.Variables(3).ValuesAsNumpy())

        daily_data: dict[
            str, DatetimeIndex | ndarray[float] | ndarray[int]] = {
            'Дата': pd.date_range(
                start=pd.to_datetime(daily.Time(), unit="s", utc=True),
                end=pd.to_datetime(daily.TimeEnd(), unit="s", utc=True),
                freq=pd.Timedelta(seconds=daily.Interval()),
                inclusive='left',
            ),
            'Описание погоды': daily_weather_code,
            'Максимальная температура, °C': daily_temperature_max,
            'Минимальная температура, °C': daily_temperature_min,
            'Максимальная вероятность выпадения осадков, %':
                daily_precipitation,
        }

        daily_dataframe: DataFrame = pd.DataFrame(data=daily_data)
        days_3_dataframe: DataFrame = daily_dataframe.loc[1:3].copy()
        days_3_dataframe['Дата'] = days_3_dataframe['Дата'].apply(
            lambda x: x.astimezone(self.timezone)
        )
        days_3_dataframe['Дата'] = days_3_dataframe['Дата'].apply(
            lambda x: x.strftime('%Y-%m-%d')
        )
        days_3_dataframe['Описание погоды'] = days_3_dataframe[
            'Описание погоды'].apply(self.get_weather_descript)
        days_3_dataframe['Максимальная температура, °C'] = days_3_dataframe[
            'Максимальная температура, °C'].apply(round)
        days_3_dataframe['Минимальная температура, °C'] = days_3_dataframe[
            'Минимальная температура, °C'].apply(round)

        return days_3_dataframe

    def get_city_time(self):
        """Получение наименования города и текущего времени.

        Returns:
            self.city: Город.
            current_city_time: Текущее время.
        """
        current_city_time: str = datetime.now().astimezone(
            pytz.timezone(self.timezone)).strftime('%H:%M')
        return self.city, current_city_time
