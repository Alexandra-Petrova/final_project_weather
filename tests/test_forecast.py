import pytest

from final_project.class_forecast import Forecasts


@pytest.mark.parametrize(
    'input_degree, expected_description',
    [(45, 'Северо-восточный'),
     (315, 'Северо-западный')]
)
def test_read_json(input_degree, expected_description):
    for i in range(2):
        assert Forecasts.calculate_wind_dir(input_degree) == expected_description