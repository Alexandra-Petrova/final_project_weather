import json

import requests

from requests import Response


class Location:
    """
    Класс описывает местоположение.
    """

    def __init__(self, city: str):
        """Устанавливает атрибуты для объекта Location.

        Args:
            city: Город.
            url: URL-адрес для получения координат и часового пояса города.
        """
        self.__city = city
        self.__url: str = (
            f"https://geocoding-api.open-meteo.com/v1/search?name="
            f"{self.__city}&count=1&language=ru&format=json"
        )

    def get_json(self):
        """Запрос данных о городе с сайта, запись их в файл location.json."""
        response: Response = requests.get(self.__url)
        data: dict = response.json()
        with open("location.json", "w", newline="", encoding="utf-8") as file:
            json.dump(data, file)

    @staticmethod
    def read_json() -> dict:
        """Чтение данных о городе из файла location.json.

        Returns:
            Словарь с названием, координатами и часовым поясом города.
        """
        with open("location.json", "r", encoding="utf-8") as file:
            location_params: dict = json.load(file)
        city_name: str = location_params["results"][0]["name"]
        latitude: float = location_params["results"][0]["latitude"]
        longitude: float = location_params["results"][0]["longitude"]
        timezone: str = location_params["results"][0]["timezone"]
        return {
            "city_name": city_name,
            "latitude": latitude,
            "longitude": longitude,
            "timezone": timezone,
        }


if __name__ == "__main__":
    user_city = input("Введите название города: ")
    user_city_location = Location(user_city)
    user_city_location.get_json()
    location_params = user_city_location.read_json()

    print(location_params["latitude"])
    print(location_params["longitude"])
    print(location_params["timezone"])
    print(location_params["city_name"])
