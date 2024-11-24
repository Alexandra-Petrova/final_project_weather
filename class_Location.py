import requests
import json


class GetLocation:
	"""
	Класс описывает местоположение.
	"""
	def __init__(self, city: str):
		self.__city = city
		self.__url = f'https://geocoding-api.open-meteo.com/v1/search?name={self.__city}&count=1&language=ru&format=json'

	def get_json(self):
		response = requests.get(self.__url)
		data = response.json()
		with open('location.json', 'w', newline='', encoding='utf-8') as file:
			json.dump(data, file)

	@staticmethod
	def read_json():
		with open('location.json', 'r', encoding='utf-8') as file:
			location_params = json.load(file)
		city_name = location_params['results'][0]['name']
		latitude = location_params['results'][0]['latitude']
		longitude = location_params['results'][0]['longitude']
		timezone = location_params['results'][0]['timezone']
		return {'city_name': city_name,
				'latitude': latitude,
				'longitude': longitude,
				'timezone': timezone}


if __name__ == '__main__':
	try:
		location_params = GetLocation.read_json()
	except:
		user_city = input('Введите название города: ')
		user_city_location = GetLocation(user_city)
		user_city_location.get_json()
		location_params = user_city_location.read_json()

	print(location_params['latitude'])
	print(location_params['longitude'])
	print(location_params['timezone'].replace('/', '%2F'))
	print(location_params['city_name'])
