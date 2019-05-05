# Intenal modules
from app.models import GeoPosition
from app.service import distance_util


def test_calculate_distance():
    start = GeoPosition(latitude=10.1111, longitude=10.1111)
    end = GeoPosition(latitude=10.1112, longitude=10.1112)
    distance = distance_util.calculate(start, end)
    assert distance == 1000

    start = GeoPosition(latitude=10.1111, longitude=10.1111)
    end = GeoPosition(latitude=10.1111, longitude=10.1111)
    distance = distance_util.calculate(start, end)
    assert distance == 0
