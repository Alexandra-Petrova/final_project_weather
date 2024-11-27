from final_project.class_location import Location


def test_read_json():
    user_city = Location('Томск')
    user_city.get_json()
    assert user_city.read_json() == {"city_name": 'Томск',
                                     "latitude": 56.49771,
                                     "longitude": 84.97437,
                                     "timezone": 'Asia/Tomsk'}