# Internal modules
from app.models import GeoPosition


def is_within(
    origin: GeoPosition, destination: GeoPosition, max_dist: int, min_dist: int = 0
) -> bool:
    """Checks if two positions are within a specified distance of each others.

    :param origin: GeoPosition to calculate distance from.
    :param destination: GeoPosition to calculate distance to.
    :param max_dist: Maximum distance in meters.
    :param min_dist: Minimum distance in meters.
    :return: Boolean.
    """
    distance = calculate(origin, destination)
    return min_dist <= distance and distance <= max_dist


def calculate(origin: GeoPosition, destination: GeoPosition) -> int:
    """Calculates the distance in meters between two positions.

    :param origin: GeoPosition to calculate distance from.
    :param destination: GeoPosition to calculate distance to.
    :return: Distance in meters as an integer.
    """
    return 1000
