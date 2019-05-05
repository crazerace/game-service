# Intenal modules
from app.models import Coordinate
from app.service import distance_util


def test_calculate_distance():
    start = Coordinate(latitude=10.111, longitude=10.111)
    end = Coordinate(latitude=10.111641, longitude=10.111641)
    distance = distance_util.calculate(start, end)
    assert distance == 100

    start = Coordinate(latitude=10.111, longitude=10.111)
    end = Coordinate(latitude=10.111, longitude=10.111)
    distance = distance_util.calculate(start, end)
    assert distance == 0


def test_is_within():
    origin = Coordinate(latitude=59.318329, longitude=18.042192)
    too_close = Coordinate(latitude=59.316556, longitude=18.033478)  # 532 meters from origin

    assert not distance_util.is_within(origin, too_close, max_dist=3000, min_dist=1000)
    assert distance_util.is_within(origin, too_close, max_dist=3000)

    within = Coordinate(latitude=59.318134, longitude=18.063666)  # 1218 meters from origin
    assert distance_util.is_within(origin, within, max_dist=3000, min_dist=1000)
    assert not distance_util.is_within(origin, within, max_dist=3000, min_dist=1500)

    out_of_range = Coordinate(latitude=59.326934, longitude=18.103433)  # 3603 meters from origin
    assert not distance_util.is_within(origin, out_of_range, max_dist=3000, min_dist=1000)
    assert not distance_util.is_within(origin, out_of_range, max_dist=3000)
    assert distance_util.is_within(origin, out_of_range, max_dist=3700, min_dist=1000)

