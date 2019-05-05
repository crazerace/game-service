# 3rd party modules
from geopy.distance import geodesic

# Internal modules
from app.models import Coordinate


def is_within(
    origin: Coordinate, destination: Coordinate, max_dist: int, min_dist: int = 0
) -> bool:
    """Checks if two positions are within a specified distance of each others.

    :param origin: Coordinate to calculate distance from.
    :param destination: Coordinate to calculate distance to.
    :param max_dist: Maximum distance in meters.
    :param min_dist: Minimum distance in meters.
    :return: Boolean.
    """
    dist = calculate(origin, destination)
    return min_dist <= dist and dist <= max_dist


def calculate(origin: Coordinate, destination: Coordinate) -> int:
    """Calculates the distance in meters between two positions.

    :param origin: Coordinate to calculate distance from.
    :param destination: Coordinate to calculate distance to.
    :return: Distance in meters as an integer.
    """
    origin_tuple = (origin.latitude, origin.longitude)
    destination_tuple = (destination.latitude, destination.longitude)
    distance = geodesic(origin_tuple, destination_tuple)
    return round(distance.meters)
