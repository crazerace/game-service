# 3rd party modules
from geopy.distance import geodesic

# Internal modules
from app.models.dto import CoordinateDTO


def is_within(
    origin: CoordinateDTO, destination: CoordinateDTO, max_dist: int, min_dist: int = 0
) -> bool:
    """Checks if two positions are within a specified distance of each others.

    :param origin: CoordinateDTO to calculate distance from.
    :param destination: CoordinateDTO to calculate distance to.
    :param max_dist: Maximum distance in meters.
    :param min_dist: Minimum distance in meters.
    :return: Boolean.
    """
    dist = calculate(origin, destination)
    return min_dist <= dist and dist <= max_dist


def is_at_least(origin: CoordinateDTO, destination: CoordinateDTO, min_dist: int) -> bool:
    """Checks if two positions are at least a specified distance appart.

    :param origin: CoordinateDTO to calculate distance from.
    :param destination: CoordinateDTO to calculate distance to.
    :param min_dist: Minimum distance in meters.
    :return: Boolean.
    """
    dist = calculate(origin, destination)
    return min_dist < dist


def calculate(origin: CoordinateDTO, destination: CoordinateDTO) -> int:
    """Calculates the distance in meters between two positions.

    :param origin: CoordinateDTO to calculate distance from.
    :param destination: CoordinateDTO to calculate distance to.
    :return: Distance in meters as an integer.
    """
    origin_tuple = (origin.latitude, origin.longitude)
    destination_tuple = (destination.latitude, destination.longitude)
    distance = geodesic(origin_tuple, destination_tuple)
    return round(distance.meters)
